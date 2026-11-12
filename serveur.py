# serveurT — serveur de Transition (AutoniaX, extension réseau distribuée)
#
# Étape 0 du cahier (chaîne minimale de bout en bout) :
#   - une route WebSocket
#   - un registre en mémoire (liste des connexions actives)
#   - un seul type de message : "register"
#   - mAutoniax (pilote) reçoit la liste des sAutoniax (exécutants) connectés
#
# Nomenclature (cf. cahier, section 5.4, à trancher avant l'Étape 0) :
# "pilote" / "exécutant" — retenu plutôt que "pilote"/"observateur" pour
# éviter toute confusion avec le protocole du serveur LOCAL existant
# (srv_registre, srv_gerer_register, etc.), qui reste totalement séparé
# et inchangé. Ce fichier ne contient AUCUNE logique métier AutoniaX :
# il fait uniquement relais de messages + registre des connexions, comme
# prévu par le cahier ("Ne contient aucune logique métier AutoniaX").
#
# Ce serveurT est un projet à part (cf. cahier section 3) : pas de
# dépendance au reste du code AutoniaX, déployé séparément sur Render.

import asyncio
import base64
import io
import json
import logging
import posixpath
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response

# CORRECTIF ROBUSTESSE (diagnostic : crash serveur code -11 = SIGSEGV,
# observé après une rafale de ~20 démarrages de profils isolés
# simultanés -- cf. échange du 2026-09-10). Cause identifiée : TOUT le
# travail bloquant (appels Google Drive via googleapiclient/httplib2/
# ssl, ET décodage/réencodage d'images via Pillow/libwebp dans
# _recompresser_pour_diffusion) était envoyé au pool de threads PAR
# DÉFAUT de la boucle asyncio (run_in_executor(None, ...)), qui n'a
# AUCUNE limite de taille : sous forte charge, ce pool crée autant de
# threads OS que de tâches soumises, chacun exécutant du code natif en
# C (ssl, Drive, libwebp) en parallèle sans restriction. C'est ce
# genre de pression mémoire/CPU concurrente sur du code natif qui peut
# aboutir à un segfault du process entier -- un crash que Python ne
# peut PAS intercepter avec un try/except, contrairement aux erreurs
# Python ordinaires (déjà bien gérées partout ailleurs dans ce
# fichier).
#
# Fix : un ThreadPoolExecutor DÉDIÉ et borné (max_workers fixe, cf.
# EXECUTOR_TRAVAIL_BLOQUANT_MAX_WORKERS ci-dessous) remplace le pool
# par défaut pour tout le travail bloquant de ce fichier (Drive +
# Pillow). Un ThreadPoolExecutor met déjà en FILE D'ATTENTE les tâches
# au-delà de max_workers (aucune tâche n'est perdue, elles attendent
# simplement leur tour) -- combiné à un sémaphore asyncio côté appelant
# (cf. _a_thread plus bas et envoyer_capture) pour éviter également
# d'empiler des milliers de tâches en attente d'un coup en cas de
# rafale extrême (ex. 20 profils qui démarrent en même temps).
EXECUTOR_TRAVAIL_BLOQUANT_MAX_WORKERS = 6
_executor_travail_bloquant = ThreadPoolExecutor(
    max_workers=EXECUTOR_TRAVAIL_BLOQUANT_MAX_WORKERS,
    thread_name_prefix="travail-bloquant",
)
# Sémaphore asyncio, MÊME limite que l'executor -- empêche d'empiler
# plus de tâches "en vol" que l'executor ne peut en exécuter à la
# fois, ce qui borne aussi la mémoire consommée par les tâches en
# attente (buffers d'images, réponses Drive, etc. gardés vivants tant
# que la tâche n'est pas passée) plutôt que de les laisser s'accumuler
# sans limite dans la file interne de l'executor.
_semaphore_travail_bloquant = asyncio.Semaphore(EXECUTOR_TRAVAIL_BLOQUANT_MAX_WORKERS)

# PATCH stockage (demande explicite utilisateur : "je veux que on
# connecte deja notre stokage cloudflare avec notre serveur, parceque on
# vas envoyer certains fichier sur le stoakge persistant", cf. cahier
# réseau section 2 "Stockage cloud" et Étape 9).
#
# MIGRATION TOTALE Backblaze B2 -> Google Drive (décision explicite
# utilisateur : "migration total vers le drive"). Symétrique du même
# changement déjà fait côté AutoniaX.py (cf. GestionnaireStockageDrive
# Direct, _config_stockage_depuis_reglages).
#
# TOUT LE CODE DRIVE EST EN DUR ICI, DANS CE SEUL FICHIER (décision
# explicite utilisateur : "je ne veux pas de fichier drive.py
# suplementire dans ma pipeeine ... code ce qui est necessaire en dure
# dans le sscript") -- aucune dépendance à un module drive_stockage
# séparé à distribuer sur Colab, contrairement à un essai précédent.
# _ClientDriveMinimal ci-dessous réimplique juste assez de l'API Drive
# v3 (put/get/head/list/delete/copy par clé façon S3) pour les besoins
# de ce fichier, avec les mêmes noms de méthodes que l'ancien client
# boto3 pour minimiser les changements dans le reste du fichier.
#
# Dépendances (à ajouter au pip install du notebook ServeurTLauncher,
# section 1) : google-api-python-client, google-auth.
from googleapiclient.discovery import build as _drive_build
from googleapiclient.http import MediaIoBaseUpload as _DriveMediaUpload, MediaIoBaseDownload as _DriveMediaDownload
from google.oauth2 import service_account as _drive_service_account


class DriveNoSuchKey(Exception):
    """Levée quand une clé demandée (get_object/head_object) n'existe
    pas -- équivalent du ClientError/NoSuchKey de boto3, pour que le
    code appelant existant (qui testait déjà ce cas, cf. Gestionnaire
    Stockage.existe plus bas) continue de fonctionner avec un minimum
    de changements."""
    pass


def _echapper_nom_drive(nom: str) -> str:
    """Échappe une apostrophe dans un nom de fichier/dossier pour
    l'insérer sans risque dans une requête Drive `q=...` (syntaxe de
    requête Drive : une apostrophe littérale s'échappe par \\')."""
    return nom.replace("'", "\\'")


class _ClientDriveMinimal:
    """Enveloppe minimale autour de l'API Google Drive v3, exposant les
    mêmes noms de méthodes que boto3 (put_object/get_object/head_object/
    list_objects_v2/delete_object/copy_object) pour minimiser les
    changements dans le code appelant existant (GestionnaireStockage,
    GestionnaireStockageBB). Les clés façon S3 ("ServeurT/serveur.py")
    sont traduites en chemins de dossiers/fichiers Drive réels, résolus
    (et créés si besoin, pour les écritures) sous UN SEUL dossier
    racine -- ce dossier doit déjà exister et avoir été partagé
    manuellement en Éditeur avec l'adresse e-mail du compte de service
    AVANT le premier appel."""

    MIME_DOSSIER = "application/vnd.google-apps.folder"

    def __init__(self, cle_service_json: dict, dossier_racine_id: str):
        creds = _drive_service_account.Credentials.from_service_account_info(
            cle_service_json,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        self._service = _drive_build("drive", "v3", credentials=creds)
        self._racine_id = dossier_racine_id
        self._cache_dossiers: dict[str, str] = {}

    def _resoudre_dossier(self, segments_dossier: list[str], creer_si_absent: bool) -> str:
        cle_cache = "/".join(segments_dossier)
        if cle_cache in self._cache_dossiers:
            return self._cache_dossiers[cle_cache]

        parent_id = self._racine_id
        chemin_partiel = []
        for segment in segments_dossier:
            chemin_partiel.append(segment)
            cle_partielle = "/".join(chemin_partiel)
            if cle_partielle in self._cache_dossiers:
                parent_id = self._cache_dossiers[cle_partielle]
                continue

            requete = (
                f"'{parent_id}' in parents and name = '{_echapper_nom_drive(segment)}' "
                f"and mimeType = '{self.MIME_DOSSIER}' and trashed = false"
            )
            resultats = self._service.files().list(
                q=requete, fields="files(id, name)", pageSize=1,
            ).execute().get("files", [])

            if resultats:
                dossier_id = resultats[0]["id"]
            elif creer_si_absent:
                metadata = {"name": segment, "mimeType": self.MIME_DOSSIER, "parents": [parent_id]}
                dossier_id = self._service.files().create(body=metadata, fields="id").execute()["id"]
            else:
                raise DriveNoSuchKey(f"Dossier '{cle_partielle}' introuvable sous la racine Drive.")

            self._cache_dossiers[cle_partielle] = dossier_id
            parent_id = dossier_id

        return parent_id

    @staticmethod
    def _decouper_cle(cle: str) -> tuple[list[str], str]:
        segments = cle.split("/")
        return segments[:-1], segments[-1]

    def _trouver_fichier(self, cle: str) -> Optional[dict]:
        segments_dossier, nom_fichier = self._decouper_cle(cle)
        try:
            parent_id = self._resoudre_dossier(segments_dossier, creer_si_absent=False)
        except DriveNoSuchKey:
            return None
        requete = f"'{parent_id}' in parents and name = '{_echapper_nom_drive(nom_fichier)}' and trashed = false"
        resultats = self._service.files().list(
            q=requete, fields="files(id, name, size)", pageSize=1,
        ).execute().get("files", [])
        return resultats[0] if resultats else None

    def put_object(self, Key: str, Body: bytes) -> None:
        segments_dossier, nom_fichier = self._decouper_cle(Key)
        parent_id = self._resoudre_dossier(segments_dossier, creer_si_absent=True)
        media = _DriveMediaUpload(io.BytesIO(Body), mimetype="application/octet-stream", resumable=False)
        existant = self._trouver_fichier(Key)
        if existant is not None:
            self._service.files().update(fileId=existant["id"], media_body=media).execute()
        else:
            metadata = {"name": nom_fichier, "parents": [parent_id]}
            self._service.files().create(body=metadata, media_body=media, fields="id").execute()

    def get_object(self, Key: str) -> dict:
        fichier = self._trouver_fichier(Key)
        if fichier is None:
            raise DriveNoSuchKey(f"Clé introuvable : '{Key}'")
        requete = self._service.files().get_media(fileId=fichier["id"])
        buffer = io.BytesIO()
        downloader = _DriveMediaDownload(buffer, requete)
        termine = False
        while not termine:
            _, termine = downloader.next_chunk()
        buffer.seek(0)
        return {"Body": buffer}

    def head_object(self, Key: str) -> dict:
        fichier = self._trouver_fichier(Key)
        if fichier is None:
            raise DriveNoSuchKey(f"Clé introuvable : '{Key}'")
        return fichier

    def list_objects_v2(self, Prefix: str = "") -> dict:
        """PATCH (bug post-migration B2 -> Drive : contrairement à S3/B2,
        où un préfixe liste TOUTES les clés en dessous quelle que soit
        leur profondeur -- pas de vrais dossiers --, Drive a de vrais
        sous-dossiers, et la version précédente de cette méthode ne
        listait que les enfants DIRECTS du dossier résolu, en excluant
        les sous-dossiers eux-mêmes de la sortie. Résultat : tout ce qui
        vivait sous un sous-dossier -- ex. "App/AutoniaX.py" -- restait
        invisible pour list_objects_v2("") (racine), et l'onglet
        "Stockage cloud" affichait "(bucket vide)" même quand Drive
        contenait bel et bien des fichiers. Cette version descend
        récursivement dans chaque sous-dossier rencontré pour reproduire
        fidèlement le comportement plat qu'attend le reste du code
        (StockageCloudScreen._construire_noeuds_arborescence_stockage
        reconstruit lui-même une arborescence à partir de clés plates,
        exactement comme avec B2)."""
        prefixe_nettoye = Prefix.rstrip("/")
        segments_dossier = [s for s in prefixe_nettoye.split("/") if s] if prefixe_nettoye else []
        try:
            parent_id = self._resoudre_dossier(segments_dossier, creer_si_absent=False)
        except DriveNoSuchKey:
            return {"Contents": []}
        prefixe_affiche = f"{prefixe_nettoye}/" if prefixe_nettoye else ""
        contenu = self._lister_recursif(parent_id, prefixe_affiche)
        return {"Contents": contenu}

    def _lister_recursif(self, dossier_id: str, prefixe_affiche: str) -> list[dict]:
        """Descend récursivement sous dossier_id, en accumulant
        {"Key": ..., "Size": ...} pour chaque FICHIER rencontré (jamais
        les dossiers eux-mêmes, cohérent avec le comportement plat de
        S3/B2) -- cf. docstring de list_objects_v2 pour le contexte."""
        requete = f"'{dossier_id}' in parents and trashed = false"
        resultats = self._service.files().list(
            q=requete, fields="files(id, name, size, mimeType)", pageSize=1000,
        ).execute().get("files", [])
        contenu: list[dict] = []
        for f in resultats:
            if f.get("mimeType") == self.MIME_DOSSIER:
                contenu.extend(
                    self._lister_recursif(f["id"], f"{prefixe_affiche}{f['name']}/")
                )
            else:
                contenu.append({
                    "Key": f"{prefixe_affiche}{f['name']}",
                    "Size": int(f.get("size", 0)),
                })
        return contenu

    def delete_object(self, Key: str) -> None:
        fichier = self._trouver_fichier(Key)
        if fichier is not None:
            self._service.files().delete(fileId=fichier["id"]).execute()

    def copy_object(self, CopySource: dict, Key: str) -> None:
        cle_source = CopySource["Key"]
        fichier_source = self._trouver_fichier(cle_source)
        if fichier_source is None:
            raise DriveNoSuchKey(f"Clé source introuvable : '{cle_source}'")
        segments_dossier, nom_fichier = self._decouper_cle(Key)
        parent_id = self._resoudre_dossier(segments_dossier, creer_si_absent=True)
        metadata = {"name": nom_fichier, "parents": [parent_id]}
        self._service.files().copy(fileId=fichier_source["id"], body=metadata).execute()


# PATCH (migration Render -> Colab+tunnel Cloudflare -- demande explicite
# utilisateur : "a cause des limitaitons de render jai decider de faire
# une migrations ... on execute mon code serveur sur un notebook collab
# ... et on utilise un tunnels cloudflare pour le rendre accelible
# publiquement") -- clé de service Drive EN DUR (même décision déjà
# actée pour B2 : "voila les identifiant de BB que tu vas stoker en dure
# dans les fichier ... ce sont mes identifiant ... cest pas pour la
# production cest un projet personnels", reconduite telle quelle pour
# Drive), séparée de GestionnaireStockage ci-dessous (config profils,
# reçue par message WebSocket -- ce mécanisme-là reste INCHANGÉ, seuls
# les champs transmis changent, cf. plus bas). Ce second accès Drive est
# nécessaire pour marquer_serveur_a_jour() (cf. plus bas) : ce serveur,
# une fois qu'un nouveau serveur.py vient d'être poussé depuis mAutoniax,
# doit pouvoir écrire ServeurT/stat.json {"updated": true} de lui-même --
# impossible avec le seul mécanisme par message WebSocket, qui suppose
# déjà une connexion active.
#
# À REMPLACER : coller ici le contenu JSON complet de la clé de service
# (Google Cloud Console -> IAM & Admin -> Comptes de service -> Clés ->
# Ajouter une clé -> JSON). Le placeholder ci-dessous ne fonctionnera
# pas tel quel.
DRIVE_CLE_SERVICE_JSON = {
    "type": "service_account",
    "project_id": "able-marking-506808-a8",
    "private_key_id": "0dcb47d8b9532953e5f20a9abc006ec2bca3f6fc",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCr9p+6s4oFMKgc\nAVxCnwbZISreYrby9A/+jg3Nsw2uZ7dnV5x9J9FKcdIjWpNAt2hY46/PPlLvvUJ+\nlRzsEABnsVjRr9paVkmOqFRpJKUKdU6DxK6iMGqOy1vCR+7HsFo3RK4Oi6MnzHew\nhzt9/Hd0NvbUO/giXGaIxfw6iuCz+WrJNDb5H0FG8vd47mkViqySvix6+km1v4/X\nyQI/1CAv1uSgw72e/tmBg92IUFelVGnbkKwKv1sWcPVxcqNHraxuVu0IhRMpBYyr\nBhHrOmsXcNmEnJtQvk0ykJ3gozRIPuENLS+ev4FvCq+NGwDrYVz02RM7m1tz9w8g\nRuqkjz8dAgMBAAECggEABQgGvWIyaBt317XseqCHhUPUqsQNoUclzqdeXQXfoRo0\nwgfMsta+52Q0J0enpk2Xdn5W7wPeTlhlwSlgusFvGZmVRTFVfK4ooc1oBtmFIKy0\n+uL+zw0GmR33FdSf9mTBBvvx8cgBIpF3cQlL4tBHuHVBPI1yoaK9d0P/sMDOeUWH\nGLz4477Y0m4YIUWxNC4ZHK/3IuXBeb6mGFrmr8JBs8PirHaVIBR/adYo4fimf0r9\nsYGo88oHKS2IpZmWNC+D8HQ/4yEzmDQ0+V6u2dtH0a4FGogaMdDFg7RQLMX5Ekja\n4G38KxeS8PaVm+K8ArdnBwwsDsP9dOneS3mO3ao+UQKBgQDk7O5D+O4O29xkASNb\nXqFQvQ4PR3y7RpCxLtMOKLXIP2IOiusAB2SKqvbu5AuU/MRa9EXrRDtPpzRXhrCB\nTEfg4+/GvpxLKUObMH6hl6zmDi00eOnuiwPDO/IyjXVlS0E3y+ufoYF4m6DQ1Kmh\nxaCo9GyFldabFAfjY25JznjmeQKBgQDATRPd8b3njPGFESZgLBct79hSwX1fgag/\nyTQHXFl+DXuFERKrv04CbWdjLQrSjamgbTgiYEB/KGKfgFJp1tqp97hX1gNi0DBU\ndsUW8COgAosqrfLLfXBl/IQiax+tcY1tRa4oT4RjZ82oL9G2AB2GWVArQtVX6xJ0\np03vgkwExQKBgQDQybbVj6evLZ7oJpGUt83w0TyNeumr9EPrFYWwmDiTFhvcn56N\nPDDat+rXHm3hyFddjQRn+qcNkrYOTe2VP3kfB0ScwyPQ+SWL2MLlpmwutidMgCr7\nQRaBbZ8LtDCp3eTxeq6/vJFU6rvVOuArhw9siOChRXOhpLc9EGZ6MjHaIQKBgQCT\nL+vO6yNBwf1yrmfDILw1KulWnkbJ/UG8YNJz99l/w+4RMboqvuiErxx9KpKoCkoV\nQsO+fBGhwlWKY/uwiwUfJz5v7Jz22wbC/41nOzLpXEkMx8uYuVB4n0i712aNqOZp\nBvaAYCyisWcWHlPTjE8M7/uOwT7uZjzgENZ0RjTNSQKBgQC/iKLAnNf9R0QabiYd\nRyXDQjAyaqiaPQX6qW6Q8X9hj+JAgM39UlAXtAU2dDW3cXw/0Cedt7kI8pO58pR2\nnipySG1a73qUC9e6P1ygF4v7V8zmpo0HxjgNX4A92Honi4ZxqXM0QUaOabNk/fG1\n3r5fCBBVAzU+Cqvoru/NsagndQ==\n-----END PRIVATE KEY-----\n",
    "client_email": "autoniax-storage@able-marking-506808-a8.iam.gserviceaccount.com",
    "client_id": "109049196207223821545",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/autoniax-storage%40able-marking-506808-a8.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}
DRIVE_DOSSIER_RACINE_ID = "1mOSb2L3N1ebkgCb5S5d7fjBUJRLVggGJ"  # même dossier racine que côté AutoniaX.py (ReglagesApp.drive_dossier_racine_id)

# CORRECTIF (nettoyage -- incohérence relevée entre ce fichier et
# ServeurTLauncher.ipynb) : ce module NE PUBLIE PAS l'URL du tunnel
# (ServeurT/url_tunnel.txt) -- c'est le notebook ServeurT Manager,
# seul, qui s'en charge (cf. etape_4_publier_url_tunnel du notebook),
# juste après avoir lui-même capté l'URL dans la sortie de cloudflared.
# Ce serveur n'a connaissance ni de l'URL de son propre tunnel ni même
# de l'existence de cloudflared -- normal, cloudflared tourne comme un
# process totalement séparé, lancé par le notebook, pas par ce script.
#
# Tout le stockage lié au serveurT lui-même (script + statut de mise à
# jour + URL tunnel) vit sous le préfixe ServeurT/ du dossier racine
# Drive (décision explicite utilisateur : "il faut creer un dosseir :
# ServeurT ... ne toke pas tout directement a la racine"), distinct de
# Profils/ (déjà utilisé par GestionnaireStockage/profils cf. reste du
# fichier).
DRIVE_PREFIXE_SERVEURT = "ServeurT/"
DRIVE_CLE_SCRIPT_SERVEUR = DRIVE_PREFIXE_SERVEURT + "serveur.py"
DRIVE_CLE_STAT = DRIVE_PREFIXE_SERVEURT + "stat.json"
DRIVE_CLE_URL_TUNNEL = DRIVE_PREFIXE_SERVEURT + "url_tunnel.txt"


class GestionnaireStockageBB:
    """Client Drive AUTONOME, clé de service en dur (cf. commentaire
    ci-dessus) -- utilisé UNIQUEMENT pour ServeurT/stat.json, ÉCRIT
    depuis ce process (cf. marquer_serveur_a_jour plus bas). ServeurT/
    serveur.py et ServeurT/url_tunnel.txt vivent sous le même préfixe
    Drive mais sont entièrement gérés côté notebook ServeurT Manager
    (ServeurTLauncher.ipynb) -- ce process-ci ne les lit ni ne les
    écrit jamais lui-même (cf. DRIVE_CLE_URL_TUNNEL/DRIVE_CLE_SCRIPT_
    SERVEUR ci-dessus, définies seulement pour documenter le contrat
    partagé, PAS pour un usage direct dans cette classe). Aucun lien
    avec GestionnaireStockage (config profils par message WebSocket,
    cf. plus bas) -- deux clients Drive distincts qui peuvent même
    pointer vers des dossiers racine différents si besoin un jour, sans
    aucune dépendance entre eux.

    Nom de classe conservé tel quel (GestionnaireStockageBB, "BB" pour
    Backblaze) malgré la migration -- renommer casserait le commentaire
    d'instanciation ci-dessous (bb_stockage) et tous les commentaires
    qui la référencent dans ce fichier ; seul le contenu change ici,
    pas l'API publique ni le nom.

    Instancié UNE FOIS au niveau module (cf. bb_stockage plus bas) --
    stateless mis à part le client Drive lui-même, aucune raison d'en
    recréer un par appel."""

    def __init__(self):
        self._client = _ClientDriveMinimal(
            cle_service_json=DRIVE_CLE_SERVICE_JSON,
            dossier_racine_id=DRIVE_DOSSIER_RACINE_ID,
        )

    def marquer_serveur_a_jour(self, updated: bool) -> None:
        """Écrit ServeurT/stat.json avec le champ "updated" -- True juste
        après qu'un nouveau serveur.py a été poussé vers Drive (cf. son
        appelant dans mettre_a_jour_app_fin ci-dessus), False par le
        notebook ServeurT Manager lui-même une fois le nouveau script
        téléchargé et sur le point d'être relancé (cf. CONTENU_NOTEBOOK_
        SERVEURT_MANAGER côté AutoniaX.py, qui écrit directement sur
        Drive avec ses PROPRES identifiants -- ce serveur en cours
        d'exécution n'a aucun rôle dans cette remise à False, il peut
        même avoir déjà été tué à ce moment-là). Remplace tout le
        contenu de stat.json (pas de fusion de champs) -- un seul champ
        y vit pour l'instant, pas de risque d'écraser autre chose ; si
        stat.json grossit un jour avec d'autres champs, cette méthode
        devra lire-modifier-écrire plutôt qu'écraser."""
        try:
            contenu = json.dumps({"updated": updated}).encode("utf-8")
            self._client.put_object(Key=DRIVE_CLE_STAT, Body=contenu)
            logger.info("stat.json mis à jour sur Drive (%s) : updated=%s", DRIVE_CLE_STAT, updated)
        except Exception as e:
            logger.warning("Échec d'écriture de stat.json sur Drive : %r", e)


# PATCH (recompression par pilote -- demande explicite utilisateur : "les
# capture doivent arriver désormais sur le serveurT avec le webp 100
# pourcent, et maintenant le serveurT pour renvoyer chez nous on va nous
# même modifier les paramètres" -- réglage résolution/qualité PAR PILOTE,
# cf. Connexion.preference_capture et _recompresser_pour_diffusion plus
# bas). Import défensif (même patron que PILLOW_DISPONIBLE côté
# AutoniaX.py) : si Pillow n'est pas encore présent dans l'environnement
# Render (ex. redéploiement pas encore fait après ce patch), le relais
# de capture retombe simplement sur l'image reçue telle quelle (qualité
# 100 brute, cf. son fallback plus bas) plutôt que de faire planter tout
# le serveur pour ce seul motif.
try:
    from PIL import Image as PILImage
    PILLOW_DISPONIBLE = True
except ImportError:
    PILLOW_DISPONIBLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
# BUGFIX (bouton "Copier les logs de cette execution" cote AutoniaX.py --
# constat : la section "Serveur (serveurT)" ressortait TOUJOURS vide) --
# sans ceci, logging.Formatter utilise time.localtime par defaut, donc
# %(asctime)s est ecrit dans le fuseau horaire LOCAL de la machine qui
# heberge ce process (ex. Kaggle/Colab/Render, fuseau non garanti et
# potentiellement different de la machine mAutoniax qui lit ces logs) --
# un decalage constate d'environ 1h entre les deux, qui ne peut PAS etre
# corrige de facon fiable cote client puisqu'il n'est ni nul ni connu a
# l'avance. Forcer logging.Formatter.converter sur time.gmtime fait
# ecrire %(asctime)s en UTC, independamment du fuseau de la machine hote
# -- AutoniaX.py (_horodatage_estime_depuis_ligne_log) suppose desormais
# explicitement de l'UTC pour cette source, donc les deux cotes doivent
# rester alignes si ce choix change un jour.
logging.Formatter.converter = time.gmtime
logger = logging.getLogger("serveurT")

# PATCH (Profils Kaggle, phase 3) -- types relayes par le sous-onglet "Profils Kaggle".
TYPES_KAGGLE_PILOTE_VERS_EXECUTANT = frozenset({
    "kaggle_lister_profils", "kaggle_envoyer_profils", "kaggle_telecharger_profils",
})
TYPES_KAGGLE_EXECUTANT_VERS_PILOTE = frozenset({
    "kaggle_lister_profils_resultat", "kaggle_progression", "kaggle_resultat",
})
bb_stockage = GestionnaireStockageBB()  # cf. sa définition plus haut ; instancié ici, APRÈS logger (utilisé par marquer_serveur_a_jour)


# PATCH (bouton "Copier tous les logs", 3 sources -- demande explicite
# utilisateur : "sa doit copier tout les logs depuis le demarage, pas
# juste les n dernier ligne"). Buffer EN MÉMOIRE, SANS PLAFOND -- pas de
# deque(maxlen=...) : toute ligne loguée depuis le démarrage du process
# est gardée, jusqu'au prochain redémarrage Render (mémoire simple,
# cohérent avec Registre plus haut -- aucune persistance disque/DB
# voulue ici). Alimenté par TamponJournalMemoire ci-dessous, attaché au
# logger RACINE (pas seulement "serveurT") pour capturer aussi les
# lignes émises par uvicorn/fastapi eux-mêmes, utiles au diagnostic.
class TamponJournalMemoire(logging.Handler):
    """Handler logging qui accumule chaque ligne formatée dans une liste
    Python simple, exposée telle quelle par la route GET /logs (cf. plus
    bas) et par le message WS "logs_executant" côté sAutoniax (même
    patron de handler, dupliqué dans AutoniaX.py -- pas de code partagé
    entre les deux fichiers, cf. en-tête : "projet à part, aucune
    dépendance au reste du code AutoniaX")."""

    def __init__(self):
        super().__init__()
        self.lignes: list[str] = []

    def emit(self, record: logging.LogRecord):
        try:
            self.lignes.append(self.format(record))
        except Exception:
            # Une erreur de formatage sur UNE ligne ne doit jamais faire
            # planter le logging lui-même (cf. patron standard
            # logging.Handler.handleError, ici simplement absorbée).
            pass


tampon_journal = TamponJournalMemoire()
tampon_journal.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logging.getLogger().addHandler(tampon_journal)

app = FastAPI()

# Rôles acceptés dans le message "register" -- cf. cahier section 5.2.
ROLES_VALIDES = {"pilote", "executant"}


class GestionnaireStockage:
    """Enveloppe autour de DriveStockage (PATCH -- migration totale
    Backblaze B2 -> Google Drive, cf. commentaire d'en-tête pour la
    raison du changement ; anciennement Cloudflare R2 avant B2).

    Config reçue via le message "configurer_stockage" (envoyé par
    mAutoniax -- cf. ClientServeurT._envoyer_config_stockage côté
    AutoniaX.py), PAS via variables d'environnement Render (choix
    explicite utilisateur : "Champ dans les Réglages d'AutoniaX, envoyé
    au serveur"). Conséquence : aucune persistance disque ici -- le
    serveurT oublie la config à chaque redémarrage, mAutoniax la
    renvoie systématiquement à chaque (re)connexion (cf. serveur.py
    route_websocket, comportement symétrique côté client).

    Générique dès maintenant (upload/download/liste par clé) plutôt que
    couplé à un type de fichier précis -- le type exact de fichiers à
    transiter en premier n'est pas encore tranché (cf. cahier Étape 9,
    "à mentionner plus tard"), donc rien ici ne présuppose "profil" vs
    "capture d'écran" vs autre chose."""

    def __init__(self):
        self._client = None
        self._dossier_racine_id: Optional[str] = None
        self._configure_par: Optional[str] = None  # id_connexion du pilote qui a configuré

    @property
    def configure(self) -> bool:
        return self._client is not None and self._dossier_racine_id is not None

    @staticmethod
    async def _a_thread(fonction_bloquante, *args):
        """CORRECTIF (bug identifié : TimeoutError() systématique côté
        client après 30s sur telecharger_fichier_debut/_chunk, alors que
        le serveur finissait par répondre -- juste trop tard). Cause
        réelle : _ClientDriveMinimal (googleapiclient) est 100% SYNCHRONE
        (.execute() bloquant, aucun await) -- appelé directement depuis
        route_websocket (coroutine sur LA SEULE boucle asyncio du
        process), chaque appel Drive (list/get_media/create/...) BLOQUE
        TOUT le serveur pendant sa propre durée : plus aucune connexion
        WebSocket (y compris celle qui attend son ack) n'est traitée
        tant que Drive n'a pas répondu. Si Drive met plus de 30s (dossier
        profond à résoudre, fichier volumineux, latence Google), le
        client abandonne (timeout_s=30.0 côté _attendre_ack_telechargement)
        avant même que le serveur ait pu envoyer l'ack.
        Fix : déporter CHAQUE appel bloquant dans un threadpool -- l'event
        loop reste libre de traiter les autres connexions/heartbeats
        pendant que Drive répond, exactement comme le fait déjà
        recompresser_pour_diffusion plus bas dans ce fichier.

        CORRECTIF ROBUSTESSE (cf. commentaire d'en-tête du fichier,
        section EXECUTOR_TRAVAIL_BLOQUANT_MAX_WORKERS -- crash serveur
        -11/SIGSEGV sous forte charge) : utilise désormais l'executor
        DÉDIÉ et borné (_executor_travail_bloquant), plus le pool par
        défaut illimité, et passe par le sémaphore
        (_semaphore_travail_bloquant) pour ne jamais avoir plus de
        EXECUTOR_TRAVAIL_BLOQUANT_MAX_WORKERS appels Drive (ou Pillow,
        cf. envoyer_capture) réellement en vol en même temps -- les
        autres attendent simplement leur tour, aucune perte, juste un
        étalement dans le temps au lieu d'un pic incontrôlé."""
        loop = asyncio.get_running_loop()
        async with _semaphore_travail_bloquant:
            return await loop.run_in_executor(_executor_travail_bloquant, fonction_bloquante, *args)

    def configurer(self, cle_service_json: str, dossier_racine_id: str, configure_par: str) -> None:
        """cle_service_json : contenu JSON complet (texte, pas un
        chemin -- ce process tourne sur Colab, une machine distante de
        celle de l'utilisateur, cf. _config_stockage_depuis_reglages
        côté AutoniaX.py qui lit le fichier local et envoie son
        CONTENU). Parsé ici en dict pour _ClientDriveMinimal, qui prend
        directement les identifiants en mémoire (Credentials.from_
        service_account_info) -- aucun fichier local nécessaire côté
        Colab (contrairement à un essai précédent), même esprit que
        DRIVE_CLE_SERVICE_JSON déjà en dict plus haut dans ce fichier."""
        infos_cle = json.loads(cle_service_json)
        self._client = _ClientDriveMinimal(
            cle_service_json=infos_cle,
            dossier_racine_id=dossier_racine_id,
        )
        self._dossier_racine_id = dossier_racine_id
        self._configure_par = configure_par
        logger.info("Stockage Drive configuré (dossier_racine_id=%s)", dossier_racine_id)

    # ------------------------------------------------------------------
    # CORRECTIF -- toutes les méthodes publiques ci-dessous sont
    # maintenant des coroutines (async def) : chacune délègue son appel
    # Drive synchrone à _a_thread (run_in_executor) plutôt que de
    # bloquer l'event loop. Les implémentations synchrones d'origine
    # sont conservées telles quelles, préfixées "_sync_", et appelées
    # UNIQUEMENT via _a_thread -- jamais directement depuis route_
    # websocket. Signatures publiques inchangées à l'exception du mot-clé
    # async/await ajouté aux appelants (cf. route_websocket).
    # ------------------------------------------------------------------

    def _sync_uploader_bytes(self, cle: str, contenu: bytes) -> None:
        if not self.configure:
            raise RuntimeError("Stockage non configuré")
        self._client.put_object(Key=cle, Body=contenu)

    async def uploader_bytes(self, cle: str, contenu: bytes) -> None:
        await self._a_thread(self._sync_uploader_bytes, cle, contenu)

    def _sync_telecharger_bytes(self, cle: str) -> bytes:
        if not self.configure:
            raise RuntimeError("Stockage non configuré")
        reponse = self._client.get_object(Key=cle)
        return reponse["Body"].read()

    async def telecharger_bytes(self, cle: str) -> bytes:
        return await self._a_thread(self._sync_telecharger_bytes, cle)

    def _sync_existe(self, cle: str) -> bool:
        if not self.configure:
            raise RuntimeError("Stockage Drive non configuré")
        try:
            self._client.head_object(Key=cle)
            return True
        except DriveNoSuchKey:
            return False

    async def existe(self, cle: str) -> bool:
        return await self._a_thread(self._sync_existe, cle)

    def _sync_lister(self, prefixe: str = "") -> list[str]:
        if not self.configure:
            raise RuntimeError("Stockage Drive non configuré")
        reponse = self._client.list_objects_v2(Prefix=prefixe)
        return [obj["Key"] for obj in reponse.get("Contents", [])]

    async def lister(self, prefixe: str = "") -> list[str]:
        return await self._a_thread(self._sync_lister, prefixe)

    def _sync_lister_avec_taille(self, prefixe: str = "") -> list[dict]:
        """Comme _sync_lister, mais renvoie aussi la taille en octets de
        chaque objet (PATCH -- demande explicite utilisateur : "on
        affiche la taille des fichiers py à côté d'eu" dans l'onglet
        Stockage cloud). list_objects_v2 renvoie déjà "Size" par objet
        (cf. _sync_lister ci-dessus qui le jetait) -- pas d'appel
        supplémentaire nécessaire, juste ne plus jeter cette info."""
        if not self.configure:
            raise RuntimeError("Stockage Drive non configuré")
        reponse = self._client.list_objects_v2(Prefix=prefixe)
        return [
            {"cle": obj["Key"], "taille_octets": obj["Size"]}
            for obj in reponse.get("Contents", [])
        ]

    async def lister_avec_taille(self, prefixe: str = "") -> list[dict]:
        return await self._a_thread(self._sync_lister_avec_taille, prefixe)

    def _sync_supprimer(self, cle: str) -> None:
        """Supprime UN objet par sa clé complète (PATCH -- demande
        explicite utilisateur : "je veux que on puisse désormais
        supprimer un élément directement, clic droit et supprimer" dans
        l'onglet Stockage cloud). delete_object (DriveStockage) est
        idempotent comme son équivalent S3 -- ne lève pas d'erreur si la
        clé n'existe déjà plus, l'appelant (StockageCloudScreen)
        s'appuie sur sa propre confirmation utilisateur avant l'appel,
        pas sur une vérification d'existence préalable ici."""
        if not self.configure:
            raise RuntimeError("Stockage Drive non configuré")
        self._client.delete_object(Key=cle)

    async def supprimer(self, cle: str) -> None:
        await self._a_thread(self._sync_supprimer, cle)

    def _sync_renommer(self, cle_source: str, cle_destination: str) -> None:
        """Renomme UN objet (PATCH -- boutons "Renommer"/"Supprimer" de
        Profils Cloud, demande explicite utilisateur). Drive n'a pas de
        vraie opération "rename" atomique par clé façon S3 : on simule
        via copy_object (source -> destination) puis delete_object
        (source), même esprit que _sync_supprimer juste au-dessus (aucune
        vérification métier ici, l'appelant -- handler renommer_profil_
        cloud -- vérifie lui-même que la clé destination n'est pas déjà
        prise avant d'appeler ceci). Si delete_object échoue après un
        copy_object réussi, l'objet source persiste en doublon plutôt
        que de perdre les données -- préférence explicite pour un échec
        visible/rattrapable côté UI (message d'erreur renvoyé) plutôt
        qu'une perte silencieuse."""
        if not self.configure:
            raise RuntimeError("Stockage Drive non configuré")
        self._client.copy_object(
            CopySource={"Key": cle_source},
            Key=cle_destination,
        )
        self._client.delete_object(Key=cle_source)

    async def renommer(self, cle_source: str, cle_destination: str) -> None:
        await self._a_thread(self._sync_renommer, cle_source, cle_destination)


stockage = GestionnaireStockage()


# =====================================================================================================
# TRANSIT DRIVE (spec « Transit Drive : sortir les données lourdes du pont pilote », étape 2)
# -----------------------------------------------------------------------------------------------------
# Les données lourdes (images, SVG, zips, profils) ne passent plus par ce serveur : celui qui possède la
# donnée l'écrit lui-même dans un zip pré-créé de Transit/ (data1.zip ... dataN.zip) sur Drive, avec le
# compte de service, et l'autre côté le télécharge directement. CE SERVEUR NE VOIT JAMAIS LES DONNÉES : il
# tient seulement la table des zips (libre / occupé) pour que deux transferts simultanés n'utilisent jamais
# le même zip, et ne fait que deux choses : ATTRIBUER un zip libre, et le REPRENDRE quand son destinataire
# a fini de le lire.
#
# Au premier appel, Transit/ est lu UNE fois (nom dataN.zip -> fileId) ; ensuite tout se fait par fileId.
# Aucun fichier n'est créé ici (le compte de service ne peut pas en créer : quota) -- les emplacements sont
# pré-créés par l'utilisateur, le compte de service ne fait que les écraser.
#
# Jeton : chaque attribution renvoie un « jeton » aléatoire, exigé à la libération. Il protège contre une
# libération en double (reprise réseau) arrivant APRÈS que le zip a été réattribué à un autre transfert.
# Pas (encore) de délai maximal d'utilisation : « depuis » est mémorisé pour l'ajouter plus tard.
import re as _re_transit

DRIVE_DOSSIER_TRANSIT = "Transit"
_TRANSIT_NOM_RE = _re_transit.compile(r"^data(\d+)\.zip$")


class GestionnaireTransit:
    def __init__(self):
        self._emplacements: dict = {}      # "data7.zip" -> {"file_id", "jeton", "occupe_par", "depuis"}
        self._ordre: list = []             # noms triés par numéro (data1, data2, ... data10, ...)
        self._initialise = False
        self._verrou_init = None           # asyncio.Lock créé paresseusement (dans la boucle)

    @staticmethod
    def _lire_dossier_transit_sync(client) -> dict:
        """Bloquant (à lancer dans le threadpool) : {nom: fileId} des fichiers dataN.zip de Transit/."""
        dossier_id = client._resoudre_dossier([DRIVE_DOSSIER_TRANSIT], creer_si_absent=False)
        table: dict = {}
        page = None
        while True:
            reponse = client._service.files().list(
                q=f"'{dossier_id}' in parents and trashed = false and mimeType != '{client.MIME_DOSSIER}'",
                fields="nextPageToken, files(id, name)", pageSize=1000, pageToken=page,
            ).execute()
            for f in reponse.get("files", []):
                if _TRANSIT_NOM_RE.match(f["name"]):
                    if f["name"] in table:
                        logger.warning("Transit : '%s' existe en double dans Drive, le premier est gardé.", f["name"])
                        continue
                    table[f["name"]] = f["id"]
            page = reponse.get("nextPageToken")
            if not page:
                return table

    async def _assurer_initialise(self) -> None:
        if self._initialise:
            return
        if self._verrou_init is None:
            self._verrou_init = asyncio.Lock()
        async with self._verrou_init:
            if self._initialise:
                return
            loop = asyncio.get_running_loop()
            async with _semaphore_travail_bloquant:
                table = await loop.run_in_executor(
                    _executor_travail_bloquant, self._lire_dossier_transit_sync, bb_stockage._client,
                )
            if not table:
                raise RuntimeError(f"Le dossier {DRIVE_DOSSIER_TRANSIT}/ ne contient aucun fichier dataN.zip.")
            self._ordre = sorted(table, key=lambda n: int(_TRANSIT_NOM_RE.match(n).group(1)))
            self._emplacements = {
                nom: {"file_id": table[nom], "jeton": None, "occupe_par": None, "depuis": None}
                for nom in self._ordre
            }
            self._initialise = True       # APRÈS la construction : un échec laisse la table vide et retente au prochain appel
            logger.info("Transit : %d zips trouvés (%s ... %s)", len(self._ordre), self._ordre[0], self._ordre[-1])

    def nb_occupes(self) -> int:
        return sum(1 for e in self._emplacements.values() if e["jeton"] is not None)

    async def demander(self, id_connexion: str, nom_demandeur: str) -> dict:
        """Attribue le premier zip libre. Aucun await entre la recherche et la réservation : deux demandes
        simultanées ne peuvent pas obtenir le même zip (une seule boucle asyncio)."""
        await self._assurer_initialise()
        for nom in self._ordre:
            e = self._emplacements[nom]
            if e["jeton"] is None:
                e["jeton"] = uuid.uuid4().hex
                e["occupe_par"] = id_connexion
                e["depuis"] = time.time()
                logger.info("Transit : %s attribué à '%s' (%d/%d occupés)", nom, nom_demandeur or id_connexion,
                            self.nb_occupes(), len(self._ordre))
                return {"ok": True, "slot": nom, "file_id": e["file_id"], "jeton": e["jeton"]}
        logger.warning("Transit : plein (%d zips occupés), demande de '%s' refusée", len(self._ordre), nom_demandeur or id_connexion)
        return {"ok": False, "plein": True, "erreur": f"Transit plein : les {len(self._ordre)} zips sont tous occupés."}

    def liberer(self, nom: str, jeton: str) -> dict:
        """Remet un zip dans la liste des libres. Idempotent : libérer un zip déjà libre répond ok (reprise réseau).
        Un jeton qui ne correspond pas à l'attribution en cours est refusé (zip réattribué entre-temps)."""
        e = self._emplacements.get(nom)
        if e is None:
            return {"ok": False, "erreur": f"Zip inconnu : {nom!r}."}
        if e["jeton"] is None:
            return {"ok": True, "deja_libre": True}
        if e["jeton"] != jeton:
            logger.warning("Transit : libération de %s refusée (jeton périmé)", nom)
            return {"ok": False, "erreur": "Jeton périmé : ce zip a été réattribué à un autre transfert."}
        duree = time.time() - (e["depuis"] or time.time())
        e["jeton"] = None
        e["occupe_par"] = None
        e["depuis"] = None
        logger.info("Transit : %s libéré après %.1fs (%d/%d occupés)", nom, duree, self.nb_occupes(), len(self._ordre))
        return {"ok": True}


transit = GestionnaireTransit()


class UploadProfilEnCours:
    """État d'un envoi de profil en cours de réception, EN CHUNKS (PATCH
    -- demande explicite utilisateur : "vraie progression par chunks
    (envoi découpé en morceaux, % précis pendant l'upload)"). Un seul
    upload à la fois PAR CONNEXION (pas de dict indexé par nom_profil :
    envoyer_profil_debut réinitialise/remplace tout upload précédent
    non terminé pour cette connexion -- cf. cahier "simple et fiable
    suffit"). Le fichier temporaire est écrit en ajout (mode "ab") au
    fil des chunks reçus, PAS accumulé en mémoire -- un profil peut
    peser plusieurs centaines de Mo, garder ça en RAM serait risqué.
    Nettoyé (fichier temp supprimé) soit à la fin normale
    (envoyer_profil_fin), soit à la déconnexion (cf. route_websocket,
    bloc finally) pour ne jamais laisser un fichier orphelin sur
    disque si le client coupe la connexion en plein envoi."""

    def __init__(self, nom_profil: str, taille_totale_octets: int, nb_chunks: int):
        self.nom_profil = nom_profil
        self.taille_totale_octets = taille_totale_octets
        self.nb_chunks_attendus = nb_chunks
        self.prochain_index_attendu = 0
        # Fichier temporaire nommé de façon unique (uuid4) -- évite toute
        # collision si, malgré l'attente normale d'un seul upload par
        # connexion, deux sessions se chevauchaient un jour.
        self.chemin_temp = Path(tempfile.gettempdir()) / f"serveurT_profil_{uuid.uuid4().hex}.zip"

    def ecrire_chunk(self, contenu_bytes: bytes) -> None:
        with open(self.chemin_temp, "ab") as f:
            f.write(contenu_bytes)

    def nettoyer(self) -> None:
        self.chemin_temp.unlink(missing_ok=True)


# RETRAIT (migration "Mettre à jour" vers Drive direct -- demande
# explicite utilisateur : "mAutoniax upload directement ... plus de
# envoie autonome de fichier du serveur vers les sautoniax") : l'ancienne
# classe UploadAppEnCours (état d'un envoi mettre_a_jour_app EN COURS de
# réception, EN CHUNKS, côté serveur) a été entièrement retirée -- plus
# aucun octet de fichier (AutoniaX.py, mouseData.sqlite3, project.json,
# service_api.zip, serveur.py) ne transite par ce serveur ni pour le
# Flux A ("Mettre à jour" général, upload direct Drive par le pilote) ni
# pour le Flux B (mise à jour ciblée onglet Instances, upload direct
# Drive + simple message de retéléchargement relayé, cf. handlers
# demander_retelechargement_service_api/_project_json).


class RetourProjetEnCours:
    """État d'accumulation du zip résultat d'un projet EN COURS de
    réception depuis un exécutant (PATCH E.2 -- cf. docstring du champ
    Connexion.retour_projet_en_cours). Même pattern EXACT que
    UploadProfilEnCours : écriture en append sur un fichier temporaire
    unique, jamais accumulé en mémoire. Nettoyé (fichier temp supprimé)
    après upload réussi vers B2 (retour_projet_execute_fin), ou à la
    déconnexion (cf. route_websocket, bloc finally) pour ne jamais
    laisser un fichier orphelin sur disque."""

    def __init__(self, session_id: str, id_pilote: str, nb_chunks: int):
        self.session_id = session_id
        self.id_pilote = id_pilote
        self.nb_chunks_attendus = nb_chunks
        self.prochain_index_attendu = 0
        self.chemin_temp = Path(tempfile.gettempdir()) / f"serveurT_retour_projet_{uuid.uuid4().hex}.zip"

    def ecrire_chunk(self, contenu_bytes: bytes) -> None:
        with open(self.chemin_temp, "ab") as f:
            f.write(contenu_bytes)

    def nettoyer(self) -> None:
        self.chemin_temp.unlink(missing_ok=True)


# Taille de chunk pour le téléchargement générique (telecharger_fichier_
# debut/_chunk/_fin, cf. TelechargementFichierEnCours ci-dessous) --
# MÊME valeur que TAILLE_CHUNK_PROFIL_OCTETS côté client
# (ClientServeurT, AutoniaX.py), pour rester cohérent avec le reste du
# protocole. Testée avec succès en conditions réelles sur mouseData.
# sqlite3 (11 034 624 octets -> 3 chunks) AVANT le passage temporaire à
# un chunk unique -- cf. le commentaire détaillé et sourcé (mesures
# précises : ~6s de latence fixe par aller-retour sur ce tunnel
# Cloudflare gratuit, indépendante de la taille du message) dans
# telecharger_fichier_debut plus bas, qui explique pourquoi le chunk
# unique a de nouveau échoué même une fois le heartbeat applicatif
# corrigé côté client -- ne PAS repasser à len(contenu) sans relire ce
# commentaire.
TAILLE_CHUNK_TELECHARGEMENT_OCTETS = 5 * 1024 * 1024


class TelechargementFichierEnCours:
    """État d'un téléchargement en cours (sens inverse d'UploadProfilEnCours)
    -- PATCH protocole générique de téléchargement (demande explicite
    utilisateur : "sAutoniax vas directement demander la requette au
    serveur et telecharger"). Contrairement à l'upload, le contenu
    entier est déjà connu dès telecharger_fichier_debut (lu depuis B2
    en un seul telecharger_bytes) : il est gardé en mémoire pour cette
    connexion et servi chunk par chunk sur demande explicite du client
    (cf. Phase 2 de ClientServeurT._telecharger_fichier), plutôt que
    relu depuis B2 à chaque chunk. Un seul téléchargement à la fois PAR
    CONNEXION, même logique que UploadProfilEnCours."""

    def __init__(self, cle: str, contenu: bytes, taille_chunk: int):
        self.cle = cle
        self.contenu = contenu
        self.taille_chunk = taille_chunk

    def lire_chunk(self, index: int) -> bytes:
        debut = index * self.taille_chunk
        if debut < 0 or debut >= len(self.contenu):
            raise IndexError(index)
        return self.contenu[debut:debut + self.taille_chunk]


# CHANGEMENT (demande explicite utilisateur : "cest au serveur que sa
# doit compresser ... je veux que dans les parametres de rendue tu mets
# le parametre de compression : 100, 50, 10, webp biensure" + "sa ne
# doit plus redimensionner ... pourquoi sa ne veux pas juste diminuer
# la qualiter") -- ancien mécanisme de redimensionnement par hauteur
# cible (RESOLUTIONS_HAUTEUR_PX, "medium"/"economie") SUPPRIMÉ : la
# recompression ne change plus JAMAIS les dimensions en pixels de
# l'image, quel que soit le réglage choisi -- seule la QUALITÉ de
# compression WebP varie désormais (cf. _recompresser_pour_diffusion,
# qui ne fait plus aucun img.resize()). "resolution" reste dans le
# protocole/Connexion.preference_capture pour ne pas casser le contrat
# existant, mais n'est plus utilisé pour redimensionner -- seule
# "qualite" a un effet réel sur la taille du fichier envoyé.
#
# CHANGEMENT (demande explicite utilisateur : "si on met la compression
# a 5, cette image vas avoir quel taille" -- après vérification que 10
# restait plus lourd que la cible visée) -- palier "5" ajouté SOUS 10
# pour permettre une compression encore plus agressive quand l'aperçu
# fidèle importe moins que la légèreté du flux (ex. simple surveillance
# d'activité). Toujours juste un paramètre `quality` WebP, aucun
# redimensionnement (cf. paragraphe ci-dessus, inchangé).
QUALITES_AUTORISEES = {100, 50, 10, 5}
QUALITE_PAR_DEFAUT = 100
RESOLUTION_PAR_DEFAUT = "full"

# PATCH E (cf. cahier des charges patchs.md, section E.6.3 -- "Limite de
# 30 instances simultanées par sAutoniax"). Nombre MAXIMUM de profils
# pouvant être "en cours" (cf. Connexion.profils_en_cours) à la fois sur
# UN MÊME exécutant -- vérifié par Registre.nb_instances_totales_sur à
# chaque "envoyer_projet_vers_sautoniax_debut" (compte déjà en cours +
# ce qui serait ouvert par la demande, cf. le handler). Constante plutôt
# qu'une valeur en dur répétée, cohérent avec QUALITES_AUTORISEES
# ci-dessus.
LIMITE_INSTANCES_PAR_EXECUTANT = 30


def _recompresser_pour_diffusion(image_b64_source: str, preference: dict) -> str:
    """Reçoit la capture TELLE QUE REÇUE de l'exécutant (WebP qualité
    100, pleine résolution -- cf. ClientServeurT._envoyer_capture côté
    AutoniaX.py, aucune dégradation à la source) et produit la version à
    envoyer à UN pilote précis, selon SON réglage de qualité (`preference`,
    cf. Connexion.preference_capture -- {"resolution": "full" (fixe,
    conservé pour compatibilité de protocole, sans effet ici), "qualite":
    5/10/50/100}).

    CHANGEMENT (demande explicite utilisateur : "sa ne doit plus
    redimensionner ... pourquoi sa ne veux pas juste diminuer la
    qualiter") -- ne redimensionne PLUS JAMAIS l'image (ancien
    RESOLUTIONS_HAUTEUR_PX/img.resize() retiré) : les dimensions en
    pixels envoyées au pilote sont TOUJOURS celles de la capture source,
    quel que soit `qualite`. Seule la compression WebP (paramètre
    `quality`, qui ne touche que l'algorithme de codage, jamais les
    dimensions) varie -- c'est ce qui permet de réduire la taille du
    fichier (ex. 76 Ko -> 10-20 Ko à qualite=10) sans jamais changer la
    taille affichée côté panneau de rendu.

    Défensif, même esprit que _compresser_capture_webp côté AutoniaX.py :
    si Pillow est absent (PILLOW_DISPONIBLE=False, ex. redéploiement Render
    pas encore fait) OU si la recompression échoue pour une raison
    quelconque, retourne l'image source TELLE QUELLE plutôt que de faire
    échouer toute la diffusion pour ce seul pilote -- une capture plus
    lourde mais reçue vaut mieux qu'aucune capture. Cas qualité 100 :
    retourne aussi directement la source sans repasser par Pillow (rien
    à gagner à réencoder une capture déjà en WebP qualité 100, évite un
    aller-retour décodage/réencodage inutile pour le réglage par défaut
    le plus fidèle)."""
    qualite = preference.get("qualite", QUALITE_PAR_DEFAUT)
    if qualite not in QUALITES_AUTORISEES:
        qualite = QUALITE_PAR_DEFAUT
    if qualite == 100:
        return image_b64_source
    if not PILLOW_DISPONIBLE:
        return image_b64_source
    try:
        donnees_source = base64.b64decode(image_b64_source)
        # CORRECTIF ROBUSTESSE (cf. commentaire d'en-tête du fichier --
        # crash -11/SIGSEGV sous forte charge) : garde-fou sur la taille
        # AVANT de passer les octets à Pillow/libwebp (code natif en C).
        # Une capture anormalement volumineuse (bug côté exécutant,
        # capture corrompue, ou simplement une résolution d'écran très
        # élevée) ajoute un facteur de risque supplémentaire pour du
        # code natif déjà sous pression lors d'une rafale de captures
        # simultanées -- mieux vaut renvoyer la source telle quelle
        # (comportement déjà prévu ci-dessous pour tout échec) que de
        # tenter un décodage/réencodage coûteux sur un fichier suspect.
        # 32 Mo est très généreux pour une capture d'écran WebP qualité
        # 100 (normalement quelques centaines de Ko à quelques Mo) --
        # marge large pour ne jamais pénaliser un cas légitime.
        LIMITE_TAILLE_RECOMPRESSION_OCTETS = 32 * 1024 * 1024
        if len(donnees_source) > LIMITE_TAILLE_RECOMPRESSION_OCTETS:
            logger.warning(
                "_recompresser_pour_diffusion : source trop volumineuse (%d octets > %d), "
                "recompression sautée -- capture envoyée à ce pilote telle que reçue.",
                len(donnees_source), LIMITE_TAILLE_RECOMPRESSION_OCTETS,
            )
            return image_b64_source
        with io.BytesIO(donnees_source) as buffer_entree:
            img = PILImage.open(buffer_entree)
            img.load()
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            # Aucun redimensionnement ici (cf. docstring ci-dessus) --
            # seule la qualité de compression WebP change la taille du
            # fichier, jamais les dimensions en pixels de l'image.
            with io.BytesIO() as buffer_sortie:
                img.save(buffer_sortie, format="WEBP", quality=qualite)
                donnees_sortie = buffer_sortie.getvalue()
        return base64.b64encode(donnees_sortie).decode("ascii")
    except Exception as e:
        logger.warning(
            "_recompresser_pour_diffusion : échec (qualite=%r, source_len=%d) : %r -- "
            "capture envoyée à ce pilote telle que reçue.",
            qualite, len(image_b64_source or ""), e,
        )
        return image_b64_source


class Connexion:
    """Une connexion active (pilote ou exécutant) -- l'équivalent minimal
    de srv_InstanceInfo/srv_PiloteInfo côté serveur local (cf. cahier
    section 4 : "sert de modèle pour le registre du serveurT", pas de
    réutilisation directe de code, le serveurT reste un projet séparé)."""

    def __init__(self, websocket: WebSocket, id_connexion: str):
        self.websocket = websocket
        self.id_connexion = id_connexion
        self.role: Optional[str] = None
        self.nom: str = ""
        # AJOUT (correctif bug "badge/spinner de cellule bloqué en cours
        # indéfiniment" -- cf. docstring ClientServeurT._id_pilote_stable
        # côté AutoniaX.py pour le diagnostic complet) : identifiant STABLE
        # d'un pilote, transmis par le client lui-même au register (généré
        # UNE SEULE FOIS à sa construction, jamais recalculé à la
        # reconnexion -- contrairement à id_connexion, réattribué par ce
        # serveur à CHAQUE nouvelle connexion WebSocket). "" tant qu'aucun
        # register ne l'a fourni (ancien mAutoniax pas encore mis à jour,
        # ou connexion pas encore enregistrée) -- cf. Registre.pilote_par_id,
        # qui résout désormais un id_pilote par CETTE valeur plutôt que par
        # id_connexion, symétrique de executant_par_id (résolution par nom).
        self.id_pilote_stable: str = ""
        self.connecte_le: str = datetime.now(timezone.utc).isoformat()
        # PATCH (watchdog exécutants silencieux -- demande explicite
        # utilisateur : "un sautoniax ne repond plus je ne sais pas sil
        # cest deconnecter ... comment faire a ce que on a toujours de
        # vrai logs de debug ... pour tracker la moindre donne de bug
        # suspect") -- time.monotonic() du dernier message REÇU sur cette
        # connexion, tous types confondus (y compris "heartbeat", cf.
        # route_websocket qui met à jour ce champ EN TOUT PREMIER, avant
        # même le dispatch par type_message). Comparé périodiquement par
        # _boucle_watchdog_executants ci-dessous pour détecter un
        # exécutant dont le WebSocket reste ouvert (pas de
        # WebSocketDisconnect, donc aucun log de déconnexion "normale")
        # mais qui ne parle plus -- cas typique d'un process gelé/bloqué
        # côté sAutoniax, distinct d'une vraie coupure réseau.
        # monotonic (pas time.time()) : insensible à un ajustement
        # d'horloge système, seul l'écoulement réel du temps compte ici.
        self.derniere_activite: float = time.monotonic()
        # PATCH (bloc "Envoyer un profil" -- upload en chunks) -- None
        # tant qu'aucun envoi de profil n'est en cours sur CETTE connexion.
        self.upload_profil: Optional[UploadProfilEnCours] = None
        # RETRAIT (migration "Mettre à jour" vers Drive direct -- demande
        # explicite utilisateur : "mAutoniax upload directement ... plus de
        # envoie autonome de fichier du serveur vers les sautoniax") : les
        # champs upload_app, upload_service_api, upload_project_json
        # (accumulation en chunks côté serveur, cf. ex-classe
        # UploadAppEnCours) ont été entièrement retirés -- plus aucun octet
        # de fichier ne transite ni ne s'accumule sur cette connexion pour
        # le Flux A ("Mettre à jour" général) ni pour le Flux B (mise à
        # jour ciblée onglet Instances, cf. handlers
        # demander_retelechargement_service_api/_project_json qui relaient
        # un simple signal, sans fichier).
        # PATCH (protocole générique de téléchargement, sens inverse) --
        # None tant qu'aucun téléchargement n'est en cours sur CETTE
        # connexion (cf. TelechargementFichierEnCours).
        self.telechargement_en_cours: Optional[TelechargementFichierEnCours] = None
        # PATCH (Patch 4.2/4.9 -- statut détaillé par sAutoniax, retour
        # utilisateur explicite : "je veux voir le statut de chaque
        # sAutoniax connecté, pas juste un nombre"). Uniquement pertinent
        # pour role="executant" -- reste "" pour un pilote (jamais
        # affiché, cf. Connexion.vers_dict qui expose ce champ tel quel
        # quel que soit le rôle, sans en faire un cas particulier ici).
        # Mis à jour via le message "statut_executant" (cf. route_
        # websocket) envoyé par le sAutoniax lui-même -- valeurs
        # attendues côté UI (AutoniaX.py) : "inactif" / "demarrage_profils"
        # / "execution_projet:<nom>" / "erreur", mais le serveur ne
        # valide ni n'interprète cette chaîne (relais pur, cf. principe
        # "aucune logique métier AutoniaX" de l'en-tête du fichier) --
        # "inactif" par défaut, un sAutoniax qui vient de se connecter
        # n'a encore rien à signaler.
        self.statut: str = "inactif"
        # AJOUT (correctif "ligne sAutoniax reste grisée indéfiniment
        # après reconnexion" -- signal_pret n'était JAMAIS persisté ici,
        # seulement diffusé une fois au moment de sa réception (cf.
        # handler "sautoniax_pret" plus bas) : un pilote qui se
        # (re)connecte APRÈS ce moment précis (redémarrage du serveurT,
        # nouveau pilote ouvert, etc.) ne recevait donc plus jamais cette
        # information pour un exécutant pourtant déjà prêt depuis
        # longtemps -- cf. Connexion.vers_dict()/instances_list, qui
        # l'expose désormais, et InstancesConnecteesScreen côté AutoniaX.py
        # qui le lit à la construction de la liste plutôt que seulement
        # via le signal live sautoniax_pret_recu. False par défaut : un
        # exécutant qui vient de se connecter n'a pas encore terminé son
        # propre démarrage (téléchargement de dépendances, etc.).
        self.sautoniax_pret: bool = False
        # PATCH (Patch 4.4 -- projets distribués) -- REMPLACÉ par PATCH E
        # (cf. cahier des charges patchs.md, section E.6 -- "Profil déjà
        # utilisé ailleurs" / "Limite de 30 instances simultanées") :
        # l'ancien verrou binaire "un nom de projet ou rien" ne permettait
        # de savoir QUE si CET exécutant traitait déjà quelque chose, pas
        # QUELS profils précis étaient occupés -- insuffisant pour
        # détecter un conflit de profil (E.6.2) ou compter les instances
        # réellement ouvertes pour la limite de 30 (E.6.3), et surtout
        # incompatible avec un batch qui enchaîne plusieurs projets
        # SÉQUENTIELLEMENT sur ce même sAutoniax (E.4) : un simple verrou
        # empêchait tout empilement, il fallait déjà refuser puis
        # réessayer manuellement plus tard.
        #
        # self.profils_en_cours : nom_profil -> dict {"session_id",
        # "id_projet_batch", "nom_projet"} pour CHAQUE profil actuellement
        # ouvert par un projet en cours d'exécution sur CET exécutant
        # (rempli au démarrage réel du projet, cf. "profils_demarres" plus
        # bas -- PAS à l'envoi/la simple réception des chunks, cf. E.6.1
        # "dès qu'un projet termine son exécution, tous les profils qu'il
        # avait ouverts doivent être fermés" : le pendant logique est que
        # l'entrée n'existe QUE pendant l'exécution réelle, jamais avant).
        # Un profil présent ici, quel que soit l'exécutant qui le porte,
        # est considéré "déjà utilisé ailleurs" pour toute AUTRE tentative
        # de lancement (cf. profil_disponible_partout dans Registre) --
        # la contrainte d'unicité porte sur le PROFIL, pas sur le projet.
        self.profils_en_cours: dict[str, dict] = {}
        # PATCH E (E.4 -- batch = plusieurs ProjetBatch enchaînés
        # SÉQUENTIELLEMENT sur un seul sAutoniax). DÉCISION EXPLICITE
        # UTILISATEUR : le séquencement lui-même vit côté PILOTE (cf.
        # AutoniaX.py, ClientServeurT.envoyer_batch_vers_sautoniax) -- le
        # pilote n'envoie le ProjetBatch suivant d'un batch qu'une fois
        # averti que le précédent est terminé (retour_projet_execute_
        # fin). PAS de file d'attente ni de buffer de chunks à maintenir
        # côté serveur (qui resterait fidèle au principe "chaque chunk
        # est transmis puis oublié immédiatement", cf. docstring du
        # handler envoyer_projet_vers_sautoniax_debut) : E.6.2/E.6.3
        # (conflit de profil, limite d'instances) s'appliquent déjà
        # projet par projet, suffisant pour empêcher tout chevauchement
        # réel sans structure supplémentaire.
        #
        # RÉSERVÉ pour un futur raffinement (E.2 -- continuité en cas de
        # déconnexion/reconnexion du pilote pendant un batch en cours) :
        # PAS encore alimenté par ce patch, laissé vide/inutilisé pour
        # l'instant plutôt que retiré -- une liste vide est un no-op
        # inoffensif, mais supprimer le champ casserait vers_dict() plus
        # bas si un futur patch s'appuie dessus avant d'y repenser.
        self.batchs_en_file: list[str] = []
        # PATCH (recompression par pilote -- demande explicite
        # utilisateur : "le serveurT pour renvoyer chez nous on va nous
        # même modifier les paramètres, ça sera juste basé sur le taux de
        # compression, par défaut on va mettre 80, mais on pourra
        # modifier mettre 100, 50" -- résolution ajoutée ensuite : "Full,
        # Medium, Économie" ~1080p/540p/240p). Uniquement pertinent pour
        # role="pilote" (reste à sa valeur par défaut, jamais lue, pour
        # un exécutant) -- réglé par le message "definir_preference_
        # capture" (cf. route_websocket), lu par
        # _recompresser_pour_diffusion à chaque "envoyer_capture" reçu
        # d'un exécutant. PATCH B.3 (demande explicite utilisateur --
        # combo Compression retiré côté client, qualité toujours 100 ;
        # défaut résolution passé de "full" à "medium"/Moyen) : synchronisé
        # avec RESOLUTION_PAR_DEFAUT/QUALITE_PAR_DEFAUT ci-dessus -- un
        # pilote qui ne règle jamais rien démarre désormais en Moyen (360p).
        self.preference_capture: dict = {"resolution": RESOLUTION_PAR_DEFAUT, "qualite": QUALITE_PAR_DEFAUT}
        # PATCH E.2 (cf. cahier des charges patchs.md -- "quand un batch
        # termine son exécution, le serveurT le stocke dans un dossier
        # cloud dédié 'Batch Traité'... permet la continuité même en cas
        # de déconnexion/reconnexion"). État d'accumulation du zip
        # résultat EN COURS de réception sur CETTE connexion exécutant,
        # entre "retour_projet_execute_debut" et "retour_projet_execute_
        # fin" -- même pattern disque que self.upload_profil
        # (UploadProfilEnCours, écriture en append, PAS accumulé en
        # mémoire : un dossier de résultat peut peser autant qu'un
        # profil). None tant qu'aucun retour de projet n'est en cours de
        # réception. Un seul à la fois par connexion, cohérent avec le
        # séquencement pilote (E.4) : un exécutant ne traite jamais deux
        # projets en parallèle, donc ne renvoie jamais deux résultats en
        # chevauchement.
        self.retour_projet_en_cours: Optional["RetourProjetEnCours"] = None

    def vers_dict(self) -> dict:
        """Représentation publique envoyée aux pilotes -- pas d'objet
        WebSocket ni d'attribut interne exposé, juste ce qui est utile
        pour afficher la liste côté mAutoniax.

        PATCH E -- "nb_instances_actives" ajouté (nombre de profils
        actuellement ouverts sur cet exécutant, cf. self.profils_en_cours)
        : utile côté UI pour un futur affichage de charge par sAutoniax
        (ex. "12/30 instances"), sans que le client ait besoin de
        recalculer ça lui-même à partir d'une structure qu'il ne reçoit
        pas (profils_en_cours reste interne au serveur, pas exposé tel
        quel -- seul le compte l'est, cf. "aucune logique métier" mais
        un compte n'en est pas une, juste une donnée dérivée simple).

        PATCH (identité stable par nom, cf. docstring de Registre) --
        "id" vaut désormais self.nom pour un EXÉCUTANT (PAS self.
        id_connexion, qui change à chaque reconnexion) : c'est cette
        valeur que le pilote mémorise et renvoie tel quel dans tous ses
        messages ciblés (id_executant), résolue côté serveur par
        Registre.executant_par_id, qui cherche désormais par nom. Pour
        un PILOTE (self.role == "pilote"), pas de contrainte d'unicité
        équivalente (cf. Registre.ajouter) -- id_connexion reste utilisé
        tel quel dans ce cas, un pilote n'a aujourd'hui aucun message
        ciblé qui aurait besoin de le distinguer d'un autre par un id
        stable.

        "sautoniax_pret" (AJOUT, correctif ligne grisée indéfiniment) :
        reflet direct de self.sautoniax_pret -- False tant que ce message
        n'a pas été reçu sur CETTE connexion, True dès qu'il l'a été (ne
        redescend plus jamais à False tant que la connexion reste
        ouverte). Permet à un pilote qui se connecte APRÈS coup, ou qui
        reconstruit sa liste suite à instances_list, de dégriser
        immédiatement un exécutant déjà prêt -- sans dépendre uniquement
        du signal live "sautoniax_pret", émis une seule fois et donc
        manqué par tout pilote pas encore connecté à ce moment-là."""
        return {
            "id": self.nom if self.role == "executant" else self.id_connexion,
            "role": self.role,
            "nom": self.nom,
            "connecte_le": self.connecte_le,
            "statut": self.statut,
            "nb_instances_actives": len(self.profils_en_cours),
            "sautoniax_pret": self.sautoniax_pret,
        }


class _VueConnexionsGarde(dict):
    """dict en lecture seule utilisé UNIQUEMENT comme valeur de retour de
    Registre.connexions (property) -- cf. sa docstring pour le contexte
    complet du bug que cette classe empêche de réapparaître.

    Se comporte comme un dict normal pour len()/itération/.values(), MAIS
    .get() lève une AssertionError immédiate et explicite si la clé
    demandée ressemble à un id_pilote_stable (préfixe "pilote-") : c'est
    la signature EXACTE de la classe de bug corrigée dans ce fichier
    (registre.connexions.get(id_pilote_cible) au lieu de registre.
    pilote_par_id(id_pilote_cible)) -- ce dict est indexé par id_connexion
    (str(id(websocket)), toujours purement numérique, cf. route_websocket),
    jamais par id_pilote_stable. Mieux vaut un crash bruyant et immédiat
    en développement/test qu'un `logger.warning("... introuvable/
    déconnecté, message perdu")` silencieux en production, qui a laissé
    ce bug vivre dans 7 handlers différents sans qu'aucun test ni relecture
    ne le remarque."""

    def get(self, key, default=None):
        if isinstance(key, str) and key.startswith("pilote-"):
            raise AssertionError(
                f"Registre.connexions.get({key!r}) : clé qui ressemble à un "
                "id_pilote_stable, jamais présente dans ce dict (indexé "
                "uniquement par id_connexion). Utiliser "
                "registre.pilote_par_id(...) à la place -- cf. docstring "
                "Registre.pilote_par_id et _VueConnexionsGarde."
            )
        return super().get(key, default)


class Registre:
    """Registre en mémoire de toutes les connexions actives -- juste un
    dict, comme prévu par le cahier ("Stockage d'état côté serveurT : en
    mémoire simple pour commencer", cf. section 5.4, point encore ouvert
    mais tranché ici pour l'Étape 0 : mémoire simple, pas de base).

    PATCH (identité stable par nom -- demande explicite utilisateur :
    "je crois que il faut dautre donene pour identifier un client, par
    exemple le noms de session, il ne doit pas y avoir 2 sautoniax avec
    le meme noms ... quand ya deconnection et reconnection apres,
    liaison est cassee avec mautoniax") -- id_connexion (str(id(websocket)),
    cf. route_websocket) change à CHAQUE reconnexion, même machine, même
    nom : un pilote qui aurait mémorisé l'ancien id_connexion pointe donc
    dans le vide après toute coupure/reconnexion d'un exécutant. Le NOM
    (connexion.nom, fourni par le sAutoniax lui-même au register, stable
    d'un lancement à l'autre -- cf. AutoniaX.py, main_sautoniax :
    dérivé de --instance-id ou du profil) devient donc l'identité
    FONCTIONNELLE unique d'un exécutant : cf. ajouter() ci-dessous, qui
    garantit qu'un nom d'exécutant n'est jamais porté par deux connexions
    en même temps, et Connexion.vers_dict() qui expose désormais le NOM
    (pas id_connexion) comme "id" public vu par les pilotes -- eux
    utilisent ensuite ce nom tel quel dans tous leurs messages ciblés
    (id_executant), résolu ici même par executant_par_id ci-dessous.
    id_connexion reste un détail d'implémentation PUREMENT interne
    (clé du dict self.connexions, nécessaire pour retrouver l'objet
    WebSocket exact d'une connexion précise) -- jamais exposé, jamais
    utilisé comme identité par quoi que ce soit en dehors de cette
    classe."""

    def __init__(self):
        # RENOMMÉ (garde-fou structurel, cf. bug confirmé et corrigé à 7
        # endroits différents : profils_sautoniax_resultat, tester_proxy_
        # sautoniax_resultat, telecharger_profil_vers_sautoniax_resultat,
        # liste_profils_locaux_sautoniax_resultat, envoyer_profil_fin (x2),
        # instances_projet -- tous appelaient `registre.connexions.get
        # (id_pilote_cible)` alors que id_pilote_cible est un id_pilote_
        # stable ("pilote-xxxx"), PAS une clé de ce dict, qui n'est indexée
        # QUE par id_connexion (str(id(websocket))) -- lookup qui échouait
        # SILENCIEUSEMENT à CHAQUE fois, même pilote parfaitement connecté,
        # log "introuvable/déconnecté" trompeur). Le nom explicite
        # "_par_id_connexion" rend ce genre d'erreur visible immédiatement
        # à la relecture -- `registre._par_id_connexion.get(un_id_pilote)`
        # se remarque, contrairement à `registre.connexions.get(...)`, trop
        # générique pour alerter qui que ce soit. Accès direct désormais
        # PRIVÉ (préfixe "_") : tout code hors de cette classe qui a besoin
        # de résoudre un id métier DOIT passer par une méthode de
        # résolution nommée ci-dessous (executant_par_id / pilote_par_id),
        # jamais par un accès dict brut qui ne distingue pas les espaces
        # de clés. Propriété `connexions` conservée juste en dessous, en
        # lecture seule, uniquement pour len()/itération globale (cf.
        # "connexions_actives" plus bas) -- PAS pour un .get() ciblé par id
        # métier.
        self._par_id_connexion: dict[str, Connexion] = {}
        # CORRECTIF (bug n°3, même famille EXACTE que RegistreTunnel.
        # _verrous_par_websocket, cf. sa docstring pour le diagnostic
        # complet -- issue encode/starlette#1369, écriture concurrente
        # non sûre sur un même objet WebSocket) : cette route ("/ws",
        # canal de contrôle général) diffuse vers tous les pilotes
        # depuis PLUSIEURS tâches asyncio différentes (une par connexion
        # exécutant, cf. les boucles "for pilote in registre.pilotes():
        # await pilote.websocket.send_text(...)" dans route_websocket) --
        # exactement le même schéma qui causait des écritures entrelacées
        # côté /ws_tunnel avant son propre correctif. Un `asyncio.Lock`
        # PAR OBJET WebSocket réel (indexé par id(websocket), jamais par
        # id_connexion/nom seuls -- une reconnexion crée un nouvel objet
        # WebSocket, donc un nouveau verrou, jamais un verrou périmé
        # partagé avec une connexion déjà fermée), créé dans ajouter() et
        # nettoyé dans retirer() pour ne jamais laisser grossir ce dict
        # indéfiniment sur la durée de vie du process.
        self._verrous_par_websocket: dict[int, asyncio.Lock] = {}

    @property
    def connexions(self) -> dict[str, Connexion]:
        """Vue en lecture seule, pour len()/itération globale UNIQUEMENT
        (ex. "connexions_actives" dans /etat). Ne PAS utiliser .get() sur
        cette vue avec un id_pilote_stable ou un id_executant -- cf.
        docstring __init__ ci-dessus : ce dict n'est indexé que par
        id_connexion. Pour résoudre un pilote ou un exécutant par son id
        métier, utiliser pilote_par_id() / executant_par_id().

        GARDE-FOU RUNTIME (filet de sécurité, en plus du renommage/de la
        privatisation ci-dessus) : la vue renvoyée est une _VueConnexions
        Garde, PAS un dict brut -- son .get() lève immédiatement une
        AssertionError explicite si on l'appelle avec une clé qui
        RESSEMBLE à un id_pilote_stable ("pilote-xxxx") ou à un nom
        d'exécutant déjà connu, plutôt que de renvoyer silencieusement
        None comme un dict.get() normal l'aurait fait -- exactement le
        bug qui s'est produit 7 fois de suite ici, jamais détecté avant
        la mise en prod faute d'un signal fort au moment de l'erreur."""
        return _VueConnexionsGarde(self._par_id_connexion)

    def ajouter(self, connexion: Connexion):
        # PATCH (identité stable par nom) -- contrainte d'unicité
        # SEULEMENT pour role="executant" (décision explicite
        # utilisateur : "il ne doit pas y avoir 2 sautoniax avec le meme
        # noms" -- ne concerne QUE les sAutoniax) : un pilote peut, lui,
        # se reconnecter ou même être ouvert deux fois sans que ça pose
        # de problème fonctionnel équivalent, aucune contrainte
        # équivalente n'est demandée ni nécessaire pour ce rôle.
        #
        # Si un exécutant du même nom existe déjà (cas normal d'une
        # reconnexion : l'ancien websocket est mort ou zombie côté
        # serveur, mais son entrée n'a pas encore été retirée -- ex. la
        # coupure n'a pas encore levé WebSocketDisconnect côté ancienne
        # connexion), il est retiré du registre AVANT que la nouvelle ne
        # soit ajoutée : jamais deux entrées pour le même nom en même
        # temps, jamais de connexion fantôme qui répondrait "occupé" à
        # tort pour un nom en réalité déjà libre.
        if connexion.role == "executant" and connexion.nom:
            ancien = next(
                (c for c in self.executants() if c.nom == connexion.nom),
                None,
            )
            if ancien is not None:
                self._par_id_connexion.pop(ancien.id_connexion, None)
                self._verrous_par_websocket.pop(id(ancien.websocket), None)
        # CORRECTIF (bug découvert en testant le correctif de pilote_par_id
        # ci-dessous -- même famille EXACTE que le nettoyage exécutant
        # juste au-dessus, jamais étendu au rôle "pilote") : à chaque
        # reconnexion de mAutoniax (coupure réseau, veille, redémarrage --
        # cf. les logs "register : mAutoniax (pilote)" qui reviennent
        # plusieurs fois de suite sur une courte période), un NOUVEL
        # id_connexion est attribué mais id_pilote_stable reste identique
        # (généré une seule fois à la construction du process, cf.
        # ClientServeurT._id_pilote_stable). Sans ce nettoyage, l'ANCIENNE
        # entrée (websocket mort ou zombie, tant que WebSocketDisconnect
        # n'a pas encore été levé côté serveur) restait dans le registre
        # EN PLUS de la nouvelle -- pilote_par_id() ci-dessous, qui prend
        # la PREMIÈRE correspondance trouvée par id_pilote_stable, pouvait
        # alors retourner la connexion fantôme plutôt que la connexion
        # réellement active, et un relais vers elle échouait silencieusement
        # (send_text sur un websocket déjà fermé). Même logique que pour un
        # exécutant : l'ancienne entrée est retirée AVANT que la nouvelle
        # ne soit ajoutée, jamais deux entrées pour le même id_pilote_stable
        # en même temps.
        elif connexion.role == "pilote" and connexion.id_pilote_stable:
            ancien_pilote = next(
                (c for c in self.pilotes() if c.id_pilote_stable == connexion.id_pilote_stable),
                None,
            )
            if ancien_pilote is not None:
                self._par_id_connexion.pop(ancien_pilote.id_connexion, None)
                self._verrous_par_websocket.pop(id(ancien_pilote.websocket), None)
        self._par_id_connexion[connexion.id_connexion] = connexion
        # CORRECTIF (bug n°3) -- cf. docstring de self._verrous_par_websocket
        # dans __init__ : un verrou frais par websocket réel, créé dès
        # l'enregistrement (même point que RegistreTunnel.ajouter_pilote/
        # ajouter_executant).
        self._verrous_par_websocket.setdefault(id(connexion.websocket), asyncio.Lock())

    def retirer(self, id_connexion: str):
        connexion = self._par_id_connexion.pop(id_connexion, None)
        if connexion is not None:
            self._verrous_par_websocket.pop(id(connexion.websocket), None)

    def verrou_pour(self, websocket: WebSocket) -> asyncio.Lock:
        """Verrou dédié à CE websocket précis -- cf. docstring de
        self._verrous_par_websocket dans __init__, symétrique EXACT de
        RegistreTunnel.verrou_pour. setdefault ici aussi (pas seulement
        dans ajouter()) en filet de sécurité : le verrou doit exister
        même pour un websocket qui n'est plus dans le registre au moment
        de l'appel (ex. retirer() vient de tourner pendant qu'un envoi
        pour ce même websocket était déjà en file dans une autre tâche) --
        un Lock frais et non partagé dans ce cas résiduel reste toujours
        correct (au pire, pas de sérialisation utile pour un envoi isolé
        déjà en toute fin de vie de la connexion, jamais un verrou
        incorrect)."""
        return self._verrous_par_websocket.setdefault(id(websocket), asyncio.Lock())

    def pilotes(self) -> list[Connexion]:
        return [c for c in self._par_id_connexion.values() if c.role == "pilote"]

    def executants(self) -> list[Connexion]:
        return [c for c in self._par_id_connexion.values() if c.role == "executant"]

    def executant_par_id(self, id_executant: str) -> Optional[Connexion]:
        """Retrouve un exécutant précis par son NOM (PATCH identité
        stable -- id_executant, malgré son nom conservé tel quel dans
        toute la signature/tous les appelants pour ne rien casser
        ailleurs, contient désormais le NOM de l'exécutant, pas
        id_connexion -- cf. docstring de Registre et Connexion.vers_dict :
        c'est ce que le pilote reçoit comme "id" et renvoie ensuite tel
        quel dans tous ses messages ciblés). None si le nom est inconnu
        OU si la connexion trouvée n'a pas (ou plus) le rôle
        "executant"."""
        connexion = next(
            (c for c in self.executants() if c.nom == id_executant),
            None,
        )
        if connexion is None or connexion.role != "executant":
            return None
        return connexion

    def pilote_par_id(self, id_pilote: str) -> Optional[Connexion]:
        """Retrouve un pilote précis par son identifiant STABLE -- cf.
        docstring Connexion.id_pilote_stable / ClientServeurT._id_pilote_
        stable (côté AutoniaX.py) pour le diagnostic complet du bug que ce
        correctif résout. Symétrique EXACT de executant_par_id ci-dessus,
        mais résout par id_pilote_stable (fourni par le client à son
        register, stable à travers les reconnexions) plutôt que par nom
        (self.nom reste "mAutoniax" par défaut pour tout pilote qui ne le
        change pas explicitement -- PAS unique, donc inutilisable comme clé
        de résolution, contrairement au nom d'un exécutant déjà garanti
        unique par Registre.ajouter).

        Repli EXPLICITE sur id_connexion si id_pilote vaut cette valeur
        (compat ascendante -- ancien mAutoniax non mis à jour, ou message
        historique encore construit avec l'ancien id_connexion comme
        id_pilote) : un id_pilote qui ne correspond à AUCUN id_pilote_
        stable connu est donc retenté une seconde fois comme id_connexion
        brut, avant de renvoyer None. Aucun risque de collision entre les
        deux espaces de valeurs (id_pilote_stable est toujours préfixé
        "pilote-", id_connexion est toujours un str(id(...)) purement
        numérique, cf. route_websocket)."""
        # Défense en profondeur : Registre.ajouter() retire désormais
        # toute ancienne connexion pilote partageant le même id_pilote_
        # stable AVANT d'ajouter la nouvelle (cf. sa docstring), donc deux
        # entrées avec le même id_pilote_stable ne devraient normalement
        # jamais coexister. S'il en restait quand même plusieurs (état
        # transitoire imprévu), on retient explicitement la plus RÉCEMMENT
        # connectée (connecte_le le plus grand) plutôt que la première
        # trouvée par next() -- qui dépendrait alors de l'ordre
        # d'insertion du dict, potentiellement une connexion fantôme plus
        # ancienne.
        candidats = [
            c for c in self.pilotes()
            if c.id_pilote_stable and c.id_pilote_stable == id_pilote
        ]
        if candidats:
            return max(candidats, key=lambda c: c.connecte_le)
        # Repli id_connexion (compat ascendante, cf. docstring ci-dessus).
        connexion = self._par_id_connexion.get(id_pilote)
        if connexion is not None and connexion.role == "pilote":
            return connexion
        return None

    # ------------------------------------------------------------------
    # PATCH E (cf. cahier des charges patchs.md, section E.6 --
    # "Vérifications serveur avant de (re)lancer un traitement"). Ces
    # deux méthodes sont de la pure comptabilité sur Connexion.profils_
    # en_cours (déjà peuplé par chaque exécutant, cf. route_websocket --
    # bloc "profils_demarres"/"profils_ouverts_fermes" plus bas) -- ni
    # l'une ni l'autre n'interprète le CONTENU d'un projet/profil, elles
    # comptent et croisent des noms, ce qui reste dans l'esprit "aucune
    # logique métier AutoniaX" de l'en-tête du fichier (une vérification
    # mécanique de disponibilité n'est pas une décision de traitement).
    # ------------------------------------------------------------------

    def profils_deja_utilises(self, noms_profils: list[str]) -> dict[str, str]:
        """PATCH E (E.6.2 -- "si un ou plusieurs profils sélectionnés
        sont déjà en cours d'exécution réelle ... refuser"). Croise
        `noms_profils` contre profils_en_cours de TOUS les exécutants
        connectés (pas seulement la cible visée par la demande en cours)
        -- cf. cahier des charges E.7 : "un profil déjà utilisé dans un
        AUTRE batch n'a AUCUNE contrainte [...] MAIS déjà en cours
        d'exécution réelle ailleurs reste un conflit, peu importe sur
        quel sAutoniax". Retourne {nom_profil: nom_exécutant_occupant}
        pour CHAQUE profil demandé qui est actuellement occupé --
        dict vide si aucun conflit, pour un test direct `if
        profils_deja_utilises(...):` côté appelant plutôt qu'un booléen
        séparé à maintenir en synchronisation."""
        occupes: dict[str, str] = {}
        recherche = set(noms_profils)
        if not recherche:
            return occupes
        for connexion in self.executants():
            for nom_profil in connexion.profils_en_cours:
                if nom_profil in recherche:
                    occupes[nom_profil] = connexion.nom or connexion.id_connexion
        return occupes

    def nb_instances_totales_sur(self, id_executant: str) -> int:
        """PATCH E (E.6.3 -- "limite de 30 instances simultanées par
        sAutoniax"). Nombre de profils actuellement ouverts sur CET
        exécutant précis (contrairement à profils_deja_utilises ci-
        dessus, qui regarde TOUS les exécutants -- ici la limite est
        PAR sAutoniax, cf. cahier : "sur un même sAutoniax"). 0 si
        l'exécutant est introuvable/déconnecté plutôt qu'une exception --
        cohérent avec executant_par_id ci-dessus qui retourne déjà None
        dans ce cas sans lever d'erreur."""
        connexion = self.executant_par_id(id_executant)
        if connexion is None:
            return 0
        return len(connexion.profils_en_cours)


# PATCH B.4 (contrôle à distance réel, cf. cahier des charges patchs.md)
# -- corrélation requete_id -> id_pilote pour router command_result. Le
# protocole "command"/"command_result" (cf. _executer_commande_camoufox
# côté AutoniaX.py) est générique et ne transporte PAS l'id du pilote
# expéditeur dans sa réponse (il n'a jamais eu besoin de ça avant B.4,
# utilisé jusqu'ici uniquement par le serveur central EMBARQUÉ dans
# AutoniaX.py -- srv_gerer_command -- qui, lui, connaît déjà pilote_id
# via sa propre connexion WebSocket directe). Ici, côté serveurT, le
# pilote et l'exécutant ne se parlent JAMAIS directement (toujours relayé)
# -- donc c'est CE dict, en mémoire, rempli à l'envoi (commande_instance)
# et consommé/purgé à la réception (command_result), qui route la
# réponse vers le bon pilote. TTL volontairement absent (dict simple,
# comme le reste de Registre) : une entrée orpheline (sAutoniax déconnecté
# avant réponse) reste en mémoire mais ne grossit jamais de façon
# significative -- un contrôle à distance interactif produit au plus
# quelques commandes par seconde, purgées presque aussitôt après.
COMMANDES_INSTANCE_EN_ATTENTE: dict[str, str] = {}

registre = Registre()


# ======================================================================
# Api2Api -- registre + verrouillage + corrélation requête/réponse.
#
# But (cf. spécification complète fournie par l'utilisateur, résumée
# ici) : n'importe quel Task ordinaire (local ou réseau, n'importe où
# sur le réseau) peut envoyer une requête synchrone (données = fichiers,
# texte ou image) à n'importe quel autre Task de type "Api2Api", conçu
# pour attendre passivement des requêtes et y répondre. Le serveurT est
# le SEUL point de routage/orchestration -- ni l'appelant ni le
# fournisseur n'écrivent de code réseau eux-mêmes (cf. Api2Api/
# attendre_requete côté AutoniaX.py, qui exposent des primitives
# synchrones bloquantes).
#
# Modèle retenu (décisions explicites utilisateur, itérées) :
#   - Un seul type global "api2api" -- pas de nom/tag choisi par
#     l'utilisateur, Api2Api() prend le premier Task Api2Api LIBRE
#     trouvé sur tout le réseau, peu importe lequel.
#   - Verrouillage EXCLUSIF uniquement (mode "partagé" envisagé puis
#     explicitement écarté) : un Task Api2Api ne sert qu'UN SEUL client
#     à la fois, du verrouillage jusqu'à la libération.
#   - Attente BLOQUANTE avec timeout côté appelant si aucun Api2Api
#     n'est libre au moment de l'appel (pas d'échec immédiat) -- cf.
#     FILE_ATTENTE_API2API plus bas.
#   - Libération AUTOMATIQUE par inactivité si le client oublie
#     .free() (crash, oubli) -- mesurée depuis le dernier api2api_
#     requete envoyé par CE client, cf. _boucle_watchdog_api2api.
#
# Symétrique de Registre/COMMANDES_INSTANCE_EN_ATTENTE ci-dessus (même
# esprit : dict simple en mémoire, pas de base, cf. cahier section 5.4).
# ======================================================================

# Un Task Api2Api enregistré = une entrée dans ce dict, clé = id_api2api
# (uuid généré ici à l'enregistrement, PAS l'id_connexion du fournisseur
# -- un même process/connexion pourrait en théorie enregistrer plusieurs
# Task Api2Api successifs au fil de sa vie, chacun avec sa propre
# identité de verrouillage). Valeur :
#   {
#     "id_connexion_fournisseur": str,   # connexion WebSocket qui porte ce Task
#     "statut": "libre" | "verrouille",
#     "id_connexion_proprietaire": Optional[str],  # connexion du client qui l'a verrouillé
#     "derniere_activite": float,        # time.monotonic(), rafraîchi à chaque api2api_requete reçu -- cf. watchdog
# }
REGISTRE_API2API: dict[str, dict] = {}

# File d'attente des clients bloqués sur Api2Api() faute d'un Api2Api
# libre au moment de l'appel (cf. "attente bloquante avec timeout").
# clé = id_connexion du client en attente, valeur = asyncio.Event à
# déclencher dès qu'un Api2Api se libère (réveille le handler
# api2api_verrouiller de CE client pour qu'il retente immédiatement,
# plutôt que du polling). PAS de garantie d'ordre FIFO explicite --
# jamais demandée (décision explicite utilisateur sur la question
# symétrique en mode "partagé", annulée avant d'avoir eu besoin d'y
# répondre) : tous les clients en attente sont réveillés ensemble à
# chaque libération, le premier qui verrouille effectivement gagne côté
# handler (cf. api2api_verrouiller), les autres retombent en attente.
FILE_ATTENTE_API2API: dict[str, "asyncio.Event"] = {}

# Corrélation requete_id -> id_connexion du CLIENT qui attend la
# réponse -- même patron exact que COMMANDES_INSTANCE_EN_ATTENTE
# ci-dessus (purgé à la réception de la réponse, pas de TTL séparé).
REQUETES_API2API_EN_ATTENTE: dict[str, str] = {}

# Timeout d'inactivité (secondes) au-delà duquel un verrou Api2Api sans
# aucune api2api_requete est libéré automatiquement -- cf. _boucle_
# watchdog_api2api. Généreux à dessein (un traitement fournisseur peut
# légitimement prendre du temps entre deux requêtes d'un même client,
# ex. attente d'un résultat de génération IA) -- ce n'est qu'un filet
# de sécurité contre un client mort/planté, pas une limite de débit.
TIMEOUT_INACTIVITE_API2API_SECONDES = 120.0
INTERVALLE_WATCHDOG_API2API_SECONDES = 10.0


def _api2api_libres() -> list[str]:
    """Liste des id_api2api actuellement "libre" -- ordre d'insertion du
    dict (Python 3.7+, garanti), donc le PREMIER enregistré est pris en
    premier à statut égal (pas une vraie garantie FIFO globale -- cf.
    docstring de FILE_ATTENTE_API2API -- mais un ordre déterministe reste
    préférable à un choix arbitraire)."""
    return [id_api2api for id_api2api, entree in REGISTRE_API2API.items() if entree["statut"] == "libre"]


def _api2api_reveiller_attente():
    """Réveille TOUS les clients actuellement bloqués sur Api2Api() (cf.
    FILE_ATTENTE_API2API) -- appelée à chaque fois qu'un Api2Api devient
    libre (nouvel enregistrement OU libération d'un verrou existant).
    Chaque client réveillé retente son verrouillage immédiatement (cf.
    handler api2api_verrouiller) ; en cas de course entre plusieurs
    clients réveillés pour un seul Api2Api libre, un seul l'obtient
    réellement (le dict REGISTRE_API2API n'est jamais modifié en dehors
    de la boucle asyncio single-thread de FastAPI/uvicorn, donc pas de
    vraie condition de course au sens thread -- juste un ordre
    d'exécution des coroutines à départager, sans garantie particulière,
    cf. docstring FILE_ATTENTE_API2API)."""
    for event in FILE_ATTENTE_API2API.values():
        event.set()


def _api2api_liberer_entree(id_api2api: str):
    """Remet un Api2Api à "libre" (verrou retiré) et réveille la file
    d'attente -- factorisé, utilisé à la fois par le handler api2api_
    liberer (libération explicite du client), par le watchdog
    d'inactivité, et par le nettoyage à la déconnexion (route_websocket,
    finally) si c'est le CLIENT propriétaire qui se déconnecte (pas le
    fournisseur -- cf. _api2api_desenregistrer_fournisseur pour ce
    second cas, distinct : là, l'entrée entière disparaît plutôt que de
    redevenir libre)."""
    entree = REGISTRE_API2API.get(id_api2api)
    if entree is None:
        return
    entree["statut"] = "libre"
    entree["id_connexion_proprietaire"] = None
    _api2api_reveiller_attente()


def _api2api_desenregistrer_fournisseur(id_connexion: str):
    """Retire du registre TOUS les Task Api2Api portés par CETTE
    connexion fournisseur (déconnexion du sAutoniax/mAutoniax qui
    exécutait ce Task, ou désenregistrement explicite à l'arrêt propre
    du Task) -- contrairement à _api2api_liberer_entree, l'entrée
    disparaît ENTIÈREMENT (plus aucun client ne doit jamais pouvoir la
    verrouiller, le fournisseur n'existe plus). Si un client avait
    actuellement cette entrée verrouillée, il reste bloqué sur son
    prochain api2api_requete jusqu'à erreur explicite (cf. handler
    api2api_requete, qui vérifie déjà que l'id_api2api existe encore
    avant de relayer) -- pas de notification proactive au client ici,
    l'erreur au prochain appel suffit et reste plus simple qu'un
    nouveau message dédié."""
    a_retirer = [
        id_api2api for id_api2api, entree in REGISTRE_API2API.items()
        if entree["id_connexion_fournisseur"] == id_connexion
    ]
    for id_api2api in a_retirer:
        REGISTRE_API2API.pop(id_api2api, None)
    if a_retirer:
        logger.info("api2api : %d Task(s) Api2Api désenregistré(s) (fournisseur déconnecté, id=%s)", len(a_retirer), id_connexion)


def _api2api_liberer_si_proprietaire(id_connexion: str):
    """Libère tout verrou Api2Api actuellement détenu par CETTE
    connexion cliente (déconnexion du client en cours de session Api2Api
    -- cf. décision explicite utilisateur : le client mort ne doit pas
    garder le verrou indéfiniment). Distinct de _api2api_desenregistrer_
    fournisseur : ici l'entrée elle-même n'est PAS retirée, juste rendue
    de nouveau libre (le Task fournisseur, lui, tourne toujours et reste
    disponible pour un prochain client)."""
    for id_api2api, entree in REGISTRE_API2API.items():
        if entree["statut"] == "verrouille" and entree["id_connexion_proprietaire"] == id_connexion:
            _api2api_liberer_entree(id_api2api)


def _api2api_reset_admin() -> int:
    """OUTIL DE DÉVELOPPEMENT (retour utilisateur explicite : "j'ai besoin
    d'une commande spéciale qui va réinitialiser le registre, mettre tout
    le monde à free" -> précisé ensuite : "vider complètement, donc
    réinitialiser") -- VIDE ENTIÈREMENT REGISTRE_API2API, PAS un simple
    passage à statut="libre" (cf. _api2api_liberer_entree pour ce cas-là,
    déjà utilisé ailleurs) : chaque fournisseur Api2Api actuellement
    enregistré (même verrouillé) disparaît complètement du registre --
    quiconque a un Task tournant sur `while True: req = attendre_requete()`
    devra RELANCER ce Task pour se ré-enregistrer, exactement comme après
    un redémarrage du serveurT (REGISTRE_API2API n'est jamais persisté,
    cf. sa docstring : "dict simple en mémoire, pas de base").

    Purge aussi les DEUX structures satellites, pour ne rien laisser
    d'incohérent derrière ce reset :
      - FILE_ATTENTE_API2API : réveille tout client actuellement bloqué
        sur Api2Api() (cf. _api2api_reveiller_attente) -- chacun retente
        aussitôt son verrouillage, ne trouve plus aucun candidat libre
        (le registre est vide), et retombe proprement en attente/timeout
        selon son propre timeout_attente_s, plutôt que de rester bloqué
        indéfiniment sur un Api2Api qui vient de disparaître sous ses
        pieds sans qu'il en soit jamais informé.
      - REQUETES_API2API_EN_ATTENTE : toute corrélation requete_id ->
        client en attente d'une réponse (cf. handler api2api_requete)
        devient orpheline dès que son fournisseur disparaît -- purgée ici
        pour éviter qu'une éventuelle api2api_reponse tardive et
        désormais sans rapport avec quoi que ce soit ne soit routée par
        erreur vers un client qui a depuis longtemps abandonné ou changé
        de contexte.

    RÉSERVÉ AU DÉVELOPPEMENT -- aucune vérification de permission/rôle
    ici (cf. handler api2api_reset_admin, qui n'en fait pas non plus) :
    n'importe quelle connexion peut actuellement déclencher ce reset
    global, ce qui casserait tout Api2Api en cours pour TOUS les clients
    du réseau, pas seulement l'appelant. Acceptable uniquement parce que
    ce protocole tourne aujourd'hui en développement local/de confiance
    -- à verrouiller derrière une vraie authentification admin avant tout
    usage en dehors de ce contexte.

    Renvoie le nombre d'entrées qui étaient enregistrées dans
    REGISTRE_API2API juste avant le vidage (0 si déjà vide) -- purement
    informatif, pour que l'appelant (handler ci-dessous) puisse le
    reloguer/le renvoyer dans son ack sans avoir à réinspecter le
    registre lui-même après coup."""
    nombre_avant = len(REGISTRE_API2API)
    REGISTRE_API2API.clear()
    REQUETES_API2API_EN_ATTENTE.clear()
    _api2api_reveiller_attente()
    logger.warning(
        "api2api : RESET ADMIN -- registre entièrement vidé (%d Task(s) Api2Api désenregistré(s) d'un coup)",
        nombre_avant,
    )
    return nombre_avant


async def _boucle_watchdog_api2api():
    """Toutes les INTERVALLE_WATCHDOG_API2API_SECONDES, libère tout
    verrou Api2Api sans aucune api2api_requete depuis plus de TIMEOUT_
    INACTIVITE_API2API_SECONDES -- cf. décision explicite utilisateur
    ("Libérer automatiquement après un timeout d'inactivité", mesuré
    "depuis le dernier .request() envoyé par ce client"). Même patron
    EXACT que _boucle_watchdog_executants ci-dessus (tâche de fond
    permanente, lancée une seule fois au démarrage, cf. lifespan)."""
    while True:
        await asyncio.sleep(INTERVALLE_WATCHDOG_API2API_SECONDES)
        maintenant = time.monotonic()
        for id_api2api, entree in list(REGISTRE_API2API.items()):
            if entree["statut"] != "verrouille":
                continue
            silence = maintenant - entree["derniere_activite"]
            if silence < TIMEOUT_INACTIVITE_API2API_SECONDES:
                continue
            logger.warning(
                "api2api : verrou '%s' libéré automatiquement (inactif depuis %.0fs, propriétaire=%s)",
                id_api2api, silence, entree["id_connexion_proprietaire"],
            )
            _api2api_liberer_entree(id_api2api)


@app.on_event("startup")
async def _lancer_watchdog_api2api():
    """Démarre _boucle_watchdog_api2api comme tâche de fond, même patron
    exact que _lancer_watchdog_executants ci-dessus."""
    asyncio.create_task(_boucle_watchdog_api2api())


async def diffuser_liste_executants():
    """Envoie la liste à jour des exécutants connectés à TOUS les pilotes
    connectés -- déclenché à chaque enregistrement ou déconnexion d'un
    exécutant (cf. cahier section 5.3 : "liste des sAutoniax connectés
    envoyée à mAutoniax"). Une connexion pilote dont l'envoi échoue est
    silencieusement ignorée ici (sa propre boucle de réception détectera
    la déconnexion et appellera registre.retirer)."""
    message = json.dumps({
        "type": "executants_connectes",
        "executants": [c.vers_dict() for c in registre.executants()],
    })
    # CORRECTIF (bug n°3, cf. docstring de Registre._verrous_par_websocket) --
    # sérialise cet envoi avec toute autre écriture concurrente vers le
    # MÊME websocket pilote, émise par une autre tâche (autre connexion
    # exécutant, ou un autre appel concurrent à cette même fonction).
    for pilote in registre.pilotes():
        try:
            async with registre.verrou_pour(pilote.websocket):
                await pilote.websocket.send_text(message)
        except Exception:
            pass


# PATCH (watchdog exécutants silencieux -- demande explicite utilisateur :
# "un sautoniax ne repond plus ... comment faire a ce que on a toujours
# de vrai logs de debug ... pour tracker la moindre donne de bug
# suspect", rythme précisé ensuite : "fait le tout les 10 seconde ...
# tout les 10 second en donnent bien assez dinformations pour voir une
# anormalie"). Tâche de fond permanente, lancée une seule fois au
# démarrage du process (cf. lifespan tout en bas) -- tourne pour TOUTE
# la durée de vie du serveur, indépendamment des connexions individuelles
# qui vont et viennent.
#
# Détecte un cas que route_websocket/WebSocketDisconnect NE couvre PAS :
# un exécutant dont le WebSocket reste ouvert des deux côtés (donc aucune
# exception, aucun log de déconnexion "normale" en finally) mais qui ne
# répond plus -- process gelé, boucle bloquée, deadlock côté sAutoniax.
# Sans ce watchdog, ce cas est silencieux : le serveur continue de croire
# la connexion vivante tant qu'elle n'est pas formellement fermée.
INTERVALLE_WATCHDOG_SECONDES = 3.0
# Seuil de silence à partir duquel un exécutant est jugé suspect : plus
# large que DELAI_HEARTBEAT_SECONDES côté client (15s, cf. AutoniaX.py)
# pour absorber une marge réseau normale sans fausse alerte à chaque
# heartbeat un peu en retard -- 2x15s + une marge = 35s.
# BUGFIX (retour utilisateur : "le délai est trop élevé" pour qu'un
# sAutoniax déconnecté disparaisse) -- avant : tick 10s + seuil 35s + un
# tick de marge avant retrait = 35 à 55s. Maintenant : tick 3s + seuil 25s
# (un heartbeat de 15s manqué + 10s de marge) = environ 25 à 31s.
# Une déconnexion PROPRE (fermeture du WebSocket) reste instantanée, cf.
# finally de route_websocket. Remonter ce seuil si des faux positifs
# apparaissent sur un sAutoniax très chargé.
SEUIL_SILENCE_SUSPECT_SECONDES = 25.0


async def _boucle_watchdog_executants():
    """Toutes les INTERVALLE_WATCHDOG_SECONDES, parcourt les exécutants
    connectés et compare leur derniere_activite à maintenant. Un
    exécutant silencieux depuis plus de SEUIL_SILENCE_SUSPECT_SECONDES :
    - est loggé en WARNING côté serveur (visible dans /logs et la
      console Render), avec la durée exacte de silence -- point de départ
      pour corréler avec les derniers messages connus de cet exécutant
      dans les logs juste avant qu'il ne se taise ;
    - déclenche un message "executant_silencieux" envoyé à TOUS les
      pilotes connectés (même diffusion que diffuser_liste_executants),
      pour que ce soit visible EN DIRECT côté mAutoniax sans attendre
      qu'un humain remarque l'absence de réponse -- cf. AutoniaX.py,
      ClientServeurT._traiter_message.
    Une seule alerte par épisode de silence (self._deja_alerte plus bas,
    remis à zéro dès que l'activité reprend) : pas de spam d'un nouveau
    WARNING toutes les 10s tant que l'exécutant reste silencieux, une
    seule notification suffit pour signaler l'anomalie."""
    deja_alertes: set[str] = set()
    while True:
        await asyncio.sleep(INTERVALLE_WATCHDOG_SECONDES)
        maintenant = time.monotonic()
        executants_encore_silencieux: set[str] = set()
        executants_a_retirer: list[Connexion] = []
        for connexion in registre.executants():
            # BUGFIX (sAutoniax-2 retiré du registre en PLEIN
            # téléchargement de mouseData.sqlite3, jamais réapparu côté
            # pilote -- demande explicite utilisateur : "rend plus
            # robuste la detection de tout les sautoniax") -- cause
            # confirmée par les logs : entre l'envoi d'un chunk par le
            # serveur (telecharger_fichier_debut/chunk plus haut) et la
            # prochaine demande de l'exécutant, celui-ci peut légitimement
            # rester silencieux plusieurs dizaines de secondes (décodage
            # + écriture disque d'un chunk de plusieurs Mo, cf. logs
            # DIAG_TELECHARGEMENT attente_ack=59.9s sur un chunk de
            # 5 242 880 octets) -- bien au-delà de SEUIL_SILENCE_SUSPECT_
            # SECONDES (35s, dimensionné pour un heartbeat de 15s, pas
            # pour un transfert de fichier). connexion.derniere_activite
            # n'est mise à jour qu'à la RÉCEPTION d'un message complet
            # (cf. route_websocket) -- tant que l'exécutant digère un
            # chunk volumineux, aucun message n'arrive, donc le watchdog
            # le jugeait à tort déconnecté et le retirait du registre en
            # PLEIN transfert. L'exécutant continuait pourtant le
            # téléchargement (WebSocket resté ouvert des deux côtés) et
            # finissait par annoncer "sautoniax_pret" -- mais sans jamais
            # renvoyer de "register", donc sans jamais réapparaître dans
            # executants_detail_change côté pilote : invisible dans
            # l'onglet malgré une connexion bel et bien fonctionnelle.
            #
            # Un transfert de fichier ACTIF sur cette connexion
            # (connexion.telechargement_en_cours, cf. telecharger_
            # fichier_debut/_fin plus haut -- déjà posé/vidé à cet effet,
            # aucune donnée nouvelle à maintenir) est donc exempté du
            # calcul de silence : ce protocole a sa propre notion de
            # progression (chaque chunk traité), le watchdog générique
            # n'a pas besoin d'y superposer sa propre horloge, faite pour
            # détecter l'absence TOTALE d'activité, pas un simple silence
            # entre deux chunks d'un transfert par ailleurs sain.
            if connexion.telechargement_en_cours is not None:
                continue
            silence = maintenant - connexion.derniere_activite
            if silence < SEUIL_SILENCE_SUSPECT_SECONDES:
                continue
            executants_encore_silencieux.add(connexion.id_connexion)
            if connexion.id_connexion in deja_alertes:
                # BUGFIX (badge clone bloqué indéfiniment en "en cours" --
                # cf. section retrait ci-dessous) : déjà alerté ne veut PAS
                # dire déjà retiré -- avant ce correctif, ce `continue`
                # sautait l'exécutant à CHAQUE tick suivant du watchdog dès
                # la 2e alerte, donc le retrait plus bas (exécuté seulement
                # pour un exécutant fraîchement ajouté à deja_alertes)
                # n'avait jamais lieu non plus. Le retrait doit se produire
                # une seule fois -- ici, sur CE `continue` -- mais pas être
                # sauté avec lui.
                if connexion in registre.executants():
                    executants_a_retirer.append(connexion)
                continue  # déjà signalé pour cet épisode de silence, pas de répétition
            deja_alertes.add(connexion.id_connexion)
            logger.warning(
                "exécutant silencieux : %s (id=%s) -- aucun message reçu depuis %.0fs "
                "(connexion WebSocket toujours ouverte, pas de WebSocketDisconnect)",
                connexion.nom, connexion.id_connexion, silence,
            )
            message = json.dumps({
                "type": "executant_silencieux",
                # PATCH (identité stable par nom) -- le pilote route/
                # mémorise tout par nom désormais (cf. Connexion.
                # vers_dict), ce message ciblé doit rester cohérent :
                # connexion.nom, pas id_connexion (qui n'a de sens
                # qu'en interne au serveur).
                "id_executant": connexion.nom,
                "nom": connexion.nom,
                "silence_secondes": round(silence, 1),
            })
            # CORRECTIF (bug n°3) -- cf. diffuser_liste_executants ci-dessus.
            for pilote in registre.pilotes():
                try:
                    async with registre.verrou_pour(pilote.websocket):
                        await pilote.websocket.send_text(message)
                except Exception:
                    pass
        # BUGFIX (demande explicite utilisateur : "sa ne fonctionne pas ,
        # sa contionnue de mettre le badge qui tourne , alors que sa
        # devais devennir reconnecter" -- lire : "déconnecté", pas
        # "reconnecter") -- CAUSE RÉELLE : ce watchdog se contentait
        # d'ALERTER (log + message "executant_silencieux" ci-dessus) mais
        # ne retirait JAMAIS l'exécutant de `registre`. Or côté pilote,
        # TaskConfigScreen._invalider_executions_clone_disparues (cf.
        # AutoniaX.py) ne marque un profil clone "deconnecte" QUE quand
        # son id_executant disparaît de `executants_detail_change` --
        # signal lui-même émis UNIQUEMENT par diffuser_liste_executants(),
        # lue depuis `registre.executants()`. Un exécutant qui gèle sans
        # fermer proprement son WebSocket (pas de WebSocketDisconnect, cf.
        # docstring de _boucle_watchdog_executants) ne déclenchait donc
        # JAMAIS le retrait normal (finally de route_websocket, plus bas)
        # -- il restait pour toujours dans `registre.executants()`, donc
        # pour toujours dans ids_executants_actifs côté pilote, donc
        # jamais marqué "deconnecte" : le badge tournait indéfiniment.
        #
        # Ce watchdog est le SEUL endroit qui sait qu'un exécutant au
        # WebSocket ouvert ne répond plus -- c'est donc ici, et
        # seulement ici, qu'un vrai retrait peut être déclenché pour ce
        # cas précis (distinct du retrait normal sur WebSocketDisconnect,
        # déjà géré ailleurs et inchangé). Retrait différé d'UN tick
        # (executants_a_retirer, jamais retiré pendant qu'on itère
        # registre.executants() lui-même juste au-dessus) plutôt
        # qu'immédiat dès le premier silence détecté : laisse UNE marge
        # (le prochain tick de INTERVALLE_WATCHDOG_SECONDES) après la
        # première alerte avant de conclure à une déconnexion définitive,
        # pour ne jamais retirer sur une unique lecture de silence limite
        # -- cohérent avec "pas de relance automatique" déjà acté côté
        # pilote (cf. docstring _invalider_executions_clone_disparues) :
        # ce correctif ne fait QUE permettre au statut "deconnecte" de se
        # déclencher, il ne change rien à la politique de reprise
        # (toujours manuelle, via le bouton ▶ existant).
        for connexion in executants_a_retirer:
            registre.retirer(connexion.id_connexion)
            logger.warning(
                "exécutant retiré du registre après silence confirmé : %s (id=%s) -- "
                "toujours aucun message depuis %.0fs, considéré déconnecté.",
                connexion.nom, connexion.id_connexion,
                maintenant - connexion.derniere_activite,
            )
        if executants_a_retirer:
            await diffuser_liste_executants()
        # Un exécutant qui n'est plus dans executants_encore_silencieux a
        # soit repris contact (derniere_activite rafraîchie entre-temps),
        # soit s'est déconnecté (registre.retirer, plus dans registre.
        # executants() du tout) -- dans les deux cas, purge de deja_alertes
        # pour qu'un FUTUR épisode de silence sur ce même id redéclenche
        # bien une alerte, plutôt que de rester marqué "déjà alerté" pour
        # toujours après une seule reprise.
        deja_alertes &= executants_encore_silencieux


@app.on_event("startup")
async def _lancer_watchdog_executants():
    """Démarre _boucle_watchdog_executants comme tâche de fond dès que le
    serveur est prêt à recevoir des requêtes -- une seule fois pour toute
    la durée de vie du process (pas relancée par connexion). La référence
    à la tâche n'a pas besoin d'être conservée : elle tourne pour
    toujours (boucle infinie), le process entier s'arrête avec elle."""
    asyncio.create_task(_boucle_watchdog_executants())


@app.get("/")
async def racine():
    """Simple endpoint de vie -- utile pour vérifier que le déploiement
    Render répond (avant même de tester le WebSocket), et pour un futur
    "health check" Render si besoin."""
    return {
        "service": "serveurT",
        "statut": "en ligne",
        "connexions_actives": len(registre.connexions),
        "stockage_configure": stockage.configure,
    }


@app.get("/fichier/{cle:path}")
async def telecharger_fichier_http(cle: str):
    """Téléchargement HTTP direct d'un fichier du bucket B2 (PATCH --
    problème d'oeuf-et-la-poule pour le notebook Kaggle : le protocole
    telecharger_fichier_debut/_chunk/_fin passe par ClientServeurT, qui
    n'existe qu'À L'INTÉRIEUR d'AutoniaX.py -- impossible de l'utiliser
    pour télécharger AutoniaX.py lui-même avant de l'avoir. Cette route
    HTTP simple contourne le problème : `wget`/`curl` suffisent, aucun
    protocole WebSocket ni aucune dépendance Python nécessaire côté
    notebook pour cette toute première récupération).

    ÉLARGIE à toute clé du bucket, plus seulement "App/" (retour
    explicite utilisateur -- contexte de test : "fait le pour tout") --
    même route, même mécanisme HTTP simple qu'avant pour AutoniaX.py,
    désormais utilisée aussi pour mouseData.sqlite3/project.json/
    service_api.zip/profils. Route toujours sans authentification :
    n'importe qui connaissant l'URL du tunnel peut appeler cette route
    et lire n'importe quel fichier du bucket, profils compris (donc
    d'éventuels cookies/sessions utilisateur qu'ils contiennent) --
    accepté explicitement pour ce test, à revoir avant tout usage hors
    contexte de test."""
    # Normalisation (contre un éventuel "../" pour sortir du bucket) --
    # {cle:path} chez Starlette capture la chaîne brute sans jamais la
    # normaliser elle-même.
    cle = posixpath.normpath(cle).lstrip("/")
    if cle == "." or "../" in cle or cle == "..":
        logger.warning("telecharger_fichier_http refusé : clé invalide ('%s')", cle)
        return JSONResponse(
            status_code=403,
            content={"erreur": "Clé invalide."},
        )
    if not stockage.configure:
        logger.warning("telecharger_fichier_http refusé : stockage non configuré")
        return JSONResponse(status_code=503, content={"erreur": "Stockage non configuré côté serveurT."})
    try:
        if not await stockage.existe(cle):
            return JSONResponse(status_code=404, content={"erreur": f"Fichier introuvable ('{cle}')."})
        contenu = await stockage.telecharger_bytes(cle)
        logger.info("telecharger_fichier_http : '%s' servi (%d octets)", cle, len(contenu))
        return Response(content=contenu, media_type="application/octet-stream")
    except Exception as e:
        logger.exception("Échec telecharger_fichier_http ('%s')", cle)
        return JSONResponse(status_code=500, content={"erreur": str(e)})


@app.get("/logs")
async def obtenir_logs_serveur():
    """PATCH (bouton "Copier tous les logs", source serveurT). Renvoie
    TOUTES les lignes accumulées dans tampon_journal depuis le démarrage
    du process -- pas de troncature, pas de pagination (demande
    explicite utilisateur : "depuis le demarage, pas juste les n dernier
    ligne"). Route HTTP publique, sans authentification -- même choix
    que GET /fichier/... pour l'aspect "pas de protocole WebSocket
    nécessaire pour une simple lecture", mais SANS donnée sensible ici
    (pas d'identifiants B2, pas de contenu de profil : uniquement des
    lignes de log serveur), donc pas de restriction de préfixe
    équivalente à nécessiter."""
    return {"logs": tampon_journal.lignes}


@app.websocket("/ws")
async def route_websocket(websocket: WebSocket):
    await websocket.accept()

    # PATCH (migration Colab+tunnel -- demande explicite utilisateur :
    # "il faut que on a une confiramtion valide, donc si en sessayent de
    # se connecter les mautoniax ou sautoniax echoue ou se connecte un
    # une mauvaise url ou puisse refuser") -- message envoyé IMMÉDIATEMENT
    # à l'ouverture, avant même "register" : preuve que cette URL (lue
    # depuis ServeurT/url_tunnel.txt sur B2, potentiellement périmée --
    # l'URL change à CHAQUE redémarrage du tunnel, cf. Quick Tunnel
    # Cloudflare) pointe bien vers CE serveurT et pas vers un service
    # totalement différent qui répondrait par hasard sur ce port/domaine
    # (ou plus simplement : que la connexion WebSocket a réellement
    # abouti, ce qu'un simple "ws ouvert sans erreur" ne garantit pas
    # toujours selon le client). Cf. AutoniaX.py, ClientServeurT --
    # attend ce message AVANT d'envoyer "register", et retente une
    # nouvelle lecture de l'URL sur B2 si absent/timeout.
    await websocket.send_text(json.dumps({
        "type": "serveurT_bonjour",
        "version_protocole": 1,
    }))

    # Identifiant de connexion technique (PAS l'identité stable du
    # sAutoniax -- cf. cahier section 5.4, point encore ouvert :
    # "quel identifiant utiliser pour qu'il soit reconnu d'une session à
    # l'autre" -- non tranché à l'Étape 0, on utilise pour l'instant
    # l'objet websocket lui-même comme clé, suffisant pour prouver la
    # chaîne de bout en bout).
    id_connexion = str(id(websocket))
    connexion = Connexion(websocket, id_connexion)

    try:
        while True:
            texte_brut = await websocket.receive_text()
            # PATCH (watchdog exécutants silencieux) -- horodate CE message
            # en tout premier, avant même de tenter de le parser : un
            # message JSON invalide compte quand même comme un signe de
            # vie de la connexion (cf. derniere_activite, comparé plus
            # bas par _boucle_watchdog_executants), la connexion n'est
            # "silencieuse" QUE si rien n'arrive du tout, pas si ce
            # qu'elle envoie est mal formé.
            connexion.derniere_activite = time.monotonic()
            try:
                message = json.loads(texte_brut)
            except json.JSONDecodeError:
                logger.warning("Message JSON invalide reçu, ignoré : %r", texte_brut[:200])
                continue

            type_message = message.get("type")

            if type_message == "register":
                role = message.get("role")
                if role not in ROLES_VALIDES:
                    logger.warning("register refusé, rôle invalide : %r", role)
                    await websocket.send_text(json.dumps({
                        "type": "erreur",
                        "message": f"Rôle invalide, attendu un de {sorted(ROLES_VALIDES)}.",
                    }))
                    continue

                connexion.role = role
                connexion.nom = message.get("nom", "")
                # AJOUT (cf. docstring Connexion.id_pilote_stable) : reçu
                # tel quel, "" si absent (ancien mAutoniax non mis à jour --
                # Registre.pilote_par_id retombe alors sur son repli
                # id_connexion, cf. sa docstring). Non concerné pour un
                # exécutant (déjà résolu par nom, cf. executant_par_id) --
                # lu inconditionnellement ici, sans effet s'il est absent
                # du message.
                connexion.id_pilote_stable = message.get("id_pilote_stable", "")

                # PATCH (identité stable par nom) -- un EXÉCUTANT sans nom
                # (ou nom réduit à des espaces) ne peut PAS être admis : la
                # contrainte d'unicité de Registre.ajouter() ne s'applique
                # que si connexion.nom est "truthy", donc un nom vide la
                # contournerait silencieusement (aucune protection contre
                # deux sAutoniax "anonymes" simultanés qui s'écraseraient
                # mutuellement dans routage par nom -- cf. main_sautoniax,
                # qui retombe sur "sautoniax" par défaut SEULEMENT si ni
                # --instance-id ni --profil ne sont fournis ; mais un nom
                # vide, lui, n'a jamais de sens et doit être refusé net
                # plutôt que de laisser une ambiguïté silencieuse s'installer
                # dans le registre). Un PILOTE, en revanche, n'a besoin
                # d'aucune identité stable (pas de contrainte d'unicité, cf.
                # docstring Registre.ajouter) : un nom vide reste toléré
                # pour ce rôle, inchangé.
                if role == "executant" and not connexion.nom.strip():
                    logger.warning("register refusé, nom vide pour un exécutant (id=%s)", id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "erreur",
                        "message": "Un sAutoniax doit avoir un nom non vide pour s'enregistrer.",
                    }))
                    continue

                registre.ajouter(connexion)
                logger.info("register : %s (%s) id=%s", connexion.nom, role, id_connexion)

                # PATCH (identité stable par nom) -- "id" renvoyé au CLIENT
                # lui-même lors de son propre register doit être cohérent
                # avec ce que vers_dict() expose aux AUTRES (les pilotes) :
                # pour un exécutant, c'est désormais son nom, PAS
                # id_connexion (qui change à chaque reconnexion). Motif :
                # côté sAutoniax, ClientServeurT._id_serveur (rempli à partir
                # de CE champ, cf. _traiter_message) sert à reconnaître les
                # demandes qui LE ciblent (cf. _sur_regler_capture_instance_
                # demande, comparaison à instance_id_visee) -- et le pilote,
                # lui, cible désormais par nom (cf. combo_executant_reseau.
                # currentData(), qui stocke maintenant le "id" reçu dans
                # vers_dict(), donc le nom). Si ce champ restait id_connexion
                # ici, un sAutoniax ne reconnaîtrait plus jamais les demandes
                # qui lui sont adressées (comparaison nom vs id technique,
                # toujours fausse) -- exactement la classe de bug que
                # l'option B doit éliminer, pas seulement déplacer côté
                # opposé. Pour un PILOTE, id_connexion reste renvoyé tel
                # quel dans CE champ précis ("register_ok.id", jamais
                # relu par le client -- cf. ClientServeurT._sur_message,
                # qui ignore ce champ pour role="pilote") : AUCUNE
                # RÉGRESSION à corriger ici. Un pilote possède désormais
                # bel et bien une notion d'identité stable À PART, cf.
                # AJOUT plus récent Connexion.id_pilote_stable/Registre.
                # pilote_par_id (correctif "badge/spinner de cellule
                # bloqué en cours indéfiniment") -- mais celle-ci transite
                # PAR UN CHAMP SÉPARÉ du register ("id_pilote_stable", cf.
                # juste au-dessus), jamais par ce "register_ok.id" -- pas
                # de raison de le changer ici, ce serait sans effet côté
                # client et romprait potentiellement un appelant qui en
                # dépendrait déjà ailleurs.
                id_public = connexion.nom if role == "executant" else id_connexion
                await websocket.send_text(json.dumps({
                    "type": "register_ok",
                    "id": id_public,
                }))

                if role == "executant":
                    await diffuser_liste_executants()
                elif role == "pilote":
                    # Un pilote qui vient de s'enregistrer reçoit
                    # immédiatement l'état actuel (pas besoin d'attendre
                    # qu'un exécutant se (dé)connecte pour voir quelque
                    # chose, cf. critère de validation de l'Étape 0 :
                    # "depuis mAutoniax, voir apparaître un sAutoniax
                    # connecté").
                    await websocket.send_text(json.dumps({
                        "type": "executants_connectes",
                        "executants": [c.vers_dict() for c in registre.executants()],
                    }))

            elif type_message == "ping":
                # PATCH heartbeat (diagnostic : "pourquoi sa cest
                # deconnecter ?" -- coupure de connexion WebSocket par
                # le proxy/infra de Render apres un court silence sans
                # trafic applicatif, cf. AutoniaX.py/ClientServeurT.
                # _tache_heartbeat pour le detail complet du
                # diagnostic). Repond immediatement par un "pong" --
                # le contenu du message n'a aucune importance, seul
                # le fait qu'un data frame applicatif circule dans les
                # deux sens compte pour empecher un proxy intermediaire
                # de considerer la connexion comme inactive. Ne touche
                # ni au registre ni au role de la connexion : accepte
                # avant meme le register (aucune raison de le refuser,
                # un ping precoce ne peut rien casser).
                await websocket.send_text(json.dumps({"type": "pong"}))

            elif type_message in ("transit_demander", "transit_liberer"):
                # AJOUT (Transit Drive, cf. GestionnaireTransit) -- les DEUX seuls messages du protocole : demander un
                # zip libre, le libérer. Autorisés au pilote ET à l'exécutant (une fois enregistré). Réponse envoyée
                # à l'appelant seul, avec son « rid » recopié (corrélation côté client). Aucune donnée ne passe ici.
                rid = message.get("rid")
                if not connexion.role:
                    logger.warning("%s refusé : connexion non enregistrée id=%s", type_message, id_connexion)
                    reponse_transit = {"ok": False, "erreur": "Connexion non enregistrée (register requis)."}
                elif type_message == "transit_demander":
                    try:
                        reponse_transit = await transit.demander(id_connexion, connexion.nom)
                    except Exception as e:
                        logger.exception("Transit : échec de la demande de zip")
                        reponse_transit = {"ok": False, "erreur": f"Transit indisponible : {e}"}
                else:
                    reponse_transit = transit.liberer(str(message.get("slot", "")), str(message.get("jeton", "")))
                reponse_transit["type"] = "transit_attribue" if type_message == "transit_demander" else "transit_libere"
                reponse_transit["rid"] = rid
                await websocket.send_text(json.dumps(reponse_transit))

            elif type_message == "statut_executant":
                # PATCH (Patch 4.2/4.9 -- statut détaillé par sAutoniax).
                # Réservé au rôle "executant" -- un sAutoniax signale ainsi
                # son propre statut ("inactif" / "demarrage_profils" /
                # "execution_projet:<nom>" / "erreur", cf. Connexion.statut)
                # à chaque changement d'état, spontanément (pas de
                # sollicitation du serveur). Rediffusé à tous les pilotes
                # via diffuser_liste_executants() -- RÉUTILISE le MÊME
                # type de message "executants_connectes" que la
                # connexion/déconnexion d'un exécutant (liste entière,
                # pas un delta), plutôt qu'un type "executant_statut_
                # change" dédié : le client n'a besoin de traiter qu'un
                # seul format de message pour les deux cas, cf.
                # ClientServeurT._traiter_message qui ne connaît que
                # "executants_connectes".
                if connexion.role != "executant":
                    logger.warning(
                        "statut_executant refusé (rôle=%r, seul 'executant' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    continue
                nouveau_statut = message.get("statut")
                if not isinstance(nouveau_statut, str) or not nouveau_statut:
                    logger.warning("statut_executant refusé : champ 'statut' manquant/invalide id=%s", id_connexion)
                    continue
                connexion.statut = nouveau_statut
                logger.info("statut_executant : '%s' -> %r id=%s", connexion.nom, nouveau_statut, id_connexion)
                await diffuser_liste_executants()

            elif type_message == "configurer_stockage":
                # PATCH stockage (demande explicite utilisateur : "je
                # veux que on connecte deja notre stokage cloudflare avec
                # notre serveur"). Réservé au rôle "pilote" -- un
                # exécutant n'a aucune raison de configurer les
                # identifiants de stockage globaux du serveurT.
                #
                # MIGRATION TOTALE Backblaze B2 -> Google Drive : les 4
                # champs B2 (access_key_id/secret_access_key/endpoint/
                # bucket_name) sont remplacés par 2 champs Drive
                # (cle_service_json/dossier_racine_id), envoyés par
                # ClientServeurT._envoyer_config_stockage (cf. AutoniaX.py,
                # _config_stockage_depuis_reglages) juste après le
                # register, systématiquement à chaque (re)connexion
                # puisque rien n'est persisté ici entre deux redémarrages
                # (cf. GestionnaireStockage, mémoire simple comme le
                # reste du registre à cette étape).
                if connexion.role != "pilote":
                    logger.warning(
                        "configurer_stockage refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "stockage_configure",
                        "ok": False,
                        "erreur": "Seul le pilote peut configurer le stockage.",
                    }))
                    continue

                cle_service_json = message.get("cle_service_json")
                dossier_racine_id = message.get("dossier_racine_id")

                if not all([cle_service_json, dossier_racine_id]):
                    logger.warning("configurer_stockage refusé : champ(s) manquant(s)")
                    await websocket.send_text(json.dumps({
                        "type": "stockage_configure",
                        "ok": False,
                        "erreur": "Champs manquants (cle_service_json, dossier_racine_id requis).",
                    }))
                    continue

                try:
                    stockage.configurer(
                        cle_service_json=cle_service_json,
                        dossier_racine_id=dossier_racine_id,
                        configure_par=id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "stockage_configure",
                        "ok": True,
                    }))
                except Exception as e:
                    logger.exception("Échec configuration stockage Drive")
                    await websocket.send_text(json.dumps({
                        "type": "stockage_configure",
                        "ok": False,
                        "erreur": str(e),
                    }))

            # RETRAIT (migration "Mettre à jour" vers Drive direct --
            # demande explicite utilisateur : "mAutoniax upload
            # directement ... plus de envoie autonome de fichier du
            # serveur vers les sautoniax"). Les handlers "mettre_a_jour_
            # app_debut"/"mettre_a_jour_app_chunk"/"mettre_a_jour_app_fin"
            # (protocole en chunks avec accumulation côté connexion.
            # upload_app puis stockage.uploader_bytes) ont été retirés :
            # le pilote (AutoniaX.py, ClientServeurT._envoyer_mise_a_jour_app)
            # uploade désormais DIRECTEMENT vers Drive pour les 5 éléments
            # (autoniax, mouse_data, project, service_api, serveur_t),
            # sans plus jamais envoyer ce protocole à ce serveur -- coupure
            # nette côté serveur également (point ouvert 1 de la spec,
            # tranché : pilote et exécutant déployés depuis le même
            # dépôt/notebook et redémarrés ensemble à chaque mise à jour).
            # Le cas "serveur_t" (dossier ServeurT/ + flag stat.json) est
            # désormais géré directement par GestionnaireStockageDriveDirect.
            # envoyer_serveur_py côté AutoniaX.py, sans plus jamais passer
            # par ce serveur non plus.

            elif type_message == "lister_stockage":
                # PATCH (demande explicite utilisateur : "dans l'onglet
                # de stokage tu vas rajouter un autre sous onglet:
                # stokage cloud, et il y aura l'affichage de
                # l'arborescence du cloud"). Réservé au rôle "pilote",
                # même logique que configurer_stockage/mettre_a_jour_
                # app. Renvoie la liste BRUTE et PLATE des clés du
                # bucket (ex. "App/AutoniaX.py") -- B2/S3 n'a pas de
                # vrais dossiers, c'est côté client (cf. AutoniaX.py,
                # _construire_arborescence_stockage) que ces clés sont
                # regroupées par préfixes communs pour ressembler à une
                # arborescence. Le serveur reste ici un simple relais
                # sans logique de présentation, cohérent avec le
                # principe "aucune logique métier AutoniaX" du fichier.
                if connexion.role != "pilote":
                    logger.warning(
                        "lister_stockage refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "stockage_liste",
                        "ok": False,
                        "erreur": "Seul le pilote peut lister le stockage.",
                    }))
                    continue

                if not stockage.configure:
                    logger.warning("lister_stockage refusé : stockage non configuré")
                    await websocket.send_text(json.dumps({
                        "type": "stockage_liste",
                        "ok": False,
                        "erreur": "Stockage non configuré -- configure d'abord le stockage (onglet Identifiant).",
                    }))
                    continue

                try:
                    objets = await stockage.lister_avec_taille()
                    logger.info("lister_stockage : %d clé(s) renvoyée(s)", len(objets))
                    await websocket.send_text(json.dumps({
                        "type": "stockage_liste",
                        "ok": True,
                        # "cles" gardé tel quel (rétrocompatibilité --
                        # un client qui ignore "objets" continue de
                        # fonctionner comme avant le PATCH taille).
                        "cles": [o["cle"] for o in objets],
                        "objets": objets,
                    }))
                except Exception as e:
                    logger.exception("Échec lister_stockage")
                    await websocket.send_text(json.dumps({
                        "type": "stockage_liste",
                        "ok": False,
                        "erreur": str(e),
                    }))

            elif type_message == "supprimer_stockage":
                # PATCH (demande explicite utilisateur : "dans le
                # sous-onglet stockage cloud, je veux que on puisse
                # désormais supprimer un élément directement, clic
                # droit et supprimer" -- même esprit que lister_
                # stockage juste au-dessus : réservé au rôle "pilote",
                # le serveurT reste un simple relais sans logique
                # métier AutoniaX (aucune vérification côté serveur
                # que les clés appartiennent bien au préfixe Profils/
                # ou autre -- StockageCloudScreen n'affiche/n'autorise
                # le clic-droit que sur des clés déjà listées, la
                # confirmation de suppression se fait côté UI).
                #
                # PATCH (demande explicite utilisateur : "je veux
                # aussi que même les dossiers puissent supprimer") --
                # "cles" est désormais une LISTE (un dossier
                # reconstruit ou une série groupée représentent
                # plusieurs clés S3, pas une seule) : chaque clé est
                # supprimée individuellement en boucle, une erreur sur
                # une clé n'interrompt pas les suivantes (mieux vaut
                # supprimer le maximum possible que tout annuler sur un
                # seul échec partiel, cohérent avec la prudence déjà en
                # place ailleurs dans ce fichier vis-à-vis des échecs
                # partiels). Repli sur l'ancien champ "cle" (str
                # unique) accepté aussi, pour rester compatible avec un
                # client plus ancien qui enverrait encore ce format.
                cles = message.get("cles")
                if cles is None:
                    cle_unique = message.get("cle", "")
                    cles = [cle_unique] if cle_unique else []

                if connexion.role != "pilote":
                    logger.warning(
                        "supprimer_stockage refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "stockage_supprimer_resultat",
                        "ok": False, "cles": cles,
                        "erreur": "Seul le pilote peut supprimer un élément du stockage.",
                    }))
                    continue

                if not stockage.configure:
                    logger.warning("supprimer_stockage refusé : stockage non configuré")
                    await websocket.send_text(json.dumps({
                        "type": "stockage_supprimer_resultat",
                        "ok": False, "cles": cles,
                        "erreur": "Stockage non configuré -- configure d'abord le stockage (onglet Identifiant).",
                    }))
                    continue

                if not cles:
                    await websocket.send_text(json.dumps({
                        "type": "stockage_supprimer_resultat",
                        "ok": False, "cles": cles,
                        "erreur": "Aucune clé fournie.",
                    }))
                    continue

                erreurs = []
                for cle in cles:
                    try:
                        await stockage.supprimer(cle)
                        logger.info("supprimer_stockage : '%s' supprimé", cle)
                    except Exception as e:
                        logger.exception("Échec supprimer_stockage ('%s')", cle)
                        erreurs.append(f"{cle} : {e}")

                if erreurs:
                    await websocket.send_text(json.dumps({
                        "type": "stockage_supprimer_resultat",
                        "ok": False, "cles": cles,
                        "erreur": "; ".join(erreurs),
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "stockage_supprimer_resultat",
                        "ok": True, "cles": cles,
                    }))

            elif type_message == "mettre_a_jour_meta_profil":
                # PATCH (colonne "Badges" de ProfilsCloudScreen, demande
                # explicite utilisateur : "je veux que il soit aussi
                # activable" -- clarifié : "en cloud ça persiste sur le
                # cloud") -- bascule UN champ (youtube/tiktok/ia/favori/
                # test) du <nom>.meta.json d'un profil DÉJÀ présent dans
                # Profils/, SANS toucher au zip (cf. envoyer_profil_fin
                # ci-dessous pour l'écriture initiale du meta.json à
                # l'upload -- même clé, même format JSON, mais ici on ne
                # fait QUE lire-fusionner-réécrire ce petit fichier,
                # aucun chunk de zip n'est impliqué). Réservé au rôle
                # "pilote", même garde-fous que lister_stockage/
                # supprimer_stockage juste au-dessus.
                nom_profil = message.get("nom_profil", "")
                champ = message.get("champ", "")
                valeur = message.get("valeur")
                CHAMPS_META_BADGES_VALIDES = {"youtube", "tiktok", "ia", "favori", "test"}

                if connexion.role != "pilote":
                    logger.warning(
                        "mettre_a_jour_meta_profil refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "meta_profil_maj_resultat",
                        "ok": False, "nom_profil": nom_profil, "champ": champ,
                        "erreur": "Seul le pilote peut modifier les métadonnées d'un profil.",
                    }))
                    continue

                if not stockage.configure:
                    logger.warning("mettre_a_jour_meta_profil refusé : stockage non configuré")
                    await websocket.send_text(json.dumps({
                        "type": "meta_profil_maj_resultat",
                        "ok": False, "nom_profil": nom_profil, "champ": champ,
                        "erreur": "Stockage non configuré -- configure d'abord le stockage (onglet Identifiant).",
                    }))
                    continue

                if not nom_profil or champ not in CHAMPS_META_BADGES_VALIDES or not isinstance(valeur, bool):
                    await websocket.send_text(json.dumps({
                        "type": "meta_profil_maj_resultat",
                        "ok": False, "nom_profil": nom_profil, "champ": champ,
                        "erreur": "Requête invalide (nom_profil/champ/valeur manquant ou incorrect).",
                    }))
                    continue

                cle_meta = f"Profils/{nom_profil}.meta.json"
                try:
                    try:
                        meta_existant = json.loads(await stockage.telecharger_bytes(cle_meta))
                        if not isinstance(meta_existant, dict):
                            meta_existant = {}
                    except DriveNoSuchKey:
                        # .meta.json pas encore créé pour ce profil (envoyé
                        # avant ce patch, ou par un client plus ancien) --
                        # on en crée un tout neuf plutôt que d'échouer,
                        # même tolérance que envoyer_profil_fin ci-dessous.
                        # CORRECTIF (migration B2 -> Drive) : telecharger_
                        # bytes lève désormais DriveNoSuchKey (pas
                        # ClientError) quand la clé est absente -- ce
                        # bloc catchait encore l'ancienne exception boto3,
                        # qui ne pouvait plus jamais être levée depuis
                        # GestionnaireStockage.telecharger_bytes.
                        meta_existant = {}
                    meta_existant[champ] = valeur
                    await stockage.uploader_bytes(cle_meta, json.dumps(meta_existant).encode("utf-8"))
                    logger.info(
                        "mettre_a_jour_meta_profil : '%s'.%s = %r", nom_profil, champ, valeur,
                    )
                except Exception as e:
                    logger.exception("Échec mettre_a_jour_meta_profil ('%s'.%s)", nom_profil, champ)
                    await websocket.send_text(json.dumps({
                        "type": "meta_profil_maj_resultat",
                        "ok": False, "nom_profil": nom_profil, "champ": champ,
                        "erreur": str(e),
                    }))
                    continue

                await websocket.send_text(json.dumps({
                    "type": "meta_profil_maj_resultat",
                    "ok": True, "nom_profil": nom_profil, "champ": champ, "valeur": valeur,
                }))

            elif type_message == "renommer_profil_cloud":
                # PATCH (bouton "Renommer" de Profils Cloud, demande
                # explicite utilisateur) -- renomme "<ancien_nom>.zip"
                # ET "<ancien_nom>.meta.json" (ce dernier seulement s'il
                # existe -- un profil envoyé par un très ancien client
                # sans meta.json reste renommable) dans Profils/, via
                # GestionnaireStockage.renommer (copy_object + delete_
                # object, cf. sa docstring). Réservé au rôle "pilote",
                # mêmes garde-fous que supprimer_stockage/mettre_a_jour_
                # meta_profil ci-dessus. cf. ClientServeurT.demander_
                # renommer_profil_cloud côté AutoniaX.py.
                ancien_nom = message.get("ancien_nom", "")
                nouveau_nom = message.get("nouveau_nom", "")

                if connexion.role != "pilote":
                    logger.warning(
                        "renommer_profil_cloud refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "renommer_profil_cloud_resultat",
                        "ok": False, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                        "erreur": "Seul le pilote peut renommer un profil.",
                    }))
                    continue

                if not stockage.configure:
                    logger.warning("renommer_profil_cloud refusé : stockage non configuré")
                    await websocket.send_text(json.dumps({
                        "type": "renommer_profil_cloud_resultat",
                        "ok": False, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                        "erreur": "Stockage non configuré -- configure d'abord le stockage (onglet Identifiant).",
                    }))
                    continue

                # Validation : noms non vides, distincts, et sans "/"
                # (un profil vit à plat dans Profils/, un "/" dans le
                # nouveau nom permettrait d'écrire hors de ce préfixe).
                if not ancien_nom or not nouveau_nom:
                    await websocket.send_text(json.dumps({
                        "type": "renommer_profil_cloud_resultat",
                        "ok": False, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                        "erreur": "Requête invalide (ancien_nom/nouveau_nom manquant).",
                    }))
                    continue
                if "/" in nouveau_nom or "\\" in nouveau_nom:
                    await websocket.send_text(json.dumps({
                        "type": "renommer_profil_cloud_resultat",
                        "ok": False, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                        "erreur": "Le nouveau nom ne peut pas contenir '/' ou '\\'.",
                    }))
                    continue
                if nouveau_nom == ancien_nom:
                    await websocket.send_text(json.dumps({
                        "type": "renommer_profil_cloud_resultat",
                        "ok": False, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                        "erreur": "Le nouveau nom est identique à l'ancien.",
                    }))
                    continue

                cle_zip_source = f"Profils/{ancien_nom}.zip"
                cle_zip_dest = f"Profils/{nouveau_nom}.zip"
                cle_meta_source = f"Profils/{ancien_nom}.meta.json"
                cle_meta_dest = f"Profils/{nouveau_nom}.meta.json"

                try:
                    if not await stockage.existe(cle_zip_source):
                        await websocket.send_text(json.dumps({
                            "type": "renommer_profil_cloud_resultat",
                            "ok": False, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                            "erreur": f"Profil '{ancien_nom}' introuvable dans le cloud.",
                        }))
                        continue
                    if await stockage.existe(cle_zip_dest):
                        await websocket.send_text(json.dumps({
                            "type": "renommer_profil_cloud_resultat",
                            "ok": False, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                            "erreur": f"Un profil nommé '{nouveau_nom}' existe déjà dans le cloud.",
                        }))
                        continue

                    await stockage.renommer(cle_zip_source, cle_zip_dest)
                    if await stockage.existe(cle_meta_source):
                        await stockage.renommer(cle_meta_source, cle_meta_dest)
                    logger.info(
                        "renommer_profil_cloud : '%s' -> '%s'", ancien_nom, nouveau_nom,
                    )
                except Exception as e:
                    logger.exception("Échec renommer_profil_cloud ('%s' -> '%s')", ancien_nom, nouveau_nom)
                    await websocket.send_text(json.dumps({
                        "type": "renommer_profil_cloud_resultat",
                        "ok": False, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                        "erreur": str(e),
                    }))
                    continue

                await websocket.send_text(json.dumps({
                    "type": "renommer_profil_cloud_resultat",
                    "ok": True, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                }))

            elif type_message == "envoyer_profil_debut":
                # PATCH (bloc "Envoyer un profil" de MiseAJourStockageScreen
                # -- demande explicite utilisateur : "j'aimerais envoyer un
                # profil complet vers le cloud ... dans un dossier nommé
                # Test et dans le sous dossier Profils", puis "vraie
                # progression par chunks"). Ouvre une session d'upload EN
                # CHUNKS pour cette connexion (cf. UploadProfilEnCours) --
                # remplace silencieusement toute session précédente non
                # terminée sur CETTE connexion (un nouvel envoi écrase
                # l'état d'un envoi abandonné, cohérent avec le choix
                # "simple et fiable" déjà fait ailleurs).
                #
                # PATCH (upload PAR UN EXÉCUTANT -- demande explicite
                # utilisateur : "un bouton de mise a jour de ce profils
                # vers le cloud en passant par le serveurT", pour renvoyer
                # un profil potentiellement modifié en session depuis un
                # sAutoniax distant). Ouvert désormais aux DEUX rôles
                # ("pilote" ET "executant") -- même protocole EXACT des
                # deux côtés (cf. ClientServeurT.envoyer_profil, déjà
                # utilisable tel quel par n'importe quel rôle côté client,
                # aucune vérification de rôle là-bas), seule la SOURCE du
                # zip change (local pilote vs dossier profil sAutoniax,
                # cf. handler demander_upload_profil_vers_cloud plus bas
                # qui déclenche cet appel côté exécutant).
                if connexion.role not in ("pilote", "executant"):
                    logger.warning(
                        "envoyer_profil_debut refusé (rôle=%r) id=%s", connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_debut_ack", "ok": False,
                        "erreur": "Seul un pilote ou un exécutant peut envoyer un profil.",
                    }))
                    continue
                if not stockage.configure:
                    logger.warning("envoyer_profil_debut refusé : stockage non configuré")
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_debut_ack", "ok": False,
                        "erreur": "Stockage non configuré -- configure d'abord le stockage (onglet Identifiant).",
                    }))
                    continue

                nom_profil = message.get("nom_profil")
                taille_totale = message.get("taille_totale_octets")
                nb_chunks = message.get("nb_chunks")
                if not nom_profil or not isinstance(taille_totale, int) or not isinstance(nb_chunks, int) or nb_chunks <= 0:
                    logger.warning("envoyer_profil_debut refusé : champ(s) manquant(s) ou invalide(s)")
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_debut_ack", "ok": False,
                        "erreur": "Champs manquants ou invalides (nom_profil, taille_totale_octets, nb_chunks requis).",
                    }))
                    continue

                # Si une session précédente traînait (envoi abandonné),
                # on nettoie son fichier temp avant d'en ouvrir un nouveau.
                if connexion.upload_profil is not None:
                    connexion.upload_profil.nettoyer()
                connexion.upload_profil = UploadProfilEnCours(nom_profil, taille_totale, nb_chunks)
                logger.info(
                    "envoyer_profil_debut : '%s' (%d octets, %d chunk(s) attendu(s)) id=%s",
                    nom_profil, taille_totale, nb_chunks, id_connexion,
                )
                await websocket.send_text(json.dumps({"type": "envoi_profil_debut_ack", "ok": True}))

            elif type_message == "envoyer_profil_chunk":
                # Accepte le chunk STRICTEMENT dans l'ordre (index ==
                # prochain_index_attendu) -- le client envoie séquentiellement
                # (cf. ClientServeurT._envoyer_profil) donc pas besoin de
                # gérer un désordre, mais on le REFUSE explicitement plutôt
                # que de l'accepter silencieusement au mauvais endroit dans
                # le fichier (ce qui corromprait le zip assemblé sans que
                # personne ne le sache avant l'ouverture du zip côté humain).
                session = connexion.upload_profil
                if session is None:
                    logger.warning("envoyer_profil_chunk refusé : aucun envoi en cours id=%s", id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_chunk_ack", "ok": False,
                        "erreur": "Aucun envoi de profil en cours (envoyer_profil_debut requis d'abord).",
                    }))
                    continue

                index = message.get("index")
                contenu_b64 = message.get("contenu_b64")
                if index != session.prochain_index_attendu:
                    logger.warning(
                        "envoyer_profil_chunk refusé : index=%r attendu=%d id=%s",
                        index, session.prochain_index_attendu, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_chunk_ack", "ok": False, "index": index,
                        "erreur": f"Chunk hors ordre (attendu {session.prochain_index_attendu}).",
                    }))
                    continue

                try:
                    contenu_bytes = base64.b64decode(contenu_b64)
                    session.ecrire_chunk(contenu_bytes)
                    session.prochain_index_attendu += 1
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_chunk_ack", "ok": True, "index": index,
                    }))
                except Exception as e:
                    logger.warning("envoyer_profil_chunk : échec écriture chunk %r (%s)", index, e)
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_chunk_ack", "ok": False, "index": index, "erreur": str(e),
                    }))

            elif type_message == "envoyer_profil_fin":
                # Tous les chunks reçus (vérifié via prochain_index_attendu
                # == nb_chunks_attendus) -- assemble = le fichier temp EST
                # déjà le zip complet (écrit au fil des chunks, cf.
                # UploadProfilEnCours.ecrire_chunk), il ne reste qu'à
                # l'uploader vers B2 puis nettoyer le temporaire, que
                # l'upload B2 réussisse ou échoue (jamais de fichier
                # orphelin laissé sur le disque Render après ce message).
                session = connexion.upload_profil
                if session is None:
                    logger.warning("envoyer_profil_fin refusé : aucun envoi en cours id=%s", id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_resultat", "ok": False,
                        "erreur": "Aucun envoi de profil en cours.",
                    }))
                    continue

                if session.prochain_index_attendu != session.nb_chunks_attendus:
                    logger.warning(
                        "envoyer_profil_fin refusé : %d/%d chunk(s) reçu(s) id=%s",
                        session.prochain_index_attendu, session.nb_chunks_attendus, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_resultat", "ok": False, "nom_profil": session.nom_profil,
                        "erreur": f"Envoi incomplet ({session.prochain_index_attendu}/{session.nb_chunks_attendus} chunk(s)).",
                    }))
                    session.nettoyer()
                    connexion.upload_profil = None
                    continue

                # Dossier "Profils" à la racine du bucket (PATCH -- demande
                # explicite utilisateur : "il y a plus de Test, j'ai dit que
                # tu crées un seul dossier Profils à la racine, Test n'est
                # plus qu'un badge" -- remplace l'ancien "Test/Profils/",
                # "Test" devient uniquement un badge togglable sur la carte
                # profil, cf. DELEGATE_ROLE_TEST côté AutoniaX.py, sans
                # aucun lien avec l'emplacement de stockage cloud).
                cle = f"Profils/{session.nom_profil}.zip"
                try:
                    contenu_zip = session.chemin_temp.read_bytes()
                    await stockage.uploader_bytes(cle, contenu_zip)
                    logger.info(
                        "envoyer_profil_fin : '%s' uploadé (%d octets) vers %s",
                        session.nom_profil, len(contenu_zip), cle,
                    )
                    # PATCH (Patch 4.3 -- onglet Profils Cloud) : "meta",
                    # objet JSON optionnel envoyé PAR LE CLIENT dans ce
                    # même message envoyer_profil_fin (cf. AutoniaX.py
                    # _envoyer_profil) -- {"pays", "ip", "proxy_configure",
                    # "date_envoi_iso"} construit côté pilote à partir de
                    # obtenir_config_profil(nom_profil) (PATCH -- "ip"
                    # ajouté au dict, demande explicite utilisateur :
                    # "sa naffihce pas les adresse ip"), PAS recalculé ici
                    # (le serveur ne connaît ni géoip ni le registre local
                    # profils_config.json, cf. principe "aucune logique
                    # métier AutoniaX" de ce fichier -- il se contente de
                    # stocker tel quel ce que le pilote lui donne). Absent
                    # ou invalide -> aucun meta.json écrit/mis à jour,
                    # SILENCIEUSEMENT (pas une erreur qui ferait échouer
                    # tout l'envoi du profil lui-même -- l'essentiel, le
                    # zip, est déjà bien uploadé au moment où ceci
                    # s'exécute) : un profil déjà présent AVANT ce patch,
                    # ou envoyé par un client plus ancien, reste listable
                    # sans metadata, cf. ProfilsCloudScreen côté client
                    # (case par case, valeurs par défaut si meta absent).
                    meta = message.get("meta")
                    if isinstance(meta, dict):
                        try:
                            cle_meta = f"Profils/{session.nom_profil}.meta.json"
                            await stockage.uploader_bytes(cle_meta, json.dumps(meta).encode("utf-8"))
                            logger.info("envoyer_profil_fin : meta.json écrit pour '%s'", session.nom_profil)
                        except Exception:
                            logger.exception("envoyer_profil_fin : échec écriture meta.json pour '%s' (ignoré)", session.nom_profil)
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_resultat", "ok": True,
                        "nom_profil": session.nom_profil, "taille_octets": len(contenu_zip),
                    }))
                    # PATCH (upload PAR UN EXÉCUTANT, cf. handler demander_
                    # upload_profil_vers_cloud plus haut) -- "id_pilote"
                    # présent UNIQUEMENT quand cet envoi a été déclenché à
                    # distance par ce pilote précis (cf. ClientServeurT
                    # côté sAutoniax, qui le transmet tel quel dans son
                    # propre envoyer_profil_fin une fois reçu via
                    # demander_upload_profil_vers_cloud) -- absent pour un
                    # envoi classique depuis MiseAJourStockageScreen
                    # (pilote local), qui reçoit déjà sa propre réponse
                    # ci-dessus, rien de plus à faire dans ce cas. Relais
                    # best-effort : un pilote déconnecté entre-temps ne
                    # doit jamais faire échouer l'upload lui-même, déjà
                    # réussi à ce stade.
                    id_pilote_upload = message.get("id_pilote", "")
                    if id_pilote_upload:
                        # CORRECTIF (cf. profils_sautoniax_resultat, même bug
                        # EXACT) : résolution par id_pilote_stable.
                        pilote_upload = registre.pilote_par_id(id_pilote_upload)
                        if pilote_upload is not None and pilote_upload.role == "pilote":
                            try:
                                async with registre.verrou_pour(pilote_upload.websocket):
                                    await pilote_upload.websocket.send_text(json.dumps({
                                        "type": "upload_profil_executant_resultat", "ok": True,
                                        "id_executant": connexion.nom, "nom_profil": session.nom_profil,
                                        "taille_octets": len(contenu_zip),
                                    }))
                            except Exception:
                                logger.exception("Échec relais upload_profil_executant_resultat vers pilote '%s'", id_pilote_upload)
                except Exception as e:
                    logger.exception("Échec upload profil (%s)", session.nom_profil)
                    await websocket.send_text(json.dumps({
                        "type": "envoi_profil_resultat", "ok": False,
                        "nom_profil": session.nom_profil, "erreur": str(e),
                    }))
                    id_pilote_upload = message.get("id_pilote", "")
                    if id_pilote_upload:
                        # CORRECTIF (cf. profils_sautoniax_resultat, même bug
                        # EXACT) : résolution par id_pilote_stable.
                        pilote_upload = registre.pilote_par_id(id_pilote_upload)
                        if pilote_upload is not None and pilote_upload.role == "pilote":
                            try:
                                async with registre.verrou_pour(pilote_upload.websocket):
                                    await pilote_upload.websocket.send_text(json.dumps({
                                        "type": "upload_profil_executant_resultat", "ok": False,
                                        "id_executant": connexion.nom, "nom_profil": session.nom_profil,
                                        "erreur": str(e),
                                    }))
                            except Exception:
                                logger.exception("Échec relais upload_profil_executant_resultat vers pilote '%s'", id_pilote_upload)
                finally:
                    session.nettoyer()
                    connexion.upload_profil = None

            elif type_message == "notifier_upload_profil_resultat":
                # AJOUT (migration upload profil -> Drive DIRECT, symétrique
                # du téléchargement déjà direct -- demande explicite
                # utilisateur : "sa ne doit plus passer par le serveur sa
                # doit directement uploader vers le drive puisque les
                # identifiant sont deja dans lapp"). Le fichier ET son
                # éventuel meta.json sont désormais uploadés DIRECTEMENT
                # vers Drive par le client (pilote ou sAutoniax), SANS
                # transiter par ce serveur (cf. AutoniaX.py,
                # GestionnaireStockageDriveDirect.envoyer_fichier_vers_cloud) :
                # ce serveur ne voit donc plus jamais les octets du profil
                # dans ce chemin. Seul le RÉSULTAT (ok/erreur) a encore
                # besoin de transiter par ici, uniquement pour relayer au
                # pilote distant qui avait demandé cet upload (id_pilote,
                # cf. demander_upload_profil_vers_cloud) -- un envoi
                # classique depuis un pilote LOCAL n'a jamais besoin de ce
                # message (il connaît déjà son propre résultat directement,
                # sans aller-retour serveur).
                #
                # Réservé aux rôles "executant"/"pilote" (les deux peuvent
                # légitimement uploader un profil vers Drive direct) --
                # simple relais ciblé, même patron EXACT que le bloc
                # id_pilote de envoyer_profil_fin ci-dessus, mais SANS
                # jamais toucher au stockage ni à un quelconque
                # UploadProfilEnCours (aucun octet à gérer ici).
                id_pilote_notif = message.get("id_pilote", "")
                nom_profil_notif = message.get("nom_profil", "")
                ok_notif = bool(message.get("ok"))
                if not id_pilote_notif or not nom_profil_notif:
                    logger.warning(
                        "notifier_upload_profil_resultat refusé : id_pilote/nom_profil manquant(s) id=%s",
                        id_connexion,
                    )
                    continue
                pilote_notif = registre.pilote_par_id(id_pilote_notif)
                if pilote_notif is not None and pilote_notif.role == "pilote":
                    charge_utile = {
                        "type": "upload_profil_executant_resultat", "ok": ok_notif,
                        "id_executant": connexion.nom, "nom_profil": nom_profil_notif,
                    }
                    if ok_notif:
                        charge_utile["taille_octets"] = message.get("taille_octets", 0)
                    else:
                        charge_utile["erreur"] = message.get("erreur", "Erreur inconnue")
                    try:
                        async with registre.verrou_pour(pilote_notif.websocket):
                            await pilote_notif.websocket.send_text(json.dumps(charge_utile))
                        logger.info(
                            "notifier_upload_profil_resultat : '%s' ok=%s -- relayé au pilote '%s'",
                            nom_profil_notif, ok_notif, id_pilote_notif,
                        )
                    except Exception:
                        logger.exception("Échec relais notifier_upload_profil_resultat vers pilote '%s'", id_pilote_notif)
                else:
                    logger.warning(
                        "notifier_upload_profil_resultat : pilote '%s' introuvable/déconnecté -- résultat perdu (best-effort).",
                        id_pilote_notif,
                    )

            elif type_message == "demander_upload_profil_vers_cloud":
                # PATCH (bouton "Mettre à jour vers le cloud" du panneau de
                # propriétés, onglet Instances -- demande explicite
                # utilisateur : "un bouton de mise a jour de ce profils
                # vers le cloud en passant par le serveurT"). Réservé au
                # rôle "pilote". Simple relais CIBLÉ (même patron EXACT
                # que kill_projet/kill_profil ci-dessus -- le serveur ne
                # sait pas zipper/lire le disque du sAutoniax, cf. principe
                # "aucune logique métier AutoniaX") : l'exécutant visé,
                # une fois ce message reçu, déclenche lui-même son propre
                # envoyer_profil_debut/_chunk/_fin (cf. ClientServeurT.
                # envoyer_profil, réutilisé tel quel côté sAutoniax,
                # PATCH ci-dessus qui ouvre ce protocole au rôle
                # "executant") -- CE message-ci ne fait que déclencher ce
                # déclenchement, il ne transporte aucune donnée de profil
                # lui-même.
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_upload_profil_vers_cloud refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_upload_profil_vers_cloud_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander un upload de profil vers le cloud.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_profil = message.get("nom_profil", "")
                if not nom_profil:
                    await websocket.send_text(json.dumps({
                        "type": "demander_upload_profil_vers_cloud_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": "Champ 'nom_profil' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_upload_profil_vers_cloud refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_upload_profil_vers_cloud_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_upload_profil_vers_cloud", "nom_profil": nom_profil,
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_upload_profil_vers_cloud : transmis à '%s' (id=%s, profil=%r) par pilote id=%s",
                        cible.nom, id_executant, nom_profil, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_upload_profil_vers_cloud_ack", "ok": True,
                        "id_executant": id_executant, "nom_profil": nom_profil,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_upload_profil_vers_cloud à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_upload_profil_vers_cloud_ack", "ok": False,
                        "id_executant": id_executant, "nom_profil": nom_profil, "erreur": str(e),
                    }))

            elif type_message == "demander_renommer_profil_sautoniax":
                # PATCH (bouton "Renommer" du panneau de propriétés,
                # onglet Instances -- demande explicite utilisateur : "on
                # puisse renommer un profil qui est sur un sautoniax (on
                # le renomme quand il est fermé, pas en cours)"). Réservé
                # au rôle "pilote". Même patron EXACT que demander_upload_
                # profil_vers_cloud ci-dessus : simple relais CIBLÉ (le
                # serveur ne sait ni ne doit valider si le profil est
                # actif ou si le nouveau nom est déjà pris -- "aucune
                # logique métier AutoniaX" -- cf. AutoniaX.py,
                # _sur_renommer_profil_sautoniax_demande côté main_
                # sautoniax pour ces vérifications) : l'exécutant visé,
                # une fois ce message reçu, renomme lui-même son dossier
                # local puis répond via renommer_profil_sautoniax_resultat
                # (cf. bloc plus bas).
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_renommer_profil_sautoniax refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_renommer_profil_sautoniax_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander un renommage de profil.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                ancien_nom = message.get("ancien_nom", "")
                nouveau_nom = message.get("nouveau_nom", "")
                if not ancien_nom or not nouveau_nom:
                    await websocket.send_text(json.dumps({
                        "type": "demander_renommer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom, "erreur": "Champ 'ancien_nom' ou 'nouveau_nom' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_renommer_profil_sautoniax refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_renommer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom, "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_renommer_profil_sautoniax", "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_renommer_profil_sautoniax : transmis à '%s' (id=%s, '%s' -> '%s') par pilote id=%s",
                        cible.nom, id_executant, ancien_nom, nouveau_nom, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_renommer_profil_sautoniax_ack", "ok": True,
                        "id_executant": id_executant, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_renommer_profil_sautoniax à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_renommer_profil_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom, "erreur": str(e),
                    }))

            elif type_message == "renommer_profil_sautoniax_resultat":
                # PATCH (même feature que demander_renommer_profil_
                # sautoniax ci-dessus) -- résultat RÉEL renvoyé par
                # l'exécutant (cf. AutoniaX.py, ClientServeurT.envoyer_
                # renommer_profil_sautoniax_resultat), relayé CIBLÉ au
                # seul pilote demandeur (id_pilote transmis dans le
                # message reçu ici, connu de l'exécutant depuis le
                # message "demander_renommer_profil_sautoniax" original)
                # -- même patron EXACT que notifier_upload_profil_resultat
                # ci-dessus (résultat léger, aucun octet de profil
                # transporté ici). Réservé au rôle "executant".
                if connexion.role != "executant":
                    logger.warning(
                        "renommer_profil_sautoniax_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion,
                    )
                    continue
                id_pilote_cible = message.get("id_pilote", "")
                ancien_nom = message.get("ancien_nom", "")
                nouveau_nom = message.get("nouveau_nom", "")
                if not id_pilote_cible:
                    logger.warning(
                        "renommer_profil_sautoniax_resultat refusé : id_pilote manquant id=%s", id_connexion,
                    )
                    continue
                pilote_cible = registre.pilote_par_id(id_pilote_cible)
                if pilote_cible is not None and pilote_cible.role == "pilote":
                    charge_utile = {
                        "type": "renommer_profil_sautoniax_resultat", "ok": bool(message.get("ok")),
                        "id_executant": connexion.nom, "ancien_nom": ancien_nom, "nouveau_nom": nouveau_nom,
                        "erreur": message.get("erreur", ""),
                    }
                    try:
                        async with registre.verrou_pour(pilote_cible.websocket):
                            await pilote_cible.websocket.send_text(json.dumps(charge_utile))
                        logger.info(
                            "renommer_profil_sautoniax_resultat : '%s' -> '%s' ok=%s -- relayé au pilote '%s'",
                            ancien_nom, nouveau_nom, charge_utile["ok"], id_pilote_cible,
                        )
                    except Exception:
                        logger.exception("Échec relais renommer_profil_sautoniax_resultat vers pilote '%s'", id_pilote_cible)
                else:
                    logger.warning(
                        "renommer_profil_sautoniax_resultat : pilote '%s' introuvable/déconnecté -- résultat perdu (best-effort).",
                        id_pilote_cible,
                    )

            elif type_message == "demander_toggle_proxy_natif":
                # PATCH (SPEC_proxy_natif_tunnel.md, section 13.3 --
                # toggle "Proxy natif" par profil, panneau de propriétés
                # de l'onglet Instances). Réservé au rôle "pilote". Même
                # patron EXACT que demander_upload_profil_vers_cloud
                # ci-dessus (relais CIBLÉ pur, "aucune logique métier
                # AutoniaX" -- le serveur ne connaît ni ne valide l'état
                # "proxy natif" lui-même, il transmet juste l'ordre au
                # sAutoniax visé, qui décide seul de l'accepter ou non
                # -- ex. refus si le profil est actuellement actif, cf.
                # spec section 13.5) : l'exécutant visé répond via
                # toggle_proxy_natif_resultat plus bas (DIFFUSÉ à tous
                # les pilotes, même raisonnement que demarrer_profil_
                # isole_resultat -- ce nouvel état doit apparaître à
                # jour dans le panneau de n'importe quel pilote ayant ce
                # sAutoniax sélectionné, pas seulement celui qui a
                # cliqué le toggle).
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_toggle_proxy_natif refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_toggle_proxy_natif_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander le changement de proxy natif.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_profil = message.get("nom_profil", "")
                actif_demande = bool(message.get("actif", False))
                if not nom_profil:
                    await websocket.send_text(json.dumps({
                        "type": "demander_toggle_proxy_natif_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": "Champ 'nom_profil' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_toggle_proxy_natif refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_toggle_proxy_natif_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_toggle_proxy_natif", "nom_profil": nom_profil, "actif": actif_demande,
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_toggle_proxy_natif : transmis à '%s' (id=%s, profil=%r, actif=%s) par pilote id=%s",
                        cible.nom, id_executant, nom_profil, actif_demande, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_toggle_proxy_natif_ack", "ok": True,
                        "id_executant": id_executant, "nom_profil": nom_profil,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_toggle_proxy_natif à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_toggle_proxy_natif_ack", "ok": False,
                        "id_executant": id_executant, "nom_profil": nom_profil, "erreur": str(e),
                    }))

            elif type_message == "toggle_proxy_natif_resultat":
                # PATCH (cf. demander_toggle_proxy_natif ci-dessus) --
                # résultat RÉEL renvoyé par l'exécutant (ok=True/False
                # selon que le profil était disponible pour ce
                # changement, cf. spec section 13.5). DIFFUSÉ à tous les
                # pilotes connectés (même patron EXACT que demarrer_
                # profil_isole_resultat/creer_profil_sautoniax_resultat
                # -- PAS un relais ciblé au seul demandeur, contrairement
                # à demander_upload_profil_vers_cloud_ack qui n'est qu'un
                # accusé de transmission : ici c'est l'ÉTAT RÉEL du
                # profil qui change, potentiellement affiché dans
                # plusieurs panneaux pilotes ouverts en même temps sur ce
                # même sAutoniax). Réservé au rôle "executant".
                if connexion.role != "executant":
                    logger.warning("toggle_proxy_natif_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                message_diffuse = dict(message)
                message_diffuse["id_executant"] = connexion.nom
                logger.info(
                    "toggle_proxy_natif_resultat : '%s' -- profil=%r actif=%s ok=%s -- diffusé à %d pilote(s)",
                    connexion.nom, message.get("nom_profil", ""), message.get("actif", False),
                    message.get("ok", False), len(registre.pilotes()),
                )
                # CORRECTIF (bug n°3, cf. docstring de Registre.
                # _verrous_par_websocket -- même schéma EXACT que le bug
                # n°2 déjà corrigé sur /ws_tunnel : plusieurs connexions
                # exécutant, chacune dans sa propre tâche asyncio,
                # peuvent diffuser vers le MÊME pilote en même temps).
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps(message_diffuse))
                    except Exception:
                        logger.exception("Échec relais toggle_proxy_natif_resultat vers pilote '%s'", pilote.nom)

            elif type_message == "upload_profil_executant_echec_local":
                # PATCH (cf. demander_upload_profil_vers_cloud plus haut,
                # et ClientServeurT.envoyer_upload_profil_echec_local côté
                # AutoniaX.py) -- cas d'échec PRÉCOCE (profil absent
                # localement sur le sAutoniax visé, avant même toute
                # tentative d'upload B2) : DIFFUSÉ à tous les pilotes
                # connectés, même patron que statut_executant/kill_profil_
                # resultat_reel -- le message reçu ne porte pas id_pilote
                # (contrairement au cas normal d'échec en cours d'upload,
                # cf. bloc except de envoyer_profil_fin, qui lui CONNAÎT
                # id_pilote puisqu'il a été transmis dans ce même message
                # par ClientServeurT._envoyer_profil). Réservé au rôle
                # "executant". Réutilise le type "upload_profil_executant_
                # resultat" (ok=False) pour que le pilote n'ait qu'un seul
                # format de résultat à traiter, quelle que soit la cause
                # de l'échec.
                if connexion.role != "executant":
                    logger.warning(
                        "upload_profil_executant_echec_local refusé (rôle=%r) id=%s", connexion.role, id_connexion,
                    )
                    continue
                nom_profil = message.get("nom_profil", "")
                message_erreur = message.get("message", "")
                logger.info(
                    "upload_profil_executant_echec_local : '%s' -- profil=%r -- diffusé à %d pilote(s)",
                    connexion.nom, nom_profil, len(registre.pilotes()),
                )
                # CORRECTIF (bug n°3) -- cf. commentaire toggle_proxy_natif_resultat ci-dessus.
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps({
                                "type": "upload_profil_executant_resultat", "ok": False,
                                "id_executant": connexion.nom, "nom_profil": nom_profil, "erreur": message_erreur,
                            }))
                    except Exception:
                        logger.exception("Échec relais upload_profil_executant_echec_local vers pilote '%s'", pilote.nom)

            elif type_message == "telecharger_fichier_debut":
                # PATCH (protocole de téléchargement générique, sens
                # inverse de envoyer_profil_* -- demande explicite
                # utilisateur : "sAutoniax vas directement demander la
                # requette au serveur et telecharger"). Réservé au rôle
                # "executant" à l'origine (le pilote envoyait des
                # fichiers via envoyer_profil_*/mettre_a_jour_app, jamais
                # via ce protocole de téléchargement).
                #
                # PATCH E.2 -- ÉLARGI au rôle "pilote" (cf. cahier des
                # charges patchs.md : "un bouton Télécharger par entrée
                # terminée [...] télécharge les données traitées"). Ce
                # protocole est déjà générique par clé (aucune logique
                # métier, cf. docstring de GestionnaireStockage) : la
                # SEULE différence entre un sAutoniax qui télécharge un
                # profil et un pilote qui télécharge un résultat "Batch
                # Traité" est le RÔLE de qui demande, jamais le mécanisme
                # lui-même -- dupliquer tout ce protocole pour le pilote
                # aurait recréé un second chemin à maintenir pour
                # strictement le même comportement. connexion.
                # telechargement_en_cours fonctionne déjà indépendamment
                # du rôle (juste un état par connexion), rien d'autre à
                # changer plus bas dans telecharger_fichier_chunk/_fin.
                #
                # NOTE nommage : le client écoute les réponses sous le
                # type "telechargement_fichier_debut_ack" (PAS
                # "telecharger_fichier_debut_ack", cf. AutoniaX.py
                # _traiter_message) -- on renvoie donc bien avec le
                # "e" supplémentaire ("telechargement"), pour matcher
                # exactement ce que le client attend.
                # PATCH corrélation cle/index (diagnostic ack tardif qui
                # pollue la requête suivante -- cf. analyse : Future
                # unique et partagée côté client, résolue sans vérifier
                # que l'ack reçu correspond bien à la requête en vol).
                # 'cle' est maintenant lue EN PREMIER, avant tout
                # early-return, pour que TOUS les acks -- y compris les
                # refus (rôle, stockage non configuré, champ manquant) --
                # incluent 'cle' et permettent au client de filtrer un
                # ack tardif/désynchronisé plutôt que de résoudre
                # aveuglément la Future en attente.
                cle = message.get("cle")

                if connexion.role not in ("executant", "pilote"):
                    logger.warning(
                        "telecharger_fichier_debut refusé (rôle=%r, executant/pilote uniquement) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "telechargement_fichier_debut_ack", "ok": False, "cle": cle,
                        "erreur": "Seul un exécutant ou un pilote peut télécharger un fichier.",
                    }))
                    continue

                if not stockage.configure:
                    logger.warning("telecharger_fichier_debut refusé : stockage non configuré")
                    await websocket.send_text(json.dumps({
                        "type": "telechargement_fichier_debut_ack", "ok": False, "cle": cle,
                        "erreur": "Stockage non configuré -- le pilote doit configurer le stockage d'abord.",
                    }))
                    continue

                if not cle:
                    logger.warning("telecharger_fichier_debut refusé : champ 'cle' manquant")
                    await websocket.send_text(json.dumps({
                        "type": "telechargement_fichier_debut_ack", "ok": False, "cle": cle,
                        "erreur": "Champ manquant (cle requis).",
                    }))
                    continue

                try:
                    t_debut_total = time.monotonic()
                    if not await stockage.existe(cle):
                        logger.warning("telecharger_fichier_debut refusé : clé introuvable '%s'", cle)
                        await websocket.send_text(json.dumps({
                            "type": "telechargement_fichier_debut_ack", "ok": False, "cle": cle,
                            "erreur": f"Fichier introuvable dans le stockage ('{cle}').",
                        }))
                        continue

                    # DIAGNOSTIC (demande explicite utilisateur : "patcher
                    # les fichiers pour que ca logs assez d'infos ciblees
                    # pour trancher rapidement sur l'origine du probleme")
                    # -- timestamps monotonic (insensibles aux ajustements
                    # d'horloge système, contrairement à time.time()) à
                    # chaque étape : lecture B2, encodage base64, ENVOI
                    # réseau lui-même (l'étape la plus suspecte -- un
                    # `await websocket.send_text()` qui traîne alors que
                    # rien ne l'indique dans les logs actuels, cf.
                    # incident précédent où l'ack n'est jamais arrivé
                    # sans aucune exception loggée côté serveur).
                    t_avant_b2 = time.monotonic()
                    contenu = await stockage.telecharger_bytes(cle)
                    t_apres_b2 = time.monotonic()

                    # DIAGNOSTIC RÉSOLU (demande explicite utilisateur :
                    # "patcher les fichiers pour que ca logs assez
                    # d'infos ciblees pour trancher rapidement sur
                    # l'origine du probleme") -- les logs DIAG_
                    # TELECHARGEMENT (des deux côtés, serveur ET client)
                    # ont confirmé la cause avec certitude : le serveur
                    # traite et envoie chaque chunk en ~5ms (lecture +
                    # b64encode + json.dumps + envoi), le client reçoit
                    # et écrit chaque chunk en ~4ms -- mais entre les
                    # deux, ~6.04s fixes et quasi-constants séparaient
                    # chaque "envoi du chunk N par le serveur" et
                    # "réception de la demande du chunk N+1" côté client
                    # (attente_ack mesurée à 6.03-6.05s sur les 26 chunks
                    # testés, peu importe leur taille -- y compris le
                    # dernier chunk de 24 576 octets, bien plus petit,
                    # qui a payé le même délai). Régularité bien trop
                    # parfaite pour de la congestion réseau variable :
                    # c'est une latence FIXE du tunnel Cloudflare gratuit
                    # (trycloudflare.com) entre Kaggle et Colab, par
                    # aller-retour, indépendante de la taille du message
                    # -- ni un bug de ce code serveur, ni du code client.
                    #
                    # Conséquence directe : moins de chunks = moins de
                    # fois où ce délai fixe est payé. Un chunk UNIQUE
                    # couvrant tout le fichier (testé précédemment,
                    # nb_chunks=1, ~14.7 Mo encodé en base64 pour ce
                    # fichier de 10.8 Mo) avait échoué avec un
                    # TimeoutError sec après 30s -- AUCUN ack n'était
                    # jamais revenu, contrairement aux petits chunks qui
                    # finissaient toujours par arriver. La cause exacte
                    # de cet échec précis n'a jamais été confirmée (pas
                    # de limite de taille de message documentée
                    # publiquement pour cloudflared -- recherché sans
                    # résultat concluant), donc PAS de retour à un chunk
                    # unique tant que ce point reste incertain.
                    #
                    # Valeur retenue : 5 Mo (retour utilisateur explicite
                    # après discussion sur 4 Mo). Pour mouseData.sqlite3
                    # (11 034 624 octets) : 3 chunks au lieu de 22, donc
                    # 3 délais de ~6s payés au lieu de 22 -- environ 18-
                    # 20s de latence de tunnel au lieu de ~2min08,
                    # BEAUCOUP plus petit que le chunk unique qui avait
                    # échoué (5 Mo < 10.8 Mo), donc prudent vis-à-vis de
                    # cette limite non identifiée tout en restant un gain
                    # massif par rapport aux 512 Ko d'origine.
                    #
                    # CORRECTIF RADICAL, PUIS RE-CORRIGÉ (le "CORRECTIF
                    # RADICAL" précédent -- retour utilisateur explicite :
                    # "je veux le telechargement le plus rapidement
                    # possible" -- était revenu à un chunk UNIQUE
                    # (taille_chunk = len(contenu)) en attribuant les
                    # échecs à 5 Mo au seul heartbeat applicatif côté
                    # client (_tache_heartbeat), corrigé depuis. Ce
                    # heartbeat a bien été corrigé (il se suspend
                    # pendant tout transfert en chunks actif, et
                    # _attendre_ack_telechargement est passé à 120s),
                    # MAIS le chunk unique a de nouveau échoué en test
                    # réel après ce correctif : la connexion tombe
                    # (ConnectionClosedError sans frame de fermeture,
                    # ~88-90s après l'envoi du seul chunk) alors même
                    # que le heartbeat applicatif JSON continue d'être
                    # émis et que le ping/pong natif de la lib websockets
                    # côté client a ENTRE-TEMPS ÉTÉ DÉSACTIVÉ
                    # explicitement (ping_interval=None sur
                    # websockets.connect, cf. AutoniaX.py) pour ne plus
                    # risquer de fermer lui-même la connexion -- donc
                    # aucun mécanisme APPLICATIF ne ferme plus la
                    # connexion pendant un chunk unique, et elle tombe
                    # quand même. Ceci confirme, plutôt qu'infirme, le
                    # paragraphe ci-dessus : la latence fixe de ~6s/
                    # aller-retour mesurée sur ce même tunnel Cloudflare
                    # gratuit n'était qu'un symptôme d'un comportement
                    # plus large de cette infrastructure (hors de
                    # contrôle de ce code) qui tolère mal une connexion
                    # WebSocket sans échange de PAQUETS DE DONNÉES
                    # significatifs pendant une durée prolongée --
                    # peu importe que des petits messages JSON de
                    # heartbeat continuent, eux, de circuler. Retour
                    # donc à un découpage en chunks de taille fixe
                    # (constante ci-dessous) plutôt qu'un chunk unique,
                    # pour garantir un flux de VRAIS chunks de données
                    # à intervalle régulier tant qu'un fichier volumineux
                    # est en cours de transfert -- indépendamment de ce
                    # qui se passe par ailleurs côté heartbeat/ping.
                    taille_chunk = min(TAILLE_CHUNK_TELECHARGEMENT_OCTETS, len(contenu)) if contenu else 1
                    nb_chunks = max(1, -(-len(contenu) // taille_chunk))  # arrondi au-dessus
                    connexion.telechargement_en_cours = TelechargementFichierEnCours(
                        cle, contenu, taille_chunk,
                    )
                    logger.info(
                        "telecharger_fichier_debut : '%s' (%d octets, %d chunk(s)) id=%s",
                        cle, len(contenu), nb_chunks, id_connexion,
                    )
                    ack_debut = json.dumps({
                        "type": "telechargement_fichier_debut_ack", "ok": True, "cle": cle,
                        "nb_chunks": nb_chunks,
                    })
                    t_avant_send = time.monotonic()
                    await websocket.send_text(ack_debut)
                    t_apres_send = time.monotonic()
                    logger.info(
                        "DIAG_TELECHARGEMENT debut : '%s' id=%s -- "
                        "lecture_B2=%.3fs taille_msg_ack=%d octets envoi_ack=%.3fs total=%.3fs",
                        cle, id_connexion,
                        t_apres_b2 - t_avant_b2,
                        len(ack_debut),
                        t_apres_send - t_avant_send,
                        t_apres_send - t_debut_total,
                    )
                except Exception as e:
                    logger.exception("Échec telecharger_fichier_debut ('%s')", cle)
                    await websocket.send_text(json.dumps({
                        "type": "telechargement_fichier_debut_ack", "ok": False, "cle": cle,
                        "erreur": str(e),
                    }))

            elif type_message == "telecharger_fichier_chunk":
                # Chaque chunk est demandé explicitement par index (cf.
                # Phase 2 de ClientServeurT._telecharger_fichier côté
                # AutoniaX.py) -- le serveur garde le contenu complet en
                # mémoire pour CETTE connexion (cf.
                # TelechargementFichierEnCours) entre telecharger_fichier_
                # debut et telecharger_fichier_fin, pas besoin de relire
                # B2 à chaque chunk.
                #
                # Historique de taille_chunk (cf. telecharger_fichier_
                # debut ci-dessus pour le réglage actuel -- remis à 512
                # Ko le temps du diagnostic DIAG_TELECHARGEMENT) :
                #   1) 512 Ko fixes (ORIGINE) : chaque chunk coûte un
                #      aller-retour websocket complet -- mesuré à ~5-6s
                #      par aller-retour en usage réel (logs : 22 chunks
                #      pour 10.5 Mo -> 2min08 de téléchargement total).
                #      Lent mais FIABLE : chaque chunk finissait par
                #      arriver.
                #   2) Un seul chunk couvrant tout le fichier (nb_chunks
                #      =1, ~14.7 Mo encodé en base64) : ÉCHEC EN
                #      CONDITIONS RÉELLES -- TimeoutError sec après 30s
                #      côté client, ET AUCUNE exception loggée côté
                #      serveur (le "telecharger_fichier_debut : ... (1
                #      chunk(s))" est bien loggé, donc le code a atteint
                #      ce point -- mais aucun log ne permettait de savoir
                #      si l'ack a effectivement été envoyé par
                #      websocket.send_text() ou si CET envoi précis a
                #      lui-même traîné/échoué silencieusement). D'où
                #      l'instrumentation DIAG_TELECHARGEMENT ci-dessus et
                #      ci-dessous : mesurer explicitement le temps de
                #      chaque envoi réseau, pas seulement le temps total.
                #   3) Ne PAS retenter une taille de chunk plus grande
                #      tant que les logs DIAG_TELECHARGEMENT n'ont pas
                #      confirmé où le temps se perd réellement.
                session = connexion.telechargement_en_cours
                cle = message.get("cle")
                index = message.get("index")

                if session is None or session.cle != cle:
                    logger.warning(
                        "telecharger_fichier_chunk refusé : aucun téléchargement en cours pour '%s' id=%s",
                        cle, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "telechargement_fichier_chunk_ack", "ok": False, "cle": cle, "index": index,
                        "erreur": "Aucun téléchargement en cours pour cette clé (telecharger_fichier_debut requis d'abord).",
                    }))
                    continue

                try:
                    t_avant_lecture = time.monotonic()
                    contenu_chunk = session.lire_chunk(index)
                    t_avant_b64 = time.monotonic()
                    contenu_b64 = base64.b64encode(contenu_chunk).decode("ascii")
                    t_avant_dumps = time.monotonic()
                    msg_chunk = json.dumps({
                        "type": "telechargement_fichier_chunk_ack", "ok": True, "cle": cle, "index": index,
                        "contenu_b64": contenu_b64,
                    })
                    t_avant_send_chunk = time.monotonic()
                    await websocket.send_text(msg_chunk)
                    t_apres_send_chunk = time.monotonic()
                    logger.info(
                        "DIAG_TELECHARGEMENT chunk : '%s' index=%d id=%s -- "
                        "taille_chunk_brut=%d octets taille_msg=%d octets "
                        "lecture=%.3fs b64encode=%.3fs json_dumps=%.3fs envoi=%.3fs total=%.3fs",
                        cle, index, id_connexion,
                        len(contenu_chunk), len(msg_chunk),
                        t_avant_b64 - t_avant_lecture,
                        t_avant_dumps - t_avant_b64,
                        t_avant_send_chunk - t_avant_dumps,
                        t_apres_send_chunk - t_avant_send_chunk,
                        t_apres_send_chunk - t_avant_lecture,
                    )
                except IndexError:
                    logger.warning("telecharger_fichier_chunk refusé : index=%r invalide id=%s", index, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "telechargement_fichier_chunk_ack", "ok": False, "cle": cle, "index": index,
                        "erreur": f"Index de chunk invalide ({index!r}).",
                    }))

            elif type_message == "telecharger_fichier_fin":
                # Purement déclaratif côté client (cf. Phase 3 de
                # _telecharger_fichier) -- on en profite pour libérer le
                # contenu gardé en mémoire pour cette connexion, plutôt
                # que d'attendre la déconnexion.
                cle = message.get("cle")
                if connexion.telechargement_en_cours is not None and connexion.telechargement_en_cours.cle == cle:
                    connexion.telechargement_en_cours = None
                logger.info("telecharger_fichier_fin : '%s' id=%s", cle, id_connexion)

            elif type_message == "envoyer_capture":
                # PATCH (mode sAutoniax -- demande explicite utilisateur :
                # "il faut compresser en .webp 80 pourcent avant d'envoyer"
                # puis "la capture envoyée au serveurT, le serveurT envoie
                # directement à mAutoniax sous forme de message de
                # réception"). Réservé au rôle "executant". Relais TEMPS
                # RÉEL uniquement (PAS de passage par B2/GestionnaireStockage
                # -- une capture d'écran de contrôle n'a pas vocation à être
                # persistée, contrairement à un profil ou une mise à jour
                # d'app) vers TOUS les pilotes connectés, même patron que
                # diffuser_liste_executants. Aucun accusé de réception
                # n'est attendu par le client (cf. ClientServeurT.
                # _envoyer_capture, "envoi-et-oublie" comme _envoyer_
                # lister_stockage) -- pas de réponse envoyée à l'exécutant
                # ici.
                #
                # PATCH (recompression par pilote -- demande explicite
                # utilisateur : "les capture doivent arriver désormais sur
                # le serveurT avec le webp 100 pourcent, et maintenant le
                # serveurT pour renvoyer chez nous on va nous même modifier
                # les paramètres") -- image_b64 REÇUE ICI reste toujours
                # celle envoyée par l'exécutant (qualité 100, cf.
                # ClientServeurT._envoyer_capture côté AutoniaX.py, plus de
                # dégradation à la source). Ce qui change : PLUS un seul
                # message_relais identique pour tous les pilotes -- chaque
                # pilote reçoit une version recompressée selon SA PROPRE
                # préférence (cf. Connexion.preference_capture, réglée via
                # le message "definir_preference_capture"). Regroupement
                # par (resolution, qualite) IDENTIQUE avant recompression
                # (cf. _recompresser_pour_diffusion) : un seul appel Pillow
                # coûteux (CPU-bound, cf. sa docstring) par combinaison
                # distincte réellement utilisée, même si N pilotes la
                # partagent -- cas courant (tout le monde au défaut 80/
                # full, par exemple), pas un recompress par pilote un par
                # un.
                if connexion.role != "executant":
                    logger.warning(
                        "envoyer_capture refusé (rôle=%r, seul 'executant' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    continue

                instance_id = message.get("instance_id", "")
                image_b64 = message.get("image_b64", "")
                if not image_b64:
                    logger.warning("envoyer_capture refusé : champ 'image_b64' manquant id=%s", id_connexion)
                    continue

                # PATCH (demande explicite utilisateur : "lorsque on demande
                # une capture [bouton 'Capturer tout' du panneau des
                # profils clone], la qualité doit être automatiquement à
                # 100, jamais celle du FenetreRenduTaskReseau actuel, ça ne
                # doit pas changer sa qualité actuelle") -- champ optionnel
                # posé côté client UNIQUEMENT pour les captures issues de
                # capture_propre déclenchées par "Capturer tout" (cf.
                # ClientServeurT._envoyer_capture/envoyer_capture côté
                # AutoniaX.py, jamais pour le streaming continu normal ni
                # le "Rafraîchir" du panneau de rendu réseau, qui restent
                # inchangés et continuent de dépendre de preference_capture
                # de chaque pilote). Diffusé à qualité 100 pour TOUS les
                # pilotes connectés recevant CETTE capture précise (retour
                # utilisateur explicite -- pas de ciblage par pilote
                # demandeur, cf. message envoyer_capture qui ne transporte
                # aucun id_pilote) -- ne modifie JAMAIS
                # Connexion.preference_capture d'aucun pilote : le
                # streaming affiché à l'écran (et toute future capture non
                # marquée) garde exactement le réglage courant de chacun,
                # cette dérogation ne vaut que pour ce message-ci.
                forcer_qualite_100 = bool(message.get("forcer_qualite_100", False))

                cache_recompression: dict[tuple, str] = {}
                nb_pilotes_ok = 0
                loop = asyncio.get_running_loop()
                for pilote in registre.pilotes():
                    if forcer_qualite_100:
                        preference = {"resolution": RESOLUTION_PAR_DEFAUT, "qualite": 100}
                    else:
                        preference = pilote.preference_capture
                    cle_cache = (preference.get("resolution", RESOLUTION_PAR_DEFAUT), preference.get("qualite", QUALITE_PAR_DEFAUT))
                    image_pour_ce_pilote = cache_recompression.get(cle_cache)
                    if image_pour_ce_pilote is None:
                        # PATCH -- déporté dans un executor (même patron
                        # que ClientServeurT._envoyer_capture côté
                        # AutoniaX.py) : le décodage/réencodage WebP via
                        # Pillow est synchrone et CPU-bound, jamais
                        # exécuté directement dans la boucle asyncio pour
                        # ne pas geler TOUS les websockets du serveur
                        # (autres pilotes/exécutants) pendant ce calcul.
                        #
                        # CORRECTIF ROBUSTESSE (cf. commentaire d'en-tête
                        # du fichier -- crash -11/SIGSEGV sous forte
                        # charge) : executor DÉDIÉ et borné
                        # (_executor_travail_bloquant), plus le pool par
                        # défaut illimité, et passage par le même
                        # sémaphore que les appels Drive
                        # (_semaphore_travail_bloquant) -- Pillow/libwebp
                        # est du code natif exactement comme Drive/ssl,
                        # partage donc la même limite globale de travail
                        # bloquant "en vol" plutôt qu'une limite séparée
                        # qui laisserait la charge totale repartir à la
                        # hausse.
                        async with _semaphore_travail_bloquant:
                            image_pour_ce_pilote = await loop.run_in_executor(
                                _executor_travail_bloquant, _recompresser_pour_diffusion, image_b64, preference
                            )
                        cache_recompression[cle_cache] = image_pour_ce_pilote
                    message_relais = json.dumps({
                        "type": "capture_recue",
                        # PATCH (identité stable par nom) -- connexion.nom
                        # (PAS id_connexion) : c'est ce que le pilote
                        # compare désormais à combo_executant_reseau.
                        # currentData() (cf. AutoniaX.py, sur_capture_
                        # reseau_recue) pour savoir si CETTE capture
                        # concerne le sAutoniax actuellement sélectionné à
                        # l'écran -- avec id_connexion ici, cette
                        # comparaison échouerait TOUJOURS (le combo ne
                        # connaît plus que des noms), et le panneau de
                        # rendu réseau resterait noir en permanence malgré
                        # des captures bel et bien reçues.
                        "id_executant": connexion.nom,
                        "nom_executant": connexion.nom,
                        "instance_id": instance_id,
                        "image_b64": image_pour_ce_pilote,
                    })
                    # CORRECTIF (bug n°3) -- particulièrement important
                    # ici : ce flux de capture tourne en continu, plusieurs
                    # exécutants différents peuvent diffuser vers le même
                    # pilote quasi simultanément.
                    try:
                        _t0 = time.time()
                        async with registre.verrou_pour(pilote.websocket):
                            _t1 = time.time()
                            await pilote.websocket.send_text(message_relais)
                        _t2 = time.time()
                        if _t2 - _t0 > 0.5:
                            logger.warning("[LAG-RELAIS] capture -> pilote '%s' : attente verrou %.2fs + send_text %.2fs (%d octets)",
                                           pilote.nom, _t1 - _t0, _t2 - _t1, len(message_relais))
                        nb_pilotes_ok += 1
                    except Exception:
                        pass
                # DIAGNOSTIC (poids source vs poids réellement envoyé par
                # variante -- le log précédent n'affichait que la taille
                # de la source brute, identique à chaque capture puisque
                # l'exécutant envoie toujours en qualité 100, ce qui
                # rendait impossible de vérifier depuis les logs seuls
                # si la recompression par pilote avait un effet réel).
                detail_variantes = ", ".join(
                    f"{cle}={len(valeur)}o" for cle, valeur in cache_recompression.items()
                )
                # PATCH (demande utilisateur explicite : "je ne veux plus
                # voir ces logs, il ne doivent plus être enregistrés...
                # peut-être que après je vais remettre à true") -- passé
                # en DEBUG (pas supprimé) : une ligne par capture relayée,
                # très bruyant en mode capture continue. Réactivable via
                # le niveau de logging, sans toucher au code.
                logger.info(
                    "envoyer_capture : relayé à %d pilote(s), %d variante(s) recompressée(s) "
                    "(exécutant='%s', instance_id=%r, %d octets b64 source -> [%s])",
                    nb_pilotes_ok, len(cache_recompression), connexion.nom, instance_id, len(image_b64),
                    detail_variantes,
                )

            elif type_message == "definir_preference_capture":
                # PATCH (recompression par pilote, cf. docstring du bloc
                # "envoyer_capture" ci-dessus) -- réservé au rôle "pilote"
                # (seul un pilote a un preference_capture qui compte,
                # cf. Connexion.__init__). Réglé côté UI par
                # PanneauRenduInstance (AutoniaX.py, panneau de rendu
                # réseau) -- appliqué au PROCHAIN "envoyer_capture"
                # relayé, aucun effet rétroactif sur des captures déjà
                # envoyées. Valeurs non reconnues (qualite invalide)
                # retombent silencieusement sur les défauts dans
                # _recompresser_pour_diffusion -- pas de rejet du message
                # ici, un mauvais réglage ne doit jamais couper le flux
                # de captures pour ce pilote.
                #
                # CHANGEMENT (demande explicite utilisateur : "sa ne doit
                # plus redimensionner ... je veux le parametre de
                # compression : 100, 50, 10") -- "resolution" n'est plus
                # validée dynamiquement (ancien RESOLUTIONS_HAUTEUR_PX
                # supprimé) : elle est ignorée par _recompresser_pour_
                # diffusion, toujours forcée à "full" ici pour rester
                # cohérente avec le protocole existant côté AutoniaX.py
                # sans jamais redéclencher de redimensionnement. Seule
                # "qualite" (5/10/50/100) a un effet réel désormais.
                if connexion.role != "pilote":
                    logger.warning(
                        "definir_preference_capture refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    continue
                qualite = message.get("qualite", QUALITE_PAR_DEFAUT)
                if qualite not in QUALITES_AUTORISEES:
                    qualite = QUALITE_PAR_DEFAUT
                connexion.preference_capture = {"resolution": "full", "qualite": qualite}
                logger.info(
                    "definir_preference_capture : pilote='%s' -> qualite=%r id=%s",
                    connexion.nom, qualite, id_connexion,
                )

            elif type_message == "kill_projet":
                # PATCH (Patch 4.2/4.9 -- action "Kill" par ligne de
                # l'onglet Instances, retour utilisateur explicite : "un
                # bouton kill qui envoie l'ordre d'arret du projet en
                # cours a ce sAutoniax precis"). Réservé au rôle "pilote".
                # Simple relais CIBLÉ (pas de diffusion à tous les
                # exécutants, contrairement à envoyer_capture qui diffuse
                # à tous les PILOTES) -- le serveur ne connaît pas le
                # détail de "comment" un sAutoniax arrête un projet en
                # cours (cf. principe "aucune logique métier AutoniaX"),
                # il transmet juste l'ordre à la connexion visée. Accusé
                # de réception immédiat au pilote (kill_projet_ack) :
                # confirme seulement que l'ordre a été TRANSMIS au
                # sAutoniax visé, pas qu'il a effectivement arrêté quoi
                # que ce soit -- cf. statut_executant, qui redescendra
                # séparément à "inactif" une fois l'arrêt réellement
                # effectif côté sAutoniax.
                if connexion.role != "pilote":
                    logger.warning(
                        "kill_projet refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "kill_projet_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander un kill_projet.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("kill_projet refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "kill_projet_ack", "ok": False, "id_executant": id_executant,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({"type": "kill_projet"}))
                    logger.info("kill_projet : transmis à '%s' (id=%s) par pilote id=%s", cible.nom, id_executant, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "kill_projet_ack", "ok": True, "id_executant": id_executant,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission kill_projet à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "kill_projet_ack", "ok": False, "id_executant": id_executant,
                        "erreur": str(e),
                    }))

            elif type_message == "redemarrer_executant":
                # PATCH -- action "Redémarrer" du menu contextuel de
                # l'onglet Instances : retélécharge AutoniaX.py depuis le
                # serveurT et relance le sAutoniax ciblé, sans redémarrer
                # le kernel Kaggle (cf. CODE_SORTIE_REDEMARRAGE côté
                # AutoniaX.py). Réservé au rôle "pilote". Même patron
                # EXACT que kill_projet juste au-dessus : simple relais
                # CIBLÉ (le serveur ne connaît pas le détail de "comment"
                # un sAutoniax redémarre, cf. principe "aucune logique
                # métier AutoniaX"), avec accusé de réception immédiat
                # (redemarrer_executant_ack) qui confirme seulement que
                # l'ordre a été TRANSMIS, pas que le redémarrage a
                # effectivement eu lieu.
                if connexion.role != "pilote":
                    logger.warning(
                        "redemarrer_executant refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "redemarrer_executant_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander un redemarrer_executant.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("redemarrer_executant refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "redemarrer_executant_ack", "ok": False, "id_executant": id_executant,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({"type": "redemarrer_executant"}))
                    logger.info("redemarrer_executant : transmis à '%s' (id=%s) par pilote id=%s", cible.nom, id_executant, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "redemarrer_executant_ack", "ok": True, "id_executant": id_executant,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission redemarrer_executant à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "redemarrer_executant_ack", "ok": False, "id_executant": id_executant,
                        "erreur": str(e),
                    }))

            elif type_message == "kill_profil":
                # PATCH (arrêt/redémarrage PAR PROFIL -- demande explicite
                # utilisateur : "je veux que on puisse arreter aussi un
                # profils en execution, que on puisse redemarer un
                # profils", granularité RÉELLE distincte de kill_projet/
                # redemarrer_executant ci-dessus, qui agissent sur TOUT le
                # projet en cours). Réservé au rôle "pilote". Même patron
                # EXACT que kill_projet (simple relais CIBLÉ, le serveur
                # ne connaît pas le détail de "comment" un sAutoniax
                # interrompt un profil précis -- cf. principe "aucune
                # logique métier AutoniaX") -- "nom_profil" et
                # "redemarrer" transmis tels quels, kill_profil_ack
                # confirme seulement la TRANSMISSION, pas l'arrêt effectif
                # (cf. kill_profil_resultat_reel plus bas pour ça, envoyé
                # séparément par le sAutoniax une fois l'action réellement
                # effectuée).
                if connexion.role != "pilote":
                    logger.warning(
                        "kill_profil refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "kill_profil_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander un kill_profil.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_profil = message.get("nom_profil", "")
                redemarrer = bool(message.get("redemarrer", False))
                if not nom_profil:
                    await websocket.send_text(json.dumps({
                        "type": "kill_profil_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "redemarrer": redemarrer,
                        "erreur": "Champ 'nom_profil' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("kill_profil refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "kill_profil_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "redemarrer": redemarrer,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "kill_profil", "nom_profil": nom_profil, "redemarrer": redemarrer,
                        }))
                    logger.info(
                        "kill_profil : transmis à '%s' (id=%s, profil=%r, redemarrer=%s) par pilote id=%s",
                        cible.nom, id_executant, nom_profil, redemarrer, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "kill_profil_ack", "ok": True, "id_executant": id_executant,
                        "nom_profil": nom_profil, "redemarrer": redemarrer,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission kill_profil à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "kill_profil_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "redemarrer": redemarrer, "erreur": str(e),
                    }))

            elif type_message == "kill_profil_resultat_reel":
                # PATCH (cf. kill_profil ci-dessus) -- symétrique de
                # statut_executant : le sAutoniax signale ici le résultat
                # RÉEL de l'action (pas juste la transmission, déjà
                # confirmée par kill_profil_ack au moment du relais),
                # DIFFUSÉ À TOUS LES PILOTES connectés (même raisonnement
                # que statut_executant -- le sAutoniax ne sait pas quel
                # pilote précis a demandé l'action, le message kill_profil
                # qu'il a reçu ne portait pas d'id_pilote). Réservé au
                # rôle "executant". Best-effort par pilote (un pilote
                # injoignable ne bloque jamais les autres).
                if connexion.role != "executant":
                    logger.warning(
                        "kill_profil_resultat_reel refusé (rôle=%r) id=%s", connexion.role, id_connexion,
                    )
                    continue
                message_diffuse = dict(message)
                message_diffuse["id_executant"] = connexion.nom
                logger.info(
                    "kill_profil_resultat_reel : '%s' -- profil=%r redemarrer=%s ok=%s -- diffusé à %d pilote(s)",
                    connexion.nom, message.get("nom_profil", ""), message.get("redemarrer", False),
                    message.get("ok", False), len(registre.pilotes()),
                )
                # CORRECTIF (bug n°3) -- cf. commentaire toggle_proxy_natif_resultat plus haut.
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps(message_diffuse))
                    except Exception:
                        logger.exception("Échec relais kill_profil_resultat_reel vers pilote '%s'", pilote.nom)

            elif type_message == "arreter_execution_profil":
                # PATCH (Section 8 -- “Arrêter” interrompt le CODE, pas le
                # profil) -- distinct de kill_profil ci-dessus : n'a
                # vocation qu'à terminer le process d'exécution de
                # code du profil isolé visé (l'exécuteur, cf. AutoniaX.py
                # § nouveau registre _executeurs_isoles) -- le navigateur
                # (_procs_isoles) de ce profil n'est PAS touché, contrairement
                # à kill_profil qui détruit tout le profil. Même patron EXACT
                # que kill_profil (simple relais CIBLÉ, le serveur ne connaît
                # pas le détail de "comment" un sAutoniax interrompt un
                # exécuteur précis -- cf. principe "aucune logique métier
                # AutoniaX") -- pas de champ "redemarrer" ici (contrairement
                # à kill_profil) : arrêter le code ne redémarre jamais le
                # profil, une cellule suivante sur ce même profil relance
                # simplement un exécuteur neuf à la demande (cf. plan §4).
                # arreter_execution_profil_ack confirme seulement la
                # TRANSMISSION, pas l'arrêt effectif (cf. arreter_execution_
                # profil_resultat_reel plus bas pour ça, envoyé séparément
                # par le sAutoniax une fois l'action réellement effectuée).
                if connexion.role != "pilote":
                    logger.warning(
                        "arreter_execution_profil refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "arreter_execution_profil_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander un arreter_execution_profil.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_profil = message.get("nom_profil", "")
                if not nom_profil:
                    await websocket.send_text(json.dumps({
                        "type": "arreter_execution_profil_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil,
                        "erreur": "Champ 'nom_profil' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("arreter_execution_profil refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "arreter_execution_profil_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "arreter_execution_profil", "nom_profil": nom_profil,
                        }))
                    logger.info(
                        "arreter_execution_profil : transmis à '%s' (id=%s, profil=%r) par pilote id=%s",
                        cible.nom, id_executant, nom_profil, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "arreter_execution_profil_ack", "ok": True, "id_executant": id_executant,
                        "nom_profil": nom_profil,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission arreter_execution_profil à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "arreter_execution_profil_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": str(e),
                    }))

            elif type_message == "arreter_execution_profil_resultat_reel":
                # PATCH (cf. arreter_execution_profil ci-dessus) -- symétrique
                # de kill_profil_resultat_reel : le sAutoniax signale ici le
                # résultat RÉEL de l'arrêt de l'exécuteur (pas juste la
                # transmission, déjà confirmée par arreter_execution_profil_ack
                # au moment du relais), DIFFUSÉ À TOUS LES PILOTES connectés
                # (même raisonnement que kill_profil_resultat_reel -- le
                # sAutoniax ne sait pas quel pilote précis a demandé l'action,
                # le message arreter_execution_profil qu'il a reçu ne portait
                # pas d'id_pilote). Réservé au rôle "executant". Best-effort
                # par pilote (un pilote injoignable ne bloque jamais les
                # autres).
                if connexion.role != "executant":
                    logger.warning(
                        "arreter_execution_profil_resultat_reel refusé (rôle=%r) id=%s", connexion.role, id_connexion,
                    )
                    continue
                message_diffuse = dict(message)
                message_diffuse["id_executant"] = connexion.nom
                logger.info(
                    "arreter_execution_profil_resultat_reel : '%s' -- profil=%r ok=%s -- diffusé à %d pilote(s)",
                    connexion.nom, message.get("nom_profil", ""),
                    message.get("ok", False), len(registre.pilotes()),
                )
                # CORRECTIF (bug n°3) -- cf. commentaire toggle_proxy_natif_resultat plus haut.
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps(message_diffuse))
                    except Exception:
                        logger.exception("Échec relais arreter_execution_profil_resultat_reel vers pilote '%s'", pilote.nom)

            elif type_message == "demander_profils_sautoniax":
                # PATCH (onglet Instances, panneau de propriétés -- demande
                # explicite utilisateur : "longlet intance, pour un
                # sautoniax doit afficher tout les profils dabord, actifs
                # et pas actifs" + "il faut mettre un bouton de mise a
                # jour explicite" -- PAS de signalement automatique à la
                # connexion, uniquement à la demande explicite du pilote).
                # Réservé au rôle "pilote". Même patron EXACT que kill_
                # profil/demander_upload_profil_vers_cloud (relais CIBLÉ
                # pur, le serveur ne sait pas lire le disque du sAutoniax,
                # cf. principe "aucune logique métier AutoniaX") --
                # l'exécutant visé, une fois ce message reçu, scanne son
                # propre dossier de profils locaux et croise avec ses
                # profils actuellement actifs (cf. AutoniaX.py, handler
                # _sur_demander_profils_sautoniax côté main_sautoniax),
                # puis répond via "profils_sautoniax_resultat" (RELAIS
                # DIRECT au pilote demandeur, PAS une diffusion -- cf. ce
                # handler plus bas, contrairement à kill_profil_resultat_
                # reel/statut_executant qui eux sont diffusés à tous les
                # pilotes : cette liste n'intéresse QUE celui qui l'a
                # demandée, pas de raison de la pousser à tous).
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_profils_sautoniax refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_profils_sautoniax_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander la liste des profils d'un sAutoniax.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_profils_sautoniax refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_profils_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_profils_sautoniax", "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_profils_sautoniax : transmis à '%s' (id=%s) par pilote id=%s",
                        cible.nom, id_executant, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_profils_sautoniax_ack", "ok": True, "id_executant": id_executant,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_profils_sautoniax à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_profils_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "erreur": str(e),
                    }))

            elif type_message == "profils_sautoniax_resultat":
                # PATCH (cf. demander_profils_sautoniax ci-dessus) --
                # RELAIS DIRECT au pilote demandeur (id_pilote transmis
                # tel quel par le sAutoniax, reçu dans le message
                # demander_profils_sautoniax qu'il a lui-même reçu -- même
                # mécanisme EXACT que id_pilote dans envoyer_profil_fin
                # pour l'upload distant). Réservé au rôle "executant".
                # Best-effort : un pilote déconnecté entre-temps ne fait
                # jamais planter l'exécutant qui vient de répondre.
                if connexion.role != "executant":
                    logger.warning("profils_sautoniax_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                id_pilote_cible = message.get("id_pilote", "")
                # CORRECTIF (bug confirmé, cf. docstring Registre.pilote_par_id
                # et Connexion.id_pilote_stable) : id_pilote_cible est un
                # id_pilote_stable ("pilote-xxxx"), PAS un id_connexion --
                # registre.connexions.get() cherchait dans le mauvais espace
                # de clés et échouait TOUJOURS, même pilote parfaitement
                # connecté. pilote_par_id() résout par id_pilote_stable
                # (avec repli id_connexion pour compat ascendante).
                pilote_cible = registre.pilote_par_id(id_pilote_cible)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning(
                        "profils_sautoniax_resultat : pilote '%s' introuvable/déconnecté, message perdu (id=%s)",
                        id_pilote_cible, id_connexion,
                    )
                else:
                    try:
                        message_relais = dict(message)
                        message_relais["id_executant"] = connexion.nom
                        async with registre.verrou_pour(pilote_cible.websocket):
                            await pilote_cible.websocket.send_text(json.dumps(message_relais))
                        logger.info(
                            "profils_sautoniax_resultat : '%s' -- %d profil(s) -- relayé au pilote '%s'",
                            connexion.nom, len(message.get("profils", [])), id_pilote_cible,
                        )
                    except Exception:
                        logger.exception("Échec relais profils_sautoniax_resultat vers pilote '%s'", id_pilote_cible)

            elif type_message in TYPES_KAGGLE_PILOTE_VERS_EXECUTANT:
                # PATCH (Profils Kaggle, phase 3) -- ordres du sous-onglet "Profils
                # Kaggle" : kaggle_lister_profils, kaggle_envoyer_profils,
                # kaggle_telecharger_profils. Meme patron EXACT que
                # demander_profils_sautoniax : relais CIBLE pur, reserve au pilote.
                # Le serveur ne transporte QUE les ordres et la progression : les
                # archives vont directement sAutoniax <-> Kaggle (jamais par ici).
                # Chaque ordre porte un id_operation, relaye tel quel.
                ack = type_message + "_ack"
                if connexion.role != "pilote":
                    logger.warning("%s refuse (role=%r, seul 'pilote' est autorise) id=%s", type_message, connexion.role, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": ack, "ok": False, "id_operation": message.get("id_operation", ""),
                        "erreur": "Seul le pilote peut envoyer un ordre Kaggle.",
                    }))
                    continue
                id_executant = message.get("id_executant", "")
                id_operation = message.get("id_operation", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("%s refuse : executant '%s' introuvable/deconnecte", type_message, id_executant)
                    await websocket.send_text(json.dumps({
                        "type": ack, "ok": False, "id_executant": id_executant, "id_operation": id_operation,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue
                try:
                    message_relais = dict(message)
                    message_relais["id_pilote"] = (connexion.id_pilote_stable or id_connexion)
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps(message_relais))
                    logger.info("%s : transmis a '%s' (op=%s) par pilote id=%s", type_message, cible.nom, id_operation, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": ack, "ok": True, "id_executant": id_executant, "id_operation": id_operation,
                    }))
                except Exception as e:
                    logger.exception("Echec transmission %s a '%s'", type_message, id_executant)
                    await websocket.send_text(json.dumps({
                        "type": ack, "ok": False, "id_executant": id_executant, "id_operation": id_operation,
                        "erreur": str(e),
                    }))

            elif type_message in TYPES_KAGGLE_EXECUTANT_VERS_PILOTE:
                # PATCH (Profils Kaggle, phase 3) -- reponses de l'executant :
                # kaggle_lister_profils_resultat, kaggle_progression, kaggle_resultat.
                # Meme patron EXACT que profils_sautoniax_resultat : relais DIRECT au
                # pilote demandeur (id_pilote), best-effort, jamais de plantage.
                if connexion.role != "executant":
                    logger.warning("%s refuse (role=%r) id=%s", type_message, connexion.role, id_connexion)
                    continue
                id_pilote_cible = message.get("id_pilote", "")
                pilote_cible = registre.pilote_par_id(id_pilote_cible)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning("%s : pilote '%s' introuvable/deconnecte, message perdu (id=%s)", type_message, id_pilote_cible, id_connexion)
                else:
                    try:
                        message_relais = dict(message)
                        message_relais["id_executant"] = connexion.nom
                        async with registre.verrou_pour(pilote_cible.websocket):
                            await pilote_cible.websocket.send_text(json.dumps(message_relais))
                    except Exception:
                        logger.exception("Echec relais %s vers pilote '%s'", type_message, id_pilote_cible)

            elif type_message == "demander_horloge_mautoniax":
                # PATCH (cf. AutoniaX.py, section historique juste avant
                # RelaisProxyLocal.obtenir_horloge_mautoniax -- "pourquoi
                # mautoniax ne donne pas lui meme la date directement",
                # migration depuis /ws_tunnel vers /ws JSON standard).
                # Sens INVERSE de demander_profils_sautoniax/demander_
                # toggle_proxy_natif ci-dessus : c'est ici l'EXÉCUTANT qui
                # initie la demande, ciblant le PILOTE dont il connaît déjà
                # l'id_pilote_stable (posé lors du toggle proxy natif, cf.
                # RelaisProxyLocal.dernier_id_pilote_connu). Réservé au
                # rôle "executant" -- relais CIBLÉ pur, résolu par id_
                # pilote_stable (PAS id_connexion, même raisonnement EXACT
                # que profils_sautoniax_resultat/pilote_par_id ci-dessus) :
                # le serveur ne calcule aucune heure lui-même, seul le
                # mAutoniax visé répond via horloge_mautoniax_resultat
                # plus bas (RELAIS DIRECT au SEUL exécutant demandeur, pas
                # une diffusion -- cette heure n'intéresse que lui).
                if connexion.role != "executant":
                    logger.warning(
                        "demander_horloge_mautoniax refusé (rôle=%r, seul 'executant' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    continue
                id_pilote_cible = message.get("id_pilote", "")
                pilote_cible = registre.pilote_par_id(id_pilote_cible)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning(
                        "demander_horloge_mautoniax : pilote '%s' introuvable/déconnecté, demande perdue (id=%s)",
                        id_pilote_cible, id_connexion,
                    )
                    continue
                try:
                    async with registre.verrou_pour(pilote_cible.websocket):
                        await pilote_cible.websocket.send_text(json.dumps({
                            "type": "demander_horloge_mautoniax", "id_executant": connexion.nom,
                        }))
                    logger.info(
                        "demander_horloge_mautoniax : transmis au pilote '%s' par '%s' (id=%s)",
                        id_pilote_cible, connexion.nom, id_connexion,
                    )
                except Exception:
                    logger.exception("Échec transmission demander_horloge_mautoniax vers pilote '%s'", id_pilote_cible)

            elif type_message == "horloge_mautoniax_resultat":
                # PATCH (cf. demander_horloge_mautoniax ci-dessus) --
                # réponse RÉELLE du pilote (iso_local, nom_fuseau), RELAIS
                # DIRECT au SEUL exécutant demandeur (id_executant transmis
                # tel quel par le serveur dans demander_horloge_mautoniax
                # qu'il a lui-même reçu -- même mécanisme EXACT que
                # id_pilote pour profils_sautoniax_resultat, sens
                # inversé). Réservé au rôle "pilote". Best-effort : un
                # exécutant déconnecté entre-temps ne fait jamais planter
                # le pilote qui vient de répondre.
                if connexion.role != "pilote":
                    logger.warning("horloge_mautoniax_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                id_executant_cible = message.get("id_executant", "")
                executant_cible = registre.executant_par_id(id_executant_cible)
                if executant_cible is None:
                    logger.warning(
                        "horloge_mautoniax_resultat : exécutant '%s' introuvable/déconnecté, message perdu (id=%s)",
                        id_executant_cible, id_connexion,
                    )
                    continue
                try:
                    async with registre.verrou_pour(executant_cible.websocket):
                        await executant_cible.websocket.send_text(json.dumps(message))
                    logger.info(
                        "horloge_mautoniax_resultat : relayé au seul exécutant '%s' (id=%s)",
                        id_executant_cible, id_connexion,
                    )
                except Exception:
                    logger.exception("Échec relais horloge_mautoniax_resultat vers exécutant '%s'", id_executant_cible)

            elif type_message == "demander_demarrer_profil_isole":
                # PATCH (onglet Instances, panneau de propriétés -- bouton
                # "Démarrer" sur un profil INACTIF -- demande explicite
                # utilisateur : "on peu tres bien demarer sans projetbatch").
                # Réservé au rôle "pilote". Même patron EXACT que kill_
                # profil/demander_profils_sautoniax ci-dessus (relais CIBLÉ
                # pur) -- le sAutoniax visé lance lui-même Camoufox pour ce
                # profil seul (cf. AutoniaX.py, handler _sur_demarrer_
                # profil_isole_demande côté main_sautoniax, réutilise le
                # même mécanisme que le Notebook Distant : téléchargement
                # si absent + camoufox_demarrer_navigateur + signalement
                # profils_demarres). "instance_id" n'est PAS transmis ici
                # (contrairement à kill_profil) -- c'est le sAutoniax
                # lui-même qui le génère au lancement et le fait connaître
                # au pilote séparément via son propre message de résultat
                # (cf. demarrer_profil_isole_resultat plus bas), pour
                # rester cohérent avec instances_projet déjà existant.
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_demarrer_profil_isole refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_demarrer_profil_isole_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander le démarrage d'un profil isolé.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_profil = message.get("nom_profil", "")
                if not nom_profil:
                    await websocket.send_text(json.dumps({
                        "type": "demander_demarrer_profil_isole_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": "Champ 'nom_profil' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_demarrer_profil_isole refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_demarrer_profil_isole_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_demarrer_profil_isole", "nom_profil": nom_profil, "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_demarrer_profil_isole : transmis à '%s' (id=%s, profil=%r) par pilote id=%s",
                        cible.nom, id_executant, nom_profil, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_demarrer_profil_isole_ack", "ok": True,
                        "id_executant": id_executant, "nom_profil": nom_profil,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_demarrer_profil_isole à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_demarrer_profil_isole_ack", "ok": False,
                        "id_executant": id_executant, "nom_profil": nom_profil, "erreur": str(e),
                    }))

            elif type_message == "demarrer_profil_isole_resultat":
                # PATCH (cf. demander_demarrer_profil_isole ci-dessus) --
                # symétrique de kill_profil_resultat_reel : résultat RÉEL
                # du démarrage (pas juste la transmission, déjà confirmée
                # par demander_demarrer_profil_isole_ack), DIFFUSÉ à tous
                # les pilotes connectés (même raisonnement -- ce profil,
                # une fois actif, doit apparaître à jour dans le panneau
                # de N'IMPORTE QUEL pilote qui aurait la liste ouverte
                # pour ce sAutoniax, pas seulement celui qui a cliqué
                # "Démarrer"). Réservé au rôle "executant".
                if connexion.role != "executant":
                    logger.warning("demarrer_profil_isole_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                message_diffuse = dict(message)
                message_diffuse["id_executant"] = connexion.nom
                logger.info(
                    "demarrer_profil_isole_resultat : '%s' -- profil=%r ok=%s -- diffusé à %d pilote(s)",
                    connexion.nom, message.get("nom_profil", ""), message.get("ok", False), len(registre.pilotes()),
                )
                # CORRECTIF (bug n°3) -- cf. commentaire toggle_proxy_natif_resultat plus haut.
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps(message_diffuse))
                    except Exception:
                        logger.exception("Échec relais demarrer_profil_isole_resultat vers pilote '%s'", pilote.nom)

            elif type_message == "demander_tester_proxy_sautoniax":
                # PATCH (bouton "+" du panneau de propriétés -- dialogue
                # de création de profil, bouton "Tester le proxy" --
                # décision explicite utilisateur : "test EN LOCAL par le
                # sAutoniax distant lui-même"). Réservé au rôle "pilote".
                # Même patron EXACT que demander_demarrer_profil_isole
                # ci-dessus (relais CIBLÉ pur) : le sAutoniax visé teste
                # lui-même le proxy (cf. AutoniaX.py, handler _sur_
                # tester_proxy_sautoniax_demande côté main_sautoniax,
                # réutilise _tester_proxy_sync, la même fonction que
                # TestProxyWorker côté pilote) et répond via tester_
                # proxy_sautoniax_resultat plus bas (relais direct, PAS
                # une diffusion -- un test de proxy ne concerne que le
                # pilote qui l'a demandé).
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_tester_proxy_sautoniax refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_tester_proxy_sautoniax_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander un test de proxy.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                proxy_texte = message.get("proxy_texte", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_tester_proxy_sautoniax refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_tester_proxy_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_tester_proxy_sautoniax", "proxy_texte": proxy_texte, "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_tester_proxy_sautoniax : transmis à '%s' (id=%s) par pilote id=%s",
                        cible.nom, id_executant, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_tester_proxy_sautoniax_ack", "ok": True, "id_executant": id_executant,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_tester_proxy_sautoniax à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_tester_proxy_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "erreur": str(e),
                    }))

            elif type_message == "tester_proxy_sautoniax_resultat":
                # PATCH (cf. demander_tester_proxy_sautoniax ci-dessus) --
                # RELAIS DIRECT au pilote demandeur (même patron EXACT que
                # telecharger_profil_vers_sautoniax_resultat : id_pilote
                # transmis tel quel, ne concerne QUE celui qui a demandé
                # ce test précis, pas une diffusion à tous). Réservé au
                # rôle "executant".
                if connexion.role != "executant":
                    logger.warning("tester_proxy_sautoniax_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                id_pilote_cible = message.get("id_pilote", "")
                # CORRECTIF (cf. profils_sautoniax_resultat plus haut, même
                # bug EXACT) : résolution par id_pilote_stable, pas par
                # id_connexion.
                pilote_cible = registre.pilote_par_id(id_pilote_cible)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning(
                        "tester_proxy_sautoniax_resultat : pilote '%s' introuvable/déconnecté, message perdu (id=%s)",
                        id_pilote_cible, id_connexion,
                    )
                else:
                    try:
                        message_relais = dict(message)
                        message_relais["id_executant"] = connexion.nom
                        async with registre.verrou_pour(pilote_cible.websocket):
                            await pilote_cible.websocket.send_text(json.dumps(message_relais))
                        logger.info(
                            "tester_proxy_sautoniax_resultat : '%s' -- succes=%s -- relayé au pilote '%s'",
                            connexion.nom, message.get("succes", False), id_pilote_cible,
                        )
                    except Exception:
                        logger.exception("Échec relais tester_proxy_sautoniax_resultat vers pilote '%s'", id_pilote_cible)

            elif type_message == "demander_creer_profil_sautoniax":
                # PATCH (bouton "+" du panneau de propriétés de l'onglet
                # "Instances sAutoniax" -- demande explicite utilisateur :
                # "je veux que desormais on puisse creer un profils").
                # Réservé au rôle "pilote". Même patron EXACT que
                # demander_demarrer_profil_isole ci-dessus (relais CIBLÉ
                # pur) : le sAutoniax visé crée lui-même le dossier de
                # profil (cf. AutoniaX.py, handler _sur_creer_profil_
                # sautoniax_demande côté main_sautoniax) et répond via
                # creer_profil_sautoniax_resultat plus bas (DIFFUSÉ à
                # tous les pilotes -- même raisonnement que demarrer_
                # profil_isole_resultat : ce nouveau profil doit
                # apparaître à jour dans le panneau de n'importe quel
                # pilote ayant ce sAutoniax sélectionné).
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_creer_profil_sautoniax refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_creer_profil_sautoniax_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander la création d'un profil.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_profil = message.get("nom_profil", "")
                type_instance = message.get("type_instance", "")
                proxy_texte = message.get("proxy_texte", "")
                # AJOUT (spec A.4 -- JSON de contraintes de résolution
                # d'écran) -- simple relais transparent, comme le reste
                # des champs de ce handler : le serveur ne valide ni
                # n'interprète ce dict, seul le sAutoniax cible (via
                # enregistrer_config_profil) et le pilote (au moment du
                # clic "Coller") le font.
                contraintes = message.get("contraintes") or {}
                if not nom_profil:
                    await websocket.send_text(json.dumps({
                        "type": "demander_creer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": "Champ 'nom_profil' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_creer_profil_sautoniax refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_creer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_creer_profil_sautoniax", "nom_profil": nom_profil,
                            "type_instance": type_instance, "proxy_texte": proxy_texte, "id_pilote": (connexion.id_pilote_stable or id_connexion),
                            "contraintes": contraintes,
                        }))
                    logger.info(
                        "demander_creer_profil_sautoniax : transmis à '%s' (id=%s, profil=%r, type=%r) par pilote id=%s",
                        cible.nom, id_executant, nom_profil, type_instance, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_creer_profil_sautoniax_ack", "ok": True,
                        "id_executant": id_executant, "nom_profil": nom_profil,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_creer_profil_sautoniax à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_creer_profil_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "nom_profil": nom_profil, "erreur": str(e),
                    }))

            elif type_message == "creer_profil_sautoniax_resultat":
                # PATCH (cf. demander_creer_profil_sautoniax ci-dessus) --
                # symétrique de demarrer_profil_isole_resultat : résultat
                # RÉEL de la création (nom déjà pris = échec), DIFFUSÉ à
                # tous les pilotes connectés. Réservé au rôle "executant".
                if connexion.role != "executant":
                    logger.warning("creer_profil_sautoniax_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                message_diffuse = dict(message)
                message_diffuse["id_executant"] = connexion.nom
                logger.info(
                    "creer_profil_sautoniax_resultat : '%s' -- profil=%r ok=%s -- diffusé à %d pilote(s)",
                    connexion.nom, message.get("nom_profil", ""), message.get("ok", False), len(registre.pilotes()),
                )
                # CORRECTIF (bug n°3) -- cf. commentaire toggle_proxy_natif_resultat plus haut.
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps(message_diffuse))
                    except Exception:
                        logger.exception("Échec relais creer_profil_sautoniax_resultat vers pilote '%s'", pilote.nom)

            elif type_message == "sautoniax_pret":
                # AJOUT (spec A.3, signal "sAutoniax prêt") -- même patron
                # EXACT que creer_profil_sautoniax_resultat ci-dessus :
                # DIFFUSÉ à tous les pilotes connectés, réservé au rôle
                # "executant", id_executant repris de connexion.nom (pas
                # du champ envoyé par le client, plus robuste) -- émis par
                # AutoniaX.py (ClientServeurT.envoyer_sautoniax_pret) une
                # seule fois, juste après que CET exécutant a terminé sa
                # propre connexion/enregistrement au serveurT.
                #
                # CORRECTIF (ligne grisée indéfiniment après reconnexion
                # d'un pilote/redémarrage serveurT) -- persisté sur la
                # connexion elle-même (cf. Connexion.sautoniax_pret) EN
                # PLUS de la diffusion live ci-dessous : un pilote qui se
                # connecte plus tard lira ce champ directement dans
                # instances_list au lieu de dépendre uniquement de ce
                # signal ponctuel, qu'il aurait raté s'il n'était pas
                # encore connecté au moment de son émission.
                if connexion.role != "executant":
                    logger.warning("sautoniax_pret refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                connexion.sautoniax_pret = True
                message_diffuse = {"type": "sautoniax_pret", "id_executant": connexion.nom}
                logger.info(
                    "sautoniax_pret : '%s' -- diffusé à %d pilote(s)",
                    connexion.nom, len(registre.pilotes()),
                )
                # CORRECTIF (bug n°3) -- cf. commentaire toggle_proxy_natif_resultat plus haut.
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps(message_diffuse))
                    except Exception:
                        logger.exception("Échec relais sautoniax_pret vers pilote '%s'", pilote.nom)

            elif type_message == "demander_supprimer_profil_sautoniax":
                # PATCH (bouton "Supprimer tous les profils" du panneau de
                # propriétés de l'onglet "Instances sAutoniax" -- demande
                # explicite utilisateur : "je veux que tu ajoute un
                # bouton pour suprimer tout les profils"). Réservé au
                # rôle "pilote". Même patron EXACT que demander_creer_
                # profil_sautoniax ci-dessus (relais CIBLÉ pur) : le
                # sAutoniax visé supprime lui-même le dossier de profil
                # (cf. AutoniaX.py, handler _sur_supprimer_profil_demande
                # côté main_sautoniax, refuse si le profil est actif) et
                # répond via supprimer_profil_sautoniax_resultat plus bas
                # (DIFFUSÉ à tous les pilotes -- ce profil doit disparaître
                # du panneau de n'importe quel pilote ayant ce sAutoniax
                # sélectionné).
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_supprimer_profil_sautoniax refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_supprimer_profil_sautoniax_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander la suppression d'un profil.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_profil = message.get("nom_profil", "")
                if not nom_profil:
                    await websocket.send_text(json.dumps({
                        "type": "demander_supprimer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": "Champ 'nom_profil' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_supprimer_profil_sautoniax refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_supprimer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_supprimer_profil_sautoniax", "nom_profil": nom_profil,
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_supprimer_profil_sautoniax : transmis à '%s' (id=%s, profil=%r) par pilote id=%s",
                        cible.nom, id_executant, nom_profil, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_supprimer_profil_sautoniax_ack", "ok": True,
                        "id_executant": id_executant, "nom_profil": nom_profil,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_supprimer_profil_sautoniax à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_supprimer_profil_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "nom_profil": nom_profil, "erreur": str(e),
                    }))

            elif type_message == "supprimer_profil_sautoniax_resultat":
                # PATCH (cf. demander_supprimer_profil_sautoniax ci-dessus)
                # -- symétrique de creer_profil_sautoniax_resultat :
                # résultat RÉEL de la suppression (profil actif = échec),
                # DIFFUSÉ à tous les pilotes connectés. Réservé au rôle
                # "executant".
                if connexion.role != "executant":
                    logger.warning("supprimer_profil_sautoniax_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                message_diffuse = dict(message)
                message_diffuse["id_executant"] = connexion.nom
                logger.info(
                    "supprimer_profil_sautoniax_resultat : '%s' -- profil=%r ok=%s -- diffusé à %d pilote(s)",
                    connexion.nom, message.get("nom_profil", ""), message.get("ok", False), len(registre.pilotes()),
                )
                # CORRECTIF (bug n°3) -- cf. commentaire toggle_proxy_natif_resultat plus haut.
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps(message_diffuse))
                    except Exception:
                        logger.exception("Échec relais supprimer_profil_sautoniax_resultat vers pilote '%s'", pilote.nom)

            # AJOUT (régénérer le navigateur d'un profil) -- blocs calqués sur demander_supprimer_profil_sautoniax / supprimer_profil_sautoniax_resultat.
            elif type_message == "demander_regenerer_profil_sautoniax":
                # AJOUT (régénérer le navigateur d'un profil) -- réservé au rôle
                # "pilote". Relais CIBLÉ pur, même patron que demander_supprimer_
                # profil_sautoniax ci-dessus : le sAutoniax visé remplace lui-même
                # l'empreinte (et par défaut les données) du profil, GARDE son
                # proxy, relance (cf. AutoniaX.py, _sur_regenerer_profil_demande,
                # côté main_sautoniax) et répond via regenerer_profil_sautoniax_
                # resultat plus bas (DIFFUSÉ à tous les pilotes).
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_regenerer_profil_sautoniax refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_regenerer_profil_sautoniax_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander la régénération du navigateur d'un profil.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_profil = message.get("nom_profil", "")
                if not nom_profil:
                    await websocket.send_text(json.dumps({
                        "type": "demander_regenerer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": "Champ 'nom_profil' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_regenerer_profil_sautoniax refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_regenerer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "nom_profil": nom_profil, "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_regenerer_profil_sautoniax", "nom_profil": nom_profil,
                            "garder_donnees": bool(message.get("garder_donnees", False)),
                            "relancer": bool(message.get("relancer", True)),
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_regenerer_profil_sautoniax : transmis à '%s' (id=%s, profil=%r) par pilote id=%s",
                        cible.nom, id_executant, nom_profil, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_regenerer_profil_sautoniax_ack", "ok": True,
                        "id_executant": id_executant, "nom_profil": nom_profil,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_regenerer_profil_sautoniax à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_regenerer_profil_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "nom_profil": nom_profil, "erreur": str(e),
                    }))

            elif type_message == "regenerer_profil_sautoniax_resultat":
                # PATCH (cf. demander_regenerer_profil_sautoniax ci-dessus)
                # -- symétrique de creer_profil_sautoniax_resultat :
                # résultat RÉEL de la régénération du navigateur,
                # DIFFUSÉ à tous les pilotes connectés. Réservé au rôle
                # "executant".
                if connexion.role != "executant":
                    logger.warning("regenerer_profil_sautoniax_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                message_diffuse = dict(message)
                message_diffuse["id_executant"] = connexion.nom
                logger.info(
                    "regenerer_profil_sautoniax_resultat : '%s' -- profil=%r ok=%s -- diffusé à %d pilote(s)",
                    connexion.nom, message.get("nom_profil", ""), message.get("ok", False), len(registre.pilotes()),
                )
                # CORRECTIF (bug n°3) -- cf. commentaire toggle_proxy_natif_resultat plus haut.
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps(message_diffuse))
                    except Exception:
                        logger.exception("Échec relais regenerer_profil_sautoniax_resultat vers pilote '%s'", pilote.nom)

            elif type_message == "demander_dupliquer_profil_sautoniax":
                # AJOUT (dupliquer un profil cible) -- réservé au rôle
                # "pilote". Même patron EXACT que demander_supprimer_profil_
                # sautoniax (relais CIBLÉ pur) : le sAutoniax visé copie
                # lui-même le dossier du profil source vers chaque nom
                # cible (cf. AutoniaX.py, _sautoniax_dupliquer_profil) puis
                # répond via dupliquer_profil_sautoniax_resultat plus bas
                # (DIFFUSÉ à tous les pilotes).
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_dupliquer_profil_sautoniax refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_dupliquer_profil_sautoniax_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander la duplication d'un profil.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_source = message.get("nom_source", "")
                noms_cibles = message.get("noms_cibles") or []
                if not nom_source or not isinstance(noms_cibles, list) or not noms_cibles:
                    await websocket.send_text(json.dumps({
                        "type": "demander_dupliquer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "nom_source": nom_source, "erreur": "Champs 'nom_source'/'noms_cibles' manquants ou invalides.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("demander_dupliquer_profil_sautoniax refusé : exécutant '%s' introuvable/déconnecté", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_dupliquer_profil_sautoniax_ack", "ok": False, "id_executant": id_executant,
                        "nom_source": nom_source, "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_dupliquer_profil_sautoniax", "nom_source": nom_source,
                            "noms_cibles": noms_cibles,
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_dupliquer_profil_sautoniax : transmis à '%s' (id=%s, source=%r, cibles=%r) par pilote id=%s",
                        cible.nom, id_executant, nom_source, noms_cibles, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_dupliquer_profil_sautoniax_ack", "ok": True,
                        "id_executant": id_executant, "nom_source": nom_source,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_dupliquer_profil_sautoniax à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_dupliquer_profil_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "nom_source": nom_source, "erreur": str(e),
                    }))

            elif type_message == "dupliquer_profil_sautoniax_resultat":
                # AJOUT (cf. demander_dupliquer_profil_sautoniax) -- résultat
                # RÉEL de la duplication, DIFFUSÉ à tous les pilotes connectés
                # (même patron que supprimer_profil_sautoniax_resultat).
                # Réservé au rôle "executant".
                if connexion.role != "executant":
                    logger.warning("dupliquer_profil_sautoniax_resultat refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                message_diffuse = dict(message)
                message_diffuse["id_executant"] = connexion.nom
                logger.info(
                    "dupliquer_profil_sautoniax_resultat : '%s' -- source=%r ok=%s -- diffusé à %d pilote(s)",
                    connexion.nom, message.get("nom_source", ""), message.get("ok", False), len(registre.pilotes()),
                )
                for pilote in registre.pilotes():
                    try:
                        async with registre.verrou_pour(pilote.websocket):
                            await pilote.websocket.send_text(json.dumps(message_diffuse))
                    except Exception:
                        logger.exception("Échec relais dupliquer_profil_sautoniax_resultat vers pilote '%s'", pilote.nom)

            elif type_message == "demander_telecharger_profil_vers_sautoniax":
                # PATCH (onglet Instances -- demande explicite utilisateur :
                # "apres sa on vas pouvoir envoyer un profils du cloud vers
                # un sautoniax et sa vas le chargez dans sont dossier de
                # profils"). Réservé au rôle "pilote". SENS INVERSE de
                # demander_upload_profil_vers_cloud (celui-ci = exécutant
                # -> cloud, celui-là = cloud -> exécutant), même patron
                # EXACT de relais CIBLÉ pur : le sAutoniax visé, une fois ce
                # message reçu, appelle lui-même _sautoniax_assurer_profil_
                # local (cf. AutoniaX.py, réutilisée telle quelle -- déjà
                # utilisée par le mode mono-profil legacy ET le Notebook
                # Distant, aucune duplication) pour télécharger le profil
                # depuis Profils/<nom>.zip dans SON PROPRE dossier
                # sautoniax_profils local, PUIS répond via profils_
                # sautoniax_resultat (même message de résultat que la
                # liste, cf. plus haut -- pas de type dédié : le pilote
                # redemande simplement un rafraîchissement de la liste une
                # fois notifié du succès, cf. demander_telecharger_profil_
                # vers_sautoniax_resultat plus bas qui ne porte que ok/
                # erreur, PAS la liste elle-même).
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_telecharger_profil_vers_sautoniax refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_telecharger_profil_vers_sautoniax_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander l'envoi d'un profil vers un sAutoniax.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                nom_profil = message.get("nom_profil", "")
                if not nom_profil:
                    await websocket.send_text(json.dumps({
                        "type": "demander_telecharger_profil_vers_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "nom_profil": nom_profil,
                        "erreur": "Champ 'nom_profil' manquant.",
                    }))
                    continue
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning(
                        "demander_telecharger_profil_vers_sautoniax refusé : exécutant '%s' introuvable/déconnecté",
                        id_executant,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_telecharger_profil_vers_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "nom_profil": nom_profil,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_telecharger_profil_vers_sautoniax",
                            "nom_profil": nom_profil, "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_telecharger_profil_vers_sautoniax : transmis à '%s' (id=%s, profil=%r) par pilote id=%s",
                        cible.nom, id_executant, nom_profil, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_telecharger_profil_vers_sautoniax_ack", "ok": True,
                        "id_executant": id_executant, "nom_profil": nom_profil,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_telecharger_profil_vers_sautoniax à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_telecharger_profil_vers_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "nom_profil": nom_profil, "erreur": str(e),
                    }))

            elif type_message == "telecharger_profil_vers_sautoniax_resultat":
                # PATCH (cf. demander_telecharger_profil_vers_sautoniax
                # ci-dessus) -- RELAIS DIRECT au pilote demandeur (même
                # patron EXACT que profils_sautoniax_resultat : id_pilote
                # transmis tel quel, ne concerne QUE celui qui a demandé
                # ce téléchargement précis, pas une diffusion à tous).
                # Réservé au rôle "executant".
                if connexion.role != "executant":
                    logger.warning(
                        "telecharger_profil_vers_sautoniax_resultat refusé (rôle=%r) id=%s",
                        connexion.role, id_connexion,
                    )
                    continue
                id_pilote_cible = message.get("id_pilote", "")
                # CORRECTIF (cf. profils_sautoniax_resultat plus haut, même
                # bug EXACT) : résolution par id_pilote_stable, pas par
                # id_connexion.
                pilote_cible = registre.pilote_par_id(id_pilote_cible)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning(
                        "telecharger_profil_vers_sautoniax_resultat : pilote '%s' introuvable/déconnecté, message perdu (id=%s)",
                        id_pilote_cible, id_connexion,
                    )
                else:
                    try:
                        message_relais = dict(message)
                        message_relais["id_executant"] = connexion.nom
                        async with registre.verrou_pour(pilote_cible.websocket):
                            await pilote_cible.websocket.send_text(json.dumps(message_relais))
                        logger.info(
                            "telecharger_profil_vers_sautoniax_resultat : '%s' -- profil=%r ok=%s -- relayé au pilote '%s'",
                            connexion.nom, message.get("nom_profil", ""), message.get("ok", False), id_pilote_cible,
                        )
                    except Exception:
                        logger.exception("Échec relais telecharger_profil_vers_sautoniax_resultat vers pilote '%s'", id_pilote_cible)

            elif type_message == "telecharger_profil_vers_sautoniax_progression":
                # PATCH (cf. telecharger_profil_vers_sautoniax_resultat
                # ci-dessus) -- RELAIS DIRECT au pilote demandeur, même
                # patron EXACT que projet_distant_progression : aucune
                # logique métier, un message unique (pas en chunks) relayé
                # tel quel avec id_executant ajouté. Réservé au rôle
                # "executant". Sans ce relais, envoyer_telecharger_profil_
                # vers_sautoniax_progression (client, côté exécutant)
                # tombe dans le vide -- le pilote ne reçoit jamais la
                # progression bien qu'il sache déjà la traiter (dispatch
                # _traiter_message -> telecharger_profil_vers_sautoniax_
                # progression_recu).
                if connexion.role != "executant":
                    continue
                id_pilote = message.get("id_pilote", "")
                pilote_cible = registre.pilote_par_id(id_pilote)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning("telecharger_profil_vers_sautoniax_progression : pilote '%s' introuvable, message perdu", id_pilote)
                    continue
                try:
                    message_relais = dict(message)
                    message_relais["id_executant"] = connexion.nom
                    async with registre.verrou_pour(pilote_cible.websocket):
                        await pilote_cible.websocket.send_text(json.dumps(message_relais))
                except Exception:
                    logger.exception("Échec relais telecharger_profil_vers_sautoniax_progression vers pilote '%s'", id_pilote)

            elif type_message == "demander_liste_profils_locaux_sautoniax":
                # PATCH (BUGFIX -- "Type de message inconnu (Étape 0, seul
                # 'register' est géré) : 'demander_liste_profils_locaux_
                # sautoniax'") : ce type de message est déjà émis par
                # ClientServeurT.demander_liste_profils_locaux_sautoniax
                # (cf. AutoniaX.py -- TaskScript Editor, appelée à chaque
                # changement de sAutoniax sélectionné pour peupler le menu
                # "Profils" avec les profils RÉELLEMENT présents sur CE
                # sAutoniax, pas tous les profils du cloud) et déjà géré
                # en réception côté sAutoniax (cf. AutoniaX.py, bloc
                # "elif data.get(\"type\") == 'demander_liste_profils_
                # locaux_sautoniax'" -- scanne sautoniax_profils/ en
                # local et répond via liste_profils_locaux_sautoniax_
                # resultat) -- mais AUCUN handler ne le relayait ici, donc
                # chaque demande tombait dans le vide (log "Type de
                # message inconnu"), et le menu "Profils" du TaskScript
                # Editor restait vide/jamais rafraîchi pour le sAutoniax
                # sélectionné. Même patron EXACT que demander_telecharger_
                # profil_vers_sautoniax ci-dessus (relais CIBLÉ pur, aucune
                # logique métier ici -- le serveur ne lit jamais lui-même
                # le disque du sAutoniax). Réservé au rôle "pilote".
                if connexion.role != "pilote":
                    logger.warning(
                        "demander_liste_profils_locaux_sautoniax refusé (rôle=%r, seul 'pilote' est autorisé) id=%s",
                        connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_liste_profils_locaux_sautoniax_ack", "ok": False,
                        "erreur": "Seul le pilote peut demander la liste des profils locaux d'un sAutoniax.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning(
                        "demander_liste_profils_locaux_sautoniax refusé : exécutant '%s' introuvable/déconnecté",
                        id_executant,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_liste_profils_locaux_sautoniax_ack", "ok": False,
                        "id_executant": id_executant,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_liste_profils_locaux_sautoniax", "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "demander_liste_profils_locaux_sautoniax : transmis à '%s' (id=%s) par pilote id=%s",
                        cible.nom, id_executant, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "demander_liste_profils_locaux_sautoniax_ack", "ok": True,
                        "id_executant": id_executant,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission demander_liste_profils_locaux_sautoniax à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "demander_liste_profils_locaux_sautoniax_ack", "ok": False,
                        "id_executant": id_executant, "erreur": str(e),
                    }))

            elif type_message == "liste_profils_locaux_sautoniax_resultat":
                # PATCH (cf. demander_liste_profils_locaux_sautoniax
                # ci-dessus) -- RELAIS DIRECT au pilote demandeur, même
                # patron EXACT que telecharger_profil_vers_sautoniax_
                # resultat (id_pilote transmis tel quel par le sAutoniax,
                # reçu dans le message qu'il a lui-même reçu). Réservé au
                # rôle "executant". Best-effort : un pilote déconnecté
                # entre-temps ne fait jamais planter l'exécutant qui vient
                # de répondre.
                if connexion.role != "executant":
                    logger.warning(
                        "liste_profils_locaux_sautoniax_resultat refusé (rôle=%r) id=%s",
                        connexion.role, id_connexion,
                    )
                    continue
                id_pilote_cible = message.get("id_pilote", "")
                # CORRECTIF (cf. profils_sautoniax_resultat plus haut, même
                # bug EXACT) : résolution par id_pilote_stable, pas par
                # id_connexion.
                pilote_cible = registre.pilote_par_id(id_pilote_cible)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning(
                        "liste_profils_locaux_sautoniax_resultat : pilote '%s' introuvable/déconnecté, message perdu (id=%s)",
                        id_pilote_cible, id_connexion,
                    )
                else:
                    try:
                        message_relais = dict(message)
                        message_relais["id_executant"] = connexion.nom
                        async with registre.verrou_pour(pilote_cible.websocket):
                            await pilote_cible.websocket.send_text(json.dumps(message_relais))
                        logger.info(
                            "liste_profils_locaux_sautoniax_resultat : '%s' -- %d profil(s) -- relayé au pilote '%s'",
                            connexion.nom, len(message.get("profils", [])), id_pilote_cible,
                        )
                    except Exception:
                        logger.exception("Échec relais liste_profils_locaux_sautoniax_resultat vers pilote '%s'", id_pilote_cible)

            elif type_message == "envoyer_projet_vers_sautoniax_debut":
                # PATCH (Patch 4.4.a -- envoi d'un projet + profils cochés
                # vers un sAutoniax ciblé). Réservé au rôle "pilote". Même
                # protocole EN CHUNKS que envoyer_profil_* (cf. Upload
                # ProfilEnCours), mais RELAYÉ EN DIRECT vers l'exécutant
                # visé plutôt que stocké sur B2 -- ce transfert est un
                # dossier de projet complet (sous-projets + profils
                # cochés, potentiellement volumineux), pas un objet
                # destiné à persister dans le cloud (cf. §4.4.a : "le
                # serveurT transmet au sAutoniax ciblé"). Aucun état
                # ProjetEnvoiEnCours nécessaire côté serveur -- chaque
                # chunk est transmis puis oublié immédiatement, seul le
                # PILOTE et l'EXÉCUTANT gardent l'état de la session (id
                # de session généré par le pilote, cf. AutoniaX.py
                # ClientServeurT._envoyer_projet_vers_sautoniax, transmis
                # tel quel dans chaque message pour corréler les chunks
                # côté exécutant).
                #
                # PATCH E (cf. cahier des charges patchs.md, section E.6 --
                # "Vérifications serveur avant de (re)lancer un
                # traitement") -- REMPLACE l'ancien verrou binaire
                # "projet_distribue_en_cours" par DEUX vérifications
                # distinctes, dans l'ordre demandé par le cahier :
                #   E.6.2 -- un ou plusieurs des profils DEMANDÉS ici
                #     sont-ils déjà "en cours" (cf. Connexion.profils_en_
                #     cours, peuplé par le message "profils_demarres" une
                #     fois le sAutoniax cible confirmé les avoir
                #     réellement démarrés -- PAS à l'envoi lui-même, cf.
                #     docstring de Registre.profils_deja_utilises) ?
                #   E.6.3 -- le nombre total de profils qui tourneraient
                #     EN MÊME TEMPS sur CETTE cible (déjà en cours +
                #     ceux demandés ici) dépasse-t-il 30 ?
                # Le nettoyage post-exécution (E.6.1) n'est PAS une
                # vérification à l'envoi -- c'est le sAutoniax lui-même
                # qui notifie profils_fermes une fois terminé (cf.
                # ClientServeurT.envoyer_profils_fermes), rien à vérifier
                # ici pour ce point.
                if connexion.role != "pilote":
                    logger.warning(
                        "envoyer_projet_vers_sautoniax_debut refusé (rôle=%r) id=%s", connexion.role, id_connexion,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_debut_ack", "ok": False,
                        "erreur": "Seul le pilote peut envoyer un projet vers un sAutoniax.",
                    }))
                    continue

                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("envoyer_projet_vers_sautoniax_debut refusé : exécutant '%s' introuvable", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_debut_ack", "ok": False, "id_executant": id_executant,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue

                profils_demandes = message.get("profils", [])

                # E.6.2 -- conflit de profil (cf. docstring de Registre.
                # profils_deja_utilises : croise TOUS les exécutants, pas
                # seulement `cible`, un profil ne doit tourner nulle part
                # deux fois à la fois).
                conflits = registre.profils_deja_utilises(profils_demandes)
                if conflits:
                    noms_en_conflit = ", ".join(sorted(conflits.keys()))
                    logger.warning(
                        "envoyer_projet_vers_sautoniax_debut refusé : profil(s) déjà en cours ailleurs (%s)",
                        noms_en_conflit,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_debut_ack", "ok": False, "id_executant": id_executant,
                        "erreur": (
                            f"Profil(s) déjà en cours d'exécution ailleurs : {noms_en_conflit}. "
                            "Patientez ou changez de profils."
                        ),
                    }))
                    continue

                # E.6.3 -- limite de 30 instances SIMULTANÉES sur CETTE
                # cible précise (déjà en cours + ce qui serait ouvert par
                # cette demande, cf. docstring de section E : "compte
                # tenu de ce qui tourne déjà + ce qu'on veut lancer").
                nb_deja_en_cours = registre.nb_instances_totales_sur(id_executant)
                nb_apres_lancement = nb_deja_en_cours + len(profils_demandes)
                if nb_apres_lancement > LIMITE_INSTANCES_PAR_EXECUTANT:
                    logger.warning(
                        "envoyer_projet_vers_sautoniax_debut refusé : limite d'instances dépassée sur '%s' (%d + %d > %d)",
                        id_executant, nb_deja_en_cours, len(profils_demandes), LIMITE_INSTANCES_PAR_EXECUTANT,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_debut_ack", "ok": False, "id_executant": id_executant,
                        "erreur": (
                            f"Limite de {LIMITE_INSTANCES_PAR_EXECUTANT} instances simultanées dépassée sur "
                            f"cet exécutant ({nb_deja_en_cours} déjà en cours + {len(profils_demandes)} demandé(s))."
                        ),
                    }))
                    continue

                session_id = message.get("session_id", "")
                nom_projet = message.get("nom_projet", "")
                if not session_id or not nom_projet:
                    logger.warning("envoyer_projet_vers_sautoniax_debut refusé : champ(s) manquant(s)")
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_debut_ack", "ok": False, "id_executant": id_executant,
                        "erreur": "Champs manquants (session_id, nom_projet requis).",
                    }))
                    continue

                try:
                    # Relais direct au sAutoniax visé -- transmet aussi
                    # id_pilote (id_connexion de CE pilote) pour que
                    # l'exécutant sache à qui adresser retour_projet_
                    # execute_* une fois le traitement terminé (cf.
                    # §4.4.d), sans que le serveur ait besoin de garder
                    # un état de session dédié pour ça.
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "envoyer_projet_vers_sautoniax_debut",
                            "session_id": session_id, "nom_projet": nom_projet,
                            "profils": profils_demandes,
                            "nb_chunks": message.get("nb_chunks", 0),
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    # PATCH E -- PAS de marquage "en cours" ici (contraste
                    # avec l'ancien cible.projet_distribue_en_cours =
                    # nom_projet) : le sAutoniax n'a encore RIEN démarré à
                    # cet instant, seulement reçu le dossier (cf. E.6.1,
                    # le marquage réel arrive plus tard via le message
                    # "profils_demarres" une fois les profils confirmés
                    # opérationnels côté sAutoniax).
                    logger.info(
                        "envoyer_projet_vers_sautoniax_debut : '%s' (session=%s) -> '%s'",
                        nom_projet, session_id, id_executant,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_debut_ack", "ok": True, "id_executant": id_executant,
                        "session_id": session_id,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission envoyer_projet_vers_sautoniax_debut à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_debut_ack", "ok": False, "id_executant": id_executant,
                        "erreur": str(e),
                    }))

            elif type_message == "profils_demarres":
                # PATCH E (E.6.1/E.6.2/E.6.3 -- cf. cahier des charges
                # patchs.md, section E.6, et docstring de Connexion.
                # profils_en_cours). Réservé au rôle "executant" : c'est
                # LUI qui sait quand un profil a réellement démarré (pas
                # le pilote, qui ne fait qu'envoyer une demande, cf.
                # ClientServeurT.envoyer_profils_demarres côté AutoniaX.py
                # -- appelé une fois _sautoniax_attendre_instances_pretes
                # confirmé). Aucun accusé de réception nécessaire (fire-
                # and-forget côté émetteur, cf. sa docstring) -- purement
                # une mise à jour d'état interne au serveur, rien à
                # relayer à personne.
                if connexion.role != "executant":
                    logger.warning("profils_demarres refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                noms_profils = message.get("profils", [])
                infos_communes = {
                    "session_id": message.get("session_id", ""),
                    "id_projet_batch": message.get("id_projet_batch", ""),
                    "nom_projet": message.get("nom_projet", ""),
                }
                for nom_profil in noms_profils:
                    connexion.profils_en_cours[nom_profil] = dict(infos_communes)
                logger.info(
                    "profils_demarres : %d profil(s) démarré(s) sur '%s' (%s)",
                    len(noms_profils), id_connexion, ", ".join(noms_profils),
                )

            elif type_message == "instances_projet":
                # PATCH E.1 (cf. cahier des charges patchs.md, section
                # E.1, et docstring de ClientServeurT.envoyer_instances_
                # projet côté AutoniaX.py pour le pourquoi de ce message
                # dédié plutôt qu'une extension de "profils_demarres").
                # Réservé au rôle "executant", comme profils_demarres.
                # CONTRAIREMENT à profils_demarres : simple RELAIS direct
                # au pilote ciblé (id_pilote transmis, même routage exact
                # que retour_projet_execute_* plus bas) -- aucun état
                # interne modifié ici, ce message ne sert qu'à faire
                # connaître au pilote les instance_id réels d'un batch
                # multi-profils, pour cibler ensuite une capture/commande
                # sur l'instance précise voulue (cf. E.1 -- bouton
                # "Aperçu" par ligne de "Projets Distribués"). Best-effort
                # -- si le pilote est absent/déconnecté, le message est
                # simplement perdu (loggé), jamais bloquant pour
                # l'exécutant qui l'a envoyé.
                if connexion.role != "executant":
                    logger.warning("instances_projet refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                id_pilote_instances = message.get("id_pilote", "")
                # CORRECTIF (cf. profils_sautoniax_resultat plus haut, même
                # bug EXACT) : résolution par id_pilote_stable.
                pilote_cible_instances = registre.pilote_par_id(id_pilote_instances)
                if pilote_cible_instances is None or pilote_cible_instances.role != "pilote":
                    logger.warning(
                        "instances_projet : pilote '%s' introuvable/déconnecté, message perdu (id=%s)",
                        id_pilote_instances, id_connexion,
                    )
                else:
                    try:
                        message_relais = dict(message)
                        message_relais["id_executant"] = connexion.nom
                        async with registre.verrou_pour(pilote_cible_instances.websocket):
                            await pilote_cible_instances.websocket.send_text(json.dumps(message_relais))
                    except Exception:
                        logger.exception("Échec relais instances_projet vers pilote '%s'", id_pilote_instances)

            elif type_message == "profils_fermes":
                # PATCH E -- symétrique de "profils_demarres" ci-dessus
                # (cf. E.6.1 : "dès qu'un projet termine son exécution,
                # tous les profils qu'il avait ouverts doivent être
                # fermés pour libérer les ressources"). .pop(..., None) :
                # un profil absent de profils_en_cours (ex. notification
                # en double, ou fermeture d'un profil jamais confirmé
                # démarré) est un no-op silencieux, jamais une erreur --
                # cohérent avec le reste du fichier (relais/comptabilité
                # tolérant, cf. principe "aucune logique métier").
                if connexion.role != "executant":
                    logger.warning("profils_fermes refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                noms_profils = message.get("profils", [])
                for nom_profil in noms_profils:
                    connexion.profils_en_cours.pop(nom_profil, None)
                logger.info(
                    "profils_fermes : %d profil(s) libéré(s) sur '%s' (%s)",
                    len(noms_profils), id_connexion, ", ".join(noms_profils),
                )

            elif type_message == "envoyer_projet_vers_sautoniax_chunk":
                # Relais direct, chunk par chunk, même session_id que le
                # message _debut correspondant -- le serveur ne rassemble
                # ni ne valide l'ordre des chunks ici (contrairement à
                # UploadProfilEnCours) : il transmet tel quel à
                # l'exécutant visé, qui est responsable de l'assemblage
                # (cf. AutoniaX.py côté sAutoniax) puisque ce transfert
                # n'est jamais stocké sur B2 -- aucune raison de dupliquer
                # cette logique côté serveur alors qu'il ne fait que
                # relayer.
                if connexion.role != "pilote":
                    logger.warning("envoyer_projet_vers_sautoniax_chunk refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("envoyer_projet_vers_sautoniax_chunk refusé : exécutant '%s' introuvable", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_chunk_ack", "ok": False,
                        "session_id": message.get("session_id", ""),
                        "index": message.get("index"),
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue
                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "envoyer_projet_vers_sautoniax_chunk",
                            "session_id": message.get("session_id", ""),
                            "index": message.get("index"),
                            "contenu_b64": message.get("contenu_b64", ""),
                        }))
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_chunk_ack", "ok": True,
                        "session_id": message.get("session_id", ""),
                        "index": message.get("index"),
                    }))
                except Exception as e:
                    logger.exception("Échec transmission envoyer_projet_vers_sautoniax_chunk à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "envoyer_projet_vers_sautoniax_chunk_ack", "ok": False,
                        "session_id": message.get("session_id", ""),
                        "index": message.get("index"), "erreur": str(e),
                    }))

            elif type_message == "envoyer_projet_vers_sautoniax_fin":
                # Purement déclaratif, relayé tel quel à l'exécutant visé
                # (signale la fin de la séquence de chunks, même patron
                # que envoyer_profil_fin/telecharger_fichier_fin) -- pas
                # d'accusé de réception distinct attendu par le pilote au-
                # delà du "ok" immédiat ci-dessous : le VRAI résultat
                # (démarrage des profils réussi ou non, cf. §4.4.c)
                # arrivera plus tard via statut_executant, pas ici.
                if connexion.role != "pilote":
                    logger.warning("envoyer_projet_vers_sautoniax_fin refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is not None:
                    try:
                        async with registre.verrou_pour(cible.websocket):
                            await cible.websocket.send_text(json.dumps({
                                "type": "envoyer_projet_vers_sautoniax_fin",
                                "session_id": message.get("session_id", ""),
                            }))
                    except Exception:
                        pass
                logger.info("envoyer_projet_vers_sautoniax_fin : session=%s -> '%s'", message.get("session_id", ""), id_executant)

            elif type_message in ("retour_projet_execute_debut", "retour_projet_execute_chunk", "retour_projet_execute_fin"):
                # PATCH (Patch 4.4.d -- retour du projet exécuté, sens
                # inverse d'envoyer_projet_vers_sautoniax_* : exécutant ->
                # serveurT -> pilote). Réservé au rôle "executant". Relayé
                # AU PILOTE QUI AVAIT ENVOYÉ LE PROJET -- id_pilote transmis
                # par le sAutoniax dans chaque message (reçu lui-même dans
                # envoyer_projet_vers_sautoniax_debut, cf. bloc ci-dessus),
                # pas une diffusion à tous les pilotes (un seul pilote est
                # concerné par ce retour précis).
                #
                # PATCH E.2 (cf. cahier des charges patchs.md -- "quand un
                # batch termine son exécution, le serveurT le stocke dans
                # un dossier cloud dédié 'Batch Traité' ... permet la
                # continuité même en cas de déconnexion/reconnexion").
                # AJOUT, ne remplace rien : chaque chunk est maintenant
                # AUSSI accumulé sur disque (cf. Connexion.retour_projet_
                # en_cours) en plus d'être relayé en direct au pilote
                # (best-effort, comme avant -- si le pilote est absent, le
                # relais échoue silencieusement mais l'accumulation, elle,
                # continue normalement). À "_fin", le zip complet est
                # uploadé vers B2 SI le stockage est configuré -- sinon
                # (pilote local sans B2 configuré) le comportement reste
                # EXACTEMENT celui d'avant ce patch, relais direct
                # uniquement, aucune régression pour qui n'utilise pas B2.
                if connexion.role != "executant":
                    logger.warning("%s refusé (rôle=%r) id=%s", type_message, connexion.role, id_connexion)
                    continue

                if type_message == "retour_projet_execute_debut":
                    nb_chunks = message.get("nb_chunks")
                    session_id = message.get("session_id", "")
                    id_pilote_debut = message.get("id_pilote", "")
                    if not isinstance(nb_chunks, int) or nb_chunks <= 0:
                        logger.warning("retour_projet_execute_debut refusé : nb_chunks invalide id=%s", id_connexion)
                    else:
                        # Toute accumulation précédente non terminée
                        # (retour abandonné) est nettoyée avant d'en
                        # ouvrir une nouvelle -- même choix que
                        # envoyer_profil_debut (UploadProfilEnCours).
                        if connexion.retour_projet_en_cours is not None:
                            connexion.retour_projet_en_cours.nettoyer()
                        connexion.retour_projet_en_cours = RetourProjetEnCours(
                            session_id, id_pilote_debut, nb_chunks,
                        )

                elif type_message == "retour_projet_execute_chunk":
                    session_accum = connexion.retour_projet_en_cours
                    if session_accum is not None:
                        index = message.get("index")
                        contenu_b64 = message.get("contenu_b64")
                        # Même contrainte d'ordre strict que envoyer_
                        # profil_chunk -- si un chunk arrive hors ordre
                        # (ne devrait jamais arriver, cf. _envoyer_retour_
                        # projet_execute qui envoie séquentiellement),
                        # on abandonne silencieusement l'ACCUMULATION
                        # SEULE (pas le relais direct ci-dessous, qui
                        # continue normalement) plutôt que de risquer un
                        # zip B2 corrompu -- l'utilisateur garde au moins
                        # le résultat en direct si le pilote est connecté.
                        if index == session_accum.prochain_index_attendu:
                            try:
                                session_accum.ecrire_chunk(base64.b64decode(contenu_b64))
                                session_accum.prochain_index_attendu += 1
                            except Exception:
                                logger.exception("retour_projet_execute_chunk : échec accumulation, id=%s", id_connexion)
                                connexion.retour_projet_en_cours.nettoyer()
                                connexion.retour_projet_en_cours = None
                        else:
                            logger.warning(
                                "retour_projet_execute_chunk : hors ordre pour l'accumulation B2 "
                                "(index=%r attendu=%d) -- accumulation abandonnée, relais direct maintenu, id=%s",
                                index, session_accum.prochain_index_attendu, id_connexion,
                            )
                            session_accum.nettoyer()
                            connexion.retour_projet_en_cours = None

                id_pilote = message.get("id_pilote", "")
                pilote_cible = registre.pilote_par_id(id_pilote)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning("%s : pilote '%s' introuvable/déconnecté, retour perdu", type_message, id_pilote)
                    if type_message == "retour_projet_execute_fin":
                        # Le sAutoniax se libère quand même -- le pilote
                        # déconnecté n'a plus personne à qui reprocher un
                        # retour perdu, mais CE sAutoniax ne doit pas
                        # rester bloqué "occupé" indéfiniment pour un
                        # projet dont plus personne n'attend le résultat.
                        # PATCH E : plus de champ binaire à vider -- ce
                        # sont les profils encore listés dans
                        # profils_en_cours qui bloqueraient cet exécutant
                        # (E.6.2/E.6.3). Normalement déjà vidés par
                        # "profils_fermes" (cf. bloc plus haut), mais on
                        # nettoie ici aussi par sécurité, au cas où ce
                        # message aurait été perdu/pas encore reçu --
                        # sans ça, ces profils resteraient "en cours"
                        # indéfiniment alors que plus personne n'attend
                        # ce résultat.
                        if connexion.profils_en_cours:
                            logger.warning(
                                "retour_projet_execute_fin (pilote perdu) : "
                                "nettoyage de secours de %d profil(s) encore "
                                "marqués en cours sur '%s' (id=%s)",
                                len(connexion.profils_en_cours), connexion.nom, id_connexion,
                            )
                            connexion.profils_en_cours.clear()
                        # PATCH E.2 -- c'est PRÉCISÉMENT le cas que cette
                        # section doit couvrir : pilote absent au moment du
                        # retour. L'upload B2 ci-dessous (hors de ce bloc
                        # if, cf. suite) a lieu MÊME ICI -- "continue" est
                        # volontairement PAS utilisé pour ce message précis
                        # (contrairement à avant ce patch) afin de ne pas
                        # sauter l'upload de secours.
                        if type_message != "retour_projet_execute_fin":
                            continue
                    else:
                        continue
                else:
                    try:
                        message_relais = dict(message)
                        message_relais["id_executant"] = connexion.nom
                        async with registre.verrou_pour(pilote_cible.websocket):
                            await pilote_cible.websocket.send_text(json.dumps(message_relais))
                    except Exception:
                        logger.exception("Échec relais %s vers pilote '%s'", type_message, id_pilote)

                if type_message == "retour_projet_execute_fin":
                    # PATCH E.2 -- upload B2 de l'accumulation complète,
                    # SI le stockage est configuré ET que l'accumulation a
                    # abouti (nb de chunks reçus == attendu -- cf. garde
                    # ci-dessous, symétrique à envoyer_profil_fin). Ne
                    # bloque jamais le reste du traitement de ce message
                    # (libération des profils, log "redevient disponible"
                    # plus bas) : une erreur d'upload B2 est loggée et
                    # avalée, jamais une raison de laisser ce sAutoniax
                    # bloqué "occupé".
                    session_accum = connexion.retour_projet_en_cours
                    if session_accum is not None and stockage.configure:
                        if session_accum.prochain_index_attendu == session_accum.nb_chunks_attendus:
                            try:
                                contenu_zip = session_accum.chemin_temp.read_bytes()
                                nom_projet_meta = message.get("nom_projet") or "projet"
                                horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                                # Nom de dossier lisible + session_id pour
                                # garantir l'unicité (deux envois du même
                                # nom de projet à quelques secondes
                                # d'écart ne doivent jamais s'écraser l'un
                                # l'autre) -- cf. E.2 : "un bouton
                                # Télécharger par entrée terminée".
                                prefixe = f"Batch Traité/{nom_projet_meta} — {horodatage} — {session_accum.session_id}"
                                await stockage.uploader_bytes(f"{prefixe}/resultat.zip", contenu_zip)
                                meta = {
                                    "session_id": session_accum.session_id,
                                    "nom_projet": nom_projet_meta,
                                    # PATCH (identité stable par nom) -- connexion.nom
                                    # (déjà présent juste en dessous comme nom_executant,
                                    # gardé ici aussi par cohérence avec le reste des
                                    # métadonnées d'archive -- id_connexion n'aurait plus
                                    # aucun sens une fois ce sAutoniax déconnecté/reconnecté).
                                    "id_executant": connexion.nom,
                                    "nom_executant": connexion.nom,
                                    "id_pilote": session_accum.id_pilote,
                                    "date_iso": datetime.now(timezone.utc).isoformat(),
                                    "taille_octets": len(contenu_zip),
                                }
                                await stockage.uploader_bytes(f"{prefixe}/meta.json", json.dumps(meta).encode("utf-8"))
                                logger.info(
                                    "retour_projet_execute_fin : '%s' archivé dans B2 (%d octets) sous '%s'",
                                    nom_projet_meta, len(contenu_zip), prefixe,
                                )
                            except Exception:
                                logger.exception(
                                    "retour_projet_execute_fin : échec upload B2 (session=%s) -- résultat "
                                    "conservé uniquement côté relais direct s'il a réussi",
                                    session_accum.session_id,
                                )
                        else:
                            logger.warning(
                                "retour_projet_execute_fin : accumulation B2 incomplète (%d/%d chunk(s)) "
                                "id=%s -- pas d'upload, relais direct seul",
                                session_accum.prochain_index_attendu, session_accum.nb_chunks_attendus, id_connexion,
                            )
                    if session_accum is not None:
                        session_accum.nettoyer()
                        connexion.retour_projet_en_cours = None

                    # PATCH E : la libération réelle des profils occupés
                    # par CE projet a normalement déjà eu lieu via le
                    # message "profils_fermes" envoyé par le sAutoniax
                    # juste avant ce retour (cf. AutoniaX.py,
                    # _sautoniax_traiter_projet_recu -- envoyer_profils_
                    # fermes appelé avant envoyer_retour_projet_execute).
                    # Filet de sécurité seulement : si pour une raison
                    # quelconque profils_fermes n'est jamais arrivé (perte
                    # réseau ponctuelle du message, par ex.) alors que la
                    # fin du projet, elle, est bien arrivée, on ne doit
                    # pas laisser ces profils bloqués "en cours"
                    # indéfiniment -- ça empêcherait tout nouveau
                    # lancement les utilisant (E.6.2) et fausserait le
                    # compte d'instances actives (E.6.3) pour rien.
                    if connexion.profils_en_cours:
                        logger.warning(
                            "retour_projet_execute_fin : %d profil(s) encore "
                            "marqués en cours sur '%s' (id=%s) sans "
                            "'profils_fermes' préalable -- nettoyage de "
                            "secours",
                            len(connexion.profils_en_cours), connexion.nom, id_connexion,
                        )
                        connexion.profils_en_cours.clear()
                    logger.info("retour_projet_execute_fin : '%s' redevient disponible (id=%s)", connexion.nom, id_connexion)

            elif type_message == "demander_retelechargement_service_api":
                # AJOUT (migration Flux B vers Drive direct -- demande
                # explicite utilisateur : "et pour le sync, le serveur
                # envoie juste un message de retélarchement au
                # sautoniax, il le retélécharge eux même directement sur
                # le cloud. plus de envoie autonome de fichier du serveur
                # vers les sautoniax"). REMPLACE ENTIÈREMENT l'ancien
                # protocole en chunks mettre_a_jour_service_api_debut/
                # _chunk/_fin (relais direct + accumulation cloud côté
                # connexion.upload_service_api, retirés) : le pilote a
                # déjà uploadé le fichier DIRECTEMENT sur Drive (cf.
                # ClientServeurT._mettre_a_jour_service_api côté
                # AutoniaX.py, App/service_api.zip) AVANT d'envoyer ce
                # message léger -- aucune accumulation, AUCUN stockage.
                # uploader_bytes ici, le fichier est déjà sur Drive.
                # Relais PUR : transmet tel quel à l'exécutant ciblé, en
                # ajoutant id_pilote (point ouvert 4 de la spec, tranché
                # : nécessaire pour que l'exécutant sache à qui répondre
                # via envoyer_mise_a_jour_service_api_resultat, cf.
                # docstring Connexion.id_pilote_stable, même valeur que
                # celle déjà transmise par l'ancien protocole _debut).
                if connexion.role != "pilote":
                    continue
                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is not None:
                    try:
                        async with registre.verrou_pour(cible.websocket):
                            await cible.websocket.send_text(json.dumps({
                                "type": "demander_retelechargement_service_api",
                                "id_executant": id_executant,
                                "id_pilote": (connexion.id_pilote_stable or id_connexion),
                            }))
                    except Exception:
                        logger.exception("Échec transmission demander_retelechargement_service_api à '%s'", id_executant)
                logger.info("demander_retelechargement_service_api relayé -> '%s'", id_executant)

            elif type_message == "mettre_a_jour_service_api_resultat":
                # Retour exécutant -> pilote (succès/échec de l'application
                # locale de la mise à jour côté sAutoniax) -- même relais
                # ciblé par id_pilote que retour_projet_execute_*.
                if connexion.role != "executant":
                    continue
                id_pilote = message.get("id_pilote", "")
                pilote_cible = registre.pilote_par_id(id_pilote)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning("mettre_a_jour_service_api_resultat : pilote '%s' introuvable, résultat perdu", id_pilote)
                    continue
                try:
                    message_relais = dict(message)
                    message_relais["id_executant"] = connexion.nom
                    async with registre.verrou_pour(pilote_cible.websocket):
                        await pilote_cible.websocket.send_text(json.dumps(message_relais))
                except Exception:
                    logger.exception("Échec relais mettre_a_jour_service_api_resultat vers pilote '%s'", id_pilote)

            elif type_message == "demander_retelechargement_project_json":
                # AJOUT (migration Flux B vers Drive direct) -- miroir
                # EXACT de demander_retelechargement_service_api
                # ci-dessus, pour project.json : relais PUR, aucune
                # accumulation, aucun stockage.uploader_bytes ici (le
                # pilote a déjà uploadé App/project.json directement sur
                # Drive avant d'envoyer ce message léger, cf.
                # ClientServeurT._mettre_a_jour_project_json côté
                # AutoniaX.py). Remplace ENTIÈREMENT l'ancien protocole
                # en chunks mettre_a_jour_project_json_debut/_chunk/_fin.
                if connexion.role != "pilote":
                    continue
                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is not None:
                    try:
                        async with registre.verrou_pour(cible.websocket):
                            await cible.websocket.send_text(json.dumps({
                                "type": "demander_retelechargement_project_json",
                                "id_executant": id_executant,
                                "id_pilote": (connexion.id_pilote_stable or id_connexion),
                            }))
                    except Exception:
                        logger.exception("Échec transmission demander_retelechargement_project_json à '%s'", id_executant)
                logger.info("demander_retelechargement_project_json relayé -> '%s'", id_executant)

            elif type_message == "mettre_a_jour_project_json_resultat":
                # Retour exécutant -> pilote, même relais ciblé par
                # id_pilote que mettre_a_jour_service_api_resultat ci-dessus.
                if connexion.role != "executant":
                    continue
                id_pilote = message.get("id_pilote", "")
                pilote_cible = registre.pilote_par_id(id_pilote)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning("mettre_a_jour_project_json_resultat : pilote '%s' introuvable, résultat perdu", id_pilote)
                    continue
                try:
                    message_relais = dict(message)
                    message_relais["id_executant"] = connexion.nom
                    async with registre.verrou_pour(pilote_cible.websocket):
                        await pilote_cible.websocket.send_text(json.dumps(message_relais))
                except Exception:
                    logger.exception("Échec relais mettre_a_jour_project_json_resultat vers pilote '%s'", id_pilote)

            elif type_message == "executer_notebook_distant":
                # PATCH (Patch 4.5 -- Notebook Distant, mode faible
                # connexion). Réservé au rôle "pilote". Le code envoyé est
                # transmis TEL QUEL (pas en chunks -- du code source
                # texte, pas un fichier binaire volumineux, cf. §4.5 :
                # même patron que mettre_a_jour_app qui envoie déjà du
                # texte via contenu_b64 en un seul message). Ciblé sur un
                # couple (sAutoniax, profil) -- id_executant ET
                # profil_nom transmis tels quels au sAutoniax visé, qui
                # est seul responsable de router vers le bon profil (cf.
                # §4.5 : "ciblé sur un couple (sAutoniax, profil)").
                if connexion.role != "pilote":
                    logger.warning("executer_notebook_distant refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "executer_notebook_distant_ack", "ok": False,
                        "erreur": "Seul le pilote peut exécuter du code sur un sAutoniax.",
                    }))
                    continue
                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    await websocket.send_text(json.dumps({
                        "type": "executer_notebook_distant_ack", "ok": False, "id_executant": id_executant,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue
                session_id = message.get("session_id", "")
                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "executer_notebook_distant",
                            "session_id": session_id,
                            "profil_nom": message.get("profil_nom", ""),
                            "code": message.get("code", ""),
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                            # CORRECTIF (Composants en notebook distant, retour
                            # explicite utilisateur -- "je veux le filtrage
                            # precis comme en local") : relais TEL QUEL, sans
                            # aucune logique métier ici (même esprit que le
                            # reste de ce bloc, cf. commentaire "transmis TEL
                            # QUEL" ci-dessus) -- {nom_service_api: instance_id/
                            # id_executant} des ServiceAPI liés pour le Task
                            # d'origine, cf. MoteurExecutionCelluleReseau.lancer
                            # (mAutoniax) et _construire_composants_direct
                            # (sAutoniax) pour le calcul/l'usage réel de ce
                            # champ -- le serveurT n'a besoin de rien en
                            # comprendre, juste de le transporter. {} par
                            # défaut (ancien mAutoniax pas encore mis à jour,
                            # ou notebook distant manuel sans Task associé).
                            "services_api_lies": message.get("services_api_lies") or {},
                            # AJOUT (SPEC_lot_corrections_2026-09.md section 11,
                            # point non couvert -- "serveur.py doit être adapté
                            # en miroir") : simple relais TEL QUEL, sans aucune
                            # logique métier ici (même esprit que services_api_
                            # lies ci-dessus) -- le serveurT n'a besoin de rien
                            # comprendre à ces deux booléens, juste de les
                            # transporter jusqu'au sAutoniax visé, qui sait déjà
                            # les interpréter (cf. AutoniaX.py, _sur_executer_
                            # notebook_distant_demande : reinitialiser_result_
                            # color injecte result_color='#FFFFFF' (CHANGEMENT
                            # hex, cf. retour utilisateur "on fonctionne
                            # maintenant avec le code hexadecimal") dans le
                            # namespace avant exec(), lire_result_color_finale
                            # lit sa valeur finale après exec()). False par
                            # défaut si absent du message reçu -- cohérent avec
                            # l'envoi toujours explicite côté ClientServeurT._
                            # executer_notebook_distant (jamais omis), mais reste
                            # défensif si un ancien pilote non mis à jour omettait
                            # ces champs.
                            "reinitialiser_result_color": message.get("reinitialiser_result_color", False),
                            "lire_result_color_finale": message.get("lire_result_color_finale", False),
                        }))
                    logger.info(
                        "executer_notebook_distant : session=%s profil=%r -> '%s'",
                        session_id, message.get("profil_nom", ""), id_executant,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "executer_notebook_distant_ack", "ok": True, "id_executant": id_executant,
                        "session_id": session_id,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission executer_notebook_distant à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "executer_notebook_distant_ack", "ok": False, "id_executant": id_executant,
                        "erreur": str(e),
                    }))

            elif type_message == "initialiser_notebook_distant":
                # PATCH (bouton "Initialiser" du Notebook Distant --
                # protocole manquant, jamais ajouté côté serveur alors que
                # ClientServeurT.initialiser_notebook_distant l'envoie déjà
                # côté pilote et que _sautoniax_initialiser_notebook_distant
                # sait déjà le traiter côté exécutant). Réservé au rôle
                # "pilote", même pattern EXACT que executer_notebook_distant
                # ci-dessus : ciblé par id_executant, ack immédiat (ok/
                # erreur), PAS de champ `code` (uniquement session_id +
                # profil_nom, cf. ClientServeurT._initialiser_notebook_distant).
                if connexion.role != "pilote":
                    logger.warning("initialiser_notebook_distant refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "initialiser_notebook_distant_ack", "ok": False,
                        "erreur": "Seul le pilote peut initialiser un profil sur un sAutoniax.",
                    }))
                    continue
                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    await websocket.send_text(json.dumps({
                        "type": "initialiser_notebook_distant_ack", "ok": False, "id_executant": id_executant,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue
                session_id = message.get("session_id", "")
                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "initialiser_notebook_distant",
                            "session_id": session_id,
                            "profil_nom": message.get("profil_nom", ""),
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "initialiser_notebook_distant : session=%s profil=%r -> '%s'",
                        session_id, message.get("profil_nom", ""), id_executant,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "initialiser_notebook_distant_ack", "ok": True, "id_executant": id_executant,
                        "session_id": session_id,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission initialiser_notebook_distant à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "initialiser_notebook_distant_ack", "ok": False, "id_executant": id_executant,
                        "erreur": str(e),
                    }))

            elif type_message == "fermer_notebook_distant":
                # PATCH (bouton "Fermer" à côté d'"Initialiser", Task
                # réseau -- demande explicite utilisateur : "il faut que
                # onlajoute a coter du bouton initialiser , la il vas
                # detruit le prfils lancer") -- ferme le profil ACTUELLEMENT
                # chargé par initialiser_notebook_distant sur ce sAutoniax
                # (Camoufox + capture périodique), SANS en recharger un
                # nouveau. Même pattern EXACT que initialiser_notebook_
                # distant ci-dessus : réservé au rôle "pilote", ciblé par
                # id_executant, ack immédiat (transmission), le résultat
                # RÉEL (fermé ou "rien à fermer") arrive séparément via
                # fermer_notebook_distant_resultat (cf. bloc générique de
                # relais juste plus bas, où ce type est ajouté au tuple).
                if connexion.role != "pilote":
                    logger.warning("fermer_notebook_distant refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "fermer_notebook_distant_ack", "ok": False,
                        "erreur": "Seul le pilote peut fermer un profil sur un sAutoniax.",
                    }))
                    continue
                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    await websocket.send_text(json.dumps({
                        "type": "fermer_notebook_distant_ack", "ok": False, "id_executant": id_executant,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue
                session_id = message.get("session_id", "")
                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "fermer_notebook_distant",
                            "session_id": session_id,
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "fermer_notebook_distant : session=%s -> '%s'",
                        session_id, id_executant,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "fermer_notebook_distant_ack", "ok": True, "id_executant": id_executant,
                        "session_id": session_id,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission fermer_notebook_distant à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "fermer_notebook_distant_ack", "ok": False, "id_executant": id_executant,
                        "erreur": str(e),
                    }))

            elif type_message in (
                "notebook_distant_log", "notebook_distant_resultat",
                "initialiser_notebook_distant_log", "initialiser_notebook_distant_resultat",
                "fermer_notebook_distant_resultat", "notebook_distant_image", "morceau",
                "sessions_vivantes",   # AJOUT (signal de vie des sessions, exécutant -> pilote)
            ):
                # Retour exécutant -> pilote : logs stdout/stderr au fil de
                # l'exécution (notebook_distant_log, plusieurs messages
                # possibles) PUIS un résultat final unique
                # (notebook_distant_resultat, ok/erreur) -- ET, même
                # structure de message (session_id/id_pilote + payload),
                # la progression du CHARGEMENT du profil déclenché par
                # initialiser_notebook_distant ci-dessus (initialiser_
                # notebook_distant_log/_resultat, cf. envoyer_initialiser_
                # notebook_distant_log/_resultat côté ClientServeurT) ET le
                # résultat de la FERMETURE déclenchée par fermer_notebook_
                # distant ci-dessus (fermer_notebook_distant_resultat, cf.
                # envoyer_fermer_notebook_distant_resultat côté
                # ClientServeurT) ET une image ponctuelle envoyée par
                # Image.view() (notebook_distant_image, cf. envoyer_
                # notebook_distant_image côté ClientServeurT -- PATCH,
                # screenshot() retourne désormais un objet Image plutôt
                # qu'un chemin) -- d'où le même bloc de relais générique
                # pour les 6 types, aucune distinction de traitement
                # nécessaire ici, le payload spécifique (ligne / ok+message
                # / image_b64) est transmis TEL QUEL et interprété côté
                # pilote selon le type reçu. Même relais ciblé par
                # id_pilote que retour_projet_execute_*/mettre_a_jour_
                # service_api_resultat -- la capture WebP du RENDU
                # PÉRIODIQUE, elle, continue de transiter par le canal
                # existant envoyer_capture/capture_recue (cf. §4.5 :
                # "réutilisation du mécanisme déjà existant de
                # ReceptionScreen"), jamais dupliquée ici -- notebook_
                # distant_image est un envoi PONCTUEL déclenché par le
                # script utilisateur (.view()), pas un flux périodique.
                if connexion.role != "executant":
                    continue
                id_pilote = message.get("id_pilote", "")
                pilote_cible = registre.pilote_par_id(id_pilote)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning("%s : pilote '%s' introuvable, message perdu", type_message, id_pilote)
                    continue
                try:
                    message_relais = dict(message)
                    message_relais["id_executant"] = connexion.nom
                    _t0 = time.time()
                    async with registre.verrou_pour(pilote_cible.websocket):
                        _t1 = time.time()
                        message_relais["t_srv_envoi"] = _t1   # DIAG : horodatage serveur, lu par le pilote
                        _texte_relais = json.dumps(message_relais)
                        await pilote_cible.websocket.send_text(_texte_relais)
                    _t2 = time.time()
                    if type_message != "morceau" or _t2 - _t0 > 0.5:
                        logger.info("[RELAIS] %s -> pilote : attente verrou %.3fs, send_text %.3fs, %d octets%s",
                                    type_message, _t1 - _t0, _t2 - _t1, len(_texte_relais),
                                    (" (émis par l'exécutant à %.3f, soit %.3fs avant relais)" % (message["horodatage_envoi"], _t1 - message["horodatage_envoi"])) if isinstance(message.get("horodatage_envoi"), (int, float)) else "")
                except Exception:
                    logger.exception("Échec relais %s vers pilote '%s'", type_message, id_pilote)

            elif type_message == "pont_pilote_reponse":
                # AJOUT (pont fichiers pilote <-> clone) -- réponse du PILOTE à une demande d'accès fichier faite par
                # le code d'un clone en cours d'exécution (la demande, elle, voyage dans "notebook_distant_image" et
                # est relayée par le bloc générique ci-dessus). SIMPLE RELAIS, aucune logique métier : réservé au
                # rôle "pilote", ciblé sur l'exécutant `id_executant`, sans ack (le clone renvoie sa demande tant qu'il
                # n'a pas de réponse, et le pilote répond alors depuis son cache -- cf. ServicePilotePont).
                if connexion.role != "pilote":
                    logger.warning("pont_pilote_reponse refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    logger.warning("pont_pilote_reponse : exécutant '%s' introuvable ou déconnecté, réponse perdue (le clone renverra sa demande)", id_executant)
                    continue
                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps(message))
                except Exception:
                    logger.exception("Échec relais pont_pilote_reponse vers '%s'", id_executant)

            elif type_message == "regler_capture_instance":
                # PATCH (protocole générique de pilotage à distance du
                # rythme de capture d'UNE instance précise -- réutilisable
                # aussi bien par le mode mono-profil, Notebook Distant/Task
                # réseau, où instance_id désigne l'unique boucle de capture
                # en cours sur le sAutoniax ciblé, que par le futur mode
                # multi-profils, Projets Distribués, où instance_id désigne
                # UNE instance précise parmi plusieurs tournant en parallèle
                # sur le même sAutoniax). Réservé au rôle "pilote". Deux
                # actions distinctes transportées dans le même message
                # (plutôt que deux types de message séparés) car elles
                # ciblent toujours le même couple (id_executant, instance_id)
                # et ne nécessitent qu'un seul point de routage :
                #   - action="ponctuelle" : demande une capture immédiate,
                #     hors du cycle périodique en cours.
                #   - action="taux" : reconfigure à CHAUD le FPS d'envoi
                #     automatique (champ "fps" requis, float > 0).
                # Simple relais TEL QUEL vers le sAutoniax ciblé (même
                # patron que executer_notebook_distant) -- c'est LUI qui
                # sait, selon son mode (mono/multi-profils), comment
                # traduire cette demande en commande locale vers
                # l'instance concernée (cf. AutoniaX.py, gestionnaire
                # sAutoniax de ce message).
                if connexion.role != "pilote":
                    logger.warning("regler_capture_instance refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "regler_capture_instance_ack", "ok": False,
                        "erreur": "Seul le pilote peut régler la capture d'une instance.",
                    }))
                    continue
                id_executant = message.get("id_executant", "")
                instance_id = message.get("instance_id", "")
                action = message.get("action", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    await websocket.send_text(json.dumps({
                        "type": "regler_capture_instance_ack", "ok": False,
                        "id_executant": id_executant, "instance_id": instance_id,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue
                if action not in ("ponctuelle", "taux"):
                    await websocket.send_text(json.dumps({
                        "type": "regler_capture_instance_ack", "ok": False,
                        "id_executant": id_executant, "instance_id": instance_id,
                        "erreur": f"action '{action}' inconnue (attendu 'ponctuelle' ou 'taux').",
                    }))
                    continue
                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "regler_capture_instance",
                            "instance_id": instance_id,
                            "action": action,
                            "fps": message.get("fps", 0.0),
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info(
                        "regler_capture_instance : action=%r instance=%r -> '%s'",
                        action, instance_id, id_executant,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "regler_capture_instance_ack", "ok": True,
                        "id_executant": id_executant, "instance_id": instance_id,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission regler_capture_instance à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "regler_capture_instance_ack", "ok": False,
                        "id_executant": id_executant, "instance_id": instance_id,
                        "erreur": str(e),
                    }))

            elif type_message == "commande_instance":
                # PATCH B.4 (contrôle à distance réel, cf. cahier des
                # charges patchs.md) -- relais TEL QUEL d'une commande de
                # pilotage (clic/scroll/double-clic/saisie clavier) du
                # panneau de rendu réseau (FenetreRenduTaskReseau, cf.
                # AutoniaX.py) vers le sAutoniax ciblé. Même patron exact
                # que regler_capture_instance juste au-dessus (réservé au
                # rôle "pilote", résolution de l'exécutant cible via
                # registre, ack ok/erreur immédiat) -- SIMPLE RELAIS,
                # aucune interprétation de l'action ici : c'est le
                # sAutoniax qui sait, via son dispatcher déjà existant et
                # déjà fonctionnel (_executer_commande_camoufox, appelé
                # depuis _ecouter_serveur sur réception d'un message
                # "type": "command"), comment exécuter concrètement
                # l'action demandée sur la page Camoufox de CETTE
                # instance précise.
                #
                # "action"/"x"/"y"/etc. transportés tels quels par le
                # pilote (mêmes noms de champs que _executer_commande_
                # camoufox attend déjà : "click"/"scroll"/"type_text"/
                # "paste"/"mousemove", cf. AutoniaX.py) -- ce handler ne
                # valide QUE le routage (exécutant existant, rôle
                # autorisé), jamais le contenu de la commande elle-même
                # (délégué au sAutoniax, qui a déjà toute la logique de
                # validation par action).
                if connexion.role != "pilote":
                    logger.warning("commande_instance refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "commande_instance_ack", "ok": False,
                        "erreur": "Seul le pilote peut envoyer une commande de contrôle à distance.",
                    }))
                    continue
                id_executant = message.get("id_executant", "")
                instance_id = message.get("instance_id", "")
                requete_id = message.get("requete_id", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    await websocket.send_text(json.dumps({
                        "type": "commande_instance_ack", "ok": False,
                        "id_executant": id_executant, "instance_id": instance_id, "requete_id": requete_id,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue
                try:
                    COMMANDES_INSTANCE_EN_ATTENTE[requete_id] = id_connexion
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "command",
                            "instance_id": instance_id,
                            "requete_id": requete_id,
                            # Reprend tel quel le sous-dict "commande" fourni par
                            # le pilote (action + paramètres propres à cette
                            # action, ex. x/y/bouton pour "click") -- évite de
                            # lister ici chaque champ possible, un par action,
                            # ce que _executer_commande_camoufox fait déjà pour
                            # sa propre validation.
                            **message.get("commande", {}),
                        }))
                    logger.info(
                        "commande_instance : action=%r instance=%r -> '%s'",
                        message.get("commande", {}).get("action"), instance_id, id_executant,
                    )
                    await websocket.send_text(json.dumps({
                        "type": "commande_instance_ack", "ok": True,
                        "id_executant": id_executant, "instance_id": instance_id, "requete_id": requete_id,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission commande_instance à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "commande_instance_ack", "ok": False,
                        "id_executant": id_executant, "instance_id": instance_id, "requete_id": requete_id,
                        "erreur": str(e),
                    }))
                    COMMANDES_INSTANCE_EN_ATTENTE.pop(requete_id, None)

            elif type_message == "command_result":
                # PATCH B.4 (contrôle à distance réel, cf. cahier des
                # charges patchs.md) -- retour d'exécution exécutant ->
                # pilote. Contrairement à projet_distant_progression
                # juste en dessous, l'exécutant ne transmet PAS id_pilote
                # ici : "command"/"command_result" est le protocole
                # générique déjà utilisé par _executer_commande_camoufox
                # (cf. AutoniaX.py, ~L54654/55004/55165...), partagé avec
                # le serveur central EMBARQUÉ (srv_gerer_command_result)
                # qui n'en a jamais eu besoin -- lui connaît déjà le
                # pilote via sa connexion WebSocket directe. Ici, côté
                # serveurT, le routage passe donc par la corrélation
                # requete_id -> id_pilote enregistrée à l'envoi (cf.
                # COMMANDES_INSTANCE_EN_ATTENTE, handler commande_instance
                # ci-dessus) plutôt que par un champ du message lui-même.
                #
                # .pop() (pas .get()) : consomme l'entrée à la réception,
                # c'est le patron documenté sur COMMANDES_INSTANCE_EN_ATTENTE
                # (purge dès la réponse, pas de TTL séparé nécessaire).
                if connexion.role != "executant":
                    continue
                requete_id = message.get("requete_id", "")
                id_pilote = COMMANDES_INSTANCE_EN_ATTENTE.pop(requete_id, None)
                if id_pilote is None:
                    # Requête inconnue (déjà purgée, requete_id vide/absent
                    # côté sAutoniax, ou double réponse) -- pas d'erreur
                    # bloquante : on logue et on abandonne silencieusement,
                    # comme projet_distant_progression le fait déjà pour un
                    # id_pilote introuvable.
                    logger.warning(
                        "command_result : requete_id=%r sans corrélation en attente (perdu ou déjà routé)",
                        requete_id,
                    )
                    continue
                pilote_cible = registre.pilote_par_id(id_pilote)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning("command_result : pilote '%s' introuvable, réponse perdue", id_pilote)
                    continue
                try:
                    message_relais = dict(message)
                    message_relais["id_executant"] = connexion.nom
                    async with registre.verrou_pour(pilote_cible.websocket):
                        await pilote_cible.websocket.send_text(json.dumps(message_relais))
                except Exception:
                    logger.exception("Échec relais command_result vers pilote '%s'", id_pilote)

            elif type_message == "projet_distant_progression":
                # PATCH (Patch 4.4.b -- suivi temps réel des projets
                # distribués). Retour exécutant -> pilote CIBLÉ (celui qui
                # avait envoyé ce projet, id_pilote transmis par
                # l'exécutant) -- même relais ciblé par id_pilote que
                # retour_projet_execute_*/notebook_distant_resultat, aucune
                # logique métier ici : un message unique (pas en chunks),
                # relayé tel quel avec id_executant ajouté.
                if connexion.role != "executant":
                    continue
                id_pilote = message.get("id_pilote", "")
                pilote_cible = registre.pilote_par_id(id_pilote)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning("projet_distant_progression : pilote '%s' introuvable, message perdu", id_pilote)
                    continue
                try:
                    message_relais = dict(message)
                    message_relais["id_executant"] = connexion.nom
                    async with registre.verrou_pour(pilote_cible.websocket):
                        await pilote_cible.websocket.send_text(json.dumps(message_relais))
                except Exception:
                    logger.exception("Échec relais projet_distant_progression vers pilote '%s'", id_pilote)

            elif type_message == "demander_logs_executant":
                # PATCH (bouton "Copier tous les logs", source sAutoniax
                # -- demande explicite utilisateur : "Tous les sAutoniax
                # connectes"). Réservé au rôle "pilote". Simple relais
                # ciblé TEL QUEL vers UN sAutoniax précis (même patron que
                # regler_capture_instance ci-dessus) -- le pilote appelle
                # ce message une fois PAR sAutoniax connecté (boucle côté
                # AutoniaX.py sur registre.executants(), pas de diffusion
                # groupée ici : chaque sAutoniax répond à son propre
                # rythme, pas de agrégation côté serveur -- c'est mAutoniax
                # qui assemble les réponses "logs_executant" au fur et à
                # mesure qu'elles arrivent, cf. gestionnaire pilote dans
                # AutoniaX.py).
                if connexion.role != "pilote":
                    logger.warning("demander_logs_executant refusé (rôle=%r) id=%s", connexion.role, id_connexion)
                    continue
                id_executant = message.get("id_executant", "")
                cible = registre.executant_par_id(id_executant)
                if cible is None:
                    await websocket.send_text(json.dumps({
                        "type": "logs_executant", "ok": False,
                        "id_executant": id_executant,
                        "erreur": f"Exécutant '{id_executant}' introuvable ou déconnecté.",
                    }))
                    continue
                try:
                    async with registre.verrou_pour(cible.websocket):
                        await cible.websocket.send_text(json.dumps({
                            "type": "demander_logs_executant",
                            "id_pilote": (connexion.id_pilote_stable or id_connexion),
                        }))
                    logger.info("demander_logs_executant : -> '%s'", id_executant)
                except Exception as e:
                    logger.exception("Échec transmission demander_logs_executant à '%s'", id_executant)
                    await websocket.send_text(json.dumps({
                        "type": "logs_executant", "ok": False,
                        "id_executant": id_executant,
                        "erreur": str(e),
                    }))

            elif type_message == "logs_executant":
                # Réponse du sAutoniax à "demander_logs_executant"
                # ci-dessus -- même patron de relais ciblé par id_pilote
                # que projet_distant_progression/retour_projet_execute_* :
                # message unique (pas en chunks, cf. remarque sur la
                # taille potentielle plus bas côté AutoniaX.py), relayé
                # tel quel avec id_executant ajouté pour que mAutoniax
                # sache quel sAutoniax a répondu.
                if connexion.role != "executant":
                    continue
                id_pilote = message.get("id_pilote", "")
                pilote_cible = registre.pilote_par_id(id_pilote)
                if pilote_cible is None or pilote_cible.role != "pilote":
                    logger.warning("logs_executant : pilote '%s' introuvable, message perdu", id_pilote)
                    continue
                try:
                    message_relais = dict(message)
                    message_relais["id_executant"] = connexion.nom
                    async with registre.verrou_pour(pilote_cible.websocket):
                        await pilote_cible.websocket.send_text(json.dumps(message_relais))
                except Exception:
                    logger.exception("Échec relais logs_executant vers pilote '%s'", id_pilote)

            elif type_message == "api2api_enregistrer":
                # Un Task de type Api2Api (n'importe quel rôle -- pilote
                # OU exécutant, cf. spécification : "n'importe quel
                # sAutoniax ou mAutoniax") s'annonce disponible. Génère
                # un id_api2api propre (PAS id_connexion -- cf. docstring
                # REGISTRE_API2API : une même connexion pourrait en
                # théorie enregistrer plusieurs Task Api2Api successifs
                # au fil de sa vie). Statut initial "libre" -- réveille
                # aussitôt toute file d'attente existante (un client
                # bloqué sur Api2Api() peut désormais aboutir).
                id_api2api = uuid.uuid4().hex[:12]
                REGISTRE_API2API[id_api2api] = {
                    "id_connexion_fournisseur": id_connexion,
                    "statut": "libre",
                    "id_connexion_proprietaire": None,
                    "derniere_activite": time.monotonic(),
                }
                logger.info("api2api_enregistrer : id_api2api=%s fournisseur=%s (%s)", id_api2api, connexion.nom or id_connexion, connexion.role)
                await websocket.send_text(json.dumps({
                    "type": "api2api_enregistrer_ack", "ok": True, "id_api2api": id_api2api,
                    "requete_id": message.get("requete_id", ""),
                }))
                _api2api_reveiller_attente()

            elif type_message == "api2api_desenregistrer":
                # Arrêt PROPRE d'un Task Api2Api (contrairement à la
                # déconnexion brute, gérée par _api2api_desenregistrer_
                # fournisseur dans le finally de route_websocket) --
                # même effet final (l'entrée disparaît entièrement), État
                # explicite ici pour un cas normal (utilisateur arrête le
                # Task volontairement) plutôt qu'une coupure.
                #
                # GARDE-FOU (audit suite à un faux positif diagnostiqué
                # ailleurs, cf. AutoniaX.py/api2api_attendre_requete_bloquant) --
                # avant ce garde-fou, N'IMPORTE QUELLE connexion connaissant
                # un id_api2api pouvait le désenregistrer, même si elle
                # n'en était pas le fournisseur (aucune vérification
                # d'id_connexion). Le vrai bug reproduit était ailleurs
                # (côté client), mais ce trou reste un risque réel si un
                # futur appelant se trompait d'id_api2api -- corrigé ici en
                # ignorant toute tentative de désenregistrement par une
                # connexion qui n'est pas le fournisseur enregistré.
                id_api2api = message.get("id_api2api", "")
                entree = REGISTRE_API2API.get(id_api2api)
                if entree is not None and entree.get("id_connexion_fournisseur") != id_connexion:
                    logger.warning(
                        "api2api_desenregistrer refusé : id_connexion=%s a tenté de désenregistrer "
                        "id_api2api=%s, qui appartient à id_connexion_fournisseur=%s",
                        id_connexion, id_api2api, entree.get("id_connexion_fournisseur"),
                    )
                    await websocket.send_text(json.dumps({
                        "type": "api2api_desenregistrer_ack", "ok": False, "id_api2api": id_api2api,
                    }))
                    continue
                entree = REGISTRE_API2API.pop(id_api2api, None)
                if entree is not None:
                    logger.info("api2api_desenregistrer : id_api2api=%s", id_api2api)
                await websocket.send_text(json.dumps({
                    "type": "api2api_desenregistrer_ack", "ok": entree is not None, "id_api2api": id_api2api,
                }))

            elif type_message == "api2api_verrouiller":
                # Cherche un Api2Api LIBRE (cf. _api2api_libres, premier
                # trouvé par ordre d'enregistrement) et le verrouille
                # IMMÉDIATEMENT pour ce client si un existe -- sinon
                # inscrit ce client dans FILE_ATTENTE_API2API et attend
                # (bloquant CE handler, PAS toute la boucle réception de
                # route_websocket -- une coroutine asyncio.sleep/wait
                # n'empêche pas les autres messages/connexions d'être
                # traités entre-temps) jusqu'à ce qu'un Api2Api se libère
                # OU que le timeout demandé expire (cf. spécification :
                # "Attendre (bloquant) qu'un devienne libre, avec un
                # timeout"). requete_id transporté tel quel dans la
                # réponse : permet au CLIENT de corréler cette réponse
                # tardive avec l'appel Api2Api() qui l'a déclenchée (le
                # client peut avoir plusieurs appels Api2Api() en attente
                # simultanée dans des threads différents).
                requete_id = message.get("requete_id", "")
                timeout_s = float(message.get("timeout_s", 30.0))
                deadline = time.monotonic() + timeout_s

                id_api2api_obtenu = None
                while True:
                    candidats = _api2api_libres()
                    if candidats:
                        id_api2api_obtenu = candidats[0]
                        REGISTRE_API2API[id_api2api_obtenu]["statut"] = "verrouille"
                        REGISTRE_API2API[id_api2api_obtenu]["id_connexion_proprietaire"] = id_connexion
                        REGISTRE_API2API[id_api2api_obtenu]["derniere_activite"] = time.monotonic()
                        break
                    restant = deadline - time.monotonic()
                    if restant <= 0:
                        break
                    event_attente = FILE_ATTENTE_API2API.setdefault(id_connexion, asyncio.Event())
                    event_attente.clear()
                    try:
                        await asyncio.wait_for(event_attente.wait(), timeout=restant)
                    except asyncio.TimeoutError:
                        break
                    # Réveillé (un Api2Api vient potentiellement de se
                    # libérer) -- reboucle pour retenter _api2api_libres()
                    # immédiatement ; si un autre client a gagné la
                    # course entre-temps, la boucle attend simplement à
                    # nouveau sur le restant du délai.
                FILE_ATTENTE_API2API.pop(id_connexion, None)

                if id_api2api_obtenu is not None:
                    logger.info("api2api_verrouiller : id_api2api=%s -> client=%s", id_api2api_obtenu, connexion.nom or id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "api2api_verrouiller_ack", "ok": True,
                        "requete_id": requete_id, "id_api2api": id_api2api_obtenu,
                    }))
                else:
                    logger.info("api2api_verrouiller : timeout (%.0fs) sans Api2Api libre, client=%s", timeout_s, connexion.nom or id_connexion)
                    await websocket.send_text(json.dumps({
                        "type": "api2api_verrouiller_ack", "ok": False,
                        "requete_id": requete_id,
                        "erreur": f"Aucun Task Api2Api libre après {timeout_s:.0f}s d'attente.",
                    }))

            elif type_message == "api2api_liberer":
                # Libération EXPLICITE (Api2ApiTask.free() côté script)
                # -- réservée au propriétaire actuel du verrou : une
                # tentative de libérer un Api2Api qu'on ne possède pas
                # (déjà libéré, jamais verrouillé par ce client, ou
                # verrouillé par un AUTRE client) est un no-op silencieux
                # côté effet (rien à corrompre), mais renvoie ok=False
                # pour que l'appelant puisse le détecter s'il le souhaite.
                id_api2api = message.get("id_api2api", "")
                entree = REGISTRE_API2API.get(id_api2api)
                if entree is None or entree["id_connexion_proprietaire"] != id_connexion:
                    await websocket.send_text(json.dumps({
                        "type": "api2api_liberer_ack", "ok": False, "id_api2api": id_api2api,
                        "requete_id": message.get("requete_id", ""),
                        "erreur": "Ce Task Api2Api n'est pas verrouillé par cette connexion (déjà libéré, ou jamais possédé).",
                    }))
                    continue
                _api2api_liberer_entree(id_api2api)
                logger.info("api2api_liberer : id_api2api=%s (client=%s)", id_api2api, connexion.nom or id_connexion)
                await websocket.send_text(json.dumps({
                    "type": "api2api_liberer_ack", "ok": True, "id_api2api": id_api2api,
                    "requete_id": message.get("requete_id", ""),
                }))

            elif type_message == "api2api_reset_admin":
                # OUTIL DE DÉVELOPPEMENT (retour utilisateur : "j'ai
                # besoin d'une commande spéciale qui va réinitialiser le
                # registre, mettre tout le monde à free" -> "vider
                # complètement, donc réinitialiser") -- appelable depuis
                # une cellule de Task/notebook via reinitialiser_
                # registre_api2api() (cf. _construire_espace_noms_
                # api2api côté AutoniaX.py), PAS un endpoint HTTP séparé
                # ni une commande console serveur -- décision explicite
                # utilisateur : "appelable dans mon notebook TaskScript
                # editor". AUCUNE vérification de permission/rôle ici
                # (cf. docstring de _api2api_reset_admin) : n'importe
                # quelle connexion peut déclencher ce reset global, à
                # dessein réservé au développement.
                nombre_retires = _api2api_reset_admin()
                await websocket.send_text(json.dumps({
                    "type": "api2api_reset_admin_ack", "ok": True,
                    "requete_id": message.get("requete_id", ""),
                    "nombre_retires": nombre_retires,
                }))

            elif type_message == "api2api_requete":
                # Requête du CLIENT (Api2ApiTask.request(...) côté
                # script) vers le Task fournisseur qu'il a verrouillé --
                # même patron de corrélation EXACT que commande_instance/
                # command_result ci-dessus (REQUETES_API2API_EN_ATTENTE
                # au lieu de COMMANDES_INSTANCE_EN_ATTENTE), sans
                # restriction de rôle (contrairement à commande_instance,
                # réservé au pilote -- ici les deux côtés peuvent être
                # pilote OU exécutant, cf. spécification). "donnees"
                # transporté tel quel (liste de {"nom": str, "contenu_b64":
                # str} -- cf. AutoniaX.py, Api2Api.request : UN SEUL
                # paquet réseau groupé même pour plusieurs fichiers, cf.
                # décision explicite utilisateur "sa seras trasformer en
                # un seul paquet pour lotimisation").
                id_api2api = message.get("id_api2api", "")
                requete_id = message.get("requete_id", "")
                entree = REGISTRE_API2API.get(id_api2api)
                if entree is None:
                    await websocket.send_text(json.dumps({
                        "type": "api2api_requete_ack", "ok": False, "requete_id": requete_id,
                        "erreur": f"Task Api2Api '{id_api2api}' introuvable (désenregistré ou jamais existé).",
                    }))
                    continue
                if entree["id_connexion_proprietaire"] != id_connexion:
                    await websocket.send_text(json.dumps({
                        "type": "api2api_requete_ack", "ok": False, "requete_id": requete_id,
                        "erreur": "Ce Task Api2Api n'est pas verrouillé par cette connexion.",
                    }))
                    continue
                fournisseur = registre._par_id_connexion.get(entree["id_connexion_fournisseur"])
                if fournisseur is None:
                    # Fournisseur déconnecté sans que le nettoyage n'ait
                    # encore retiré cette entrée (ordre d'exécution
                    # improbable mais possible) -- traité comme
                    # introuvable plutôt que de relayer vers une
                    # connexion morte.
                    REGISTRE_API2API.pop(id_api2api, None)
                    await websocket.send_text(json.dumps({
                        "type": "api2api_requete_ack", "ok": False, "requete_id": requete_id,
                        "erreur": "Le Task Api2Api fournisseur est déconnecté.",
                    }))
                    continue
                try:
                    REQUETES_API2API_EN_ATTENTE[requete_id] = id_connexion
                    entree["derniere_activite"] = time.monotonic()  # cf. watchdog : réinitialise le timer d'inactivité
                    async with registre.verrou_pour(fournisseur.websocket):
                        await fournisseur.websocket.send_text(json.dumps({
                            "type": "api2api_requete_recue",
                            "id_api2api": id_api2api,
                            "requete_id": requete_id,
                            "donnees": message.get("donnees", []),
                        }))
                    logger.info("api2api_requete : id_api2api=%s requete_id=%s -> fournisseur=%s", id_api2api, requete_id, fournisseur.nom or entree["id_connexion_fournisseur"])
                    await websocket.send_text(json.dumps({
                        "type": "api2api_requete_ack", "ok": True, "requete_id": requete_id,
                    }))
                except Exception as e:
                    logger.exception("Échec transmission api2api_requete (id_api2api=%s)", id_api2api)
                    REQUETES_API2API_EN_ATTENTE.pop(requete_id, None)
                    await websocket.send_text(json.dumps({
                        "type": "api2api_requete_ack", "ok": False, "requete_id": requete_id, "erreur": str(e),
                    }))

            elif type_message == "api2api_reponse":
                # Réponse du FOURNISSEUR (req.repondre(...) côté script)
                # -- routée vers le client via REQUETES_API2API_EN_ATTENTE
                # (corrélation posée à l'envoi de api2api_requete
                # ci-dessus), même patron .pop()/purge immédiate que
                # command_result.
                requete_id = message.get("requete_id", "")
                id_client = REQUETES_API2API_EN_ATTENTE.pop(requete_id, None)
                if id_client is None:
                    logger.warning("api2api_reponse : requete_id=%r sans corrélation en attente (perdu ou déjà routé)", requete_id)
                    continue
                client_cible = registre._par_id_connexion.get(id_client)
                if client_cible is None:
                    logger.warning("api2api_reponse : client '%s' introuvable, réponse perdue", id_client)
                    continue
                try:
                    async with registre.verrou_pour(client_cible.websocket):
                        await client_cible.websocket.send_text(json.dumps({
                            "type": "api2api_reponse",
                            "requete_id": requete_id,
                            "ok": message.get("ok", True),
                            "donnees": message.get("donnees", []),
                            "erreur": message.get("erreur"),
                        }))
                except Exception:
                    logger.exception("Échec relais api2api_reponse vers client '%s'", id_client)

            else:
                logger.warning("Type de message inconnu (Étape 0, seul 'register' est géré) : %r", type_message)

    except WebSocketDisconnect:
        pass
    finally:
        etait_executant = connexion.role == "executant"
        registre.retirer(id_connexion)
        # PATCH -- nettoie tout upload de profil laissé en suspens si la
        # connexion tombe en plein milieu d'un envoi (client fermé,
        # coupure réseau...), pour ne jamais laisser un .zip partiel
        # orphelin sur le disque Render.
        if connexion.upload_profil is not None:
            connexion.upload_profil.nettoyer()
        # RETRAIT (migration "Mettre à jour" vers Drive direct) : le
        # nettoyage à la déconnexion de connexion.upload_app/
        # upload_service_api/upload_project_json a été retiré en même
        # temps que ces champs (cf. __init__ de Connexion) -- plus aucune
        # accumulation de fichier en vol sur cette connexion pour ces
        # flux, donc plus rien à nettoyer ici pour eux.
        # PATCH téléchargement -- rien à nettoyer sur disque (le
        # contenu est gardé en mémoire pure, cf. TelechargementFichierEnCours),
        # juste s'assurer que la référence ne traîne pas inutilement.
        connexion.telechargement_en_cours = None
        # Api2Api -- deux nettoyages DISTINCTS et indépendants (une même
        # connexion peut en théorie cumuler les deux rôles au fil de sa
        # vie, cf. docstrings respectives) : tout Task Api2Api que CETTE
        # connexion fournissait disparaît entièrement du registre, ET
        # tout verrou Api2Api que CETTE connexion possédait en tant que
        # client est libéré (le Task fournisseur, lui, reste disponible
        # pour un prochain client).
        _api2api_desenregistrer_fournisseur(id_connexion)
        _api2api_liberer_si_proprietaire(id_connexion)
        FILE_ATTENTE_API2API.pop(id_connexion, None)
        logger.info("déconnexion : %s (%s) id=%s", connexion.nom, connexion.role, id_connexion)
        if etait_executant:
            await diffuser_liste_executants()


# ---------------------------------------------------------------------------
# AJOUT (SPEC_proxy_natif_tunnel.md, section 8 -- relais pur du tunnel
# proxy natif) : deuxième route WebSocket, /ws_tunnel, en parallèle de
# /ws ci-dessus. Aucune logique métier AutoniaX ici, cf. principe déjà
# énoncé en tête de ce fichier -- uniquement du relais binaire, avec un
# seul point de "logique" toléré explicitement par la spec (section 8,
# dernier paragraphe) : le remappage de stream_id par _RemappeurStreamId
# ci-dessous, nécessaire pour qu'un même pilote puisse distinguer les
# flux ouverts par plusieurs sAutoniaX simultanés sans collision d'id
# (chaque sAutoniaX génère ses stream_id indépendamment, à partir de 1).
#
# Format de trame IDENTIQUE (dupliqué volontairement, cf. section 2 :
# "les deux fichiers restent des projets séparés") à celui d'AutoniaX.py
# (_construire_trame_tunnel/_lire_entete_trame_tunnel) :
#   [1 octet type_trame][4 octets big-endian stream_id][payload]
# ---------------------------------------------------------------------------

TYPE_TRAME_OPEN = 0x01
TYPE_TRAME_OPEN_OK = 0x02
TYPE_TRAME_OPEN_FAIL = 0x03
TYPE_TRAME_DATA = 0x04
TYPE_TRAME_CLOSE = 0x05
# AJOUT (revue de bout en bout /ws_tunnel) -- mêmes valeurs EXACTES que
# TYPE_TRAME_PING/TYPE_TRAME_PONG côté AutoniaX.py (cf. RelaisProxyLocal/
# ServiceSortieProxy, docstring de TYPE_TRAME_PING) : les deux clients
# (sAutoniaX et mAutoniaX) émettent un PING binaire périodique sur ce
# canal puisque le ping natif websockets est désactivé des deux côtés
# (cf. ws_ping_interval=None plus bas, et ping_interval=None côté
# websockets.connect) -- le serveur, seul point de passage commun aux
# deux, est le mieux placé pour répondre PONG et détecter un silence
# prolongé (cf. SEUIL_SILENCE_TUNNEL_SECONDES ci-dessous).
TYPE_TRAME_PING = 0x06
TYPE_TRAME_PONG = 0x07
# REVU (cf. AutoniaX.py, docstring de TYPE_TRAME_HORLOGE_DEMANDE --
# "pourquoi mautoniax ne donne pas lui meme la date directement") --
# BUGFIX : la version initiale envoyait HORLOGE de façon spontanée, une
# seule fois, à la connexion du tunnel pilote -- cassé dès que ce tunnel
# existait déjà avant la connexion d'un nouvel exécutant (jamais
# rejouée pour lui). Design demande/réponse à la place : HORLOGE_DEMANDE
# (exécutant -> pilote, un seul destinataire) puis HORLOGE (pilote ->
# TOUS les exécutants de ce pilote, cf. RegistreTunnel.executants_de --
# par simplicité de relais, pas parce que la réponse concerne tout le
# monde ; chaque exécutant ignore une HORLOGE qui ne répond à aucune de
# ses propres demandes en attente, cf. AutoniaX.py côté RelaisProxyLocal).
# Aucune des deux trames n'a de stream_id applicatif réel
# (STREAM_ID_HEARTBEAT_TUNNEL, comme PING/PONG) -- interceptées AVANT le
# bloc de remappage de stream_id (cf. route_websocket_tunnel ci-dessous).
TYPE_TRAME_HORLOGE_DEMANDE = 0x09
TYPE_TRAME_HORLOGE = 0x08
STREAM_ID_HEARTBEAT_TUNNEL = 0  # convention -- jamais un vrai stream_id (les compteurs démarrent à 1, cf. _RemappeurStreamId/RelaisProxyLocal._prochain_stream_id)
TAILLE_ENTETE_TRAME = 5  # 1 octet type + 4 octets stream_id big-endian

# AJOUT -- délai de silence toléré sur /ws_tunnel avant de considérer une
# connexion (pilote OU exécutant) comme morte et de la fermer nous-mêmes
# (déclenche le même nettoyage que route_websocket_tunnel, finally).
# Alignée sur DELAI_HEARTBEAT_TUNNEL_SECONDES = 15.0 côté AutoniaX.py
# (RelaisProxyLocal/ServiceSortieProxy._boucle_heartbeat_tunnel) : un
# PING toutes les 15s des deux côtés, donc un silence de plus de 35s
# (plus de 2 PING manqués) signale une connexion morte plutôt qu'un
# simple ralentissement ponctuel -- même marge que SEUIL_SILENCE_
# SUSPECT_SECONDES déjà utilisé pour le watchdog du canal /ws JSON, pour
# rester cohérent avec le reste du fichier plutôt que d'inventer une
# nouvelle valeur arbitraire.
SEUIL_SILENCE_TUNNEL_SECONDES = 35.0


def _construire_trame(type_trame: int, stream_id: int, payload: bytes = b"") -> bytes:
    return bytes([type_trame]) + stream_id.to_bytes(4, "big") + payload


def _lire_entete_trame(trame: bytes) -> tuple[int, int, bytes]:
    type_trame = trame[0]
    stream_id = int.from_bytes(trame[1:5], "big")
    payload = trame[TAILLE_ENTETE_TRAME:]
    return type_trame, stream_id, payload


class _RemappeurStreamId:
    """AJOUT (section 8, dernier paragraphe -- "le seul point de logique
    ajouté côté serveur : un remappage d'identifiant, pas une inspection
    du contenu"). Un sAutoniaX numérote ses propres stream_id à partir de
    1 (cf. AutoniaX.py, RelaisProxyLocal._prochain_stream_id) --
    INDÉPENDAMMENT de tout autre sAutoniaX connecté au même pilote. Sans
    remappage, deux sAutoniaX du même pilote pourraient tous les deux
    ouvrir un "stream_id=1" en même temps : le pilote (un seul
    ServiceSortieProxy, cf. section 7) ne pourrait alors plus savoir à
    quel sAutoniaX renvoyer un DATA/CLOSE entrant pour ce stream_id.

    Une instance par pilote_tunnel (créée dans RegistreTunnel.ajouter_
    pilote, cf. plus bas), qui tient la correspondance dans les DEUX
    sens :
      - global -> (id_executant, stream_id_local) : pour router un
        paquet ENTRANT côté pilote (DATA/CLOSE) vers le bon exécutant et
        son stream_id d'origine.
      - (id_executant, stream_id_local) -> global : pour traduire un
        paquet SORTANT du pilote (OPEN_OK/OPEN_FAIL/DATA/CLOSE) vers le
        stream_id que CET exécutant précis reconnaîtra comme le sien.

    Le pilote ne voit donc QUE des stream_id globaux, jamais les
    stream_id locaux des exécutants -- symétrique de ce que fait déjà
    Registre pour les identités (nom d'exécutant vs id_connexion), même
    principe appliqué ici à un identifiant de flux plutôt qu'à une
    connexion entière."""

    def __init__(self):
        self._prochain_id_global = 1
        self._global_vers_local: dict[int, tuple[str, int]] = {}
        self._local_vers_global: dict[tuple[str, int], int] = {}

    def vers_global(self, id_executant: str, stream_id_local: int) -> int:
        """Appelé côté OPEN reçu d'un exécutant -- alloue (ou retrouve,
        si déjà connu, cf. tous les autres types de trame du même flux
        qui réutilisent ce mapping sans en recréer un nouveau) un
        stream_id global unique pour ce couple (id_executant, local)."""
        cle_locale = (id_executant, stream_id_local)
        global_existant = self._local_vers_global.get(cle_locale)
        if global_existant is not None:
            return global_existant
        id_global = self._prochain_id_global
        self._prochain_id_global += 1
        self._global_vers_local[id_global] = cle_locale
        self._local_vers_global[cle_locale] = id_global
        return id_global

    def vers_local(self, stream_id_global: int) -> Optional[tuple[str, int]]:
        """Appelé côté trame reçue du pilote (OPEN_OK/OPEN_FAIL/DATA/
        CLOSE) -- retrouve à quel exécutant et quel stream_id LOCAL de
        cet exécutant ce stream_id global correspond. None si inconnu
        (flux déjà fermé/nettoyé, ou pilote désynchronisé -- ignoré par
        l'appelant plutôt que de lever, cf. route_websocket_tunnel)."""
        return self._global_vers_local.get(stream_id_global)

    def oublier(self, stream_id_global: int):
        """Nettoyage d'un flux terminé (CLOSE dans un sens ou dans
        l'autre) -- évite une fuite mémoire sur un tunnel de longue
        durée avec beaucoup de connexions TCP ouvertes/fermées."""
        cle_locale = self._global_vers_local.pop(stream_id_global, None)
        if cle_locale is not None:
            self._local_vers_global.pop(cle_locale, None)

    def oublier_executant(self, id_executant: str) -> list[int]:
        """Appelé à la déconnexion d'un exécutant (section 8, dernier
        paragraphe : "le serveur envoie CLOSE pour tous les stream_id
        actifs de cette paire à l'autre bout") -- retire tous les flux de
        CET exécutant du remappage et retourne la liste des stream_id
        GLOBAUX concernés, pour que l'appelant puisse notifier le pilote
        (un CLOSE par stream_id global encore ouvert)."""
        ids_globaux = [
            id_global for id_global, (nom, _local) in self._global_vers_local.items()
            if nom == id_executant
        ]
        for id_global in ids_globaux:
            self.oublier(id_global)
        return ids_globaux

    def flux_ouverts(self) -> list[tuple[int, str, int]]:
        """Instantané (id_global, id_executant, stream_id_local) de tous
        les flux actuellement ouverts pour ce pilote -- utilisé à la
        déconnexion DU PILOTE (section 8, dernier paragraphe) pour
        notifier CHAQUE exécutant concerné, un par un."""
        return [
            (id_global, nom_executant, stream_id_local)
            for id_global, (nom_executant, stream_id_local) in self._global_vers_local.items()
        ]

    def id_global_existant(self, id_executant: str, stream_id_local: int) -> Optional[int]:
        """Symétrique en lecture seule de vers_global ci-dessus, SANS en
        créer un nouveau si absent (utilisé pour DATA/CLOSE, qui doivent
        retrouver un mapping déjà créé par un OPEN antérieur -- jamais en
        créer un nouveau à cette occasion, contrairement à vers_global)."""
        return self._local_vers_global.get((id_executant, stream_id_local))


class RegistreTunnel:
    """AJOUT (section 8) -- registre EN MÉMOIRE, séparé et indépendant du
    Registre existant (cf. classe Registre plus haut, canal /ws JSON) :
    une paire (pilote, exécutant) qui tunnelise n'a pas besoin d'être déjà
    enregistrée sur /ws pour ouvrir /ws_tunnel (les deux connexions sont
    indépendantes l'une de l'autre, cf. section 3 : "une deuxième
    connexion WebSocket, binaire, dédiée"), même si en pratique un
    exécutant/pilote qui ouvre un tunnel a nécessairement déjà une
    connexion /ws active par ailleurs (cf. AutoniaX.py, RelaisProxyLocal/
    ServiceSortieProxy, tous deux construits à partir d'un client_t/
    ClientServeurT déjà connecté).

    Cf. section 4 : "un seul mAutoniaX par id_pilote_stable ; plusieurs
    sAutoniaX (exécutants) peuvent tunneliser pour le même pilote en même
    temps" -- d'où pilotes_tunnel (1 websocket par id_pilote_stable) et
    executants_tunnel (1 websocket par (id_pilote_stable, id_executant)).

    AJOUT (revue de bout en bout) -- verrou_pour(websocket) : plusieurs
    routes route_websocket_tunnel tournent en tâches asyncio INDÉPENDANTES
    (une par connexion), et RIEN ne les sérialise entre elles -- si deux
    exécutants du même pilote envoient chacun un DATA en même temps, on
    obtient deux `await pilote_ws.send_bytes(...)` concurrents sur le
    MÊME objet WebSocket, depuis deux tâches différentes (idem dans
    l'autre sens : le pilote qui écrit à un exécutant en même temps que
    le finally de déconnexion d'un AUTRE exécutant écrit au même pilote
    ailleurs -- mais ça ne concerne jamais le MÊME websocket exécutant,
    donc pas de conflit dans ce cas précis). Starlette ne garantit PAS la
    sécurité des écritures concurrentes sur une même connexion (cf. issue
    encode/starlette#1369, AssertionError sur application_state observée
    en usage concurrent réel) -- même famille de bug que "concurrent
    write to websocket connection" bien connue dans d'autres écosystèmes
    WebSocket (ex. Gorilla en Go, qui n'autorise explicitement qu'un seul
    writer actif). Un `asyncio.Lock` PAR OBJET WebSocket (indexé par
    id(websocket), pas par id_pilote_stable/id_executant seuls -- une
    reconnexion crée un nouvel objet WebSocket, donc un nouveau verrou,
    jamais un verrou périmé partagé avec une connexion déjà fermée)
    sérialise tous les envois vers CE websocket précis, peu importe
    quelle tâche les émet. Nettoyé explicitement à la déconnexion
    (retirer_pilote/retirer_executant) pour ne jamais laisser grossir
    _verrous_par_websocket indéfiniment sur la durée de vie du process."""

    def __init__(self):
        self.pilotes_tunnel: dict[str, WebSocket] = {}
        self.executants_tunnel: dict[tuple[str, str], WebSocket] = {}
        # Un _RemappeurStreamId PAR pilote (cf. sa docstring) -- deux
        # pilotes différents ne doivent jamais partager le même espace de
        # stream_id globaux, chacun a le sien, réinitialisé à la première
        # connexion de ce pilote (cf. ajouter_pilote).
        self._remappeurs_par_pilote: dict[str, _RemappeurStreamId] = {}
        # AJOUT -- cf. docstring de classe : un verrou par websocket réel,
        # pour sérialiser les écritures concurrentes venant de tâches
        # différentes.
        self._verrous_par_websocket: dict[int, asyncio.Lock] = {}

    def ajouter_pilote(self, id_pilote_stable: str, websocket: WebSocket):
        # Même logique de remplacement propre qu'un register classique
        # (cf. Registre.ajouter, cas role == "pilote") -- une reconnexion
        # du même pilote remplace l'ancienne entrée plutôt que d'ouvrir
        # une deuxième route pour le même id_pilote_stable.
        self.pilotes_tunnel[id_pilote_stable] = websocket
        self._remappeurs_par_pilote.setdefault(id_pilote_stable, _RemappeurStreamId())
        self._verrous_par_websocket.setdefault(id(websocket), asyncio.Lock())

    def ajouter_executant(self, id_pilote_stable: str, id_executant: str, websocket: WebSocket):
        self.executants_tunnel[(id_pilote_stable, id_executant)] = websocket
        self._verrous_par_websocket.setdefault(id(websocket), asyncio.Lock())

    def retirer_pilote(self, id_pilote_stable: str):
        websocket = self.pilotes_tunnel.pop(id_pilote_stable, None)
        self._remappeurs_par_pilote.pop(id_pilote_stable, None)
        if websocket is not None:
            self._verrous_par_websocket.pop(id(websocket), None)

    def retirer_executant(self, id_pilote_stable: str, id_executant: str):
        websocket = self.executants_tunnel.pop((id_pilote_stable, id_executant), None)
        if websocket is not None:
            self._verrous_par_websocket.pop(id(websocket), None)

    def executants_de(self, id_pilote_stable: str) -> list[tuple[str, WebSocket]]:
        """Tous les (id_executant, websocket) actuellement tunnelisés
        pour ce pilote -- utilisé à la déconnexion DU PILOTE (section 8,
        dernier paragraphe) pour notifier tous ses exécutants d'un coup."""
        return [
            (id_exec, ws) for (id_pilote, id_exec), ws in self.executants_tunnel.items()
            if id_pilote == id_pilote_stable
        ]

    def remappeur_de(self, id_pilote_stable: str) -> Optional[_RemappeurStreamId]:
        return self._remappeurs_par_pilote.get(id_pilote_stable)

    def verrou_pour(self, websocket: WebSocket) -> asyncio.Lock:
        """Verrou dédié à CE websocket précis -- cf. docstring de classe.
        setdefault ici aussi (pas seulement dans ajouter_pilote/
        ajouter_executant) en filet de sécurité : le verrou doit exister
        même si un appelant l'utilise avant l'enregistrement complet, ou
        pour un websocket qui n'est plus dans le registre au moment de
        l'appel (ex. envoi de CLOSE final pendant que retirer_* vient de
        tourner) -- un Lock frais et non partagé dans ce cas résiduel
        reste toujours correct (au pire, pas de sérialisation utile pour
        un envoi isolé déjà en toute fin de vie de la connexion, jamais
        un verrou incorrect)."""
        return self._verrous_par_websocket.setdefault(id(websocket), asyncio.Lock())


registre_tunnel = RegistreTunnel()


@app.websocket("/ws_tunnel")
async def route_websocket_tunnel(websocket: WebSocket):
    """AJOUT (section 8) -- relais pur, symétrique de route_websocket
    ci-dessus mais pour le canal binaire du proxy natif. Message
    d'annonce JSON initial (seule exception texte de ce canal, cf.
    section 8 : "juste pour l'identification, avant de basculer en
    binaire pur"), puis boucle de relais binaire jusqu'à déconnexion."""
    await websocket.accept()

    try:
        texte_annonce = await websocket.receive_text()
        annonce = json.loads(texte_annonce)
    except Exception:
        logger.warning("/ws_tunnel : annonce initiale invalide ou absente, connexion fermée.")
        try:
            await websocket.close()
        except Exception:
            pass
        return

    role = annonce.get("role")
    id_pilote_stable = annonce.get("id_pilote_stable", "")
    id_executant = annonce.get("id_executant", "")

    if role not in ("pilote", "executant") or not id_pilote_stable:
        logger.warning("/ws_tunnel : annonce refusée (role=%r, id_pilote_stable=%r).", role, id_pilote_stable)
        try:
            await websocket.close()
        except Exception:
            pass
        return
    if role == "executant" and not id_executant:
        logger.warning("/ws_tunnel : annonce exécutant refusée, id_executant manquant.")
        try:
            await websocket.close()
        except Exception:
            pass
        return

    if role == "pilote":
        registre_tunnel.ajouter_pilote(id_pilote_stable, websocket)
        logger.info("/ws_tunnel : pilote connecté (id_pilote_stable=%s).", id_pilote_stable)
    else:
        registre_tunnel.ajouter_executant(id_pilote_stable, id_executant, websocket)
        logger.info("/ws_tunnel : exécutant connecté (id_pilote_stable=%s, id_executant=%s).", id_pilote_stable, id_executant)

    try:
        while True:
            # AJOUT (revue de bout en bout) -- asyncio.wait_for() plutôt
            # qu'un watchdog séparé façon _boucle_watchdog_executants (cf.
            # /ws) : ici une seule route porte tout le flux de réception
            # d'une connexion donnée, pas besoin d'un registre externe de
            # "dernière activité" -- un simple timeout sur l'attente
            # suffit à détecter un silence, PING compris (cf. plus bas :
            # tout PING reçu réinitialise ce même receive_bytes()).
            try:
                trame = await asyncio.wait_for(websocket.receive_bytes(), timeout=SEUIL_SILENCE_TUNNEL_SECONDES)
            except asyncio.TimeoutError:
                logger.warning(
                    "/ws_tunnel : silence de plus de %.0fs (role=%s, id_pilote_stable=%s%s), connexion fermée.",
                    SEUIL_SILENCE_TUNNEL_SECONDES, role, id_pilote_stable,
                    f", id_executant={id_executant}" if role == "executant" else "",
                )
                # Contrairement à WebSocketDisconnect (où le TCP est déjà
                # mort côté client), ici la connexion peut être encore
                # techniquement ouverte côté serveur -- on la ferme nous-
                # mêmes avant le nettoyage du registre (finally, plus
                # bas) pour ne pas laisser un socket serveur pendre.
                try:
                    await websocket.close()
                except Exception:
                    pass
                break
            if len(trame) < TAILLE_ENTETE_TRAME:
                continue
            type_trame, stream_id, payload = _lire_entete_trame(trame)

            if type_trame == TYPE_TRAME_PING:
                # Réponse immédiate, jamais relayée à l'autre bout (c'est
                # un message serveur<->client, pas une trame applicative
                # OPEN/DATA/CLOSE) -- cf. AutoniaX.py, RelaisProxyLocal/
                # ServiceSortieProxy._boucle_reception_tunnel, qui traite
                # le PONG au passage sans action (la seule preuve de vie
                # utile est déjà d'avoir reçu N'IMPORTE QUELLE trame ici).
                # Verrou (cf. RegistreTunnel.verrou_pour) : cette écriture
                # n'est normalement jamais concurrente avec elle-même
                # (une seule boucle de réception par connexion), mais
                # protégée par cohérence avec les 3 sites d'écriture
                # ci-dessous, qui EUX le sont réellement.
                try:
                    async with registre_tunnel.verrou_pour(websocket):
                        await websocket.send_bytes(_construire_trame(TYPE_TRAME_PONG, STREAM_ID_HEARTBEAT_TUNNEL))
                except Exception:
                    pass
                continue

            if type_trame == TYPE_TRAME_HORLOGE_DEMANDE:
                # REVU (cf. docstring de TYPE_TRAME_HORLOGE_DEMANDE) --
                # seul un exécutant émet cette trame (cf. AutoniaX.py,
                # RelaisProxyLocal._assurer_connexion_tunnel) ; un pilote
                # qui l'enverrait par erreur est ignoré plutôt que de
                # risquer un relais vers nulle part (un pilote n'a pas
                # de "pilote à lui" à qui demander).
                if role != "executant":
                    continue
                # Pas de remappage de stream_id (cf. STREAM_ID_HEARTBEAT_
                # TUNNEL, jamais un vrai flux) -- relayée telle quelle au
                # SEUL pilote de cet exécutant (symétrique du relais
                # exécutant->pilote normal, mais sans passer par le
                # remappeur puisqu'il n'y a rien à retraduire ici).
                pilote_ws = registre_tunnel.pilotes_tunnel.get(id_pilote_stable)
                if pilote_ws is None:
                    # Pilote pas (ou plus) connecté -- rien à relayer,
                    # cf. même raisonnement que le relais exécutant->
                    # pilote normal juste plus bas : le sAutoniax
                    # demandeur timeoutera proprement côté obtenir_
                    # horloge_mautoniax, aucune action nécessaire ici.
                    continue
                try:
                    async with registre_tunnel.verrou_pour(pilote_ws):
                        await pilote_ws.send_bytes(_construire_trame(TYPE_TRAME_HORLOGE_DEMANDE, STREAM_ID_HEARTBEAT_TUNNEL))
                except Exception as e:
                    logger.warning("/ws_tunnel : relais HORLOGE_DEMANDE exécutant->pilote échoué (%r).", e)
                continue

            if type_trame == TYPE_TRAME_HORLOGE:
                # REVU (cf. docstring de TYPE_TRAME_HORLOGE_DEMANDE) --
                # seul le pilote émet cette trame, TOUJOURS en réponse à
                # une TYPE_TRAME_HORLOGE_DEMANDE reçue (cf. AutoniaX.py,
                # ServiceSortieProxy._boucle_reception_tunnel) ; un
                # exécutant qui l'enverrait par erreur est ignoré plutôt
                # que de risquer de relayer une fausse heure aux autres
                # exécutants de ce pilote.
                if role != "pilote":
                    continue
                # Pas de remappage de stream_id ici (cf. STREAM_ID_
                # HEARTBEAT_TUNNEL, jamais un vrai flux) -- diffusée à
                # TOUS les exécutants actuellement connectés pour ce
                # pilote plutôt qu'au seul demandeur : le serveur ne
                # fait aucune corrélation demande/réponse (HORLOGE_
                # DEMANDE n'emporte aucun identifiant permettant de
                # savoir QUEL exécutant a demandé, cf. son payload vide)
                # -- chaque exécutant reçoit donc potentiellement une
                # HORLOGE qu'il n'a pas lui-même demandée, mais c'est
                # sans conséquence : c'est la même heure du même
                # mAutoniax pour tout le monde, et un exécutant qui n'a
                # rien demandé se contente de mettre à jour sa valeur
                # stockée (cf. AutoniaX.py, RelaisProxyLocal._boucle_
                # reception_tunnel) sans effet de bord.
                for _id_executant, executant_ws in registre_tunnel.executants_de(id_pilote_stable):
                    try:
                        async with registre_tunnel.verrou_pour(executant_ws):
                            await executant_ws.send_bytes(_construire_trame(TYPE_TRAME_HORLOGE, STREAM_ID_HEARTBEAT_TUNNEL, payload))
                    except Exception as e:
                        logger.warning("/ws_tunnel : relais HORLOGE pilote->exécutant échoué (%r).", e)
                continue

            if role == "executant":
                # Sens exécutant -> pilote : remappe le stream_id LOCAL de
                # cet exécutant en stream_id GLOBAL avant de relayer (cf.
                # _RemappeurStreamId, seul point de logique ajouté ici).
                remappeur = registre_tunnel.remappeur_de(id_pilote_stable)
                pilote_ws = registre_tunnel.pilotes_tunnel.get(id_pilote_stable)
                if remappeur is None or pilote_ws is None:
                    # Pilote pas (ou plus) connecté -- rien à relayer,
                    # cf. section 6 côté sAutoniaX : timeout côté client
                    # (DELAI_TIMEOUT_OPEN_TUNNEL_SECONDES) prendra le relais
                    # pour un OPEN resté sans réponse, aucune action
                    # nécessaire ici.
                    continue
                if type_trame == TYPE_TRAME_OPEN:
                    stream_id_global = remappeur.vers_global(id_executant, stream_id)
                else:
                    # OPEN_FAIL n'existe pas dans ce sens (c'est une
                    # réponse du pilote), mais DATA/CLOSE dans ce sens
                    # doivent retrouver un mapping DÉJÀ créé par un OPEN
                    # antérieur -- ignoré si absent (flux déjà fermé/
                    # jamais ouvert, cf. remappeur.vers_local symétrique
                    # côté pilote pour le même raisonnement).
                    stream_id_global = remappeur.id_global_existant(id_executant, stream_id)
                    if stream_id_global is None:
                        continue
                try:
                    async with registre_tunnel.verrou_pour(pilote_ws):
                        await pilote_ws.send_bytes(_construire_trame(type_trame, stream_id_global, payload))
                except Exception as e:
                    logger.warning("/ws_tunnel : relais exécutant->pilote échoué (%r).", e)
                if type_trame == TYPE_TRAME_CLOSE:
                    remappeur.oublier(stream_id_global)

            else:
                # Sens pilote -> exécutant : stream_id reçu est GLOBAL,
                # le retraduire vers (id_executant, stream_id_local) pour
                # savoir à quel exécutant précis le relayer.
                remappeur = registre_tunnel.remappeur_de(id_pilote_stable)
                if remappeur is None:
                    continue
                resolu = remappeur.vers_local(stream_id)
                if resolu is None:
                    # Flux déjà fermé/inconnu (ex. CLOSE en double, ou
                    # course entre une fermeture cliente et une trame déjà
                    # en vol) -- ignoré silencieusement, cf. même principe
                    # que le "continue" symétrique ci-dessus.
                    continue
                id_executant_cible, stream_id_local = resolu
                executant_ws = registre_tunnel.executants_tunnel.get((id_pilote_stable, id_executant_cible))
                if executant_ws is None:
                    continue
                try:
                    async with registre_tunnel.verrou_pour(executant_ws):
                        await executant_ws.send_bytes(_construire_trame(type_trame, stream_id_local, payload))
                except Exception as e:
                    logger.warning("/ws_tunnel : relais pilote->exécutant échoué (%r).", e)
                if type_trame == TYPE_TRAME_CLOSE:
                    remappeur.oublier(stream_id)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning("/ws_tunnel : erreur de boucle (%r).", e)
    finally:
        if role == "pilote":
            # Section 8, dernier paragraphe : "le serveur envoie CLOSE
            # pour tous les stream_id actifs de cette paire à l'autre
            # bout" -- ICI, tous les exécutants de ce pilote reçoivent un
            # CLOSE pour chacun de leurs flux encore ouverts.
            remappeur = registre_tunnel.remappeur_de(id_pilote_stable)
            if remappeur is not None:
                for id_global, nom_executant, stream_id_local in remappeur.flux_ouverts():
                    executant_ws = registre_tunnel.executants_tunnel.get((id_pilote_stable, nom_executant))
                    if executant_ws is not None:
                        try:
                            async with registre_tunnel.verrou_pour(executant_ws):
                                await executant_ws.send_bytes(_construire_trame(TYPE_TRAME_CLOSE, stream_id_local))
                        except Exception:
                            pass
            registre_tunnel.retirer_pilote(id_pilote_stable)
            logger.info("/ws_tunnel : pilote déconnecté (id_pilote_stable=%s).", id_pilote_stable)
        else:
            # Symétrique -- le pilote de cet exécutant reçoit un CLOSE
            # pour chacun des flux que CET exécutant avait ouverts (les
            # flux des AUTRES exécutants du même pilote ne sont pas
            # affectés, cf. oublier_executant qui filtre par id_executant).
            remappeur = registre_tunnel.remappeur_de(id_pilote_stable)
            pilote_ws = registre_tunnel.pilotes_tunnel.get(id_pilote_stable)
            if remappeur is not None:
                ids_globaux_ouverts = remappeur.oublier_executant(id_executant)
                if pilote_ws is not None:
                    for id_global in ids_globaux_ouverts:
                        try:
                            async with registre_tunnel.verrou_pour(pilote_ws):
                                await pilote_ws.send_bytes(_construire_trame(TYPE_TRAME_CLOSE, id_global))
                        except Exception:
                            pass
            registre_tunnel.retirer_executant(id_pilote_stable, id_executant)
            logger.info("/ws_tunnel : exécutant déconnecté (id_pilote_stable=%s, id_executant=%s).", id_pilote_stable, id_executant)


if __name__ == "__main__":
    # Lancement local pour test avant déploiement Render (cf. cahier :
    # "Déployé sur Render (hébergement réel, pas en local)" est le
    # critère de validation FINAL de l'Étape 0, mais rien n'empêche de
    # vérifier d'abord que ça tourne en local). Render fournit le port
    # via la variable d'environnement PORT -- repli sur 8000 en local.
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # BUGFIX (keepalive ping timeout, code 1011 -- MÊME cause de fond
    # que le correctif ping_interval=None déjà appliqué côté client sur
    # websockets.connect, cf. AutoniaX.py/ClientServeurT._boucle_async) :
    # uvicorn utilise la même lib `websockets` en interne pour le
    # protocole WebSocket (--ws=auto), avec ses PROPRES ping/pong natifs
    # au niveau protocole, réglés par défaut à ws_ping_interval=20.0/
    # ws_ping_timeout=20.0 (documentation uvicorn) -- totalement
    # indépendants du heartbeat applicatif JSON de ce code (cf. logger
    # côté serveur : aucune trace de "ping"/"pong" applicatif ici, ce
    # protocole-là n'existe que côté AutoniaX.py). Avoir désactivé UNIQUEMENT
    # le ping natif côté CLIENT (websockets.connect) ne suffisait pas :
    # le SERVEUR, lui, continuait d'attendre son propre pong toutes les
    # 20s et fermait la connexion (code 1011, "keepalive ping timeout")
    # si sa boucle événementielle mettait plus de 20s à répondre --
    # exactement ce qui se produit pendant qu'un gros chunk (plusieurs
    # Mo encodés en base64) est en cours de traitement/envoi côté
    # serveur, cf. DIAG_TELECHARGEMENT. ws_ping_interval=None désactive
    # ENTIÈREMENT ce ping/pong natif côté serveur, sur le même principe
    # que côté client -- la détection de connexion morte repose
    # désormais uniquement sur le heartbeat applicatif JSON piloté par
    # AutoniaX.py (_tache_heartbeat), des deux côtés de la connexion.
    # DIAGNOSTIC (retour utilisateur : "Le serveurT s'est arrêté de
    # lui-même (code -11)") -- code de sortie -11 = signal SIGSEGV
    # (segmentation fault), un crash NATIF du process (jamais levé par
    # une exception Python pure, donc rien à "except" ici) -- ne
    # provient donc PAS de ce fichier serveur.py lui-même (code Python
    # standard), mais d'une extension C sous-jacente. uvicorn.run(...)
    # ci-dessous ne précisait pas explicitement loop= : Uvicorn choisit
    # alors AUTOMATIQUEMENT `uvloop` (event loop en C, basé sur libuv)
    # si le paquet est installé dans l'environnement -- connu pour
    # occasionnellement segfaulter sous Google Colab après une longue
    # durée de vie du process ou sous charge concurrente élevée (cas
    # observé ici : ~1h de logs, plusieurs pilotes/sAutoniax connectés
    # en parallèle, juste avant le crash). loop="asyncio" force la
    # boucle événementielle standard de la stdlib Python (pure Python +
    # C stable de CPython lui-même, pas de libuv tiers) -- plus lente de
    # quelques % en théorie, mais élimine cette cause de crash native la
    # plus probable. Si le crash -11 persiste malgré ce changement,
    # la cause est ailleurs (googleapiclient/httplib2, cf. les erreurs
    # SSL WRONG_VERSION_NUMBER juste avant le crash dans les logs --
    # possiblement lié si une connexion HTTP en cours d'utilisation par
    # un thread de l'executor était dans un état incohérent au moment du
    # crash, bien que rien ne le confirme avec certitude depuis un seul
    # jeu de logs).
    uvicorn.run(app, host="0.0.0.0", port=port, ws_ping_interval=None, ws_ping_timeout=None, ws_max_size=512 * 1024 * 1024, loop="asyncio")
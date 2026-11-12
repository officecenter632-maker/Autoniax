# Spécification : sous-onglet « Profils Kaggle »

## 1. Objectif et périmètre
Ajouter à **Réseau > Profils** un troisième sous-onglet, **« Profils Kaggle »**, qui permet de :
- **A. Envoyer** vers Kaggle les profils présents sur les sAutoniax connectés, après arrêt des exécutions, archivage et nommage par compte ;
- **B. Télécharger** des profils depuis Kaggle et les répartir équitablement sur les sAutoniax choisis.

Kaggle et Drive restent deux stockages **séparés**. « Profils Cloud » (Drive) n'est pas modifié.

## 2. Décisions figées

| Sujet | Décision |
|---|---|
| Compte | Un seul compte Kaggle, `mikereichlin`, jeton **écrit en dur** (décision utilisateur, y compris dans la version poussée sur git) |
| Datasets | Un dataset **privé** par profil, **une seule version** conservée |
| Nom d'archive | Email du compte connecté, via un JSON de correspondance (import par presse-papiers) |
| Case « Garder le nom actuel » | Cochée par défaut pour un profil venu de Kaggle ; si décochée, le profil doit figurer dans le JSON |
| Profils concernés | Tous ceux des sAutoniax connectés, cochés par défaut, décochables |
| Arrêt avant envoi | Obligatoire : les exécutions sont arrêtées avant toute archive |
| Suppression locale | Case cochée par défaut ; suppression du dossier sur le sAutoniax **uniquement après envoi vérifié** |
| Répartition | Équitable par nombre de profils, aperçu à confirmer |
| Transport des archives | Direct sAutoniax ↔ Kaggle. Le serveurT ne transporte que ordres et progression |

## 3. Constantes (en dur, dans le code et le notebook)
- `KAGGLE_USERNAME = "mikereichlin"` et `KAGGLE_API_TOKEN = "KGAT_…"`, posé dans `os.environ["KAGGLE_API_TOKEN"]` avant tout import de `kaggle`.
- Paquet épinglé : `kaggle==2.2.5` (minimum 1.8.0). Même épinglage dans `PAQUETS_PIP` du notebook sAutoniax, car la version préinstallée sur Kaggle peut être trop ancienne.
- `PREFIXE_DATASET = "ax-"` ; `MAX_TRANSFERTS_SIMULTANES = 3` (global, tous sAutoniax confondus) ; `NB_TENTATIVES = 3` (attente 5 s, 15 s, 45 s) ; `DELAI_PRET_KAGGLE_S = 600` ; `QUOTA_PRIVE_GO = 100` (affichage seulement).

## 4. Correspondance de noms (JSON via presse-papiers)

**Format :** `{ "nom_profil_local": "email@domaine.com", ... }`.

**Interface (aucun QTextEdit ni QPlainTextEdit dans le sous-onglet) :**
- Bouton **« Importer la correspondance (presse-papiers) »** : lit `QGuiApplication.clipboard().text()`, parse le JSON et le valide.
- Bouton **« Vider »**.
- Un libellé de résumé : « N correspondances, importées le … », avec en infobulle les 10 premières entrées.

**Règles de validation :**
- Le JSON doit être un objet dont toutes les clés et valeurs sont des chaînes non vides (espaces retirés).
- En cas d'erreur (JSON invalide, mauvais type, presse-papiers vide), un message clair s'affiche et la correspondance précédente reste **intacte**.
- Un import réussi **remplace** entièrement la correspondance (pas de fusion).
- Une valeur sans `@` est acceptée avec un avertissement.
- Deux profils qui donnent le même email sont signalés (cf. §7).
- La correspondance est **persistée** dans les réglages de l'application (`ReglagesApp`, clé `kaggle_correspondance_noms`) et survit aux redémarrages.

## 5. Nommage Kaggle

| Élément | Règle |
|---|---|
| **Nom d'archive** | Case « Garder le nom » cochée : nom local actuel. Décochée : valeur du JSON |
| **Identifiant du dataset** | `PREFIXE_DATASET` + nom d'archive transformé : minuscules, tout caractère hors `a-z0-9` remplacé par `-`, tirets consécutifs fusionnés. Au-delà de la limite Kaggle (50 caractères, à confirmer au premier test), troncature suivie de `-` et de 8 caractères de hash |
| **Titre** | `AX <nom d'archive>`, tronqué à 50 caractères |
| **Sous-titre** | `ax;cree=<date UTC ISO>` : porte la date de création, que l'API ne fournit pas |
| **Description** | JSON compact : nom d'archive, nom local d'origine, email, sAutoniax d'origine |

**Contenu du dataset :**
- `<nom_archive>.zip` : l'archive produite par `_zipper_dossier_profil`, qui nettoie déjà le fingerprint.
- `meta.json` : nom d'archive, nom local d'origine, taille, date d'envoi UTC, instance d'origine.

**Date de création :** écrite au premier envoi. Aux mises à jour, le sous-titre existant est relu et la valeur conservée, sans jamais l'écraser. La date de mise à jour vient de Kaggle (`last_updated`).

**Après un téléchargement :** le dossier local porte le nom d'archive, et l'archive d'origine est enregistrée dans `sautoniax_profils/_kaggle_origine.json`. C'est ce qui coche « Garder le nom » aux envois suivants.

## 6. Interface du sous-onglet
Classe `ProfilsKaggleScreen`, ajoutée dans `ProfilsScreen` après « Profils Local ». Elle suit le thème Mocha et les icônes qtawesome des autres écrans, et relaie ses signaux comme les écrans existants.

**Barre haute :** boutons de correspondance (§4), état de connexion Kaggle (vérifié au chargement), quota utilisé (somme des tailles des datasets `ax-` sur `QUOTA_PRIVE_GO`).

**Bloc A, « Envoyer vers Kaggle » :**
- Arbre sAutoniax → profils, tout coché par défaut.
- Colonnes : profil, taille, dernière modification, case « Garder le nom », nom d'archive résultant, état, progression.
- Les lignes en erreur de nommage sont en rouge, avec le motif en infobulle.
- Case **« Supprimer du sAutoniax après envoi »**, cochée par défaut.
- Bouton **« Arrêter + Archiver + Envoyer »**, qui ouvre un récapitulatif à confirmer (profils concernés, archives créées ou mises à jour, suppression locale oui/non).

**Bloc B, « Télécharger depuis Kaggle » :**
- Bouton « Actualiser » et tableau des datasets `ax-` : case, nom d'archive, taille, créé le, mis à jour le.
- Tri par clic sur en-tête, sur création ou mise à jour, **du plus récent au plus ancien**. Le tri par défaut est la mise à jour, décroissante.
- Liste des sAutoniax connectés, cochables.
- Bouton **« Répartir et télécharger »**, avec aperçu de la répartition à confirmer.

**Journal :** une `QListWidget` limitée à 500 lignes, sans éditeur de texte.

**Règles d'état :** pendant une opération, les boutons d'action sont désactivés, et une seule opération Kaggle à la fois est autorisée.

## 7. Flux A : Envoyer
1. **Vérification locale (pilote) :** résolution des noms (§5), détection des profils absents du JSON avec case décochée (exclus et signalés), des doublons d'email et des collisions d'identifiant (les profils concernés sont bloqués). Les autres partent normalement.
2. **Arrêt :** le pilote réutilise l'ordre existant `arreter_execution_profil` pour chaque profil en cours, puis attend `arreter_execution_profil_resultat_reel`, avec délai maximum. Sans confirmation d'arrêt d'un profil, **ce profil n'est pas archivé** (cookies et bases SQLite possiblement incohérents).
3. **Par profil**, côté sAutoniax (un à la fois par sAutoniax, dans la limite globale de `MAX_TRANSFERTS_SIMULTANES`) :
   - zip dans un dossier temporaire ;
   - détection de l'existence du dataset (`dataset_status`) : s'il est absent, `dataset_create_new` en **privé** ; s'il existe, `dataset_create_version(delete_old_versions=True, convert_to_csv=False)` ;
   - attente que Kaggle soit « prêt » (jusqu'à `DELAI_PRET_KAGGLE_S`), puis vérification que le fichier est présent avec la bonne taille ;
   - si la case est cochée : suppression du dossier local, **uniquement après cette vérification** ;
   - nettoyage des fichiers temporaires dans tous les cas.
4. **Erreurs :** `NB_TENTATIVES` essais ; en cas d'échec, rien n'est supprimé et la ligne passe en erreur avec son motif.
5. **Même profil sur deux sAutoniax :** seule la copie modifiée le plus récemment est envoyée, avec un avertissement.
6. Les exécutions restent **arrêtées** à la fin.

## 8. Flux B : Télécharger
1. **Répartition :** tourniquet dans l'ordre d'affichage, sAutoniax triés de façon stable par identifiant (10 profils sur 3 sAutoniax donnent 4, 3 et 3).
2. **Par profil**, côté sAutoniax cible : téléchargement direct depuis Kaggle, extraction (gestion des deux cas : zip conservé ou décompressé par Kaggle), écrasement d'un profil du même nom, puis écriture dans `_kaggle_origine.json`.
3. **Sécurité :** si le profil cible tourne sur ce sAutoniax, il est refusé avec le motif « en cours d'exécution ».
4. **Déconnexion en cours de route :** les lignes concernées passent en erreur. Il n'y a pas de réaffectation automatique dans cette version.
5. Le disque de session est vidé par le notebook à chaque démarrage (section 3) : ces profils ne survivent pas à un redémarrage de la session. C'est le comportement actuel, il n'est pas modifié.

## 9. Protocole serveurT
**Constat (phase 3) :** le relais n'est pas générique, chaque type est déclaré. `serveur.py` porte deux branches :
pilote → sAutoniax (`kaggle_lister_profils`, `kaggle_envoyer_profils`, `kaggle_telecharger_profils`, accusé `<type>_ack`, `id_pilote` ajouté) et sAutoniax → pilote (`kaggle_lister_profils_resultat`, `kaggle_progression`, `kaggle_resultat`, `id_executant` ajouté).
Le pilote envoie **un profil par ordre** d'envoi et borne lui-même à `MAX_TRANSFERTS_SIMULTANES`. Le flux A commence par un listage frais (`actif` par profil), arrête les profils actifs, puis envoie ; un profil dont l'arrêt n'est pas confirmé n'est pas archivé.

| Type de message | Rôle |
|---|---|
| `kaggle_lister_profils` / `…_resultat` | liste des profils d'un sAutoniax (nom, taille, date de modification, origine Kaggle) |
| `kaggle_envoyer_profils` | profils à envoyer, avec nom d'archive et option de suppression |
| `kaggle_telecharger_profils` | datasets à télécharger et noms locaux |
| `kaggle_progression` | étape et pourcentage par profil |
| `kaggle_resultat` | succès ou échec par profil, avec motif |

Chaque opération porte un identifiant, et les messages inconnus sont ignorés sans planter.

## 10. Classe `GestionnaireKaggle` (la « zone de script »)
Un bloc de code isolé, avec méthodes : `authentifier()`, `lister_datasets()`, `dataset_existe(ref)`, `envoyer_profil(...)`, `telecharger_profil(...)`, `slug_depuis_nom(...)`. Aucun appel Kaggle n'est écrit ailleurs.

Elle est utilisée côté pilote (liste, quota) et côté sAutoniax (envoi, téléchargement). Elle est appelée **hors thread Qt**, comme le reste des transferts de l'application.

## 11. Fichiers modifiés
- `AutoniaX.pyw` : classe Kaggle, sous-onglet, messages, câblage `ProfilsScreen` → `ReseauScreen` → `MainWindow`.
- `serveur.py` : seulement si le relais n'est pas générique.
- Notebook sAutoniax : paquet `kaggle` épinglé et variable d'environnement du jeton.
- Notebook ServeurT : inchangé, sauf si `serveur.py` est modifié (la mise à jour passe alors par l'onglet « Code »).

## 12. Livraison et workflow git
Livraison par phases, chacune avec commit et push (jeton en dur inclus, décision utilisateur) :
- **Phase 1 :** classe Kaggle isolée, nommage et import presse-papiers.
- **Phase 2 :** sous-onglet (interface seule, sans réseau).
- **Phase 3 :** flux A (arrêt, archive, envoi).
- **Phase 4 :** flux B (téléchargement, répartition).

À chaque modification de `AutoniaX.pyw`, rendu **uniquement** de `AutoniaX.pyw.xz` (LZMA2, preset 9 extrême, dict 128 Mo, CRC64), vérifié avec `xz -t`, avec en une ligne la taille avant et après. Le fichier non compressé n'est jamais présenté, et l'original n'est pas laissé dans le dossier de sortie.

## 13. Critères d'acceptation
- L'import presse-papiers accepte un JSON valide et refuse les autres sans perdre l'ancienne correspondance.
- Un profil jamais envoyé crée son dataset ; un profil déjà envoyé le met à jour, et une seule version reste visible sur Kaggle.
- Aucun dossier local n'est supprimé sans envoi vérifié ni sans confirmation d'arrêt de l'exécution.
- Les deux tris du bloc B fonctionnent, du plus récent au plus ancien.
- La répartition de 10 profils sur 3 sAutoniax donne 4, 3 et 3.
- Un échec sur un profil n'arrête pas les autres.
- Aucun appel à Drive n'est ajouté ni modifié.

## 14. Limites connues et points à valider au premier test réel
- Kaggle n'est pas joignable depuis l'environnement de développement : tests locaux avec un faux client uniquement. Le premier essai réel se fait avec 1 ou 2 profils.
- À confirmer à ce moment-là : limite exacte de longueur de l'identifiant, comportement de Kaggle sur un zip (décompressé ou non), débit acceptable de l'API.

**Hors périmètre :** réaffectation automatique après déconnexion, fusion de correspondances, relance automatique des exécutions, partage de datasets entre comptes.

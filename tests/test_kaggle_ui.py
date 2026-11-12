"""Test d'interface (hors ecran) du sous-onglet Profils Kaggle -- phase 2.
Usage : QT_QPA_PLATFORM=offscreen python3 tests/test_kaggle_ui.py
Necessite PySide6 et QtAwesome. Extrait le bloc Kaggle, Mocha et ProfilsKaggleScreen de AutoniaX.pyw."""
import hashlib, io, json, logging, os, re, shutil, sys, tempfile, time, uuid, zipfile
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor, QGuiApplication
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
                               QTreeWidget, QTreeWidgetItem, QPushButton, QMessageBox, QFrame, QAbstractItemView,
                               QCheckBox, QLabel, QPlainTextEdit, QTextEdit)
import qtawesome as qta

RACINE = Path(__file__).resolve().parent.parent
src = (RACINE / "AutoniaX.pyw").read_text(encoding="utf-8")
i0 = src.index("# PROFILS KAGGLE (phase 1) -- DEBUT DU BLOC ISOLE")
i1 = src.index("# PROFILS KAGGLE (phase 1) -- FIN DU BLOC ISOLE")
bloc = src[src.rfind("\n# ====", 0, i0) + 1: src.index("\n", i1) + 1]
ecran = src[src.index("class ProfilsKaggleScreen(QWidget):"): src.index("class ControleurKaggle(QObject):")]
m0 = src.index("class Mocha:\n")
mocha = src[m0: src.index("\n\n\n", m0)]

logging.disable(logging.CRITICAL)
app = QApplication.instance() or QApplication([])


class FauxQMessageBox:
    Yes, No = QMessageBox.Yes, QMessageBox.No
    reponse = QMessageBox.Yes
    messages: list = []
    @staticmethod
    def warning(parent, titre, texte):
        FauxQMessageBox.messages.append(("warning", texte))
    @staticmethod
    def information(parent, titre, texte):
        FauxQMessageBox.messages.append(("information", texte))
    @staticmethod
    def question(parent, titre, texte, boutons=None, defaut=None):
        FauxQMessageBox.messages.append(("question", texte))
        return FauxQMessageBox.reponse


ns = dict(os=os, re=re, json=json, shutil=shutil, tempfile=tempfile, zipfile=zipfile, hashlib=hashlib, time=time,
          uuid=uuid, logging=logging, Path=Path, Optional=Optional, Qt=Qt, Signal=Signal, QBrush=QBrush,
          QColor=QColor, QGuiApplication=QGuiApplication, QWidget=QWidget, QHBoxLayout=QHBoxLayout,
          QVBoxLayout=QVBoxLayout, QListWidget=QListWidget, QListWidgetItem=QListWidgetItem,
          QTreeWidget=QTreeWidget, QTreeWidgetItem=QTreeWidgetItem, QPushButton=QPushButton,
          QMessageBox=FauxQMessageBox, QFrame=QFrame, QAbstractItemView=QAbstractItemView, QCheckBox=QCheckBox,
          QLabel=QLabel, qta=qta, ReglagesApp=None)
exec(mocha, ns)
exec(compile(bloc, "kaggle_block", "exec"), ns)
exec(compile(ecran, "kaggle_ecran", "exec"), ns)

nb = 0
def ok(cond, msg):
    global nb
    nb += 1
    if not cond:
        print("ECHEC :", msg)
        sys.exit(1)


class FauxReglages:
    def __init__(self):
        self.kaggle_correspondance_noms = {}
        self.kaggle_correspondance_date = ""
        self.sauvegardes = 0
    def save(self):
        self.sauvegardes += 1


reglages = FauxReglages()
E = ns["ProfilsKaggleScreen"]()
E.definir_reglages(reglages)
emis = {k: [] for k in ("verifier", "profils", "datasets", "envoyer", "telecharger")}
E.demande_kaggle_verifier_connexion.connect(lambda: emis["verifier"].append(1))
E.demande_kaggle_actualiser_profils.connect(lambda ids: emis["profils"].append(list(ids)))
E.demande_kaggle_actualiser_datasets.connect(lambda: emis["datasets"].append(1))
E.demande_kaggle_envoyer.connect(lambda c: emis["envoyer"].append(c))
E.demande_kaggle_telecharger.connect(lambda c: emis["telecharger"].append(c))
E.show()
app.processEvents()

ok(not E.findChildren(QPlainTextEdit) and not E.findChildren(QTextEdit), "aucun QTextEdit/QPlainTextEdit dans le sous-onglet")
ok(len(emis["verifier"]) == 1, "connexion Kaggle verifiee au premier affichage")
ok(E.label_correspondance.text() == "Aucune correspondance importee.", "resume vide")
ok(not E.bouton_envoyer.isEnabled() and not E.bouton_telecharger.isEnabled(), "boutons inactifs au depart")

# ---- sAutoniax et profils ------------------------------------------------
E.definir_sautoniax_disponibles({"s2": "Beta", "s1": "Alpha"})
ok(emis["profils"] and emis["profils"][-1] == ["s1", "s2"], "nouveaux sAutoniax : profils demandes")
E.definir_profils_sautoniax("s1", [
    {"nom": "alice", "taille_octets": 5 * 1024 * 1024, "modifie_ts": 1_780_000_000, "origine_kaggle": None},
    {"nom": "bob", "taille_octets": 2048, "modifie_ts": 1_780_000_100, "origine_kaggle": "bob@x.com"},
    {"nom": "commun", "taille_octets": 10, "modifie_ts": 1_780_000_500, "origine_kaggle": None}])
E.definir_profils_sautoniax("s2", [
    {"nom": "carl", "taille_octets": 1, "modifie_ts": 1_780_000_000, "origine_kaggle": None},
    {"nom": "commun", "taille_octets": 10, "modifie_ts": 1_780_000_900, "origine_kaggle": None}])
ok(E.arbre_envoi.topLevelItemCount() == 2 and E.arbre_envoi.topLevelItem(0).text(0) == "Alpha", "arbre : sAutoniax tries par nom")
ok(E.arbre_envoi.topLevelItem(0).childCount() == 3 and E.arbre_envoi.topLevelItem(1).childCount() == 2, "arbre : profils par sAutoniax")
ok(all(it.checkState(0) == Qt.Checked for it in E._items.values()), "tout coche par defaut")
ok(E._items[("s1", "bob")].checkState(E.COL_GARDER) == Qt.Checked, "'Garder le nom' coche pour un profil venu de Kaggle")
ok(E._items[("s1", "alice")].checkState(E.COL_GARDER) == Qt.Unchecked, "'Garder le nom' decoche sinon")
ok(E._items[("s1", "alice")].text(E.COL_TAILLE) == "5,0 Mo", "taille formatee")
ok(E.case_supprimer.isChecked(), "suppression locale cochee par defaut")

# ---- nommage : sans correspondance, les decoches sont en erreur (rouge) ----
it_alice = E._items[("s1", "alice")]
ok(it_alice.text(E.COL_ETAT) == "erreur de nommage" and "Absent" in it_alice.toolTip(E.COL_ETAT), "profil absent du JSON : erreur + infobulle")
ok(it_alice.foreground(0).color().name() == QColor(ns["Mocha"].red).name(), "ligne en erreur : rouge")
ok(E._items[("s1", "bob")].text(E.COL_ARCHIVE) == "bob", "garder le nom : nom local")
ok(E._items[("s2", "commun")].text(E.COL_ETAT) == "erreur de nommage", "commun (copie la plus recente) absent du JSON : erreur")
ok(E._items[("s1", "commun")].text(E.COL_ETAT).startswith("ignore"), "commun (copie plus ancienne) : ignore, pas en erreur")

# ---- import presse-papiers --------------------------------------------------
QGuiApplication.clipboard().setText("pas du json")
E._sur_clic_importer()
ok(FauxQMessageBox.messages[-1][0] == "warning" and reglages.kaggle_correspondance_noms == {}, "import invalide refuse")
QGuiApplication.clipboard().setText(json.dumps({"alice": "alice@x.com", "commun": "commun@x.com", "carl": "carl@x.com"}))
E._sur_clic_importer()
ok(reglages.kaggle_correspondance_noms["alice"] == "alice@x.com" and reglages.sauvegardes == 1, "import valide persiste")
ok(E.label_correspondance.text().startswith("3 correspondances"), "resume mis a jour")
ok("alice -> alice@x.com" in E.label_correspondance.toolTip(), "infobulle du resume")
ok(it_alice.text(E.COL_ARCHIVE) == "alice@x.com" and it_alice.text(E.COL_ETAT) == "pret", "nom d'archive = email apres import")
QGuiApplication.clipboard().setText("[1, 2")
E._sur_clic_importer()
ok(reglages.kaggle_correspondance_noms["alice"] == "alice@x.com", "mauvais import : ancienne correspondance intacte")

# ---- meme profil sur deux sAutoniax -----------------------------------------
ancien, recent = E._items[("s1", "commun")], E._items[("s2", "commun")]
ok(recent.text(E.COL_ETAT).startswith("pret") and ancien.text(E.COL_ETAT).startswith("ignore"), "copie la plus recente gardee, l'ancienne ignoree")
ok("Alpha" not in ancien.toolTip(E.COL_ETAT) and "Beta" in ancien.toolTip(E.COL_ETAT), "avertissement nomme le sAutoniax gagnant")

# ---- envoi : recapitulatif, signal, verrouillage ------------------------------
ok(E.bouton_envoyer.isEnabled(), "bouton envoyer actif")
FauxQMessageBox.reponse = QMessageBox.No
E._sur_clic_envoyer()
ok(not emis["envoyer"] and not E.operation_en_cours(), "refus du recapitulatif : rien n'est envoye")
FauxQMessageBox.reponse = QMessageBox.Yes
E._sur_clic_envoyer()
recap = FauxQMessageBox.messages[-1][1]
ok("ARRETEES" in recap and "OUI" in recap, "recapitulatif : arret + suppression locale")
charge = emis["envoyer"][0]
noms = sorted((p["id_executant"], p["nom_local"], p["nom_archive"]) for p in charge["profils"])
ok(noms == [("s1", "alice", "alice@x.com"), ("s1", "bob", "bob"), ("s2", "carl", "carl@x.com"), ("s2", "commun", "commun@x.com")],
   "charge d'envoi : profils partants et noms d'archive")
ok(charge["supprimer_local"] is True and charge["id_operation"], "charge d'envoi : suppression + id d'operation")
ok(E.operation_en_cours() and not E.bouton_envoyer.isEnabled() and not E.bouton_importer.isEnabled()
   and not E.bouton_actualiser_datasets.isEnabled() and not E.bouton_telecharger.isEnabled(), "boutons d'action desactives pendant l'operation")
n = len(emis["envoyer"])
E._sur_clic_envoyer()
ok(len(emis["envoyer"]) == n, "une seule operation a la fois")
op = charge["id_operation"]
E.sur_progression_envoi("autre-op", "s1", "alice", "Archivage", 50)
ok(E._items[("s1", "alice")].text(E.COL_PROG) == "0 %", "progression d'une autre operation ignoree")
E.sur_progression_envoi(op, "s1", "alice", "Envoi vers Kaggle", 42)
ok(E._items[("s1", "alice")].text(E.COL_PROG) == "42 %" and E._items[("s1", "alice")].text(E.COL_ETAT) == "Envoi vers Kaggle", "progression affichee")
E.sur_resultat_envoi(op, "s1", "alice", True, "")
E.sur_resultat_envoi(op, "s2", "carl", False, "panne reseau")
ok(E._items[("s2", "carl")].text(E.COL_ETAT) == "ERREUR" and E._items[("s2", "carl")].toolTip(E.COL_ETAT) == "panne reseau", "echec d'un profil avec motif")
ok(E._items[("s1", "alice")].text(E.COL_ETAT) == "envoye", "succes d'un autre profil")
avant_p, avant_d = len(emis["profils"]), len(emis["datasets"])
E.terminer_operation("autre-op")
ok(E.operation_en_cours(), "terminer avec un autre identifiant : ignore")
E.terminer_operation(op)
ok(not E.operation_en_cours() and E.bouton_envoyer.isEnabled(), "ecran libere")
ok(len(emis["profils"]) == avant_p + 1 and len(emis["datasets"]) == avant_d + 1, "listes rafraichies a la fin de l'operation")

# ---- bloc B : datasets, tri -----------------------------------------------------
datasets = [
    {"ref": "u/ax-a", "slug": "ax-a", "nom_archive": "a@x.com", "taille_octets": 100, "cree_le": "2026-01-01T00:00:00Z", "maj_le": "2026-11-01 10:00:00"},
    {"ref": "u/ax-b", "slug": "ax-b", "nom_archive": "b@x.com", "taille_octets": 200, "cree_le": "2026-06-01T00:00:00Z", "maj_le": "2026-03-01 10:00:00"},
    {"ref": "u/ax-c", "slug": "ax-c", "nom_archive": "c@x.com", "taille_octets": 300, "cree_le": "2026-03-01T00:00:00Z", "maj_le": "2026-09-01 10:00:00"},
    {"ref": "u/ax-d", "slug": "ax-d", "nom_archive": "d@x.com", "taille_octets": 400, "cree_le": None, "maj_le": None}]
E.definir_datasets(datasets)
ordre = lambda: [E.table_datasets.topLevelItem(r).text(0) for r in range(E.table_datasets.topLevelItemCount())]
ok(ordre() == ["a@x.com", "c@x.com", "b@x.com", "d@x.com"], "tri par defaut : mise a jour, du plus recent au plus ancien")
E._sur_clic_entete_datasets(2)
ok(ordre() == ["b@x.com", "c@x.com", "a@x.com", "d@x.com"], "tri par creation, du plus recent au plus ancien")
E._sur_clic_entete_datasets(3)
ok(ordre() == ["a@x.com", "c@x.com", "b@x.com", "d@x.com"], "retour au tri par mise a jour")
E._sur_clic_entete_datasets(0)
ok(ordre() == ["a@x.com", "c@x.com", "b@x.com", "d@x.com"], "clic sur une autre colonne : tri inchange")
ok("Quota prive" in E.label_quota.text() and "100 Go" in E.label_quota.text(), "quota affiche")
ok(E._items[("s1", "alice")].text(E.COL_ETAT) == "pret (creation)", "etat creation/mise a jour d'apres la liste Kaggle")

# ---- telechargement : repartition ------------------------------------------------
E.definir_datasets([{"ref": f"u/ax-p{i}", "slug": f"ax-p{i:02d}", "nom_archive": f"p{i:02d}@x.com", "taille_octets": 1,
                     "cree_le": f"2026-01-{i + 1:02d}T00:00:00Z", "maj_le": f"2026-02-{i + 1:02d} 10:00:00"} for i in range(10)])
E.definir_sautoniax_disponibles({"s1": "Alpha", "s2": "Beta", "s3": "Gamma"})
ok(not E.bouton_telecharger.isEnabled(), "telechargement inactif sans selection")
for r in range(E.table_datasets.topLevelItemCount()):
    E.table_datasets.topLevelItem(r).setCheckState(0, Qt.Checked)
ok(not E.bouton_telecharger.isEnabled(), "telechargement inactif sans sAutoniax coche")
for r in range(E.liste_cibles.count()):
    E.liste_cibles.item(r).setCheckState(Qt.Checked)
ok(E.bouton_telecharger.isEnabled(), "telechargement actif")
E._sur_clic_telecharger()
rep = {b["id_executant"]: b["profils"] for b in emis["telecharger"][0]["repartition"]}
ok(sorted(len(v) for v in rep.values()) == [3, 3, 4] and len(rep["s1"]) == 4, "10 profils sur 3 sAutoniax : 4, 3, 3")
ok(rep["s1"][0]["nom_archive"] == "p09@x.com" and rep["s1"][0]["nom_local"] == "p09@x.com", "ordre d'affichage (plus recent en premier) + nom local = nom d'archive")
ok("Alpha : 4 profil(s)" in FauxQMessageBox.messages[-1][1], "apercu de la repartition")
ok(E.operation_en_cours() and not E.bouton_telecharger.isEnabled(), "verrouille pendant le telechargement")
E.sur_non_branche(emis["telecharger"][0]["id_operation"])
ok(not E.operation_en_cours(), "stub phase 2 : ecran libere")

# ---- sAutoniax deconnecte, journal borne ----------------------------------------
E.definir_sautoniax_disponibles({"s1": "Alpha"})
ok(E.arbre_envoi.topLevelItemCount() == 1 and E.liste_cibles.count() == 1, "sAutoniax deconnectes retires")
for i in range(700):
    E.ajouter_journal(f"ligne {i}")
ok(E.journal.count() == 500 and E.journal.item(499).text().endswith("ligne 699"), "journal limite a 500 lignes")

# ---- etat de connexion ------------------------------------------------------------
E.definir_etat_connexion(True, "", 1024 ** 3)
ok(E.label_connexion.text() == "Kaggle : connecte" and "1,0 Go" in E.label_quota.text(), "connexion OK + quota")
E.definir_etat_connexion(False, "jeton refuse")
ok("jeton refuse" in E.label_connexion.text(), "connexion en echec")

# ---- indicateur de requete en cours -----------------------------------------------
E.definir_activite_kaggle(True, "Connexion a Kaggle en cours...")
ok(not E.barre_activite_kaggle.isHidden() and "en cours" in E.label_connexion.text(), "barre + libelle pendant la connexion")
ok("en cours" in E.journal.item(E.journal.count() - 1).text(), "ligne de journal 'en cours'")
E.definir_etat_connexion(False, "jeton refuse")
ok(E.barre_activite_kaggle.isHidden(), "barre masquee apres un echec")
E.definir_activite_kaggle(True, "Actualisation en cours...")
E.definir_datasets([])
ok(E.barre_activite_kaggle.isHidden(), "barre masquee quand les datasets arrivent")

print(f"OK -- {nb} verifications d'interface passees")

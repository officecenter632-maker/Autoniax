"""Test du ControleurKaggle (phase 3) : vrai ecran + faux client reseau, hors ecran.
Usage : QT_QPA_PLATFORM=offscreen python3 tests/test_kaggle_controleur.py"""
import hashlib, io, json, logging, os, re, shutil, sys, tempfile, threading, time, uuid, zipfile
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QObject, QTimer
from PySide6.QtGui import QBrush, QColor, QGuiApplication
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
                               QTreeWidget, QTreeWidgetItem, QPushButton, QMessageBox, QFrame, QAbstractItemView,
                               QCheckBox, QLabel)
import qtawesome as qta

RACINE = Path(__file__).resolve().parent.parent
src = (RACINE / "AutoniaX.pyw").read_text(encoding="utf-8")
i0 = src.index("# PROFILS KAGGLE (phase 1) -- DEBUT DU BLOC ISOLE")
i1 = src.index("# PROFILS KAGGLE (phase 1) -- FIN DU BLOC ISOLE")
bloc = src[src.rfind("\n# ====", 0, i0) + 1: src.index("\n", i1) + 1]
ecran = src[src.index("class ProfilsKaggleScreen(QWidget):"): src.index("class ControleurKaggle(QObject):")]
ctrl = src[src.index("class ControleurKaggle(QObject):"): src.index("class ProfilsScreen(QWidget):")]
m0 = src.index("class Mocha:\n")
mocha = src[m0: src.index("\n\n\n", m0)]

logging.disable(logging.CRITICAL)
app = QApplication.instance() or QApplication([])


class FauxQMessageBox:
    Yes, No = QMessageBox.Yes, QMessageBox.No
    @staticmethod
    def warning(*a): pass
    @staticmethod
    def information(*a): pass
    @staticmethod
    def question(*a, **k): return QMessageBox.Yes


ns = dict(os=os, re=re, json=json, shutil=shutil, tempfile=tempfile, zipfile=zipfile, hashlib=hashlib, time=time,
          uuid=uuid, logging=logging, Path=Path, Optional=Optional, threading=threading, Qt=Qt, Signal=Signal,
          QObject=QObject, QTimer=QTimer, QBrush=QBrush, QColor=QColor, QGuiApplication=QGuiApplication,
          QWidget=QWidget, QHBoxLayout=QHBoxLayout, QVBoxLayout=QVBoxLayout, QListWidget=QListWidget,
          QListWidgetItem=QListWidgetItem, QTreeWidget=QTreeWidget, QTreeWidgetItem=QTreeWidgetItem,
          QPushButton=QPushButton, QMessageBox=FauxQMessageBox, QFrame=QFrame, QAbstractItemView=QAbstractItemView,
          QCheckBox=QCheckBox, QLabel=QLabel, qta=qta, ReglagesApp=None)
exec(mocha, ns)
exec(compile(bloc, "kaggle_block", "exec"), ns)
exec(compile(ecran, "kaggle_ecran", "exec"), ns)
exec(compile(ctrl, "kaggle_ctrl", "exec"), ns)

nb = 0
def ok(cond, msg):
    global nb
    nb += 1
    if not cond:
        print("ECHEC :", msg)
        sys.exit(1)

def pomper(ms=60):
    fin = time.time() + ms / 1000
    while time.time() < fin:
        app.processEvents()
        time.sleep(0.005)


class FauxClient(QObject):
    kaggle_profils_recus = Signal(str, list)
    kaggle_progression_recue = Signal(str, str, str, str, int)
    kaggle_resultat_recu = Signal(str, str, str, bool, str)
    kaggle_ack_recu = Signal(str, str, str, bool, str)
    arreter_execution_profil_resultat = Signal(bool, str, str, str)
    arreter_execution_profil_resultat_reel_recu = Signal(str, str, bool, str)
    def __init__(self):
        super().__init__()
        self.ordres, self.arrets = [], []
    def envoyer_ordre_kaggle(self, type_ordre, id_executant, id_operation, **champs):
        self.ordres.append((type_ordre, id_executant, id_operation, champs))
    def arreter_execution_profil(self, id_executant, nom_profil):
        self.arrets.append((id_executant, nom_profil))


class FauxReglages:
    def __init__(self):
        self.kaggle_correspondance_noms = {}
        self.kaggle_correspondance_date = ""
    def save(self): pass


class FauxGestionnaire:
    connexion_ok = True
    def authentifier(self):
        if not FauxGestionnaire.connexion_ok:
            raise RuntimeError("jeton refuse")
    def lister_datasets(self):
        return [{"ref": "u/ax-a", "slug": "ax-a", "titre": "AX a@x.com", "nom_archive": "a@x.com",
                 "taille_octets": 2048, "cree_le": "2026-01-01T00:00:00Z", "maj_le": "2026-02-01 10:00:00", "prive": True}]


E = ns["ProfilsKaggleScreen"]()
E.definir_reglages(FauxReglages())
C = FauxClient()
K = ns["ControleurKaggle"](C, E, fabrique_gestionnaire=FauxGestionnaire)

# --- connexion / datasets (thread -> signaux Qt)
E.definir_sautoniax_disponibles({"s1": "Alpha", "s2": "Beta"})
E.show()
pomper(300)
ok(E.label_connexion.text() == "Kaggle : connecte" and E.table_datasets.topLevelItemCount() == 1, "connexion + datasets via le controleur")
ok(E.label_quota.text().startswith("Quota prive : 2,0 Ko"), "quota affiche")
ok(sorted(o[1] for o in C.ordres if o[0] == "kaggle_lister_profils") == ["s1", "s2"], "ouverture : listage des profils des deux sAutoniax")
FauxGestionnaire.connexion_ok = False
K.verifier_connexion(); pomper(300)
ok("jeton refuse" in E.label_connexion.text(), "connexion en echec affichee")

# --- liste des profils recue
now = time.time()
C.kaggle_profils_recus.emit("s1", [{"nom": "a", "taille_octets": 10, "modifie_ts": now, "origine_kaggle": None, "actif": True},
                                    {"nom": "b", "taille_octets": 20, "modifie_ts": now, "origine_kaggle": None, "actif": False}])
C.kaggle_profils_recus.emit("s2", [{"nom": "c", "taille_octets": 30, "modifie_ts": now, "origine_kaggle": None, "actif": False}])
ok(("s1", "a") in E._items and ("s1", "b") in E._items and ("s2", "c") in E._items, "arbre rempli")

# --- flux A complet
E.definir_reglages(FauxReglages())
C.ordres.clear()
for cle in [("s1", "a"), ("s1", "b"), ("s2", "c")]:
    E._items[cle].setCheckState(E.COL_PROFIL, Qt.Checked)
    E._items[cle].setCheckState(E.COL_GARDER, Qt.Checked)
E._recalculer_noms()
E._sur_clic_envoyer()
op = E._operation_id
ok(op is not None, "operation demarree")
pomper(50)
listages = [o for o in C.ordres if o[0] == "kaggle_lister_profils" and o[2] == op]
ok(sorted(o[1] for o in listages) == ["s1", "s2"], "flux : listage frais avant l'arret")
C.kaggle_profils_recus.emit("s1", [{"nom": "a", "actif": True}, {"nom": "b", "actif": False}])
C.kaggle_profils_recus.emit("s2", [{"nom": "c", "actif": False}])
ok(C.arrets == [("s1", "a")], "flux : arret demande uniquement pour le profil actif")
envois = [o for o in C.ordres if o[0] == "kaggle_envoyer_profils"]
ok(sorted((o[1], o[3]["profils"][0]["nom_local"]) for o in envois) == [("s1", "b"), ("s2", "c")], "flux : le profil actif attend son arret")
ok(all(len(o[3]["profils"]) == 1 and o[3]["supprimer_local"] is True for o in envois), "flux : 1 profil par ordre, suppression locale transmise")
C.arreter_execution_profil_resultat.emit(True, "s1", "a", "")  # simple accuse de transmission
ok(len([o for o in C.ordres if o[0] == "kaggle_envoyer_profils"]) == 2, "flux : l'accuse de transmission ne vaut pas arret")
C.arreter_execution_profil_resultat_reel_recu.emit("s1", "a", True, "")
C.kaggle_progression_recue.emit(op, "s2", "c", "Envoi vers Kaggle", 40)
ok(E._items[("s2", "c")].text(E.COL_ETAT) == "Envoi vers Kaggle", "progression affichee")
C.kaggle_resultat_recu.emit("autre-op", "s2", "c", True, "ignore")
ok(E._items[("s2", "c")].text(E.COL_ETAT) == "Envoi vers Kaggle", "resultat d'une autre operation ignore")
C.kaggle_resultat_recu.emit(op, "s2", "c", True, "ok")
C.kaggle_resultat_recu.emit(op, "s1", "b", False, "disque plein")
ok(E._operation_id == op, "flux : l'operation continue tant qu'un profil reste")
envois = [o for o in C.ordres if o[0] == "kaggle_envoyer_profils"]
ok(("s1", "a") in [(o[1], o[3]["profils"][0]["nom_local"]) for o in envois], "flux : le profil arrete part apres son tour")
C.kaggle_resultat_recu.emit(op, "s1", "a", True, "ok")
ok(E._operation_id is None, "ecran libere a la fin")
jr = [E.journal.item(r).text() for r in range(E.journal.count())]
ok(any("Alpha / b : ERREUR (disque plein)" in l for l in jr) and any("Beta / c : OK" in l for l in jr)
   and any("Alpha / a : OK" in l for l in jr), "resultats par profil dans le journal (l'arbre est reconstruit a la fin)")

# --- echec de transmission d'un listage
C.ordres.clear()
E._sur_clic_envoyer()
op2 = E._operation_id
ok(op2 is not None, "seconde operation")
C.kaggle_ack_recu.emit("kaggle_lister_profils", "s1", op2, False, "serveurT hors ligne")
C.kaggle_ack_recu.emit("kaggle_lister_profils", "s2", op2, False, "serveurT hors ligne")
ok(E._operation_id is None, "echec de transmission : l'ecran est libere, pas de blocage")

# --- flux B via le controleur
C.ordres.clear()
E.definir_datasets([{"ref": "u/ax-x", "slug": "ax-x", "titre": "AX x@x.com", "nom_archive": "x@x.com", "taille_octets": 1,
                     "cree_le": None, "maj_le": "2026-02-01 10:00:00", "prive": True}])
E.table_datasets.topLevelItem(0).setCheckState(0, Qt.Checked)
E.liste_cibles.item(0).setCheckState(Qt.Checked)
E._rafraichir_boutons()
E._sur_clic_telecharger()
opb = E._operation_id
ok(opb is not None, "telechargement demarre")
dl = [o for o in C.ordres if o[0] == "kaggle_telecharger_profils"]
ok(len(dl) == 1 and dl[0][3]["profils"][0]["slug"] == "ax-x", "ordre de telechargement envoye")
C.kaggle_progression_recue.emit(opb, dl[0][1], "x@x.com", "Extraction", 60)
C.kaggle_resultat_recu.emit(opb, dl[0][1], "x@x.com", True, "ok")
ok(E._operation_id is None, "telechargement termine, ecran libere")
jr = [E.journal.item(r).text() for r in range(E.journal.count())]
ok(any("x@x.com : Extraction 60 %" in l for l in jr) and any("x@x.com : OK" in l for l in jr), "progression et resultat de telechargement")

print(f"OK -- {nb} verifications du controleur passees")

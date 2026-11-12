"""Verifie le cablage de ProfilsScreen (3e sous-onglet, relais des signaux Kaggle,
transmission des sAutoniax) avec des ecrans Cloud/Local factices.
Usage : QT_QPA_PLATFORM=offscreen python3 tests/test_kaggle_cablage.py"""
import os, re, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget

RACINE = Path(__file__).resolve().parent.parent
src = (RACINE / "AutoniaX.pyw").read_text(encoding="utf-8")
i = src.index("class ProfilsScreen(QWidget):")
j = src.index("class ReceptionScreen(QWidget):")
code = src[i:j]
app = QApplication.instance() or QApplication([])

class FauxCloud(QWidget):
    demande_liste_stockage = Signal(); demande_liste_profils_locaux = Signal(); demande_telechargement_meta = Signal(str)
    demande_envoi_profil_vers_sautoniax = Signal(str, str); demande_liste_sautoniax_disponibles = Signal()
    demande_maj_meta_profil = Signal(str, str, bool); demande_renommer_profil_cloud = Signal(str, str)
    demande_suppression_profil_cloud = Signal(list); demande_telechargement_local_profil = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent); self.recus = []
    def definir_sautoniax_disponibles(self, e): self.recus.append(e)

class FauxLocal(QWidget):
    demande_liste_profils_locaux = Signal(); demande_envoi_profil = Signal(str)

class FauxKaggle(QWidget):
    demande_kaggle_verifier_connexion = Signal(); demande_kaggle_actualiser_profils = Signal(list)
    demande_kaggle_actualiser_datasets = Signal(); demande_kaggle_envoyer = Signal(dict); demande_kaggle_telecharger = Signal(dict)
    def __init__(self, parent=None):
        super().__init__(parent); self.recus = []; self.reglages = None
    def definir_sautoniax_disponibles(self, e): self.recus.append(e)
    def definir_reglages(self, r): self.reglages = r

ns = dict(QWidget=QWidget, QVBoxLayout=QVBoxLayout, QTabWidget=QTabWidget, Signal=Signal, Optional=Optional,
          ProfilsCloudScreen=FauxCloud, ProfilsLocalScreen=FauxLocal, ProfilsKaggleScreen=FauxKaggle)
exec(compile(code, "profils_screen", "exec"), ns)
P = ns["ProfilsScreen"]()
titres = [P.sous_onglets.tabText(k) for k in range(P.sous_onglets.count())]
assert titres == ["Profils Cloud", "Profils Local", "Profils Kaggle"], titres
assert P.sous_onglets.widget(2) is P.kaggle_screen

recus = {}
for nom in ("verifier_connexion", "actualiser_profils", "actualiser_datasets", "envoyer", "telecharger"):
    sig = getattr(P, f"demande_kaggle_{nom}")
    sig.connect(lambda *a, n=nom: recus.setdefault(n, []).append(a))
P.kaggle_screen.demande_kaggle_verifier_connexion.emit()
P.kaggle_screen.demande_kaggle_actualiser_profils.emit(["s1"])
P.kaggle_screen.demande_kaggle_actualiser_datasets.emit()
P.kaggle_screen.demande_kaggle_envoyer.emit({"id_operation": "o"})
P.kaggle_screen.demande_kaggle_telecharger.emit({"id_operation": "t"})
assert recus == {"verifier_connexion": [()], "actualiser_profils": [(["s1"],)], "actualiser_datasets": [()],
                 "envoyer": [({"id_operation": "o"},)], "telecharger": [({"id_operation": "t"},)]}, recus
P.definir_sautoniax_disponibles({"s1": "Alpha"})
assert P.cloud_screen.recus == [{"s1": "Alpha"}] and P.kaggle_screen.recus == [{"s1": "Alpha"}], "sAutoniax transmis aux deux ecrans"
P.definir_reglages_kaggle("R")
assert P.kaggle_screen.reglages == "R"
print("OK -- cablage ProfilsScreen verifie")

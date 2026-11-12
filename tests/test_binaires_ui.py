"""Ecran sAutoniax Manager : cases des binaires (coche par defaut), reecriture du notebook, application apres depot.
Usage : QT_QPA_PLATFORM=offscreen python3 tests/test_binaires_ui.py (depuis la racine du depot)"""
import sys, json, re, os, tempfile, urllib.request, urllib.error
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import PySide6.QtWidgets as W, PySide6.QtCore as C, PySide6.QtGui as G
src=open("AutoniaX.pyw",encoding="utf-8").read()
i=src.index("BINAIRES_SAUTONIAX = ("); j=src.index("def get_notebook_serveurt_path()")
a=src.index("class NotebookManagerScreen(QWidget):"); b=src.index("class ServeurTManagerScreen(")
c=src.index("class SAutoniaxManagerScreen("); d=src.index("class SAutoniaxAvecServeurManagerScreen(")
ns={}
for mod in (W,C,G):
    ns.update({k:getattr(mod,k) for k in dir(mod) if not k.startswith("_")})
import qtawesome as qta
ns.update(json=json,re=re,Path=Path,Optional=Optional,dataclass=dataclass,urllib=urllib,qta=qta,Mocha=type("M",(type,),{"__getattr__":lambda s,n:"#888"})("M",(),{}))
tmp=Path(tempfile.mkdtemp()); chemin=tmp/"sAutoniax.ipynb"
import shutil; shutil.copy("sAutoniax.ipynb",chemin)
ns["get_notebook_execution_path"]=lambda: chemin
exec(src[i:j],ns)
try:
    exec(src[a:b],ns); exec(src[c:d],ns)
except Exception as e:
    print("ERR",repr(e)); sys.exit(1)
app=W.QApplication([])
E=None
for _ in range(15):
    try:
        E=ns["SAutoniaxManagerScreen"](); break
    except NameError as e:
        nom=str(e).split("'")[1]; print("stub",nom)
        ns[nom]=type(nom,(W.QWidget,),{"__init__":lambda self,*a,**k: W.QWidget.__init__(self),"__getattr__":lambda self,n: (lambda *a,**k: None)})
    except Exception as e:
        print("INST ERR",repr(e)); sys.exit(1)
nb = 0
def ok(c, m):
    global nb
    nb += 1
    if not c:
        print("ECHEC :", m); sys.exit(1)
def texte(): return chemin.read_text(encoding="utf-8")
ok(all(case.isChecked() for case in E._cases_binaires.values()) and len(E._cases_binaires) == 4, "4 cases, toutes cochees par defaut")
E._cases_binaires["INSTALLER_CHROME"].setChecked(False)
E._cases_binaires["INSTALLER_CLOAKBROWSER"].setChecked(False)
ok("INSTALLER_CHROME = False" in texte() and "INSTALLER_CLOAKBROWSER = False" in texte() and "INSTALLER_CAMOUFOX = True" in texte(), "decocher reecrit le notebook")
ok("Camoufox" in E.label_statut_binaires.text() and "Chrome" not in E.label_statut_binaires.text(), "statut liste les binaires gardes")
# un nouveau notebook depose (tout a True) recoit les cases actuelles
shutil.copy("sAutoniax.ipynb", chemin)
ok("INSTALLER_CHROME = True" in texte(), "notebook fraichement depose : tout a True")
E._apres_depot_notebook()
ok("INSTALLER_CHROME = False" in texte() and "INSTALLER_CLOAKBROWSER = False" in texte(), "apres depot : les cases sont appliquees")
# notebook absent : message, pas de plantage
chemin.unlink()
E._cases_binaires["INSTALLER_TESSERACT"].setChecked(False)
ok("Échec" in E.label_statut_binaires.text(), "notebook absent : message d'echec")
print(f"OK -- {nb} verifications de l'ecran des binaires passees")

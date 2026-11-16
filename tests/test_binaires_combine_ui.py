"""Ecran combine (sAutoniax + ServeurT) : cases des binaires (cochees par defaut), reecriture du notebook combine, application apres depot.
Usage : QT_QPA_PLATFORM=offscreen python3 tests/test_binaires_combine_ui.py (depuis la racine du depot)"""
import sys, json, re, os, tempfile, urllib.request, urllib.error
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import PySide6.QtWidgets as W, PySide6.QtCore as C, PySide6.QtGui as G
src = open("AutoniaX.pyw", encoding="utf-8").read()
i = src.index("BINAIRES_SAUTONIAX = ("); j = src.index("def get_notebook_serveurt_path()")
a = src.index("class NotebookManagerScreen(QWidget):"); b = src.index("class ServeurTManagerScreen(")
d = src.index("class SAutoniaxAvecServeurManagerScreen("); e = src.index("class ReseauScreen(")
ns = {}
for mod in (W, C, G):
    ns.update({k: getattr(mod, k) for k in dir(mod) if not k.startswith("_")})
import qtawesome as qta
ns.update(json=json, re=re, Path=Path, Optional=Optional, dataclass=dataclass, urllib=urllib, qta=qta,
          Mocha=type("M", (type,), {"__getattr__": lambda s, n: "#888"})("M", (), {}))
tmp = Path(tempfile.mkdtemp()); chemin = tmp / "sAutoniaxAvecServeur.ipynb"
import shutil
ns["get_notebook_combine_path"] = lambda: chemin
exec(src[i:j], ns)
exec(src[a:b], ns); exec(src[d:e], ns)
app = W.QApplication([])
nb = 0
def ok(c, m):
    global nb
    nb += 1
    if not c:
        print("ECHEC :", m); sys.exit(1)
def texte(): return chemin.read_text(encoding="utf-8")
def creer():
    for _ in range(15):
        try:
            return ns["SAutoniaxAvecServeurManagerScreen"]()
        except NameError as err:
            nom = str(err).split("'")[1]
            ns[nom] = type(nom, (W.QWidget,), {"__init__": lambda self, *a, **k: W.QWidget.__init__(self),
                                                 "__getattr__": lambda self, n: (lambda *a, **k: None)})
    raise SystemExit("impossible d'instancier l'ecran")
# notebook deja depose avec d'anciennes valeurs (tout a False) : la creation de l'ecran le resynchronise (tout coche)
shutil.copy("sAutoniaxAvecServeur.ipynb", chemin)
anc = re.sub(r"(INSTALLER_\w+) = True", r"\1 = False", texte()); chemin.write_text(anc, encoding="utf-8")
E = creer()
ok(len(E._cases_binaires) == 4 and all(c.isChecked() for c in E._cases_binaires.values()), "4 cases, toutes cochees par defaut")
ok(texte().count("= True") >= 4 and "INSTALLER_CHROME = True" in texte(), "ecran cree : notebook existant resynchronise (tout a True)")
E._cases_binaires["INSTALLER_CHROME"].setChecked(False)
E._cases_binaires["INSTALLER_CLOAKBROWSER"].setChecked(False)
ok("INSTALLER_CHROME = False" in texte() and "INSTALLER_CLOAKBROWSER = False" in texte() and "INSTALLER_CAMOUFOX = True" in texte(), "decocher reecrit le notebook combine")
ok("Camoufox" in E.label_statut_binaires.text() and "Chrome" not in E.label_statut_binaires.text(), "statut liste les binaires gardes")
shutil.copy("sAutoniaxAvecServeur.ipynb", chemin)
E._apres_depot_notebook()
ok("INSTALLER_CHROME = False" in texte() and "INSTALLER_CLOAKBROWSER = False" in texte(), "apres depot : les cases sont appliquees")
chemin.unlink()
E._cases_binaires["INSTALLER_TESSERACT"].setChecked(False)
ok("Échec" in E.label_statut_binaires.text(), "notebook absent : message d'echec, pas de plantage")
# sans notebook au demarrage : rien n'est cree
E2 = creer()
ok(not chemin.exists(), "pas de notebook : l'ecran n'en cree pas")
print(f"OK -- {nb} verifications de l'ecran combine passees")

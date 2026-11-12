"""Cases 'binaires a telecharger' du sAutoniax Manager : reecriture des INSTALLER_* du notebook et
comportement de la cellule d'installation selon ces variables.
Usage : python3 tests/test_binaires_sautoniax.py (depuis la racine du depot)"""
import json, shutil, sys, tempfile, types
from pathlib import Path
from unittest import mock

RACINE = Path(__file__).resolve().parent.parent
src = (RACINE / "AutoniaX.pyw").read_text(encoding="utf-8")
nb = 0
def ok(c, m):
    global nb
    nb += 1
    if not c:
        print("ECHEC :", m); sys.exit(1)

# ---- fonction de configuration -------------------------------------------------------
i = src.index("BINAIRES_SAUTONIAX = (")
j = src.index("def get_notebook_serveurt_path()")
import re
from typing import Optional
ns = dict(json=json, re=re, Path=Path, Optional=Optional, get_notebook_execution_path=lambda: None)
exec(src[i:j], ns)
VARS = [v for v, _ in ns["BINAIRES_SAUTONIAX"]]
ok(VARS == ["INSTALLER_CAMOUFOX", "INSTALLER_CHROME", "INSTALLER_CLOAKBROWSER", "INSTALLER_TESSERACT"], "4 binaires declares")

def lire(chemin): return json.loads(Path(chemin).read_text(encoding="utf-8"))
def code(nbk): return "\n".join("".join(c["source"]) for c in nbk["cells"] if c["cell_type"] == "code")

with tempfile.TemporaryDirectory() as tmp:
    chemin = Path(tmp) / "sAutoniax.ipynb"
    shutil.copy(RACINE / "sAutoniax.ipynb", chemin)
    avant = lire(chemin)
    for v in VARS:
        ok(f"{v} = True" in code(avant), f"{v} present et True par defaut dans le notebook")
    ns["configurer_binaires_notebook"]({v: v == "INSTALLER_CAMOUFOX" for v in VARS}, chemin)
    apres = lire(chemin)
    c = code(apres)
    ok("INSTALLER_CAMOUFOX = True" in c and all(f"{v} = False" in c for v in VARS[1:]), "seul Camoufox reste coche")
    ok(code(avant).replace("= True", "= X").replace("= False", "= X") == c.replace("= True", "= X").replace("= False", "= X"), "rien d'autre ne change")
    ns["configurer_binaires_notebook"]({v: True for v in VARS}, chemin)
    ok(code(lire(chemin)) == code(avant), "tout recoche = notebook d'origine")
    # notebook ancien sans les variables
    vieux = lire(chemin)
    for cell in vieux["cells"]:
        cell["source"] = [l for l in cell["source"] if not l.startswith("INSTALLER_CHROME")]
    chemin.write_text(json.dumps(vieux), encoding="utf-8")
    try:
        ns["configurer_binaires_notebook"]({"INSTALLER_CHROME": False}, chemin); ok(False, "doit lever")
    except ValueError as e:
        ok("INSTALLER_CHROME" in str(e), "message clair si variable absente")
    try:
        ns["configurer_binaires_notebook"]({}, Path(tmp) / "absent.ipynb"); ok(False, "doit lever")
    except FileNotFoundError:
        ok(True, "FileNotFoundError si notebook absent")

# ---- cellule d'installation, executee avec de faux outils -----------------------------------
nbk = lire(RACINE / "sAutoniax.ipynb")
cellule = next("".join(c["source"]) for c in nbk["cells"] if c["cell_type"] == "code" and "def etape_1_installer_dependances" in "".join(c["source"]))

def executer(flags):
    cmds = []
    def faux_run(cmd, **k):
        cmds.append(" ".join(cmd))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")
    fake_cloak = types.ModuleType("cloakbrowser")
    fake_cloak.binary_info = lambda: {"installed": True, "binary_path": "/x/cloak", "version": "1"}
    g = dict(flags)
    import subprocess, importlib, glob
    with mock.patch.object(subprocess, "run", faux_run), \
         mock.patch.object(glob, "glob", lambda p: ["/x/camoufox-bin"]), \
         mock.patch.object(shutil, "which", lambda n: "/x/" + n), \
         mock.patch("os.path.getsize", lambda p: 1048576), \
         mock.patch.dict(sys.modules, {"cloakbrowser": fake_cloak}), \
         mock.patch.object(importlib, "import_module", lambda n, *a, **k: None):
        exec(cellule, g)
        g["_installer_paquets_pip"] = lambda: None
        g["etape_1_installer_dependances"]()
    return " | ".join(cmds)

TOUT = {v: True for v in VARS}
c = executer(TOUT)
ok("camoufox fetch" in c.replace("-m camoufox fetch", "camoufox fetch") and "install chrome" in c and "cloakbrowser install" in c and "tesseract-ocr" in c and "install-deps firefox" in c, "tout coche : tout est installe")
c = executer({**{v: False for v in VARS}, "INSTALLER_CAMOUFOX": True})
ok("camoufox fetch" in c.replace("-m camoufox fetch", "camoufox fetch") and "install-deps firefox" in c, "Camoufox seul : fetch + libs firefox")
ok("chrome" not in c and "cloakbrowser" not in c and "chromium" not in c and "tesseract" not in c, "Camoufox seul : rien d'autre telecharge")
c = executer({v: False for v in VARS})
ok(c == "", "tout decoche : aucune commande de telechargement")
c = executer({**TOUT, "INSTALLER_CHROME": False})
ok("install chrome" not in c and "cloakbrowser install" in c, "Chrome decoche seul")
c = executer({})  # notebook ancien sans variables : comportement d'avant
ok("install chrome" in c and "cloakbrowser install" in c and "tesseract-ocr" in c, "sans variables : tout installe (compatibilite)")
print(f"OK -- {nb} verifications des binaires sAutoniax passees")

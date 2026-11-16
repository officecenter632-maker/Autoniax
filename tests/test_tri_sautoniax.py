"""Tri NUMERIQUE des sAutoniax (sAutoniax-9 avant sAutoniax-10) : table des instances (colonnes 0 et 1) et listes/combos par nom.
Usage : QT_QPA_PLATFORM=offscreen python3 tests/test_tri_sautoniax.py (depuis la racine du depot)"""
import ast, re, sys, os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
src = open("AutoniaX.pyw", encoding="utf-8").read()
tree = ast.parse(src)
nb = 0
def ok(c, m):
    global nb
    nb += 1
    if not c:
        print("ECHEC :", m); sys.exit(1)
ns = {"re": re, "Qt": Qt}
for n in tree.body:
    if isinstance(n, ast.FunctionDef) and n.name == "_cle_tri_numerique_generique":
        exec(ast.get_source_segment(src, n), ns)
cle = ns["_cle_tri_numerique_generique"]
noms = [f"sAutoniax-{k}" for k in (10, 2, 1, 9, 30, 11, 8, 0, 3)]
ok(sorted(noms, key=cle) == [f"sAutoniax-{k}" for k in (0, 1, 2, 3, 8, 9, 10, 11, 30)], "cle numerique : 9 < 10")
# methode reelle InstancesConnecteesScreen._executants_tries, sur un faux self
classe = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "InstancesConnecteesScreen")
meth = next(n for n in classe.body if isinstance(n, ast.FunctionDef) and n.name == "_executants_tries")
import textwrap
exec(textwrap.dedent(ast.get_source_segment(src, meth)), ns)
class Faux:
    _colonne_tri = 0; _ordre_tri = Qt.AscendingOrder; _sautoniax_prets = set()
    def __init__(self, ids): self._executants = {f"sAutoniax-{k}": {"nom": f"sAutoniax-{k}", "role": "executant", "statut": "ok", "connecte_le": ""} for k in ids}
    def _libelle_statut_connectivite(self, i, s): return "ok"
f = Faux((10, 9, 2, 1, 8, 11))
attendu = [f"sAutoniax-{k}" for k in (1, 2, 8, 9, 10, 11)]
ok([i for i, _ in ns["_executants_tries"](f)] == attendu, "table instances colonne 0 : ordre numerique")
f._colonne_tri = 1
ok([i for i, _ in ns["_executants_tries"](f)] == attendu, "table instances colonne 1 (instance_id) : ordre numerique")
f._ordre_tri = Qt.DescendingOrder
ok([i for i, _ in ns["_executants_tries"](f)] == attendu[::-1], "ordre decroissant")
# aucun tri alphabetique restant sur un nom de sAutoniax
for motif in (r"key=lambda kv: kv\[1\]\)", r"key=lambda kv: \(kv\[1\], kv\[0\]\)", r"key=lambda paire: paire\[1\]\n"):
    ok(not re.search(r"sorted\([^\n]*(executant|sautoniax)[^\n]*" + motif, src, re.I), f"plus de tri texte sur les noms ({motif})")
print(f"OK -- {nb} verifications du tri numerique passees")

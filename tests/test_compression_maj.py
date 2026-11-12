"""Test de la compression avant envoi cloud (mise a jour AutoniaX) et de la decompression cote notebook.
Usage : python3 tests/test_compression_maj.py (depuis la racine du depot)"""
import json, lzma, os, subprocess, sys, tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
src = (RACINE / "AutoniaX.pyw").read_text(encoding="utf-8")
i = src.index("def compresser_xz_maximal(")
fn = src[i: src.index("    return compresse\n", i) + len("    return compresse\n")]
import re, time
preset = int(re.search(r"^PRESET_XZ_MAJ = (\d+)", src, re.M).group(1))
ns = {"PRESET_XZ_MAJ": preset}
exec(fn, ns)
nb = 0
def ok(c, m):
    global nb
    nb += 1
    if not c:
        print("ECHEC :", m); sys.exit(1)

data = (RACINE / "AutoniaX.pyw").read_bytes()
xz = ns["compresser_xz_maximal"](data)
ok(lzma.decompress(xz) == data and len(xz) < len(data) / 4, "aller-retour exact et taux > 4x")
with tempfile.NamedTemporaryFile(suffix=".xz", delete=False) as f:
    f.write(xz)
r = subprocess.run(["xz", "-t", f.name], capture_output=True)
os.unlink(f.name)
ok(r.returncode == 0, "xz -t valide l'archive")
ok(xz[:6] == b"\xfd7zXZ\x00" and xz[6:8] == b"\x00\x04", "format XZ, controle CRC64")
ok(lzma.decompress(ns["compresser_xz_maximal"](b"")) == b"", "fichier vide")
ok(preset == 3, "preset rapide (3) retenu")
t0 = time.time(); ns["compresser_xz_maximal"](data); duree = time.time() - t0
ok(duree < 60, f"compression rapide ({duree:.1f}s)")
ok('DRIVE_CLE_AUTONIAX_XZ = DRIVE_PREFIXE_APP + "AutoniaX.pyw.xz"' in src, "cle .xz declaree")
ok('cle_drive = DRIVE_CLE_AUTONIAX_XZ' in src and "compresser_xz_maximal, contenu" in src, "envoi autoniax : cle .xz + compression")

nbk = json.loads((RACINE / "sAutoniax.ipynb").read_text(encoding="utf-8"))
cellule = next("".join(c["source"]) for c in nbk["cells"] if c["cell_type"] == "code" and "def etape_2_telecharger_autoniax" in "".join(c["source"]))
class NoKey(Exception): pass
class Corps:
    def __init__(s, b): s.b = b
    def read(s): return s.b
def essai(objets):
    with tempfile.TemporaryDirectory() as tmp:
        class Client:
            def __init__(s, **k): pass
            def get_object(s, Key):
                if Key not in objets: raise NoKey()
                return {"Body": Corps(objets[Key])}
        g = dict(DriveNoSuchKey=NoKey, _ClientDriveMinimal=Client, DRIVE_CLE_SERVICE_JSON="{}", DRIVE_DOSSIER_RACINE_ID="x", REPERTOIRE_TRAVAIL=tmp)
        exec(cellule, g)
        g["etape_2_telecharger_autoniax"]()
        return (Path(tmp) / "AutoniaX.py").read_bytes()
ok(essai({"App/AutoniaX.pyw.xz": xz}) == data, "notebook : archive .xz decompressee")
ok(essai({"App/AutoniaX.py": b"ancien"}) == b"ancien", "notebook : repli sur l'ancien fichier non compresse")
ok(essai({"App/AutoniaX.pyw.xz": xz, "App/AutoniaX.py": b"perime"}) == data, "notebook : l'archive prime sur l'ancien fichier")
try:
    essai({}); ok(False, "absence totale doit lever")
except RuntimeError as e:
    ok("introuvable" in str(e), "notebook : message clair si rien sur Drive")
print(f"OK -- {nb} verifications de compression passees")

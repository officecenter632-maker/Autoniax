"""Tests du bloc Kaggle (phase 1) contre un faux client en memoire.
Usage : python3 tests/test_kaggle_block.py  (depuis la racine du depot)
Le bloc est extrait de AutoniaX.pyw entre ses deux marqueurs."""
import hashlib, io, json, logging, os, re, shutil, sys, tempfile, time, zipfile
from pathlib import Path
from typing import Optional

RACINE = Path(__file__).resolve().parent.parent
src = (RACINE / "AutoniaX.pyw").read_text(encoding="utf-8")
debut = src.index("# PROFILS KAGGLE (phase 1) -- DEBUT DU BLOC ISOLE")
fin = src.index("# PROFILS KAGGLE (phase 1) -- FIN DU BLOC ISOLE")
bloc = src[src.rfind("\n# ====", 0, debut) + 1: src.index("\n", fin) + 1]

ns = dict(os=os, re=re, json=json, shutil=shutil, tempfile=tempfile, zipfile=zipfile, hashlib=hashlib,
          time=time, logging=logging, Path=Path, Optional=Optional)
logging.disable(logging.CRITICAL)
exec(compile(bloc, "kaggle_block", "exec"), ns)

nb = 0
def ok(cond, msg):
    global nb
    nb += 1
    if not cond:
        print("ECHEC :", msg)
        sys.exit(1)

def leve(exc, f):
    try:
        f()
    except exc as e:
        return e
    return None

# ---- nommage -------------------------------------------------------------
slug = ns["slug_depuis_nom"]
ok(slug("Jean.Dupont@Gmail.com") == "ax-jean-dupont-gmail-com", "slug email")
ok(slug("Élodie  ___ Test") == "ax-elodie-test", "slug accents/tirets fusionnes")
long = slug("a" * 200)
ok(len(long) <= 50 and re.fullmatch(r"ax-a+-[0-9a-f]{8}", long), "slug tronque + hash")
ok(slug("a" * 200) == long and slug("a" * 201) != long, "slug deterministe, hash distinct")
ok(len(slug("x")) >= 6, "slug minimum 6")
ok(len(slug("@@@")) >= 6 and slug("@@@").startswith("ax-"), "slug sans caractere valide")
ok(ns["titre_depuis_nom"]("a@b.com") == "AX a@b.com", "titre")
ok(len(ns["titre_depuis_nom"]("z" * 99)) <= 50, "titre tronque")
ok(ns["nom_archive_depuis_titre"]("AX a@b.com") == "a@b.com", "nom depuis titre")
st = ns["sous_titre_creation"]("2026-11-12T10:00:00Z")
ok(st == "ax;cree=2026-11-12T10:00:00Z" and 20 <= len(st) <= 80, "sous-titre")
ok(ns["date_creation_depuis_sous_titre"](st) == "2026-11-12T10:00:00Z", "relecture date")
ok(ns["date_creation_depuis_sous_titre"]("autre") is None, "sous-titre inconnu")

# ---- correspondance ------------------------------------------------------
vc = ns["valider_correspondance"]
c, av = vc('{" p1 ": " a@b.com ", "p2": "sans-arobase"}')
ok(c == {"p1": "a@b.com", "p2": "sans-arobase"} and len(av) == 1, "validation + avertissement sans @")
for mauvais in ["", "   ", "pas du json", "[1,2]", '"x"', '{"a": 1}', '{"a": ""}', '{"": "x"}', '{"a": null}', '{"a ": "x", "a": "y"}']:
    ok(leve(ns["ErreurCorrespondance"], lambda m=mauvais: vc(m)) is not None, f"refuse {mauvais!r}")

class FauxReglages:
    def __init__(self):
        self.kaggle_correspondance_noms = {"ancien": "old@x.com"}
        self.kaggle_correspondance_date = "2026-01-01T00:00:00Z"
        self.sauvegardes = 0
    def save(self):
        self.sauvegardes += 1

r = FauxReglages()
ok(leve(ns["ErreurCorrespondance"], lambda: ns["importer_correspondance"](r, "{cassé")) is not None, "import invalide leve")
ok(r.kaggle_correspondance_noms == {"ancien": "old@x.com"} and r.sauvegardes == 0, "ancienne correspondance intacte")
ns["importer_correspondance"](r, '{"n1": "e1@x.com"}')
ok(r.kaggle_correspondance_noms == {"n1": "e1@x.com"} and r.sauvegardes == 1, "import remplace (pas de fusion)")
lib, tip = ns["resume_correspondance"](r)
ok(lib.startswith("1 correspondance,") and "n1 -> e1@x.com" in tip, "resume")
ns["importer_correspondance"](r, json.dumps({f"p{i}": f"e{i}@x.com" for i in range(15)}))
ok(len(ns["resume_correspondance"](r)[1].splitlines()) == 11, "infobulle limitee a 10 entrees")
ns["vider_correspondance"](r)
ok(r.kaggle_correspondance_noms == {} and ns["resume_correspondance"](r)[0].startswith("Aucune"), "vider")

# ---- resolution des noms -------------------------------------------------
res = ns["resoudre_noms_archive"](
    [{"nom_local": "A", "garder_nom": True}, {"nom_local": "B", "garder_nom": False},
     {"nom_local": "C", "garder_nom": False}, {"nom_local": "D", "garder_nom": False},
     {"nom_local": "E", "garder_nom": False}],
    {"B": "b@x.com", "D": "dup@x.com", "E": "DUP@x.com"})
ok(res[0]["nom_archive"] == "A" and not res[0]["erreur"], "garder le nom")
ok(res[1]["nom_archive"] == "b@x.com" and not res[1]["erreur"], "nom du JSON")
ok(res[2]["erreur"] and "Absent" in res[2]["erreur"], "absent du JSON, case decochee")
ok(res[3]["erreur"] and res[4]["erreur"], "doublon d'email : les deux bloques")
res2 = ns["resoudre_noms_archive"]([{"nom_local": "x.y", "garder_nom": True}, {"nom_local": "x-y", "garder_nom": True}], {})
ok(all(r["erreur"] and "Collision" in r["erreur"] for r in res2), "collision d'identifiant")

# ---- repartition ---------------------------------------------------------
rep = ns["repartir_equitablement"](list(range(10)), ["s3", "s1", "s2"])
ok(sorted(len(v) for v in rep.values()) == [3, 3, 4] and len(rep["s1"]) == 4, "10 profils sur 3 -> 4,3,3")
ok(rep["s1"] == [0, 3, 6, 9], "tourniquet dans l'ordre d'affichage")


# ---- aides pures de la phase 2 -------------------------------------------
ok(ns["formater_taille_octets"](512) == "512 o" and ns["formater_taille_octets"](5 * 1024 ** 2) == "5,0 Mo"
   and ns["formater_taille_octets"](None) == "?", "format des tailles")
ok(ns["formater_horodatage"]("2026-11-12T10:00:00Z") == "2026-11-12 10:00" and ns["formater_horodatage"](None) == "", "format des dates")
td = ns["trier_datasets"]
dd = [{"slug": "a", "cree_le": "2026-01-01T00:00:00Z", "maj_le": "2026-11-01 10:00:00"},
      {"slug": "b", "cree_le": "2026-06-01T00:00:00Z", "maj_le": "2026-03-01 10:00:00"},
      {"slug": "c", "cree_le": None, "maj_le": None}]
ok([d["slug"] for d in td(dd, "maj")] == ["a", "b", "c"] and [d["slug"] for d in td(dd, "cree")] == ["b", "a", "c"], "tri maj/cree, plus recent d'abord, inconnus en dernier")
ok([d["slug"] for d in td(dd)] == ["a", "b", "c"], "tri par defaut : mise a jour")
L = [{"id_executant": "s1", "nom_executant": "A", "nom_local": "x", "garder_nom": True, "coche": True, "modifie_ts": 100},
     {"id_executant": "s2", "nom_executant": "B", "nom_local": "x", "garder_nom": True, "coche": True, "modifie_ts": 200},
     {"id_executant": "s1", "nom_executant": "A", "nom_local": "y", "garder_nom": False, "coche": True, "modifie_ts": 1},
     {"id_executant": "s1", "nom_executant": "A", "nom_local": "z", "garder_nom": True, "coche": False, "modifie_ts": 1}]
pl = ns["planifier_envoi"](L, {})
ok(pl[0]["ignore"] and not pl[0]["partira"] and pl[1]["partira"] and pl[1]["avertissement"], "meme profil sur 2 sAutoniax : la copie recente part")
ok(pl[2]["erreur"] and not pl[2]["partira"], "decoche et absent du JSON : bloque")
ok(not pl[3]["partira"] and not pl[3]["erreur"], "ligne non cochee : ignoree sans erreur")
pl2 = ns["planifier_envoi"](L, {"y": "y@x.com"})
ok(pl2[2]["partira"] and pl2[2]["nom_archive"] == "y@x.com", "present dans le JSON : part")
ok(ns["planifier_envoi"]([dict(L[0], modifie_ts=5), dict(L[1], modifie_ts=5)], {})[0]["partira"], "egalite de date : la premiere ligne gagne")
rs = ns["resume_plan_envoi"](pl2, L, {slug("x")}, True)
ok(rs["total"] == 2 and rs["sautoniax"] == 2 and rs["maj"] == 1 and rs["crees"] == 1 and rs["ignores"] == 1, "resume du plan")
ok(ns["resume_plan_envoi"](pl2, L, None, False)["inconnus"], "resume : liste Kaggle non chargee")

class ReglagesQuiEchoue(FauxReglages):
    def save(self):
        raise OSError("disque plein")
rq = ReglagesQuiEchoue()
e = leve(ns["ErreurCorrespondance"], lambda: ns["importer_correspondance"](rq, '{"a": "a@x.com"}'))
ok(e is not None and rq.kaggle_correspondance_noms == {"ancien": "old@x.com"}, "echec d'ecriture : ancienne correspondance restauree")
ok(len(vc('{"a": "m@x.com", "b": "M@x.com"}')[1]) == 1, "avertissement : meme email pour deux profils")

# ---- faux client Kaggle --------------------------------------------------
class Obj:
    def __init__(self, **kw):
        self.__dict__.update(kw)

class FauxKaggle:
    def __init__(self):
        self.datasets = {}  # ref -> dict(title, subtitle, versions, fichiers)
        self.appels = []
        self.pannes = 0
        self.statuts = ["queued", "ready"]
        self.zip_decompresse = False
        self.taille_corrompue = False
    def authenticate(self):
        self.appels.append("auth")
    def dataset_status(self, ref):
        if ref not in self.datasets:
            e = Exception("404 Not Found")
            e.response = Obj(status_code=404)
            raise e
        d = self.datasets[ref]
        return d["statuts"].pop(0) if len(d["statuts"]) > 1 else d["statuts"][0]
    def _lire(self, folder):
        meta = json.load(open(os.path.join(folder, "dataset-metadata.json"), encoding="utf-8"))
        fich = {f: os.path.getsize(os.path.join(folder, f)) for f in os.listdir(folder) if f != "dataset-metadata.json"}
        if self.taille_corrompue:
            fich = {k: v + 1 for k, v in fich.items() if k.endswith(".zip")}
        if self.zip_decompresse:
            fich = {"contenu.txt": 5}
        return meta, fich
    def dataset_create_new(self, folder, public=False, quiet=False, convert_to_csv=True, dir_mode="skip", **kw):
        if self.pannes > 0:
            self.pannes -= 1
            raise RuntimeError("panne reseau simulee")
        meta, fich = self._lire(folder)
        assert public is False and convert_to_csv is False
        self.datasets[meta["id"]] = {"title": meta["title"], "subtitle": meta.get("subtitle"), "versions": 1,
                                     "fichiers": fich, "statuts": list(self.statuts), "prive": True,
                                     "maj": "2026-11-12 10:00:00"}
        self.appels.append("create")
        return Obj(error="")
    def dataset_create_version(self, folder, version_notes, quiet=False, convert_to_csv=True,
                               delete_old_versions=False, dir_mode="skip", **kw):
        meta, fich = self._lire(folder)
        assert delete_old_versions is True and convert_to_csv is False
        d = self.datasets[meta["id"]]
        d["versions"] = 1  # delete_old_versions : une seule version conservee
        d["title"] = meta["title"]
        if meta.get("subtitle"):
            d["subtitle"] = meta["subtitle"]
        d["fichiers"] = fich
        d["statuts"] = list(self.statuts)
        self.appels.append("version")
        return Obj(error="")
    def dataset_list(self, user=None, mine=False, page=1, **kw):
        if page > 1:
            return []
        return [Obj(ref=r, title=d["title"], subtitle=d["subtitle"], total_bytes=sum(d["fichiers"].values()),
                    last_updated=d["maj"], is_private=True) for r, d in self.datasets.items()] + \
               [Obj(ref="mikereichlin/autre-projet", title="Autre", subtitle="", total_bytes=1, last_updated=None, is_private=True)]
    def dataset_list_files(self, ref, **kw):
        return Obj(dataset_files=[Obj(name=n, total_bytes=t) for n, t in self.datasets[ref]["fichiers"].items()])
    def dataset_download_files(self, ref, path=None, force=False, quiet=True, unzip=False, **kw):
        d = self.datasets[ref]
        if self.zip_decompresse:
            with zipfile.ZipFile(os.path.join(path, "enveloppe.zip"), "w") as z:
                z.writestr("contenu.txt", "hello")
            return
        arch = [n for n in d["fichiers"] if n.endswith(".zip")][0]
        shutil.copyfile(d["contenu_zip"], os.path.join(path, arch))

def faire_gestionnaire(api):
    return ns["GestionnaireKaggle"](api=api, pause=lambda s: None)

def faux_zipper_factory(racine):
    def zipper(chemin):
        sortie = Path(racine) / (os.path.basename(chemin) + ".zip")
        with zipfile.ZipFile(sortie, "w") as z:
            for dp, _, fs in os.walk(chemin):
                for f in fs:
                    z.write(os.path.join(dp, f), os.path.relpath(os.path.join(dp, f), chemin))
        return sortie
    return zipper

with tempfile.TemporaryDirectory() as tmp:
    profils = Path(tmp) / "profils"
    (profils / "Alice" / "Default").mkdir(parents=True)
    (profils / "Alice" / "Default" / "Cookies").write_text("cookie")
    zip_tmp = Path(tmp) / "zips"
    zip_tmp.mkdir()
    zipper = faux_zipper_factory(zip_tmp)

    api = FauxKaggle()
    g = faire_gestionnaire(api)
    g.authentifier()
    ok(not g.dataset_existe("mikereichlin/ax-a-b-com"), "dataset inexistant (404)")

    # creation, avec etapes de progression et suppression locale apres verification
    etapes = []
    r1 = g.envoyer_profil(str(profils / "Alice"), "a@b.com", nom_local="Alice", email="a@b.com", instance="s1",
                          supprimer_local=True, zipper=zipper, progression=lambda e, p: etapes.append((e, p)))
    ref = "mikereichlin/ax-a-b-com"
    ok(r1["ok"] and r1["cree"] and "create" in api.appels, "creation du dataset")
    ok(api.datasets[ref]["subtitle"].startswith("ax;cree="), "sous-titre de creation ecrit")
    ok(not (profils / "Alice").exists() and r1["dossier_supprime"], "dossier local supprime apres verification")
    ok(not list(zip_tmp.iterdir()), "zip temporaire supprime")
    ok(etapes[-1] == ("Termine", 100) and [p for _, p in etapes] == sorted(p for _, p in etapes), "progression croissante")
    ok(not [p for p in Path(tempfile.gettempdir()).glob("ax_kaggle_*")], "dossier temporaire nettoye")
    creation = api.datasets[ref]["subtitle"]
    # garde une copie du zip pour tester le telechargement
    contenu = Path(tmp) / "contenu.zip"
    with zipfile.ZipFile(contenu, "w") as z:
        z.writestr("Default/Cookies", "cookie")
    api.datasets[ref]["contenu_zip"] = str(contenu)
    api.datasets[ref]["fichiers"] = {"a@b.com.zip": contenu.stat().st_size, "meta.json": 10}

    # mise a jour : date de creation conservee, une seule version
    (profils / "Alice" / "Default").mkdir(parents=True)
    time.sleep(1.1)
    r2 = g.envoyer_profil(str(profils / "Alice"), "a@b.com", nom_local="Alice", email="a@b.com", instance="s1",
                          supprimer_local=False, zipper=zipper)
    ok(not r2["cree"] and "version" in api.appels, "mise a jour d'un dataset existant")
    ok(api.datasets[ref]["subtitle"] == creation, "date de creation jamais ecrasee")
    ok(api.datasets[ref]["versions"] == 1, "une seule version conservee")
    ok((profils / "Alice").exists(), "pas de suppression si case decochee")

    # retries : 2 pannes puis succes ; 3 pannes = echec sans suppression
    api.pannes = 2
    (profils / "Bob").mkdir()
    (profils / "Bob" / "f").write_text("x")
    r3 = g.envoyer_profil(str(profils / "Bob"), "bob@x.com", zipper=zipper, supprimer_local=True)
    ok(r3["ok"] and not (profils / "Bob").exists(), "retry apres 2 pannes")
    api.pannes = 3
    (profils / "Carl").mkdir()
    (profils / "Carl" / "f").write_text("x")
    e = leve(ns["ErreurKaggle"], lambda: g.envoyer_profil(str(profils / "Carl"), "carl@x.com", zipper=zipper, supprimer_local=True))
    ok(e is not None and "3 tentatives" in str(e), "echec apres 3 tentatives")
    ok((profils / "Carl").exists(), "rien supprime en cas d'echec")
    ok(not list(zip_tmp.iterdir()), "zip temporaire nettoye meme en cas d'echec")

    # taille incorrecte -> pas de suppression
    api.taille_corrompue = True
    (profils / "Dan").mkdir()
    (profils / "Dan" / "f").write_text("x")
    e = leve(ns["ErreurKaggle"], lambda: g.envoyer_profil(str(profils / "Dan"), "dan@x.com", zipper=zipper, supprimer_local=True))
    ok(e is not None and (profils / "Dan").exists(), "verification de taille : pas de suppression")
    api.taille_corrompue = False

    # delai depasse
    ns["DELAI_PRET_KAGGLE_S"] = 0.05
    api.statuts = ["queued"]
    (profils / "Eve").mkdir()
    (profils / "Eve" / "f").write_text("x")
    e = leve(ns["ErreurKaggle"], lambda: g.envoyer_profil(str(profils / "Eve"), "eve@x.com", zipper=zipper, supprimer_local=True))
    ok(e is not None and (profils / "Eve").exists(), "Kaggle jamais pret : pas de suppression")
    ns["DELAI_PRET_KAGGLE_S"] = 600
    api.statuts = ["queued", "ready"]

    # liste + quota
    liste = g.lister_datasets()
    ok({d["slug"] for d in liste} >= {"ax-a-b-com", "ax-bob-x-com"} and all(d["slug"].startswith("ax-") for d in liste),
       "liste filtree sur le prefixe ax-")
    a = next(d for d in liste if d["slug"] == "ax-a-b-com")
    ok(a["nom_archive"] == "a@b.com" and a["cree_le"] and a["prive"], "champs du listing")
    ok(g.quota_utilise_octets(liste) == sum(d["taille_octets"] for d in liste), "quota")

    # telechargement
    cible = Path(tmp) / "recu"
    r4 = g.telecharger_profil("ax-a-b-com", str(cible), "a@b.com", "a@b.com")
    ok(r4["ok"] and (cible / "a@b.com" / "Default" / "Cookies").read_text() == "cookie", "telechargement + extraction")
    ok(ns["lire_origines_kaggle"](str(cible)) == {"a@b.com": "a@b.com"}, "_kaggle_origine.json ecrit")
    (cible / "a@b.com" / "vieux").write_text("v")
    g.telecharger_profil("ax-a-b-com", str(cible), "a@b.com", "a@b.com")
    ok(not (cible / "a@b.com" / "vieux").exists(), "ecrasement d'un profil du meme nom")

    # zip decompresse par Kaggle
    api.zip_decompresse = True
    r5 = g.telecharger_profil("ax-a-b-com", str(cible), "decomp", "a@b.com")
    ok((cible / "decomp" / "contenu.txt").read_text() == "hello", "cas Kaggle qui decompresse")
    api.zip_decompresse = False

    # archive malveillante
    mal = Path(tmp) / "mal.zip"
    with zipfile.ZipFile(mal, "w") as z:
        z.writestr("../../evasion.txt", "x")
    api.datasets[ref]["contenu_zip"] = str(mal)
    e = leve(ns["ErreurKaggle"], lambda: g.telecharger_profil("ax-a-b-com", str(cible), "mal", "a@b.com"))
    ok(e is not None and "suspect" in str(e) and not (Path(tmp) / "evasion.txt").exists(), "chemin suspect refuse")

    # lecture d'un fichier d'origine corrompu
    (cible / "_kaggle_origine.json").write_text("n'importe quoi")
    ok(ns["lire_origines_kaggle"](str(cible)) == {}, "origine corrompue ignoree")

print(f"OK -- {nb} verifications passees")

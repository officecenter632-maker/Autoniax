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
ok(slug("Jean.Dupont@Gmail.com") == "ax-jean-dupont-gmail", "slug email")
for brut in ("ADRESSE_DU_COMPTE@domaine.com", "Jean.Dupont@Gmail.com", "a@b.com", "x.y+z@mail.fr"):
    relu = ns["nom_archive_depuis_titre"](ns["titre_depuis_nom"](brut))  # nom relu apres telechargement
    ok(slug(relu) == slug(brut) and ns["titre_depuis_nom"](relu) == ns["titre_depuis_nom"](brut),
       f"re-envoi d'un profil restaure : meme dataset ({brut})")
ok(slug("Élodie  ___ Test") == "ax-elodie-test", "slug accents/tirets fusionnes")
long = slug("a" * 200)
ok(len(long) <= 50 and re.fullmatch(r"ax-a+-[0-9a-f]{8}", long), "slug tronque + hash")
ok(slug("a" * 200) == long and slug("a" * 201) != long, "slug deterministe, hash distinct")
ok(len(slug("x")) >= 6, "slug minimum 6")
ok(len(slug("@@@")) >= 6 and slug("@@@").startswith("ax-"), "slug sans caractere valide")
ok(ns["titre_depuis_nom"]("a@b.com") == "AX a_b", "titre : .com retire, @ remplace par _")
ok(ns["titre_depuis_nom"]("jo.doe@mail.fr") == "AX jo_doe_mail_fr", "titre : autres caracteres speciaux remplaces par _")
ok("@" not in ns["titre_depuis_nom"]("ADRESSE_DU_COMPTE@domaine.com") and ns["titre_depuis_nom"]("ADRESSE_DU_COMPTE@domaine.com") == "AX ADRESSE_DU_COMPTE_domaine", "titre : cas du journal")
ok(len(ns["titre_depuis_nom"]("z" * 99)) <= 50, "titre tronque")
ok(ns["nom_archive_depuis_titre"]("AX a_b") == "a_b", "nom depuis titre")
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
        if getattr(self, "forbidden_au_lieu_de_404", False) or getattr(self, "forbidden_toujours", False):
            if ref not in self.datasets or getattr(self, "forbidden_toujours", False):
                e = Exception("403 Client Error: Forbidden for url: https://api.kaggle.com/v1/datasets.DatasetApiService/GetDatasetStatus")
                e.response = Obj(status_code=403)
                raise e
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
        if mine and user:
            raise ValueError("Cannot specify both mine and a user")
        if page > 1:
            return []
        return [Obj(ref=r, title=d["title"], subtitle=d["subtitle"], total_bytes=(0 if getattr(self, "taille_liste_zero", False) else sum(d["fichiers"].values())),
                    last_updated=d["maj"], is_private=True) for r, d in self.datasets.items()] + \
               [Obj(ref="mikereichlin/autre-projet", title="Autre", subtitle="", total_bytes=1, last_updated=None, is_private=True)]
    def dataset_list_files(self, ref, page_token=None, page_size=20, **kw):
        tous = [Obj(name=n, total_bytes=t) for n, t in self.datasets[ref]["fichiers"].items()]
        if getattr(self, "pages_de", 0):
            debut = int(page_token or 0)
            fin = debut + self.pages_de
            return Obj(dataset_files=tous[debut:fin], next_page_token=(str(fin) if fin < len(tous) else None))
        return Obj(dataset_files=tous)
    def dataset_download_file(self, ref, file_name, path=None, force=False, quiet=True, **kw):
        if getattr(self, "fichier_par_fichier_interdit", False):
            e = Exception("404 Client Error: Not Found for url: https://api.kaggle.com/v1/datasets.DatasetApiService/DownloadDataset")
            e.response = Obj(status_code=404, text='{"code":5,"message":"Not found"}')
            raise e
        shutil.copyfile(self.datasets[ref]["contenu_zip"], os.path.join(path, "telechargement" if getattr(self, "nom_sans_extension", False) else file_name))
    def dataset_download_files(self, ref, path=None, force=False, quiet=True, unzip=False, **kw):
        if getattr(self, "bundle_404", False):
            e = Exception("404 Client Error: Not Found for url: https://api.kaggle.com/v1/datasets.DatasetApiService/DownloadDataset")
            e.response = Obj(status_code=404)
            raise e
        d = self.datasets[ref]
        if getattr(self, "telechargement_vide", False):
            return
        if getattr(self, "zip_dans_sous_dossier", False):
            arch = [n for n in d["fichiers"] if n.endswith(".zip")][0]
            os.makedirs(os.path.join(path, "sous"), exist_ok=True)
            shutil.copyfile(d["contenu_zip"], os.path.join(path, "sous", arch))
            return
        if getattr(self, "enveloppe_avec_zip", False):
            arch = [n for n in d["fichiers"] if n.endswith(".zip")][0]
            with zipfile.ZipFile(os.path.join(path, "enveloppe.zip"), "w") as z:
                z.write(d["contenu_zip"], arch)
                z.writestr("meta.json", "{}")
            return
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
    ok(not g.dataset_existe("mikereichlin/ax-a-b"), "dataset inexistant (404)")
    # 403 au lieu de 404 pour un dataset pas encore cree : tranche via la liste de ses propres datasets
    api.forbidden_au_lieu_de_404 = True
    ok(not g.dataset_existe("mikereichlin/ax-a-b"), "403 sur dataset inexistant : traite comme absent")
    api.forbidden_au_lieu_de_404 = False

    # creation, avec etapes de progression et suppression locale apres verification
    etapes = []
    r1 = g.envoyer_profil(str(profils / "Alice"), "a@b.com", nom_local="Alice", email="a@b.com", instance="s1",
                          supprimer_local=True, zipper=zipper, progression=lambda e, p: etapes.append((e, p)))
    ref = "mikereichlin/ax-a-b"
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

    # jeton sans droit sur GetDatasetStatus : 403 permanent -> repli sur la liste des fichiers
    api.forbidden_toujours = True
    (profils / "Fay").mkdir()
    (profils / "Fay" / "f").write_text("x")
    rf = g.envoyer_profil(str(profils / "Fay"), "fay@x.com", nom_local="Fay", email="fay@x.com", instance="s1",
                          supprimer_local=True, zipper=zipper)
    ok(rf["ok"] and rf["cree"] and not (profils / "Fay").exists(), "403 permanent sur le statut : envoi termine via la liste des fichiers")
    api.forbidden_toujours = False

    # liste + quota
    liste = g.lister_datasets()
    ok({d["slug"] for d in liste} >= {"ax-a-b", "ax-bob-x"} and all(d["slug"].startswith("ax-") for d in liste),
       "liste filtree sur le prefixe ax-")
    a = next(d for d in liste if d["slug"] == "ax-a-b")
    ok(a["nom_archive"] == "a_b" and a["cree_le"] and a["prive"], "champs du listing")
    ok(g.quota_utilise_octets(liste) == sum(d["taille_octets"] for d in liste), "quota")

    # telechargement
    cible = Path(tmp) / "recu"
    r4 = g.telecharger_profil("ax-a-b", str(cible), "a@b.com", "a@b.com")
    ok(r4["ok"] and (cible / "a@b.com" / "Default" / "Cookies").read_text() == "cookie", "telechargement + extraction")
    ok(ns["lire_origines_kaggle"](str(cible)) == {"a@b.com": "a@b.com"}, "_kaggle_origine.json ecrit")
    (cible / "a@b.com" / "vieux").write_text("v")
    g.telecharger_profil("ax-a-b", str(cible), "a@b.com", "a@b.com")
    ok(not (cible / "a@b.com" / "vieux").exists(), "ecrasement d'un profil du meme nom")

    # 404 sur le telechargement du dataset complet : repli fichier par fichier ; nom d'archive derive du titre (a_b)
    api.bundle_404 = True
    r4b = g.telecharger_profil("ax-a-b", str(cible), "repli", "a_b")
    ok(r4b["ok"] and (cible / "repli" / "Default" / "Cookies").read_text() == "cookie", "404 sur le zip complet : repli fichier par fichier")
    api.fichier_par_fichier_interdit = True
    e = leve(ns["ErreurKaggle"], lambda: g.telecharger_profil("ax-a-b", str(cible), "repli2", "a_b"))
    ok(e is not None and "repli fichier par fichier" in str(e) and "Not found" in str(e), "les deux voies refusees : erreur detaillee (reponse Kaggle incluse)")
    api.bundle_404 = False
    api.fichier_par_fichier_interdit = False

    # fichier recu sans extension .zip (repli fichier par fichier) : reconnu par son contenu
    api.bundle_404 = True
    api.nom_sans_extension = True
    r4c = g.telecharger_profil("ax-a-b", str(cible), "sansext", "a_b")
    ok(r4c["ok"] and (cible / "sansext" / "Default" / "Cookies").read_text() == "cookie", "fichier sans extension .zip reconnu")
    api.bundle_404 = False
    api.nom_sans_extension = False
    # enveloppe Kaggle (zip contenant meta.json + l'archive dont le nom differe du nom deduit du titre)
    api.enveloppe_avec_zip = True
    r4d = g.telecharger_profil("ax-a-b", str(cible), "envel", "a_b")
    ok(r4d["ok"] and (cible / "envel" / "Default" / "Cookies").read_text() == "cookie" and not (cible / "envel" / "meta.json").exists(),
       "enveloppe : archive interne retrouvee malgre un nom different")
    api.enveloppe_avec_zip = False

    # liste de fichiers paginee : toutes les pages sont lues (taille totale exacte)
    api.datasets[ref]["fichiers"].update({f"extra{i}.bin": 1000 for i in range(5)})
    api.pages_de = 2
    attendu_total = sum(api.datasets[ref]["fichiers"].values())
    ok(sum(t for _, t in g._fichiers_dataset(ref)) == attendu_total and len(g._fichiers_dataset(ref)) == len(api.datasets[ref]["fichiers"]),
       "liste de fichiers paginee : toutes les pages lues")
    api.taille_liste_zero = True
    ok(next(d for d in g.lister_datasets() if d["ref"] == ref)["taille_octets"] == attendu_total, "taille affichee = somme de toutes les pages")
    api.taille_liste_zero = False
    api.pages_de = 0
    for i in range(5):
        del api.datasets[ref]["fichiers"][f"extra{i}.bin"]
    # archive recue dans un sous-dossier : trouvee quand meme
    api.zip_dans_sous_dossier = True
    r4e = g.telecharger_profil("ax-a-b", str(cible), "sousdos", "a_b")
    ok(r4e["ok"] and (cible / "sousdos" / "Default" / "Cookies").read_text() == "cookie", "archive dans un sous-dossier trouvee")
    api.zip_dans_sous_dossier = False
    # telechargement qui ne depose rien : erreur de diagnostic complete
    api.telechargement_vide = True
    e = leve(ns["ErreurKaggle"], lambda: g.telecharger_profil("ax-a-b", str(cible), "vide", "a_b"))
    ok(e is not None and "recus : aucun" in str(e) and "voie : dataset complet" in str(e) and "sur Kaggle :" in str(e)
       and "bibliotheque kaggle" in str(e), "aucun fichier recu : diagnostic (voie, recus, fichiers sur Kaggle, version)")
    api.telechargement_vide = False
    # taille absente de la liste des datasets : lue dans la liste des fichiers
    api.taille_liste_zero = True
    liste0 = g.lister_datasets()
    ok(liste0 and all(d["taille_octets"] > 0 for d in liste0), "taille 0 dans la liste : relue via la liste des fichiers")
    api.taille_liste_zero = False

    # zip decompresse par Kaggle
    api.zip_decompresse = True
    r5 = g.telecharger_profil("ax-a-b", str(cible), "decomp", "a@b.com")
    ok((cible / "decomp" / "contenu.txt").read_text() == "hello", "cas Kaggle qui decompresse")
    api.zip_decompresse = False

    # archive malveillante
    mal = Path(tmp) / "mal.zip"
    with zipfile.ZipFile(mal, "w") as z:
        z.writestr("../../evasion.txt", "x")
    api.datasets[ref]["contenu_zip"] = str(mal)
    e = leve(ns["ErreurKaggle"], lambda: g.telecharger_profil("ax-a-b", str(cible), "mal", "a@b.com"))
    ok(e is not None and "suspect" in str(e) and not (Path(tmp) / "evasion.txt").exists(), "chemin suspect refuse")

    # lecture d'un fichier d'origine corrompu
    (cible / "_kaggle_origine.json").write_text("n'importe quoi")
    ok(ns["lire_origines_kaggle"](str(cible)) == {}, "origine corrompue ignoree")

# ---- phase 3 : cote sAutoniax (scan, traitement d'un envoi) ---------------
with tempfile.TemporaryDirectory() as tmp:
    dp = Path(tmp) / "sautoniax_profils"
    (dp / "Alice" / "Default").mkdir(parents=True)
    (dp / "Alice" / "Default" / "Cookies").write_text("cookie")
    (dp / "Bob").mkdir()
    (dp / "Bob" / "f.txt").write_text("xx")
    (dp / "Vide").mkdir()
    (dp / "_kaggle_origine.json").write_text(json.dumps({"Bob": "bob@x.com"}))
    sc = ns["scanner_profils_kaggle"](str(dp), {"Bob"})
    ok([p["nom"] for p in sc] == ["Alice", "Bob"], "scan : dossiers vides et fichiers ignores")
    ok(sc[0]["taille_octets"] == 6 and sc[0]["modifie_ts"] > 0 and not sc[0]["actif"] and sc[0]["origine_kaggle"] is None, "scan : taille, date, inactif")
    ok(sc[1]["actif"] and sc[1]["origine_kaggle"] == "bob@x.com", "scan : actif + origine Kaggle")
    ok(ns["scanner_profils_kaggle"](str(Path(tmp) / "absent"), set()) == [], "scan : dossier absent")

    zt = Path(tmp) / "zips"; zt.mkdir()
    zp = faux_zipper_factory(zt)
    api3 = FauxKaggle()
    g3 = faire_gestionnaire(api3)
    te = ns["traiter_envoi_kaggle"]
    r = te(g3, str(dp), {"nom_local": "Bob", "nom_archive": "bob@x.com"}, True, {"Bob"}, zipper=zp)
    ok(r[0] is False and "en cours d'execution" in r[1] and (dp / "Bob").exists() and not api3.datasets, "profil actif : refuse, rien envoye ni supprime")
    for mauvais in ("../Alice", "a/b", "..", ""):
        r = te(g3, str(dp), {"nom_local": mauvais, "nom_archive": "x@y.com"}, True, set(), zipper=zp)
        ok(r[0] is False, f"nom de profil refuse : {mauvais!r}")
    r = te(g3, str(dp), {"nom_local": "Zed", "nom_archive": "z@y.com"}, True, set(), zipper=zp)
    ok(r[0] is False and "introuvable" in r[1], "dossier introuvable")
    r = te(g3, str(dp), {"nom_local": "Alice", "nom_archive": "alice@x.com", "email": "alice@x.com"}, False, set(), instance="s1", zipper=zp)
    ok(r[0] is True and (dp / "Alice").exists() and "mikereichlin/ax-alice-x" in api3.datasets and "cree" in r[1], "envoi OK sans suppression : dossier conserve")
    r = te(g3, str(dp), {"nom_local": "Alice", "nom_archive": "alice@x.com"}, True, set(), zipper=zp)
    ok(r[0] is True and not (dp / "Alice").exists() and api3.datasets["mikereichlin/ax-alice-x"]["versions"] == 1, "mise a jour + suppression apres verification, une seule version")
    api3.pannes = 99
    r = te(g3, str(dp), {"nom_local": "Bob", "nom_archive": "bob@x.com"}, True, set(), zipper=zp)
    ok(r[0] is False and (dp / "Bob").exists() and not list(zt.iterdir()), "echec reseau : rien supprime, temporaires nettoyes")

# ---- phase 3 : flux A cote pilote (orchestration pure) ---------------------
class Horloge:
    def __init__(self): self.t = 1000.0
    def __call__(self): return self.t

def faire_flux(profils, **kw):
    ev = {"lister": [], "arreter": [], "envoyer": [], "notif": [], "fin": 0}
    h = Horloge()
    f = ns["FluxEnvoiKaggle"](
        profils, lister=lambda i: ev["lister"].append(i), arreter=lambda i, n: ev["arreter"].append((i, n)),
        envoyer=lambda i, p: ev["envoyer"].append((i, p["nom_local"])),
        notifier=lambda i, n, o, m: ev["notif"].append((i, n, o, m)),
        terminer=lambda: ev.__setitem__("fin", ev["fin"] + 1), horloge=h, **kw)
    return f, ev, h

def P(i, n): return {"id_executant": i, "nom_local": n, "nom_archive": n + "@x.com"}

f, ev, h = faire_flux([P("s1", "a"), P("s1", "b"), P("s2", "c")])
f.demarrer()
ok(sorted(ev["lister"]) == ["s1", "s2"] and not ev["envoyer"], "flux : un listage par sAutoniax, rien n'est envoye avant")
f.sur_liste("s1", [{"nom": "a", "actif": True}, {"nom": "b", "actif": False}])
ok(ev["arreter"] == [("s1", "a")] and ev["envoyer"] == [("s1", "b")], "flux : profil actif arrete, profil inactif part sans arret")
f.sur_liste("s2", [{"nom": "c", "actif": False}])
ok(("s2", "c") in ev["envoyer"] and ("s1", "a") not in ev["envoyer"], "flux : un profil dont l'arret n'est pas confirme ne part pas")
f.sur_arret("s1", "a", True)
ok(("s1", "a") not in ev["envoyer"], "flux : au plus 1 envoi a la fois par sAutoniax")
f.sur_resultat("s1", "b", True, "ok")
ok(("s1", "a") in ev["envoyer"], "flux : le profil arrete part des que le sAutoniax est libre")
f.sur_resultat("s2", "c", False, "erreur reseau")
f.sur_resultat("s1", "a", True, "ok")
ok(ev["fin"] == 1 and f.est_termine() and sorted((n, o) for _, n, o, _ in ev["notif"]) == [("a", True), ("b", True), ("c", False)],
   "flux : une erreur n'arrete pas les autres, fin signalee une seule fois")

f, ev, h = faire_flux([P("s1", "a")])
f.demarrer(); f.sur_liste("s1", [{"nom": "a", "actif": True}])
f.sur_arret("s1", "a", False, "refus")
ok(not ev["envoyer"] and ev["notif"][0][2] is False and "non confirme" in ev["notif"][0][3] and ev["fin"] == 1, "flux : arret refuse -> pas d'archive")
f, ev, h = faire_flux([P("s1", "a")])
f.demarrer(); f.sur_liste("s1", [{"nom": "a", "actif": True}])
h.t += ns["DELAI_ARRET_S"] + 1; f.verifier_delais()
ok(not ev["envoyer"] and "non confirme" in ev["notif"][0][3], "flux : delai d'arret depasse -> pas d'archive")
f, ev, h = faire_flux([P("s1", "a")])
f.demarrer(); f.sur_liste("s1", [{"nom": "autre", "actif": False}])
ok(not ev["envoyer"] and "introuvable" in ev["notif"][0][3], "flux : profil disparu du sAutoniax")
f, ev, h = faire_flux([P("s1", "a"), P("s2", "b")])
f.demarrer(); h.t += ns["DELAI_LISTAGE_S"] + 1; f.verifier_delais()
ok(len(ev["notif"]) == 2 and "injoignable" in ev["notif"][0][3] and ev["fin"] == 1, "flux : liste jamais recue -> erreur, pas de blocage")
f, ev, h = faire_flux([P("s1", "a"), P("s2", "b")])
f.demarrer(); f.sur_liste("s1", [{"nom": "a"}]); f.sur_liste("s2", [{"nom": "b"}])
f.sur_executants_connectes({"s1"})
ok(("s2", "b", False, "sAutoniax deconnecte pendant l'operation.") in ev["notif"] and not f.est_termine(), "flux : deconnexion -> ligne en erreur, les autres continuent")
f.sur_resultat("s1", "a", True, "ok")
ok(f.est_termine(), "flux : termine apres deconnexion partielle")
f, ev, h = faire_flux([P("s1", "a")])
f.demarrer(); f.sur_liste("s1", [{"nom": "a"}])
f.sur_echec_transmission("kaggle_envoyer_profils", "s1", "serveurT hors ligne")
ok(ev["notif"][0][2] is False and ev["fin"] == 1, "flux : echec de transmission de l'envoi")
f, ev, h = faire_flux([P("s1", "a")])
f.demarrer(); f.sur_liste("s1", [{"nom": "a"}])
h.t += ns["DELAI_INACTIVITE_ENVOI_S"] + 1; f.verifier_delais()
ok(ev["notif"][0][2] is False and ev["fin"] == 1, "flux : inactivite prolongee -> erreur")
f.sur_resultat("s1", "a", True, "ok tardif")
ok(ev["notif"][-1] == ("s1", "a", True, "ok tardif"), "flux : un resultat tardif reel corrige la ligne")
f, ev, h = faire_flux([P("s%d" % i, "p%d" % i) for i in range(5)])
f.demarrer()
for i in range(5): f.sur_liste("s%d" % i, [{"nom": "p%d" % i}])
ok(len(ev["envoyer"]) == 3, "flux : au plus MAX_TRANSFERTS_SIMULTANES envois en parallele")
f.sur_resultat("s0", "p0", True, "ok")
ok(len(ev["envoyer"]) == 4, "flux : un creneau libere lance le suivant")
f, ev, h = faire_flux([])
f.demarrer()
ok(ev["fin"] == 1, "flux : aucun profil -> termine")

# ---- phase 4 : flux B ------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    api4 = FauxKaggle(); g4 = faire_gestionnaire(api4)
    dp = Path(tmp) / "sp"; (dp / "Alice").mkdir(parents=True); (dp / "Alice" / "f.txt").write_text("1")
    zt = Path(tmp) / "z"; zt.mkdir(); zp = faux_zipper_factory(zt)
    ok(ns["traiter_envoi_kaggle"](g4, str(dp), {"nom_local": "Alice", "nom_archive": "alice@x.com"}, False, set(), zipper=zp)[0], "prepa : dataset sur le faux Kaggle")
    api4.datasets["mikereichlin/ax-alice-x"]["contenu_zip"] = str(zp(str(dp / "Alice")))
    td = ns["traiter_telechargement_kaggle"]
    cible = Path(tmp) / "cible"
    pr = {"slug": "ax-alice-x", "nom_archive": "alice@x.com", "nom_local": "alice@x.com"}
    r = td(g4, str(cible), pr, {"alice@x.com"})
    ok(r[0] is False and "en cours d'execution" in r[1] and not cible.exists(), "telechargement refuse si le profil tourne")
    r = td(g4, str(cible), pr, set())
    ok(r[0] and (cible / "alice@x.com" / "f.txt").read_text() == "1", "telechargement + extraction")
    ok(ns["lire_origines_kaggle"](str(cible)) == {"alice@x.com": "alice@x.com"}, "origine Kaggle notee")
    for mauvais in ("../x", "a/b", "_kaggle_origine.json", ".."):
        ok(td(g4, str(cible), dict(pr, nom_local=mauvais), set())[0] is False, f"nom local refuse {mauvais!r}")
    ok(td(g4, str(cible), {"slug": "", "nom_archive": ""}, set())[0] is False, "ordre incomplet")
    ok(td(g4, str(cible), dict(pr, slug="ax-inconnu"), set())[0] is False, "dataset inconnu : erreur sans plantage")

def faire_flux_b(rep, **kw):
    ev = {"envoyer": [], "notif": [], "fin": 0}
    h = Horloge()
    f = ns["FluxTelechargementKaggle"](rep, envoyer=lambda i, p: ev["envoyer"].append((i, p["nom_archive"])),
        notifier=lambda i, n, o, m: ev["notif"].append((i, n, o)),
        terminer=lambda: ev.__setitem__("fin", ev["fin"] + 1), horloge=h, **kw)
    return f, ev, h
def Q(*noms): return [{"slug": "ax-" + n, "nom_archive": n} for n in noms]
rep = ns["repartir_equitablement"]([{"slug": "ax-%d" % i, "nom_archive": str(i)} for i in range(10)], ["s1", "s2", "s3"])
ok(sorted(len(v) for v in rep.values()) == [3, 3, 4], "repartition 10 -> 4,3,3")
f, ev, h = faire_flux_b([{"id_executant": "s1", "profils": Q("a", "b")}, {"id_executant": "s2", "profils": Q("c")}])
f.demarrer()
ok(ev["envoyer"] == [("s1", "a"), ("s2", "c")], "flux B : 1 envoi a la fois par sAutoniax")
f.sur_resultat("s1", "a", False, "refus"); f.sur_resultat("s2", "c", True, "ok")
ok(("s1", "b") in ev["envoyer"] and ev["fin"] == 0, "flux B : une erreur n'arrete pas les autres")
f.sur_executants_connectes({"s2"})
ok(ev["fin"] == 1 and ("s1", "b", False) in ev["notif"], "flux B : deconnexion -> erreur, fin")
f, ev, h = faire_flux_b([{"id_executant": "s%d" % i, "profils": Q("p%d" % i)} for i in range(5)])
f.demarrer(); ok(len(ev["envoyer"]) == 3, "flux B : 3 simultanes au plus")
f, ev, h = faire_flux_b([{"id_executant": "s1", "profils": Q("a")}])
f.demarrer(); h.t += ns["DELAI_INACTIVITE_ENVOI_S"] + 1; f.verifier_delais()
ok(ev["fin"] == 1 and ev["notif"][0][2] is False, "flux B : inactivite -> erreur")
f, ev, h = faire_flux_b([]); f.demarrer(); ok(ev["fin"] == 1, "flux B : vide -> termine")

print(f"OK -- {nb} verifications passees")

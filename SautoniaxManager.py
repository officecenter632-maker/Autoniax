# =============================================================================
# Fichier généré par AutoniaX -- export du CODE de toutes les cellules d'un
# notebook (Task), pour édition facile dans un vrai éditeur externe.
#
# COMMENT ÇA MARCHE :
#
# 1. Chaque cellule du notebook est délimitée par un en-tête reconnaissable :
#
#        # ==== CELLULE #<rang> titre="<titre de la cellule>" ====
#        # description: <description de la cellule>
#        <code de la cellule, sur autant de lignes que nécessaire>
#
#    <rang> est la POSITION de la cellule dans le notebook, PAS un
#    identifiant interne : 0 = la cellule "Variable dynamique" (tout en
#    haut du notebook), 1, 2, 3... = les cellules suivantes, dans l'ordre
#    où elles apparaissent dans AutoniaX.
#
# 2. Vous pouvez modifier LIBREMENT le titre, la description et le code
#    de chaque cellule directement dans ce fichier, avec n'importe quel
#    éditeur de texte ou IDE, MAIS :
#    - le titre ne doit contenir ni guillemet double (") ni retour à la
#      ligne (les deux cassent la ligne d'en-tête au prochain collage) ;
#    - la description doit rester sur UNE SEULE ligne (une description
#      multi-lignes serait coupée à la première ligne au collage) ;
#    - le CODE d'une cellule ne doit jamais contenir une ligne qui
#      ressemble à "# ==== CELLULE #... ====" (même en commentaire ou en
#      exemple) : elle serait alors lue comme le début d'une NOUVELLE
#      cellule au moment du collage.
#
# 3. CE N'EST PAS UN SCRIPT PYTHON AUTONOME -- ce fichier n'est jamais
#    exécuté tel quel (ni par vous, ni par AutoniaX). C'est une VUE TEXTE
#    d'un notebook, où chaque cellule s'exécute dans UN SEUL espace de
#    noms Python PARTAGÉ pour tout le Task (exactement comme un notebook
#    Jupyter) : une variable ou fonction définie dans une cellule reste
#    disponible dans toutes les suivantes, sans réimport. Conséquence
#    directe pour le CODE de chaque cellule :
#    - N'AJOUTEZ JAMAIS de bloc "if __name__ == '__main__':" -- il n'y a
#      pas de point d'entrée unique à protéger, chaque cellule EST déjà
#      son propre point d'entrée, exécutée directement au moment voulu
#      (soit individuellement, soit via "Tout exécuter" dans l'ordre :
#      "# Variable dynamique" en premier, puis "# Main", puis les
#      suivantes dans leur ordre d'affichage) ; un tel bloc empêcherait
#      simplement le code qu'il contient de s'exécuter.
#    - N'ajoutez pas non plus de fonction main() appelée en fin de
#      fichier "à l'ancienne" (def main(): ... ; main()) SAUF si c'est
#      déjà le style utilisé dans la cellule d'origine -- le code au
#      niveau racine de la cellule s'exécute déjà tel quel, une
#      indirection supplémentaire n'apporte rien ici.
#    - Ne réimportez pas ce qui est déjà importé par une cellule
#      précédente de CE MÊME notebook (une cellule plus haut dans l'ordre
#      d'exécution) : l'import reste disponible, comme dans Jupyter.
#    - Respectez le modèle d'exécution et les fonctions/objets déjà
#      disponibles sans import documentés dans l'onglet "Documentation
#      pour IA" d'AutoniaX (ResultatAction, ZoneClicRect,
#      extraire_texte_fichier, Api2Api, etc.) plutôt que d'en inventer ou
#      d'en deviner de nouveaux.
#
# 4. Pour renvoyer vos modifications dans AutoniaX, il FAUT repartir du
#    TEXTE de ce fichier, jamais du fichier lui-même :
#    a. Ouvrez ce fichier .py dans un éditeur de texte ou IDE.
#    b. Sélectionnez tout son contenu et copiez-le (Ctrl+A puis Ctrl+C)
#       DANS CET ÉDITEUR -- pas depuis l'explorateur de fichiers, pas en
#       recliquant sur le bouton qui a généré ce fichier dans AutoniaX.
#    c. Revenez dans AutoniaX et cliquez sur le bouton "Coller" (à côté du
#       bouton qui a généré ce fichier) dans la barre d'outils du notebook
#       ouvert. Chaque cellule existante à la position <rang> est alors
#       mise à jour (titre, description et code) ; si un rang dépasse le
#       nombre de cellules déjà présentes, une NOUVELLE cellule est créée
#       à la fin.
#    Le bouton "Coller" lit TOUJOURS le texte actuellement dans le
#    presse-papier système, jamais un fichier sur disque -- c'est un choix
#    assumé, pas une limitation à contourner. Cliquer sur le bouton qui a
#    généré ce fichier place une RÉFÉRENCE vers ce fichier .py dans le
#    presse-papier (comme un Ctrl+C d'un fichier dans l'Explorateur), PAS
#    son texte : un "Coller" fait juste après ce clic-là ne lira donc rien
#    d'utile, quel que soit le contenu de ce fichier. Le texte doit
#    provenir d'un vrai Ctrl+C fait DANS un éditeur de texte, sur CE
#    fichier ouvert (étape b ci-dessus).
#
# 5. Aucune cellule n'est jamais supprimée par un collage : un rang
#    absent de ce fichier (si vous effacez un bloc entier) laisse
#    simplement la cellule correspondante inchangée dans AutoniaX. Et si
#    la cellule "# Variable dynamique" (rang 0) elle-même est absente du
#    Task ouvert au moment du collage, le bloc de rang 0 de ce fichier est
#    ignoré (rien à mettre à jour) plutôt que de créer une nouvelle
#    cellule à cette position.
#
# ATTENTION : ne modifiez pas la ligne d'en-tête "# ==== CELLULE #... ===="
# elle-même (le numéro de rang et les guillemets autour du titre doivent
# rester dans ce format exact), sous peine que cette cellule ne soit pas
# reconnue au moment du collage.
#
# 6. SI VOUS DEMANDEZ À UNE IA DE MODIFIER CE FICHIER : demandez-lui de
#    PATCHER les cellules concernées (modifier UNIQUEMENT le code des
#    cellules à changer, en conservant TEL QUEL le reste du fichier --
#    en-tête, cellules non concernées, lignes "# ==== CELLULE #... ===="
#    de toutes les cellules), jamais de réécrire tout le fichier depuis
#    zéro. Une réécriture complète risque de renuméroter, fusionner ou
#    reformuler des cellules qui n'avaient pas besoin de changer, ce qui
#    casse silencieusement le repérage par rang au moment du collage
#    (cf. point 4 ci-dessus) et peut faire perdre du code auquel vous
#    teniez dans une cellule que vous ne vouliez pas toucher.
# =============================================================================

# ==== CELLULE #0 titre="# Variable dynamique" ====
# description: 
####################################################################################
RETRY = 3                  # nombre de tentatives supplémentaires par défaut (0 = aucun retry)
TIMEOUT = 10                # timeout réseau par défaut, en secondes (None = timeout du moteur)
LATENCE_AVANT = 0.2         # pause par défaut avant chaque action, en secondes
LATENCE_APRES = 0.2         # pause par défaut après chaque action, en secondes
SOURIS_INSTANTANEE = False  # True = déplacement de souris instantané (pas de trajectoire simulée)
LIST_TASKS = []             # liste des tâches (dicts de champs métier) attribuées à ce profil (cf. bouton WORKSPACE du panneau clone) -- fournissez vous-même le chemin du WORKSPACE si besoin de marquer_tache_terminee(tache, VOTRE_CHEMIN)
RESULT_COLOR = "#006400"    # couleur (hex) de la pastille du panneau clone pour ce lot -- réinitialisée en début de lot, lue à la fin
RESULT_OUTPUT = None        # donnée(s) à RETOURNER au pilote à la fin du lot : dict/liste/texte (sauvegardé en .json) OU chemin d'un fichier (image...) -- réinitialisée en début de lot
RESULT_SAVE_PATH = ""      # dossier du PILOTE où ranger RESULT_OUTPUT (un sous-dossier par profil) -- chemin local au pilote, jamais lu côté sAutoniax
def RESULT_OUTPUT_HANDLER(valeur):
    # Exécutée côté PILOTE, dès que le résultat de ce profil est reçu.
    # UN SEUL paramètre : `valeur` (le contenu de RESULT_OUTPUT tel quel -- dict/liste/str/nombre,
    # ou un chemin de fichier si RESULT_OUTPUT était un fichier). Tout le reste (dossier, nom de
    # profil, format...) est à coder en dur ici, par vous.
    import json
    from pathlib import Path
    from datetime import datetime
    dossier = Path("C:/Users/Office/Downloads/saver")
    dossier.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    (dossier / f"{horodatage}_resultat.json").write_text(
        json.dumps(valeur, ensure_ascii=False, indent=2), encoding="utf-8",
    )
####################################################################################

# ==== CELLULE #1 titre="# Fonctions Kaggle" ====
# description: 
import json, re, time, threading

# ---- Annulation d'un demarrage en cours (ordre d'arret recu pendant le demarrage) ----
_ANNULATION = threading.Event()


class DemarrageAnnule(Exception):
    pass


def _pause_annulable(secondes):
    """Comme time.sleep, mais leve DemarrageAnnule si _ANNULATION est active (verifie toutes les 0,25 s)."""
    fin = time.time() + secondes
    while True:
        if _ANNULATION.is_set():
            raise DemarrageAnnule("demarrage annule")
        reste = fin - time.time()
        if reste <= 0:
            return
        time.sleep(min(0.25, reste))

# ---- JavaScript (chaines brutes : les \s etc. sont envoyes tels quels au navigateur) ----
_JS_NB_LIENS = r"""document.querySelectorAll('a[href*="/code/"]').length"""

_JS_CLIC_NOTEBOOK = r"""
const nom = __NOM__.toLowerCase();
const slug = __SLUG__;
const lire = a => (a.getAttribute('aria-label') || a.textContent || '').trim();
const slugDe = a => { try { return new URL(a.href).pathname.split('/')[3] || ''; } catch (e) { return ''; } };
const liens = Array.from(document.querySelectorAll('a[href*="/code/"]'));
const trouves = liens.filter(a => lire(a).toLowerCase() === nom || slugDe(a).toLowerCase() === slug);
if (!trouves.length) {
    const noms = Array.from(new Set(liens.map(lire).filter(t => t && t.length < 60)));
    return {ok: false, erreur: 'notebook introuvable sur la page', disponibles: noms.slice(0, 30)};
}
const a = trouves[0];
const info = {ok: true, nom: lire(a), href: a.href};
a.click();
return info;
"""

_JS_ETAT_SESSION = r"""
const b = document.querySelector('button[aria-label="Start session"]');
const stop = document.querySelector('button[aria-label="Stop session"]');
const m = (document.body.innerText || '').match(/Draft Session\s*\n?\s*([^\n]*)/i);
return {start: !!b, start_actif: !!b && !b.disabled, stop: !!stop, statut: m ? m[1].trim() : null};
"""

_JS_CLIC_START = r"""
const b = document.querySelector('button[aria-label="Start session"]');
if (!b) return {ok: false, erreur: 'bouton Start session introuvable'};
if (b.disabled) return {ok: false, erreur: 'bouton Start session desactive'};
b.click();
return {ok: true};
"""

_JS_CLIC_RUN = r"""
if (window.__sautoniax_run_clique && !__FORCER__) return {ok: true, deja: true};
const b = document.querySelector('button[aria-label="__LABEL__"]');
if (!b) return {ok: false, erreur: 'bouton __LABEL__ introuvable'};
if (b.disabled || b.getAttribute('aria-disabled') === 'true') return {ok: false, erreur: 'bouton __LABEL__ desactive'};
b.click();
window.__sautoniax_run_clique = true;
return {ok: true, deja: false};
"""

_JS_RUN_EN_COURS = r"""!!document.querySelector('button[aria-label="Stop execution"]')"""
_JS_PAGE_COMPLETE = r"""document.readyState === 'complete'"""

# ---- Internet du notebook (Session options > interrupteur "Internet off/on") : doit etre ACTIF avant le Run ----
_JS_INTERNET_ETAT = r"""
const lab = document.querySelector('#internet-toggle-switch-label');
const dlg = Array.from(document.querySelectorAll('[role="dialog"],[role="alertdialog"]')).map(d => (d.textContent || '').trim().slice(0, 200));
if (!lab) {
    return {present: false, options_repliees: !!document.querySelector('button[aria-label="Expand Session options"]'),
            sidebar_repliee: !!document.querySelector('button[aria-label="Expand Sidebar"]'), dialogues: dlg};
}
const inp = lab.querySelector('input[type="checkbox"]');
const texte = (lab.textContent || '').trim();
return {present: true, actif: inp ? !!inp.checked : /internet on/i.test(texte), texte: texte, desactive: !!(inp && inp.disabled), dialogues: dlg};
"""

_JS_INTERNET_DEPLIER = r"""
const so = document.querySelector('button[aria-label="Expand Session options"]');
if (so) { so.click(); return {ok: true, clique: 'session options'}; }
const sb = document.querySelector('button[aria-label="Expand Sidebar"]');
if (sb) { sb.click(); return {ok: true, clique: 'sidebar'}; }
return {ok: false};
"""

_JS_INTERNET_CLIC = r"""
const lab = document.querySelector('#internet-toggle-switch-label');
const inp = lab ? lab.querySelector('input[type="checkbox"]') : null;
if (!inp) return {ok: false, erreur: 'interrupteur Internet introuvable'};
if (inp.disabled) return {ok: false, erreur: 'interrupteur Internet desactive (compte non verifie ?)'};
if (inp.checked) return {ok: true, deja: true};
inp.click();
return {ok: true, deja: false};
"""

# ---- Barre laterale de l'accueil kaggle.com : "Your Work" > "Viewed" (a REPLIER) et "Edited" (a DEPLIER) ----
# Les notebooks Sautoniax sont dans "Edited" : replie, ils sont absents de la page. Un appel = au plus un clic par section ;
# "pret" = rien n'a ete clique (etat deja bon). Retourne aussi les noms listes dans "Edited".
_JS_SIDEBAR_PREPARER = r"""
const clique = [];
const lien = n => document.querySelector('a[data-click-log-id="' + n + '"]');
const yw = document.querySelector('button[aria-label="Expand Your Work"]');
if (yw) { yw.click(); clique.push('your work'); }
const v = lien('viewed'), e = lien('edited');
if (!v && !e) {
    return {ok: false, clique: clique, erreur: 'sections Viewed/Edited introuvables (pas sur l accueil, ou barre laterale repliee)',
            menu: !!document.querySelector('button[aria-label="Navigation menu"]')};
}
const vOuvert = v ? v.getAttribute('aria-expanded') === 'true' : false;
const eOuvert = e ? e.getAttribute('aria-expanded') === 'true' : false;
if (v && vOuvert) {
    const b = document.querySelector('button[aria-label="Collapse Viewed"]');
    if (b) { b.click(); clique.push('viewed replie'); }
}
if (e && !eOuvert) {
    const b = document.querySelector('button[aria-label="Expand Edited"]');
    if (b) { b.click(); clique.push('edited deplie'); }
}
const li = e ? e.closest('li') : null;
const liste = li ? li.nextElementSibling : null;
const notebooks = liste ? Array.from(liste.querySelectorAll('a[href*="/code/"]'))
    .map(a => (a.getAttribute('aria-label') || a.textContent || '').trim()).filter(Boolean) : [];
return {ok: true, pret: clique.length === 0 && !vOuvert && eOuvert, viewed_ouvert: vOuvert, edited_ouvert: eOuvert,
        clique: clique, notebooks: notebooks};
"""
_JS_EDITEUR_PRET = r"""document.readyState === 'complete' && !!document.querySelector('iframe[name="notebook-editor-cells"]')"""


def _slug_kaggle(nom):
    return re.sub(r"[^a-z0-9]+", "-", nom.lower()).strip("-")


def ouvrir_et_lancer_notebook(nom_notebook, demarrer_session=True, lancer_run=True,
                              bouton_run="Run All", forcer_run=False,
                              delai_notebook=30.0, delai_session=300.0,
                              delai_page=30.0, timeout_nav=30.0, pause_avant_run=10.0,
                              delai_run=20.0, pause_chargement=15.0, essais_run=3,
                              verifier_internet=True, delai_internet=20.0,
                              attendre_session=True, session_neuve=False, attendre_run=True, ouvrir_seulement=False):
    """Ouvre le notebook Kaggle `nom_notebook` (onglet actif), demarre sa session, puis clique sur Run.

    Fonction CONTINUE (relancable a volonte) : chaque etape verifie l'etat reel avant d'agir.
      1) pas sur kaggle.com / sur un autre notebook -> navigue vers kaggle.com
      2) pas sur CE notebook                         -> clic JS sur son lien (par son nom)
      3) session eteinte                             -> clic JS sur "Start session" (si demarrer_session)
      4) session en cours                            -> clic JS sur `bouton_run` (si lancer_run),
                                                        une seule fois par page sauf forcer_run=True
    Parametres :
      nom_notebook     nom exact du notebook, ex. "Sautoniax5" (casse ignoree)
      demarrer_session False = ne demarre pas la session
      lancer_run       False = ne clique pas sur Run
      bouton_run       "Run All" ou "Run current cell"
      forcer_run       True = recliquer sur Run meme si deja clique sur cette page
      attendre_session False = apres le clic sur Start session, RETOURNE tout de suite (res["session"] = "demarrage") sans attendre que
                       la session soit demarree : sert au demarrage en 2 phases (ouvrir + Start sur tous les notebooks, puis Run un a un)
      ouvrir_seulement True = s'arrete des que le notebook est OUVERT (clic sur son lien, URL changee) : n'attend NI l'editeur NI la pause de
                       chargement, ne touche ni a Internet ni a la session (res["ouvert"] = True). Le chargement se poursuit dans l'onglet pendant
                       que l'appelant ouvre les autres ; un 2e appel sur le meme onglet continue (Internet, Start session...)
      attendre_run     False = apres le clic sur Run, RETOURNE tout de suite (res["run"] = "clique") sans attendre le "Run en cours" :
                       l'appelant verifie plus tard (demarrage en 2 phases)
      session_neuve    True = la session vient de demarrer (phase Run d'un demarrage en 2 phases) : impose la pause avant Run
      verifier_internet True = verifie que Internet est ACTIF (Session options) avant de demarrer la session ET juste avant Run ;
                       s'il est eteint, l'active ; s'il n'est pas activable, le Run n'est PAS lance (echec)
    Delais d'attente (en secondes) :
      delai_internet   attente max (defaut 20 s) du panneau Session options et de l'activation d'Internet
      timeout_nav      temps max accorde au chargement de kaggle.com par naviguer() (defaut 30)
      delai_page       attente que la page soit chargee (accueil : liens affiches ; notebook : editeur affiche)
      delai_notebook   attente de l'ouverture du notebook apres le clic, et des boutons de session
      delai_session    attente max du demarrage de la session apres Start session (defaut 300 = 5 min)
      delai_run        attente max (defaut 20 s) que le Run apparaisse comme en cours apres CHAQUE clic
      essais_run       nombre max de clics sur Run si le Run ne demarre pas (defaut 3)
      pause_chargement pause (defaut 15 s, minimum 15 s impose) apres l'ouverture du notebook, pour qu'il finisse de se charger
                       COMPLETEMENT avant tout clic (Start session, Run)
      pause_avant_run  pause (defaut 10 s, minimum 10 s impose) avant de cliquer sur Run quand la page vient d'etre ouverte ou la session
                       demarree, pour laisser les cellules (dans une iframe d'un autre domaine, donc
                       non verifiables) finir de se charger
    Retourne un dict : {"ok": bool, "notebook": str, "etapes": [...], "erreur": str (si echec)}.
    """
    # Attentes minimales imposees : jamais moins de 15 s apres l'ouverture du notebook, 10 s avant Run.
    pause_chargement = max(15.0, pause_chargement)
    pause_avant_run = max(10.0, pause_avant_run)
    inst = Instance.instance()
    slug = _slug_kaggle(nom_notebook)
    res = {"ok": False, "notebook": nom_notebook, "etapes": []}

    def log(msg):
        print(f"[{nom_notebook}] {msg}")

    def etape(msg):
        res["etapes"].append(msg)
        log(msg)

    def echec(msg):
        res["erreur"] = msg
        log(f"ECHEC : {msg}")
        return res

    def js(code):
        try:
            return inst.evaluer_js(code, retry=RETRY, timeout=TIMEOUT)
        except Exception as e:
            return {"_erreur": str(e)}

    def url_actuelle():
        r = js("location.href")
        return r if isinstance(r, str) else ""

    def sur_ce_notebook(u):
        return bool(re.search(r"kaggle\.com/code/[^/]+/" + re.escape(slug) + r"(?:[/?#]|$)", u, re.I))

    def attendre(condition, delai, pas=1.0):
        fin = time.time() + delai
        while time.time() < fin:
            if _ANNULATION.is_set():
                raise DemarrageAnnule("demarrage annule")
            if condition():
                return True
            _pause_annulable(pas)
        return bool(condition())

    def etat():
        e = js(_JS_ETAT_SESSION)
        return e if isinstance(e, dict) and "_erreur" not in e else {}

    def session_en_cours():
        e = etat()
        return bool(e.get("stop")) and not e.get("start")

    def preparer_sidebar():
        """Accueil kaggle.com : replie "Viewed", deplie "Edited" (la, les notebooks sont listes). Verifie l'etat reel, jusqu'a 6 essais."""
        r = {}
        for _ in range(6):
            r = js(_JS_SIDEBAR_PREPARER)
            if isinstance(r, dict) and r.get("ok") and r.get("pret"):
                return r
            if isinstance(r, dict) and r.get("clique"):
                etape(f"Barre laterale : {', '.join(r['clique'])}.")
            _pause_annulable(1.0)
        log(f"Avertissement : barre laterale (Viewed/Edited) non preparee : {r}")
        return r

    def attendre_accueil():
        def liens_affiches():
            n = js(_JS_NB_LIENS)
            return js(_JS_PAGE_COMPLETE) is True and isinstance(n, int) and n > 0
        if not attendre(liens_affiches, delai_page):
            log("Avertissement : la page d'accueil ne semble pas entierement chargee.")
        preparer_sidebar()

    def aller_accueil():
        r = inst.naviguer("https://www.kaggle.com", retry=RETRY, timeout=timeout_nav)
        if not r:
            return False, getattr(r, "message", "navigation impossible")
        attendre_accueil()
        return True, ""

    def cliquer_notebook():
        preparer_sidebar()    # Viewed replie / Edited deplie : sinon le notebook peut etre absent de la page
        code = _JS_CLIC_NOTEBOOK.replace("__NOM__", json.dumps(nom_notebook)).replace("__SLUG__", json.dumps(slug))
        return js(code)

    def assurer_internet():
        """Internet doit etre ACTIF avant de lancer le Run. Retourne (True, "deja"|"active") ou (False, raison)."""
        def lire():
            e = js(_JS_INTERNET_ETAT)
            return e if isinstance(e, dict) and "_erreur" not in e else {}
        fin = time.time() + delai_internet
        e = lire()
        while not e.get("present") and time.time() < fin:    # panneau Session options replie : on le deplie
            js(_JS_INTERNET_DEPLIER)
            _pause_annulable(1.5)
            e = lire()
        if not e.get("present"):
            return False, f"interrupteur Internet introuvable (panneau Session options inaccessible) : {e}"
        if e.get("actif"):
            etape("Internet deja active.")
            return True, "deja"
        r = js(_JS_INTERNET_CLIC)
        if not (isinstance(r, dict) and r.get("ok")):
            return False, f"activation d'Internet impossible : {r}"
        etape("Clic JS sur l'interrupteur Internet.")
        if attendre(lambda: lire().get("actif") is True, delai_internet):
            etape("Internet active.")
            return True, "active"
        return False, f"Internet n'a pas ete active (interrupteur : {lire()})"

    # --- Etape 1 : etre sur kaggle.com ---
    url = url_actuelle()
    log(f"Page actuelle : {url or '(inconnue)'}")
    deja_accueil = False
    a_change = False   # True des qu'on a ouvert une page ou demarre la session (-> pause avant Run)
    if sur_ce_notebook(url):
        etape("Deja sur ce notebook.")
    else:
        if "kaggle.com" not in url or "/code/" in url:
            ok, msg = aller_accueil()
            if not ok:
                return echec(f"navigation vers kaggle.com impossible : {msg}")
            etape("kaggle.com charge.")
            deja_accueil = True
        else:
            attendre_accueil()    # onglet deja sur l'accueil (ex. onglet neuf) : on attend qu'il soit charge avant de chercher le notebook

        # --- Etape 2 : ouvrir le notebook par son nom ---
        r = cliquer_notebook()
        if isinstance(r, dict) and not r.get("ok") and not deja_accueil:
            ok, msg = aller_accueil()
            if not ok:
                return echec(f"navigation vers kaggle.com impossible : {msg}")
            etape("kaggle.com charge (nouvel essai).")
            r = cliquer_notebook()
        if not (isinstance(r, dict) and r.get("ok")):
            dispo = r.get("disponibles") if isinstance(r, dict) else None
            return echec(f"notebook '{nom_notebook}' introuvable ({dispo if dispo else r})")
        etape(f"Clic JS sur '{r['nom']}' -> {r['href']}")
        if not attendre(lambda: sur_ce_notebook(url_actuelle()), delai_notebook):
            return echec("le notebook ne s'est pas ouvert dans le delai")
        etape("Notebook ouvert.")
        a_change = True

    if ouvrir_seulement:
        res["ok"] = True
        res["ouvert"] = True
        etape("Notebook ouvert : chargement laisse en arriere-plan.")
        return res

    # Attendre que l'editeur du notebook soit affiche (page chargee + iframe des cellules presente)
    if not attendre(lambda: js(_JS_EDITEUR_PRET) is True, delai_page):
        log("Avertissement : l'editeur du notebook ne semble pas entierement charge.")
    if a_change and pause_chargement:
        log(f"Attente de {pause_chargement} s : chargement complet du notebook avant d'agir.")
        _pause_annulable(pause_chargement)

    # --- Etape 2b : Internet actif AVANT de demarrer la session ---
    if verifier_internet:
        ok_i, msg_i = assurer_internet()
        if not ok_i:
            return echec(msg_i)
        if msg_i == "active":
            _pause_annulable(5)    # laisse l'eventuel redemarrage de session se stabiliser avant de relire son etat

    # --- Etape 3 : session ---
    if not attendre(lambda: bool(etat().get("start") or etat().get("stop")), delai_notebook):
        return echec(f"boutons de session introuvables (etat : {etat()})")
    e = etat()
    log(f"Etat de la session : {e.get('statut')}")
    if session_en_cours():
        etape("Session deja demarree.")
    elif not demarrer_session:
        etape("Session eteinte (demarrer_session=False) : rien lance.")
        res["ok"] = True
        return res
    elif e.get("start_actif"):
        r = js(_JS_CLIC_START)
        if not (isinstance(r, dict) and r.get("ok")):
            return echec(f"demarrage impossible : {r}")
        etape("Clic JS sur Start session.")
        if not attendre_session:
            etape("Session en cours de demarrage (on n'attend pas : Run plus tard).")
            res["ok"] = True
            res["session"] = "demarrage"
            return res
        dernier = e.get("statut")
        fin = time.time() + delai_session
        while time.time() < fin and not session_en_cours():
            _pause_annulable(2)
            st = etat().get("statut")
            if st != dernier:
                dernier = st
                log(f"Session : {dernier}")
        if not session_en_cours():
            return echec("la session n'a pas demarre dans le delai")
        etape("Session demarree.")
        a_change = True
    else:
        return echec(f"Start session non cliquable (etat : {e})")

    # --- Etape 4 : Run ---
    if not lancer_run:
        etape("Run non demande (lancer_run=False).")
        res["ok"] = True
        return res
    if (a_change or session_neuve) and pause_avant_run:
        log(f"Pause de {pause_avant_run} s avant Run (chargement des cellules).")
        _pause_annulable(pause_avant_run)
    if verifier_internet:    # derniere verification, juste avant le clic sur Run
        ok_i, msg_i = assurer_internet()
        if not ok_i:
            return echec(msg_i + " -> Run non lance")
        if msg_i == "active":
            _pause_annulable(3)
            if not session_en_cours():    # activer Internet a pu arreter la session : on la redemarre
                attendre(lambda: bool(etat().get("start_actif")) or session_en_cours(), delai_notebook)
                if not session_en_cours():
                    r = js(_JS_CLIC_START)
                    if not (isinstance(r, dict) and r.get("ok")):
                        return echec(f"session arretee apres l'activation d'Internet et redemarrage impossible : {r}")
                    etape("Session redemarree apres l'activation d'Internet.")
                    if not attendre(session_en_cours, delai_session, pas=2.0):
                        return echec("la session n'a pas redemarre apres l'activation d'Internet")
                    _pause_annulable(pause_avant_run)
    if js(_JS_RUN_EN_COURS) is True:
        etape("Run deja en cours : rien a relancer.")
        res["ok"] = True
        return res
    for essai in range(1, essais_run + 1):
        code = (_JS_CLIC_RUN.replace("__LABEL__", bouton_run)
                            .replace("__FORCER__", "true" if (forcer_run or essai > 1) else "false"))
        r = js(code)
        if not (isinstance(r, dict) and r.get("ok")):
            return echec(f"Run impossible : {r}")
        if r.get("deja"):
            etape(f"Run deja clique sur cette page ({bouton_run}).")
            res["ok"] = True
            return res
        etape(f"Clic JS sur {bouton_run} (essai {essai}/{essais_run}).")
        if not attendre_run:
            etape("Run clique : verification laissee a l'appelant (on n'attend pas).")
            res["ok"] = True
            res["run"] = "clique"
            return res
        if attendre(lambda: js(_JS_RUN_EN_COURS) is True, delai_run, pas=0.5):
            etape("Run en cours.")
            res["ok"] = True
            return res
        log("Le Run n'a pas demarre.")
        if essai < essais_run:
            _pause_annulable(pause_avant_run)
    return echec(f"le Run n'a pas demarre apres {essais_run} clic(s) (cellules deja terminees, notebook vide, ou clic sans effet)")
    res["ok"] = True
    return res

_JS_CLIC_STOP_RUN = r"""
const b = document.querySelector('button[aria-label="Stop execution"]');
if (!b) return {ok: false, erreur: 'aucun Run en cours (bouton Stop execution absent)'};
b.click();
return {ok: true};
"""


def arreter_notebook(arreter_session=False, delai=30.0):
    """Arrete le Run en cours (clic JS sur \"Stop execution\") dans l'onglet actif, qui doit deja etre
    sur le notebook. Si arreter_session=True, arrete ensuite la session via Active Events (3 points -> Stop Session).
    Retourne {\"ok\": bool, \"etapes\": [...], \"erreur\": str (si echec)}."""
    inst = Instance.instance()
    res = {"ok": False, "etapes": []}

    def log(msg):
        print(f"[arret] {msg}")

    def etape(msg):
        res["etapes"].append(msg)
        log(msg)

    def echec(msg):
        res["erreur"] = msg
        log(f"ECHEC : {msg}")
        return res

    def js(code):
        try:
            return inst.evaluer_js(code, retry=RETRY, timeout=TIMEOUT)
        except Exception as e:
            return {"_erreur": str(e)}

    def attendre(condition, delai_max, pas=0.5):
        fin = time.time() + delai_max
        while time.time() < fin:
            if condition():
                return True
            time.sleep(pas)
        return bool(condition())

    if js(_JS_RUN_EN_COURS) is True:
        r = js(_JS_CLIC_STOP_RUN)
        if not (isinstance(r, dict) and r.get("ok")):
            return echec(f"arret du Run impossible : {r}")
        etape("Clic JS sur Stop execution.")
        if attendre(lambda: js(_JS_RUN_EN_COURS) is not True, delai):
            etape("Run arrete.")
        else:
            return echec("le Run tourne encore apres le delai")
    else:
        etape("Aucun Run en cours.")

    if arreter_session:
        etape("Arret de la session via Active Events.")
        rf = fermer_sessions_actives()
        if not rf.get("ok"):
            return echec(f"arret de la session via Active Events impossible : {rf.get('erreur')}")
        etape("Session arretee.")
    res["ok"] = True
    return res

_JS_CLIC_ACTIVE_EVENTS = r"""
const b = document.querySelector('button[aria-controls="active-events-panel"]');
if (!b) return {ok: false, erreur: 'bouton View Active Events introuvable'};
if (b.getAttribute('aria-expanded') !== 'true') b.click();
return {ok: true};
"""

_JS_ETAT_ACTIVE_EVENTS = r"""
const b = document.querySelector('button[aria-controls="active-events-panel"]');
return b ? {ouvert: b.getAttribute('aria-expanded') === 'true'} : {};
"""


def ouvrir_active_events(pause_apres=3.0):
    """Clique sur le bouton \"View Active Events\" (barre de navigation Kaggle) dans l'onglet actif.
    Fonction a part : ne touche pas au Run en cours, ne ferme ni n'arrete rien. Elle ouvre seulement le
    panneau, puis indique s'il est ouvert. Retourne {\"ok\": bool, \"ouvert\": bool, \"erreur\": str (si echec)}."""
    inst = Instance.instance()

    def js(code):
        try:
            return inst.evaluer_js(code, retry=RETRY, timeout=TIMEOUT)
        except Exception as e:
            return {"_erreur": str(e)}

    r = js(_JS_CLIC_ACTIVE_EVENTS)
    if not (isinstance(r, dict) and r.get("ok")):
        print(f"[active-events] ECHEC : {r}", flush=True)
        return {"ok": False, "erreur": str(r)}
    time.sleep(pause_apres)
    e = js(_JS_ETAT_ACTIVE_EVENTS)
    ouvert = bool(isinstance(e, dict) and e.get("ouvert"))
    print(f"[active-events] Panneau {'ouvert' if ouvert else 'non confirme ouvert (voir la page)'}.")
    return {"ok": True, "ouvert": ouvert}


_JS_LISTER_SESSIONS = r"""
const p = document.querySelector('#active-events-panel');
if (!p) return {ouvert: false, sessions: []};
const bs = Array.from(p.querySelectorAll('button[aria-label^="More options for "]'));
const statuts = {};
Array.from(p.querySelectorAll('li[aria-label^="Status for "]')).forEach(li => {
    const m = (li.getAttribute('aria-label') || '').match(/^Status for (.*?): (.*?)\./);
    if (m) statuts[m[1]] = m[2];
});
return {ouvert: true, sessions: bs.map(b => b.getAttribute('aria-label').replace('More options for ', '')), statuts: statuts};
"""

# Sequence complete d'evenements souris (pointerdown/mousedown/pointerup/mouseup/click) au centre de
# l'element, comme un vrai clic : un simple .click() n'est pas toujours pris en compte par ces menus.
_JS_EVT = r"""
const __clic = el => {
    const r = el.getBoundingClientRect();
    const o = {bubbles: true, cancelable: true, composed: true, view: window,
               clientX: r.left + r.width / 2, clientY: r.top + r.height / 2,
               button: 0, buttons: 1, pointerId: 1, pointerType: 'mouse', isPrimary: true};
    const o2 = Object.assign({}, o, {buttons: 0});
    el.dispatchEvent(new PointerEvent('pointerdown', o));
    el.dispatchEvent(new MouseEvent('mousedown', o));
    if (el.focus) el.focus();
    el.dispatchEvent(new PointerEvent('pointerup', o2));
    el.dispatchEvent(new MouseEvent('mouseup', o2));
    el.dispatchEvent(new MouseEvent('click', o2));
};
const __item_stop = () => Array.from(document.querySelectorAll('ul[role="menu"] li[role="menuitem"]'))
    .find(e => /stop\s*session/i.test((e.textContent || '').trim()));
"""

# Ouvre le menu "More options for <nom>" (sans rien faire s'il est deja ouvert).
_JS_OUVRIR_MENU = _JS_EVT + r"""
if (__item_stop()) return {ok: true, deja: true};
const p = document.querySelector('#active-events-panel');
const bs = p ? Array.from(p.querySelectorAll('button[aria-label^="More options for "]')) : [];
const b = bs[__INDEX__];
if (!b) return {ok: false, erreur: 'bouton More options introuvable'};
__clic(b);
return {ok: true, deja: false};
"""

# Clique sur "Stop Session" DES QUE l'option est dans la page (appele en boucle rapide).
_JS_CLIC_ITEM_STOP = _JS_EVT + r"""
const it = __item_stop();
if (!it) return {ok: false, menus: document.querySelectorAll('ul[role="menu"]').length};
__clic(it);
return {ok: true};
"""

_JS_FERMER_MENU = r"""
const bd = document.querySelector('.MuiMenu-root .MuiBackdrop-root, .MuiPopover-root .MuiBackdrop-root');
if (bd) bd.click();
document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
return {ok: true};
"""


_JS_BADGE = r"""
const b = document.querySelector('button[aria-controls="active-events-panel"]');
if (!b) return {existe: false};
const m = (b.innerText || '').match(/\d+/);
return {existe: true, nombre: m ? parseInt(m[0], 10) : 0, ouvert: b.getAttribute('aria-expanded') === 'true',
        panneau: !!document.querySelector('#active-events-panel')};
"""

_JS_DUMP = r"""
const p = document.querySelector('#active-events-panel');
const b = document.querySelector('button[aria-controls="active-events-panel"]');
const lire = e => (e.textContent || '').trim();
return {
  url: location.href,
  badge_texte: b ? (b.innerText || '').trim() : null,
  badge_ouvert: b ? b.getAttribute('aria-expanded') : null,
  panneau_present: !!p,
  panneau_texte: p ? (p.innerText || '').slice(0, 1500) : null,
  boutons_3_points: p ? Array.from(p.querySelectorAll('button[aria-label^="More options for "]')).map(x => x.getAttribute('aria-label')) : [],
  statuts: p ? Array.from(p.querySelectorAll('li[aria-label^="Status for "]')).map(x => x.getAttribute('aria-label')) : [],
  menus_ouverts: document.querySelectorAll('ul[role="menu"]').length,
  items_menu: Array.from(document.querySelectorAll('li[role="menuitem"]')).map(lire),
  dialogues: Array.from(document.querySelectorAll('[role="dialog"],[role="alertdialog"],.MuiDialog-root')).map(d => lire(d).slice(0, 300)),
  bouton_stop_session_page: !!document.querySelector('button[aria-label="Stop session"]'),
  bouton_start_session_page: !!document.querySelector('button[aria-label="Start session"]'),
  run_en_cours: !!document.querySelector('button[aria-label="Stop execution"]'),
  panneau_html: p ? p.outerHTML.slice(0, 5000) : null
};
"""

_JS_ETAT_MENU = r"""
const menus = Array.from(document.querySelectorAll('ul[role="menu"]'));
const items = Array.from(document.querySelectorAll('li[role="menuitem"]')).map(e => (e.textContent || '').trim());
const p = document.querySelector('#active-events-panel');
const dots = p ? Array.from(p.querySelectorAll('button[aria-label^="More options for "]')).length : -1;
return {menus: menus.length, items: items, boutons_3_points: dots};
"""


# 4 facons de "cliquer" : on les essaie dans l'ordre et on verifie a chaque fois que ca a marche.
#   0 = .click() natif | 1 = sequence souris complete | 2 = appel direct du onClick React | 3 = clavier (Entree)
NB_STRATEGIES_CLIC = 4
# Facons gardees d'apres les logs reels : le click natif (0) deplie bien le menu des 3 points ; la facon 1 (sequence
# souris) plante en JS sur ce navigateur et est donc retiree. Items du menu : natif (0) puis appel React (2) en secours.
STRATS_OUVERTURE = [0]
STRATS_ITEM = [0, 2]

_JS_STRAT = _JS_EVT + r"""
const __props = el => { const k = Object.keys(el).find(x => x.indexOf('__reactProps$') === 0); return k ? el[k] : null; };
const __strat = (el, n) => {
    if (n === 0) { el.click(); return 'click natif'; }
    if (n === 1) { __clic(el); return 'sequence souris complete'; }
    if (n === 2) {
        const p = __props(el);
        if (!p || typeof p.onClick !== 'function') return null;
        p.onClick({type: 'click', currentTarget: el, target: el, button: 0, buttons: 0, detail: 1,
                   preventDefault() {}, stopPropagation() {}, persist() {}, isDefaultPrevented: () => false,
                   nativeEvent: new MouseEvent('click', {bubbles: true})});
        return 'appel direct du onClick React';
    }
    if (n === 3) {
        el.focus();
        ['keydown', 'keyup'].forEach(t => el.dispatchEvent(new KeyboardEvent(t,
            {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true})));
        return 'clavier Entree';
    }
    return null;
};
"""

# Clic sur les 3 points ("More options for <nom>") avec la strategie __N__.
_JS_OUVRIR_MENU_STRAT = _JS_STRAT + r"""
const nom = __NOM__;
const p = document.querySelector('#active-events-panel');
const bs = p ? Array.from(p.querySelectorAll('button[aria-label^="More options for "]')) : [];
const b = bs.find(x => x.getAttribute('aria-label') === 'More options for ' + nom);
if (!b) return {ok: false, erreur: 'bouton 3 points introuvable', boutons: bs.map(x => x.getAttribute('aria-label'))};
const s = __strat(b, __N__); /*strat:__N__*/
return {ok: !!s, strategie: s, erreur: s ? null : 'strategie indisponible'};
"""

# Clic sur "Stop Session" dans le menu ouvert, strategie __N__.
_JS_CLIC_ITEM_STRAT = _JS_STRAT + r"""
const it = __item_stop();
if (!it) return {ok: false, erreur: 'option Stop Session absente (menu ferme ?)'};
const s = __strat(it, __N__); /*item:__N__*/
return {ok: !!s, strategie: s, erreur: s ? null : 'strategie indisponible'};
"""

# Lit le panneau Active Events ; l'ouvre d'abord (clic) s'il est ferme. UN SEUL appel JS (chaque appel coute 4-5 s sur le clone).
_JS_LISTER_OUVRIR = r"""
const b = document.querySelector('button[aria-controls="active-events-panel"]');
let p = document.querySelector('#active-events-panel');
let clique = false;
if (!p && b && b.getAttribute('aria-expanded') !== 'true') { b.click(); clique = true; p = document.querySelector('#active-events-panel'); }
const m = b ? (b.innerText || '').match(/\d+/) : null;
const badge = m ? parseInt(m[0], 10) : 0;
if (!p) return {ouvert: false, clique: clique, sessions: [], statuts: {}, badge: badge, bouton: !!b};
const bs = Array.from(p.querySelectorAll('button[aria-label^="More options for "]'));
const statuts = {};
Array.from(p.querySelectorAll('li[aria-label^="Status for "]')).forEach(li => {
    const mm = (li.getAttribute('aria-label') || '').match(/^Status for (.*?): (.*?)\./);
    if (mm) statuts[mm[1]] = mm[2];
});
const textes = Array.from(p.querySelectorAll('li')).slice(0, 8).map(li => (li.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 80));
return {ouvert: true, clique: clique, sessions: bs.map(x => x.getAttribute('aria-label').replace('More options for ', '')), statuts: statuts, badge: badge, textes: textes};
"""

# 3 points + Stop Session en UN SEUL appel : deplie le menu (click natif), et si "Stop Session" est deja la, clique dessus (strategie __N__).
_JS_MENU_ET_STOP = _JS_STRAT + r"""
const nom = __NOM__;
const p = document.querySelector('#active-events-panel');
const bs = p ? Array.from(p.querySelectorAll('button[aria-label^="More options for "]')) : [];
const b = bs.find(x => x.getAttribute('aria-label') === 'More options for ' + nom);
if (!__item_stop()) {
    if (!b) return {ok: false, erreur: 'bouton 3 points introuvable', boutons: bs.map(x => x.getAttribute('aria-label'))};
    __strat(b, 0);
}
const it = __item_stop();
if (it) {
    const s = __strat(it, __N__);
    return {ok: !!s, etape: 'stop_clique', strategie: s, erreur: s ? null : 'strategie indisponible'};
}
return {ok: true, etape: 'menu_ouvert',
        items: Array.from(document.querySelectorAll('li[role="menuitem"]')).map(e => (e.textContent || '').trim())};
"""


def fermer_sessions_actives(delai_total=420.0, pause=1.0, essais_par_session=4,
                            attente_menu=10.0, attente_verif=30.0, verifs_vides=2, verbeux=True, noms=None):
    """Arrete TOUTES les sessions en cours du panneau \"View Active Events\" (onglet actif), UNE PAR UNE.
    Pour chaque session : 3 points -> \"Stop Session\" (click natif, puis appel du onClick React en secours).
    Le bouton Stop session de la barre du notebook n'est JAMAIS utilise. Une session passee en \"Cancelled\" compte comme ARRETEE : fin immediate.
    Le nombre d'appels JS est reduit au minimum (chaque appel dure 4-5 s sur le clone).
    Si `noms` est donne (liste de noms de notebooks), n'arrete QUE les sessions portant ces noms (comparaison par slug, casse ignoree) ;
    les autres sessions du panneau ne sont pas touchees. noms=None : comportement inchange (toutes les sessions).
    LOGS : seulement les decisions importantes (console + cle \"logs\" du resultat). Pas de fichier, pas de ligne par appel JS.
    Retourne {\"ok\": bool, \"fermees\": [noms], \"logs\": [...], \"erreur\": str (si echec)}."""
    import traceback
    inst = Instance.instance()
    res = {"ok": False, "fermees": [], "logs": []}
    cibles_slug = None if noms is None else {_slug_kaggle(n) for n in noms}

    def cible(nom_session):
        return cibles_slug is None or _slug_kaggle(nom_session) in cibles_slug

    t0 = time.time()

    def log(msg):
        ligne = f"[fermeture +{time.time() - t0:5.1f}s] {msg}"
        res["logs"].append(ligne)
        print(ligne, flush=True)

    def js(code, nom="js", limite=1500):
        try:
            return inst.evaluer_js(code, retry=RETRY, timeout=TIMEOUT)
        except Exception as e:
            log(f"[JS] {nom} : EXCEPTION : {type(e).__name__} : {e}")
            return {"_erreur": str(e)}

    def dump(etiquette):
        log(f"===== ETAT COMPLET DE LA PAGE : {etiquette} =====")
        log(repr(js(_JS_DUMP, "dump de la page"))[:7000])

    def echec(msg):
        res["erreur"] = msg
        log(f"ECHEC : {msg}")
        try:
            dump("apres echec")
        except Exception:
            pass
        return res

    def succes(msg):
        log(msg)
        res["ok"] = True
        log(f"Termine : {time.time() - t0:.1f} s.")
        return res

    def lire():
        r = js(_JS_LISTER_OUVRIR, "lecture du panneau (l'ouvre si ferme)")
        return r if isinstance(r, dict) and isinstance(r.get("sessions"), list) else None

    def termine(nom, statuts):
        # Statut autre que "en cours" (Cancelled, Completed, Failed...) : la session est arretee.
        s = (statuts or {}).get(nom) or ""
        return bool(re.search(r"cancel|complet|fail|error|stopp|dismiss", s, re.I))

    def etat_session(nom, delai):
        # "partie" = plus listee | "annulee" = listee mais Cancelled/terminee | None = rien ne change dans le delai
        fin = time.time() + delai
        while True:
            l = lire()
            if l is not None and l.get("ouvert"):
                if nom not in l["sessions"]:
                    return "partie"
                if termine(nom, l.get("statuts")):
                    return "annulee"
            if time.time() >= fin:
                return None
            time.sleep(0.5)

    def stop_par_menu(nom):
        for m in (0, 2):   # 0 = click natif | 2 = appel direct du onClick React (secours)
            code = _JS_MENU_ET_STOP.replace("__NOM__", json.dumps(nom)).replace("__N__", str(m))
            r = js(code, f"3 points + Stop Session de '{nom}' - facon {m}")
            if not (isinstance(r, dict) and r.get("ok")):
                log(f"Impossible de cliquer : {r}")
                return False   # (panneau ferme ?) la boucle principale le rouvre et recommence
            if r.get("etape") == "menu_ouvert":
                log(f"Menu des 3 points ouvert : {r.get('items')}. J'attends 'Stop Session'...")
                fin = time.time() + attente_menu
                clique = None
                while time.time() < fin:
                    r2 = js(_JS_CLIC_ITEM_STRAT.replace("__N__", str(m)), f"'Stop Session' - facon {m}")
                    if isinstance(r2, dict) and r2.get("ok"):
                        clique = r2
                        break
                    time.sleep(0.3)
                if not clique:
                    log("L'option 'Stop Session' n'est pas apparue dans le menu.")
                    js(_JS_FERMER_MENU, "fermeture du menu")
                    continue
                r = clique
            log(f"'Stop Session' clique (facon {m} : {r.get('strategie')}). Verification (jusqu'a {attente_verif:.0f} s)...")
            e = etat_session(nom, attente_verif)
            if e == "partie":
                log(f"La facon {m} a fait disparaitre '{nom}'.")
                return True
            if e == "annulee":
                log(f"La facon {m} a passe '{nom}' en Cancelled : session ARRETEE.")
                return True
            log(f"'{nom}' tourne toujours apres la facon {m}.")
            js(_JS_FERMER_MENU, "fermeture du menu")
        return False

    log(f"Debut (delai max {delai_total} s, RETRY={RETRY}, TIMEOUT={TIMEOUT}). Cibles : {sorted(noms) if noms is not None else 'toutes les sessions'}.")
    try:
        fin_totale = time.time() + delai_total
        essais = {}
        vides = 0
        erreurs_lecture = 0
        panneau_ferme = 0
        while time.time() < fin_totale:
            l = lire()
            if l is None:
                erreurs_lecture += 1
                log(f"Panneau illisible ({erreurs_lecture}/3).")
                if erreurs_lecture >= 3:
                    return echec("impossible de lire le panneau Active Events")
                time.sleep(pause)
                continue
            erreurs_lecture = 0
            if not l.get("ouvert"):
                panneau_ferme += 1
                log(f"Panneau pas encore affiche (clic d'ouverture : {l.get('clique')}, tentative {panneau_ferme}/8).")
                if panneau_ferme >= 8:
                    return echec("le panneau Active Events ne s'ouvre pas")
                time.sleep(pause)
                continue
            panneau_ferme = 0
            sessions = l["sessions"]
            statuts = l.get("statuts") or {}

            if not sessions:
                if l.get("badge"):
                    log(f"Liste vide mais le badge indique {l['badge']} evenement(s) : je ne conclus pas.")
                    vides = 0
                    time.sleep(pause)
                    continue
                vides += 1
                if vides >= verifs_vides:
                    return succes("Plus aucune session en cours : tout est arrete.")
                time.sleep(pause)
                continue
            vides = 0

            actives = [x for x in sessions if cible(x) and not termine(x, statuts)]
            if not actives:
                if noms is not None and not res["fermees"] and not any(cible(x) for x in sessions):
                    log(f"Aucune session ne porte les noms {sorted(noms)} ; sessions listees : {sessions}")
                return succes(f"Aucune session en cours (reste seulement : {statuts}). Tout est arrete.")

            nom = min(actives, key=lambda x: essais.get(x, 0))
            essais[nom] = essais.get(nom, 0) + 1
            if essais[nom] > essais_par_session:
                return echec(f"'{nom}' ne s'arrete pas apres {essais_par_session} tentatives")
            log(f"{len(actives)} session(s) en cours : {actives} (statuts : {statuts}). Traitement de '{nom}' "
                f"(tentative {essais[nom]}/{essais_par_session}, via les 3 points de Active Events).")
            ok = stop_par_menu(nom)
            if ok:
                if nom not in res["fermees"]:
                    res["fermees"].append(nom)
                log(f"'{nom}' arretee.")
            else:
                log(f"'{nom}' n'est pas arretee : on recommence.")
                time.sleep(pause)

        return echec(f"delai de {delai_total} s depasse, il reste des sessions en cours")
    except Exception as e:
        log("EXCEPTION NON PREVUE :\n" + traceback.format_exc())
        return echec(f"exception : {type(e).__name__} : {e}")

# ==== CELLULE #2 titre="# Main" ====
# description: 
# Ouvre le notebook, demarre sa session et clique sur Run (cf. cellule "# Fonctions Kaggle").
# False = ne relance PAS le notebook (execution du fichier entier = seulement le clic Active Events).
# Mettre True pour ouvrir le notebook, demarrer la session et lancer le Run.
LANCER_NOTEBOOK = False
if LANCER_NOTEBOOK:
    resultat = ouvrir_et_lancer_notebook("Sautoniax5")
    print(resultat)
else:
    print("Notebook non relance (LANCER_NOTEBOOK = False).")

# ==== CELLULE #3 titre="# Active Events" ====
# description: Ferme TOUTES les sessions actives (desactive par defaut : l'execution du fichier entier ne coupe plus rien).
# False = ne fait rien (le fichier entier peut etre execute : l'arret se fait ensuite depuis l'app de bureau).
# Mettre True pour ouvrir "View Active Events" puis fermer TOUTES les sessions actives (3 points -> Stop Session).
ARRETER_TOUTES_SESSIONS = False
import traceback
if ARRETER_TOUTES_SESSIONS:
    print("=== Cellule Active Events : version v22 ===", flush=True)
    try:
        resultat_active_events = ouvrir_active_events()
        print(resultat_active_events, flush=True)
        resultat_fermeture = fermer_sessions_actives()
        print({k: v for k, v in resultat_fermeture.items() if k != "logs"}, flush=True)
    except Exception:
        print("ERREUR DANS LA CELLULE :\n" + traceback.format_exc(), flush=True)
else:
    print("Aucune session arretee (ARRETER_TOUTES_SESSIONS = False).", flush=True)

# ==== CELLULE #4 titre="# Pilotage" ====
# description: Pont de fichiers avec l'app SautoniaxManager : publie l'etat du bot, execute demarrer / arreter / actualiser (un onglet par notebook).
# BOUCLE BLOQUANTE : derniere cellule, peut etre lancee via "Tout executer" (la cellule "# Active Events" est desactivee par defaut, elle n'arrete plus rien).
# AU DEMARRAGE (phase "verification", boutons de l'app grises) :
#   1. liste des onglets (list_tabs) : lesquels sont deja sur kaggle.com, lesquels sont un notebook connu (retrouves par leur url) ;
#   2. onglets de notebook deja ouverts -> on verifie SEULEMENT lesquels sont en cours d'execution (lecture d'Active Events : aucune navigation, aucun clic) ;
#      un onglet kaggle.com sans notebook suffit aussi a prouver que Kaggle repond (meme lecture, sans navigation) ;
#   3. aucun onglet sur kaggle.com -> on va sur kaggle.com (onglet d'accueil) pour verifier que Kaggle est disponible (etat publie : cle "kaggle").
#   Un notebook trouve arrete avec son onglet est actualise juste avant son prochain demarrage (pas au demarrage du pilotage).
# JOURNAL : evenements seulement (ordres, onglet choisi, changements de statut, erreurs, noms des sessions Active Events). Memoire + ecriture GROUPEE
#   dans <PONT_DIR>/logs/<BOT_ID>.log (jamais une ecriture par ligne) + les LOG_LIGNES_PONT dernieres lignes publiees dans le pont (cle "logs", affichees par l'app).
# Arret propre : _P_STOP.set() depuis une autre cellule, ou creer le fichier agents/<BOT_ID>/stop.json dans le dossier du pont.
# Protocole (meme principe qu'IngXAi, dossier propre a SautoniaxManager) :
#   agents/<BOT_ID>.json            bot -> app : etat, signe de vie (ts), notebooks {nom: {statut, detail}}
#   agents/<BOT_ID>/inbox/*.json    app -> bot : {"id", "type": "demarrer"|"arreter"|"actualiser", "notebook" | "notebooks"}   ("demarrer" + "notebooks" = LOT : ouverture + Start de tous, puis Run au fur et a mesure)
#   agents/<BOT_ID>/outbox/*.json   bot -> app : {"type": "accuse", "id", "ordre", "ok", "erreur", "duree_s"}
import os, socket, threading, traceback
from pathlib import Path

# ---- Reglages ----
PONT_DIR = Path(os.environ.get("SAUTONIAXMANAGER_BRIDGE") or "D:/ScaleTube/CHANNELS/IngeniaX/Code/AutoniaX/SautoniaxManager/pont")   # = PONT_DEFAUT de l'app
def _p_profil_clone():
    """Nom du PROFIL de ce clone, lu dans la ligne de commande de son executeur (--instance-id sautoniax-<12 hex>-<profil>) :
    unique par profil, stable d'un redemarrage a l'autre. Deux clones sur la meme machine ont le meme nom d'hote : c'est lui qui les distingue."""
    try:
        import sys as _sys
        a = list(_sys.argv)
        if "--instance-id" in a:
            iid = str(a[a.index("--instance-id") + 1])
            m = re.match(r"^sautoniax-[^-]+-(.+)$", iid)    # session = 12 hex, ou "isole" pour un profil isole
            return (m.group(1) if m else iid).strip()
    except Exception:
        pass
    return ""

_PROFIL = _p_profil_clone()
_ENV_ID = os.environ.get("SAUTONIAX_BOT_ID") or _PROFIL
if _ENV_ID:
    BOT_ID = "bot-" + (re.sub(r"[^a-z0-9]+", "", _ENV_ID.lower()) or "clone")[:24]
else:    # dernier recours : nom d'hote + PID (sinon deux clones d'une meme machine s'ecrasent le meme fichier du pont)
    BOT_ID = "bot-" + (re.sub(r"[^a-z0-9]+", "", socket.gethostname().lower()) or "clone")[:10] + "-" + str(os.getpid())
COMPTE = os.environ.get("SAUTONIAX_COMPTE") or _PROFIL or BOT_ID    # nom affiche dans l'app (remplace par le nom du compte Kaggle lu sur l'accueil)
NOTEBOOKS = [n.strip() for n in (os.environ.get("SAUTONIAX_NOTEBOOKS") or "").split(",") if n.strip()]    # notebooks de CE bot (variable SAUTONIAX_NOTEBOOKS par clone, ex. "Sautoniax0,Sautoniax1")
PREFIXE_NOTEBOOKS = "sautoniax"    # les notebooks de la liste "Edited" dont le nom commence ainsi sont ajoutes a l'app ("" = tous)
URL_KAGGLE = "https://www.kaggle.com"
SIGNE_VIE_S = 3.0        # periode d'ecriture du signe de vie (thread a part : il continue pendant un long demarrage)
SCRUTATION_S = 1.0       # periode de lecture de l'inbox
RAFRAICHIR_S = 60.0      # periode de relecture d'Active Events (source de verite de "en cours") quand aucun ordre n'attend
ESSAIS_VERIF_KAGGLE = 3    # tentatives pour joindre kaggle.com quand aucun onglet n'y est
PAUSE_VERIF_KAGGLE_S = 5.0
LOG_LIGNES_PONT = 40     # dernieres lignes du journal publiees dans le pont pour l'app
LOG_FICHIER_MAX = 1000000  # octets : au-dela, le fichier devient <BOT_ID>.old
LANCER_PILOTAGE = True

# ---- Etat partage (le thread du signe de vie lit, la boucle principale ecrit) ----
_P_LOCK = threading.RLock()
_P_ETAT = {}        # nom -> {"statut": arrete|demarrage|en_cours|arret|erreur|inconnu, "detail": str}
_P_ONGLETS = {}     # nom -> tab_id  (jamais suppose valide : toujours recoupe avec list_tabs())
_P_INFO = {"etat": "actif", "phase": "demarrage", "debut": time.time()}
_P_STOP = threading.Event()
_P_ACCUEIL = {"id": None}    # onglet de reference : page d'accueil kaggle.com (liste des notebooks, Active Events) ; jamais utilise pour un notebook
_RE_ACCUEIL = r"^https?://(www\.)?kaggle\.com/?(\?[^#]*)?(#.*)?$"
_P_COURANT = {"nom": None}    # notebook dont le demarrage est en cours (lu par le veilleur)
_P_LOT = {"noms": [], "annules": set()}    # lot de demarrage en cours (noms) et slugs retires du lot par un ordre d'arret (lus par le veilleur)
PAUSE_ENTRE_OUVERTURES = 2.0    # pause (s) entre l'ouverture de deux onglets de notebook
PAUSE_CHARGEMENT_LOT = 15.0    # minimum (s) entre l'ouverture d'un notebook et son clic sur Start session
TIMEOUT_NOUVEL_ONGLET = 30.0    # attente (s) du chargement d'un NOUVEL onglet. retry=0 : UNE seule tentative (chaque nouvelle tentative de new_tab ouvre un onglet de plus,
#                                 l'ancien restant ouvert). Sans ces valeurs new_tab prenait RETRY=3 / TIMEOUT=10 de la cellule "Fonctions Kaggle" : 4 onglets pour 1.
DELAI_RUN_LOT = 20.0    # attente (s) avant de constater qu'un Run clique ne tourne pas, et de recliquer
ESSAIS_RUN_LOT = 3    # clics max sur Run par notebook
ESSAIS_OUVERTURE = 3    # passes max d'ouverture : un notebook dont l'ouverture echoue est reessaye APRES les autres
MOTS_REESSAI = ("onglet", "playwright", "timeout", "navigation", "ouvert", "runtimeerror")
DELAI_SESSION_LOT = 300.0    # attente max (s) du demarrage de la session d'un notebook du lot, apres son Start session
REVEIL_S = 0.0    # periode (s) du reveil AUTOMATIQUE (0 = desactive) : seul l'ordre "reveiller" envoye par l'app (bouton de la carte du bot) reveille
SELECTEUR_CELLULES = 'iframe[name="notebook-editor-cells"]'    # zone des cellules : une iframe d'un AUTRE domaine (jupyter-proxy.kaggle.net), inaccessible en JS -> vrai clic souris sur l'iframe
_P_LOGS = []        # journal en memoire (200 dernieres lignes)
_P_A_ECRIRE = []    # lignes pas encore ecrites sur disque
_P_FLAGS = {"raf_ko": False, "sessions": None}
_P_ABSENTS = {}   # nom -> nb de relectures consecutives ou un notebook "en cours" est absent d'Active Events (anti-clignotement)

def _p_session_suivie(nom):
    """Active Events liste AUSSI les editions de dataset (bouton "More options for undefined", nom type "AX xxx_protonmail") :
    seules les sessions de NOTEBOOK suivies comptent (NOTEBOOKS, ou nom commencant par PREFIXE_NOTEBOOKS)."""
    n = (nom or "").strip()
    if not n or n.lower() == "undefined":
        return False
    if _slug_kaggle(n) in {_slug_kaggle(x) for x in NOTEBOOKS}:
        return True
    return (not PREFIXE_NOTEBOOKS) or n.lower().startswith(PREFIXE_NOTEBOOKS.lower())
_P_ACTUALISER_AVANT = set()   # notebooks trouves arretes avec leur onglet : actualises juste avant leur prochain demarrage


def _p_log(msg, niveau="INFO", echo=True):
    """Une ligne de journal. echo=False : deja affichee par la fonction appelee (on ne la garde que dans le journal)."""
    ligne = f"{time.strftime('%H:%M:%S')} {niveau:<5} {msg}"
    with _P_LOCK:
        _P_LOGS.append(ligne)
        del _P_LOGS[:-200]
        _P_A_ECRIRE.append(ligne)
    if echo:
        print("[pilotage] " + ligne, flush=True)


def _p_log_vider():
    """Ecrit d'un coup les lignes en attente (appele a la fin de chaque ordre et par le signe de vie, jamais par ligne)."""
    with _P_LOCK:
        if not _P_A_ECRIRE:
            return
        lignes = list(_P_A_ECRIRE)
        del _P_A_ECRIRE[:]
    fichier = PONT_DIR / "logs" / f"{BOT_ID}.log"
    try:
        fichier.parent.mkdir(parents=True, exist_ok=True)
        if fichier.exists() and fichier.stat().st_size > LOG_FICHIER_MAX:
            os.replace(fichier, fichier.with_suffix(".old"))
        with open(fichier, "a", encoding="utf-8") as f:
            f.write("\n".join(lignes) + "\n")
    except OSError:
        pass


def _p_ecrire(chemin, data):
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    tmp = chemin.with_name(chemin.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, chemin)


def _p_lire(chemin):
    try:
        return json.loads(Path(chemin).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _p_set(nom, statut, detail=""):
    with _P_LOCK:
        avant = _P_ETAT.get(nom, {}).get("statut")
        _P_ETAT[nom] = {"statut": statut, "detail": detail}
    if avant != statut:
        _p_log(f"{nom} : {avant or '-'} -> {statut}" + (f" ({detail})" if detail else ""), "ERROR" if statut == "erreur" else "INFO")


def _p_publier():
    with _P_LOCK:
        data = dict(_P_INFO, profil=COMPTE, compte=(_P_FLAGS.get("compte") or COMPTE), executant=socket.gethostname(), pid=os.getpid(),
                    ts=time.time(), notebooks={n: dict(v) for n, v in _P_ETAT.items()}, logs=_P_LOGS[-LOG_LIGNES_PONT:],
                    reveil={n: dict(v) for n, v in (_P_FLAGS.get("reveil") or {}).items()})
    try:
        _p_ecrire(PONT_DIR / "agents" / f"{BOT_ID}.json", data)
    except OSError:
        pass


def _p_battement(stop):
    while not stop.wait(SIGNE_VIE_S):
        _p_publier()
        _p_log_vider()


def _p_veilleur(stop, inbox):
    """Thread a part : pendant un demarrage (notebook seul ou LOT), un ordre d'arret qui vise un notebook du lot (present dans l'inbox,
    sans le consommer) l'ecarte : s'il est en cours de manipulation son demarrage est annule, sinon il est simplement retire du lot
    (_P_LOT["annules"]). La boucle principale execute ensuite l'arret. Un arret qui vise d'AUTRES notebooks attend la fin du lot
    (un seul onglet est manipule a la fois)."""
    while not stop.wait(1.0):
        with _P_LOCK:
            nom = _P_COURANT.get("nom")
            lot = list(_P_LOT.get("noms") or [])
        if not (nom or lot):
            continue
        slug_cour = _slug_kaggle(nom) if nom else None
        slugs_lot = {_slug_kaggle(n): n for n in lot}
        if nom:
            slugs_lot.setdefault(slug_cour, nom)
        try:
            fichiers = list(Path(inbox).glob("*.json"))
        except OSError:
            continue
        for f in fichiers:
            o = _p_lire(f)
            if not (isinstance(o, dict) and o.get("type") == "arreter"):
                continue
            for n in (o.get("notebooks") or []):
                sl = _slug_kaggle(str(n))
                if sl not in slugs_lot:
                    continue
                if sl == slug_cour:
                    if not _ANNULATION.is_set():
                        _p_log(f"ordre d'arret recu pendant le demarrage de {slugs_lot[sl]} : demarrage annule")
                        _ANNULATION.set()
                else:
                    with _P_LOCK:
                        if sl not in _P_LOT["annules"]:
                            _P_LOT["annules"].add(sl)
                            _p_log(f"ordre d'arret recu : {slugs_lot[sl]} retire du lot de demarrage")


def _p_js(code):
    try:
        return Instance.instance().evaluer_js(code, retry=RETRY, timeout=TIMEOUT)
    except Exception as e:
        return {"_erreur": str(e)}


def _p_tabs(strict=False):
    """list_tabs(). strict=True : None si la lecture echoue (on ne confond jamais "illisible" et "aucun onglet")."""
    try:
        return list(Instance.instance().list_tabs() or [])
    except Exception as e:
        if strict:
            _p_log(f"list_tabs impossible : {type(e).__name__} : {e}", "ERROR")
            return None
        return []


def _p_synchroniser():
    """Recoupe la table notebook -> onglet avec list_tabs() : oublie les onglets disparus, retrouve ceux dont l'url est un notebook connu."""
    tabs = _p_tabs(strict=True)
    if tabs is None:
        raise RuntimeError("liste des onglets illisible")
    ids = {t.get("id") for t in tabs}
    with _P_LOCK:
        for nom in [n for n, i in _P_ONGLETS.items() if i not in ids]:
            _p_log(f"onglet {_P_ONGLETS[nom]} de {nom} disparu : oublie", "WARN")
            del _P_ONGLETS[nom]
        pris = set(_P_ONGLETS.values())
        for t in tabs:
            if t.get("id") in pris:
                continue
            for nom in set(NOTEBOOKS) | set(_P_ETAT):
                motif = r"kaggle\.com/code/[^/]+/" + re.escape(_slug_kaggle(nom)) + r"(?:[/?#]|$)"
                if nom not in _P_ONGLETS and re.search(motif, t.get("url") or "", re.I):
                    _P_ONGLETS[nom] = t["id"]
                    pris.add(t["id"])
                    _p_log(f"onglet {t['id']} retrouve par son url pour {nom}")
    return tabs


def _p_assurer_accueil():
    """Onglet d'accueil kaggle.com : celui deja connu, sinon un onglet DEJA sur l'accueil (non associe a un notebook), sinon on en CREE un.
    Retourne (tab_id | None, neuf). None = liste des onglets illisible ou creation impossible (repli : un onglet kaggle.com quelconque)."""
    tabs = _p_tabs(strict=True)
    if tabs is None:
        return None, False
    ids = {t.get("id") for t in tabs}
    with _P_LOCK:
        tid = _P_ACCUEIL["id"]
        pris = set(_P_ONGLETS.values())
    if tid is not None and tid in ids:
        return tid, False
    for t in tabs:
        if t.get("id") not in pris and re.match(_RE_ACCUEIL, t.get("url") or "", re.I):
            with _P_LOCK:
                _P_ACCUEIL["id"] = t["id"]
            _p_log(f"onglet d'accueil Kaggle deja ouvert : {t['id']}")
            return t["id"], False
    try:
        r = Instance.instance().new_tab(URL_KAGGLE, retry=0, timeout=TIMEOUT_NOUVEL_ONGLET)
    except Exception as e:
        _p_log(f"creation de l'onglet d'accueil impossible : {type(e).__name__} : {e}", "WARN")
        return None, False
    if not r or not getattr(r, "tab_id", None):
        _p_log(f"creation de l'onglet d'accueil impossible : {getattr(r, 'message', '')}", "WARN")
        return None, False
    with _P_LOCK:
        _P_ACCUEIL["id"] = r.tab_id
    _p_log(f"onglet d'accueil Kaggle cree : {r.tab_id}")
    return r.tab_id, True


def _p_preparer_accueil(tid):
    """Onglet d'accueil fraichement cree : attend son chargement, detecte la page de connexion, replie Viewed / deplie Edited
    et ajoute a l'app les notebooks de la liste Edited. Retourne True si Kaggle repond."""
    try:
        Instance.instance().switch_tab(tid)
    except Exception as e:
        _p_log(f"switch_tab({tid}) impossible : {e}", "WARN")
    fin = time.time() + 30
    while time.time() < fin and _p_js(_JS_PAGE_COMPLETE) is not True:
        time.sleep(1.0)
    url = _p_js("location.href")
    url = url if isinstance(url, str) else ""
    if re.search(r"/(login|signin|sign-in)(?:[/?#]|$)", url, re.I):
        _p_set_kaggle("non_connecte", url[:120])
        return False
    if not _p_est_kaggle(url):
        etat, detail = _p_verifier_kaggle(onglet=tid)
        _p_set_kaggle(etat, detail)
        return etat == "disponible"
    _p_set_kaggle("disponible")
    for _ in range(6):    # la barre laterale s'affiche un peu apres le chargement
        if _p_decouvrir_sidebar():
            _P_FLAGS["sidebar_t"] = time.time()
            return True
        time.sleep(2.0)
    _p_log("accueil : barre laterale (Viewed/Edited) illisible", "WARN")
    return True


def _p_choisir_onglet(nom):
    """(tab_id, neuf). Onglet deja associe a CE notebook s'il existe ; sinon un NOUVEL onglet (sur kaggle.com).
    L'onglet d'accueil et les onglets etrangers ne sont jamais reutilises."""
    inst = Instance.instance()
    tabs = _p_synchroniser()
    with _P_LOCK:
        _p_log("onglets : " + str([(t.get("id"), (t.get("url") or "")[:55]) for t in tabs]) + f" ; table : {dict(_P_ONGLETS)} ; accueil : {_P_ACCUEIL['id']}", "DEBUG")
        if nom in _P_ONGLETS:
            _p_log(f"{nom} : onglet {_P_ONGLETS[nom]} deja associe, reutilise")
            return _P_ONGLETS[nom], False
    with _P_LOCK:    # onglet d'accueil kaggle.com LIBRE (ni la reference, ni un notebook) : reutilise au lieu d'en creer un de plus
        pris = set(_P_ONGLETS.values()) | {_P_ACCUEIL["id"]}
    libre = next((t.get("id") for t in tabs if t.get("id") not in pris and re.match(_RE_ACCUEIL, t.get("url") or "", re.I)), None)
    if libre is not None:
        try:
            inst.switch_tab(libre)
            _p_log(f"{nom} : onglet d'accueil libre {libre} reutilise (pas de nouvel onglet)")
            return libre, True
        except Exception as e:
            _p_log(f"{nom} : onglet libre {libre} inutilisable ({e}) : nouvel onglet", "WARN")
    _p_log(f"{nom} : ouverture d'un nouvel onglet")
    avant = {t.get("id") for t in _p_tabs()}
    try:
        r = inst.new_tab(URL_KAGGLE, retry=0, timeout=TIMEOUT_NOUVEL_ONGLET)
        erreur = None if (r and getattr(r, "tab_id", None)) else str(getattr(r, "message", "") or "echec")
    except Exception as e:
        r, erreur = None, f"{type(e).__name__} : {e}"
    if erreur is None:
        _p_log(f"{nom} : nouvel onglet {r.tab_id}")
        return r.tab_id, True
    # Echec annonce (timeout Playwright...) : le navigateur a souvent CREE l'onglet quand meme (et ses nouvelles tentatives internes
    # en creent d'autres). On prend l'onglet cree au lieu de declarer un echec : les autres restent des onglets d'accueil libres, reutilises ensuite.
    time.sleep(1.5)
    nouveaux = [t.get("id") for t in _p_tabs() if t.get("id") not in avant]
    if nouveaux:
        tid = nouveaux[-1]
        try:
            inst.switch_tab(tid)
        except Exception as e:
            _p_log(f"{nom} : switch_tab({tid}) impossible : {e}", "WARN")
        _p_log(f"{nom} : creation annoncee en echec ({erreur[:80]}) mais {len(nouveaux)} onglet(s) cree(s) : {tid} utilise", "WARN")
        return tid, True
    raise RuntimeError(f"ouverture d'un onglet impossible : {erreur}")


def _p_demarrer(nom):
    ok, erreur, _res = _p_demarrer_lot([nom])
    return ok, erreur


def _p_demarrer_lot(noms):
    """Demarrage EN 2 PHASES d'un lot de notebooks :
      PHASE 1 : pour chaque notebook (un onglet chacun) : ouverture + Internet + clic sur Start session, SANS attendre la fin du demarrage.
      PHASE 2 : on tourne sur les onglets ; des qu'une session est demarree, clic sur Run (une a la fois, dans l'ordre ou elles sont pretes).
    Un ordre d'arret visant un notebook du lot le retire (voir _p_veilleur). Retourne (ok, erreur, {nom: {"ok", "erreur"}})."""
    noms = [n for n in dict.fromkeys(noms or []) if n]
    if not noms:
        return False, "nom de notebook manquant", {}
    t0 = time.time()
    resultats = {}
    _ANNULATION.clear()
    with _P_LOCK:
        _P_LOT["noms"], _P_LOT["annules"] = list(noms), set()
    for n in noms:
        if n in _P_ACTUALISER_AVANT:    # trouve arrete au demarrage du pilotage : onglet actualise avant de redemarrer
            try:
                _p_actualiser(n)
            except Exception as e:
                _p_log(f"{n} : actualisation avant demarrage impossible : {e}", "WARN")
            _P_ACTUALISER_AVANT.discard(n)
        _p_set(n, "demarrage", "en attente d'ouverture")

    def retire(n):
        with _P_LOCK:
            return _slug_kaggle(n) in _P_LOT["annules"]

    def termine(n, ok, erreur=""):
        resultats[n] = {"ok": bool(ok), "erreur": erreur}
        if erreur.startswith("annule"):
            _p_set(n, "arret", "demarrage annule")
            _p_log(f"demarrer {n} : ANNULE par un ordre d'arret")
        else:
            _p_set(n, "en_cours" if ok else "erreur", erreur)
            _p_log(f"demarrer {n} : {'ok' if ok else 'ECHEC ' + erreur} (onglet {_P_ONGLETS.get(n)})", "INFO" if ok else "ERROR")

    def agir(n, fn):
        """Execute fn() sur le notebook n (marque comme courant pour le veilleur). Retourne (resultat, erreur_annulation_ou_exception)."""
        _ANNULATION.clear()
        with _P_LOCK:
            _P_COURANT["nom"] = n
        try:
            return fn(), None
        except DemarrageAnnule:
            return {"ok": False}, "annule par l'utilisateur"
        except Exception as e:
            _p_log(f"{n} : exception {type(e).__name__} : {e}", "ERROR")
            return {"ok": False}, f"{type(e).__name__} : {e}"[:150]
        finally:
            with _P_LOCK:
                _P_COURANT["nom"] = None
            _ANNULATION.clear()

    def ouvrir(n):
        _p_set(n, "demarrage", "ouverture du notebook")
        tid, neuf = _p_choisir_onglet(n)
        if not neuf:
            Instance.instance().switch_tab(tid)
        with _P_LOCK:
            _P_ONGLETS[n] = tid
        return ouvrir_et_lancer_notebook(n, lancer_run=False, attendre_session=False, ouvrir_seulement=True)

    def demarrer_nb(n):
        """2e passe : l'onglet est deja ouvert (et a charge pendant que les autres s'ouvraient) -> Internet + Start session."""
        _p_set(n, "demarrage", "demarrage de la session")
        tid = _P_ONGLETS.get(n)
        if tid is None:
            raise RuntimeError("onglet du notebook introuvable")
        Instance.instance().switch_tab(tid)
        return ouvrir_et_lancer_notebook(n, lancer_run=False, attendre_session=False)

    def lancer(n, neuve=True):
        # forcer_run : un vieil onglet peut garder le marqueur "Run deja clique" d'une session precedente (le Run serait alors ignore)
        return ouvrir_et_lancer_notebook(n, demarrer_session=False, lancer_run=True, session_neuve=neuve, forcer_run=True, attendre_run=False)

    try:
        # ---- PHASE 1 : ouvrir + Start session sur chaque notebook ----
        lot_passe = list(noms)
        for passe in range(1, ESSAIS_OUVERTURE + 1):
            if not lot_passe:
                break
            a_reouvrir = []
            if passe > 1:
                _p_log(f"nouvel essai d'ouverture (passe {passe}/{ESSAIS_OUVERTURE}) : {lot_passe}")
                time.sleep(5.0)
            verif = {}    # nom -> {"t", "essais"} : Run clique, "Run en cours" pas encore constate (on est deja passe au notebook suivant)
            attente = {}    # nom -> instant du clic sur Start session (notebooks dont la session demarre, Run pas encore clique)
            _p_log(f"demarrage en 3 passes (passe {passe}) : ouvrir tous les onglets de {lot_passe}, puis Start session de chacun, puis Run au fur et a mesure")

            def ouverture_ko(n, r, err):
                msg = err or str(r.get("erreur") or "echec")[:150]
                if passe < ESSAIS_OUVERTURE and not msg.startswith("annule") and any(k in msg.lower() for k in MOTS_REESSAI):
                    a_reouvrir.append(n)    # ouverture echouee (navigateur lent, onglet non cree...) : reessai apres les autres
                    _p_set(n, "demarrage", "ouverture echouee : nouvel essai plus tard")
                    _p_log(f"{n} : ouverture echouee ({msg[:100]}) : nouvel essai apres les autres notebooks", "WARN")
                else:
                    termine(n, False, msg)

            # PASSE A : ouvrir TOUS les onglets a la suite, sans attendre le chargement des notebooks (ils chargent en arriere-plan)
            ouverts = {}    # nom -> instant de l'ouverture
            for n in lot_passe:
                if retire(n):
                    termine(n, False, "annule par l'utilisateur")
                    continue
                r, err = agir(n, lambda n=n: ouvrir(n))
                for e in r.get("etapes", []):
                    _p_log(f"  {n} : {e}", "DEBUG", echo=False)
                if err or not r.get("ok"):
                    ouverture_ko(n, r, err)
                else:
                    ouverts[n] = time.time()
                    _p_set(n, "demarrage", "notebook en chargement")
                    time.sleep(PAUSE_ENTRE_OUVERTURES)    # petit decalage : evite de charger toutes les pages lourdes au meme instant
            # PASSE B : on repasse sur chaque onglet (deja charge, ou presque) : Internet + Start session
            for n in list(ouverts):
                if retire(n):
                    termine(n, False, "annule par l'utilisateur")
                    continue
                reste = PAUSE_CHARGEMENT_LOT - (time.time() - ouverts[n])    # le minimum de 15 s apres l'ouverture est conserve, mais deja ecoule
                if reste > 0:
                    time.sleep(reste)
                r, err = agir(n, lambda n=n: demarrer_nb(n))
                for e in r.get("etapes", []):
                    _p_log(f"  {n} : {e}", "DEBUG", echo=False)
                if err or not r.get("ok"):
                    ouverture_ko(n, r, err)
                else:
                    attente[n] = time.time()
                    _p_set(n, "demarrage", "session en cours de demarrage")
            # ---- PHASE 2 : Run des que la session de chaque notebook est demarree ----
            if attente:
                _p_log(f"phase 2 : attente des sessions de {list(attente)} pour cliquer sur Run")
            def apres_run(n, r, err, essais):
                for x in r.get("etapes", []):
                    _p_log(f"  {n} : {x}", "DEBUG", echo=False)
                if err:
                    termine(n, False, err)
                elif not r.get("ok"):
                    termine(n, False, str(r.get("erreur") or "echec")[:150])
                elif r.get("run") == "clique":    # on ne reste pas : on passe au suivant, la verification se fait plus loin
                    verif[n] = {"t": time.time(), "essais": essais}
                    _p_set(n, "demarrage", f"Run clique : verification ({essais}/{ESSAIS_RUN_LOT})")
                else:
                    termine(n, True)    # Run deja en cours

            while attente or verif:
                for n in list(attente):
                    if retire(n):
                        del attente[n]
                        termine(n, False, "annule par l'utilisateur")
                        continue
                    tid = _P_ONGLETS.get(n)
                    if tid is None:
                        del attente[n]
                        termine(n, False, "onglet du notebook introuvable")
                        continue
                    try:
                        Instance.instance().switch_tab(tid)
                    except Exception as e:
                        _p_log(f"switch_tab({tid}) impossible : {e}", "WARN")
                    e = _p_js(_JS_ETAT_SESSION)
                    pret = isinstance(e, dict) and bool(e.get("stop")) and not e.get("start")
                    if pret:
                        _p_set(n, "demarrage", "session demarree : lancement du Run")
                        _p_log(f"{n} : session demarree, clic sur Run")
                        del attente[n]
                        r, err = agir(n, lambda n=n: lancer(n))
                        apres_run(n, r, err, 1)
                    elif time.time() - attente[n] > DELAI_SESSION_LOT:
                        del attente[n]
                        termine(n, False, "la session n'a pas demarre dans le delai")
                    elif isinstance(e, dict) and e.get("statut"):
                        _p_set(n, "demarrage", f"session : {str(e.get('statut'))[:40]}")
                for n in list(verif):    # confirme que le Run tourne vraiment ; sinon reclique (jusqu'a ESSAIS_RUN_LOT clics)
                    if retire(n):
                        del verif[n]
                        termine(n, False, "annule par l'utilisateur")
                        continue
                    try:
                        Instance.instance().switch_tab(_P_ONGLETS[n])
                    except Exception as e:
                        _p_log(f"switch_tab impossible pour {n} : {e}", "WARN")
                    if _p_js(_JS_RUN_EN_COURS) is True:
                        del verif[n]
                        _p_log(f"{n} : Run en cours (confirme)")
                        termine(n, True)
                    elif time.time() - verif[n]["t"] > DELAI_RUN_LOT:
                        essais = verif.pop(n)["essais"]
                        if essais >= ESSAIS_RUN_LOT:
                            termine(n, False, f"le Run n'a pas demarre apres {essais} clic(s)")
                        else:
                            _p_log(f"{n} : Run non demarre apres {DELAI_RUN_LOT:.0f} s : nouveau clic ({essais + 1}/{ESSAIS_RUN_LOT})", "WARN")
                            r, err = agir(n, lambda n=n: lancer(n, neuve=False))
                            apres_run(n, r, err, essais + 1)
                if attente or verif:
                    time.sleep(2.0)
            lot_passe = a_reouvrir
    finally:
        with _P_LOCK:
            _P_LOT["noms"], _P_LOT["annules"] = [], set()
            _P_COURANT["nom"] = None
        _ANNULATION.clear()
    for n in noms:
        if n not in resultats:
            termine(n, False, "non traite")
    echecs = {n: v["erreur"] for n, v in resultats.items() if not v["ok"]}
    ok = not echecs
    erreur = "" if ok else "; ".join(f"{n} : {e}" for n, e in echecs.items())[:150]
    _p_log(f"lot {noms} : {len(noms) - len(echecs)}/{len(noms)} ok ({time.time() - t0:.1f} s)", "INFO" if ok else "ERROR")
    return ok, erreur, resultats


def _p_actualiser(nom):
    """Recharge l'onglet du notebook (switch_tab puis naviguer sur sa propre url) : aucune methode dediee, aucune fermeture d'onglet."""
    if _P_ETAT.get(nom, {}).get("statut") in ("en_cours", "demarrage"):
        _p_log(f"actualiser {nom} refuse : le notebook est en cours", "WARN")
        return False, "notebook en cours : actualisation refusee"
    inst = Instance.instance()
    _p_synchroniser()
    tid = _P_ONGLETS.get(nom)
    if tid is None:
        _p_log(f"actualiser {nom} : aucun onglet connu", "WARN")
        return False, "aucun onglet pour ce notebook"
    inst.switch_tab(tid)
    url = next((t.get("url") for t in _p_tabs() if t.get("id") == tid), "") or URL_KAGGLE
    r = inst.naviguer(url, retry=RETRY, timeout=30.0)
    if not r:
        _p_log(f"actualiser {nom} : navigation impossible sur {url} : {getattr(r, 'message', '')}", "ERROR")
        return False, f"actualisation impossible : {getattr(r, 'message', '')}"
    _P_ACTUALISER_AVANT.discard(nom)
    _p_log(f"{nom} : onglet {tid} actualise ({url[:70]})")
    return True, ""


_JS_SANTE_NOTEBOOK = r"""
const f = document.querySelector('iframe[name="notebook-editor-cells"]');
const r = f ? f.getBoundingClientRect() : null;
return {url: location.href, stop: !!document.querySelector('button[aria-label="Stop session"]'),
        start: !!document.querySelector('button[aria-label="Start session"]'),
        iframe: !!f, visible: !!r && r.width > 50 && r.height > 50};
"""


def _p_reveiller_un(inst, nom):
    """Reveille l'onglet d'UN notebook en cours : onglet connu et sur la bonne page, page vivante, session non coupee, puis un VRAI clic souris
    sur la zone des cellules (iframe d'un autre domaine : pas de JS possible dedans). Un onglet disparu est ABANDONNE : jamais rouvert.
    Retourne {"ok": bool, "erreur": str}."""
    tid = _P_ONGLETS.get(nom)
    if tid is None:
        return {"ok": False, "erreur": "onglet absent : abandonne"}
    onglet = next((t for t in _p_tabs() if t.get("id") == tid), None)
    if onglet is None:
        _P_ONGLETS.pop(nom, None)
        return {"ok": False, "erreur": "onglet absent : abandonne"}
    url = onglet.get("url") or ""
    motif = r"kaggle\.com/code/[^/]+/" + re.escape(_slug_kaggle(nom)) + r"(?:[/?#]|$)"
    if not re.search(motif, url, re.I):
        return {"ok": False, "erreur": f"onglet sur une autre page ({url[:60]}) : abandonne"}
    try:
        inst.switch_tab(tid)
    except Exception as e:
        return {"ok": False, "erreur": f"switch_tab impossible : {e}"}
    time.sleep(1.0)
    s = _p_js(_JS_SANTE_NOTEBOOK)
    if not isinstance(s, dict) or s.get("_erreur"):
        return {"ok": False, "erreur": "page morte (aucune reponse JS) : " + str((s or {}).get("_erreur") if isinstance(s, dict) else s)[:80]}
    if s.get("start") and not s.get("stop"):
        return {"ok": False, "erreur": "session coupee (Start session affiche)"}
    if not (s.get("iframe") and s.get("visible")):
        return {"ok": False, "erreur": "zone des cellules introuvable (page incomplete)"}
    try:
        r = inst.click_element(SELECTEUR_CELLULES, scroll=False, retry=0, timeout=15.0)
    except Exception as e:
        return {"ok": False, "erreur": f"clic impossible : {type(e).__name__} : {e}"}
    if not r:
        return {"ok": False, "erreur": "clic refuse : " + str(getattr(r, "message", ""))[:100]}
    return {"ok": True, "erreur": ""}


def _p_reveiller(noms=None):
    """Reveille les onglets des notebooks EN COURS (ou de `noms`). Retourne ({nom: {"ok", "erreur"}}, erreur_globale).
    Ne rouvre ni ne navigue aucun onglet ; liste d'onglets illisible = on saute ce tour (jamais conclure a tort a un onglet absent).
    L'onglet d'accueil est reactive a la fin (la relecture d'Active Events travaille sur l'onglet actif)."""
    with _P_LOCK:
        cibles = [n for n, v in _P_ETAT.items() if v.get("statut") == "en_cours"]
    if noms:
        cibles = [n for n in dict.fromkeys(noms) if n]
    if not cibles:
        return {}, ""
    try:
        tabs = _p_synchroniser()
    except Exception as e:
        _p_log(f"reveil : onglets illisibles, tour saute ({e})", "WARN")
        return {}, "liste des onglets illisible : reveil saute"
    inst = Instance.instance()
    resultats = {}
    for nom in cibles:
        if _P_ETAT.get(nom, {}).get("statut") != "en_cours":
            res = {"ok": False, "erreur": "notebook pas en cours"}
        else:
            try:
                res = _p_reveiller_un(inst, nom)
            except Exception as e:
                res = {"ok": False, "erreur": f"{type(e).__name__} : {e}"}
        resultats[nom] = res
        avant = (_P_FLAGS.setdefault("reveil", {}).get(nom) or {})
        _P_FLAGS["reveil"][nom] = {"ok": res["ok"], "detail": res["erreur"], "ts": time.time()}
        if avant.get("ok") != res["ok"] or avant.get("detail") != res["erreur"] or not res["ok"]:
            _p_log(f"reveil {nom} : " + ("OK (clic dans la zone des cellules)" if res["ok"] else "ECHEC " + res["erreur"]), "INFO" if res["ok"] else "WARN")
    acc = _P_ACCUEIL.get("id")
    if acc is not None and acc in {t.get("id") for t in (_p_tabs() or [])}:
        try:
            inst.switch_tab(acc)
        except Exception as e:
            _p_log(f"reveil : retour a l'accueil impossible : {e}", "WARN")
    return resultats, ""


def _p_arreter(noms):
    """Arrete UNIQUEMENT les sessions de ces notebooks (Active Events, par nom), puis actualise leurs onglets."""
    noms = [n for n in dict.fromkeys(noms) if n]
    if not noms:
        return False, "aucun notebook"
    t0 = time.time()
    _p_log(f"arreter : cibles {noms}")
    for n in noms:
        _p_set(n, "arret")
    try:
        _p_synchroniser()
    except Exception as e:
        _p_log(f"synchronisation des onglets impossible ({e}) : onglet actif utilise", "WARN")
    tid = next((_P_ONGLETS[n] for n in noms if n in _P_ONGLETS), None) or _P_ACCUEIL["id"]
    if tid is not None:
        try:
            Instance.instance().switch_tab(tid)    # Active Events couvre tout le compte : n'importe quel onglet Kaggle suffit
        except Exception:
            pass
    _p_log(f"arreter : onglet utilise pour Active Events : {tid or 'onglet actif'}")
    res = fermer_sessions_actives(noms=noms)
    for l in res.get("logs", []):
        _p_log("  " + l, "DEBUG", echo=False)
    fermees = {_slug_kaggle(n) for n in res.get("fermees", [])}
    ok = bool(res.get("ok"))
    erreur = "" if ok else str(res.get("erreur") or "echec")[:150]
    for n in noms:
        if ok or _slug_kaggle(n) in fermees:
            _p_set(n, "arrete")
        else:
            _p_set(n, "erreur", erreur)
    _P_ACTUALISER_AVANT.difference_update(noms)
    if ok:
        for n in noms:
            try:
                _p_actualiser(n)
            except Exception as e:
                _p_log(f"actualisation de {n} impossible : {e}", "ERROR")
    _p_log(f"arreter {noms} : {'ok' if ok else 'ECHEC ' + erreur} ({time.time() - t0:.1f} s, fermees : {res.get('fermees')})", "INFO" if ok else "ERROR")
    return ok, erreur


def _p_est_kaggle(url):
    return bool(re.search(r"^https?://([a-z0-9-]+\.)*kaggle\.com(?:[/?#:]|$)", url or "", re.I))


def _p_onglet_kaggle(tabs):
    """Id d'un onglet deja sur kaggle.com (l'onglet actif s'il y est, sinon le premier), ou None."""
    kag = [t for t in tabs if _p_est_kaggle(t.get("url"))]
    return next((t["id"] for t in kag if t.get("actif")), kag[0]["id"] if kag else None)


def _p_set_kaggle(etat, detail=""):
    with _P_LOCK:
        avant = _P_INFO.get("kaggle")
        _P_INFO["kaggle"], _P_INFO["kaggle_detail"] = etat, detail
    if avant != etat:
        _p_log(f"Kaggle : {avant or '-'} -> {etat}" + (f" ({detail})" if detail else ""), "INFO" if etat == "disponible" else "ERROR")


def _p_lire_compte():
    """Nom du compte Kaggle (titre Welcome, <nom>! de l'accueil) : sert de nom au bot dans l'app."""
    try:
        r = _p_js(r"""const h = document.querySelector('h1'); const m = h ? (h.innerText || '').match(/^Welcome,\s*(.+?)!?$/) : null; return m ? m[1].trim() : '';""")
        if isinstance(r, str) and r.strip():
            _P_FLAGS["compte"] = r.strip()[:40]
    except Exception:
        pass


def _p_decouvrir_sidebar():
    """Sur l'ACCUEIL kaggle.com : replie Viewed, deplie Edited, et ajoute a l'app les notebooks (prefixe PREFIXE_NOTEBOOKS) qu'elle ne connait pas."""
    _p_lire_compte()
    r = _p_js(_JS_SIDEBAR_PREPARER)
    if isinstance(r, dict) and r.get("ok") and not r.get("pret"):
        time.sleep(1.5)    # on vient de cliquer : relecture pour avoir la liste Edited
        r = _p_js(_JS_SIDEBAR_PREPARER)
    if not (isinstance(r, dict) and r.get("ok")):
        return False
    ajouts = []
    with _P_LOCK:
        connus = {_slug_kaggle(n) for n in set(NOTEBOOKS) | set(_P_ETAT)}
        for n in r.get("notebooks") or []:
            if PREFIXE_NOTEBOOKS and not n.lower().startswith(PREFIXE_NOTEBOOKS.lower()):
                continue
            if _slug_kaggle(n) in connus:
                continue
            _P_ETAT[n] = {"statut": "inconnu", "detail": ""}
            connus.add(_slug_kaggle(n))
            ajouts.append(n)
    for n in ajouts:
        _p_log(f"notebook decouvert dans Edited : {n}")
    return True


def _p_verifier_kaggle(onglet=None):
    """Kaggle est-il joignable ? Va sur kaggle.com dans l'onglet d'accueil (sinon l'onglet actif). A n'appeler que si AUCUN onglet n'est deja sur
    kaggle.com. Retourne (etat, detail) : "disponible" | "non_connecte" (page de connexion) | "indisponible"."""
    inst = Instance.instance()
    try:
        accueil = onglet or inst.tab_accueil()
        if accueil in {t.get("id") for t in _p_tabs()}:
            inst.switch_tab(accueil)
    except Exception as e:
        _p_log(f"onglet d'accueil inaccessible ({e}) : onglet actif utilise", "WARN")
    detail = ""
    for essai in range(1, ESSAIS_VERIF_KAGGLE + 1):
        r = inst.naviguer(URL_KAGGLE, retry=RETRY, timeout=30.0)
        if r:
            fin = time.time() + 20
            while time.time() < fin and _p_js(_JS_PAGE_COMPLETE) is not True:
                time.sleep(1.0)
            url = _p_js("location.href")
            url = url if isinstance(url, str) else ""
            if re.search(r"/(login|signin|sign-in)(?:[/?#]|$)", url, re.I):
                return "non_connecte", url[:120]
            if _p_est_kaggle(url):
                try:
                    _p_decouvrir_sidebar()
                except Exception as e:
                    _p_log(f"lecture de la barre laterale impossible : {e}", "WARN")
                return "disponible", ""
            detail = f"page inattendue : {url or '?'}"[:120]
        else:
            detail = str(getattr(r, "message", "") or "navigation impossible")[:120]
        _p_log(f"kaggle.com : essai {essai}/{ESSAIS_VERIF_KAGGLE} : {detail}", "WARN")
        if essai < ESSAIS_VERIF_KAGGLE:
            time.sleep(PAUSE_VERIF_KAGGLE_S)
    return "indisponible", detail


def _p_rafraichir():
    """Statuts reels d'apres le panneau Active Events (Running / Cancelling / Cancelled). Un seul appel JS.
    Onglet deja sur kaggle.com : on l'utilise (switch_tab si besoin), sans naviguer. Aucun : on verifie Kaggle en allant sur kaggle.com."""
    tabs = _p_tabs(strict=True)
    if tabs is None:
        return False    # liste illisible : on ne touche a aucun onglet
    tid, neuf = _p_assurer_accueil()    # onglet d'accueil de reference : cree s'il n'existe pas
    if neuf:
        _p_preparer_accueil(tid)
        tabs = _p_tabs(strict=True) or tabs
    if tid is None:
        tid = _p_onglet_kaggle(tabs)    # repli : creation impossible, un onglet kaggle.com quelconque
    if tid is None:
        _p_log("aucun onglet sur kaggle.com : verification de la disponibilite de Kaggle")
        etat, detail = _p_verifier_kaggle()
        _p_set_kaggle(etat, detail)
        if etat != "disponible":
            return False
    else:
        if tid != next((t.get("id") for t in tabs if t.get("actif")), None):
            try:
                Instance.instance().switch_tab(tid)
            except Exception as e:
                _p_log(f"switch_tab({tid}) impossible : {e}", "WARN")
        _p_set_kaggle("disponible")
        url_onglet = next((t.get("url") for t in tabs if t.get("id") == tid), "") or ""
        if re.match(_RE_ACCUEIL, url_onglet, re.I) and time.time() - _P_FLAGS.get("sidebar_t", 0) > 300:    # accueil : la barre laterale liste les notebooks (relue toutes les 5 min)
            try:
                _p_decouvrir_sidebar()
                _P_FLAGS["sidebar_t"] = time.time()
            except Exception as e:
                _p_log(f"lecture de la barre laterale impossible : {e}", "WARN")
    l = _p_js(_JS_LISTER_OUVRIR)
    for _ in range(4):    # le clic vient d'ouvrir le panneau : React le rend un peu apres, on relit (sans recliquer : aria-expanded est alors "true")
        if isinstance(l, dict) and l.get("ouvert"):
            break
        if not (isinstance(l, dict) and (l.get("clique") or l.get("bouton"))):
            break
        time.sleep(1.5)
        l = _p_js(_JS_LISTER_OUVRIR)
    if not (isinstance(l, dict) and l.get("ouvert") and isinstance(l.get("sessions"), list)):
        if not _P_FLAGS["raf_ko"]:
            _P_FLAGS["raf_ko"] = True
            _p_log(f"relecture Active Events impossible (onglet actif sur : {next((t.get('url') for t in _p_tabs() if t.get('actif')), '?')}) ; reponse : {str(l)[:120]}", "WARN")
        return False
    if not l["sessions"] and l.get("badge"):
        return False    # panneau pas encore rempli : on ne conclut pas
    _P_FLAGS["raf_ko"] = False
    statuts = l.get("statuts") or {}
    par_slug = {_slug_kaggle(s): statuts.get(s, "") for s in l["sessions"]}
    if sorted(l["sessions"]) != _P_FLAGS["sessions"]:
        _P_FLAGS["sessions"] = sorted(l["sessions"])
        _p_log(f"Active Events : sessions {l['sessions']} (suivies : {[s for s in l['sessions'] if _p_session_suivie(s)]}) statuts {statuts}", "DEBUG")
        if any((x or "").strip().lower() == "undefined" for x in l["sessions"]):
            _p_log(f"Active Events : noms 'undefined' (editions de dataset ?) ; texte du panneau : {l.get('textes')}", "DEBUG")
    changements = []
    with _P_LOCK:
        connus = {_slug_kaggle(n) for n in set(NOTEBOOKS) | set(_P_ETAT)}
        for s in l["sessions"]:    # une session inconnue du bot (lancee a la main, autre notebook) apparait dans l'app
            if not _p_session_suivie(s):
                continue    # edition de dataset ou autre : jamais un notebook
            if _slug_kaggle(s) not in connus:
                _P_ETAT[s] = {"statut": "inconnu", "detail": ""}
                connus.add(_slug_kaggle(s))
                _p_log(f"notebook decouvert via Active Events : {s}")
        for nom in set(NOTEBOOKS) | set(_P_ETAT):
            courant = _P_ETAT.get(nom, {}).get("statut")
            s = par_slug.get(_slug_kaggle(nom))
            if s is None or re.search(r"cancelled|complet|fail|error|stopp|dismiss", s, re.I):
                reel = "arrete"
            elif re.search(r"cancelling", s, re.I):
                reel = "arret"
            else:
                reel = "en_cours"
            if reel == "arrete" and courant == "erreur":
                continue    # l'erreur reste affichee jusqu'au prochain ordre
            if s is None and courant == "en_cours":    # absent (panneau en cours de chargement ?) : on exige 2 relectures de suite
                _P_ABSENTS[nom] = _P_ABSENTS.get(nom, 0) + 1
                if _P_ABSENTS[nom] < 2:
                    continue
            else:
                _P_ABSENTS[nom] = 0
            if courant != reel:
                _P_ETAT[nom] = {"statut": reel, "detail": ""}
                changements.append(f"{nom} : {courant or '-'} -> {reel} (Active Events : {s if s is not None else 'absent'})")
    for c in changements:
        _p_log(c)
    return True


def _p_lire_ordres(inbox):
    ordres = []
    for f in sorted(Path(inbox).glob("*.json")):
        o = _p_lire(f)
        try:
            f.unlink()
        except OSError:
            pass
        if isinstance(o, dict):
            ordres.append(o)
        else:
            _p_log(f"ordre illisible ignore : {Path(f).name}", "WARN")
    return ordres


def _p_executer(o, outbox):
    typ, t0, ok, erreur, resultats = o.get("type"), time.time(), False, "", None
    with _P_LOCK:
        _P_INFO["phase"] = str(typ)
    _p_log(f"ordre recu : {typ} {o.get('notebook') or o.get('notebooks') or ''} (id {o.get('id')})")
    try:
        if typ == "demarrer":
            lot = [str(n) for n in (o.get("notebooks") or [])] or [str(o.get("notebook") or "")]
            ok, erreur, resultats = _p_demarrer_lot(lot)
        elif typ == "arreter":
            ok, erreur = _p_arreter([str(n) for n in (o.get("notebooks") or [])])
        elif typ == "actualiser":
            ok, erreur = _p_actualiser(str(o.get("notebook") or ""))
        elif typ == "reveiller":
            noms_rv = [str(n) for n in (o.get("notebooks") or [])] or None
            resultats, err_rv = _p_reveiller(noms_rv)
            ok = bool(resultats) and not err_rv and all(v["ok"] for v in resultats.values())
            erreur = err_rv or "; ".join(f"{n} : {v['erreur']}" for n, v in resultats.items() if not v["ok"]) or ("" if resultats else "aucun notebook en cours")
        else:
            erreur = f"ordre inconnu : {typ}"
    except Exception as e:
        erreur = f"{type(e).__name__} : {e}"
        _p_log("EXCEPTION : " + traceback.format_exc().strip().replace("\n", " | ")[-600:], "ERROR")
    with _P_LOCK:
        _P_INFO["phase"] = "attente"
    oid = str(o.get("id") or time.time_ns())
    try:
        _p_ecrire(Path(outbox) / f"{oid}.json", {"type": "accuse", "id": oid, "ordre": typ, "ok": bool(ok),
                                                 "erreur": erreur, "duree_s": round(time.time() - t0, 1),
                                                 **({"resultats": resultats} if resultats else {})})
    except OSError as e:
        _p_log(f"accuse non ecrit : {e}", "ERROR")
    _p_log(f"accuse {typ} : ok={bool(ok)} {erreur} ({time.time() - t0:.1f} s)", "INFO" if ok else "ERROR")
    _p_log_vider()


def _p_verification_initiale():
    """Demarrage : onglets Kaggle deja ouverts ? notebooks deja en cours ? sinon Kaggle repond-il ? Retourne True si les statuts ont pu etre lus."""
    tabs = _p_tabs(strict=True)
    if tabs is None:
        _p_log("verification initiale impossible (onglets illisibles) : reprise a la relecture periodique", "ERROR")
        return False
    _p_synchroniser()
    kag = [t for t in tabs if _p_est_kaggle(t.get("url"))]
    with _P_LOCK:
        nb = dict(_P_ONGLETS)
    _p_log(f"verification initiale : {len(tabs)} onglet(s), {len(kag)} sur kaggle.com ; notebooks deja ouverts : {nb or 'aucun'}")
    _p_log("un onglet d'accueil kaggle.com sert de reference (liste des notebooks, Active Events) : utilise s'il existe, sinon cree ; "
           "les onglets deja ouverts ne sont ni navigues ni fermes" + (f" ; onglets de notebook retrouves : {sorted(nb)}" if nb else ""))
    _p_publier()    # la liste decouverte (Edited) est visible dans l'app sans attendre Active Events
    ok = _p_rafraichir()
    _p_publier()
    with _P_LOCK:
        for nom in nb:
            if _P_ETAT.get(nom, {}).get("statut") == "arrete":
                _P_ACTUALISER_AVANT.add(nom)
        resume = {n: v["statut"] for n, v in _P_ETAT.items()}
    _p_log(f"verification initiale {'terminee' if ok else 'INCOMPLETE'} : {resume} ; Kaggle : {_P_INFO.get('kaggle')}"
           + (f" ; a actualiser avant leur prochain demarrage : {sorted(_P_ACTUALISER_AVANT)}" if _P_ACTUALISER_AVANT else ""))
    return ok


def pilotage():
    global _P_STOP
    _P_STOP = threading.Event()
    stop = _P_STOP
    global BOT_ID
    try:    # un AUTRE processus publie deja sous ce BOT_ID (clones au meme nom de machine) : sinon ils s'ecrasent le fichier et les ordres
        autre = _p_lire(PONT_DIR / "agents" / f"{BOT_ID}.json")
        if isinstance(autre, dict) and time.time() - float(autre.get("ts") or 0) < 10 and autre.get("pid") != os.getpid():
            BOT_ID = f"{BOT_ID}-{os.getpid()}"[:24]
            print(f"[pilotage] BOT_ID deja utilise par un autre processus vivant -> {BOT_ID} (definir SAUTONIAX_BOT_ID par clone)", flush=True)
    except Exception:
        pass
    base = PONT_DIR / "agents" / BOT_ID
    _p_log(f"===== pilotage {time.strftime('%Y-%m-%d')} : {BOT_ID} ({COMPTE}) sur {socket.gethostname()}, pid {os.getpid()}, pont {PONT_DIR}, notebooks {NOTEBOOKS} =====")
    try:
        (base / "inbox").mkdir(parents=True, exist_ok=True)
        (base / "outbox").mkdir(parents=True, exist_ok=True)
    except OSError as e:
        _p_log(f"dossier du pont inaccessible ({PONT_DIR}) : {e}", "ERROR")
        _p_log_vider()
        return
    perimes = list((base / "inbox").glob("*.json"))
    for f in perimes:    # ordres d'une session precedente : perimes
        f.unlink()
    if perimes:
        _p_log(f"{len(perimes)} ordre(s) perime(s) d'une session precedente ignore(s)", "WARN")
    for nom in NOTEBOOKS:
        _P_ETAT.setdefault(nom, {"statut": "inconnu", "detail": ""})
    with _P_LOCK:
        _P_INFO.update(etat="actif", phase="verification", debut=time.time(), kaggle="inconnu", kaggle_detail="")
    _p_publier()
    battement = threading.Thread(target=_p_battement, args=(stop,), daemon=True)
    battement.start()
    veilleur = threading.Thread(target=_p_veilleur, args=(stop, base / "inbox"), daemon=True)
    veilleur.start()
    dernier = 0.0
    dernier_reveil = time.time()
    try:
        try:
            if _p_verification_initiale():
                dernier = time.time()
        except Exception as e:
            _p_log(f"verification initiale : exception {type(e).__name__} : {e}", "ERROR")
        with _P_LOCK:
            _P_INFO["phase"] = "attente"
        _p_publier()
        while not stop.is_set():
            fichier_stop = base / "stop.json"
            if fichier_stop.exists():
                try:
                    fichier_stop.unlink()
                except OSError:
                    pass
                break
            ordres = _p_lire_ordres(base / "inbox")
            for o in ordres:
                _p_executer(o, base / "outbox")
            if not ordres and time.time() - dernier >= RAFRAICHIR_S:
                try:
                    _p_rafraichir()
                except Exception as e:
                    _p_log(f"relecture Active Events : exception {type(e).__name__} : {e}", "ERROR")
                dernier = time.time()
            if not ordres and REVEIL_S > 0 and time.time() - dernier_reveil >= REVEIL_S:    # reveil periodique des onglets de notebooks en cours
                dernier_reveil = time.time()
                try:
                    _p_reveiller()
                except Exception as e:
                    _p_log(f"reveil periodique : exception {type(e).__name__} : {e}", "ERROR")
            stop.wait(SCRUTATION_S)
    except Exception:
        _p_log("ERREUR BOUCLE : " + traceback.format_exc().strip().replace("\n", " | ")[-600:], "ERROR")
    finally:
        stop.set()
        battement.join(timeout=SIGNE_VIE_S + 2)
        with _P_LOCK:
            _P_INFO.update(etat="arrete", phase="")
        _p_log("pilotage arrete")
        _p_publier()
        _p_log_vider()


if LANCER_PILOTAGE:
    pilotage()
else:
    print("Pilotage non lance (LANCER_PILOTAGE = False).")
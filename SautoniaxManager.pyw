# -*- coding: utf-8 -*-
"""
SautoniaxManager : pilotage des clones (bots connectés à un compte Kaggle).

  - à gauche, les bots (comptes) ; à droite, les notebooks du bot choisi avec leur statut ;
  - on COCHE les notebooks voulus, puis « Démarrer la sélection » (UN seul bouton) ou « Arrêter la sélection » ;
  - les démarrages sont SÉQUENTIELS (un seul onglet du navigateur manipulé à la fois) : dès qu'un notebook est démarré, l'app envoie
    automatiquement le suivant de la file (statut « En file ») ; l'ordre est celui de la liste, de haut en bas ;
  - on peut arrêter à tout moment, y compris pendant un démarrage (le démarrage en cours est annulé, les notebooks encore en file sont retirés) ;
  - l'arrêt passe toujours par Active Events côté bot, jamais par le bouton de la barre du notebook.

Pont de fichiers propre à SautoniaxManager (même protocole que IngXAi, dossier distinct) :
    agents/bot-xxx.json            le bot : état, signe de vie (ts), notebooks {nom: {statut, detail}}
    agents/bot-xxx/inbox/*.json    app -> bot : {"id", "type": "demarrer"|"arreter"|"actualiser", ...}
    agents/bot-xxx/outbox/*.json   bot -> app : {"type": "accuse", "id", "ordre", "ok", "erreur", "duree_s"}
Le dossier du pont est le même que celui de la cellule « # Pilotage » de SautoniaxManager.py (PONT_DIR).

Notebooks affichés : ceux que CHAQUE bot publie ; notebooks.json ({"par_bot": {"bot-xxx": [...]}}) permet d'en ajouter à un bot précis.
Pas de liste commune : chaque bot est isolé (sidebar, notebooks, file de démarrage / arrêt).

Journal : bouton « Journal » en bas à droite. Onglet « Bot » = dernières lignes publiées par le clone (clé "logs" du pont ; le fichier complet
est <pont>/logs/bot-xxx.log) ; onglet « App » = ordres envoyés, accusés, bots qui apparaissent / se déconnectent (fichier complet : journal.log
dans le dossier de config de l'app, écrit à chaque événement, jamais par rafraîchissement).

Dépendances : pip install PySide6 qtawesome
"""
import sys
import os
import json
import time
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl, QSize
from PySide6.QtGui import QDesktopServices, QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
                               QListWidgetItem, QLabel, QPushButton, QCheckBox, QFrame, QScrollArea,
                               QPlainTextEdit, QTabWidget, QSystemTrayIcon, QMenu, QToolButton)
from collections import deque
import qtawesome as qta

APP_DIR = Path(os.environ.get("APPDATA") or (Path.home() / ".config")) / "SautoniaxManager"
CONFIG_FILE = APP_DIR / "notebooks.json"
JOURNAL_FILE = APP_DIR / "journal.log"
PONT_DEFAUT = Path("D:/ScaleTube/CHANNELS/IngeniaX/Code/AutoniaX/SautoniaxManager/pont")   # = PONT_DIR de la cellule « # Pilotage »
BOT_VIVANT_S = 20.0      # signe de vie plus vieux : bot hors ligne
BOT_OUBLI_S = 120.0      # signe de vie plus vieux : bot masqué

BLEU, BLEU_FONCE, BLEU_CLAIR = "#1E6FE0", "#1558B8", "#E8F1FD"
FOND, PANNEAU, BORD = "#FFFFFF", "#F5F8FD", "#D6E2F5"
TEXTE, GRIS, ROUGE = "#1B2A41", "#7A8BA6", "#D64545"

# statut -> (libellé, icône qtawesome, couleur) : le libellé accompagne toujours l'icône
STATUTS = {
    "arrete": ("Arrêté", "mdi6.stop-circle-outline", GRIS),
    "demarrage": ("Démarrage…", "mdi6.progress-clock", BLEU),
    "en_cours": ("En cours", "mdi6.play-circle", BLEU),
    "arret": ("Arrêt en cours…", "mdi6.progress-clock", BLEU),
    "erreur": ("Erreur", "mdi6.alert-circle", ROUGE),
    "inconnu": ("Arrêté", "mdi6.stop-circle-outline", GRIS),
    "file": ("En file", "mdi6.timer-sand", GRIS),      # statut local à l'app : coché pour démarrer, ordre pas encore envoyé
}
PEUT_DEMARRER = {"arrete", "erreur", "inconnu"}
PEUT_ARRETER = {"en_cours", "demarrage", "erreur", "file"}

QSS = f"""
QWidget {{ background: {FOND}; color: {TEXTE}; font-size: 13px; }}
QMainWindow, QScrollArea, QScrollArea > QWidget > QWidget {{ background: {FOND}; }}
QWidget#gauche {{ background: {PANNEAU}; border-right: 1px solid {BORD}; }}
QListWidget {{ background: {PANNEAU}; border: none; border-right: 1px solid {BORD}; outline: none; }}
QListWidget::item {{ border-bottom: 1px solid {BORD}; padding: 0px; }}
QListWidget::item:hover {{ background: #EDF3FC; }}
QListWidget::item:selected {{ background: {BLEU_CLAIR}; border-left: 3px solid {BLEU}; color: {TEXTE}; }}
QListWidget::item:selected:!active {{ background: {BLEU_CLAIR}; }}
QFrame#ligne {{ background: {PANNEAU}; border: 1px solid {BORD}; border-radius: 8px; }}
QLabel#titre {{ font-size: 20px; font-weight: 600; background: transparent; }}
QLabel#doux {{ color: {GRIS}; background: transparent; }}
QLabel {{ background: transparent; }}
QPushButton {{ background: {BLEU}; color: white; border: none; border-radius: 6px; padding: 7px 14px; }}
QPushButton:hover {{ background: {BLEU_FONCE}; }}
QPushButton:disabled {{ background: {BORD}; color: {GRIS}; }}
QPushButton#discret {{ background: {BLEU_CLAIR}; color: {BLEU_FONCE}; }}
QPushButton#discret:hover {{ background: {BORD}; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {BLEU}; border-radius: 3px; background: white; }}
QCheckBox::indicator:checked {{ background: {BLEU}; }}
QCheckBox::indicator:disabled {{ border-color: {BORD}; }}
QPlainTextEdit {{ background: {PANNEAU}; border: 1px solid {BORD}; font-family: Consolas, "DejaVu Sans Mono", monospace; font-size: 12px; }}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{ padding: 5px 14px; background: {PANNEAU}; border: 1px solid {BORD}; border-bottom: none; color: {GRIS}; }}
QTabBar::tab:selected {{ background: {BLEU_CLAIR}; color: {BLEU_FONCE}; font-weight: 600; }}
"""


def journal_ecrire(ligne):
    """Une ligne dans journal.log (appelé seulement sur événement ; au-delà de 1 Mo le fichier devient journal.old)."""
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        if JOURNAL_FILE.exists() and JOURNAL_FILE.stat().st_size > 1_000_000:
            os.replace(JOURNAL_FILE, JOURNAL_FILE.with_suffix(".old"))
        with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
            f.write(ligne + "\n")
    except OSError:
        pass


def _json_read(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _json_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


class Pont:
    """Côté app du pont de fichiers."""

    def __init__(self, base=None):
        self.base = Path(base) if base else Path(os.environ.get("SAUTONIAXMANAGER_BRIDGE") or PONT_DEFAUT)

    def effacer(self, bid):
        """Supprime le fichier d'état d'un bot (s'il revient en ligne, il réécrit son fichier et réapparaît)."""
        try:
            (self.base / "agents" / f"{bid}.json").unlink()
            return True
        except OSError:
            return False

    def scan(self):
        """{bot_id: {..., 'age', 'vivant'}} des bots vus récemment (les bots arrêtés ou oubliés sont masqués)."""
        bots = {}
        d = self.base / "agents"
        if not d.is_dir():
            return bots
        now = time.time()
        for f in d.glob("bot-*.json"):
            info = _json_read(f)
            if not isinstance(info, dict) or info.get("etat") == "arrete":
                continue
            age = now - float(info.get("ts") or 0)
            if age > BOT_OUBLI_S:
                continue
            info["age"] = age
            info["vivant"] = age <= BOT_VIVANT_S
            info["notebooks"] = info.get("notebooks") if isinstance(info.get("notebooks"), dict) else {}
            bots[f.stem] = info
        return bots

    def _envoyer(self, bot, data):
        oid = str(time.time_ns())
        data = dict(data, id=oid, cle=bot)
        _json_write(self.base / "agents" / bot / "inbox" / f"{oid}.json", data)
        return oid

    def demarrer(self, bot, notebooks):
        """UN ordre pour tout le lot : le bot ouvre et démarre la session de chaque notebook, puis clique sur Run au fur et à mesure."""
        if isinstance(notebooks, str):
            notebooks = [notebooks]
        return self._envoyer(bot, {"type": "demarrer", "notebooks": list(notebooks)})

    def arreter(self, bot, notebooks):
        return self._envoyer(bot, {"type": "arreter", "notebooks": list(notebooks)})

    def actualiser(self, bot, notebook):
        return self._envoyer(bot, {"type": "actualiser", "notebook": notebook})

    def reveiller(self, bot, notebooks):
        """Ordre de reveil : le bot active l'onglet de chaque notebook en cours, verifie la page et clique dans la zone des cellules."""
        return self._envoyer(bot, {"type": "reveiller", "notebooks": list(notebooks)})

    def accuses(self):
        out = []
        d = self.base / "agents"
        if not d.is_dir():
            return out
        for b in d.iterdir():
            if b.is_dir():
                for f in sorted((b / "outbox").glob("*.json")):
                    a = _json_read(f)
                    if isinstance(a, dict):
                        out.append((b.name, f, a))
        return out

    @staticmethod
    def done(path):
        try:
            Path(path).unlink()
        except OSError:
            pass


def notebooks_du_bot(bot_id, info):
    """Notebooks de CE bot uniquement : ceux qu'il publie lui-même + ceux de par_bot[bot_id] dans la config.
    Aucune liste commune : les notebooks d'un bot n'apparaissent jamais chez un autre."""
    cfg = _json_read(CONFIG_FILE)
    cfg = cfg if isinstance(cfg, dict) else {}
    par_bot = cfg.get("par_bot") if isinstance(cfg.get("par_bot"), dict) else {}
    noms = list(par_bot.get(bot_id) or [])
    for n in (info.get("notebooks") or {}):
        if n not in noms:
            noms.append(n)
    return [str(n) for n in noms if str(n).strip() and str(n).strip().lower() != "undefined"]


def ouvrir_config():
    if not CONFIG_FILE.exists():
        _json_write(CONFIG_FILE, {"par_bot": {}})
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(CONFIG_FILE)))


class BotCarte(QWidget):
    def __init__(self, bid, on_reveil=None):
        super().__init__()
        self.bid = bid
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        self.pastille = QLabel()
        lay.addWidget(self.pastille)
        col = QVBoxLayout()
        col.setSpacing(1)
        self.nom = QLabel()
        self.nom.setStyleSheet("font-weight: 600;")
        self.sous = QLabel()
        self.sous.setObjectName("doux")
        col.addWidget(self.nom)
        col.addWidget(self.sous)
        lay.addLayout(col, 1)
        self.btn_reveil = QToolButton()    # ordre manuel : réveille les onglets de tous les notebooks en cours de CE bot
        self.btn_reveil.setAutoRaise(True)
        try:
            self.btn_reveil.setIcon(qta.icon("mdi6.cursor-default-click-outline", color=BLEU_FONCE))
        except Exception:
            self.btn_reveil.setIcon(qta.icon("mdi6.refresh", color=BLEU_FONCE))
        self.btn_reveil.setFixedSize(30, 30)
        self.btn_reveil.setIconSize(QSize(20, 20))
        self.btn_reveil.setToolTip("Réveiller : active l'onglet de chaque notebook en cours et clique dans une cellule")
        if on_reveil is not None:
            self.btn_reveil.clicked.connect(lambda _c=False: on_reveil(self.bid))
        lay.addWidget(self.btn_reveil)
        self.setFixedHeight(56)    # hauteur fixe : plus de ligne écrasée / tronquée dans la sidebar
        self.setAttribute(Qt.WA_TranslucentBackground)

    def maj(self, info):
        vivant = info.get("vivant")
        self.pastille.setPixmap(qta.icon("mdi6.monitor-dashboard" if vivant else "mdi6.lan-disconnect",
                                         color=BLEU if vivant else GRIS).pixmap(22, 22))
        self.nom.setText(str(info.get("compte") or info.get("profil") or self.bid))
        n = sum(1 for v in info["notebooks"].values() if isinstance(v, dict) and v.get("statut") == "en_cours")
        self.sous.setText(f"{n} en cours" if vivant else "Hors ligne")
        self.btn_reveil.setEnabled(bool(vivant) and n > 0)


class LigneNotebook(QFrame):
    def __init__(self, nom, on_coche):
        super().__init__()
        self.nom = nom
        self.setObjectName("ligne")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)
        self.coche = QCheckBox()
        self.coche.toggled.connect(lambda _c: on_coche())
        lay.addWidget(self.coche)
        icone = QLabel()
        icone.setPixmap(qta.icon("mdi6.notebook-outline", color=BLEU_FONCE).pixmap(20, 20))
        lay.addWidget(icone)
        self.label = QLabel(nom)
        self.label.setStyleSheet("font-weight: 600;")
        lay.addWidget(self.label)
        lay.addStretch(1)
        self.detail = QLabel()
        self.detail.setObjectName("doux")
        self.detail.setMaximumWidth(200)
        lay.addWidget(self.detail)
        self.pastille = QLabel()
        lay.addWidget(self.pastille)
        self.statut = QLabel()
        self.statut.setMinimumWidth(105)
        lay.addWidget(self.statut)
        self.statut_code = "inconnu"
        self.peut_demarrer = False
        self.peut_arreter = False

    def maj(self, statut, detail, vivant, attente):
        """attente : None, ou le type de l'ordre envoyé et pas encore accusé (\"demarrer\" | \"arreter\")."""
        self.statut_code = statut if statut in STATUTS else "inconnu"
        libelle, icone, couleur = STATUTS[self.statut_code]
        self.pastille.setPixmap(qta.icon(icone, color=couleur).pixmap(18, 18))
        self.statut.setText(libelle)
        self.statut.setStyleSheet(f"color: {couleur}; font-weight: 600;")
        if attente == "arreter":
            texte = "Arrêt demandé…"
        elif self.statut_code == "file":
            texte = "En attente de son tour"
        elif attente == "demarrer" and self.statut_code != "demarrage":
            texte = "Ordre envoyé…"
        else:
            texte = detail
        self.detail.setText(self.detail.fontMetrics().elidedText(texte, Qt.ElideRight, 190))   # texte complet : info-bulle + journal
        self.detail.setToolTip(texte)
        rouge = (self.statut_code == "erreur" or detail.startswith("echec")) and attente is None
        self.detail.setStyleSheet(f"color: {ROUGE};" if rouge else "")
        # Un seul jeu de cases : « Démarrer la sélection » prend les cases démarrables, « Arrêter la sélection » les arrêtables.
        # On peut arrêter PENDANT un démarrage (la case n'est bloquée que par un arrêt déjà demandé ou en cours).
        actif = bool(vivant) and attente != "arreter" and self.statut_code != "arret"
        self.peut_demarrer = actif and self.statut_code in PEUT_DEMARRER and attente != "demarrer"
        self.peut_arreter = actif and self.statut_code in PEUT_ARRETER
        self.coche.setEnabled(self.peut_demarrer or self.peut_arreter)
        if not self.coche.isEnabled() and self.coche.isChecked():
            self.coche.setChecked(False)

    def coche_demarrer(self):
        return self.coche.isChecked() and self.peut_demarrer

    def coche_arreter(self):
        return self.coche.isChecked() and self.peut_arreter


class Fenetre(QMainWindow):
    def __init__(self, pont=None):
        super().__init__()
        self.pont = pont or Pont()
        self.setWindowTitle("SautoniaxManager")
        self.setWindowIcon(qta.icon("mdi6.monitor-dashboard", color=BLEU))
        self._creer_tray()
        self.setMinimumSize(900, 520)
        self.resize(1000, 640)
        self.bots = {}
        self.items = {}            # bid -> (QListWidgetItem, BotCarte)
        self.lignes = {}           # nom -> LigneNotebook (bot affiché)
        self.bot_affiche = None
        self.attente = {}          # (bot, nom) -> {"id", "t0", "type"}
        self.file = {}             # bot -> deque de notebooks cochés pour démarrer, pas encore envoyés (un seul ordre de démarrage à la fois)
        self.dernier = {}          # (bot, nom) -> texte (durée mesurée côté app, erreur éventuelle)
        self.journal_app = deque(maxlen=300)
        self.vivant_prec = {}      # bid -> bool, pour journaliser les connexions / déconnexions
        self.cache_bot = None      # texte déjà affiché dans l'onglet « Bot »

        centre = QWidget()
        self.setCentralWidget(centre)
        racine = QHBoxLayout(centre)
        racine.setContentsMargins(0, 0, 0, 0)
        racine.setSpacing(0)

        gauche = QWidget()
        gauche.setFixedWidth(260)
        gauche.setObjectName("gauche")
        gauche_lay = QVBoxLayout(gauche)
        gauche_lay.setContentsMargins(0, 0, 0, 0)
        gauche_lay.setSpacing(0)
        self.liste = QListWidget()
        self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.liste.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.liste.setSpacing(0)
        self.liste.currentItemChanged.connect(self._bot_choisi)
        gauche_lay.addWidget(self.liste, 1)
        bas_gauche = QHBoxLayout()
        bas_gauche.setContentsMargins(10, 8, 10, 8)
        self.btn_effacer = QPushButton(" Effacer les hors ligne")
        self.btn_effacer.setObjectName("discret")
        self.btn_effacer.setIcon(qta.icon("mdi6.delete-sweep-outline", color=BLEU_FONCE))
        self.btn_effacer.clicked.connect(self._effacer_hors_ligne)
        bas_gauche.addWidget(self.btn_effacer)
        gauche_lay.addLayout(bas_gauche)
        racine.addWidget(gauche)

        droite = QVBoxLayout()
        droite.setContentsMargins(24, 20, 24, 16)
        droite.setSpacing(10)
        racine.addLayout(droite, 1)

        entete = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        self.titre = QLabel("Aucun bot connecté")
        self.titre.setObjectName("titre")
        self.sous_titre = QLabel()
        self.sous_titre.setObjectName("doux")
        col.addWidget(self.titre)
        col.addWidget(self.sous_titre)
        entete.addLayout(col, 1)
        self.btn_tout_cocher = QPushButton()
        self.btn_tout_cocher.setObjectName("discret")
        self.btn_tout_cocher.setIcon(qta.icon("mdi6.checkbox-multiple-marked-outline", color=BLEU_FONCE))
        self.btn_tout_cocher.setToolTip("Tout sélectionner")
        self.btn_tout_decocher = QPushButton()
        self.btn_tout_decocher.setObjectName("discret")
        self.btn_tout_decocher.setIcon(qta.icon("mdi6.checkbox-multiple-blank-outline", color=BLEU_FONCE))
        self.btn_tout_decocher.setToolTip("Tout désélectionner")
        for b, etat in ((self.btn_tout_cocher, True), (self.btn_tout_decocher, False)):
            b.setFixedSize(34, 34)
            b.setIconSize(QSize(20, 20))
            b.setStyleSheet("padding: 0px;")
            b.clicked.connect(lambda _c=False, e=etat: self._cocher_tout(e))
            entete.addWidget(b)
        self.btn_config = QPushButton(" Notebooks…")
        self.btn_config.setObjectName("discret")
        self.btn_config.setIcon(qta.icon("mdi6.cog-outline", color=BLEU_FONCE))
        self.btn_config.clicked.connect(ouvrir_config)
        entete.addWidget(self.btn_config)
        droite.addLayout(entete)

        self.zone = QScrollArea()
        self.zone.setWidgetResizable(True)
        self.zone.setFrameShape(QFrame.NoFrame)
        self.zone.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.conteneur = QWidget()
        self.vbox = QVBoxLayout(self.conteneur)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(8)
        self.vbox.addStretch(1)
        self.zone.setWidget(self.conteneur)
        droite.addWidget(self.zone, 1)

        pied = QHBoxLayout()
        self.message = QLabel()
        self.message.setObjectName("doux")
        pied.addWidget(self.message, 1)
        self.btn_journal = QPushButton(" Journal")
        self.btn_journal.setObjectName("discret")
        self.btn_journal.setIcon(qta.icon("mdi6.text-box-outline", color=BLEU_FONCE))
        self.btn_journal.setCheckable(True)
        self.btn_journal.toggled.connect(self._basculer_journal)
        pied.addWidget(self.btn_journal)
        self.btn_demarrer = QPushButton(" Démarrer la sélection")
        self.btn_demarrer.setIcon(qta.icon("mdi6.play", color="white"))
        self.btn_demarrer.clicked.connect(self._demarrer_selection)
        pied.addWidget(self.btn_demarrer)
        self.btn_arreter = QPushButton(" Arrêter la sélection")
        self.btn_arreter.setIcon(qta.icon("mdi6.stop", color="white"))
        self.btn_arreter.clicked.connect(self._arreter_selection)
        pied.addWidget(self.btn_arreter)
        droite.addLayout(pied)

        self.panneau_journal = QTabWidget()
        self.panneau_journal.setFixedHeight(190)
        self.txt_bot, self.txt_app = QPlainTextEdit(), QPlainTextEdit()
        for t in (self.txt_bot, self.txt_app):
            t.setReadOnly(True)
            t.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.panneau_journal.addTab(self.txt_bot, "Bot")
        self.panneau_journal.addTab(self.txt_app, "App")
        self.panneau_journal.setVisible(False)
        droite.addWidget(self.panneau_journal)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.tick()

    # ---- journal ----
    def _log(self, msg):
        ligne = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
        self.journal_app.append(ligne)
        journal_ecrire(ligne)
        if self.btn_journal.isChecked():
            self._afficher(self.txt_app, "\n".join(self.journal_app))

    @staticmethod
    def _afficher(zone, texte):
        zone.setPlainText(texte)
        zone.verticalScrollBar().setValue(zone.verticalScrollBar().maximum())

    def _basculer_journal(self, visible):
        self.panneau_journal.setVisible(visible)
        if visible:
            self.cache_bot = None
            self._afficher(self.txt_app, "\n".join(self.journal_app))
            self._maj_journal_bot()

    def _maj_journal_bot(self):
        if not self.btn_journal.isChecked():
            return
        info = self.bots.get(self.bot_affiche) if self.bot_affiche else None
        texte = "\n".join(info.get("logs") or []) if info and isinstance(info.get("logs"), list) else ""
        if texte != self.cache_bot:
            self.cache_bot = texte
            self._afficher(self.txt_bot, texte or "(aucune ligne publiée par ce bot)")

    # ---- actions ----
    def _en_file(self, bot, nom):
        return nom in self.file.get(bot, ())

    def _demarrer_selection(self):
        """Met les notebooks cochés dans la file (ordre de la liste). Un seul démarrage à la fois : voir _pomper."""
        bot = self.bot_affiche
        noms = [n for n, l in self.lignes.items() if l.coche_demarrer() and not self._en_file(bot, n)]
        if not bot or not noms:
            return
        self.file.setdefault(bot, deque()).extend(noms)
        for n in noms:
            self.dernier.pop((bot, n), None)
            self.lignes[n].coche.setChecked(False)
        self._log(f"file de démarrage de {bot} : + {noms} (file : {list(self.file[bot])})")
        self.message.setText(f"{len(noms)} notebook(s) : ouverture + démarrage des sessions, puis Run au fur et à mesure")
        self._pomper(bot)
        self._rafraichir_lignes()

    def _pomper(self, bot):
        """Envoie la file en UN lot, SEULEMENT si aucun lot n'est en cours pour ce bot (un seul onglet manipulé à la fois).
        Rappelé à chaque tick : dès l'accusé du lot précédent, les notebooks arrivés entre-temps partent en un nouveau lot."""
        file = self.file.get(bot)
        info = self.bots.get(bot)
        if not file or not info or not info.get("vivant"):
            return
        if any(k[0] == bot and v["type"] == "demarrer" for k, v in self.attente.items()):
            return
        noms = list(file)    # TOUTE la file part en un seul lot : ouverture + Start de chacun, puis Run progressif côté bot
        file.clear()
        try:
            oid = self.pont.demarrer(bot, noms)
        except OSError as e:
            self.message.setText(f"Envoi impossible : {e}")
            self._log(f"ERREUR envoi démarrer {noms} à {bot} : {e}")
            file.extend(noms)    # on réessaiera au prochain tick
            return
        self._log(f"→ {bot} : démarrer le lot {noms} (ordre {oid})")
        t0 = time.time()
        for nom in noms:
            self.attente[(bot, nom)] = {"id": oid, "t0": t0, "type": "demarrer"}
            self.dernier.pop((bot, nom), None)

    def _arreter_selection(self):
        """Arrête les notebooks cochés. Ceux encore en file sont simplement retirés de la file (aucun ordre au bot) ;
        les autres (y compris celui en cours de démarrage : son démarrage est annulé côté bot) partent dans UN ordre d'arrêt."""
        bot = self.bot_affiche
        noms = [n for n, l in self.lignes.items() if l.coche_arreter()]
        if not bot or not noms:
            return
        en_file = [n for n in noms if self._en_file(bot, n)]
        for n in en_file:
            self.file[bot].remove(n)
            self.lignes[n].coche.setChecked(False)
        if en_file:
            self._log(f"{bot} : retiré de la file de démarrage : {en_file}")
        noms = [n for n in noms if n not in en_file]
        if not noms:
            self.message.setText("Retiré de la file")
            self._rafraichir_lignes()
            return
        try:
            oid = self.pont.arreter(bot, noms)
        except OSError as e:
            self.message.setText(f"Envoi impossible : {e}")
            self._log(f"ERREUR envoi arrêter {noms} à {bot} : {e}")
            return
        self._log(f"→ {bot} : arrêter {noms} (ordre {oid})")
        t0 = time.time()
        for n in noms:
            prec = self.attente.get((bot, n))
            if prec and prec["type"] == "demarrer":    # démarrage pas encore accusé : on le garde en suivi (le bot l'annule puis accuse),
                self.attente[(bot, "demarrage:" + n)] = prec    # sinon la file enverrait le suivant avant la fin de cette annulation
            self.attente[(bot, n)] = {"id": oid, "t0": t0, "type": "arreter"}
            self.dernier.pop((bot, n), None)
        self._rafraichir_lignes()

    def _reveiller_bot(self, bid):
        """Bouton de la carte d'un bot : ordre de réveil pour TOUS les notebooks en cours de ce bot (pas de confirmation)."""
        info = self.bots.get(bid)
        if not info or not info.get("vivant"):
            self.message.setText("Bot hors ligne : réveil impossible")
            return
        noms = sorted(n for n, v in info["notebooks"].items() if isinstance(v, dict) and v.get("statut") == "en_cours")
        if not noms:
            self.message.setText("Aucun notebook en cours à réveiller")
            return
        try:
            oid = self.pont.reveiller(bid, noms)
        except OSError as e:
            self.message.setText(f"Envoi impossible : {e}")
            self._log(f"ERREUR envoi réveil à {bid} : {e}")
            return
        self._log(f"→ {bid} : réveiller {noms} (ordre {oid})")
        self.message.setText(f"Réveil demandé à {bid} ({len(noms)} notebook(s))…")

    # ---- rafraîchissement ----
    def tick(self):
        self.bots = self.pont.scan()
        self._traiter_accuses()
        self._maj_liste_bots()
        for bot in list(self.file):
            self._pomper(bot)    # un démarrage vient d'être accusé : on envoie le suivant
        self._maj_panneau()

    def _traiter_accuses(self):
        for bot, chemin, a in self.pont.accuses():
            oid = str(a.get("id"))
            if a.get("ordre") == "reveiller":    # réveil : résumé par notebook, sans suivi de ligne
                res = a.get("resultats") if isinstance(a.get("resultats"), dict) else {}
                ko = {n: str((v or {}).get("erreur") or "") for n, v in res.items() if not (isinstance(v, dict) and v.get("ok"))}
                self._log(f"← {bot} : réveil {len(res) - len(ko)}/{len(res)} OK" + "".join(f" ; {n} : {e}" for n, e in ko.items())
                          + (f" ; {a.get('erreur')}" if not res and a.get("erreur") else ""))
                self.message.setText(f"Réveil : {len(res) - len(ko)}/{len(res)} OK" + (f" — {'; '.join(f'{n}: {e}' for n, e in ko.items())[:160]}" if ko else "")
                                     + (f" — {a.get('erreur')}" if not res and a.get("erreur") else ""))
                self.pont.done(chemin)
                continue
            touches = [(k, v) for k, v in self.attente.items() if k[0] == bot and v["id"] == oid]
            self._log(f"← {bot} : accusé {a.get('ordre')} {'OK' if a.get('ok') else 'ECHEC : ' + str(a.get('erreur') or '')}"
                      f" (bot : {a.get('duree_s')} s" + (f", app : {time.time() - touches[0][1]['t0']:.1f} s" if touches else ", ordre inconnu de l'app") + ")")
            for k, v in touches:
                duree = time.time() - v["t0"]
                nom_k = k[1][len("demarrage:"):] if k[1].startswith("demarrage:") else k[1]
                cle = (k[0], nom_k)
                verbe = "Démarré" if v["type"] == "demarrer" else "Arrêté"
                res_nb = (a.get("resultats") or {}).get(nom_k) if isinstance(a.get("resultats"), dict) else None
                if isinstance(res_nb, dict):    # lot : résultat propre à ce notebook
                    if res_nb.get("ok"):
                        self.dernier[cle] = f"{verbe} en {duree:.1f} s"
                    elif "annul" in str(res_nb.get("erreur") or ""):
                        self.dernier[cle] = "Démarrage annulé"
                    else:
                        self.dernier[cle] = f"echec : {str(res_nb.get('erreur') or '')[:120]}"
                elif a.get("ok"):
                    self.dernier[cle] = f"{verbe} en {duree:.1f} s"
                elif "annul" in str(a.get("erreur") or ""):
                    self.dernier[cle] = "Démarrage annulé"
                else:
                    self.dernier[cle] = f"echec : {str(a.get('erreur') or '')[:120]}"
                del self.attente[k]
            if touches:
                self.message.setText(f"{touches[0][1]['type'] == 'demarrer' and 'Démarrage' or 'Arrêt'} terminé"
                                     + ("" if a.get("ok") else " avec une erreur"))
            self.pont.done(chemin)

    def _effacer_hors_ligne(self):
        ids = [b for b, i in self.bots.items() if not i.get("vivant")]
        for bid in ids:
            self.pont.effacer(bid)
            self.file.pop(bid, None)
            for k in [k for k in self.attente if k[0] == bid]:
                del self.attente[k]
            self._log(f"{bid} : effacé de la liste (hors ligne)")
        if ids:
            self.message.setText(f"{len(ids)} bot(s) hors ligne effacé(s)")
        self.tick()

    def _maj_liste_bots(self):
        for bid in list(self.items):
            if bid not in self.bots:
                self._log(f"{bid} : disparu du pont (arrêté ou oublié après {BOT_OUBLI_S:.0f} s)")
                self.vivant_prec.pop(bid, None)
                if self.file.pop(bid, None):
                    self._log(f"{bid} : file de démarrage vidée (bot disparu)")
                item, _carte = self.items.pop(bid)
                self.liste.takeItem(self.liste.row(item))
        for bid in sorted(self.bots):
            vivant = bool(self.bots[bid].get("vivant"))
            if self.vivant_prec.get(bid) != vivant:
                self._log(f"{bid} : " + ("en ligne" if vivant else f"hors ligne ({self.bots[bid]['age']:.0f} s sans signe de vie)")
                          + (f" - compte {self.bots[bid].get('compte')}" if vivant and bid not in self.vivant_prec else ""))
                self.vivant_prec[bid] = vivant
            if bid not in self.items:
                item = QListWidgetItem()
                carte = BotCarte(bid, self._reveiller_bot)
                item.setData(Qt.UserRole, bid)
                item.setSizeHint(QSize(240, 56))
                self.liste.addItem(item)
                self.liste.setItemWidget(item, carte)
                self.items[bid] = (item, carte)
            self.items[bid][1].maj(self.bots[bid])
        self.btn_effacer.setEnabled(any(not i.get("vivant") for i in self.bots.values()))
        if self.bot_affiche not in self.bots:
            self.bot_affiche = None
            if self.items:
                self.liste.setCurrentItem(self.items[sorted(self.items)[0]][0])
        elif self.liste.currentItem() is None or self.liste.currentItem().data(Qt.UserRole) != self.bot_affiche:
            self.liste.setCurrentItem(self.items[self.bot_affiche][0])    # la sélection suit toujours le bot affiché

    def _bot_choisi(self, item, _prev):
        self.bot_affiche = item.data(Qt.UserRole) if item else None
        self.cache_bot = None
        self._reconstruire_lignes()
        self._maj_panneau()

    def _reconstruire_lignes(self):
        for l in self.lignes.values():
            l.setParent(None)
            l.deleteLater()
        self.lignes = {}

    def _creer_tray(self):
        """Icône dans la zone de notification : un clic réduit la fenêtre si elle est visible, la rouvre sinon."""
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        self.tray.setToolTip("SautoniaxManager")
        menu = QMenu()
        a_ouvrir = QAction("Afficher / réduire", menu); a_ouvrir.triggered.connect(self._basculer)
        a_quit = QAction("Quitter", menu); a_quit.triggered.connect(QApplication.quit)
        menu.addAction(a_ouvrir); menu.addAction(a_quit)
        self._menu_tray = menu
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda r: self._basculer() if r in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick) else None)
        self.tray.show()

    def _basculer(self):
        if self.isMinimized() or not self.isVisible():
            self.setWindowState((self.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
            self.show(); self.raise_(); self.activateWindow()
        else:
            self.showMinimized()

    def _maj_panneau(self):
        bot = self.bot_affiche
        if not bot or bot not in self.bots:
            self.titre.setText("Aucun bot connecté")
            self.sous_titre.setText(f"Pont lu : {self.pont.base}")
            self._reconstruire_lignes()
            self.btn_demarrer.setEnabled(False)
            self.btn_arreter.setEnabled(False)
            self.btn_tout_cocher.setEnabled(False)
            self.btn_tout_decocher.setEnabled(False)
            return
        info = self.bots[bot]
        self.titre.setText(str(info.get("compte") or info.get("profil") or bot))
        self.sous_titre.setText(f"{bot} · " + ("en ligne" if info["vivant"] else f"hors ligne ({info['age']:.0f} s sans signe de vie)"))
        noms = notebooks_du_bot(bot, info)
        if list(self.lignes) != noms:
            self._reconstruire_lignes()
            for n in noms:
                l = LigneNotebook(n, self._maj_boutons)
                self.lignes[n] = l
                self.vbox.insertWidget(self.vbox.count() - 1, l)
        self._rafraichir_lignes()
        self._maj_journal_bot()

    def _rafraichir_lignes(self):
        bot = self.bot_affiche
        if not bot or bot not in self.bots:
            return
        info = self.bots[bot]
        for n, l in self.lignes.items():
            etat = info["notebooks"].get(n) if isinstance(info["notebooks"].get(n), dict) else {}
            statut = etat.get("statut") or "inconnu"
            if self._en_file(bot, n):
                statut = "file"
            detail = self.dernier.get((bot, n)) or etat.get("detail") or ""
            att = self.attente.get((bot, n))
            l.maj(statut, detail, info["vivant"], att["type"] if att else None)
        if not self.lignes:
            self.message.setText(f"Aucun notebook : ajoutez-les avec « Notebooks… » ({CONFIG_FILE}).")
        self._maj_boutons()

    def _cocher_tout(self, etat):
        """Coche (ou décoche) toutes les cases du bot affiché ; seules les cases actives peuvent être cochées."""
        for l in self.lignes.values():
            if not etat or l.coche.isEnabled():
                l.coche.setChecked(etat)

    def _maj_boutons(self):
        self.btn_demarrer.setEnabled(any(l.coche_demarrer() for l in self.lignes.values()))
        self.btn_arreter.setEnabled(any(l.coche_arreter() for l in self.lignes.values()))
        actif = any(l.coche.isEnabled() for l in self.lignes.values())
        self.btn_tout_cocher.setEnabled(actif)
        self.btn_tout_decocher.setEnabled(actif)


def main():
    if sys.platform == "win32":      # identifiant d'application propre : sans lui, Windows groupe la fenêtre sous « Python » (icône Python)
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SautoniaxManager.App")
        except Exception:
            pass
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    app.setWindowIcon(qta.icon("mdi6.monitor-dashboard", color=BLEU))      # icône de la barre des tâches
    fen = Fenetre()
    fen._log(f"App démarrée - pont lu : {fen.pont.base}")
    fen.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

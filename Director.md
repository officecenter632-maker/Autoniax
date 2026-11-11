# Procédure de création des assets de l'animation

## Sommaire

**Partie A – Règles générales** : [Principe](#principe) · [Nombres](#nombres) · [Erreurs de méthode](#erreurs-de-methode)

**Partie B – Vue d'ensemble** : [Vue d'ensemble](#vue-d-ensemble)

**Partie C – Les étapes**


*Phase 1 – Choisir et documenter le sujet (étapes 0 et 0 bis)*

- [Étape 0 : choisir le sujet de la vidéo (analyse des données de scraping Reddit)](#e0)
- [Étape 0 bis : collecter et consulter tous les détails du sujet choisi](#e0bis)

*Phase 2 – Speech et scénario (étape 0 ter)*

- [Étape 0 ter : rédiger le speech et le plan d'animation à partir des données brutes](#e0ter)
  - [0 ter.1 · Ce que je te fournis : le dépôt `CreativeData`, plus rien à rejoindre à la main](#e0ter-1)
  - [0 ter.2 · Modèle de `envoyer_creative_data.py` : à recopier, pas à réécrire](#e0ter-2)
  - [0 ter.3 · Livraison progressive et reprise dans une autre session (règle de toute l'étape 0 ter)](#e0ter-3)
  - [0 ter.4 · Lire le JSON sans le lire en entier](#e0ter-4)
  - [0 ter.5 · Copier la créativité du JSON, ne rien inventer (règle de toute l'étape 0 ter)](#e0ter-5)
  - [0 ter.6 · Les couleurs : un code pour chaque élément (règle de toute l'étape 0 ter)](#e0ter-6)
  - [0 ter.7 · Principe : le speech doit refléter l'avis majoritaire des utilisateurs](#e0ter-7)
  - [0 ter.8 · Le style du speech : exactement celui des speechs de référence](#e0ter-8)
  - [0 ter.9 · La méthode (trois temps, dans cet ordre)](#e0ter-9)
  - [0 ter.10 · Ce que tu me livres (au final, dans l'ordre des phases ci-dessus)](#e0ter-10)
  - [0 ter.11 · Ce que tu contrôles avant de livrer](#e0ter-11)
  - [0 ter.12 · Suite](#e0ter-12)

*Phase 3 – Assets de base (étapes 1 à 6)*

- [Étape 1 : lister et classer les assets](#e1)
- [Étape 2 : chercher les images de référence dans Lexiax (une seule passe)](#e2)
- [Étape 3 : choisir la meilleure référence](#e3)
- [Étape 4 : construire l'archive des assets](#e4)
- [Étape 5 : rassembler les images générées dans un seul dossier](#e5)
- [Étape 6 : envoyer les images générées sur GitHub et les vérifier](#e6)

*Phase 4 – Storyboard (étapes 7 et 8)*

- [Étape 7 : organiser le storyboard et générer les plans](#e7)
- [Étape 8 : le fichier projet pour ImGen (génération automatique des plans)](#e8)

*Phase 5 – Assets d'animation (étapes 9 à 12)*

- [Étape 9 : analyser les plans et préparer la génération des assets d'animation](#e9)
  - [9.1 · Dépôt dédié : `Storyboard`](#e9-1)
  - [9.2 · Ce que je fais : te donner l'arborescence du projet](#e9-2)
  - [9.3 · Ce que tu fais : le script `envoyer_storyboard.py`](#e9-3)
  - [9.4 · Modèle de `envoyer_storyboard.py` (projet `6-musk_starlink`) : à recopier, pas à réécrire](#e9-4)
  - [9.5 · Ce que tu fais : cloner et contrôler le storyboard](#e9-5)
  - [9.6 · Réinitialiser les images à regénérer : le fichier `reinitialisation_imgen.html`](#e9-6)
  - [9.7 · Porte avant l'analyse : la mise à jour du dépôt `Storyboard` est-elle faite ?](#e9-7)
  - [9.8 · Défauts de détail : tu les corriges dans les prompts, je ne regénère rien](#e9-8)
  - [9.9 · Passe d'inventaire : décider l'ajustement technique de chaque asset, AVANT tout prompt](#e9-9)
  - [9.10 · Ce que tu fais : visualiser chaque plan, un par un](#e9-10)
  - [9.11 · Règles de découpage en générations](#e9-11)
  - [9.12 · Règles du fond détourable](#e9-12)
  - [9.13 · Ce que tu me livres : l'archive de prompts](#e9-13)
  - [9.14 · Livraison progressive (pour ne pas perdre le travail)](#e9-14)
  - [9.15 · Ce que tu me livres : `Liste_assets_animation.md`](#e9-15)
  - [9.16 · Ce que tu contrôles par programme avant chaque livraison](#e9-16)
  - [9.17 · Validation](#e9-17)
- [Étape 10 : le dossier `AssetAnimation` et le projet ImGen des assets d'animation](#e10)
- [Étape 11 : re-vérifier les assets d'animation générés](#e11)
- [Étape 12 : vectoriser les assets d'animation](#e12)

*Phase 6 – Archive, audio et animation (étapes 13, 13 bis et 14)*

- [Étape 13 : l'archive de données pour l'animation](#e13)
- [Étape 13 bis : générer l'audio de la voix off (AudioGen)](#e13bis)
- [Étape 14 : réaliser l'animation de chaque plan (rendu web, directement ici)](#e14)
  - [14.1 · Les tâches dans IngXAi : comment elles sont rangées](#e14-1)
  - [14.2 · Le travail à faire, en résumé](#e14-2)
  - [14.3 · Ce que je te fournis](#e14-3)
  - [14.4 · Le détourage et le moteur commun](#e14-4)
  - [14.5 · Avant le premier plan : tu apprends le scénario](#e14-5)
  - [14.6 · Un fichier média est intégré à la page ; un élément créé de zéro est dessiné en JavaScript](#e14-6)
  - [14.7 · L'audio du plan, intégré dans la page](#e14-7)
  - [14.7 bis · La durée du plan = la durée de la voix](#e14-7bis)
  - [14.8 · Contrat de la page : la structure imposée (pour que l'export en vidéo marche sans retouche)](#e14-8)
  - [14.9 · Plan qui continue le précédent : tu exiges le plan précédent](#e14-9)
  - [14.10 · Le format que j'attends (à respecter à chaque livraison)](#e14-10)
  - [14.11 · Vérifier avant de livrer](#e14-11)
  - [14.12 · Le registre des exigences : ne jamais refaire une erreur, ne jamais oublier une demande](#e14-12)
  - [14.13 · Ménager mes crédits (règle de toute l'étape 14)](#e14-13)
  - [14.14 · Ce que contient la page d'un plan](#e14-14)
  - [14.15 · Comment on avance : un plan à la fois](#e14-15)
  - [14.16 · Fin de l'étape](#e14-16)

*Phase 7 – Publication (étape 15)*

- [Étape 15 : exporter les animations et préparer les métadonnées de la vidéo](#e15)
  - [15.1 · Ce que je te fournis](#e15-1)
  - [15.2 · Première partie : identifier les pages HTML générées](#e15-2)
  - [15.3 · Deuxième partie : le script `envoyer_export.py`](#e15-3)
  - [15.4 · Troisième partie : le kit de publication `Metadonnees_video.html`](#e15-4)
  - [15.5 · Ce que tu fais, dans l'ordre](#e15-5)

**Partie D – Contrôle final** : [Contrôle final](#controle-final)

**Annexes – Modèles de scripts et de fichiers** : [A1](#annexe-a1) · [A2](#annexe-a2) · [A3](#annexe-a3) · [A4](#annexe-a4) · [A5](#annexe-a5) · [A6](#annexe-a6) · [A7](#annexe-a7) · [A8](#annexe-a8) · [A9](#annexe-a9) · [A10](#annexe-a10)

---

# Partie A – Règles générales

<a id="principe"></a>

## Principe

L'animation est faite d'**assets** : décors, personnages, objets, icônes. On ne les dessine pas de zéro. Pour chaque asset :

1. on trouve dans la bibliothèque d'images de **Lexiax** une image de **référence** proche (même sujet, même forme, même composition) ;
2. une IA générative **transforme** cette référence en l'asset exact voulu.

Pour économiser les fichiers à générer, on distingue deux sortes d'assets :

- **Les éléments clés** (grands, importants, récurrents) : chacun a **sa propre génération**, avec sa propre image de référence et son propre prompt.
- **Les petits éléments** (un panier, une petite icône, un objet qui n'occupe pas beaucoup d'espace) : on les **regroupe dans une même génération**. Une seule image est générée avec plusieurs éléments dedans, mais on fournit **une image de référence par élément**, pour que chaque élément garde sa propre inspiration et que la créativité ne soit pas diluée.

Cette procédure prépare tout ce dont l'IA générative a besoin : des images de référence et des prompts, organisés par génération. Une fois les images générées, elle se termine par la **collecte** de toutes les images finales dans un seul dossier, avec des noms sans ambiguïté (étape 5).

**Règle d'or : la collecte se fait en UNE SEULE PASSE.** Lexiax est lancé **une seule fois** pour **tous** les assets (éléments clés et petits éléments). Le résultat est **un seul zip** qui contient déjà toutes les images candidates, rangées par asset puis par mot. Le tri (étape 3) se fait ensuite dans ce zip, sans retourner dans Lexiax. On ne relance jamais Lexiax asset par asset.

**Règle absolue : aucun travail manuel pour moi.** Tu fais **tout** toi-même et tu **automatises** tout ce qui peut l'être. Je ne copie, ne déplace, ne renomme et ne range **aucun fichier** à la main ; je ne crée aucun dossier ; je ne remplis aucun champ ; je ne lance **jamais** un outil auxiliaire. Quand une étape a besoin d'un fichier (documentation du logiciel, liste, manifeste, archive…), **c'est le script qui le produit ou le trouve**. Mon seul geste autorisé : **lancer le script** que tu m'as livré depuis mon éditeur, et te dire que c'est fait. Si tu ne vois aucun moyen d'éviter un geste manuel, tu me le dis **avant** de me le demander, en une phrase, avec la raison. Avant chaque livraison, tu te demandes : « est-ce que je lui demande de faire quelque chose à la main ? » ; si oui, tu corriges ton script ou ta méthode, **tu ne me renvoies pas le travail**.

**Règle absolue pour TOUS les envois sur Git : le script fait tout.** Chaque envoi (références Lexiax, `assetsBrute1.zip`, `Storyboard.zip`, assets d'animation, `AnimationData.zip`, `CreativeData.zip`, `Director.md` et le registre des exigences (dépôt `Autoniax`), et tout nouvel envoi après une correction) est fait **par le script que tu m'as écrit**, du début à la fin : il **sélectionne** les fichiers, **contrôle** la structure, **crée le zip**, puis **le pousse lui-même** sur GitHub avec la méthode du modèle `envoyer_storyboard.py` (dépôt neuf, un seul commit, push forcé, vérification de la branche distante, jeton jamais affiché) et **affiche le résultat et le lien direct**. Cette méthode d'envoi est **recopiée telle quelle dans chaque script** ; tu ne la réécris pas. **Je ne glisse aucun zip dans Lexiax, je ne clique sur aucun bouton « Push sur GitHub », je ne tape aucune commande `git`, je ne crée aucun dépôt ni dossier à la main.** Si un dépôt n'existe pas encore, c'est le script qui s'en charge quand c'est possible ; si ce n'est pas possible (identifiants), tu me le dis **avant** de livrer le script, en une phrase, et tu m'indiques la seule chose nécessaire. Après un échec ou une correction, je **relance le même script** : il repousse tout seul. Je te dis seulement que c'est fait.

**Qui fait quoi**

| Acteur | Rôle |
| --- | --- |
| Moi | **Pour choisir le sujet de la vidéo, je te donne mes données de scraping Reddit (fichiers `.json` et `.csv`, ou leur archive) et rien d'autre (étape 0).** Ensuite, je lance Lexiax **une fois**, j'exécute **un** script sur mon ordinateur, qui crée le zip **et l'envoie lui-même sur GitHub** (aucun clic), et je te signale que c'est fait. Plus tard, une fois les images générées et rangées dans chaque dossier, je t'envoie l'**arborescence réelle** de mon dossier `Assets` (chemin complet inclus) et je lance le script de collecte depuis mon éditeur. Ce script de collecte **pousse lui-même `assetsBrute1.zip` sur GitHub** ; je te signale que c'est fait. Quand le Storyboard est livré et que je veux générer les plans avec ImGen, je t'envoie l'**arborescence réelle** de `Storyboard` et de `Assets` (chemin complet inclus), et le **lien du dépôt GitHub** qui contient le zip des assets (étape 8). Quand les N plans sont générés, je t'envoie l'**arborescence réelle** du projet actuel (chemin complet inclus) ; tu m'écris un script `envoyer_storyboard.py` qui sélectionne seulement le storyboard (les plans), le zippe en `Storyboard.zip` et le pousse dans le dépôt `Storyboard` (distinct de `ImageReferenceData`) ; je le lance depuis mon éditeur et je te le signale (étape 9). Quand les images d'assets d'animation sont générées avec ImGen, je t'envoie l'**arborescence réelle** du dossier qui les contient (chemin complet inclus), je lance le script d'envoi depuis mon éditeur et je te le signale (étape 11). Quand tous les assets d'animation sont vectorisés (étape 12), je te donne l'**arborescence réelle** du projet (chemin complet inclus) et mes décisions sur les points à trancher, je lance le script d'envoi depuis mon éditeur et je te le signale (étape 13). Avant d'animer, je te donne l'**arborescence réelle** du projet et mes décisions de langue et de voix ; je lance le script `ecraser_speeches.py` depuis mon éditeur, puis je colle `projet_audiogen.json` dans AudioGen, qui génère la voix off de chaque plan (étape 13 bis) ; **je relance ensuite `envoyer_animation.py` pour que l'audio de chaque plan parte dans `AnimationData.zip`**. Ensuite l'animation se fait **directement en web, dans la conversation** : tu me montres chaque plan en page web, je le regarde et je te dis « ça marche » ou ce qui est faux (étape 14). |
| Toi (l'IA) | **Tu analyses mes données de scraping, sans me poser de question, et tu me proposes le sujet de la vidéo (étape 0).** Ensuite, tu listes et classes les assets **et tu m'envoies cette liste dans un fichier `Liste_assets.md`**, tu choisis les mots **pour tous les assets d'un coup**, tu écris **un seul** script, tu **télécharges le zip depuis GitHub et tu vérifies qu'il correspond à la recherche**, tu tries les images, tu écris les prompts, tu construis l'archive **par lots, en me livrant chaque lot au fur et à mesure** (le lot 1 avec l'outil `copier_assets.pyw`), puis, à partir de mon arborescence, tu m'écris le **script Python de collecte** des images générées, avec les chemins réels de mon arborescence. Enfin tu **télécharges `assetsBrute1.zip` au lien de l'étape 6 et tu contrôles les images générées**. Ensuite tu découpes le scénario en séquences, tu crées le dossier `Storyboard` et tu rédiges le prompt de chaque plan (étape 7). Enfin, à partir de mes arborescences et du lien du dépôt, tu écris le **fichier projet JSON d'ImGen** (`projet_imgen.json`) avec les noms de fichiers, les chemins, les images de référence et les liens GitHub réels, tous vérifiés (étape 8). Enfin, à partir de mon arborescence, tu écris le **script d'envoi** `envoyer_storyboard.py` ; puis, `Storyboard.zip` poussé, tu le télécharges, tu **parcours les N plans pour décider l'ajustement technique de chaque asset** et tu me livres le **registre** (`Registre_elements_animation.md`) ; tu le livres puis tu **enchaînes aussitôt, sans attendre ma validation**, en visualisant **chaque plan, un par un**, tu anticipes ce qui est dynamique ou statique, et tu livres, par lots, l'**archive de prompts** (`animation_lot_NN.zip` : un dossier par plan, un JSON par nouvelle génération seulement, avec l'image du plan source en référence sur GitHub) et la **liste détaillée** (`Liste_assets_animation.md`) (étape 9). Quand le contrôle du storyboard trouve des images à regénérer, tu me livres directement, dans la même réponse, **`reinitialisation_imgen.html`** : une page avec une zone de copie (et un bouton « Copier ») par vague de JSON de réinitialisation pour ImGen (étape 9). Enfin, à partir de cette arborescence, tu m'écris le **script d'envoi** vers le dépôt `Assets_Animation`, puis tu télécharges le zip et tu fais le **checkup** des images pour repérer celles qui ont une génération grave (étape 11). Enfin, tu m'écris le **script d'envoi** `envoyer_animation.py` qui pousse `AnimationData.zip` (SVG, directives, storyboard, scénario, `README.md`) dans le dépôt `ShaderiaxAnim` ; tu le télécharges et tu contrôles qu'il contient tout ce qu'il faut pour animer chaque plan (étape 13). Avant l'animation, tu **clones le dépôt `Storyboard`**, tu **traduis en anglais et tu balises les `speech.txt`** (un speech par plan), puis tu me livres `Speech_audio.zip`, le script `ecraser_speeches.py` et `projet_audiogen.json` pour AudioGen (étape 13 bis) ; une fois l'audio généré, tu contrôles qu'il est dans `AnimationData.zip` (`audio/`). **Dans l'animation, tu intègres l'audio de chaque plan directement dans son HTML (étape 14), et chaque page respecte le contrat de structure (scène `#stage`, barre de lecture, horloge pilotée par `requestAnimationFrame`, une seule balise `<audio>`) pour que l'export en vidéo marche sans retouche.** Enfin tu **animes chaque plan directement en web** et tu me montres le rendu dans la conversation, une page par plan, que tu as regardée toi-même avant de me la livrer (étape 14). |
| Lexiax | Il contient la bibliothèque d'images de référence, fabrique le zip d'images ; **l'envoi sur GitHub est fait par le script**, jamais par le bouton « Push sur GitHub » ni par glisser-déposer. |

<a id="nombres"></a>

## Nombres : rien n'est fixé d'avance

**Aucun nombre de plans, de séquences ou d'audios n'est fixé dans ce document.** Les chiffres d'un projet précédent (64 plans, 51 séquences, 63 audios) ont été remplacés par des **lettres** :

- **N** : le nombre de plans de **cette** vidéo ;
- **S** : le nombre de séquences ;
- **P** : le nombre de plans parlés (ceux qui ont une voix off ; les autres, par exemple l'écran de fin, n'ont pas d'audio).

**Ces nombres découlent du speech** : on découpe le speech en idées (étape 0 ter), et **le nombre d'idées, avec leur durée, donne le nombre de plans N**. Ils sont **calculés par script** depuis `Plan_animation.md`, jamais écrits à la main ni repris d'un autre projet. Les tableaux et les exemples qui citent des numéros précis (`Plan58 à Plan64`, `6-musk_starlink`…) sont des **exemples tirés d'un projet précédent** : le vrai découpage suit **ton** `Plan_animation.md`.

---

<a id="erreurs-de-methode"></a>

## Erreurs de méthode à ne jamais refaire

Cette zone liste **les erreurs de méthode** (dépôts, fichiers, communication), distinctes des erreurs d'animation, qui sont dans `Registre_exigences_animation.md`, partie A. **Tu la relis avant chaque étape qui touche un dépôt ou un fichier.** Une erreur de méthode qui revient ne crée pas une nouvelle ligne : on ajoute une ★ et on complète « Signalée ». Chaque nouvelle erreur de méthode que je te signale est ajoutée ici par toi, **dans la même réponse**, une ligne par sujet.

| Priorité | Erreur vue | Règle + contrôle avant de répondre | Signalée |
| --- | --- | --- | --- |
| ★★★ | Un dépôt répond 404 ; tu conclus qu'il n'existe pas, puis tu prends un autre dépôt (l'ancien) qui n'a pas les bons fichiers | **Un 404 ne prouve rien** : le dépôt peut être privé ou porter un autre nom. Avant de conclure, tu testes les trois accès : `git ls-remote`, la page du dépôt et le lien direct du zip, et tu cites les codes obtenus. Si les trois échouent, tu t'arrêtes et tu me demandes **le lien exact, en une phrase**. **Tu ne remplaces jamais un dépôt par un autre** (même « l'ancien ») et tu n'avances pas sur un substitut sans me le dire **avant** d'agir. **Le dépôt de l'archive d'animation est `ShaderiaxAnim`** (`https://github.com/officecenter632-maker/ShaderiaxAnim`, `AnimationData.zip` à la racine) : si un nom de dépôt de ce document échoue, tu me demandes le bon lien tout de suite | Étape 14 ×3 |
| ★★ | Tu avances avec des données incomplètes sans t'en rendre compte (les `.webp` de `Assets_Animation` au lieu des SVG) | À la première ouverture d'un dépôt ou d'un zip, tu vérifies qu'il contient **le type de fichier attendu** (pour l'animation : les `.svg` de chaque plan, le `manifest.json`, `directives/`). S'il manque, c'est probablement le mauvais dépôt : tu le dis et tu demandes le lien, tu ne contournes pas | Étape 14 ×1 |
| ★ | Tu me poses une question en laissant entendre que le problème vient de moi (« ouvre la page dans ton navigateur ») alors que tu n'as pas épuisé tes propres essais | Avant de me demander quoi que ce soit, tu as épuisé tes propres moyens (les trois accès ci-dessus). Ensuite : **une phrase, la cause réelle, la seule chose demandée** | Étape 14 ×1 |

---

# Partie B – Vue d'ensemble

<a id="vue-d-ensemble"></a>

## Vue d'ensemble

| Étape | Qui | Résultat |
| --- | --- | --- |
| 0. Choisir le sujet de la vidéo | Moi + toi | Je te donne mes données de scraping Reddit ; tu les dédoublonnes, tu **regroupes les publications par sujet**, tu mesures l'intérêt de chaque thème, tu filtres selon le format « The Infographics Show » et tu me livres **un tableau classé, les 5 ou 6 meilleurs sujets avec leur accroche, les sujets à éviter et ton choix final** ; une fois mon choix fait, tu écris **`Sujet_choisi.md`** |
| 0 bis. Collecter et consulter tous les détails du sujet choisi | Moi + toi | Je te redonne **l'archive de collecte de l'étape 0** ; tu en tires les publications de référence du sujet choisi et tu me livres **la liste des liens Reddit à scraper** (un lien par ligne, prête à coller) ; **je crée un projet de scraping dans `Marketing_manager.pyw`**, je colle les liens, je lance la collecte et je te rends les résultats ; tu **lis tout** (publications, textes, commentaires) et tu me livres **`Dossier_sujet.md`** : les faits chiffrés avec leur source, la chronologie, les acteurs, les arguments, les contradictions tranchées et ce qui manque. **C'est la matière de la vidéo** |
| 0 ter. Rédiger le speech et le plan d'animation à partir des données brutes | Moi + toi | **Tu clones toi-même le dépôt `CreativeData`** (archive de collecte, `json_maitre.json` et `mots_reference.json`, envoyés par le script `envoyer_creative_data.py` que tu m'écris) ; **tu écris toi-même le speech, en anglais, dans le style des speechs du JSON**, en le faisant **soutenir les avis majoritaires des commentaires** (sans jamais les citer), puis tu en tires **`Plan_animation.md`**, le scénario d'animation **dont toute la créativité (visuels, mouvements, transitions, couleurs, logique d'enchaînement) est copiée des recettes et des règles du JSON, avec la traçabilité plan par plan (annexe E), sans rien inventer**. **Plus aucun speech n'est fourni de l'extérieur.** **Livraison par phases (avis → structure → speech → plan idée par idée) dans un seul fichier, `Plan_animation.md`, livré en entier à chaque fois ; pour reprendre dans une autre session, je ne te redonne que ce fichier : le reste est dans le dépôt `CreativeData`** |
| 1. Lister et classer les assets | Toi | Un fichier **`Liste_assets.md`** que tu m'envoies : une liste sans doublon, avec les éléments clés d'un côté et les petits éléments (déjà répartis en planches) de l'autre |
| 2. Chercher les références dans Lexiax (une seule passe) | Toi + moi | **Un seul zip** d'images candidates, rangé par asset puis par mot, envoyé sur GitHub |
| 2 bis. Vérifier le zip reçu | Toi | Un contrôle de structure : le zip correspond exactement à la recherche (assets, mots, images) |
| 3. Choisir la meilleure référence | Toi | Une image validée par asset, choisie dans ce zip, **par lots** |
| 4. Construire l'archive | Toi | Des archives `assets_lot_NN.zip` (un dossier par génération, avec ses références et son prompt), **livrées lot par lot** ; leur somme forme `assets.zip`. Le lot 1 contient aussi l'outil **`copier_assets.pyw`** (grille « label + Copier », bouton « Move » pour ranger les images générées) |
| 5. Rassembler les images générées | Moi + toi | Je génère les images (avec `copier_assets.pyw`) et t'envoie l'arborescence réelle de `Assets` ; tu me donnes **un script Python** (chemins réels, à lancer depuis un éditeur, à placer dans `Assets`) qui **copie** toutes les images finales dans un seul dossier `assetsBrute1`, renommées sans ambiguïté, écrit un `index.csv` avec les chemins des copies, et les range dans un zip du même nom, `assetsBrute1.zip` ; **le même script pousse ensuite `assetsBrute1.zip` sur GitHub** (dépôt `ImageReferenceData`), sans aucun geste de ma part |
| 6. Envoyer et vérifier les images générées | Moi + toi | `assetsBrute1.zip` a **déjà été poussé sur GitHub par le script de l'étape 5** (je n'ai rien à glisser ni à cliquer) ; tu le télécharges au lien indiqué et tu fais un **checkup** : les images générées correspondent à la liste et à leurs prompts |
| 7. Storyboard : générer les plans | Toi + moi | Les N plans numérotés de 1 à N (numérotation continue), rangés par **séquence** dans un dossier `Storyboard`, chacun avec son prompt (`PlanN.txt`) et son image, générés **plan par plan**. C'est un storyboard : il sert seulement à **se faire une idée** de ce qui se passe, sans validation ni vérification |
| 8. Projet ImGen : générer les plans par bots | Moi + toi | Un fichier **`projet_imgen.json`** : N images (une par plan), avec nom, chemin de sauvegarde réel, prompt et images de référence (assets pris dans le zip du dépôt GitHub, plan précédent en local), ordonnées par vagues de dépendance. Je le colle dans ImGen (bouton « + ») |
| 9. Analyser les plans et préparer la génération des assets d'animation | Moi + toi | Je te donne l'arborescence réelle du projet ; tu m'écris un script qui sélectionne le storyboard, le zippe en `Storyboard.zip` et le pousse dans le dépôt dédié **`Storyboard`** ; tu le télécharges, tu **parcours d'abord les N plans pour décider l'ajustement technique de chaque asset** (tel quel, séparé pour le calque, décomposé, animation en code, feuille de sprites, nouvelle configuration ; livrable : `Registre_elements_animation.md`, que je valide), puis tu analyses chaque plan (dynamique ou statique) et tu livres, par lots, **`animation_lot_NN.zip`** (un dossier par plan, un JSON **par nouvelle génération seulement** : fond vide, asset ou groupe d'assets, avec son prompt et l'image du plan en référence ; ce qui revient d'un autre plan n'est jamais régénéré) et **`Liste_assets_animation.md`** (fiche de chaque plan : ce qui se passe, fond, assets, chronologie, montage) |
| 10. Dossier `AssetAnimation` et projet ImGen des assets d'animation | Moi + toi | Je te donne les `animation_lot_NN.zip` ; tu les assembles en **`AssetAnimation.zip`** (un dossier `PlanN` par plan, avec les JSON de génération, les fiches de code et les fichiers `_reutilise.txt` / `_rien_a_generer.txt`) ; je le décompresse et te donne le **chemin réel** ; tu m'écris **`projet_imgen_assets.json`**, le projet ImGen qui génère toutes les images d'assets d'animation, chacune enregistrée dans le dossier de son plan |
| 11. Re-vérification des assets d'animation générés | Moi + toi | Je te donne l'arborescence réelle du dossier qui contient toutes les images d'assets d'animation générées ; tu m'écris un script qui les archive et les pousse dans le dépôt **`Assets_Animation`** ; tu télécharges le zip et tu fais un **checkup** : quelles images ont une **génération grave** (à regénérer) |
| 12. Vectoriser les assets d'animation | Moi + toi | Une fois les assets d'animation validés (étape 11), on les **vectorise avec `GenSVG.pyw`**. Je te donne l'**arborescence réelle** du dossier `AssetAnimation` (tu me la demandes si tu ne l'as pas) ; tu m'écris **`projet_gensvg.json`**, le projet GenSVG : une ligne par image d'asset, avec son image source (**dans le dépôt `Assets_Animation`**, jamais en local) et le chemin du `.svg` à produire (sur mon PC, à côté de l'image) |
| 13. Archive de données pour l'animation | Moi + toi | Je te donne l'**arborescence réelle** du projet et mes décisions sur les points à trancher ; tu m'écris **`envoyer_animation.py`**, qui rassemble en **un seul zip, `AnimationData.zip`**, les SVG de chaque plan, les fiches de code, les directives (fiches par plan, registre, séquences, scénario), les images du storyboard, un `README.md` et un **`manifest.json`** qui liste chaque fichier, puis le pousse dans le dépôt dédié **`ShaderiaxAnim`** ; tu le télécharges et tu contrôles qu'il est complet. **L'archive contient aussi l'audio généré de chaque plan (`audio/`, P fichiers) : je relance donc `envoyer_animation.py` une fois l'étape 13 bis terminée.** Le montage est hors périmètre. **Tu m'écris aussi `envoyer_autoniax.py`** (voir « Le dépôt `Autoniax` » à l'étape 14), qui pousse `Director.md` et `Registre_exigences_animation.md` dans le dépôt `Autoniax`, d'où les agents d'IngXAi les clonent. Aucun code d'animation n'est écrit à cette étape |
| 13 bis. Générer l'audio de la voix off (AudioGen) | Moi + toi | Je te donne l'**arborescence réelle** du projet et mes décisions (langue, voix) ; tu **clones le dépôt `Storyboard`**, tu **récupères les `speech.txt`**, tu **traduis chaque plan en anglais** et tu y **intègres les balises d'émotion**, en suivant les **règles de balisage écrites dans ce document** (étape 13 bis) ; **pas de page HTML** : tu me livres **`Speech_audio.zip`** (les S `speech.txt` modifiés), **`ecraser_speeches.py`** (il écrase les `speech.txt` de mon ordinateur, après sauvegarde des originaux) et **`projet_audiogen.json`** (une ligne par plan parlé, soit P) ; je colle le JSON dans AudioGen, qui génère les audios. **Cette étape se fait AVANT l'animation** ; une fois les P audios générés, **je relance `envoyer_animation.py` : l'audio de chaque plan part dans `AnimationData.zip`** |
| 14. Réaliser l'animation de chaque plan | Moi + toi | **Directement en web, sans aucun logiciel externe.** Tu lis le scénario, puis, **plan par plan**, tu écris une **page web animée** (`planN.html`) : objets, **détourage**, caméra, chronologie, éléments en code. Tu la **regardes toi-même** (images clés comparées au storyboard), tu la publies et tu me donnes le lien ; je regarde et je te dis « ça marche » ou l'erreur ; tu corriges la même page. **Les plans sont rangés comme des tâches dans IngXAi** (`projet_animation.json` : dépendances entre plans, mise en attente des plans dont le précédent n'est pas terminé, désactivation par plan), qui les attribue à des agents ; **le prompt de chaque tâche ne contient que le numéro du plan et l'ordre de cloner le dépôt `Autoniax` (le Director et le registre des exigences) : l'agent y lit seulement l'étape 14 du Director et le registre** ; chaque agent livre `planN.html` en fichier joint, que je définis comme résultat. **Chaque page respecte le contrat de structure** (scène `#stage`, barre de lecture `#seek`, bouton `#play`, horloge pilotée par `requestAnimationFrame`, une seule balise `<audio>`) pour que l'export en vidéo (notebook Kaggle) marche **sans retouche**. **La page d'un plan parlé dure exactement le temps de sa voix (durée de l'audio), sans silence final** ; les durées du scénario ne sont que des approximations. **Aucun travail manuel pour moi** |
| 15. Préparer la publication YouTube (et, si demandé, exporter les animations) | Moi + toi | **Deux livraisons indépendantes, tu ne fais que celle que je demande.** **(A) Kit de publication** : `Metadonnees_video.html`, courte, avec 3 titres candidats, la description prête à coller, les chapitres horodatés, les tags et la miniature (3 variantes selon le pattern de la chaîne, JSON ImGen) ; livrée en deux temps (textes d'abord, miniature ensuite). **(B) Export**, seulement si je le demande : je te donne l'arborescence réelle ; tu identifies les pages `.html` (`Animation/`) et tu m'écris `envoyer_export.py`, qui les zippe (parties de 85 Mo au plus) et les pousse dans le dépôt **`Export`** (un seul commit) ; tu télécharges le dépôt et tu contrôles qu'il est complet |

---

# Partie C – Les étapes

> **Phase 1 – Choisir et documenter le sujet (étapes 0 et 0 bis)**

<a id="e0"></a>

## Étape 0 : choisir le sujet de la vidéo (analyse des données de scraping Reddit)

Cette étape vient **avant tout le reste** : tant que le sujet n'est pas choisi, il n'y a ni speech, ni scénario, ni asset. Elle porte le numéro « 0 » (comme « 2 bis » ou « 13 bis ») pour ne rien renuméroter dans ce document. Le but : trouver, dans mes données de scraping Reddit, **le sujet de la prochaine vidéo de la chaîne IngeniaX**, au format **« The Infographics Show »** : une vidéo explicative de **10 à 12 minutes**, illustrée par des infographies animées (chiffres, schémas, cartes, comparaisons).

<a id="e0-1"></a>

### 0.1 · Ce que je te fournis

Mes **données de scraping Reddit** : des fichiers `.json` et `.csv`, **un jeu par compte (ou clone)**, éventuellement dans une archive. **Rien d'autre.** Tu ne me demandes ni explication, ni consigne, ni décision : tu appliques la méthode ci-dessous et tu me donnes **directement le résultat**. Si les données sont absentes ou illisibles, tu me le dis en **une phrase** (la cause réelle, la seule chose que tu me demandes), après avoir épuisé tes propres moyens.

<a id="e0-2"></a>

### 0.2 · La méthode (quatre temps, dans cet ordre)

1. **Lecture des données**
   - Tu extrais l'archive si besoin (pour un RAR : `unrar-cffi`, en lisant chaque fichier avec `infolist` / `read`, **pas** `extractall`).
   - Tu charges tous les `.json` (clé `posts` : `id`, titre, score, commentaires, subreddit, source, url).
   - Tu **dédoublonnes par `id`** en gardant le **score maximum**. Tu donnes **en une ligne** le nombre de publications uniques et le taux de redondance entre clones, sans t'y attarder.
2. **Regroupement par thème (le point clé)**
   - Tu ne te contentes pas de lister les plus gros scores : tu regroupes les publications **par sujet** (même événement ou même idée, même si les titres et les subreddits diffèrent).
   - Tu utilises des **mots-clés avec limites de mots** (`\b`) pour éviter les faux positifs (par exemple « uber » dans « YouTuber »), et **une publication n'est comptée que dans un seul thème**.
   - À la fin, tu **vérifies les publications importantes restées sans thème** pour voir s'il manque un thème.
3. **Mesure de l'intérêt**
   - Pour chaque thème : nombre de publications, nombre de **subreddits différents**, **points cumulés**, **commentaires cumulés**, score maximum.
   - Un thème repris par **plusieurs publications et plusieurs subreddits** signale un **intérêt réel**. Les points cumulés donnent **un ordre de grandeur** (les crossposts comptent double), **jamais un nombre de personnes**.
4. **Filtre « format Infographics Show »**
   - **Tu gardes** : les sujets **explicables**, avec de la **matière chiffrable ou visualisable**, pas trop de niche, **valables encore dans quelques semaines**.
   - **Tu écartes** : les actualités politiques ponctuelles, les vidéos virales sans explication, l'humour, les mèmes, les questions personnelles (AskReddit sans angle).
   - **Tu signales** les sujets qui **vieillissent vite** (guerre, actualité chaude) par rapport à ceux qui restent valables.

<a id="e0-3"></a>

### 0.3 · Ce que tu me livres (court)

- **Un tableau classé** : thème | publications | subreddits | points | commentaires.
- **Pour les 5 ou 6 meilleurs** : une **accroche en une phrase** et **ce qu'on peut illustrer en infographie**.
- **Une section « À éviter »** (courte).
- **Ton choix final**, si je ne devais en prendre qu'un, **avec la raison**.
- **Pas de diagnostic technique du scraping**, sauf si je le demande.
- **Tu restes dans ce qui est dans les données** : si tu ne sais pas, tu le dis au lieu de deviner. **Réponse en français.**

<a id="e0-4"></a>

### 0.4 · Après mon choix : `Sujet_choisi.md`

Dès que j'ai choisi (ton choix final ou un autre thème du tableau), tu me livres **un fichier `Sujet_choisi.md`, court**, pour qu'une nouvelle session reparte sans tout relire : le **thème choisi**, son **accroche**, ce qu'on peut **illustrer en infographie**, la **durée visée (10 à 12 minutes)**, les **publications de référence** (titre, subreddit, score, `id`), si le sujet est **durable ou vieillit vite**, et les **thèmes écartés avec la raison en une phrase**. **Rien qui ne soit dans les données** : un fait ajouté de ta mémoire est signalé comme tel.

<a id="e0-5"></a>

### 0.5 · Ce que tu contrôles avant de livrer

- Le dédoublonnage par `id` est fait (score maximum gardé) et le nombre de publications uniques est donné.
- **Chaque publication est dans un seul thème** ; les mots-clés ont des limites de mots ; les publications importantes sans thème ont été vérifiées.
- Les chiffres du tableau viennent **tous** des données ; les points cumulés ne sont **jamais** présentés comme un nombre de personnes.
- Les sujets qui **vieillissent vite** sont signalés, et aucun sujet « à éviter » n'est dans les 5 ou 6 meilleurs.

<a id="e0-6"></a>

### 0.6 · Suite

Une fois `Sujet_choisi.md` livré, on passe à l'**étape 0 bis** : collecter et consulter tous les détails du sujet choisi, avant le speech et le scénario.

---

<a id="e0bis"></a>

## Étape 0 bis : collecter et consulter tous les détails du sujet choisi

Cette étape vient **juste après `Sujet_choisi.md`** et **avant le speech et le scénario**. L'étape 0 a servi à **choisir** le sujet à partir de titres, de scores et de nombres de commentaires : c'est trop mince pour construire une vidéo de 10 à 12 minutes. Ici, on va chercher **tous les détails** du sujet validé, et tu les **consultes en entier** avant d'écrire quoi que ce soit.

<a id="e0bis-1"></a>

### 0 bis.1 · Ce que tu fais, dans l'ordre

1. **Tu as besoin de l'archive de collecte de l'étape 0** (le zip des données de scraping Reddit). Si elle n'est plus dans la session, tu me la redemandes en **une phrase**, sans rien d'autre. Dans ces données, tu retrouves les publications de référence de `Sujet_choisi.md` à partir de leur `id`, et tu construis chaque lien avec le champ **`permalink`** : `https://www.reddit.com` + `permalink`.
2. **Tu me donnes la liste des liens à scraper**, dans **un bloc de code prêt à coller** : **un lien Reddit par ligne**, classés par score décroissant, sans doublon d'`id`. Règles :
   - **Uniquement des liens Reddit** : `Marketing_manager.pyw` refuse tout autre lien. Les articles cités par les publications (Guardian, Wired, etc.) **n'entrent pas dans la liste** : **le script de scraping les ouvre lui-même** et enregistre leur texte (`Publications/…_article.json`) et leur page (`Pages_HTML/…_article.html`) à côté de chaque publication. Certains peuvent échouer (page 404, erreur du proxy) : tu le signales, tu ne devines pas leur contenu.
   - Tu **gardes les crossposts** (même article publié dans deux subreddits) : ce sont deux publications différentes, avec des commentaires différents.
   - Tu **écartes** les publications d'un autre thème qui contiennent seulement un mot du sujet (par exemple, pour les data centers, les publications sur les bots russes et les data centers de Yandex).
   - Tu ajoutes sous le bloc **le nombre de liens** et, en une phrase, ce qui a été écarté et pourquoi.
   Ensuite **c'est moi qui crée le projet** : dans `Marketing_manager.pyw`, je crée un projet de scraping, je colle ta liste, je lance la collecte, puis je te donne les résultats : **le zip créé par le bouton « Copier archive scrapping »** (un dossier par lancement, avec `Commentaires/`, `Pages_HTML/` et `Publications/`, seulement pour les liens déjà scrapés, complets ou partiels). Tu ne me demandes pas comment faire.
3. **Tu lis tout.** Chaque publication collectée, son texte, **ses commentaires** (au minimum les mieux notés et ceux qui apportent un chiffre, une source ou une objection) et chaque article lié. Tu ne survoles pas : si une partie est illisible ou vide, tu le dis en une phrase.
4. **Tu recoupes.** Un même chiffre ou un même événement revient souvent sous des formulations différentes (par exemple « 10 États », « 40 initiatives », « tous sauf un » dans les titres de l'étape 0). Tu **tranches avec la source la plus solide** et tu notes l'écart ; si tu ne peux pas trancher, tu gardes les deux et tu le signales.

<a id="e0bis-2"></a>

### 0 bis.2 · Ce que tu me livres : `Dossier_sujet.md`

Un seul fichier, structuré, qui sert de **base unique** au speech et au scénario :
- **Les faits chiffrés**, un par ligne : le chiffre, ce qu'il mesure, la **source** (`id` de la publication ou lien) et son niveau de confiance (établi / à vérifier).
- **La chronologie** des événements.
- **Les acteurs** (entreprises, lieux, élus, groupes) et leur rôle.
- **Les arguments** de chaque camp, tels qu'ils ressortent des commentaires.
- **Les contradictions** rencontrées et la façon dont elles ont été tranchées.
- **Ce qui manque** pour illustrer ou expliquer le sujet (y compris les articles liés dont la collecte a échoué ou qui n'ont pas été collectés), à compléter si je le demande.
- **Ce qui vient de ta mémoire**, séparé et signalé comme tel. **Rien d'autre que ce qui est dans les données** n'est présenté comme un fait établi.

<a id="e0bis-3"></a>

### 0 bis.3 · Ce que tu contrôles avant de livrer

- La liste de liens est **entièrement en liens Reddit**, construite depuis les `permalink` de l'archive de l'étape 0, sans doublon d'`id`, avec les crossposts gardés.
- **Tous** les liens de la liste ont été lus dans les résultats (ou leur échec est signalé).
- Chaque chiffre du dossier a une **source** ; aucun chiffre n'est inventé ni arrondi sans le dire.
- Les contradictions entre titres, commentaires et articles sont **listées**, pas écrasées.
- Les faits venant de ta mémoire sont **séparés** et signalés.
- Le dossier est **assez complet pour tenir 10 à 12 minutes** ; sinon tu me dis ce qu'il faut collecter en plus.

<a id="e0bis-4"></a>

### 0 bis.4 · Suite

`Dossier_sujet.md` est la matière du **speech**, puis du **scénario** (`Plan_animation.md`). La rédaction est décrite à l'**étape 0 ter**, juste en dessous.

---

> **Phase 2 – Speech et scénario (étape 0 ter)**

<a id="e0ter"></a>

## Étape 0 ter : rédiger le speech et le plan d'animation à partir des données brutes

Cette étape vient **juste après l'étape 0 bis** et **avant l'étape 1**. **Plus aucun speech n'est fourni de l'extérieur** : c'est **toi** qui l'écris, à partir des **données brutes de l'archive de scraping**, puis tu en tires le **plan d'animation**. Les étapes suivantes (assets, storyboard, animation) partent de `Plan_animation.md` : c'est donc le fichier de cette étape qui les alimente.

> **État de rédaction.** Cette étape décrit **le principe, les entrées, les sorties et les règles déjà décidées**. **Les consignes détaillées de rédaction du speech sont données par moi, à part** ; tant qu'une consigne manque, tu **me la demandes en une phrase** au lieu de l'inventer. Le JSON créatif est **en cours de mise à jour** (mes idées ont changé) : **en cas de contradiction entre ce document et la rubrique `mode_emploi_scenario` du JSON, ce document prime** jusqu'à la mise à jour du JSON. **Une exception : la règle de créativité ci-dessous (« Copier la créativité du JSON, ne rien inventer ») s'ajoute à `mode_emploi_scenario` et ne l'affaiblit jamais** : citer l'`id` de chaque choix visuel, ne jamais inventer d'`id`, signaler ce que le registre ne couvre pas.

<a id="e0ter-1"></a>

### 0 ter.1 · Ce que je te fournis : le dépôt `CreativeData`, plus rien à rejoindre à la main

**Je ne te redonne plus ni l'archive de scraping ni les JSON à chaque conversation.** Ils sont dans le dépôt GitHub **`https://github.com/officecenter632-maker/CreativeData`**, dans **un seul zip, `CreativeData.zip`** (un seul commit, remplacé à chaque envoi). Il contient, sous un dossier racine `CreativeData/` :

- **`scraping/`** : l'**archive de collecte** du projet en cours (étape 0 bis) : publications, **commentaires**, textes des articles liés. **C'est la seule matière du speech.**
- **`json_maitre.json`** : le registre des règles, recettes et codes de sens de couleur tirés des vidéos de référence, avec les **speechs de référence** (rubrique `corpus_idees`) qui donnent **le style, la forme et le rythme**.
- **`mots_reference.json`** : le fichier des mots de référence de la bibliothèque Lexiax.
- **`manifest.json`** : la liste des fichiers avec tailles et empreintes (`sha256`), la date de création et le **nom de l'archive de scraping d'origine**.

**Au début de l'étape 0 ter (ou dès que l'archive ou un JSON a changé), tu m'écris le script `envoyer_creative_data.py`**, tu me dis de le lancer, et j'attends « c'est fait ». Les deux JSON ont un **chemin fixe** (écrit en dur dans le script, voir le modèle ci-dessous) ; **seul le chemin de l'archive de scraping change d'un projet à l'autre** : **tu me le demandes en une phrase** si je ne te l'ai pas donné, et tu l'écris dans la constante `ARCHIVE_SCRAPING`. Je ne rassemble, ne zippe ni ne pousse rien à la main.

**Ce que tu fais ensuite, par programme :**

1. Tu **clones** le dépôt (`git clone --depth 1 https://github.com/officecenter632-maker/CreativeData.git`), tu dézippes `CreativeData.zip` et tu **gardes la copie** dans ton espace de travail.
2. Tu **vérifies** : le zip s'ouvre ; `manifest.json` existe et **les empreintes correspondent** ; `json_maitre.json` contient les rubriques `regles`, `recettes`, `codes_de_sens`, `corpus_idees` ; `scraping/` contient des `Publications` et des `Commentaires`.
3. Tu **notes dans la section Suivi** de `Plan_animation.md` : le **nom de l'archive de scraping d'origine** et la **date du manifest**. À la reprise, tu **compares** ces deux valeurs au manifest du dépôt : **si l'archive a changé, c'est un autre projet ou une mise à jour, et tu me le dis en une phrase avant de continuer**.
4. Si le dépôt est **inaccessible** (privé, 404, vide), tu ne conclus pas qu'il n'existe pas : tu me dis la **cause réelle** en une phrase et la **seule chose demandée** (par exemple « donne-moi l'accès au dépôt `CreativeData` »). Pour une nouvelle conversation, **seul le dernier `Plan_animation.md`** est à me redonner.

<a id="e0ter-2"></a>

### 0 ter.2 · Modèle de `envoyer_creative_data.py` : à recopier, pas à réécrire

Seule la constante `ARCHIVE_SCRAPING` change d'un projet à l'autre. Le reste (chemins fixes des deux JSON, méthode d'envoi : dépôt neuf, un seul commit, push forcé, vérification de la branche, jeton masqué) est **recopié tel quel**, comme pour `envoyer_storyboard.py`.

> **Modèle : voir [Annexe A1](#annexe-a1) (en fin de document).**

Lien de téléchargement direct : `https://github.com/officecenter632-maker/CreativeData/raw/main/CreativeData.zip`. Page du dépôt (branche `main`) : `https://github.com/officecenter632-maker/CreativeData`.

<a id="e0ter-3"></a>

### 0 ter.3 · Livraison progressive et reprise dans une autre session (règle de toute l'étape 0 ter)

Le plan d'animation est **long à produire** : on ne le fait **jamais d'un bloc**. On travaille **du global au détail**, on **livre le fichier après chaque idée**, et **un seul fichier porte tout** : **`Plan_animation.md` contient lui-même la structure, le speech, le suivi et le plan**. Pour reprendre dans une autre session, **je ne te redonne que le dernier `Plan_animation.md`** : l'**archive de scraping** et les **JSON créatifs** sont dans le dépôt **`CreativeData`** (voir « Ce que je te fournis »), que tu clones toi-même. Aucun autre fichier de travail n'est à conserver.

**Démarrer ou continuer : toujours avec un `Plan_animation.md`.** À l'étape 0 ter, **je te fournis toujours un `Plan_animation.md`**, même au tout début : c'est le **fichier de départ** (modèle ci-dessous) ou le **dernier fichier livré**. Quand je dis « **continue à l'étape 0 ter** » avec `Director.md` et ce fichier, **tu sais où reprendre sans rien me demander** :

1. Tu lis la **section Suivi**. Si elle dit **« Phase en cours : A. État : NON COMMENCÉ »**, **rien n'a été fait** : tu pars de la **phase A**. Sinon, tu reprends à la **phase et à la première idée « à faire »** indiquées.
2. Tu **clones `CreativeData`** et tu **compares** le nom de l'archive de scraping et la date du manifest à ceux de la section Suivi. **S'ils diffèrent**, tu me le dis en **une phrase** avant de continuer : c'est un autre projet ou une mise à jour.
3. **Si je ne te donne aucun `Plan_animation.md`**, tu **ne démarres pas dans le vide** : tu **me poses d'abord la question de la durée** (voir ci-dessous), puis tu **crées le fichier de départ** (modèle ci-dessous) avec le sujet, la **durée cible** et la source des entrées, tu me le livres, et tu commences la phase A. **Un `Plan_animation.md` d'un projet précédent** (le sujet ou l'archive ne correspondent pas à ceux du dépôt) **n'est jamais repris** : tu me le dis en une phrase.

**La durée de la vidéo : tu me la demandes avant de créer le fichier de départ.** **Aucune durée n'est supposée.** Tu me poses **une seule question** (avec `AskUserQuestion` si disponible, sinon en une phrase) : « **Quelle durée visée pour la vidéo ?** », avec **trois ou quatre choix** (par exemple 5 à 7 minutes, 8 à 10 minutes, 10 à 12 minutes, plus de 12 minutes) et ma réponse libre possible ; **tu proposes en premier le format habituel de la chaîne** (10 à 12 minutes), marqué « recommandé ». **Tu ne crées pas le fichier de départ sans ma réponse.** La durée est écrite dans la **section Suivi** (« **Durée cible de la vidéo** ») et reprise dans la structure ; **le nombre d'idées, le nombre de mots du speech et les durées des parties s'en déduisent** (d'après `corpus_idees.reperes`). **Si je te donne un `Plan_animation.md` sans durée cible**, tu me poses la question avant de continuer. **Si je change la durée en cours de route**, tu mets à jour la section Suivi et la structure, tu me dis ce que ça change (nombre d'idées et de plans) **avant** de continuer.

**Modèle du fichier de départ** (les valeurs entre chevrons sont remplies avec le sujet, **la durée cible que j'ai choisie**, le nom de l'archive d'origine et la date du `manifest.json` ; **la structure du fichier ne change pas**) :

> **Modèle : voir [Annexe A2](#annexe-a2) (en fin de document).**

**Les phases, dans l'ordre. Tu ne passes à la suivante qu'après mon accord, sauf pour les idées de la phase D, qui s'enchaînent. À chaque phase, tu livres `Plan_animation.md` entier.**

| Phase | Ce que `Plan_animation.md` contient à la fin de la phase | Je valide |
| --- | --- | --- |
| **A. Les avis** | Le tableau court des avis majoritaires (dans la réponse, et recopié dans la section « Structure globale »). | L'angle de la vidéo. |
| **B. La structure globale** | Le titre, la section **Suivi**, la section **Structure globale** (contenu ci-dessous) et la **charte provisoire**. Aucun speech, aucun plan. | L'ordre des parties, les idées, la charte. |
| **C. Le speech** | Chaque idée de la structure reçoit son **texte exact en anglais** (le speech est bien moins coûteux que le plan). Toujours aucun plan. | Le texte, mot pour mot, **avant** tout plan. |
| **D. Le plan, idée par idée** | Les parties traitées ont leur **tableau de plans** ; les autres gardent leur **texte et la mention `(à faire)`**. Livré **après chaque idée**. | Je peux corriger en chemin ; sans retour de ma part, tu continues. |
| **E. La clôture** | Plan **complet**, annexes A à G, **résultat du script de contrôle**, section **Suivi** retirée (voir plus bas). | Le plan entier, avant l'étape 1. |

**La forme du fichier en cours de travail.** Dans l'ordre :

1. `# Scénario – <sujet>` et la date.
2. **`## Suivi (à lire en premier)`** : la **mémoire du travail** (contenu plus bas). **Cette section est réservée au travail en cours ; elle est retirée à la phase E.**
3. **`## Structure globale`** : la **carte de la vidéo** (contenu ci-dessous). **Elle reste dans le fichier final**, en **annexe G**.
4. **`## 0. Charte visuelle et choix de production`**, puis les **parties** `## 1.`, `## 2.`… comme dans le format de l'étape 0 ter. **Une partie pas encore traitée** garde son titre, sa durée visée, sa ligne `Recettes :` prévue, et à la place du tableau la liste de ses idées avec **le texte exact de chacune** et la mention **`(à faire)`**.
5. `## Annexes` (A à F, remplies **au fur et à mesure** pour l'annexe E, **à la clôture** pour les autres).

**Contenu de la section « Structure globale » (phase B).**

1. **Le tableau des avis** (phase A) en quelques lignes, et l'**angle** choisi.
2. **La liste des parties**, dans l'ordre, chacune avec : son titre, son rôle (accroche, contexte, développement, conclusion), sa **durée visée** et sa **teinte dominante** (tirée de `codes_de_sens`, une teinte **différente de la partie précédente**).
3. **La liste des idées de chaque partie**, numérotées dans l'ordre : **numéro, genre, contenu en une phrase, faits avec leur source** (`id` de publication ou lien d'article), **thème d'avis qu'elle sert**, **nombre de mots et durée visés** (d'après `corpus_idees.reperes`), **recette visée** (`id` complet de la recette du même `declencheur_narratif`).
4. **Les totaux**, calculés par script : nombre d'idées, durée totale (**comparée à la durée cible du fichier de départ, à 10 % près ; au-delà, l'écart est justifié et je tranche**), répartition par genre comparée aux repères. **N en découle** : tu ne le fixes pas d'avance.
5. **La charte provisoire** (elle devient la section 0) : palette (tableau `Usage | Couleur | Code`, tiré des codes de sens), **éléments qui reviennent** (personnages et objets fil rouge, avec l'idée où chacun **apparaît pour la première fois** et celles où il **revient**), interdits (aucun logo réel, aucune ressemblance avec une personne réelle).
6. **Les vidéos de référence lues** pour le style, et **les rubriques et règles consultées**.

Une idée peut être **déplacée, coupée ou ajoutée** pendant les phases C et D **seulement si tu mets d'abord à jour la structure** et que tu me le dis. **La structure reste vraie** : elle n'est jamais en retard sur le speech ni sur le plan.

**Phase D : une idée, un plan livré.**

**RÈGLE ABSOLUE DE LA PHASE D : UNE SEULE IDÉE PAR LIVRAISON, JAMAIS PLUSIEURS À LA FOIS.** Tu écris les plans d'**une seule idée**, tu livres `Plan_animation.md` en entier, tu t'arrêtes, et tu **attends mon retour avant l'idée suivante**. « Okay go » ou « continue » à la phase C **ne veut pas dire** « fais toute la phase D d'un coup ». Écrire plusieurs idées, ou les 24, dans la même réponse est **une faute grave** : une erreur de fond serait répétée partout et je ne pourrais rien corriger en chemin. Si tu as la moindre hésitation, tu fais **moins**, jamais plus.

**Niveau de détail exigé pour chaque plan (colonne « Visuel et caméra »).** Une description sans ces éléments est **refusée** :
- **Position et taille de chaque élément** : à gauche, au centre ou à droite, en haut ou en bas, et sa taille en pourcentage de la hauteur de l'image ;
- **Pose et action de chaque personnage** : debout, assis, bras levé, tourné vers qui, ce qu'il tient ;
- **Chronologie à l'intérieur du plan** : dans quel ordre et à quelle seconde chaque élément entre, bouge ou sort ;
- **Cohérence des rythmes avec la durée du plan** : un élément « toutes les 1 à 2 s » ne peut pas répéter 41 fois dans un plan de 6,5 s ; tu calcules, ou tu changes de mise en scène (chute en bloc, accélération) ;
- **Aucun plan réduit à une ou deux phrases** : un plan court est détaillé de la même façon, il a seulement moins d'éléments.

**Contrôle des chiffres.** Le nombre de plans, de secondes et de mots de la section Suivi **et** de la structure globale sont calculés par le **même** script et doivent être identiques ; un écart est expliqué ou corrigé avant la livraison.

**Reprise après un effacement.** Si je te dis d'effacer des plans, tu les retires du fichier, tu remets les idées à « à faire » avec **leur texte exact conservé**, tu me livres le fichier, et tu reprends **à l'idée 1.1 seulement**.

1. **Avant de commencer une idée**, tu lis, **dans `Plan_animation.md`**, la **section Suivi**, **la ligne de l'idée** dans la structure et **son texte exact**, puis **la fin du plan déjà écrit** (l'état final de l'idée précédente). Tu **appliques la procédure « Copier la créativité du JSON, ne rien inventer »**. Tu ne relis **pas** tout le plan ni tout le JSON.
2. **Tu écris les plans de l'idée** : la **voix off est le texte exact de l'idée** (celui de la phase C), la couleur du plan suivant est **écrite dans la transition** (la teinte de la partie suivante est connue par la structure), et **tu ajoutes la ligne de chaque plan à l'annexe E** (traçabilité) **dans la même opération**.
3. **Tu livres tout de suite `Plan_animation.md` cumulatif** (le fichier **entier** dans son état actuel, **pas un extrait**), avec la section Suivi à jour, **avant de passer à l'idée suivante**.
4. **Ta réponse après chaque livraison est courte** : l'idée traitée, les plans produits, ce qui est signalé en annexe F s'il y en a, et « je continue avec l'idée suivante ». **Pas de récapitulatif des étapes.**
5. **Contrôle léger à chaque livraison**, par script : les `id` cités existent, chaque plan de l'idée cite au moins une règle, la voix off est **identique** au texte de l'idée. Le résultat tient en **une ligne**.
6. **Les titres de partie** (durée et nombre de plans) sont **recalculés par script** à chaque livraison, jamais écrits à la main.

**La section « Suivi »** commence par la phrase « **Reprise : lis cette section d'abord** » et contient :

- la **phase en cours** (A, B, C, D ou E) et ce qui est **validé** par moi ;
- le tableau `Idée | Genre | Plans | État (à faire / fait et livré / à corriger) | Remarque`, **une ligne par idée** ;
- **l'état final du dernier plan écrit** : sa teinte, **la couleur annoncée pour le plan suivant**, les **personnages et objets fil rouge déjà introduits** (avec leur premier plan) et leur **dernière apparition** ;
- **les décisions déjà prises** (arbitrages, ce que j'ai tranché, ce que j'ai demandé de corriger) et **les questions ouvertes** ;
- **les règles du JSON déjà utilisées** (leurs `id`) et les passages signalés pour l'annexe F ;
- **les vidéos de référence lues** pour le style ;
- les **nombres calculés** (idées, plans, durée totale à ce stade) ;
- **la source des entrées** : le **nom de l'archive de scraping d'origine** et la **date de création** lus dans `manifest.json` du dépôt `CreativeData`.

**Reprise dans une autre session.** Je te donne **le dernier `Plan_animation.md`**, rien d'autre. Tu **clones `CreativeData`** et tu fais les vérifications (manifest, nom de l'archive comparé à celui de la section Suivi). Tu lis **d'abord la section Suivi**, puis la **ligne de l'idée suivante** et **la fin du plan déjà écrit** ; tu **reprends à la première idée « à faire »**, avec **les mêmes conventions** (numérotation, colonnes, noms, teintes, personnages). **Tu ne recommences jamais une idée déjà livrée** et tu ne relis pas tout le JSON. Si la section Suivi manque ou semble en désaccord avec le plan, tu me le dis en **une phrase** au lieu de deviner.

**À la phase E (clôture).** Tu **retires la section Suivi**, tu **déplaces la structure en annexe G**, tu vérifies qu'**aucune partie ne porte plus la mention `(à faire)`**, et tu lances le **script de contrôle complet**. Le fichier livré pour l'étape 1 est **le format de l'étape 0 ter, sans section de travail** : titre, section 0, parties, annexes A à G.

**Ménager mes crédits.** Tu lis **uniquement ce qu'il faut pour l'idée en cours** (sa ligne, ses recettes et règles par recherche d'`id`, les plans voisins), tu écris par **édition ciblée** du fichier, tu gardes tes **réponses courtes**, et **tu me préviens quand je dois penser à te demander de livrer** si mes crédits risquent de s'arrêter : à tout moment, **le dernier fichier livré est utilisable tel quel**.

<a id="e0ter-4"></a>

### 0 ter.4 · Lire le JSON sans le lire en entier

Le JSON est **volumineux** (environ 930 Ko) : **tu ne l'ouvres jamais en entier**. Tu lis dans cet ordre : `mode_emploi`, `meta`, `corpus_idees.reperes` (durées, nombres de mots, rythme), `sommaire` (une ligne par règle), puis **seulement** les règles et les recettes dont tu as besoin pour l'idée que tu traites, en les cherchant par leur `id`. Tu privilégies les règles de statut « solide » et d'état « actif » ; une règle d'origine `SUJET` est propre à une vidéo et ne se généralise pas.

<a id="e0ter-5"></a>

### 0 ter.5 · Copier la créativité du JSON, ne rien inventer (règle de toute l'étape 0 ter)

**Je ne veux ni visuel inventé, ni logique inventée.** Tout ce qui est **créatif** dans `Plan_animation.md` doit être **copié du JSON** : **inspiré des vidéos de référence, jamais imaginé par toi**. Le JSON est le **catalogue de ce qu'on a le droit de faire**, pas une source d'idées parmi d'autres.

**Ce qui vient du sujet** (les faits, les noms, les chiffres, les lieux, les personnages de l'histoire) **et ce qui vient du JSON** (la forme) :

| Vient du JSON, copié | Vient du sujet, adapté |
| --- | --- |
| la **composition** du plan (décor, cadrage, mouvement de caméra), la **mise en scène** de l'idée, le **type de personnage ou d'objet** utilisé pour illustrer ce genre d'idée | **quels** noms, chiffres, lieux et événements remplissent cette forme |
| le **type de transition** entre deux plans, le **rythme** (durée du plan, délai entre deux apparitions, nombre d'éléments par plan) | le **texte** exact des étiquettes et des cartons |
| la **couleur et son sens** (`codes_de_sens`), la **forme et la place** des étiquettes, cartons, bulles, badges | la **traduction concrète** d'un objet du sujet (par exemple un serveur à la place d'un satellite) **en gardant la même forme visuelle** |
| la **logique d'enchaînement** (par quoi on ouvre, comment on relance, comment on change de partie, comment on conclut) | l'ordre des faits, qui suit le speech |

**Procédure pour chaque idée du speech (aucun raccourci) :**

1. Tu **identifies le genre** de l'idée et son `declencheur_narratif`.
2. Tu **ouvres la recette** du même `declencheur_narratif` et tu lis **tous ses champs** : `situation`, `solution_visuelle`, `pourquoi`, `variantes`. Si plusieurs recettes ont le même déclencheur, tu choisis **celle dont la `situation` correspond le mieux** à l'idée, et tu notes pourquoi.
3. Tu **ouvres chaque règle** citée dans `regles_utilisees` et tu lis **ses champs utiles** : `enonce`, `quoi`, `traitement`, `valeurs`, `limites`, `reutiliser`, `exemples_situation`. Tu **appliques ce qu'elles prescrivent**, valeurs comprises (durées, délais, tailles, couleurs).
4. Tu **cherches ensuite, dans `regles`, toutes les règles de statut « solide » et d'état « actif »** du même `domaine` et du même `declencheur_narratif` (par `domaine`, `declencheur_narratif` et `mots_cles`), et tu **appliques celles qui concernent l'idée** (caméra, transition, couleur, rythme, personnages, texte à l'écran). Tu ne te contentes pas des règles que la recette cite.
5. Pour **l'image concrète** de l'idée, tu pars des **`exemples_situation`** et des **`variantes`** de la règle ou de la recette, **le cas le plus proche de l'idée**, et tu **ne changes que les noms** (ce qui est propre au sujet). **Tu n'imagines pas une mise en scène nouvelle.**
6. Tu **écris le plan** (la ligne du tableau) en y **appliquant** ce que tu as copié, puis tu **notes la traçabilité** (annexe E, voir plus bas).

**Statuts : ce que tu as le droit d'utiliser.**

- **Solide + actif** : tu l'appliques.
- **`cas_particulier` ou `hypothese`** (même actif) : **tu ne l'appliques que si rien de solide ne couvre l'idée, et tu le signales** dans l'annexe F.
- **Archive** (`etat`), **`non_verifiable`** : **tu ne l'utilises pas**.
- **Origine `SUJET`** : elle ne s'applique **qu'à un sujet comparable** ; tu dis pourquoi elle l'est, sinon tu l'écartes.
- **Variations** (`variation_de`, `justification_variation`, `depend_du_formulaire`) : tu lis la justification avant d'utiliser une règle qui en a, pour savoir **dans quel cas** elle vaut.
- **Contradictions** entre deux règles : tu consultes les `alertes` et `limites_des_donnees` du JSON, tu choisis la règle **solide et active**, et tu l'écris dans la section « contradictions du registre ».

**Quand le JSON ne couvre pas un passage.** Tu **ne combles pas avec ta propre idée**. Tu prends le **cas le plus proche** du JSON (autre recette du même genre, ou règle voisine) **et tu le dis** dans l'annexe F ; si rien de proche n'existe, **tu me poses une seule question** au lieu d'improviser. **Ce que tu n'as pas trouvé dans le JSON n'existe pas pour ce plan.**

**Interdits.**

- Imaginer une métaphore, un personnage, un objet, un décor, un mouvement ou un enchaînement qui n'est **ni dans une règle, ni dans une recette, ni dans leurs exemples**.
- Citer un `id` sans avoir **lu** la règle, ou citer un `id` qui n'existe pas dans le JSON.
- Appliquer la recette « en gros » sans ses `valeurs` (durées, délais, tailles, couleurs).
- Reprendre un traitement visuel depuis `corpus_idees` : ce corpus ne sert **qu'au texte** (forme, rythme du speech).
- Remplir l'annexe E après coup **sans** avoir fait les lectures ci-dessus : la traçabilité décrit ce que tu as réellement copié.

<a id="e0ter-6"></a>

### 0 ter.6 · Les couleurs : un code pour chaque élément (règle de toute l'étape 0 ter)

**Dans `Plan_animation.md`, aucune couleur n'est laissée en mots.** Écrire « vert », « gris » ou « fond sombre » sans code est **interdit**. **Chaque élément coloré important** a **son code hexadécimal** à côté de son nom, dans « Visuel et caméra » : le **décor** (fond, murs, sol, ciel), les **personnages** (peau, vêtements, accessoires), les **objets** et **icônes**, les **écrans** (avant et après un changement d'état, par exemple vert `#22B35A` puis gris `#7F9490`), les **cartons, étiquettes, badges, pastilles, tampons**, les **halos, flèches et traînées**, et la **couleur du plan suivant** dans la transition.

- **D'où viennent les codes.** **Du JSON** : `codes_de_sens` (le sens de chaque famille de couleur) et les `valeurs` des règles et recettes citées. Tu **ne choisis pas une couleur de ton goût** : tu prends dans `codes_de_sens` **la famille qui porte le sens de l'idée** (alerte, validé, nuit, officiel…), puis le code de **la règle citée** si elle en donne un. **Si aucun code n'existe dans le JSON pour un élément**, tu prends **le code le plus proche de la même famille**, tu l'écris dans l'**annexe E** (« code pris dans la famille X, non donné par la règle ») et, s'il n'y a rien, tu me poses **une seule question**.
- **Le même élément garde le même code d'un plan à l'autre** (le propriétaire du réseau, la télécommande, le bâtiment fil rouge…). La section 0 contient donc, **en plus de la palette `Usage | Couleur | Code`**, un second tableau **« Couleurs des éléments qui reviennent »** : `Élément | Couleur | Code`, rempli **dès la phase B** (charte provisoire) et **respecté ensuite**.
- **Même décor qu'au plan précédent** : tu **réécris quand même le code** (« même décor, `#66C8F7` »). Aucun plan ne reste sans code.
- **Chaque nouveau décor change de teinte dominante** par rapport au précédent (règle du JSON), et **le code de la teinte du plan suivant est écrit dans la transition**.
- **Les codes sont des intentions.** Les images générées plus tard peuvent s'en écarter un peu ; ce réglage se fait aux étapes suivantes, **pas ici** : le plan écrit **toujours le code voulu**.

<a id="e0ter-7"></a>

### 0 ter.7 · Principe : le speech doit refléter l'avis majoritaire des utilisateurs

Mon but est que **le maximum de spectateurs trouvent le speech engageant**. Pour cela, le speech est **construit en cohérence avec les avis majoritaires des commentaires**, en tenant compte des **commentaires les mieux notés**.

- **Tu ne cites jamais un commentaire**, tu ne le paraphrases pas de près et tu ne nommes aucun utilisateur. Le speech **traduit les avis**, il ne les rapporte pas.
- **Les faits viennent des publications et des articles liés**, avec leur source. **Les commentaires règlent l'angle, le ton, l'ordre et l'importance donnée à chaque sujet : ils ne prouvent rien.** Un chiffre cité dans un commentaire n'entre dans le speech que s'il est confirmé par une publication ou un article de l'archive.
- **Tu ne présentes jamais comme un fait ce qui n'est qu'une opinion.** Le speech peut dire qu'une inquiétude est largement partagée ; il ne la transforme pas en vérité établie.

<a id="e0ter-8"></a>

### 0 ter.8 · Le style du speech : exactement celui des speechs de référence

**Le speech est écrit dans le même style que les speechs des vidéos de référence du JSON.** C'est une exigence, pas une inspiration : un spectateur de la chaîne doit retrouver **la même voix**.

- **Où sont ces speechs.** Dans `corpus_idees.videos` : pour chaque vidéo, ses idées dans l'ordre, avec le **texte dit par le narrateur** et le **genre** de l'idée (accroche, explication, exemple, histoire, transition, conclusion). Les repères chiffrés sont dans `corpus_idees.reperes` (nombre d'idées par vidéo, durées, idées entre deux transitions, **mots et durée par genre**).
- **Tu les lis avant d'écrire la première phrase**, mais **pas tout le corpus** (pour ne pas gaspiller de crédits) : assez de speechs pour en tirer le style, au minimum **l'accroche, plusieurs explications, une histoire, une transition et la conclusion de plusieurs vidéos différentes**. Tu me dis lesquelles tu as lues.
- **Ce que « le même style » veut dire** : le **ton** du narrateur ; la façon de **s'adresser au spectateur** ; la **longueur et la construction des phrases** ; le **rythme** (mots par seconde et mots par idée, selon le genre) ; la façon d'**ouvrir** (accroche), de **relancer**, de **passer d'une idée à l'autre** (transitions) et de **conclure** ; le niveau de langage ; l'usage de questions, d'exemples concrets et de chiffres.
- **Langue.** Les speechs de référence sont dans **leur langue d'origine**, pas forcément en anglais. Tu **imites le ton, la structure, le rythme et les procédés**, tu **ne recopies aucune phrase** et tu ne reprends pas leur vocabulaire. **Ton speech est en anglais.**
- **Les données du scraping ne donnent jamais le style** : elles donnent la matière (faits) et l'angle (avis majoritaires). Le style vient **uniquement** des speechs de référence.
- Si, après lecture, tu ne peux pas déterminer un point de style, tu me poses **une seule question** au lieu de deviner.

<a id="e0ter-9"></a>

### 0 ter.9 · La méthode (trois temps, dans cet ordre)

1. **Lire les données et mesurer l'avis majoritaire**
   - Tu lis les publications, leurs articles liés et les commentaires (au minimum tous les commentaires mieux notés, et ceux qui apportent un chiffre, une source ou une objection).
   - Tu **regroupes les commentaires par thème d'opinion** (même méthode que l'étape 0 : mots-clés avec limites de mots, **un commentaire compté dans un seul thème**, vérification des commentaires importants restés sans thème).
   - Pour chaque thème : **part des commentaires** et **poids par score** (les points cumulés donnent un ordre de grandeur, **jamais un nombre de personnes**). Un seul commentaire ne décide jamais d'un thème : tu comptes les thèmes.
   - Tu repères **les voix contraires** et tu mesures leur poids : elles servent de contrepoint ou de transition dans le speech, elles ne sont pas supprimées.
   - **Tu me livres d'abord un tableau court** : thème | part des commentaires | poids par score | voix contraires. Il justifie l'angle du speech.
2. **Rédiger le speech**
   - **En anglais**, **dans exactement le style des speechs de référence** (voir « Le style du speech » ci-dessus), avec la forme du corpus : accroche, alternance d'explications et d'histoires, transition à intervalles réguliers, conclusion courte. **Ce sont des tendances, pas des lois** : la durée totale reste celle du texte, dans la **durée cible** du fichier de départ.
   - **L'accroche répond à la question ou à la préoccupation la plus partagée**, les parties suivent les préoccupations **dans l'ordre de leur poids**, la conclusion va dans le sens du consensus **sans cacher les faits qui le nuancent**.
   - Chaque fait a sa **source** (`id` de la publication ou lien de l'article). Tu n'inventes **aucun fait**. Si une idée est trop abstraite pour être animée, tu la reformules ou tu cherches sur le web un fait ou un exemple, **noté avec son lien** ; sans accès au web ou sans source fiable, tu n'ajoutes rien.
   - Tu as le droit d'adapter, reformuler, réordonner, couper ou rallonger **sans demander d'accord**, tant que les faits et la langue restent justes.
3. **En tirer le plan d'animation**
   - Tu **découpes ton propre speech en idées** (jamais au milieu d'une phrase), chacune avec son genre : accroche, explication, exemple, histoire, transition, conclusion. **Le nombre de plans résulte de ce découpage** : tu n'ajoutes ni ne retires un plan pour atteindre un chiffre.
   - Pour **chaque idée**, tu suis **à la lettre la procédure « Copier la créativité du JSON, ne rien inventer »** ci-dessus : recette du même `declencheur_narratif` lue en entier, règles citées lues et appliquées avec leurs valeurs, puis règles solides et actives du même domaine, puis image concrète prise dans les `exemples_situation` et les `variantes`. Le **corpus d'idées ne sert jamais à choisir un traitement visuel**, seulement à la forme et au rythme du texte.
   - Le plan doit être **cohérent d'un bout à l'autre** : décors, personnages et objets récurrents (fil rouge), couleurs selon les **codes de sens** du JSON, enchaînement logique d'une idée à l'autre, durées calées sur le texte.
   - Tu écris **`Plan_animation.md`** dans **le format que les étapes suivantes attendent**, celui d'un scénario déjà livré (exemple : `Plan_animation.md` du projet Starlink). **Cet exemple est antérieur à la règle de créativité : il n'a ni annexe E ni annexe F, et il ne cite presque aucun `id` de règle. Il montre le format des colonnes, pas le niveau de traçabilité attendu.** Structure, dans l'ordre :
     1. **Un titre** (`# Scénario – <sujet>`) et la date.
     2. **`## 0. Charte visuelle et choix de production`** : la durée totale et le nombre de plans avec leur durée moyenne ; la **palette** (tableau `Usage | Couleur | Code`, avec les codes hexadécimaux, tirée des **codes de sens** du JSON) **et le tableau « Couleurs des éléments qui reviennent »** (`Élément | Couleur | Code`) ; **les éléments qui reviennent** (logo, étiquettes, cartons, personnages et objets fil rouge, **interdits** : aucun logo réel, aucune ressemblance avec une personne réelle) ; **les contradictions du registre et tes arbitrages** ; **« Ce que j'ai décidé à ta place »**.
     3. **Une section par partie**, titrée `## N. Titre de la partie (durée, nombre de plans)`, avec : une phrase qui dit comment la partie enchaîne ses décors ; une ligne **`Recettes :`** (les recettes du JSON utilisées, avec leur `id` complet, par exemple `recette.accroche_ouverture_enchainement`) ; puis **le tableau des plans**, colonnes exactes : **`Plan | Voix off | Visuel et caméra | Texte à l'écran | Transition et durée`**. Les plans sont numérotés **`1.1`, `1.2`…** (numéro de la partie, point, numéro du plan dans la partie). **La voix off est le speech mot pour mot** ; **chaque élément coloré est écrit dans « Visuel et caméra » avec son code hexadécimal** (voir « Les couleurs : un code pour chaque élément ») et la couleur du plan suivant dans la transition ; la durée est **en secondes**, dans la dernière colonne. Un plan sans voix off est marqué `(aucune voix off)`.
     4. **`## Annexes`** : **A. Contrôles effectués**, **B. Décisions prises**, **C. À fournir de ton côté**, **D. Rappel sur les faits** (ce qui n'a pas été recoupé avec des sources), **E. Traçabilité créative**, **F. Passages mal couverts par le registre**, **G. Structure globale** (reprise de la section de travail, avec les sources de chaque fait).
        - **Les cinq colonnes du tableau des plans ne changent pas** (les étapes suivantes les lisent) : **la traçabilité va dans l'annexe E, pas dans le tableau**.
        - **E. Traçabilité créative** : **un tableau, une ligne par plan**, colonnes exactes **`Plan | Genre | Recette | Règles (ids) | Ce qui est copié | Écart avec le JSON`**. « Genre » : accroche, explication, exemple, histoire, transition, conclusion ou autre. « Recette » : l'`id` complet. « Règles » : **les `id` complets des règles appliquées** (au moins une par plan). « Ce qui est copié » : en une phrase, **la forme reprise du JSON** (composition, mouvement, transition, valeurs de durée ou de délai, couleur et son sens). « Écart » : « aucun », ou **ce qui diffère et pourquoi** (statut de la règle, adaptation d'un nom au sujet).
        - **F. Passages mal couverts par le registre** : la liste des plans où **rien de solide et d'actif ne couvrait l'idée** (avec le cas le plus proche utilisé, ou la question que je dois trancher), les passages couverts **seulement** par une règle `cas_particulier` ou `hypothese`, et **les recettes du JSON non utilisées avec la raison de chacune** (par exemple « `recette.impact_destruction_chute` : aucune idée de ce genre dans ce speech »). **Une liste vide s'écrit « aucun » et se vérifie.**

<a id="e0ter-10"></a>

### 0 ter.10 · Ce que tu me livres (au final, dans l'ordre des phases ci-dessus)

0. **`Plan_animation.md` livré à chaque phase** (structure, puis speech, puis plan idée par idée) : c'est **le seul fichier de travail**.
1. **Le tableau des avis majoritaires** (court), avant tout le reste.
2. **Le speech** : complet, en anglais, **dans `Plan_animation.md`** (texte de chaque idée, puis colonne « Voix off »), avec les `id` ou liens des sources de chaque fait **dans la structure** (annexe G). **`Speech.md` n'est plus une source** : si je le demande, tu l'extrais **par script** de la colonne « Voix off », pour relecture.
3. **`Plan_animation.md`** : le scénario d'animation, une ligne par plan, au format ci-dessus, **avec la traçabilité créative (annexe E) et les passages mal couverts (annexe F)**. **Le nombre de plans N n'est fixé nulle part** : il découle du **nombre d'idées de ton speech** et de leur durée (voir « Nombres : rien n'est fixé d'avance »). Tu ne cherches jamais à atteindre un nombre de plans donné.
4. **Une courte note** (dans la réponse, pas un fichier) : ce qui vient du web (avec liens), ce qui manquait dans les données, et les voix contraires que le speech garde.

<a id="e0ter-11"></a>

### 0 ter.11 · Ce que tu contrôles avant de livrer

- **Chaque fait** du speech a une source dans l'archive (ou un lien web noté) ; **aucun commentaire n'est cité ni nommé**, et aucun chiffre ne repose **uniquement** sur un commentaire.
- Les **thèmes dominants** du tableau se retrouvent dans le speech **dans l'ordre de leur poids** ; les **voix contraires** y sont présentes ; aucune opinion n'est présentée comme un fait.
- Le speech est **en anglais**, dans la **durée cible du fichier de départ** (à 10 % près), et il est **dans le même style que les speechs de référence** : tu l'as **relu face à des extraits de référence** (ton, adresse au spectateur, longueur des phrases, façon d'ouvrir, de relancer et de conclure, mots par seconde par genre) ; **aucune phrase de référence n'est recopiée** ; tu m'indiques **quelles vidéos de référence tu as lues**.
- **Chaque plan** de `Plan_animation.md` s'appuie sur une **recette** et des **règles du JSON**, avec une voix off **identique mot pour mot** au speech ; **tout le speech est dans le plan**, rien de plus, rien de moins.
- **Contrôle automatique de la créativité, fait par un script que tu écris et lances** (pas à l'œil) : (1) **chaque plan** a une ligne dans l'annexe E ; (2) **chaque `id`** de recette et de règle cité **existe** dans `json_maitre.json` ; (3) **chaque plan cite au moins une règle** ; (4) **aucune règle d'état « archive »** n'est citée ; (5) toute règle `cas_particulier`, `hypothese` ou d'origine `SUJET` citée est **justifiée dans l'annexe F** ; (6) **les valeurs écrites dans « Visuel et caméra »** (durées, délais d'apparition, nombre d'éléments) **sont celles de la règle citée**, sinon l'écart est écrit dans l'annexe E ; (7) **les couleurs** utilisées pour un sens donné sont celles de `codes_de_sens` ; (8) **chaque plan** a **au moins un code hexadécimal** dans « Visuel et caméra » et **chaque mot de couleur** (rouge, vert, bleu, gris, jaune, orange, violet, rose, marron, noir, blanc, beige…) y est **suivi d'un code dans les 40 caractères** ; (9) **chaque code utilisé** figure dans la palette, dans le tableau des éléments qui reviennent, dans le JSON, ou est **justifié dans l'annexe E** ; (10) **un même élément récurrent garde le même code** d'un plan à l'autre. Tu me donnes **le résultat du script**, pas seulement « c'est fait ».
- **Aucun visuel ni aucune logique inventés** : tu as relu chaque plan avec la question « **dans quelle règle, recette ou exemple du JSON est-ce écrit ?** ». Un plan sans réponse est **corrigé ou signalé en annexe F**, jamais gardé en silence.
- Les **couleurs** respectent les codes de sens ; **aucune couleur n'est écrite en mots sans code** ; la palette et le tableau « Couleurs des éléments qui reviennent » sont écrits ; la charte et les interdits sont écrits.
- Tu n'as **pas lu le JSON en entier** (tu l'as lu **par recherche d'`id`**) ; tu me dis quelles rubriques, quelles recettes et **combien de règles** tu as ouvertes et appliquées (**le nombre de règles différentes appliquées est écrit** dans l'annexe A).

<a id="e0ter-12"></a>

### 0 ter.12 · Suite

`Plan_animation.md` alimente l'**étape 1** (lister et classer les assets). Tant que je n'ai pas validé le speech et **le plan complet (phase E)**, **tu ne passes pas à l'étape 1**. L'étape 1 part du **dernier `Plan_animation.md` livré**, jamais d'un fichier en cours de construction (une partie « à faire » dedans = phase E pas finie).

---

> **Phase 3 – Assets de base (étapes 1 à 6)**

<a id="e1"></a>

## Étape 1 : lister et classer les assets

À partir du scénario (`Plan_animation.md`), tu relèves tout ce qu'il faut produire : décors, personnages, objets, icônes.

- Une ligne par asset. Un asset qui revient dans plusieurs plans n'est listé qu'une seule fois.
- Pour chaque asset : un **nom court** (sans caractères interdits dans un nom de dossier Windows : `\ / : * ? " < > |`), une **description** (forme, taille, style, position, tirée de la colonne « Visuel et caméra »), et les **plans** où il apparaît.
- **Rien d'inventé ici non plus.** Tu **relèves** ce que le plan décrit, tu **n'ajoutes aucun asset** qui n'est pas dans une ligne de `Plan_animation.md`, et tu **ne remplaces pas** un objet du plan par un autre que tu trouverais plus joli. La **forme et le style** de chaque asset sont ceux du plan, qui les a **copiés du JSON** (annexe E). Tu relis l'annexe E : **si la recette ou la règle citée prescrit un élément précis** (par exemple le logo de la chaîne, une foule en silhouettes, un type de personnage), **cet élément est dans la liste**, même si la colonne « Visuel et caméra » l'a décrit en une demi-phrase.
- **Contrôle de l'étape 1** : chaque asset de la liste renvoie à **au moins un plan**, et **chaque objet, personnage ou décor décrit dans un plan** (hors textes et éléments d'interface) est **dans la liste ou regroupé dans une planche**. Aucun asset orphelin, aucun oublié.

<a id="e1-1"></a>

### 1.1 · Classer : élément clé ou petit élément

- **Élément clé** : il occupe beaucoup d'espace à l'écran, ou il est important dans l'histoire, ou il revient souvent (décors, personnages, objets fil rouge comme la télécommande). Il garde sa **propre génération**.
- **Petit élément** : il occupe peu d'espace et n'a pas besoin d'un fichier à lui seul (petit objet, petite icône). Il est **regroupé** avec d'autres.

<a id="e1-2"></a>

### 1.2 · Répartir les petits éléments en planches

Une **planche** est un groupe de petits éléments générés ensemble dans une seule image.

- On regroupe des éléments de même famille, de taille voisine et de style compatible.
- Une planche reste petite (en général 4 à 6 éléments), pour que chaque élément reste net et soigné.
- Chaque planche reçoit un nom (`planche_01_petits_objets`, par exemple).

Cette liste est la base de tout le reste : les noms d'assets et de planches deviendront les noms de dossiers de l'archive finale.

<a id="e1-3"></a>

### 1.3 · Livraison de l'étape 1 : le fichier `Liste_assets.md`

Quand tu as fini de lister les assets à utiliser, **tu me l'envoies sous forme de fichier `Liste_assets.md`** (pas seulement dans ta réponse). Je le relis, je le corrige si besoin, puis je m'en sers à l'étape 2. Format du fichier :

- un titre, puis une phrase rappelant que les textes et éléments d'interface (cartons, badges, tampons, étiquettes, règle de vitesse, barres de signal, jauges, pastilles) ne sont pas dans la liste, car ils sont faits au montage ;
- une section **« Éléments clés (une génération chacun) »** : un tableau `# | Asset | Plans` ;
- une section **« Petits éléments (planches) »** : une sous-section par planche (`Planche 1 : télécom`, etc.), chacune avec un tableau `Élément | Plans`.

Exemple :

> **Modèle : voir [Annexe A3](#annexe-a3) (en fin de document).**

Les descriptions détaillées (forme, taille, style, position) restent tirées du scénario : tu les utilises pour choisir les mots et écrire les prompts, mais le fichier `Liste_assets.md` n'a besoin que des noms et des plans.

<a id="e2"></a>

## Étape 2 : chercher les images de référence dans Lexiax (une seule passe)

Cette étape se fait **une seule fois pour l'ensemble des assets** : éléments clés **et** chaque petit élément des planches (chacun a besoin de sa propre référence). Lexiax fournit déjà le prompt et les règles de choix des mots (ils sont dans l'application : tu les suis, tu ne les réinventes pas).

1. **Moi, dans Lexiax** : onglet **« Images de référence »**. Je colle dans **« SPEECH À ILLUSTRER »** le contenu de **`Liste_assets.md`** (la liste complète des assets, éléments clés et petits éléments, que tu m'as envoyée à l'étape 1), puis je clique sur **« Copier prompt + mots pour l'IA »**. Cela copie le prompt et `mots.txt`, la liste de tous les mots de ma bibliothèque. Je te les envoie **une seule fois**.
2. **Toi** : pour **chaque asset de la liste**, tu choisis dans `mots.txt` les mots qui mènent à de bonnes références, puis tu écris **un seul script Python** qui récupère les images de **tous** les assets d'un coup.
   - Tu recopies chaque mot **exactement** comme dans `mots.txt`. Avant de livrer, tu **vérifies par programme** que chaque mot existe dans `mots.txt` (aucun mot inventé).
   - **Ne sature pas : peu de mots, bien choisis.** Les mots de `mots.txt` sont déjà fidèles (chacun désigne une chose réellement repérée dans la bibliothèque, avec sa meilleure image). Inutile d'empiler des mots larges, des mots voisins et des synonymes « au cas où » : ils ramènent surtout du bruit et alourdissent le zip.
   - **Cible : 3 à 5 mots par élément clé, 2 à 4 mots par petit élément.** Le maximum absolu reste 30 mots par asset, mais il n'est pas un objectif.
   - Du particulier au général : le mot le plus précis d'abord. Tu n'ajoutes un mot plus large ou un synonyme que s'il apporte une vraie famille de formes utile, et tu supprimes tout mot qui ne mènerait pas à une référence exploitable.
   - Les mots peuvent se répéter d'un asset à l'autre : le script les traite séparément, pour que chaque asset ait son propre dossier.
   - Pour les planches, chaque petit élément est traité **comme un asset à part entière** (son propre dossier et ses propres mots).
   - Tu ne fais **pas** le tri des images à ce stade.
   - Tu limites le nombre d'images par mot (par exemple 4 à 6) pour que le zip reste léger (quelques dizaines de Mo). Cette valeur est une constante du script (`MAX_PAR_MOT`) que je peux augmenter.
   - Tu **testes le script** (syntaxe et jeu de données factice) avant de me le donner.
   - Tu respectes le format de réponse demandé par le prompt : **une ligne** de consigne courte, puis **le script dans un seul bloc de code**. Rien d'autre.
3. **Moi** : je colle le script dans la zone **« SCRIPT PYTHON »** de Lexiax et je clique sur **« Exécuter »**. Le script crée **un seul zip** dans le dossier `Bibliotheque\InfographicsShowData\references_speech`. **Le même script envoie ensuite ce zip lui-même** (voir la règle sur les envois Git) : je n'ai pas à le sélectionner dans « ZIP PRÊTS ».
4. **Le script, sans aucun geste de ma part** : le zip est envoyé à la racine du dépôt **https://github.com/officecenter632-maker/ImageReferenceData** (branche `main`). Je te donne ce lien (c'est toujours le même). Plus de bouton, plus de glisser-déposer.
   - Le dépôt est public et ne garde **qu'un seul zip à la fois** : chaque nouveau push remplace le précédent.
5. **Toi** : tu télécharges le zip depuis ce dépôt, par exemple avec `git clone --depth 1 https://github.com/officecenter632-maker/ImageReferenceData.git`, puis tu prends le fichier `references_AAAAMMJJ_HHMMSS.zip` à la racine. **Tu gardes cette copie dans ton espace de travail** : si un zip complémentaire est poussé plus tard, il remplace l'ancien sur GitHub, mais pas ta copie.
6. **Toi** : avant tout tri, tu **vérifies la structure** (voir « Vérification du zip reçu » ci-dessous). Tant que la vérification n'est pas bonne, tu ne passes pas à l'étape 3.

<a id="e2-1"></a>

### 2.1 · Vérification du zip reçu (étape 2 bis)

Pour pouvoir comparer, tu gardes dans ton script la **carte de recherche** : pour chaque asset, son nom de dossier et la liste de ses mots. Une fois le zip téléchargé, tu fais ces contrôles **par programme** :

| Contrôle | Ce qui est attendu |
| --- | --- |
| Le zip | Un seul fichier `references_AAAAMMJJ_HHMMSS.zip` à la racine du dépôt, qui s'ouvre sans erreur (`testzip`). Son horodatage est **postérieur** à l'envoi de ton script ; sinon c'est probablement un ancien zip : tu me demandes de relancer le script, qui repousse tout seul. |
| `index.json` | Présent à la racine du zip, JSON valide, avec pour chaque image : asset, mot, fichier, vidéo d'origine. |
| Assets | Chaque asset de ta carte de recherche a son dossier, au nom exact. Aucun dossier d'asset inattendu (les assets déjà validés, exclus du script, n'y sont pas). |
| Mots | Dans chaque asset, chaque mot de ta carte a son dossier `NN_mot` (au nom exact) et contient au moins une image. Les mots vides sont ceux annoncés dans le bilan du script. |
| Images | Chaque image de `index.json` existe dans le zip, et chaque image du zip figure dans `index.json`. Pas plus de `MAX_PAR_MOT` images par mot. |
| Bilan | Les chiffres que tu recalcules (images par asset, mots introuvables, images manquantes) sont ceux du bilan affiché par le script. |

**Résultat** : tu me donnes un court compte rendu (« conforme », ou la liste des écarts).

- **Conforme** : tu passes à l'étape 3.
- **Écarts légers** (quelques mots vides, un asset sans image) : tu continues avec le reste et tu traites ces assets comme dans « Cas particuliers ».
- **Écarts importants** (zip périmé, assets entiers absents, `index.json` illisible) : tu t'arrêtes, tu me le dis, et on repart d'un nouveau push. Tu ne trie rien sur un zip qui ne correspond pas à la recherche.

<a id="e2-2"></a>

### 2.2 · Structure du zip de collecte

Le zip est à la racine du dépôt GitHub. Son contenu :

```
references_AAAAMMJJ_HHMMSS.zip
├── 02_proprietaire_reseau/          ← un dossier par asset
│   ├── 01_homme en costume/         ← un dossier par mot
│   │   └── <images>
│   ├── 02_costume noir/
│   └── ...
├── 12_drone/
├── P1_01_parabole_blanche_maison/   ← un petit élément de planche = un dossier d'asset
├── ...
└── index.json                       ← pour chaque image : asset, mot, fichier, vidéo d'origine
```

Le script affiche à la fin un **bilan** : nombre d'images par asset, mots introuvables, images manquantes.

<a id="e2-3"></a>

### 2.3 · Cas particuliers

- **Asset déjà validé** (par exemple l'opérateur de drone) : il n'est pas relancé, il est exclu du script.
- **Aucune bonne référence dans le zip** pour un asset : c'est l'exception. Tu me le signales à l'étape 3, et seulement pour ces assets-là tu écris un **petit script complémentaire** avec d'autres mots. On ne refait jamais la collecte complète. Le zip complémentaire passe par le même chemin (push sur le même dépôt, téléchargement, vérification de structure) et remplace l'ancien zip sur GitHub : c'est pourquoi tu as gardé ta copie du premier.

<a id="e3"></a>

## Étape 3 : choisir la meilleure référence

Une fois le zip vérifié, tu fais le tri final, asset par asset, **dans ce zip unique**, **par lots** (par exemple 5 à 8 assets à la fois, éléments clés les plus importants d'abord). Chaque lot validé passe tout de suite à l'étape 4 et m'est livré avant que tu ne trions le lot suivant.

- Tu gardes **l'image la plus proche** de l'asset voulu : même sujet, même forme, même composition.
- Les couleurs, l'ambiance et le style **n'ont pas d'importance** pour le choix : l'IA générative les change facilement.
- Tu gardes **une image par asset**. Pour une planche, cela donne une image par petit élément : on ne mélange jamais deux éléments dans une même référence.
- Tu ne retiens que les images que tu as validées. Les autres sont ignorées.
- Si un asset n'a aucune image convenable, tu le listes dans ton retour (voir « Cas particuliers »).

<a id="e4"></a>

## Étape 4 : construire l'archive des assets

Tu crées **un dossier par génération**. Chaque dossier a un sous-dossier `generation`, qui contient les images de référence et le prompt.

<a id="e4-1"></a>

### 4.1 · Pour un élément clé

Le dossier porte le nom de l'asset. Le sous-dossier contient :

- **`reference`** : l'image choisie à l'étape 3, renommée `reference` (elle garde son extension, par exemple `reference.webp`) ;
- **`prompt.txt`** : le prompt pour l'IA générative.

<a id="e4-2"></a>

### 4.2 · Pour une planche de petits éléments

Le dossier porte le nom de la planche. Le sous-dossier contient :

- **une image de référence par petit élément**, nommée `reference_01_<élément>`, `reference_02_<élément>`… (par exemple `reference_01_panier.webp`) ;
- **un seul `prompt.txt`** pour toute la planche.

<a id="e4-3"></a>

### 4.3 · Exemple

```
assets.zip
├── operateur_drone/                  ← élément clé
│   └── generation/
│       ├── reference.webp
│       └── prompt.txt
├── telecommande_geante/              ← élément clé
│   └── generation/
│       ├── reference.webp
│       └── prompt.txt
├── planche_01_petits_objets/         ← planche de petits éléments
│   └── generation/
│       ├── reference_01_panier.webp
│       ├── reference_02_sablier.webp
│       ├── reference_03_loupe.webp
│       ├── reference_04_pouce.webp
│       └── prompt.txt
└── ...
```

<a id="e4-4"></a>

### 4.4 · Ce que contient `prompt.txt`

**Pour un élément clé**, le prompt demande à l'IA générative de **modifier l'image `reference` pour obtenir l'asset voulu**. Il reprend ce que le scénario dit de cet asset :

- la description de l'asset (forme, taille, position, détails) ;
- les couleurs à utiliser, avec leurs codes, tirées de la charte visuelle du scénario (ici les couleurs comptent : ce sont elles que l'IA générative doit changer) ;
- le style : aplats vectoriels, sans ombre portée ; pour les personnages, une petite ellipse sombre sous les pieds ;
- les interdits du scénario : aucun logo réel, aucune ressemblance avec une personne réelle.

**Pour une planche**, le prompt demande **une seule image** qui réunit tous les petits éléments. Il contient en plus :

- la liste des éléments, avec pour chacun **la référence qui lui correspond** (« `reference_01_panier` sert pour le panier », etc.) et sa description propre ;
- la consigne de **transformer chaque élément à partir de sa propre référence**, sans mélanger les références entre elles ;
- la consigne de **bien séparer les éléments les uns des autres**, sur un fond uni, pour pouvoir les découper ensuite ;
- les mêmes couleurs, le même style et les mêmes interdits que pour un élément clé.

<a id="e4-5"></a>

### 4.5 · Livraison progressive (pour ne pas perdre le travail validé)

Les crédits ou les messages peuvent s'arrêter à tout moment. **Tout ce qui n'a pas été livré est perdu.** Tu ne gardes donc jamais un travail validé en attente : tu le livres par lots, au fur et à mesure.

- **Un lot = quelques générations terminées** (par exemple 5 à 8 dossiers : références validées et prompts écrits). Éléments clés d'abord, par ordre d'importance, puis les planches.
- Dès qu'un lot est prêt, tu construis **`assets_lot_NN.zip`** (`assets_lot_01.zip`, `assets_lot_02.zip`…) et tu me le livres **immédiatement**, avant de commencer le lot suivant.
- Chaque lot a **la même structure** que l'exemple ci-dessus (un dossier par génération, avec son sous-dossier `generation`). Seul le **lot 1** contient en plus, à sa racine, l'outil **`copier_assets.pyw`** (voir plus bas). Les noms de dossier ne se répètent jamais d'un lot à l'autre : je fusionne les lots en les décompressant dans un même dossier.
- À chaque lot, tu me livres aussi **`Images_deja_validees_NE_PAS_RETRIER.md`** à jour. C'est la **mémoire du travail déjà fait** : il retient toutes les images de référence déjà validées, pour que personne ne les retrie ni ne les refasse.
  - Format : un tableau `Asset | Type | Image validée (chemin dans le zip de collecte) | État | Lot`.
  - Les états possibles : « validée et livrée », « à faire », « sans référence ».
  - **Règle** : un asset « validée et livrée » est **définitif**. Tu ne le retries pas, tu ne le re-livres pas, même dans une nouvelle conversation. Tu ne traites que les assets « à faire » (et « sans référence », via le script complémentaire).
  - **Reprise** : si une conversation s'arrête (crédits épuisés), je te redonne ce fichier et le lien du dépôt, et tu continues exactement là où tu t'étais arrêté. Je garde les `assets_lot_NN.zip` déjà reçus.
- Si tu sens que la limite approche, tu livres **tout de suite** ce qui est prêt, même si le lot est incomplet, et tu signales ce qui reste.
- Un `assets.zip` final qui regroupe tous les lots n'est produit que s'il reste des crédits. Il n'est pas nécessaire : la somme des lots suffit.

<a id="e4-6"></a>

### 4.6 · `copier_assets.pyw` : copier les prompts et ranger les images générées

Générer les images à la main est pénible : il faut ouvrir chaque dossier, copier le prompt, retrouver les références, puis renommer et ranger chaque image téléchargée. Tu fournis donc **un outil** : une grille de boutons pour copier, et un bouton « Move » pour ranger.

**Livraison.** Un **seul** fichier **`copier_assets.pyw`**, livré **une seule fois**, **à la racine de `assets_lot_01.zip`** (pas dans les lots suivants). Comme je fusionne les lots dans un même dossier, il se retrouve **à la racine du dossier `assets`**, à côté des dossiers d'asset. Extension `.pyw` : un double-clic l'ouvre sans console. **tkinter uniquement** (Pillow, s'il est installé, ne sert qu'aux miniatures). Tu ne le modifies jamais d'un lot à l'autre ; s'il est corrigé, tu le re-livres, une seule fois. Tu le **testes** avant de me le donner, sur de faux dossiers d'asset et un faux dossier Téléchargements. Il doit rester dans `assets` (il cherche les dossiers d'asset à côté de lui) : pour le lancer d'ailleurs, je crée un raccourci.

**Ce qu'il reconnaît.** Une **génération** est tout dossier de `assets` qui contient `generation/prompt.txt` (élément clé ou planche). Elles sont rangées par nom de dossier : les éléments clés `01_…` à `24_…`, puis les planches `planche_01_…`. **L'image générée** d'une génération est n'importe quelle image posée **directement dans son dossier**, à côté de `generation`.

**Fenêtre principale : une grille, rien d'autre.** Pour chaque génération : un **label** (le nom du dossier) et un **bouton « Copier »**. Le label devient **vert** quand l'image générée existe. La fenêtre est **étirée sur toute la largeur de l'écran, collée en haut**, avec autant de colonnes que la largeur le permet, pour rester basse et laisser voir le navigateur en dessous. Mise à jour automatique toutes les 2 s.

- **« Copier »** met dans le presse-papiers, comme des **fichiers** à coller d'un coup dans l'IA de génération : un fichier **`<asset>_prompt.txt`** qui ne contient que le prompt (créé à la volée dans le dossier temporaire), puis les **images de référence** du sous-dossier `generation`, dans l'ordre (`reference`, ou `reference_01_…`, `reference_02_…` pour une planche). Le texte du prompt est aussi copié en texte. Sous Windows seulement ; ailleurs, seul le texte est copié.
- Une génération dont le `prompt.txt` est vide ou introuvable a son bouton grisé. Une référence introuvable est signalée dans la barre d'état et n'empêche pas la copie des autres.
- **Aucune dépendance entre générations** : contrairement aux plans, chaque asset est indépendant, on peut les générer dans n'importe quel ordre.

**Bouton « Move » : ranger les images téléchargées.** Il ouvre une fenêtre qui liste les images du dossier **Téléchargements** (miniatures, nom, date). Le but : faire correspondre chaque image à une génération précise.

- **Ordre par défaut : du plus ancien au plus récent.** L'image la plus ancienne vise la **première génération sans image**, la suivante la génération d'après, et ainsi de suite. Le bouton « Ordre » inverse (choix mémorisé dans un petit fichier `.json` créé à côté du script).
- **Cases à cocher** : seules les images cochées sont rangées. Par défaut sont cochées celles des **dernières 24 h**.
- **Permuter** : on clique sur deux lignes, puis « Permuter » : leurs cibles sont échangées.
- **Valider** : c'est seulement à ce moment que les images sont **déplacées** (pas copiées) dans le dossier de leur génération et **renommées d'après ce dossier** : `02_proprietaire_reseau.png`, `planche_01_telecom.webp` (l'extension d'origine est gardée). Les noms arbitraires de l'IA (« Cinq poses d'un homme d'affaires cartoon.png ») disparaissent donc dès le rangement.
- **Aucune image n'est jamais écrasée** : une génération qui a déjà son image n'est pas visée. Pour refaire un asset, je supprime son image à la main : son label redevient gris.
- **Annuler** ferme la fenêtre sans rien déplacer. **Dossier…** change le dossier surveillé.

**Conséquence pour l'étape 5.** Les images sont déjà dans leur dossier d'asset, **sous un nom prévisible** (`<dossier>.<extension>`). L'arborescence que je te fournis le montre, et le script `collecter_images.py` fonctionne comme décrit : il copie ces images dans `assetsBrute1`. Le cas « nom de fichier introuvable » devient rare.

---

<a id="e5"></a>

## Étape 5 : rassembler les images générées dans un seul dossier

Cette étape commence **après** que j'ai généré toutes les images avec l'IA générative (à partir des dossiers de l'étape 4) et que je les ai posées dans leur dossier d'asset. Les noms de fichier donnés par l'IA générative sont descriptifs mais arbitraires (« Cinq poses d'un homme d'affaires cartoon.png »). Le script de cette étape copie les images dans un seul dossier et les renomme sans ambiguïté, d'après le nom de leur dossier.

<a id="e5-1"></a>

### 5.1 · Ce que je te fournis : l'arborescence réelle

Je t'envoie l'**arborescence réelle du dossier `Assets`** (le dossier parent de `assets`), copiée telle quelle depuis mon ordinateur. Ce n'est pas un exemple : la première ligne donne le **chemin complet** du dossier et chaque ligne donne le **nom exact** d'un dossier ou d'un fichier. Tu t'en sers directement pour écrire le script. Exemple abrégé :

```
📁 D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink\Assets

├── assets/
│   ├── 01_operateur_drone/
│   │   ├── generation/
│   │   │   ├── prompt.txt
│   │   │   └── reference.webp
│   │   └── Comparaison de deux soldats assis.png      ← image générée
│   ├── planche_01_telecom/
│   │   ├── generation/
│   │   │   ├── prompt.txt
│   │   │   └── reference_01_parabole_blanche_maison.webp
│   │   └── Planche d'icônes de communication et défense.png   ← image générée
│   └── ...
└── assets.zip
```

Structure attendue : chaque dossier d'asset contient son sous-dossier `generation` (références et prompt) **et** l'image générée, posée directement dans le dossier d'asset, à côté de `generation`.

<a id="e5-2"></a>

### 5.2 · Ce que tu fais

1. **Tu lis l'arborescence** et tu la compares à `Liste_assets.md` : tous les éléments clés et toutes les planches sont là, chaque dossier a son image générée, aucun dossier n'est en trop. Tu me signales les écarts (dossier sans image, plusieurs images dans un dossier, nom de fichier avec des caractères étranges) avant de livrer le script.
2. **Tu écris un seul script Python, `collecter_images.py`, avec les chemins réels.**
   - Le **chemin du dossier `Assets`** est copié de la première ligne de l'arborescence, écrit en dur dans le script. Tu n'utilises ni chemin relatif, ni `__file__`, ni dossier courant.
   - Le script contient un **dictionnaire `IMAGES`** : pour chaque dossier d'asset, le **nom exact du fichier image** tel qu'il figure dans l'arborescence. C'est lui qui désigne l'image de chaque asset.
   - Si le chemin contient des **emojis** (comme `👉 📚📦 🧠`), tu les écris en codes `\U0001F449`, etc., au lieu de les coller tels quels : certains éditeurs (IDLE par exemple) refusent ces caractères dans un fichier. Le reste du script peut contenir des accents.
3. **Le script se lance depuis un éditeur, pas en ligne de commande.** Je l'ouvre dans mon éditeur (IDLE, Thonny, VS Code, PyCharm) et je clique sur « Run » / « Exécuter ». Il ne lit donc aucun argument, ne pose aucune question, n'utilise pas `sys.exit`, et il écrit son bilan avec un `print` qui ne plante pas sur les caractères que l'éditeur ne sait pas afficher.
4. **Tu livres le script dans un seul bloc de code**, avec une consigne courte : le fichier se place dans le dossier `Assets` (le dossier parent de `assets`) et se lance par « Run » dans l'éditeur.
5. **Tu testes le script** avant de me le donner, sur une arborescence factice qui reprend tes noms (dossier sans image, dossier absent, plusieurs images, nom de fichier différent, caractères accentués ou non latins).

<a id="e5-3"></a>

### 5.3 · Ce que fait le script

- Pour chaque asset du dictionnaire `IMAGES`, il cherche le fichier au **chemin exact** `Assets\assets\<dossier>\<nom du fichier>`. Le sous-dossier `generation` est ignoré : les références et les prompts ne sont pas copiés.
- Il **copie** l'image dans un nouveau dossier **`assetsBrute1`**, créé à côté de `assets` et **du même nom que le zip**, sous le **nom du dossier d'asset**. Les originaux restent à leur place dans `assets`, intacts. **Ce sont les copies de `assetsBrute1` qui font foi.**
  - `02_proprietaire_reseau\Cinq poses d'un homme d'affaires cartoon.png` devient `assetsBrute1\02_proprietaire_reseau.png`.
  - `planche_01_telecom\Planche d'icônes de communication et défense.png` devient `assetsBrute1\planche_01_telecom.png`.
- Si le nom exact est introuvable (je l'ai renommé, ou un caractère diffère), il prend l'image qu'il trouve dans le dossier et le signale. S'il y en a plusieurs, elles sont copiées sous `<asset>_v1`, `<asset>_v2`… et rien n'est écrasé.
- Si le fichier exact existe mais que le dossier contient d'autres images, seul le fichier exact est copié ; les autres sont listées dans le bilan.
- Il écrit un fichier **`index.csv`** dans `assetsBrute1`, avec une ligne par image copiée et quatre colonnes : `fichier` (nouveau nom), `asset`, `type` (`element_cle` ou `planche`) et **`chemin_copie`** (chemin complet de la copie dans `assetsBrute1`). Le CSV ne mentionne pas les originaux.
- Il range les images copiées et `index.csv` dans un **zip nommé `assetsBrute1.zip`**, créé dans le dossier `Assets`, à côté de `assets`. Les fichiers y sont dans un dossier `assetsBrute1/`, pour qu'une fois décompressé le dossier porte le même nom que le zip. Le nom vient de la constante `NOM_ZIP` en haut du script.
- Il affiche un **bilan** : nombre d'images copiées, dossiers absents, assets sans image, noms de fichier différents, autres images non copiées, dossiers non prévus. S'il n'y a aucun écart, il écrit « Aucun ecart. ».
- Le dossier `assetsBrute1`, `index.csv` et le zip sont **recréés à chaque exécution** : je peux relancer le script après avoir regénéré une image. Comme les originaux ne bougent pas, c'est sans risque.
- **Nom du dossier et du zip.** Le dossier des images et le zip portent le même nom, `assetsBrute1` : « brute » parce que ce sont les images telles que générées, avant découpage des planches et retouches. Pour une nouvelle version, je change `NOM_ZIP` en `assetsBrute2`, puis `assetsBrute3`, etc. : le dossier et le zip précédents sont conservés. Ce zip est distinct de `assets.zip` (références et prompts de l'étape 4).

<a id="e5-4"></a>

### 5.4 · Exemple de script (projet `6-musk_starlink`)

> **Modèle : voir [Annexe A4](#annexe-a4) (en fin de document).**


---

<a id="e6"></a>

## Étape 6 : envoyer les images générées sur GitHub et les vérifier

Une fois `assetsBrute1.zip` produit par le script de l'étape 5, je l'envoie sur GitHub pour que tu puisses le télécharger et faire un checkup.

<a id="e6-1"></a>

### 6.1 · Ce que je fais

1. **Je n'ai rien à glisser ni à cliquer** : `assetsBrute1.zip` a été poussé sur GitHub par le script de l'étape 5, au même lancement.
2. Si le script signale un échec d'envoi, je **relance le même script** ; il repousse tout seul. Tu ne me demandes jamais de pousser à la main.
3. Je te dis que c'est fait.

<a id="e6-2"></a>

### 6.2 · Lien de téléchargement

- **Téléchargement direct du zip** : https://github.com/officecenter632-maker/ImageReferenceData/raw/main/assetsBrute1.zip
- Page du dépôt (branche `main`) : https://github.com/officecenter632-maker/ImageReferenceData

Exemple : `curl -L -o assetsBrute1.zip https://github.com/officecenter632-maker/ImageReferenceData/raw/main/assetsBrute1.zip`

**Attention :** le dépôt ne garde **qu'un seul zip à la fois**. Ce push a **remplacé** le zip de références (`references_AAAAMMJJ_HHMMSS.zip`), qui n'est plus sur GitHub. Le lien ci-dessus pointe toujours vers `assetsBrute1.zip`. Pour une nouvelle version (`assetsBrute2`), le lien devient `.../raw/main/assetsBrute2.zip` et remplace le précédent : tu gardes ta copie dans ton espace de travail.

<a id="e6-3"></a>

### 6.3 · Ce que tu fais : le checkup

1. Tu **télécharges** `assetsBrute1.zip` au lien ci-dessus et tu **gardes la copie** dans ton espace de travail.
2. **Structure (par programme)** : le zip s'ouvre sans erreur (`testzip`), contient un dossier `assetsBrute1/` avec `index.csv`, et chaque ligne du CSV a son fichier image (et inversement). Les fichiers sont bien 24 éléments clés (`01_` à `24_`) et 6 planches (`planche_01_` à `planche_06_`), soit **30 images**, sans doublon ni manque par rapport à `Liste_assets.md`.
3. **Images (à l'œil)** : tu regardes chaque image et tu la compares à son prompt et à `Liste_assets.md` : bon sujet, bon style, pas de texte déformé, fond propre (surtout pour les planches : chaque petit élément présent, bien séparé, rien de coupé). Les assets de `Images_deja_validees_NE_PAS_RETRIER.md` ne sont pas retriés : on contrôle les images **générées**, pas les références.
4. Tu m'envoies un **bilan par asset** : OK, ou à regénérer avec la raison (et, si utile, une correction du prompt). Tu ne modifies rien toi-même : pour une image à refaire, je regénère, je relance le script (même `NOM_ZIP` ou `assetsBrute2`), qui repousse tout seul, et tu recontrôles seulement ces images.
5. Quand toutes les images sont bonnes, on passe à la **génération des storyboards**.


---

> **Phase 4 – Storyboard (étapes 7 et 8)**

<a id="e7"></a>

## Étape 7 : organiser le storyboard et générer les plans

Cette étape commence quand le checkup de l'étape 6 est terminé et que les assets bruts (`assetsBrute1`) sont bons. Le but : **générer l'image de chacun des N plans de `Plan_animation.md`, à partir des assets bruts**. Tu examines de quoi chaque plan est fait, tu rédiges son prompt de génération, je génère l'image. **C'est un storyboard, juste pour se faire une idée** de ce qui se passe : il n'y a ni validation ni vérification des plans, et pas de dossier `temp`.

<a id="e7-1"></a>

### 7.1 · Numérotation continue des plans

- Chaque plan a **un numéro unique de 1 à N** : `Plan1`, `Plan2`… `PlanN`. **Le numéro ne se réinitialise jamais**, ni au changement de partie, ni au changement de séquence.
- Les numéros du scénario (`1.1`, `4.7`, `9.7`…) ne servent plus à nommer les fichiers. Chaque prompt rappelle le numéro d'origine, pour retrouver la ligne dans `Plan_animation.md`. Correspondance (**exemple tiré d'un projet précédent** : le vrai découpage suit ton `Plan_animation.md`) :

| Partie du scénario | Plans du scénario | Numéros continus |
| --- | --- | --- |
| 1. Accroche | 1.1 à 1.6 | Plan1 à Plan6 |
| 2. Le contexte | 2.1 à 2.6 | Plan7 à Plan12 |
| 3. La nuit où tout ralentit | 3.1 à 3.8 | Plan13 à Plan20 |
| 4. Qui a donné l'ordre ? | 4.1 à 4.8 | Plan21 à Plan28 |
| 5. Rétabli, vraiment ? | 5.1 à 5.7 | Plan29 à Plan35 |
| 6. Le verdict d'Internet | 6.1 à 6.9 | Plan36 à Plan44 |
| 7. Les gouvernements s'en mêlent | 7.1 à 7.7 | Plan45 à Plan51 |
| 8. La réponse | 8.1 à 8.6 | Plan52 à Plan57 |
| 9. Conclusion et écran de fin | 9.1 à 9.7 | Plan58 à Plan64 |

<a id="e7-2"></a>

### 7.2 · Identifier les séquences

Une **séquence** est une suite de plans consécutifs qui partagent le même décor et les mêmes personnages. Dans le scénario, chaque nouveau décor change de teinte dominante : un changement de décor (donc de teinte) ouvre une nouvelle séquence. Une séquence peut ne contenir qu'un seul plan (fréquent dans l'accroche) ou en contenir plusieurs (par exemple les prises de parole officielles dans le même décor gris-vert).

1. Tu lis `Plan_animation.md` en entier.
2. Tu me proposes le **découpage en séquences** dans un tableau : numéro de séquence, plans (numéros continus et numéros d'origine), décor, teinte dominante, assets utilisés.
3. **Je le corrige et je le valide.** Tu ne crées aucun dossier avant ma validation.
4. Les séquences sont numérotées de façon continue : `sequence1`, `sequence2`, `sequence3`…

<a id="e7-3"></a>

### 7.3 · Le dossier `Storyboard`

Une fois le découpage validé, tu crées **tout le dossier d'un coup** et tu me le livres en `Storyboard.zip`. Cette première archive contient : à la racine le fichier **`Sequences.md`** (le tableau du découpage), puis tous les dossiers `sequenceN` avec leur `speech.txt`, et **tous les fichiers `PlanN.txt`**, un par plan, dans le dossier de sa séquence. **Tous sont remplis** : les N prompts sont écrits d'un coup, plans initiaux et plans suivants, pour que je puisse générer dans l'ordre que je veux. Ainsi, le nombre de fichiers `PlanN.txt` d'un dossier me dit combien de plans contient la séquence :

```
Storyboard/
├── Sequences.md
├── sequence1/
│   ├── speech.txt
│   ├── Plan1.txt
│   ├── Plan1.png
│   ├── Plan2.txt
│   └── Plan2.png
├── sequence2/
│   ├── speech.txt
│   ├── Plan3.txt
│   └── Plan3.png
└── ...
```

- **`speech.txt`** : le speech dit pendant cette séquence, **mot pour mot** (colonne « Voix off » de `Plan_animation.md`), plans dans l'ordre, une ligne par plan sous la forme `Plan6 : la phrase`. Rien n'est ajouté, rien n'est retiré. Un plan sans voix off (l'écran de fin) est marqué `PlanN : (aucune voix off)`.
- **`PlanN.txt`** : le prompt de génération du plan N, dans le dossier de sa séquence. **Un fichier par plan, tous créés dès le départ et tous remplis** : il n'y a ni validation ni attente, donc rien ne justifie de laisser un plan vide.
- **`PlanN.png`** : l'image du plan, que je pose **directement dans le dossier de la séquence**, à côté de `PlanN.txt`. Il n'y a **pas de dossier `temp`** et **aucune validation** : une image posée est une image prise, le storyboard sert seulement à se faire une idée.
- Au départ, aucune image : le dossier d'une séquence ne contient que `speech.txt` et les `PlanN.txt` remplis.
- **Aucun fichier à compléter plus tard** : il n'y a pas de zip `Storyboard_NN.zip`. Si un prompt doit être corrigé, tu me livres le fichier corrigé, avec son chemin.

<a id="e7-4"></a>

### 7.4 · Règle des fichiers `PlanN.txt` : un par plan, tous remplis dès le départ

- **Tous les plans ont leur fichier, et tous sont remplis.** Dans chaque dossier `sequenceN`, tu crées un `PlanN.txt` pour **chaque plan** de la séquence, dès la première archive, **avec son prompt complet**. Le nombre de fichiers `PlanN.txt` d'un dossier donne le nombre de plans de la séquence : `sequence1` contient `Plan1.txt` et `Plan2.txt`, donc 2 plans ; `sequence26` contient `Plan30.txt`, `Plan31.txt` et `Plan32.txt`, donc 3 plans.
- **Le plan initial** (le premier de la séquence) part des assets seuls. **Les plans suivants** de la séquence joignent aussi **l'image du plan précédent**, avec son chemin complet (`...\\Storyboard\\sequenceN\\PlanN.png`), même si cette image n'existe pas encore au moment où tu écris le prompt : elle existera quand je générerai la séquence dans l'ordre. En-tête du fichier : « Plan suivant de la séquence : joindre l'image du plan précédent (PlanN) pour garder le décor et les personnages. »
- **Aucun fichier vide**, aucun fichier à remplir plus tard.
- **Les fichiers ne sont jamais supprimés ni renommés.** Une séquence d'un seul plan n'a qu'un fichier.

Exemple : `sequence1/` contient `Plan1.txt` (plan initial) et `Plan2.txt` (plan suivant, qui joint `Plan1.png`), tous deux remplis ; `sequence2/` contient seulement `Plan3.txt`.

<a id="e7-5"></a>

### 7.5 · Ce que contient `PlanN.txt`

Avant d'écrire le prompt, tu **examines de quoi le plan est fait** : sa ligne dans `Plan_animation.md` (voix off, visuel et caméra, texte à l'écran, couleur), et ce que la voix off veut faire comprendre. Le fichier contient :

1. **L'identité du plan** : `PlanN`, numéro d'origine (par exemple 4.7), séquence, durée.
2. **La voix off** du plan, pour le contexte.
3. **Ce que le plan représente** : en une phrase, ce que l'image doit faire comprendre.
4. **Les images à joindre**, avec leur **chemin complet** (lecteur, dossiers et nom de fichier, jamais un chemin relatif ni un simple nom), pour que je puisse les glisser directement dans l'IA de génération :
   - les **assets** nécessaires, par exemple `D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink\Assets\assetsBrute1\17_bureau_angle_vitre.png`. Quand l'élément vient d'une planche, le prompt donne le chemin complet de la planche, puis dit seulement lequel (par exemple « `...\assetsBrute1\planche_04_interface.png` : le cadran VITESSE »). **Tu ne décris pas le visuel des assets joints** : ils sont fournis en image, on cite leur nom et rien de plus ;
   - **l'image du plan précédent**, si le plan est dans la même séquence, elle aussi avec son chemin complet : `D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink\Storyboard\sequenceN\PlanN.png`. C'est elle qui garde la cohérence du décor et des personnages.
5. **Le prompt de génération** : composition (ce qui est où), pose des personnages, ce qui s'affiche sur les écrans, et la couleur du fond quand le plan introduit un fond nouveau (en code couleur). Pour le style, **une seule phrase : « même style que les images de référence jointes »** ; tu ne redécris ni le style ni l'apparence des assets.
6. **Ce que l'image ne contient pas** : ni texte, ni étiquette, ni badge, ni logo (tout cela est fait au montage, voir `Liste_assets.md`). Les mouvements de caméra (zoom, recul) sont aussi faits au montage : l'image montre la **composition la plus large** du plan (celle d'où partent ou où arrivent le zoom et le recul), pour que le montage puisse s'y déplacer.
7. **Ce qui est fait au montage** : une rubrique « FAIT AU MONTAGE (à ne pas dessiner) » qui liste, pour ce plan, le texte, les tampons, les badges, le logo et le mouvement de caméra.

Le fichier suit toujours cet ordre : identité, voix off, ce que le plan représente, images à joindre, prompt de génération, phrase de style et interdits, fait au montage. Exemple, `sequence3/Plan4.txt` :

```
PLAN4  (plan 1.4 du scénario) · sequence3 · 4 s
Plan initial de la séquence : aucune image de plan précédent à joindre.

VOIX OFF
À cause de l'homme qui possède le réseau.

CE QUE LE PLAN REPRÉSENTE
Le responsable est enfin désigné : le propriétaire du réseau, assis dans son bureau, tient une télécommande géante à un seul bouton. Un petit satellite flotte au-dessus de lui, pour dire qu'il contrôle le réseau.

IMAGES À JOINDRE
- D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink\Assets\assetsBrute1\17_bureau_angle_vitre.png
- D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink\Assets\assetsBrute1\02_proprietaire_reseau.png (pose assise, première à gauche)
- D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink\Assets\assetsBrute1\08_telecommande_geante.png
- D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink\Assets\assetsBrute1\10_satellite_constellation.png (un seul satellite)

PROMPT DE GÉNÉRATION
Dans le décor 17, le propriétaire du réseau (02, pose assise) est assis derrière le bureau, face au spectateur, au centre de l'image. Il tient à deux mains, devant sa poitrine, la télécommande géante (08), presque aussi grande que son torse. Un petit satellite (10) flotte au-dessus de sa tête. Dominante vert menthe #86DDAB.

Même style que les images de référence jointes. Format 16:9.
L'image ne contient aucun texte, étiquette, badge, tampon ni logo (faits au montage). Les mouvements de caméra aussi : l'image montre la composition la plus large du plan.

FAIT AU MONTAGE (à ne pas dessiner)
Le gros plan sur la télécommande puis le recul qui révèle le personnage ; le logo de la chaîne en bas à gauche.
```

<a id="e7-6"></a>

### 7.6 · Ordre de progression

1. **Tous les prompts sont déjà écrits** (pour laisser des bots générer les plans à ma place avec ImGen, voir l'étape 8). Je génère les images dans l'ordre de chaque séquence (le plan initial d'abord, puis les suivants avec l'image du plan précédent) et je pose chaque image dans le dossier de sa séquence.
2. **Aucune validation, aucune vérification.** Tu ne contrôles pas les images et tu ne demandes pas de validation : c'est un storyboard, juste pour se faire une idée. Si je veux refaire un plan, je te le dis.
3. **Tu n'as plus de prompt à écrire**, sauf correction demandée ou plan à refaire : tu me livres alors le fichier `PlanN.txt` corrigé.

<a id="e7-7"></a>

### 7.7 · Cas particuliers

- **Plan qui reprend un plan d'une autre séquence.** Le scénario le prévoit parfois (par exemple 4.7 reprend le décor de 4.2, 9.1 celui de 1.1, 9.4 celui de 5.6). Le prompt cite alors l'image de ce plan (son **chemin complet**, par exemple `D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink\Storyboard\sequence3\Plan4.png`) en plus des assets. Si l'image de ce plan n'existe pas encore, tu me le dis et on le traite d'abord.
- **Plan sans asset généré** (carton de texte, fond uni, écran de fin) : le prompt décrit seulement le fond et la couleur ; le texte reste au montage.

---

<a id="e8"></a>

## Étape 8 : le fichier projet pour ImGen (génération automatique des plans)

Cette étape commence quand le `Storyboard` est livré (étape 7) et que je veux générer les plans avec **ImGen** (`ImGen.pyw`) au lieu de les générer à la main. Les `PlanN.txt` sont la source, le JSON en est la copie exacte, et les images arrivent au même endroit (`Storyboard\sequenceN\`).

<a id="e8-1"></a>

### 8.1 · Ce qu'ImGen attend

Un JSON que je colle dans ImGen (bouton **« + »**, « Nouveau projet »). ImGen le valide, crée le projet et affiche un tableau : une ligne par image. Les bots prennent les images **dans l'ordre du JSON**, une à la fois.

```
{
  "projet": "nom du projet",
  "images": [
    {
      "nom": "Plan1",
      "chemin_sauvegarde": "chemin complet de l'image à créer (.webp)",
      "prompt": "le prompt complet",
      "references": {
        "local": ["chemins complets d'images sur mon PC"],
        "depot": {"url": "lien du dépôt", "branche": "main", "chemins": ["chemins vus dans le zip du dépôt"]}
      }
    }
  ]
}
```

`references` est facultatif : `null`, ou `local`, ou `depot`, ou les deux (avec des images **différentes** dans chacun).

<a id="e8-2"></a>

### 8.2 · Comment le bot (`GPTimageGenarator.py`) lit les références

- **`local`** : le bot lit le fichier sur mon PC (directement, ou par le pont pilote si le bot tourne sur un notebook). Le chemin doit exister **exactement** comme écrit, extension comprise.
- **`depot`** : le bot **clone** le dépôt (`git clone --depth 1`, branche demandée), puis **extrait toujours d'abord tous les zip du dépôt** dans un dossier `<dépôt>_extrait` (comme « Extraire ici »). Les `chemins` sont donc ceux **qu'on voit dans le zip**, par exemple `assetsBrute1/17_bureau_angle_vitre.png` (le dossier du zip porte le nom du zip). Chaque chemin est cherché d'abord dans les zip extraits, puis dans le clone. Un chemin qui ne trouve aucun fichier fait échouer l'image.
- Les références sont jointes au chat **avant** le prompt, **locales d'abord**, puis celles du dépôt. Le bot ajoute lui-même à chaque prompt « Génère l'image demandée. Réponds uniquement avec l'image, sans texte. » : le JSON ne la répète pas.
- **Limites par plan** : 10 références au maximum (locales et dépôt ensemble), 10 Mo par fichier.
- **Format des images** : la compression WebP du bot est **conservée** (qualité 60). Le bot enregistre donc chaque plan en **`.webp`** et ImGen garde cette extension. Le plan suivant reçoit l'image telle quelle, en WebP.

<a id="e8-3"></a>

### 8.3 · Ce que je te fournis

1. L'**arborescence réelle** du dossier `Storyboard`, copiée telle quelle depuis mon ordinateur (chemin complet en première ligne), comme à l'étape 5. Et celle du dossier `Assets` si elle a changé.
2. Le **lien du dépôt GitHub** (toujours `https://github.com/officecenter632-maker/ImageReferenceData`, branche `main`). **Tant qu'ImGen génère, le dépôt doit contenir le zip des assets** (`assetsBrute1.zip`, ou `assetsBrute2.zip` si j'en ai fait une nouvelle version, qui contient alors les 30 images à jour). Je ne pousse rien d'autre dans le dépôt pendant ce temps : un push remplace le zip précédent et casserait tous les chemins du dépôt.

<a id="e8-4"></a>

### 8.4 · Ce que tu fais

0. **Avant de créer le projet, tu me demandes toujours** l'**arborescence réelle du dossier de références GitHub tel qu'il est sur mon PC** (chemin complet en première ligne), au cas où je devrais générer des images à la main. Tu ne commences pas sans l'avoir.
1. **Tu lis les N `PlanN.txt`** (dans `Storyboard.zip` ou dans le dossier). Tu compares l'arborescence à `Sequences.md` : S dossiers `sequenceN`, N fichiers `PlanN.txt`, aucun en trop. Tu me signales les écarts avant de livrer le JSON.
2. **Tu télécharges le dépôt** (`git clone --depth 1`), tu notes le nom du zip qu'il contient et tu en lis le contenu : c'est la **seule source** des chemins `depot`. Tu n'écris jamais un chemin de dépôt de mémoire.
3. **Tu écris le JSON, une image par plan** (N entrées), avec ces règles :

| Champ | Règle |
| --- | --- |
| `projet` | Un nom court (par exemple `6-musk_starlink_storyboard`). ImGen refuse un nom de projet déjà existant. |
| `nom` | `Plan1` … `PlanN`, uniques, numérotation continue. |
| `chemin_sauvegarde` | Le **chemin complet** `.../Storyboard/sequenceN/PlanN.webp`, écrit avec des `/`, recopié de l'arborescence (emojis du chemin recopiés tels quels : le JSON est collé dans ImGen, pas ouvert dans un éditeur Python, donc pas de codes `\U`). L'extension est `.webp` parce que le bot enregistre en WebP. |
| `prompt` | Le contenu **mot pour mot** de la rubrique « PROMPT DE GÉNÉRATION » de `PlanN.txt` (composition, phrase de style, interdits), jusqu'à « FAIT AU MONTAGE » exclu. Ni voix off, ni liste d'images, ni « FAIT AU MONTAGE », ni la consigne que le bot ajoute. Tu ne reformules rien. Guillemets et retours à la ligne échappés correctement. |
| `references.depot` | Les **assets** de « IMAGES À JOINDRE » : `url`, `branche`, et `chemins` **tels qu'ils sont dans le zip** (par exemple `assetsBrute1/17_bureau_angle_vitre.png`), dans l'ordre de « IMAGES À JOINDRE ». Une planche n'est listée **qu'une fois**, même si le plan utilise deux de ses éléments (le prompt dit lequel). Aucun caractère `* ? [ ]` dans un chemin : le bot les lit comme un motif. |
| `references.local` | Les images de **plans**, qui n'existent que sur mon PC : l'**image du plan précédent** de la séquence, et l'image reprise d'un autre plan (cas particuliers de l'étape 7), en **chemins complets**, avec l'extension **`.webp`** (le format réel enregistré par le bot). Le plan précédent d'abord. |
| Plan initial sans plan repris | Seulement `depot`. |
| Carton, fond uni, écran de fin | `"references": null` (pas d'asset, le prompt décrit le fond). |

   Une même image n'apparaît jamais à la fois dans `local` et dans `depot`. Un plan a **au plus 10 références** en tout. Si le plan joint un **asset** déjà présent en `local` dans mon arborescence, il reste malgré tout en `depot` : une seule source par image.

4. **Tu ordonnes les images par vagues.** ImGen prend la première image libre dans l'ordre du JSON et **ne tient pas compte des dépendances** : un bot pourrait commencer `Plan2` avant que `Plan1.webp` existe, et l'image échouerait (« référence locale introuvable »). Tu calcules donc, à partir des « IMAGES À JOINDRE », le graphe des dépendances entre plans :
   - **vague 1** : les plans qui ne joignent aucune image de plan (plans initiaux de séquence qui ne reprennent rien) ;
   - **vague 2** : les plans dont toutes les dépendances sont en vague 1 (deuxièmes plans de séquence, reprises d'un plan de vague 1) ;
   - **vague 3**, **vague 4**… de même.
   Dans une vague, l'ordre suit le numéro de plan. Le JSON liste la vague 1, puis la 2, etc. Tu m'indiques dans ton bilan **quel plan ouvre chaque vague** : je mets en pause à la fin d'une vague (bouton « Pause ») pour que les bots ne démarrent pas une vague dont les images précédentes ne sont pas toutes finies. Une image qui échoue faute de référence se relance via le menu « Bots » (relancer les échecs).

5. **Tu contrôles par programme avant de livrer :**

| Contrôle | Ce qui est attendu |
| --- | --- |
| Validateur d'ImGen | Tu charges `ImGen.pyw` (il s'importe sans interface ni PySide6) et tu passes ton JSON à sa fonction `parse_project_text` : **aucune erreur**. Les seuls avertissements acceptés sont « fichier local introuvable » pour des images de plans pas encore générées. |
| Plans | N entrées, `Plan1` à `PlanN`, sans doublon ni manque, chaque `chemin_sauvegarde` dans le bon dossier `sequenceN`, en `.webp`. |
| Prompts | Chaque `prompt` est identique à la rubrique de son `PlanN.txt` (comparaison automatique). |
| Dépôt | Tu clones le dépôt et tu **extrais le zip** comme le fait le bot : **chaque** chemin de `depot.chemins` désigne un fichier existant, et aucun ne contient `* ? [ ]`. Le nom de dossier dans les chemins est bien celui du zip présent dans le dépôt. |
| Références locales | Chaque chemin local de **plan** pointe vers un `PlanN.webp` d'un dossier de séquence existant, d'un plan **plus tôt dans l'ordre des vagues**. |
| Cohérence avec `PlanN.txt` | Les images à joindre de chaque plan sont toutes présentes dans `references`, ni plus, ni moins. |
| Limites du bot | Chaque plan a au plus 10 références ; aucun fichier de référence ne dépasse 10 Mo. |
| Ordre | Aucune image ne dépend d'un plan placé après elle dans le JSON. |

6. **Tu livres** le fichier **`projet_imgen.json`** (fichier complet, jamais tronqué) avec une consigne courte : « dans ImGen, clique sur **+**, colle le contenu du fichier ». Puis un bilan : nombre d'images, les vagues (plan qui ouvre chacune), le zip du dépôt vérifié, les avertissements attendus.

<a id="e8-5"></a>

### 8.5 · Premier essai

Avant de lancer les N plans, je génère **`Plan1` puis `Plan2`**. Tu me dis quoi vérifier :
- `Plan2` a bien reçu `Plan1` en référence (le chemin local avec emojis passe bien par le pont si le bot tourne sur un notebook) ;
- `Plan1` a bien été enregistré en `.webp` (si le navigateur n'a pas pu produire du WebP, le format peut différer : tu me livres alors le JSON corrigé) ;
- l'image `.webp` de `Plan1` est bien rangée dans le dossier de sa séquence, sous le nom attendu.

<a id="e8-6"></a>

### 8.6 · Corrections

Un prompt à corriger : tu me livres le `PlanN.txt` corrigé **et** l'entrée JSON correspondante, toujours identiques. Les noms de plans ne changent jamais. Si l'image du plan est déjà générée, tu me livres aussi, dans la même réponse, le `reinitialisation_imgen.html` (étape 9) pour que je puisse la réinitialiser dans ImGen d'un clic de copie. ImGen ne modifie pas les prompts : le `projet_imgen.json` corrigé doit être posé dans le dossier du projet **avant** de coller le JSON de réinitialisation.

---

> **Phase 5 – Assets d'animation (étapes 9 à 12)**

<a id="e9"></a>

## Étape 9 : analyser les plans et préparer la génération des assets d'animation

Cette étape commence quand **toutes les images des N plans sont générées** (étape 7, ou étape 8 avec ImGen) et que je les ai rangées dans `Storyboard`. Le but : à partir de chaque plan, savoir exactement ce qui est **le fond** (statique), ce qui **bouge, apparaît ou change d'état** (dynamique), et ce qui se fait **au montage** ; puis **préparer le prompt de génération de chaque élément ou groupe d'éléments**, sur fond détourable, pour qu'ils soient ensuite animés. Les images du storyboard servent de **références visuelles** : ce sont elles que l'IA générative reçoit pour regénérer chaque élément isolé du reste de la scène.

**Principe directeur : on décide d'abord, pour chaque asset, comment l'ajuster à ce que le storyboard en montre ; on ne génère jamais deux fois le même élément.** Un même fond, un même personnage, un même objet revient souvent dans plusieurs plans, et le storyboard le montre chaque fois dans une configuration précise (pose, état, taille, ce qui le cache). Les assets généraux sont déjà connus (`Liste_assets.md`, `assetsBrute1`) ; c'est leur **ajustement technique** qu'on décide. Selon son **rôle dans la scène**, un asset sert tel quel, ou est **décomposé en éléments séparés** que nous reconstituons et manipulons nous-mêmes, ou est décliné en **feuille de sprites**, ou est remplacé par une **animation en code générée par IA**, ou demande une **nouvelle configuration**. Générer chaque plan indépendamment multiplierait le travail, donnerait des découpages différents d'un plan à l'autre et produirait des versions qui ne se ressemblent pas. On **décide donc d'abord, sur les N plans et asset par asset, l'ajustement technique de chacun, avant d'écrire le moindre prompt** ; chaque asset, sous-asset, feuille de sprites et configuration est ensuite généré **une seule fois**, dans le plan où il se voit le mieux, et les autres plans le **réutilisent**. Cela renforce le côté **dynamique** : le découpage suit les mouvements dont chaque scène a besoin, et il est le même d'un plan à l'autre.

Cette étape ne génère aucune image. Elle produit trois livrables : d'abord **`Registre_elements_animation.md`** (la décision d'ajustement technique de chaque asset, configuration par configuration, livrée avant tout prompt), puis, par lots d'environ 10 plans, **l'archive de prompts** (`animation_lot_NN.zip`, un dossier par plan, un JSON par nouvelle génération) et **`Liste_assets_animation.md`** (la fiche de chaque plan : ce qui se passe, fond, assets, chronologie, montage), sans rien d'implicite, pour qu'il n'y ait aucun embrouillement ni à la création des assets sur fond détourable, ni à l'animation.

<a id="e9-1"></a>

### 9.1 · Dépôt dédié : `Storyboard`

Le storyboard ne va **pas** dans `ImageReferenceData`. Il a son propre dépôt : **`Storyboard`** (`https://github.com/officecenter632-maker/Storyboard`, branche `main`). Les deux dépôts sont indépendants : pousser `Storyboard.zip` dans `Storyboard` **ne remplace pas** `assetsBrute1.zip`, qui reste dans `ImageReferenceData`, et les chemins `depot` d'ImGen continuent de fonctionner. Il n'est donc plus nécessaire d'attendre la fin d'ImGen pour pousser, mais je garde ma copie locale de `assetsBrute1`, qui resservira pour la réutilisation des assets. Le dépôt `Storyboard` ne garde lui aussi **qu'un seul zip à la fois** : un nouveau push de `Storyboard.zip` remplace le précédent. L'envoi ne passe plus par Lexiax mais par un script (voir ci-dessous).

<a id="e9-2"></a>

### 9.2 · Ce que je fais : te donner l'arborescence du projet

1. Quand les N images sont générées et rangées dans `Storyboard`, je t'envoie l'**arborescence réelle du projet actuel**, copiée telle quelle depuis mon ordinateur : la première ligne donne le **chemin absolu complet du dossier racine du projet** (ici `D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink`, qui contient `Storyboard`, `Assets`, `Meta`…), chaque ligne le **nom exact** d'un dossier ou d'un fichier (comme à l'étape 5 et à l'étape 8).
2. **Si je ne l'ai pas encore envoyée, tu me la demandes** avant d'écrire quoi que ce soit. Tu n'écris jamais un chemin de mémoire.
3. Je te dis aussi comment je m'authentifie auprès de GitHub : `git` est installé et déjà connecté à mon compte, ou j'ai un jeton d'accès (token) à mettre dans le script. Si tu ne le sais pas, tu me le demandes en même temps que l'arborescence.

<a id="e9-3"></a>

### 9.3 · Ce que tu fais : le script `envoyer_storyboard.py`

À partir de mon arborescence, tu écris **un seul script Python, `envoyer_storyboard.py`**, qui sélectionne **uniquement le storyboard** (les plans), le zippe et l'envoie dans le dépôt `Storyboard`.

**RÈGLE D'OR : tu ne réécris JAMAIS ce script de zéro.** Le script ci-dessous (« Modèle de `envoyer_storyboard.py` ») est **déjà écrit, testé et utilisé avec succès** sur mon ordinateur. **Tu le recopies tel quel, en entier, et tu ne changes que ce que ma situation impose** : le chemin `PROJET` (copié de la première ligne de mon arborescence, emojis en codes `\U0001F449`, etc.), le nom du projet dans l'en-tête, `NB_SEQUENCES` et `NB_PLANS` si le découpage a changé, `DEPOT_URL` / `LIEN_DIRECT` si le dépôt change. **Tu ne touches ni à la structure, ni aux fonctions, ni à la logique d'envoi** (dépôt neuf, un seul commit, push forcé, vérification de la branche distante, jeton jamais affiché) : réécrire du code qui marche fait perdre du temps et introduit des erreurs. Si tu penses qu'une amélioration est vraiment nécessaire, tu me la proposes **avant**, en une phrase, et tu ne l'appliques que si je dis oui. Quand je te redemande « le code de mise à jour », tu me **renvoies ce même modèle** (avec le chemin à jour), jamais une nouvelle version.

**Règles d'écriture** (les mêmes que `collecter_images.py`, étape 5) :
- **le script s'exécute n'importe où sur l'ordinateur** : rangé dans n'importe quel dossier (le Bureau, Téléchargements…), lancé avec n'importe quel dossier courant, il fonctionne de la même façon. Pour cela, il ne dépend ni de son emplacement ni du dossier courant : tu utilises le **chemin absolu du projet**, copié de la première ligne de l'arborescence et écrit en dur en tête du script (constante `PROJET`), et tu en déduis `Storyboard` et `Storyboard.zip`. Ni chemin relatif, ni `__file__`, ni dossier courant ; les emojis du chemin sont écrits en codes `\U0001F449`, etc. ;
- le script se lance **depuis un éditeur** (« Run » / « Exécuter ») : aucun argument, aucune question, pas de `sys.exit`, un `print` qui ne plante pas sur les caractères non affichables ;
- tu le **testes** avant de me le donner, sur un faux dossier `Storyboard` et un faux dépôt `git` local (fichier en trop, image manquante, dépôt vide, ancien zip déjà présent) ;
- tu le livres **dans un seul bloc de code**, avec une consigne courte : il peut être rangé où je veux, et se lance par « Run » dans l'éditeur.

**Ce que le script sélectionne** (et rien d'autre) :

| Inclus | Exclu |
| --- | --- |
| `Sequences.md` à la racine ; dans chaque `sequenceN` : `speech.txt`, les `PlanN.txt` et les images des plans (`.webp`, `.png`, `.jpg`, `.jpeg`, casse du nom comme sur le disque) | `copier_prompts.pyw`, `copier_prompts.json`, `projet_imgen.json`, dossiers `temp`, anciens zip, tout autre fichier. Les fichiers exclus sont listés dans le bilan |

**Ce qu'il fait, dans cet ordre :**
1. **Contrôle de structure avant tout envoi** : S dossiers `sequenceN`, N fichiers `PlanN.txt`, **N images** (une par plan, dans le bon dossier), S `speech.txt`. En cas d'écart (image manquante, plan en trop, mauvais dossier), il l'affiche et **n'envoie rien** : un zip incomplet ne part pas. Une constante `FORCER = False` permet de passer outre, si je le décide.

   **Contrôle des images suspectes : pas dans le script.** Le modèle ne contient pas ce contrôle et tu ne l'y ajoutes pas (sauf si je te le demande). Tu le fais **toi-même, par programme, sur la copie téléchargée** (voir « cloner et contrôler le storyboard », point 3) : image illisible, entièrement noire ou blanche, minuscule, aplat uni, dimensions différentes. Aucun plan suspect n'est écarté en silence.
2. **Zip** : il crée `Storyboard.zip` à la racine du projet, à côté du dossier `Storyboard`, avec un dossier racine `Storyboard/` ; il est recréé à chaque lancement. S'il dépasse **100 Mo** (limite de GitHub par fichier), il s'arrête et le dit.
3. **Envoi** : avec `git`, il crée dans un dossier temporaire un dépôt neuf qui ne contient que `Storyboard.zip`, fait **un seul commit**, puis le pousse sur `https://github.com/officecenter632-maker/Storyboard` (branche `main`, push forcé). Le dépôt ne garde ainsi **qu'un seul zip et un seul commit** : l'ancien zip disparaît, et le dépôt ne grossit pas à chaque envoi. Il fonctionne aussi sur un dépôt vide (premier envoi). Après le push, il relit la branche distante pour **vérifier** que le commit y est. Il ne touche **jamais** à `ImageReferenceData`.
4. **Authentification** : il utilise les identifiants `git` déjà enregistrés sur mon ordinateur ; si je lui ai donné un jeton (constante `GITHUB_TOKEN`, vide par défaut), il l'utilise, **sans jamais l'afficher** dans le bilan. Si `git` est absent ou si l'envoi est refusé, il le dit en clair et laisse `Storyboard.zip` en place pour que je puisse l'envoyer autrement.
5. **Bilan** : nombre de fichiers zippés (plans, images, speech), taille du zip, éventuels fichiers exclus, écarts de structure, résultat du push et lien de téléchargement direct. S'il n'y a aucun écart, il écrit « Aucun ecart. ».

<a id="e9-4"></a>

### 9.4 · Modèle de `envoyer_storyboard.py` (projet `6-musk_starlink`) : à recopier, pas à réécrire

> **Modèle : voir [Annexe A5](#annexe-a5) (en fin de document).**

Après l'envoi, je te dis que c'est fait. Le lien de téléchargement direct est :
`https://github.com/officecenter632-maker/Storyboard/raw/main/Storyboard.zip`
Page du dépôt (branche `main`) : `https://github.com/officecenter632-maker/Storyboard`
Exemple : `curl -L -o Storyboard.zip https://github.com/officecenter632-maker/Storyboard/raw/main/Storyboard.zip`

<a id="e9-5"></a>

### 9.5 · Ce que tu fais : cloner et contrôler le storyboard

1. Tu **télécharges** `Storyboard.zip` depuis le dépôt `Storyboard` (`git clone --depth 1 https://github.com/officecenter632-maker/Storyboard.git`, ou `curl -L` au lien direct), tu **gardes la copie** dans ton espace de travail et tu notes le nom exact du zip et de son dossier racine.
2. **Structure (par programme)** : le zip s'ouvre sans erreur ; S dossiers `sequenceN` ; N fichiers `PlanN.txt` ; **N images** (une par plan, dans le bon dossier de séquence, extension réelle notée : `.webp` ou `.png`, majuscules ou minuscules du nom comprises) ; un `speech.txt` par séquence. Tu compares à `Sequences.md`.
3. **Images suspectes (par programme).** Tu repasses **toi-même** les mêmes contrôles que le script d'envoi sur les N images clonées : illisible, **entièrement noire ou blanche**, fichier minuscule, aplat uni, dimensions différentes de la majorité, format réel différent de l'extension. Tu ne te fies pas à ce que le script a déjà dit : tu le refais sur la copie téléchargée. Une image **noire ou blanche** n'est jamais acceptée comme « fond uni » sans que le `PlanN.txt` l'annonce (couleur noire ou blanche demandée).
4. **Images qui ne correspondent pas à leur plan (à l'œil).** Tu fabriques des **planches-contact numérotées** (12 plans par planche, le numéro écrit sur chaque image) et tu compares chaque image à la ligne « CE QUE LE PLAN REPRÉSENTE » et à « IMAGES À JOINDRE » de son `PlanN.txt` : bon décor, bons personnages, bons objets, texte parasite, élément manquant, élément d'un autre plan (par exemple une constellation avec un point d'interrogation sur un plan qui devait montrer la règle de vitesse seule), fond de la mauvaise couleur, plan qui reprend un autre plan mais qui n'en a pas le décor.
5. **Écarts** : image manquante, image en trop, plan dans le mauvais dossier, image illisible, **image noire, blanche ou vide**, **image qui ne correspond pas à son plan**. Tu me les signales **avant** de commencer l'analyse, dans un tableau `Plan | Problème | Gravité | Action` (les actions possibles : « à regénérer », « à confirmer par moi », « acceptable, noté dans les points à trancher »). Tu n'analyses jamais un plan dont l'image manque, est noire, blanche ou vide : on le traite d'abord, c'est-à-dire que **je regénère l'image, je la repose dans `Storyboard`, je relance `envoyer_storyboard.py`** et tu re-télécharges. Les plans concernés sont marqués « image à regénérer » dans `asset_profond_status.md` et dans le registre, **sans bloquer les autres plans**. **Dans la même réponse que ce tableau, tu me livres directement le fichier `reinitialisation_imgen.html`** (zones de copie des JSON de réinitialisation d'ImGen, voir la sous-section suivante) : je ne te le demande pas.

   **Deux sortes d'écarts, deux traitements.**
   - **Bloquant : à regénérer.** L'image manque, est illisible, **noire, blanche ou vide**, ou **n'a aucun rapport avec son plan** (mauvais décor, scène d'un autre plan). Seuls ces plans vont dans `reinitialisation_imgen.html` et sont marqués « image à regénérer ».
   - **Détail gênant : tu le corriges toi-même, dans les prompts.** Un texte ou un chiffre dessiné par erreur (par exemple le « 13 » du numéro d'asset de Plan56), un élément coupé par le cadre (le masque comique de Plan41), un élément en trop, en moins ou déformé, une mauvaise pose, une flèche mal orientée, un décor un peu différent (la maison avec parabole de Plan22, les deux propriétaires de Plan24, le combiné radio de Plan55). **Je ne regénère pas ces images** et tu ne me demandes pas de le faire : tu les listes dans le tableau avec l'action **« corrigé dans les prompts »** et tu appliques la règle de la sous-section « Défauts de détail » plus bas.

<a id="e9-6"></a>

### 9.6 · Réinitialiser les images à regénérer : le fichier `reinitialisation_imgen.html`

Dès que le tableau des écarts contient au moins un plan « à regénérer » (ou « à confirmer par moi »), tu me livres **dans la même réponse, sans que je le demande**, un fichier **`reinitialisation_imgen.html`**. C'est une page web autonome que j'ouvre dans mon navigateur : elle contient, pour chaque vague, **une zone de texte avec le JSON de réinitialisation et un bouton « Copier »**. Je colle ensuite ce JSON dans ImGen (bouton **« ↺ Réinitialiser par JSON… »**, à côté de « Réinitialiser »). Je n'ai jamais à écrire ni à retoucher un JSON à la main.

**Le JSON, tel qu'ImGen l'accepte (`parse_reset_json`)**

```
{
  "projet": "nom du projet",
  "reinitialiser": [
    { "nom": "Plan17", "raison": "ne correspond pas au prompt (devait être un fond seul)" },
    { "nom": "Plan20", "raison": "image noire" }
  ]
}
```

- `reinitialiser` : liste non vide. Chaque entrée est soit un nom (`"Plan17"`), soit un objet `{"nom", "raison"}`. **Tu mets toujours une raison**, courte et précise : elle est écrite dans le journal de l'image.
- `projet` : le nom exact du projet ImGen (celui de `projet_imgen.json`, par exemple `6-musk_starlink_storyboard`). ImGen refuse le JSON si le nom ne correspond pas au projet ouvert. Si tu n'as pas le `projet_imgen.json` sous la main, tu omets le champ et tu me le dis en une ligne.
- Les noms viennent **exactement** du `projet_imgen.json` (`Plan17`, jamais `plan 17`). Aucun doublon.

**Les vagues (obligatoires quand il y a une dépendance)**

ImGen ne tient pas compte des dépendances : si un plan joint en `local` l'image d'un plan réinitialisé en même temps, un bot peut le générer avec **l'ancienne image fautive**. Tu lis donc les `references.local` de `projet_imgen.json` et tu ranges les plans ainsi :

| Vague | Contenu | Quand je la colle |
| --- | --- | --- |
| **Vague 1** | Les plans « à regénérer » : seulement les écarts **bloquants** (images noires, blanches, vides, illisibles, sans rapport avec leur plan). **Jamais un simple détail gênant** : il se corrige dans les prompts | Tout de suite |
| **Vague 2** (et suivantes) | Les plans qui reprennent en `local` l'image d'un plan de la vague précédente (la dépendance est suivie de proche en proche) | Seulement quand la vague précédente est regénérée **et que je l'ai regardée** |
| **À confirmer** (zone facultative) | Les plans « à confirmer par moi » : seulement si un écart de détail me paraît quand même assez grave pour regénérer l'image (par défaut, il est corrigé dans les prompts) | Seulement si je décide de les regénérer ; **un plan de cette zone n'est jamais mis dans une vague sans ma confirmation** |

S'il n'y a aucune dépendance, il n'y a qu'une vague : tu ne crées pas de vague vide. Si un plan facultatif de la vague 2 a une image qui paraît correcte (il a seulement été généré avec une mauvaise référence), tu le marques « facultatif » dans sa raison et dans la carte.

**Le contenu de la page**

- Un en-tête : nom du projet, date, nombre de plans par vague.
- **Une carte par vague** : titre (« Vague 1 : à coller maintenant »), la condition de collage en une phrase, un petit tableau `Plan | Raison` (pour que je voie ce que je réinitialise), puis la **zone de texte en lecture seule** contenant le JSON, et le bouton **« Copier »**. Le bouton affiche « Copié ✓ » après le clic. Si la copie automatique est refusée par le navigateur, la zone se sélectionne entièrement pour un Ctrl+C.
- Une carte « À confirmer » si elle existe, visuellement distincte (bordure en pointillés).
- **Un avertissement par plan dont le prompt est lui-même la cause de l'erreur** (par exemple un texte écrit dans le prompt que le modèle a dessiné tel quel) : réinitialiser relancerait le même prompt et le même défaut. Dans ce cas, tu me livres **d'abord** le `PlanN.txt` corrigé et l'entrée JSON de `projet_imgen.json` correspondante (voir « Corrections », étape 8) et tu l'écris en haut de la carte.
- Une seule page HTML, **CSS et JavaScript dans le même fichier**, encodage UTF-8, **aucune ressource externe** (ni police, ni script, ni image distante) ; lisible en mode clair et en mode sombre ; zone de texte en police à chasse fixe.

**Structure imposée de la page (c'est le modèle livré et validé, tu le reprends tel quel).** Chaque carte de vague contient, dans cet ordre : le titre, la condition de collage en une phrase, l'avertissement éventuel (encadré orangé), le tableau `Image | Raison`, **une zone de texte `<textarea id="jN" readonly spellcheck="false">`** avec le JSON (échappé pour le HTML), puis **un seul bouton `<button id="bN" type="button">Copier</button>`**. Une seule zone et un seul bouton par vague, jamais de `<form>`.

**LE PIÈGE À ÉVITER : le bouton « Copier » qui ne fait rien.** Je double-clique sur ce fichier : il s'ouvre **depuis le disque (`file://`)**, et dans ce cas **les navigateurs bloquent souvent l'API moderne `navigator.clipboard.writeText`** (elle exige une page « sécurisée »). Une page qui n'utilise que cette API **ne copie rien, sans aucun message d'erreur** : c'est exactement ce qui s'est produit une fois. Règles obligatoires :
1. **Tu essaies d'abord la copie classique** : `t.focus(); t.select(); t.setSelectionRange(0, t.value.length); document.execCommand("copy")`. Elle fonctionne en fichier local, sur une zone `readonly` sélectionnée, et doit être appelée **directement dans le gestionnaire du clic** (jamais après un `await`, un `setTimeout` ou une promesse).
2. **Tu n'utilises `navigator.clipboard.writeText` qu'en plan B**, si `execCommand` renvoie `false`.
3. **Si les deux échouent**, la zone reste **sélectionnée** et le bouton affiche « Sélectionné : Ctrl+C » : je ne dois jamais rester devant un bouton muet.
4. Le bouton affiche « Copié ✓ » seulement quand la copie a **réellement** réussi, puis revient à « Copier » après 2 secondes.

Gestionnaire à recopier tel quel (adapter seulement les `id`) :

```javascript
document.getElementById("b1").addEventListener("click", function () {
  var t = document.getElementById("j1"), b = this;
  function fait() { b.textContent = "Copié ✓"; setTimeout(function () { b.textContent = "Copier"; }, 2000); }
  function selectionner() { t.focus(); t.select(); t.setSelectionRange(0, t.value.length); }
  function plan_b() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t.value).then(fait, function () { selectionner(); b.textContent = "Sélectionné : Ctrl+C"; });
    } else { selectionner(); b.textContent = "Sélectionné : Ctrl+C"; }
  }
  selectionner();
  var ok = false;
  try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
  if (ok) { fait(); } else { plan_b(); }
});
```

**Ce que tu contrôles par programme avant de livrer**

1. Les JSON sont **générés par un script** (`json.dumps(..., ensure_ascii=False, indent=2)`), jamais tapés à la main, puis insérés dans la page **échappés pour le HTML** (`html.escape`). Tu relis le fichier produit et tu extrais chaque zone : le texte extrait est **identique** au JSON généré.
2. Chaque JSON passe dans la fonction **`parse_reset_json`** d'`ImGen.pyw` (il s'importe sans interface) avec la liste réelle des noms du projet : **aucune erreur**, **aucun avertissement** « absent du projet », et la liste de noms retournée est exactement celle de la vague.
3. Aucun plan n'apparaît dans deux vagues ; aucun plan de la vague N+1 ne dépend d'un plan qui n'est pas dans une vague précédente ; chaque raison est non vide.
4. Le nombre de plans de la page égale le nombre de plans « à regénérer » du tableau des écarts (plus, séparément, ceux « à confirmer »).
5. **Le bouton « Copier » est contrôlé** : le script JavaScript de la page passe `node --check` (aucune erreur de syntaxe), il appelle `document.execCommand("copy")` **avant** `navigator.clipboard`, et chaque bouton a sa zone (`id` correspondants). Tu me dis honnêtement si tu n'as pas pu l'essayer dans un vrai navigateur.

**Livraison.** Le fichier `reinitialisation_imgen.html` est livré **seul**, avec en deux lignes : la consigne (« ouvre le fichier, clique sur Copier sur la vague 1, colle dans ImGen ») et le bilan (nombre de plans par vague, plans dont le prompt doit d'abord être corrigé). Quand j'ai regénéré et regardé une vague, tu **mets à jour** la page (la vague faite disparaît ou est marquée « faite »), toujours dans le même fichier et sans que je le demande. Une même relance de contrôle (nouveau `Storyboard.zip` téléchargé) qui trouve de nouveaux plans à regénérer produit une **nouvelle version** du fichier, qui reprend les vagues non faites.

<a id="e9-7"></a>

### 9.7 · Porte avant l'analyse : la mise à jour du dépôt `Storyboard` est-elle faite ?

**Avant de passer à la passe d'inventaire et à la rédaction des prompts d'animation (la suite de l'étape 9), tu t'assures que le dépôt `Storyboard` contient bien les images à jour.** Tant que des plans sont « image à regénérer » (ou « à confirmer » que j'ai décidé de regénérer), tu ne démarres pas l'analyse de ces plans : tu ne dois jamais écrire de prompt à partir d'une image périmée.

Chaque fois que je reviens vers toi (même pour une autre question) alors que des plans étaient « à regénérer », tu fais ce contrôle, dans cet ordre :

1. **Tu me demandes si j'ai regénéré ces images entre-temps** (une seule question, la liste des plans concernés).
2. **Si oui, tu me renvoies le code de mise à jour : `envoyer_storyboard.py`, en entier, dans un seul bloc de code** (même script que celui déjà livré, avec les chemins réels). Je n'ai pas à te le redemander et tu ne me dis pas « relance le script que tu as déjà » : tu le redonnes. Consigne en une ligne : « repose les nouvelles images dans `Storyboard`, lance ce script par Run, puis dis-moi quand c'est fait ». Si l'arborescence a changé depuis, tu me demandes la nouvelle arborescence **avant** de rééditer le script.
3. **Quand je te signale que c'est poussé**, tu **re-télécharges** `Storyboard.zip` (nouveau clone, pas l'ancienne copie) et tu **refais les contrôles** : structure (S séquences, N `PlanN.txt`, N images, S `speech.txt`), images suspectes par programme, puis, à l'œil, **les plans regénérés** (planche-contact numérotée), plus ceux qui les reprennent en `local`.
4. **Tu me rends le verdict** : chaque plan regénéré est soit « validé » (plus aucun écart), soit de nouveau « à regénérer » (une nouvelle version de `reinitialisation_imgen.html` reprend alors les vagues non faites, avec une raison à jour). Tu mets à jour `asset_profond_status.md` dans la même réponse.
5. **Tu ne passes à la passe d'inventaire que lorsqu'il ne reste aucun plan « à regénérer » bloquant** : ou que je t'ai dit explicitement de continuer sans eux. Dans ce dernier cas, les plans non traités restent marqués « image à regénérer » dans le registre et dans `asset_profond_status.md`, et tu n'écris aucun prompt pour eux.

**Si je n'ai rien regénéré**, tu le notes en une ligne et tu continues sur les autres plans, **sans bloquer** (règle déjà posée plus haut). **Si je dis avoir regénéré mais que je n'ai pas poussé**, tu ne te fies pas à ma parole : le nouveau téléchargement montre que les images n'ont pas changé, et tu me renvoies le code de mise à jour.

<a id="e9-8"></a>

### 9.8 · Défauts de détail : tu les corriges dans les prompts, je ne regénère rien

Une image de storyboard n'est qu'une **référence visuelle** : elle sert à générer les assets et les fonds d'animation, pas à être livrée telle quelle. Un défaut de détail qui ne la rend pas inutilisable **ne justifie donc jamais une regénération** : c'est **toi** qui le corriges quand tu écris le prompt de l'asset ou du fond concerné. Je n'ai pas à y penser.

**Ce que tu fais, sans rien me demander :**
1. **Tu repères** le défaut pendant l'inventaire et la visualisation du plan (texte ou chiffre dessiné, élément coupé, en trop, en moins, déformé, mauvaise pose, mauvaise orientation, décor différent du prompt d'origine).
2. **Tu écris la correction dans le prompt** de chaque génération concernée, en toutes lettres : ce qu'il faut **retirer** (« aucun chiffre, aucune lettre, aucun texte »), **compléter** (« l'élément est entier, non coupé, avec de la marge »), **remplacer** (« un seul propriétaire, de dos, derrière le téléphone ») ou **réorienter** (« la flèche part du propriétaire »). Le prompt décrit **ce que le plan devait montrer** (ligne « CE QUE LE PLAN REPRÉSENTE » de `PlanN.txt`), pas le défaut de l'image. Tu ne recopies jamais le défaut.
3. **Tu choisis le plan source** en tenant compte du défaut : si l'asset apparaît net et correct dans un autre plan, tu le prends comme source (voir « Choisir le plan source »).
4. **Tu les notes** dans une section du registre, **G. Détails corrigés dans les prompts** : un tableau `Plan | Défaut vu | Correction écrite dans le prompt | Générations concernées`. C'est une trace, **pas une question** : tu ne les mets pas dans « Points à trancher ».
5. **Dans `asset_profond_status.md`**, le plan reste « à faire » (puis « fait et livré »), avec dans « Remarque » : « détail corrigé dans le prompt : … ».

Cette règle remplace « image à regénérer » pour tout ce qui n'est pas bloquant. Si, **malgré** la correction écrite dans le prompt, le défaut revient sur une image que je génère, c'est **moi** qui te le signale ; tu renforces alors le prompt (et tu mets à jour le JSON), sans que je regénère le storyboard.

<a id="e9-9"></a>

### 9.9 · Passe d'inventaire : décider l'ajustement technique de chaque asset, AVANT tout prompt

**Les assets généraux, on les connaît déjà** : ce sont ceux de `Liste_assets.md`, générés à l'étape 5 (`assetsBrute1`). Cette passe **ne refait pas l'inventaire de base**. Elle sert à **ajuster techniquement** chaque asset à la configuration exacte dans laquelle le storyboard l'utilise : sa pose, son état, sa taille, ce qui le cache, et surtout **ce qu'il fait dans la scène**. Selon ce rôle, un asset est conservé tel quel, ou **décomposé en éléments séparés** que nous reconstituons nous-mêmes et manipulons comme nous voulons, ou **décliné en feuille de sprites** (une suite d'images), ou **remplacé par une animation écrite en code** (générée par IA), ou décliné en une nouvelle configuration. Cette décision se prend **une fois par asset, sur tous les plans où il apparaît**, pas plan par plan : c'est ce qui rend le découpage cohérent d'un plan à l'autre et ce qui permet de ne générer qu'une fois ce qui est identique.

**Tant que le registre n'est pas écrit et livré, tu n'écris aucun prompt, aucun JSON, aucune fiche de plan. Tu n'attends en revanche pas ma validation : une fois le registre livré, tu enchaînes immédiatement sur l'analyse plan par plan puis sur les lots.**

**1. Parcourir les N plans, dans l'ordre, asset par asset.** Les assets de départ sont ceux de `Liste_assets.md` (éléments clés et petits éléments des planches), **plus** ce que l'image montre et que la liste ne contient pas : les **fonds** (cartons, aplats, décors), les **variantes** (le propriétaire en chemise au lieu du costume, la foule en groupes ou les bras levés, le pouce qui appuie ou levé, la télécommande tenue par une vraie main) et les objets non listés (mains qui signent, chemin pointillé…). **L'image fait foi** : une apparition annoncée par la liste mais absente de l'image n'est pas comptée, et une apparition visible mais non annoncée l'est. Des **planches-contact numérotées** sont permises pour comparer les plans entre eux ; l'analyse détaillée de l'étape suivante reste un plan à la fois. Pour chaque apparition, tu notes :

- la **configuration vue** : pose ou état, orientation, taille et cadrage, ce qui le cache ou ce qu'il cache ;
- son **rôle dans la scène** : il bouge (comment : mouvement rigide, déformation, cycle, tracé, pulsation), il apparaît ou disparaît, il change d'état, il est animé avec un autre élément, il reste immobile, il sert de décor ;
- ce qui le **relie aux autres** (il tient un objet, il est devant ou derrière un autre élément, il est relié par un câble).

**2. Décider la technique, pour chaque asset.** Chaque apparition reçoit **une technique** parmi les six ci-dessous (un même plan peut en combiner plusieurs, une par élément). Les techniques sont classées **du plus simple au plus coûteux** ; tu prends **la plus simple qui donne le mouvement voulu**.

| Technique | Quand | Ce qu'on fabrique | Qui l'anime |
| --- | --- | --- | --- |
| **1. Tel quel** | L'asset sert en un seul morceau : il apparaît, se déplace, change de taille, se retourne ou s'efface comme un tout | Une génération, et des **réglages de montage** (position, taille, miroir, rotation, voile). Le même asset vu **dans la même configuration** dans plusieurs plans n'est généré qu'**une fois** | Le logiciel de montage |
| **2. Séparé pour le calque** | Un autre élément passe **devant** lui et le cache en partie (bureau devant un personnage, chaise derrière) | L'élément de devant devient un **calque séparé**, même s'il est immobile | Le logiciel de montage |
| **3. Décomposé en éléments séparés** | Une partie bouge **indépendamment**, par un **mouvement rigide** autour d'un point d'attache : rotation (bras, tête, porte, aiguille), translation, bascule ; ou deux parties arrivent à des moments différents | Une génération **par sous-asset** (ou par groupe de sous-assets compatibles). Chaque sous-asset a : son nom, son **point d'attache** (épaule, cou, charnière…), sa **zone cachée à reconstruire**, son **mouvement attendu** (axe, amplitude, durée) et son **calque** | **Nous** : nous reconstituons l'asset dans le logiciel de montage (hiérarchie, point de pivot) et le manipulons comme nous le souhaitons |
| **4. Animation par code** | L'élément est **géométrique, répétitif ou calculable**, et une image générée serait un mauvais outil : trait qui se trace, pointillés qui avancent, jauge ou barres qui se remplissent, signal qui pulse, particules (cœurs qui montent), compteur, effet de pixellisation progressive, traînées qui dérivent, très grande foule dont chaque silhouette bouge | **Pas d'image** : une **fiche de code** (cahier des charges) que l'IA transformera en code d'animation (SVG, CSS, JavaScript, Lottie ou script du logiciel de montage), sur fond transparent | Le code, écrit par l'IA, puis intégré au montage |
| **5. Feuille de sprites** | L'élément change de **forme** de façon que des parties rigides ne peuvent pas rendre : cycle (marche, hélices qui tournent, clignement), états successifs d'un même dessin (cases barrées une à une, expression qui change), déformation | **Une seule image** qui contient une suite de **4 à 12 images successives** en grille, cellules de même taille, même cadrage et même ancrage, séparées par un vide net. On la découpe ensuite en images que l'on **joue à la cadence voulue** | Le logiciel de montage (lecture d'images) |
| **6. Nouvelle configuration** | La pose, l'état ou l'angle vus **n'existent pas** dans l'asset de départ et ne s'obtiennent ni en bougeant des sous-assets ni par une feuille de sprites (de dos au lieu de face, autre tenue, ouvert au lieu de fermé) | Une **nouvelle génération**, rattachée au même asset, avec le **même cadrage, la même taille et le même point d'ancrage** que sa configuration de base | Le logiciel de montage |

**Comment choisir entre elles.**
- Un **mouvement rigide** autour d'une articulation → **décomposer** (3), jamais une feuille de sprites.
- Un **dessin riche qui change de forme** (visage, tissu, objet qui se déforme) → **feuille de sprites** (5).
- Un élément **géométrique ou répétitif** (lignes, barres, jauges, pointillés, particules, foule de silhouettes identiques) → **code** (4), plus net, plus léger et plus modifiable qu'une image. Le code reprend les **couleurs et le style en aplats** du plan ; il n'invente aucun élément.
- Quand deux techniques donnent le même résultat, tu prends la plus simple. **La décomposition suit le mouvement, jamais l'inverse** : un asset n'est découpé que si quelque chose le justifie (une partie qui bouge, qui arrive à un autre moment, ou un calque à intercaler). Chaque découpe, chaque feuille de sprites ajoute des générations à produire et un risque que les morceaux ou les images ne se raccordent pas.
- Pour décider, tu t'appuies sur la voix off, sur la ligne « CE QUE LE PLAN REPRÉSENTE », sur le scénario (`Plan_animation.md`, colonne « Visuel et caméra ») puis sur les plans voisins.

**Continuité entre deux plans.** Quand deux plans consécutifs montrent le même asset dans deux configurations (l'opérateur assis droit, puis penché la main sur la tête), tu regardes si on passe de l'une à l'autre **en animant des sous-assets** (le bras et la main qui montent) plutôt qu'en remplaçant une image par l'autre. Si oui, l'asset est **décomposé une fois**, et les deux plans utilisent les mêmes sous-assets. Sinon, c'est une **substitution** (coupe) et la seconde configuration est une nouvelle génération.

**Un seul ajustement par asset.** La décomposition (ou la feuille de sprites, ou la fiche de code) est définie **une fois** pour l'asset, sur le plan le plus exigeant (celui qui demande le plus de parties séparées, d'images ou de comportements) ; les autres plans l'utilisent, avec les parties inutiles laissées immobiles. Les points d'attache, les calques, les tailles et les ancrages sont **les mêmes d'un plan à l'autre**.

**Fonds.** Un même décor qui revient (même cadrage, teinte un peu changée ou assombrie) est **un seul fond**, généré une fois, **assez large pour le plan le plus exigeant** (zoom, recul, déplacement de caméra). Ce qui change dessus est un asset, un état, un effet de code ou de montage. Un décor vu sous un autre angle est un autre fond.

**Un doute** entre deux techniques, ou entre « nouvelle configuration » et « réutilisation avec retouche de montage », se tranche en faveur de la **solution la plus simple**, sauf si le mouvement annoncé est irréaliste ainsi ; tu le notes alors dans « Points à trancher » du registre.

**3. Choisir le plan source.** Chaque asset, sous-asset, feuille de sprites et configuration est **généré une seule fois**, dans le dossier du **plan source** : celui où il se voit **le plus net, le plus complet et le moins caché**. Par défaut, c'est sa **première apparition** ; tu prends un plan plus tardif seulement si la première est nettement moins bonne (partiellement caché, très petit, pixellisé, en transition). La génération part de **l'image de ce plan, seule référence** (règle des JSON), et **tous les sous-assets d'un même asset sont générés à partir de la même image de plan**, pour garder la même main de dessin. Les autres plans utilisent ce qui est généré, sans rien régénérer. Un élément **en code** n'a pas de plan source d'image : sa fiche de code est écrite une fois, dans le dossier du premier plan où il apparaît.

**4. Livrer `Registre_elements_animation.md`**, **avant le lot 1**, avec ces sections :

- **A. Résumé** : nombre d'assets, de fonds, d'assets décomposés, de sous-assets, de feuilles de sprites, d'éléments en code, de nouvelles configurations, et de générations économisées par rapport à « tout régénérer plan par plan ».
- **B. Fonds** : un tableau `ID | Fond | Teinte | Plan source (génération) | Plans qui l'utilisent | Retouche de montage par plan | Largeur demandée`.
- **C. Assets**, **une sous-section par asset** (celui de `Liste_assets.md`, avec son numéro, ou son nom si ajouté) :
  - un tableau **une ligne par plan** : `Plan | Configuration vue | Rôle dans la scène | Technique (1 à 6) | Génération (JSON prévu, fiche de code prévue, ou « réutilise PlanN/NN_nom ») | Retouche de montage` ;
  - si l'asset est **décomposé** : un **schéma de décomposition** (la liste des sous-assets, leur hiérarchie, le **point d'attache** de chacun, la **zone cachée à reconstruire**, le **mouvement attendu**, l'ordre des calques) ;
  - si l'asset est une **feuille de sprites** : la **grille** (colonnes × lignes), le **nombre d'images**, la **taille de cellule**, l'**ancrage**, la **cadence** (images par seconde), **boucle ou non**, et la **description image par image** ;
  - si l'asset est **en code** : la **fiche de code** (voir plus bas), ou sa référence.
- **D. Assets à usage unique** : ce qui n'apparaît que dans un plan (liste courte : plan, élément, technique).
- **E. Plans à regénérer** : les plans dont l'image du storyboard est suspecte (voir « cloner et contrôler le storyboard »), exclus de l'analyse.
- **F. Points à trancher** : tous les doutes de décision, y compris les choix de technique.
- **G. Détails corrigés dans les prompts** : les défauts de détail vus sur les images du storyboard (voir « Défauts de détail »), plan par plan, avec la correction écrite dans le prompt. Ce sont des décisions déjà prises, pas des questions.

**Fiche de code** (un fichier `NN_nom_code.md` dans le dossier du plan, jamais un JSON d'image). Elle contient : **ce que l'élément fait** (comportement, mouvement, rythme), les **paramètres modifiables** (durée, cadence, nombre d'éléments, amplitude, couleurs en codes), la **position et la taille** dans l'image (en % comme pour un asset), le **moment d'entrée et de sortie** dans le plan, la **sortie attendue** (animation sur fond transparent, format et dimensions) et le **style** (aplats, mêmes couleurs que le plan, aucun texte, aucun logo). Elle est assez précise pour qu'on la donne telle quelle à une IA qui écrira le code.

**5. Aucune validation bloquante : tu enchaînes.** Tu me livres le registre (je le lis quand je veux, il ne bloque rien) et tu passes **tout de suite** à l'analyse plan par plan, sans me demander « ok ». Le registre est **la référence** : l'analyse plan par plan s'y plie. Une décision de technique se répercute sur tous les plans où l'asset apparaît : si je te corrige le registre plus tard, tu mets à jour **tous** les plans, fiches et JSON concernés. Si l'analyse d'un plan montre qu'il faut corriger le registre (un mouvement qui exige un sous-asset de plus, une feuille de sprites au lieu d'un découpage), tu le notes dans « Points à trancher », tu mets le registre à jour avec les plans concernés et tu continues.

<a id="e9-10"></a>

### 9.10 · Ce que tu fais : visualiser chaque plan, un par un

Une fois le registre livré (sans attendre ma validation), tu regardes **l'image de chaque plan, de Plan1 à PlanN, une par une** (jamais plusieurs plans d'un coup, jamais de mémoire), en gardant le registre ouvert : pour chaque chose visible, tu dis si elle est **générée ici** ou **réutilisée d'un autre plan**. Pour chacun, tu croises : **l'image**, son `PlanN.txt` (voix off, « ce que le plan représente », « fait au montage ») et le `speech.txt` de sa séquence.

**Le plan et le speech ne se calquent pas exactement.** Une phrase de la voix off tombe dans un intervalle de temps qui peut chevaucher deux plans. Tu t'en sers pour **comprendre ce que la scène veut dire**, jamais pour caler un plan sur une phrase.

**Tu visualises la scène comme un film, pas comme une image isolée.** Tu pars de la fin du plan précédent et tu vas vers le début du suivant, et tu imagines ce qui se passe entre les deux : ce qui reste, ce qui part, ce qui arrive, et comment. L'image du plan n'est qu'une **référence visuelle** qui t'aide à voir la scène.

Avec cela, tu **anticipes ce qui sera dynamique** (ça bouge, apparaît, disparaît, change d'état) **et ce qui sera statique** (le fond). Règles :
- l'image fait foi pour ce qu'elle montre : tu **n'inventes aucun élément absent** et tu **n'oublies aucun élément visible**, **sauf un défaut de détail** (voir « Défauts de détail »), que tu **corriges dans le prompt** au lieu de le reproduire ;
- quand tu doutes d'un mouvement, tu choisis la **proposition la plus probable**, tu la notes dans « Points à trancher » et tu continues : tu ne me bloques pas ;
- si l'image montre autre chose que le prompt du `PlanN.txt` (élément en plus, en moins, déformé), tu le notes aussi dans « Points à trancher ».

**Chaque chose visible est classée dans une et une seule de ces catégories.** Le registre dit, pour chaque asset, laquelle de ses techniques s'applique ; ce tableau sert à classer ce qui n'est pas un asset (fond, forme, texte).

| Catégorie | Définition | Ce qu'on fabrique |
| --- | --- | --- |
| **FOND** | Le décor qui ne bouge pas : sol, murs, ciel, motif, couleur de fond, éléments fixes du décor | Une image de fond **vide**, pleine page, sans aucun élément mobile (pas de détourage) |
| **ASSET** | Tout élément qui **bouge, apparaît, disparaît, change d'état ou est animé séparément** : personnage, objet, icône, flèche dessinée, effet | Une image **sur fond détourable** (un élément, ou un groupe d'éléments générés ensemble) |
| **CODE** | Tout ce qui est **géométrique, répétitif ou calculable** et que le registre confie à une **animation écrite en code** par une IA (tracé, jauge, particules, pulsation, pixellisation…) | Une **fiche de code**, pas d'image |
| **MONTAGE** | Tout ce qui se fait dans le logiciel de montage : texte, étiquette, badge, tampon, logo, jauge, barre, pastille, cercle, ligne, flèche simple, règle graduée, voile, masque, ombre sous les pieds, mouvement de caméra | Rien à générer |

**Une forme géométrique simple** (rectangle, cercle, disque, ligne, flèche, trait pointillé, barre, croix, coche, coin de panneau, ellipse d'ombre) est **MONTAGE**, sauf si elle porte un dessin propre (ex. flèche en câble épais), ou si son animation est trop complexe pour le logiciel de montage (tracé, pulsation, répétition) : le registre la confie alors au **CODE**.

<a id="e9-11"></a>

### 9.11 · Règles de découpage en générations

Un plan contient souvent plusieurs éléments. Tu les **scindes** en groupes d'éléments ou en éléments seuls. Une **génération** est une image à créer : un fond vide, un asset seul, ou un groupe d'assets.

1. **Un asset par chose qui bouge indépendamment.** Si deux éléments arrivent à des moments différents, ou vont dans des directions différentes, ce sont deux assets. Quatre groupes de foule qui s'allument un par un = quatre assets.
2. **Des éléments qui bougent toujours ensemble = un seul asset.** Une pile de caisses qui ne bouge pas en bloc ; un journal et son titre.
3. **Groupe de génération.** Plusieurs assets peuvent être générés **sur une même image** seulement s'ils sont de même famille, de taille voisine, séparés par un vide net, et si chacun reste net (4 à 6 au plus). Sinon, chacun a sa propre génération.
4. **Un personnage n'est découpé que si une partie est animée, et le découpage est celui du registre.** Il est défini une fois pour l'asset, sur tous ses plans, pas plan par plan. Un personnage figé = un asset. Un personnage dont un bras se lève ou dont la main va sur la tête = **parties séparées** (corps, tête, bras animé, main), chacune avec son nom, son point d'attache (épaule, cou) et la zone cachée à reconstruire.
5. **Un état qui change l'aspect = une génération par état**, ou une **feuille de sprites** quand les états sont nombreux (4 à 12) et se suivent comme une animation (écran vert puis gris, pose normale puis main sur la tête, cadenas fermé puis ouvert), avec le même cadrage, la même taille et le même point d'ancrage.
6. **Zones cachées.** Quand un élément en cache un autre dans l'image (personnage derrière un bureau, journal sous une main), tu notes **ce qui doit être reconstruit**.
7. **Le fond d'un plan est l'image du plan sans ses éléments dynamiques.** Tu listes ce qui doit disparaître, ce qui doit être reconstruit à la place, et si le fond doit **dépasser le cadre 16:9** (zoom, recul, déplacement de caméra) et de combien.
8. **Un élément qui revient dans plusieurs plans est généré une seule fois.** Son JSON se trouve dans le dossier de son **plan source** (voir le registre). Les autres plans n'ont **aucun JSON** pour cet élément : leur fiche écrit « réutilise `PlanN/NN_nom` » et indique la **retouche de montage** (position, taille, retournement, voile, contenu d'écran…). Un plan reçoit un **nouveau JSON** pour un élément déjà connu **seulement** si c'est une **variante** (règle 5 : autre pose, autre état). Le fond d'un décor qui revient est généré **une fois**, assez large pour le plan le plus exigeant.
9. **Un plan peut n'avoir aucun JSON.** Si tout ce qu'il contient est réutilisé ou fait au montage, son dossier contient seulement un fichier `_reutilise.txt` qui liste, une ligne par élément, ce qui est réutilisé et d'où (ou `_rien_a_generer.txt` si le plan est un aplat seul).

<a id="e9-12"></a>

### 9.12 · Règles du fond détourable

Les assets (jamais les fonds) se génèrent sur un **fond uni détourable**. Chaque génération d'asset dit dans son prompt :

- **La couleur de détourage**, choisie **par génération** : vert pur `#00FF00` par défaut ; magenta `#FF00FF` si l'asset contient du vert ou du turquoise ; bleu pur `#0000FF` s'il contient du vert **et** du magenta. Elle ne doit apparaître **nulle part dans l'asset**, ni proche d'une de ses couleurs.
- **Aplat parfait** : aucune ombre portée, aucun dégradé, aucun halo, aucun sol. L'ombre sous les pieds des personnages est MONTAGE.
- **Marge** : l'asset est entier, jamais coupé, avec de la marge sur tous les côtés.
- **Transparence** : un halo, une zone translucide, une lueur ou un voile **ne se détourent pas**. Ils sont générés **opaques** ou, mieux, classés **MONTAGE**.

<a id="e9-13"></a>

### 9.13 · Ce que tu me livres : l'archive de prompts

**Une archive par lot**, `animation_lot_NN.zip` (`animation_lot_01.zip`, `animation_lot_02.zip`…), d'environ 10 plans consécutifs. **Un dossier par plan** (`Plan1`, `Plan2`…, numérotation continue, même nombre de dossiers que de plans du lot) et, dans chaque dossier, **un fichier JSON par nouvelle génération** (jamais pour un élément déjà généré dans un autre plan) : le fond vide du plan d'abord (s'il n'est pas déjà généré ailleurs), puis les assets ou groupes d'assets, du fond vers le devant. Un dossier sans nouvelle génération contient `_reutilise.txt` ou `_rien_a_generer.txt` (règle 9) ; un élément en code y a sa fiche `NN_nom_code.md`.

```
animation_lot_01.zip
├── Plan1/
│   ├── 01_fond_poste_pilotage_vide.json
│   ├── 02_operateur_assis.json
│   └── 03_ecrans_drone.json
├── Plan2/
│   ├── 01_fond_poste_pilotage_vide.json
│   ├── 02_operateur_main_sur_tete.json
│   └── ...
└── ...
```

Le nom du fichier est `NN_nom_court` : `NN` donne l'ordre (fond = `01`), le nom n'a aucun caractère interdit dans un nom Windows (`\ / : * ? " < > |`).

**Contenu d'un JSON** : le nom, le prompt, et **une seule référence : l'image du plan**, prise sur GitHub dans le dépôt `Storyboard`. Les références sont toujours au format `depot` (celui d'ImGen) ; il n'y a **ni `chemin_sauvegarde`, ni référence locale, ni asset de `assetsBrute1`** : l'image du plan contient déjà tout ce qu'il faut.

```
{
  "nom": "Plan4_02_proprietaire_assis",
  "prompt": "…",
  "references": {
    "depot": {
      "url": "https://github.com/officecenter632-maker/Storyboard",
      "branche": "main",
      "chemins": ["Storyboard/sequence3/plan4.webp"]
    }
  }
}
```

- `chemins` est le chemin **tel qu'on le voit dans le zip** du dépôt : `Storyboard/sequenceN/planN.webp`, avec la **casse exacte du fichier** (les images sont en minuscules : `plan4.webp`, alors que les prompts sont `Plan4.txt`), et sans caractère `* ? [ ]`.
- `nom` est `PlanN_NN_nom_court`, unique dans tout le projet.

**Contenu du prompt.** L'IA reçoit l'image du plan en entier : le prompt lui **désigne** l'élément à produire (sa description, sa position dans l'image : « le personnage à gauche »), jamais plus.

- **Fond** : « même image, sans [liste des éléments dynamiques] ; reconstruis ce qui était caché derrière eux ; [le fond doit être plus large / plus haut que 16:9 de tant, si la caméra bouge] ». Pas de fond détourable.
- **Asset ou groupe** : « reproduis uniquement [élément(s) désigné(s)], isolé(s), entier(s), centré(s), sur un fond uni `#00FF00` (ou la couleur choisie) ; aplat parfait, ni ombre, ni dégradé, ni halo, ni sol ; même style et mêmes couleurs que l'image de référence ; reconstruis ce qui était caché ». Pour un groupe, chaque élément est désigné et séparé des autres par un vide net. Pour un état, le prompt dit lequel (« bras levé »). Pour un personnage articulé, il dit quelle partie.
- **Feuille de sprites** : « reproduis [l'élément] en N images successives, rangées en grille de C colonnes × L lignes, **cellules de même taille**, même cadrage et même ancrage dans chaque cellule, séparées par un vide net, sur un fond uni `#00FF00` (ou la couleur choisie) ; image 1 : [état], image 2 : [état]… ». Le `nom` du JSON se termine par `_sprites`.
- **Élément en code** : **pas de JSON**. Un fichier `NN_nom_code.md` (fiche de code, voir le registre) est livré dans le dossier du plan où l'élément apparaît en premier.
- **Dans tous les cas** : « même style que l'image de référence jointe », et « aucun texte, étiquette, badge, tampon ni logo ».

<a id="e9-14"></a>

### 9.14 · Livraison progressive (pour ne pas perdre le travail)

Les jetons ou les messages peuvent s'arrêter à tout moment. **Tout ce qui n'a pas été livré est perdu.** Tu ne gardes donc jamais du travail terminé en attente, même au milieu d'un lot de 10 plans.

- **Le registre d'abord** : `Registre_elements_animation.md` est livré **dès qu'il est prêt**, avant tout prompt. C'est le premier livrable de l'étape.
- **Dès que 3 plans environ sont terminés**, tu livres **tout de suite** l'archive du lot **dans son état actuel** (`animation_lot_NN.zip` avec les dossiers des plans déjà faits), `Liste_assets_animation.md` cumulatif et `asset_profond_status.md` à jour, **avant** de continuer. Tu recommences ainsi tous les 3 plans. Chaque livraison remplace la précédente du même lot : l'archive est **cumulative**.
- Si tu sens que la limite approche, tu livres **tout de suite** ce qui est prêt, même un seul plan, et tu signales ce qui reste.
- **`asset_profond_status.md`** (ce nom exact, jamais un autre : ni `Avancement_animation.md`, ni `asset_profond.md`, ni `asset_profond_1.md`) est la mémoire du travail de l'étape 9. Il commence par le titre `# Avancement de l'animation (étape 9)` et une phrase de contrôle (zip et commit du dépôt `Storyboard` contrôlés, nombre d'images lues, état du registre), puis contient un tableau `Plan | État | Lot | Remarque`, avec les états « fait et livré », « à faire » ou « image à regénérer » (plan dont l'image du storyboard est noire, blanche, vide ou ne correspond pas à son plan : il est mis de côté jusqu'à ce que je la regénère). Un plan « fait et livré » est **définitif** : tu ne le refais pas, même dans une nouvelle session.
- **Reprise** : si la session s'arrête, je te redonne `Registre_elements_animation.md`, `asset_profond_status.md`, `Liste_assets_animation.md` et les archives déjà reçues ; tu reprends au premier plan « à faire », avec le même format, les mêmes noms et les mêmes conventions.

<a id="e9-15"></a>

### 9.15 · Ce que tu me livres : `Liste_assets_animation.md`

En plus de l'archive, **un seul fichier `Liste_assets_animation.md`**, **cumulatif**, qui dit pour chaque plan **tout ce qu'il faut savoir pour animer**. Aucun champ n'est laissé vide : un champ non applicable est écrit « sans objet ».

**Fiche d'un plan**, toujours dans le même ordre :

1. **Identité** : `PlanN`, numéro d'origine, séquence, durée, voix off, image analysée (`Storyboard/sequenceN/planN.webp`).
2. **Ce qui se passe** : en quelques phrases, ce qui reste du plan précédent, ce qui arrive, ce qui part, ce qui change, et comment.
3. **FOND (statique)** : description, couleur dominante (code), éléments à retirer, zones à reconstruire, besoin d'un fond plus large pour la caméra. **Origine** : « généré ici » (fichier JSON associé) ou « réutilise `PlanN/NN_nom` » avec la retouche de montage.
4. **ASSETS (dynamiques)**, du fond vers le devant : un tableau, une ligne par élément, avec les champs ci-dessous.
5. **Chronologie d'animation** : l'ordre exact dans lequel tout apparaît et bouge pendant les secondes du plan (ex. « 0 s : fond ; 0,5 s : opérateur ; 2 s : écran droit glisse depuis la droite »).
6. **MONTAGE** : tout ce qui se fait au montage dans ce plan (texte exact, étiquette, badge, tampon, logo, forme simple, ombre, voile, mouvement de caméra), avec son emplacement et son moment d'apparition.
7. **Contrôle de couverture** : « chaque chose visible de l'image est classée FOND, ASSET ou MONTAGE : oui ». Si une chose n'est pas classée, elle est signalée ici.
8. **Points à trancher** pour ce plan.

**Champs d'un asset** : nom ; **technique** (tel quel, calque séparé, décomposé, code, feuille de sprites, nouvelle configuration) ; type (personnage, objet, icône, effet, forme dessinée, partie de personnage) ; description visuelle (forme, couleurs en codes, pose ou état, orientation, détails) ; position et taille dans l'image (centre en % de la largeur et de la hauteur, taille en % de la hauteur, rotation en degrés) ; ordre des calques ; animation (entrée, mouvement pendant le plan avec départ et arrivée, sortie, ordre d'arrivée, délai et durée en secondes) ; états ; parties séparées (point d'attache, zone cachée) ; **pour une feuille de sprites** : grille, nombre d'images, cellule, ancrage, cadence, boucle ; **pour un élément en code** : renvoi à sa fiche de code ; zones cachées ; couleur de détourage et pourquoi si ce n'est pas le vert ; groupe de génération (quels autres éléments sont générés avec lui) ; **origine** : « généré ici » (fichier JSON associé) ou « réutilise `PlanN/NN_nom` » avec la retouche de montage ; remarque. Pour un asset réutilisé, tous les champs de **position, taille, calque et animation** restent propres à ce plan : seule la génération est partagée.

Les fiches sont livrées **par lots d'environ 10 plans**, avec l'archive du même lot.

<a id="e9-16"></a>

### 9.16 · Ce que tu contrôles par programme avant chaque livraison

| Contrôle | Ce qui est attendu |
| --- | --- |
| Couverture des plans | Un dossier de plan et une fiche pour chaque plan du lot, sans doublon ni manque, dans l'ordre |
| Contenu des dossiers | Chaque dossier de plan a au moins un JSON, ou un fichier `_reutilise.txt` / `_rien_a_generer.txt` ; chaque JSON annoncé « généré ici » dans une fiche existe dans l'archive, et inversement |
| Registre | Chaque famille du registre a **un seul** plan source et un seul JSON ; chaque « réutilise `PlanN/NN_nom` » d'une fiche pointe vers un JSON qui existe (dans l'archive ou dans un lot déjà livré) et que le registre prévoit ; aucun élément du registre n'est généré deux fois ; aucun élément visible d'un plan ne manque dans le registre |
| JSON | Chaque fichier est un JSON valide avec `nom`, `prompt` non vide et `references.depot` ; `nom` unique dans tout le projet |
| Références | Chaque `chemins` désigne un fichier **qui existe** dans le `Storyboard.zip` cloné, casse exacte, sans `* ? [ ]` ; la référence est bien l'image **du plan du dossier** (le plan source de l'élément) |
| Noms | Aucun nom de dossier ou de fichier ne contient `\ / : * ? " < > \|` |
| Détourage | Chaque prompt d'asset donne une couleur de détourage, qui n'apparaît pas dans les couleurs décrites de l'asset |
| Prompts | Chaque prompt d'asset contient : l'élément désigné, la couleur de détourage, « aplat », « sans ombre », « aucun texte » ; chaque prompt de fond contient la liste des éléments à retirer |
| Techniques | Chaque asset de chaque fiche porte une technique du registre, la même que dans le registre ; un asset décomposé a le même schéma (sous-assets, points d'attache, calques) dans tous ses plans |
| Feuilles de sprites | Chaque JSON `_sprites` contient la grille, le nombre d'images, « cellules de même taille » et la description de chaque image ; le nombre d'images décrites est égal à C × L (ou aux cellules utilisées) |
| Fiches de code | Chaque fiche `NN_nom_code.md` contient comportement, paramètres, position et taille, entrée et sortie, sortie attendue sur fond transparent, style ; **aucun JSON d'image n'existe** pour cet élément |
| Couverture visuelle | Chaque fiche de plan a la mention de couverture |

<a id="e9-17"></a>

### 9.17 · Validation

Le registre est livré **avant** le premier lot (voir la passe d'inventaire), mais **sans validation préalable** : tu enchaînes le registre, puis tous les lots, sans jamais attendre mon « ok ». Je relis chaque lot et je te signale ce qui doit changer, y compris les « Points à trancher » : tu mets alors à jour la fiche **et** le JSON concerné (et le registre si une réutilisation change), toujours identiques, sans changer les noms de fichiers. **Aucune image n'est générée par toi** : c'est moi qui lance la génération, à partir de l'archive.

---

<a id="e10"></a>

## Étape 10 : le dossier `AssetAnimation` et le projet ImGen des assets d'animation

Cette étape commence quand **tous les lots de l'étape 9 sont livrés** (les N plans sont « fait et livré » dans `asset_profond_status.md`). Le but : rassembler **tous les JSON de génération des lots dans un seul dossier**, rangé par plan comme le `Storyboard` l'est par séquence, puis générer **toutes les images d'assets d'animation avec ImGen**, chacune enregistrée **à côté de son JSON**, dans le dossier de son plan.

Cette étape ne change **rien** au contenu des JSON : leurs prompts et leurs références (l'image du plan, dans le dépôt `Storyboard`) sont ceux de l'étape 9, recopiés tels quels.

<a id="e10-1"></a>

### 10.1 · Ce que je te fournis

1. Les **`animation_lot_NN.zip`** (tous les lots, dans leur dernière version livrée). Si un lot a été corrigé après sa livraison, je te donne la version corrigée ; tu n'en utilises jamais une ancienne.
2. Plus tard, quand tu m'as livré `AssetAnimation.zip` : le **chemin réel** du dossier `AssetAnimation` sur mon ordinateur, après que je l'ai décompressé, et l'**arborescence réelle** de ce dossier, copiée telle quelle (première ligne : chemin absolu complet, emojis inclus ; une ligne par dossier ou fichier).

Comme à l'étape 8, **avant de créer le projet, tu me demandes toujours** l'arborescence réelle du dossier de références GitHub sur mon PC, au cas où je devrais générer des images à la main.

<a id="e10-2"></a>

### 10.2 · Ce que tu fais, première partie : le dossier `AssetAnimation`

1. **Tu décompresses les lots** (`animation_lot_01.zip` à `animation_lot_NN.zip`) dans ton espace de travail et tu notes leur nombre. Tu ne mélanges pas deux versions d'un même lot.
2. **Tu construis le dossier `AssetAnimation`** : à la racine, **un dossier `PlanN` par plan** (`Plan1` à `PlanN`, numérotation continue, aucun en trop, aucun manquant), et dans chacun **tout ce que le lot contenait pour ce plan, sans rien modifier ni renommer** : les JSON `NN_nom.json` (un par nouvelle génération), les fiches de code `NN_nom_code.md`, et `_reutilise.txt` ou `_rien_a_generer.txt` pour un plan sans nouvelle génération. Il n'y a **aucune image** dans l'archive : elles seront créées par ImGen, à côté des JSON. À la racine, **aucun autre fichier** : ni `Liste_assets_animation.md`, ni registre, ni statut.
3. **Tu contrôles par programme** avant de livrer :

| Contrôle | Ce que tu vérifies |
| --- | --- |
| Dossiers | Exactement N dossiers `Plan1` à `PlanN` ; aucun dossier de plan en double d'un lot à l'autre ; aucun dossier vide |
| JSON | Chaque fichier `.json` est valide, avec `nom`, `prompt` non vide et `references.depot` ; chaque `nom` est unique dans tout le projet et commence par `PlanN_` (N = le plan de son dossier) |
| Références | Chaque `chemins` désigne un fichier qui existe dans `Storyboard.zip` (dernière version du dépôt `Storyboard`), casse exacte, sans `* ? [ ]` |
| Fichiers | Tout fichier est un JSON, une fiche `NN_nom_code.md`, `_reutilise.txt` ou `_rien_a_generer.txt` ; rien d'autre ; le nombre total de fichiers est égal à la somme de ceux des lots |
| Zip | `AssetAnimation.zip` s'ouvre sans erreur (`testzip`) et contient un dossier racine `AssetAnimation/` |

4. **Tu livres `AssetAnimation.zip`** (dossier racine `AssetAnimation/` à l'intérieur du zip) avec un bilan court : nombre de plans, de JSON (donc d'images à générer), de fiches de code, de plans sans nouvelle génération. **Pas de script d'envoi, pas de push GitHub** : l'archive n'a pas besoin d'être sur GitHub, seul `Storyboard` doit y rester.

<a id="e10-3"></a>

### 10.3 · Ce que je fais

Je décompresse `AssetAnimation.zip` dans mon projet (à côté de `Storyboard` et `Assets`) et je te donne le chemin réel et l'arborescence de `AssetAnimation`.

<a id="e10-4"></a>

### 10.4 · Ce que tu fais, deuxième partie : `projet_imgen_assets.json`

À partir du chemin réel, tu écris **un seul fichier JSON**, `projet_imgen_assets.json`, au même format que le `projet_imgen.json` de l'étape 8 (`projet`, puis `images`). **Une image par fichier JSON de génération**, donc pas une par plan :

| Champ | Contenu |
| --- | --- |
| `projet` | Un nom court (par exemple `6-musk_starlink_assets_animation`). ImGen refuse un nom de projet déjà existant, et il doit différer de celui de l'étape 8. |
| `nom` | Le `nom` du JSON de génération, **recopié tel quel** (il est unique dans tout le projet). |
| `chemin_sauvegarde` | `<chemin réel de AssetAnimation>/PlanN/<nom du fichier JSON sans .json>.webp`, écrit avec des `/`, emojis du chemin recopiés tels quels (le JSON est collé dans ImGen : pas de codes `\U`). L'image est donc **à côté de son JSON**, sous le même nom. |
| `prompt` | Le `prompt` du JSON de génération, **identique**, sans le modifier. |
| `references` | Le `references` du JSON de génération, **identique** (l'image du plan, en `depot`, dans le dépôt `Storyboard`). Aucune référence locale. |

Règles :

- **Ordre** : par numéro de plan, puis par numéro de fichier (`01_`, `02_`…). Il n'y a **pas de vagues** : chaque génération part de l'image de son plan dans `Storyboard` et ne dépend d'aucune autre image à générer. Tu ne crées donc ni vague ni dépendance.
- **Aucune image pour** les fiches `NN_nom_code.md`, `_reutilise.txt` et `_rien_a_generer.txt` : un élément en code et un élément réutilisé ne se génèrent pas.
- **Dépôt** : tant qu'ImGen génère, le dépôt `Storyboard` doit contenir le `Storyboard.zip` à jour ; je ne pousse rien d'autre dans ce dépôt pendant ce temps.
- **Limites** : au plus 10 références par image (ici une seule), 10 Mo par fichier.
- **Extension** : `.webp`, comme à l'étape 8 (le bot enregistre en WebP).

<a id="e10-5"></a>

### 10.5 · Ce que tu contrôles avant de livrer le JSON

| Contrôle | Ce que tu vérifies |
| --- | --- |
| Nombre | Autant d'images dans le projet que de fichiers `.json` dans `AssetAnimation` ; aucun nom en double |
| ImGen | Le JSON passe `parse_project_text` d'ImGen sans erreur ; tu donnes les avertissements attendus |
| Chemins de sauvegarde | Chaque `chemin_sauvegarde` est sous le chemin réel de `AssetAnimation`, dans le dossier du bon plan, avec le nom du fichier JSON et l'extension `.webp` ; aucun doublon |
| Identité | Chaque `prompt` et chaque `references` sont identiques à ceux du JSON de génération d'origine (comparaison par programme) |
| Dépôt | Chaque `chemins` existe dans le `Storyboard.zip` cloné, casse exacte |

Tu livres **`projet_imgen_assets.json`** (fichier complet, jamais tronqué) avec une consigne courte : « dans ImGen, clique sur **+**, colle le contenu du fichier ». Puis un bilan : nombre d'images, répartition par lot, avertissements attendus.

<a id="e10-6"></a>

### 10.6 · Premier essai

Avant de lancer toutes les images, je génère **la première image du `Plan1`, puis celle du `Plan2`** : je vérifie que la référence est bien reçue, que l'image est enregistrée à côté de son JSON, avec le bon nom, et que le fond est bien détourable (aplat vert, sans ombre). Si un prompt est à corriger, tu me livres le JSON de génération corrigé, le `projet_imgen_assets.json` mis à jour (identiques), et, si l'image est déjà générée, le `reinitialisation_imgen.html` de l'étape 9.


**Étape suivante : l'étape 11 (re-vérification).** Quand toutes les images d'assets d'animation sont générées par ImGen, on passe à la re-vérification : on envoie les images sur GitHub et tu les contrôles.

---

<a id="e11"></a>

## Étape 11 : re-vérifier les assets d'animation générés

Cette étape commence quand **toutes les images de `projet_imgen_assets.json` sont générées** par ImGen (étape 10). Le but : envoyer toutes les images dans un dépôt dédié, **`Assets_Animation`** (`https://github.com/officecenter632-maker/Assets_Animation`, branche `main`), puis les contrôler pour trouver celles dont la **génération est grave**, à regénérer. Ce dépôt est indépendant de `ImageReferenceData` et de `Storyboard` : il ne touche à aucun des deux. Comme eux, il ne garde **qu'un seul zip et un seul commit** : un nouvel envoi remplace le précédent.

<a id="e11-1"></a>

### 11.1 · Ce que je fais : te donner l'arborescence

1. Je t'envoie l'**arborescence réelle** du dossier qui contient tous les assets d'animation générés (le dossier `AssetAnimation` de l'étape 10, avec ses images à côté des JSON), copiée telle quelle depuis mon ordinateur : la première ligne donne le **chemin absolu complet** du dossier, chaque ligne le **nom exact** d'un dossier ou d'un fichier.
2. **Si je ne l'ai pas encore envoyée, tu me la demandes** avant d'écrire quoi que ce soit. Tu n'écris jamais un chemin de mémoire.
3. Je te dis aussi comment je m'authentifie auprès de GitHub (`git` déjà connecté, ou jeton), comme pour `envoyer_storyboard.py`.

<a id="e11-2"></a>

### 11.2 · Ce que tu fais, première partie : le script d'envoi

Tu m'écris **un seul script Python** (`envoyer_assets_animation.py`) qui **archive** le dossier et le **pousse** dans le dépôt `Assets_Animation`. Même règle d'or qu'à l'étape 9 : **tu ne le réécris pas de zéro**. Tu pars du modèle `envoyer_storyboard.py` (déjà testé : contrôle de structure, un seul zip, dépôt neuf, un seul commit, push forcé, vérification de la branche distante, jeton jamais affiché) et tu ne changes que ce que ma situation impose : le chemin du dossier (copié de la première ligne de mon arborescence), le nom du zip, le dépôt, les contrôles de structure. Mêmes règles d'écriture : il s'exécute n'importe où, se lance depuis un éditeur sans argument ni question, tu le **testes** avant de me le donner, et tu le livres dans un seul bloc de code.

**Ce qu'il archive** : les images générées (`.webp`) et les JSON de génération de chaque dossier `PlanN` (pour comparer chaque image à son prompt). Il liste dans le bilan tout fichier exclu. Avant tout envoi, il vérifie que **chaque JSON a son image** ; en cas d'écart (image manquante), il l'affiche et n'envoie rien, sauf si je force.

Je le lance depuis mon éditeur et je te dis que c'est fait.

<a id="e11-3"></a>

### 11.3 · Ce que tu fais, deuxième partie : le checkup

1. Tu **télécharges le zip** depuis le dépôt `Assets_Animation` et tu **gardes la copie** dans ton espace de travail.
2. **Structure (par programme)** : le zip s'ouvre sans erreur (`testzip`), chaque JSON a son image et inversement, aucun doublon, aucun manque par rapport à `projet_imgen_assets.json`.
3. **Images suspectes (par programme)** : image illisible, entièrement noire ou blanche, minuscule, aplat uni sans contenu. Aucune n'est écartée en silence.
4. **Images (à l'œil)** : tu regardes **chaque image** et tu la compares à son prompt. Une **génération grave** (à regénérer) est : image manquante ou illisible, noire, blanche ou vide, **sans rapport avec son prompt**, **fond non détourable** (pas un aplat vert uni), élément principal **absent ou coupé**, **texte ou logo dessiné**. **Une image n'a pas besoin d'être parfaite** : un fil ou une manche qui touche le bord, un petit détail imparfait ne sont **pas** des défauts graves. Tu **ne les signales pas** et tu **n'en parles pas** : tu ne noies pas l'utilisateur sous des défauts mineurs.
5. Tu me rends un **bilan court, limité aux générations graves** : un tableau `Plan | Image | Problème | Action` (à regénérer) **uniquement** pour les images graves. S'il n'y en a aucune, tu écris simplement « aucune génération grave : les assets sont prêts pour la vectorisation » ; **pas de liste d'images acceptables, pas de remarques de détail**. **Dans la même réponse**, si des images sont à regénérer, tu me livres directement **`reinitialisation_imgen.html`** (étape 9, **avec sa structure imposée et la règle du bouton « Copier »**) pour le projet ImGen des assets, sans que je le demande. Les noms à réinitialiser sont ceux du champ `nom` de chaque JSON de génération (par exemple `Plan23_01_silhouettes_costume_face`), pas le nom du fichier du plan. Tu ne modifies rien toi-même : je regénère, je relance le script (il repousse tout seul), et tu recontrôles seulement ces images ; une image regénérée est **validée** dès qu'elle n'a plus de défaut grave (pas de seconde passe sur les détails).

**Étape suivante : l'étape 12 (vectorisation).** Quand plus aucune génération grave ne reste, on passe à la vectorisation des assets.


<a id="e12"></a>

## Étape 12 : vectoriser les assets d'animation

Cette étape commence quand **l'étape 11 est terminée** : plus aucune image d'asset d'animation n'a de génération grave (les images regénérées ont été validées et le dépôt `Assets_Animation` est à jour). Le but : **vectoriser** les assets d'animation validés avec **`GenSVG.pyw`**, l'application qui gère une file de SVG à générer à partir d'images sources (même principe qu'ImGen : je colle un JSON avec le bouton **« + »**, des bots prennent les lignes une à une).

<a id="e12-1"></a>

### 12.1 · Ce que je te fournis

1. L'**arborescence réelle** du dossier `AssetAnimation` sur mon ordinateur, **avec les images générées à côté des JSON** (étapes 10 et 11), copiée telle quelle : première ligne = **chemin absolu complet** (emojis inclus), une ligne par dossier ou fichier.
2. **Si je ne te l'ai pas encore donnée, tu me la demandes avant d'écrire quoi que ce soit.** Tu n'écris jamais un chemin de mémoire, et tu ne réutilises pas une arborescence d'une autre étape sans me demander si elle est toujours à jour.

<a id="e12-2"></a>

### 12.2 · Ce que GenSVG attend

Un JSON que je colle dans GenSVG (bouton **« + »**, « Nouveau projet »). GenSVG le valide, crée le projet (dossier `ProjetsSVG`) et affiche un tableau : **une ligne = un SVG à générer**. Le projet est distinct de ceux d'ImGen.

```
{
  "projet": "nom du projet",
  "images": [
    {
      "nom": "nom court et unique",
      "chemin_sauvegarde": "chemin complet du .svg à produire",
      "source": {"depot": {"url": "https://github.com/officecenter632-maker/Assets_Animation", "branche": "main", "chemin": "chemin de l'image vu dans le zip du dépôt"}}
    }
  ]
}
```

Règles du validateur (`parse_project_text` de GenSVG) :

- `source` est **obligatoire** et c'est **un seul chemin** : soit `{"local": "..."}`, soit `{"depot": {...}}`, **jamais les deux**. Ici on utilise **toujours `depot`** : le bot clone le dépôt `Assets_Animation` (`https://github.com/officecenter632-maker/Assets_Animation`, branche `main`) et prend l'image dans le zip. **Jamais `local`** pour la source.
- La source est une image : `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif` ou `.bmp`. Nos assets sont en **`.webp`**.
- `chemin_sauvegarde` **finit par `.svg`**. S'il est omis, GenSVG range le SVG dans `outputs/<nom>.svg` du dossier du projet : on ne l'omet **pas**.
- Chaque `nom` est **unique** (sans tenir compte de la casse) ; le chemin local est écrit avec des `/`.
- Un champ manquant ou invalide (dépôt, chemin, extension) donne une erreur.

<a id="e12-3"></a>

### 12.3 · Ce que tu fais : `projet_gensvg.json`

À partir du chemin réel, tu écris **un seul fichier JSON**, `projet_gensvg.json`. **Une ligne par image d'asset générée** (donc une par fichier `.webp` de `AssetAnimation`) :

| Champ | Contenu |
| --- | --- |
| `projet` | Un nom court (par exemple `6-musk_starlink_assets_svg`). GenSVG refuse un nom de projet déjà existant. |
| `nom` | Le `nom` du JSON de génération (par exemple `Plan23_01_silhouettes_costume_face`), **recopié tel quel**. Il est unique dans tout le projet. |
| `source.depot` | `url` du dépôt `Assets_Animation`, `branche` `main`, et `chemin` = le chemin de l'image **tel qu'il est dans le zip du dépôt**, par exemple `AssetAnimation/Plan23/01_silhouettes_costume_face.webp`. **Tu télécharges le dépôt et tu lis le contenu du zip** : tu n'écris jamais ce chemin de mémoire. |
| `chemin_sauvegarde` | Le chemin **sur mon PC**, `<chemin réel de AssetAnimation>/PlanN/<nom>.svg`, écrit avec des `/`, emojis recopiés tels quels (le JSON est collé dans GenSVG : pas de codes `\U`) : le SVG est **à côté de l'image et du JSON**, sous le même nom. C'est le seul chemin local du projet. |

Règles :

- **Ordre** : par numéro de plan, puis par numéro de fichier (`01_`, `02_`…). Il n'y a **pas de dépendance** entre les lignes : chaque SVG part de son image.
- **Aucune ligne** pour les fiches `NN_nom_code.md`, `_reutilise.txt` et `_rien_a_generer.txt` : un élément en code ou réutilisé ne se vectorise pas.
- **Les images à vectoriser sont celles du zip du dépôt `Assets_Animation`** (une ligne par `.webp` du zip, avec le `nom` lu dans son JSON). Tant que ce dépôt contient le zip à jour, je ne pousse rien d'autre dedans.
- Tu ne changes **ni les noms ni les dossiers** : `nom` est celui de l'étape 10.

<a id="e12-4"></a>

### 12.4 · Ce que tu contrôles avant de livrer le JSON

| Contrôle | Ce que tu vérifies |
| --- | --- |
| Nombre | Autant de lignes que d'images `.webp` dans l'arborescence ; aucun nom en double |
| GenSVG | Le JSON passe `parse_project_text` de GenSVG (`GenSVG.pyw` s'importe sans interface) **sans erreur** ; aucun avertissement n'est attendu |
| Chemins | Chaque `depot.chemin` désigne un fichier **existant dans le zip cloné** (casse exacte, aucun `* ? [ ]`) ; chaque `chemin_sauvegarde` est sous le chemin réel de `AssetAnimation`, dans le bon dossier de plan, en `.svg` ; aucun doublon ; **aucune source `local`** |
| Identité | Chaque `nom` est identique à celui du JSON de génération d'origine (comparaison par programme) |

Tu livres **`projet_gensvg.json`** (fichier complet, jamais tronqué) avec une consigne courte : « dans GenSVG, clique sur **+**, colle le contenu du fichier ». Puis un bilan court : nombre de lignes, répartition par plan, avertissements attendus.

<a id="e12-5"></a>

### 12.5 · Premier essai

Avant de lancer toutes les lignes, je vectorise **la première image du `Plan1`, puis celle du `Plan2`** : je vérifie que le SVG est enregistré à côté de l'image, sous le bon nom, et qu'il ressemble à l'image. Si un chemin est à corriger, tu me livres le JSON corrigé (les noms ne changent jamais).

**Règle qui vaut pour toute l'étape : tu ne me signales pas les défauts mineurs.** Seules les erreurs graves (SVG manquant, vide, sans rapport avec l'image, élément principal absent ou faux) méritent d'être remontées. Les SVG n'ont pas besoin d'être parfaits.

**Étape suivante : l'étape 13 (archive de données pour l'animation).**

---

> **Phase 6 – Archive, audio et animation (étapes 13, 13 bis et 14)**

<a id="e13"></a>

## Étape 13 : l'archive de données pour l'animation

Cette étape commence quand **l'étape 12 est terminée** : tous les assets d'animation sont vectorisés, un `.svg` à côté de chaque `.webp`. Le but : rassembler dans **un seul zip, `AnimationData.zip`, toutes les données dont tu as besoin pour écrire l'animation plan par plan**, et le pousser dans un dépôt dédié, **`ShaderiaxAnim`** (`https://github.com/officecenter632-maker/ShaderiaxAnim`, branche `main`, à créer s'il n'existe pas). Comme les autres dépôts, il ne garde **qu'un seul zip et un seul commit** : un nouvel envoi remplace le précédent. Il est indépendant de `ImageReferenceData`, `Storyboard` et `Assets_Animation`. **Le zip s'appelle `AnimationData.zip` et le dépôt `ShaderiaxAnim` : ce ne sont pas le même nom.** Le lien direct est `https://github.com/officecenter632-maker/ShaderiaxAnim/raw/main/AnimationData.zip`.

**L'animation ne passe par aucun logiciel externe.** Elle est faite **directement en web** (HTML, CSS, JavaScript), **par toi**, et **tu me montres le rendu toi-même dans la conversation** (étape 14). L'archive ne contient donc que les **données** du projet.

**Cette étape ne produit aucun code d'animation.** Elle prépare seulement l'archive. L'animation elle-même est l'étape suivante (étape 14, écrite plus bas) : tu clones le dépôt, tu lis le scénario, puis tu animes **plan par plan, progressivement**, et tu me montres chaque plan en page web pour que je te dise si tout est bon.

**Hors périmètre pour l'instant : le montage** (logo de la chaîne, police des cartons, étiquettes de date, de lieu et de source, badges, cartons de texte). L'archive ne contient donc pas de dossier `montage`. **En revanche, elle contient l'audio généré de chaque plan** (dossier `audio/`, voir plus bas) : l'audio est généré à l'étape 13 bis, donc **l'archive est d'abord poussée sans audio, puis repoussée avec l'audio** quand l'étape 13 bis est terminée (le nouvel envoi remplace le précédent). Les consignes de montage qui figurent dans les fiches restent dans les fiches, mais ne sont pas animées. On se concentre sur **l'animation des assets dans chaque plan**.

<a id="e13-1"></a>

### 13.1 · Principe : l'archive contient TOUT ce qu'il faut pour animer

**Rien ne doit manquer.** L'IA qui anime ne doit **jamais** avoir à me demander un fichier, un texte ou une explication : tout ce qui décrit le projet est dans l'archive. Elle contient donc : le **scénario** et le texte de **chaque plan** (voix off, ce que le plan représente, ce qui est fait au montage), la liste des assets et les consignes de montage, les **prompts** de chaque asset, les images (`.svg` et `.webp` des assets, images du storyboard, images brutes), les fiches de code et la **procédure de travail** (`Director.md`).

- **Si l'IA a besoin d'un fichier qui n'est pas dans l'archive, c'est un défaut du script d'envoi** : elle ne me le demande pas, elle le signale en une phrase, corrige `envoyer_animation.py` pour qu'il l'inclue, et je relance le script.
- **Le script n'omet rien en silence** : il affiche dans son bilan **chaque fichier ou dossier du projet qui n'est pas envoyé, avec la raison**, et il **parcourt toute la racine du projet** (`AssetAnimation`, `Assets`, `Meta`, `Storyboard` et tout le reste). Un fichier d'un type inattendu dans `Meta/` ou `Storyboard/` est lui aussi listé, jamais ignoré.
- **Seules exclusions admises**, toutes listées dans le bilan : les fichiers `.part*` (téléchargements interrompus) ; les fichiers de suivi du travail (`asset_profond_status.md`, `Images_deja_validees_NE_PAS_RETRIER.md`) ; les images de référence Lexiax (`reference*.webp`), qui ne servent pas à animer ; les copies `.png` rangées dans `Assets/assets/<asset>/` et `Assets/assetsBrute1.zip` (les mêmes images sont déjà dans `assets_base/images/`) ; le dossier `Animation/` s'il existe encore (ancien projet d'un outil abandonné : il n'est **jamais** envoyé) ; les anciens zip d'envoi à la racine du projet (`AnimationData.zip`, `AssetAnimation.zip`, `Assets_Animation.zip`, `Storyboard.zip`) ; tout fichier **texte** (scénario, prompts, directives, assets de base) où le **garde-fou des secrets** trouve un identifiant : il est exclu et listé, sans bloquer l'envoi ; le montage (hors périmètre, mais **ses consignes restent dans les fiches et les `PlanN.txt`**) ; **l'audio n'est jamais exclu** : il part dans `audio/` ; et, **seulement si le total dépasse le plafond de 60 Mo d'images**, les images les moins utiles (d'abord les images brutes `assetsBrute1`, jamais les SVG), listées une à une.

<a id="e13-2"></a>

### 13.2 · Ce que je te fournis

1. L'**arborescence réelle** du projet sur mon ordinateur, copiée telle quelle : première ligne = **chemin absolu complet** (emojis inclus), une ligne par dossier ou fichier. Elle doit montrer `AssetAnimation` avec ses `.svg`, `Storyboard`, et l'emplacement des fichiers `.md` de directives. **Si je ne te l'ai pas donnée, ou si tu doutes qu'elle soit à jour, tu me la demandes** : tu n'écris jamais un chemin de mémoire.
2. Mes **décisions sur les points à trancher** des fiches (section 8 de chaque plan de `Liste_assets_animation.md`, et section F du registre). Sans réponse de ma part, tu appliques la **lecture par défaut** indiquée dans chaque fiche, et tu le notes dans le `README.md`.
3. Comment je m'authentifie auprès de GitHub (`git` déjà connecté, ou jeton), comme pour `envoyer_storyboard.py`.

<a id="e13-3"></a>

### 13.3 · Ce que contient `AnimationData.zip`

Un seul dossier racine, `AnimationData/`, avec :

| Dossier ou fichier | Contenu | Origine |
| --- | --- | --- |
| `assets/PlanN/` | Les **N dossiers** `Plan1` à `PlanN`, avec les **`.svg`**, les fiches de code `NN_nom_code.md`, et les fichiers `_reutilise.txt` / `_rien_a_generer.txt`, **recopiés sans modification** | `AssetAnimation` |
| `directives/` | `Liste_assets_animation.md` (positions, calques, animations, chronologies), `Registre_elements_animation.md` (réutilisations et retouches), `Sequences.md` (durées), `Plan_animation.md` (**le scénario complet** : charte et palette, arbitrages, les 9 parties plan par plan avec voix off, visuel et caméra, texte à l'écran, couleur, annexes), **`Liste_assets.md`** (la liste des assets de base et les consignes de montage), **`Director.md`** (la procédure de travail) et **tout autre `.md` de `Meta/`**, sauf les fichiers de suivi | `Meta/` |
| `storyboard/` | Les **N images de plan** (`.webp`), rangées par séquence : elles servent de modèle visuel pour vérifier chaque animation | `Storyboard` |
| `scenario/` | `Sequences.md` du Storyboard et, pour chaque `sequenceN/`, **`speech.txt`** (la voix off mot pour mot) et **tous les `PlanN.txt`** (N) : identité du plan, voix off, **ce que le plan représente**, composition, **« FAIT AU MONTAGE »**. Ce sont les textes qui disent **comment chaque plan a été pensé** | `Storyboard/sequenceN/` |
| `prompts_assets/PlanN/` | Les **JSON de génération** de chaque asset (`nom`, `prompt`, `references`) : ce que l'asset est censé montrer | `AssetAnimation/PlanN/*.json` |
| `assets_images/PlanN/` | Les **`.webp`** d'origine des assets : modèle pour juger la vectorisation | `AssetAnimation/PlanN/*.webp` |
| `assets_base/` | `index.csv`, `prompts/<asset>/prompt.txt` (le prompt de chaque asset de base et de chaque planche) et `images/*.png` (les images brutes `assetsBrute1`, planches de poses comprises) | `Assets/` |
| `audio/sequenceN/` | **L'audio généré de chaque plan parlé** : `PlanN.<extension>` (P fichiers, un par plan parlé ; **un plan sans voix off n'a pas d'audio**), **recopiés sans modification**, avec leur **extension réelle** (`.wav`, `.mp3`… : AudioGen détecte le vrai format). **Un fichier par plan** | `Audio/sequenceN/` (étape 13 bis) |
| `README.md` | L'index de l'archive, les conventions et les décisions (voir plus bas) | Toi |
| `manifest.json` | La liste, plan par plan, des fichiers de l'archive avec leur taille (voir « `manifest.json` »), générée par le script | Script |

**Exclus** : uniquement ce que liste le « Principe » ci-dessus, **chaque exclusion étant affichée dans le bilan du script avec sa raison**. Les `.webp` des assets **ne sont plus exclus** (ils sont dans `assets_images/`, dans la limite du plafond de 60 Mo d'images), les JSON de génération non plus (`prompts_assets/`), ni `Liste_assets.md`.

<a id="e13-4"></a>

### 13.4 · Où est le dossier `AssetAnimation` dans le dépôt `ShaderiaxAnim` ?

**Nulle part : on ne crée aucun dossier `AssetAnimation` dans le dépôt.** Ce nom n'existe que **sur mon ordinateur** (étapes 10 à 12) et dans le dépôt `Assets_Animation`. Dans `ShaderiaxAnim`, **le script `envoyer_animation.py` ne crée rien à la racine** : le dépôt ne contient que **`AnimationData.zip`** (un seul fichier, un seul commit). Le contenu de `AssetAnimation` est **réparti à l'intérieur du zip**, sous le dossier racine `AnimationData/`, **sans que le nom `AssetAnimation` y apparaisse**. Correspondance :

| Sur mon ordinateur (projet) | Dans le zip (`AnimationData/…`) | Dans ton clone, après `unzip` |
| --- | --- | --- |
| `AssetAnimation/PlanN/*.svg`, `*_code.md`, `_reutilise.txt`, `_rien_a_generer.txt` | `assets/PlanN/` | `AnimationData/assets/PlanN/` |
| `AssetAnimation/PlanN/*.json` | `prompts_assets/PlanN/` | `AnimationData/prompts_assets/PlanN/` |
| `AssetAnimation/PlanN/*.webp` | `assets_images/PlanN/` | `AnimationData/assets_images/PlanN/` |

Le dépôt, vu de l'extérieur, ressemble donc à :

```
ShaderiaxAnim/            (dépôt GitHub, branche main)
└── AnimationData.zip     (le seul fichier du dépôt)
        └── AnimationData/          (dossier racine du zip)
            ├── assets/Plan1 … PlanN
            ├── assets_images/Plan1 … PlanN
            ├── prompts_assets/Plan1 … PlanN
            ├── directives/  storyboard/  scenario/  assets_base/
            ├── README.md
            └── manifest.json
```

**Conséquence pour l'étape 14 :** le dossier `AssetAnimation/PlanN` est un chemin **du projet sur mon ordinateur** (il n'est pas dans `projet_animation.json`) ; **dans ton clone du dépôt `ShaderiaxAnim`**, le même dossier est **`AnimationData/assets/PlanN/`**. Tu ne cherches jamais un dossier `AssetAnimation` dans le clone : tu ouvres chaque fichier avec le `chemin_relatif` du `manifest.json`. **Cette étape 13 n'est validée que si le contrôle de l'archive confirme que `AnimationData/assets/Plan1` à `PlanN` existent dans le zip téléchargé.**

**Le `README.md`** que tu rédiges donne, en une page : l'ordre de lecture des fichiers ; les conventions (image de **1672×941**, positions en % de la largeur (x) et de la hauteur (y), taille en % de la hauteur, rotation en degrés dans le sens horaire, calques du fond vers le devant, noms de fichiers `NN_nom` ; les SVG gardent leur fond de détourage vert ou magenta, retiré dans le code d'animation) ; où trouver l'**audio** de chaque plan (`audio/sequenceN/PlanN.<ext>`, à **intégrer directement dans la page HTML** à l'étape 14) ; où lire le scénario (`directives/Plan_animation.md` = le scénario complet, `scenario/` = voix off et texte de chaque plan) et où trouver les prompts, les images d'origine et les assets de base ; comment lire un `_reutilise.txt` (il renvoie à `PlanN/NN_nom`, avec la retouche à appliquer) ; les **dépendances entre plans** (un plan qui réutilise un asset d'un autre plan) ; les techniques 1 à 6 du registre ; **comment utiliser `manifest.json`** ; et la liste de mes **décisions** sur les points à trancher.

<a id="e13-5"></a>

### 13.5 · `manifest.json` : retrouver chaque fichier

**But : tu retrouves n'importe quel fichier de l'archive sans me demander le moindre chemin.** Tu travailles sur le clone du dépôt, dans ton espace de travail ; le `manifest.json` dit, pour chaque fichier, où il est dans l'archive. **Aucun chemin de mon PC n'est nécessaire** : le rendu se fait chez toi, dans la conversation.

**Le script `envoyer_animation.py` écrit le manifest lui-même.** Il connaît le chemin absolu du projet (constante `PROJET`, copiée de mon arborescence) et construit chaque entrée à partir des fichiers **réellement présents** sur mon disque. Tu n'écris aucun chemin à la main dans le manifest.

**Structure imposée du `manifest.json`** (JSON UTF-8, `ensure_ascii=False`) :

> **Modèle : voir [Annexe A6](#annexe-a6) (en fin de document).**

- **Tous les fichiers de `assets/PlanN/`** y figurent (SVG, fiches `NN_nom_code.md`, `_reutilise.txt`, `_rien_a_generer.txt`), avec le champ `type` (`svg`, `code`, `reutilise`, `rien`). **Chaque SVG a obligatoirement** `chemin_zip`, `chemin_relatif` et `taille`. Les N images du storyboard ont leur `chemin_relatif`. **Les P audios** (les `PlanN` des plans parlés) figurent dans la clé **`audio`**, avec `fichier`, `taille`, `chemin_zip` et `chemin_relatif` ; les plans sans voix off n'y sont pas.
- **Tous les autres fichiers de l'archive** figurent dans la liste **`fichiers_supplementaires`** du manifest : une entrée `{groupe, fichier, chemin_zip, chemin_relatif, taille}` par fichier (`groupe` = `directives`, `scenario`, `prompts_assets`, `assets_images` ou `assets_base` ; les audios, eux, sont dans la clé `audio`).
- **Tous les chemins s'écrivent avec des `/`.**
- **Le script vérifie, avant tout envoi**, que chaque fichier cité existe sur mon disque, que sa taille est la même dans le zip, et que `chemin_relatif` et `chemin_zip` désignent le même fichier. En cas d'écart, il l'affiche et n'envoie rien (sauf si je force).

**Comment tu t'en sers (étape 14).** Tu ne me demandes jamais un chemin : tu ouvres chaque fichier dans ton clone avec `chemin_relatif`. Si un chemin manque ou ne mène à rien, c'est un défaut de l'archive : tu me le signales en une phrase, tu ne me demandes pas de te le dicter.

<a id="e13-6"></a>

### 13.6 · Ce que tu fais, première partie : le script d'envoi

Tu m'écris **un seul script Python** (`envoyer_animation.py`) qui **assemble l'archive et la pousse** dans le dépôt `ShaderiaxAnim`. **Je n'ai jamais à copier ou à ranger un fichier à la main.** Même règle d'or qu'aux étapes 9 et 11 : **tu ne le réécris pas de zéro**. Tu pars du modèle `envoyer_storyboard.py` (déjà testé : contrôle de structure, un seul zip, dépôt neuf, un seul commit, push forcé, vérification de la branche distante, jeton jamais affiché) et tu ne changes que ce que ma situation impose : les chemins (copiés de mon arborescence), le contenu du zip, le nom du zip, le dépôt, les contrôles de structure. Mêmes règles d'écriture : il s'exécute n'importe où, se lance depuis un éditeur sans argument ni question, tu le **testes** avant de me le donner, et tu le livres dans un seul bloc de code.

**Contrôles du script avant tout envoi** (en cas d'écart, il l'affiche et n'envoie rien, sauf si je force) :

| Contrôle | Ce qu'il vérifie |
| --- | --- |
| Plans | Les N dossiers `Plan1` à `PlanN` existent dans `assets/` |
| Vectorisation | Chaque `.webp` de `AssetAnimation` a son `.svg`, de même nom, dans le même dossier |
| SVG lisibles | Chaque `.svg` n'est pas vide, est du XML bien formé et contient une balise `<svg>` avec `viewBox` ou dimensions |
| Fichiers parasites | Aucun fichier `.part*` ne part dans le zip |
| Storyboard | Les N images de plan sont présentes |
| Audio | **Si le dossier `Audio` de mon projet contient des audios** : il y a **un fichier `PlanN` pour chacun des plans parlés** (extension audio quelconque), aucun fichier vide, aucun doublon pour un même plan, et chaque audio est dans `audio/sequenceN/` du zip avec la même taille que sur mon disque. **S'il manque des audios, le script l'affiche, plan par plan, et n'envoie rien (sauf si je force).** **Si le dossier `Audio` n'existe pas encore** (premier envoi, avant l'étape 13 bis), il l'indique dans le bilan (« audio pas encore généré ») et l'envoi a lieu quand même, **mais l'étape 14 ne commence pas avant le second envoi, avec l'audio**. Le script affiche aussi la **taille totale du zip** : au-delà de la limite de 100 Mo par fichier de GitHub, il le signale et n'envoie rien |
| Documents | Tous les `.md` retenus de `directives/` (au moins les quatre documents d'animation, `Liste_assets.md` et `Director.md`) et le `README.md` sont présents |
| Complétude | `Storyboard/` a **S séquences**, `scenario/` contient **S `speech.txt` et N `PlanN.txt`** (un fichier exclu par le garde-fou crée donc un écart) ; `prompts_assets/` a **un JSON par SVG** ; `directives/` contient `Liste_assets.md` et `Director.md` ; `assets_base/` a un `prompt.txt` par asset de base. Le bilan affiche **tout ce qui n'est pas envoyé, avec la raison** |
| Secrets | **Garde-fou, voir ci-dessous** : aucun identifiant, jeton, mot de passe ou clé n'est détecté dans les textes ajoutés |
| Chemins du manifest | Chaque fichier de `assets/` et chaque image du storyboard a son entrée dans `manifest.json` avec `chemin_zip` et `chemin_relatif` ; chaque SVG du zip a son entrée, et inversement ; **chaque fichier de `fichiers_supplementaires` existe sur mon disque, dans le zip, avec la même taille**, et inversement |

**Garde-fou des secrets (obligatoire, avant tout envoi).** Le dépôt `ShaderiaxAnim` est **public** : tout ce qui y est poussé est lisible par tout le monde et reste dans l'historique de GitHub même après suppression. Le script **analyse donc tous les textes ajoutés avant le zip** (`scenario/`, `prompts_assets/`, `directives/`, `assets_base/`) : jetons (`ghp_`, `github_pat_`, `sk-`, `AKIA`, `xox`…), et toute affectation d'un nom contenant `token`, `password`, `passwd`, `secret`, `api_key`, `apikey`, `authorization` ou `credential` à un texte long non vide. Le **fichier concerné est exclu** et listé dans le bilan (fichier, numéro de ligne et nom de la variable, **jamais la valeur**) ; le reste part. **`FORCER` ne contourne pas ce garde-fou** : un secret n'est jamais poussé sur un dépôt public. Si des identifiants ont déjà été poussés dans un envoi précédent, tu me le dis tout de suite en une phrase, pour que je les révoque : les supprimer du dépôt ne suffit pas.

Je le lance depuis mon éditeur et je te dis que c'est fait.

<a id="e13-7"></a>

### 13.7 · Ce que tu fais, deuxième partie : le contrôle de l'archive

1. Tu **télécharges le zip** depuis le dépôt `ShaderiaxAnim` et tu **gardes la copie** dans ton espace de travail.
2. **Structure (par programme)** : le zip s'ouvre sans erreur (`testzip`), les N dossiers de plan sont là **dans `AnimationData/assets/`** (et non dans un dossier `AssetAnimation`), le nombre de SVG correspond au nombre de générations d'images (75 au registre), aucun doublon ; `scenario/` contient S `speech.txt` et N `PlanN.txt`, `prompts_assets/` un JSON par SVG, `directives/` tous les `.md` de `Meta/` retenus.
   **Audio (par programme, après le second envoi)** : `audio/` contient les **P audios** (les `PlanN` des plans parlés), chacun lisible (taille non nulle, format reconnu), chacun cité dans la clé `audio` du manifest avec la même taille ; un audio manquant est un défaut de l'archive.
   **Manifest (par programme)** : `manifest.json` est un JSON valide ; **chaque SVG du zip** y figure avec `chemin_zip`, `chemin_relatif` et `taille`, et chaque `chemin_zip` existe dans le zip, avec la même taille ; aucun chemin ne contient `\` ni `*?"<>|`.
3. **Références (par programme)** : chaque asset cité dans `Liste_assets_animation.md` existe dans `assets/`, et chaque « réutilise `PlanN/NN_nom` » ou « Origine » désigne un fichier qui existe dans l'archive.
4. **SVG (par programme, puis à l'œil)** : tu **rends chaque SVG en image** et tu cherches les SVG vides ou illisibles. **Le fond vert `#00FF00` ou magenta `#FF00FF` des SVG n'est PAS un défaut** : les SVG ne sont pas détourés, et c'est **toi** qui retires ce fond (le premier `<path>` plein cadre) **dans l'animation**, plan par plan. Tu ne le signales donc pas dans le bilan. Tu ne regardes à l'œil que les SVG suspects, en les comparant à l'image du plan dans `storyboard/`.
5. Tu me rends un **bilan court, limité aux problèmes graves** : un tableau `Plan | Fichier | Problème | Action`. S'il n'y en a aucun, tu écris simplement « archive complète : prête pour l'animation ». **Pas de remarques de détail** : un SVG n'a pas besoin d'être parfait. Pour un SVG grave, je revectorise (ou je regénère l'image), je relance le script (il repousse tout seul).

**Règle qui vaut pour toute l'étape : tu n'écris aucun code d'animation ici.** Tu demandes ce qui manque (arborescence, décisions), tu prépares l'archive, tu la contrôles.

**Étape suivante : l'étape 13 bis (génération de l'audio de la voix off), puis l'étape 14 (réalisation de l'animation de chaque plan), écrites plus bas**, une fois l'archive validée. **Avant d'écrire la moindre ligne d'animation, tu lis toi-même, en entier, le scénario** (voir l'étape 14). Tu ne me demandes pas de te l'expliquer ; si un point reste flou après lecture, tu me poses une question précise en citant le passage.

---

<a id="e13bis"></a>

## Étape 13 bis : générer l'audio de la voix off (AudioGen)

Cette étape commence quand **l'archive de l'étape 13 est validée** et se fait **avant l'étape 14** : la voix off est générée **avant** l'animation. Elle porte le numéro « 13 bis » (comme « 2 bis ») pour ne rien renuméroter dans ce document. Le but : produire **l'audio de chaque plan parlé** (P plans parlés ; un plan sans voix off, par exemple l'écran de fin, n'a pas d'audio) avec **AudioGen** (`AudioGen.pyw`, TTS CAMB.AI). **Tu prépares les textes, je les génère.** Tu **n'écris aucune page HTML** : tu me livres un zip, un script et un JSON (voir plus bas).

<a id="e13bis-1"></a>

### 13 bis.1 · Principe

- **Un speech AudioGen par plan.** Chaque ligne `PlanN : phrase` d'un `speech.txt` devient **un speech**, avec son propre fichier audio. Un plan marqué `(aucune voix off)` est ignoré. Un speech reste sous **500 caractères** (limite d'une génération sur CAMB.AI, affichée par AudioGen).
- **Langue cible : l'anglais**, sauf si je te dis une autre langue. Les balises sont **toujours en anglais** : ce sont des commandes, pas du texte à traduire.
- **Les règles de traduction et de balisage sont écrites en entier dans ce document**, à la sous-section « Règles de traduction et de balisage » juste en dessous. **Elles ne dépendent d'aucun autre fichier** : tu ne me demandes aucun prompt TTS externe, et tu les relis en entier avant de commencer. Si un fichier de règles de balisage traîne dans la conversation, **tu l'ignores** : ces règles-ci font foi.
- **La durée visée d'un speech est celle de son plan** (estimation : la durée réelle du plan sera celle de l'audio généré, voir étape 14), lue dans la première ligne de `PlanN.txt` (par exemple `· 4 s`). Tu comptes **2,5 à 3 mots par seconde**. Si le texte traduit dépasse nettement, tu le **raccourcis sans perdre le sens** et tu **signales le cas** dans ton bilan. Une phrase peut déborder sur le plan voisin (voir l'étape 9) : tu le signales aussi au lieu de la couper.
- **La source des textes est le dépôt `Storyboard`** (`https://github.com/officecenter632-maker/Storyboard`, `Storyboard.zip`, un `speech.txt` par séquence). **C'est toi qui le clones et qui lis les textes** : je ne te les donne pas. Si l'accès échoue, la règle de la zone « Erreurs de méthode » s'applique (les trois accès, jamais un autre dépôt à la place) : tu me demandes le lien exact en une phrase.
- **Tu ne modifies que les textes des `speech.txt`** : jamais un `PlanN.txt`, jamais une image, jamais `Sequences.md`.

<a id="e13bis-2"></a>

### 13 bis.2 · Règles de traduction et de balisage

Ces règles sont **complètes** : tu n'as besoin d'aucun autre fichier. Elles s'appliquent à **chaque ligne** `PlanN : texte` des `speech.txt`.

**Rôle.** Tu adaptes la voix off pour le TTS de CAMB.AI : tu traduis chaque segment, puis tu y intègres **une balise d'émotion** adaptée. Le ton par défaut est **posé, curieux, pince-sans-rire, jamais théâtral** (style Kurzgesagt), sauf si je te donne un autre ton.

**Traduire.**
- Reste **fidèle au sens et au rythme** de l'original. **Ne rajoute aucune idée.**
- **Garde la ponctuation finale** : elle pilote l'intonation du TTS.
- **Conserve la découpe** : un segment coupé à une micro-pause (par exemple « Et comestible ! », ou une phrase qui commence par « … ») **reste un segment séparé**.
- **Garde les chiffres lisibles à l'oral** (« 3,000 years old », « 1922 »).
- **Vérifie la durée** : 2,5 à 3 mots par seconde. Si le texte traduit dépasse la durée du plan, tu le raccourcis sans perdre le sens et tu signales le cas dans ton bilan.
- **Une autre langue que l'anglais** garde **les mêmes balises, en anglais** : ce sont des commandes, pas du texte à traduire.

**Choisir la balise.**
- **Une seule balise par segment, placée au tout début**, entre crochets : `[calm] Texte.` Jamais deux balises dans un même segment, jamais d'enchaînement contradictoire.
- Tu utilises **surtout les deux premiers niveaux** d'une émotion (les deux premiers mots de chaque ligne de la liste ci-dessous). Les **niveaux 3 et 4** seulement pour un **pic dramatique voulu**.
- **Aucun effet sonore** (`[laughing]`, `[sighing]`, `ahem ahem`…) **sauf si je le demande** explicitement.
- Les segments qui **prolongent la même idée gardent la même balise ou une balise voisine**, pour éviter les ruptures de timbre.
- **Pas de balise sur un segment de 1 à 2 mots** si elle risque de le déformer : tu le laisses **sans balise**.
- Tu écris la balise **exactement** comme dans la liste (minuscules, même orthographe, `grossed_out` avec son tiret bas). **Une balise qui n'est pas dans la liste est interdite.**

**Balises autorisées** (et **uniquement** celles-ci).

- **Styles** (à écrire en entier, virgules comprises) : `[shouting, angry, threatening]`, `[whispering]`, `[whispering, secretive]`, `[empathetic, helpful]`, `[happy, excited, promotional]`, `[patient, teaching]`.
- **Émotions**, **du plus subtil au plus extrême** (niveau 1, 2, 3, 4), chacune s'écrit seule entre crochets, par exemple `[curious]` :

| Famille | Niveau 1 | Niveau 2 | Niveau 3 | Niveau 4 |
| --- | --- | --- | --- | --- |
| Nervosité | uneasy | nervous | anxious | trembling |
| Peur | fearful | scared | terrified | panicked |
| Colère | irritated | angry | furious | enraged |
| Tristesse | down | sad | melancholic | depressed |
| Joie | cheerful | happy | joyful | delighted |
| Excitation | energetic | excited | thrilled | hyped |
| Calme | relaxed | calm | peaceful | serene |
| Confiance | assured | confident | certain | bold |
| Doute | uncertain | doubtful | hesitant | skeptical |
| Surprise | surprised | startled | shocked | astonished |
| Dégoût | grossed_out | disgusted | repulsed | revolted |
| Fierté | satisfied | accomplished | proud | fulfilled |
| Honte | embarrassed | guilty | ashamed | humiliated |
| Amour | warm | affectionate | loving | tender |
| Flirt | charming | playful | flirty | teasing |
| Sarcasme | dry | ironic | sarcastic | mocking |
| Détermination | focused | determined | driven | resolute |
| Frustration | annoyed | irritated | frustrated | exasperated |
| Soulagement | calmed | reassured | relieved | grateful |
| Curiosité | interested | curious | inquiring | intrigued |
| Ennui | dull | uninterested | bored | apathetic |
| Émerveillement | inspired | amazed | awed | wonderstruck |
| Méfiance | wary | suspicious | guarded | distrustful |
| Urgence | urgent | rushed | intense | pressured |
| Autorité | firm | authoritative | directive | commanding |
| Politesse | polite | courteous | respectful | formal |
| Gratitude | appreciative | thankful | grateful | warm |
| Confusion | uncertain | puzzled | confused | lost |
| Désespoir | resigned | defeated | hopeless | despairing |
| Espièglerie | lighthearted | playful | fun | silly |

**Si le texte source est ambigu ou incomplet** (une ligne vide, un `PlanN` manquant), tu me poses **une seule question** avant de générer.

<a id="e13bis-3"></a>

### 13 bis.3 · Ce que je te fournis

1. L'**arborescence réelle** du projet sur mon ordinateur, copiée telle quelle : première ligne = **chemin absolu complet** (emojis inclus). Elle doit montrer `Storyboard\sequenceN\speech.txt`. **Si je ne te l'ai pas donnée, ou si tu doutes qu'elle soit à jour, tu me la demandes** : tu n'écris jamais un chemin de mémoire.
2. Mes **décisions** : la langue (l'anglais par défaut) et, si je veux les fixer, la **voix**, le **modèle** et la **langue** d'AudioGen. Sans réponse, tu laisses ces champs vides (réglage de l'application) et tu le notes dans ton bilan.

<a id="e13bis-4"></a>

### 13 bis.4 · Ce que tu fais

1. **Tu clones `Storyboard`, tu ouvres `Storyboard.zip`** et tu lis les S `speech.txt` et les N `PlanN.txt` (pour les durées). Tu vérifies **S `speech.txt`** et **N lignes `PlanN`** (P voix off et les plans sans voix off) ; tout écart m'est signalé avant de continuer.
2. **Tu traduis et tu balises chaque ligne**, plan par plan, avec les règles ci-dessus. **Format conservé** : `speech.txt` garde une ligne par plan, sous la forme `PlanN : [balise] texte`, **mêmes noms de fichiers, mêmes numéros de plan, même ordre**. Un plan sans voix off reste tel quel.
3. **Tu me livres `Speech_audio.zip`** : un dossier racine `Storyboard/` avec les **S `sequenceN/speech.txt` modifiés**, rien d'autre. C'est la copie à relire.
4. **Tu me livres `ecraser_speeches.py`** : **un seul script Python** qui **écrase les `speech.txt` présents sur mon ordinateur** par les versions modifiées. **Tu pars de l'esprit de `envoyer_storyboard.py`** : chemin absolu **en dur** recopié de mon arborescence (emojis écrits en codes `\U`), il s'exécute n'importe où, se lance depuis un éditeur **sans argument ni question**, tu le **testes sur de faux dossiers** avant de me le donner, et tu le livres dans **un seul bloc de code**. **Il contient lui-même les textes modifiés** : je n'ai aucun zip à placer ni à ouvrir. Il fait, dans cet ordre :
   - **contrôle de structure** : les S dossiers `sequenceN` et leurs S `speech.txt` existent sur mon disque, et chaque `speech.txt` contient les mêmes numéros de plan que la version modifiée ; en cas d'écart, il l'affiche et n'écrit rien ;
   - **sauvegarde des originaux** dans `Audio\speech_originaux_fr\sequenceN\speech.txt` ; **une sauvegarde déjà présente n'est jamais remplacée**, pour qu'un deuxième lancement ne perde pas le texte d'origine ;
   - **écrasement** des S `speech.txt`, en UTF-8, puis **relecture** de chacun pour vérifier qu'il est identique à la version attendue ;
   - **bilan** : fichiers écrasés, déjà à jour, absents, écarts. Il est **idempotent** (le relancer ne change rien) et **ne pousse rien sur GitHub**.
5. **Tu me livres `projet_audiogen.json`**, le fichier que je donne à AudioGen (bouton « Nouveau projet » : je saisis le **chemin du fichier**). Format :

```
{
  "projet": "nom du projet",
  "speeches": [
    {
      "nom": "Plan1",
      "texte": "[balise] le texte du plan, balise comprise",
      "chemin_sauvegarde": "chemin complet de l'audio à créer (.wav)"
    }
  ]
}
```

| Champ | Règle |
| --- | --- |
| `projet` | Un nom court (par exemple `6-musk_starlink_audio`). |
| `nom` | les `PlanN` des plans parlés, uniques, dans l'ordre. **Un plan sans voix off n'a pas de speech.** |
| `texte` | La ligne du `speech.txt` modifié, **sans** le préfixe `PlanN :`, **balise comprise**, identique au mot près. 500 caractères au plus. |
| `chemin_sauvegarde` | Le **chemin complet** `<racine du projet>/Audio/sequenceN/PlanN.wav`, écrit avec des `/`, emojis du chemin recopiés tels quels (le JSON est lu par AudioGen, pas ouvert dans un éditeur Python : pas de codes `\U`). L'extension est `.wav` ; AudioGen détecte lui-même le vrai format. Aucun doublon. |
| `voix`, `modele`, `langue` | **Facultatifs** : seulement si j'ai donné ma décision. Sinon, absents. |

   **Tu contrôles par programme avant de livrer** : tu charges `AudioGen.pyw` (il s'importe **sans lancer l'interface**) et tu passes mon JSON à sa fonction **`lire_liste_speech(chemin)`** : **aucune erreur ni avertissement** (en particulier aucun « dépasse 500 caractères ») ; P speeches, noms et chemins uniques ; chaque `chemin_sauvegarde` est dans le bon dossier `sequenceN` ; chaque `texte` est identique à la ligne du `speech.txt` modifié ; **chaque balise est dans la liste des balises autorisées** de la sous-section « Règles de traduction et de balisage » (une seule balise par segment, placée au début, ou aucune).
6. **Tu livres** les trois fichiers avec un **bilan court**, sans tableau qui répète le contenu : les choix de balises notables, les textes raccourcis ou à risque côté durée, ce qui a été changé par rapport au texte source, et la consigne en deux lignes (« lance `ecraser_speeches.py` depuis ton éditeur ; dans AudioGen, clique sur **Nouveau projet** et donne le chemin de `projet_audiogen.json` »).

<a id="e13bis-5"></a>

### 13 bis.5 · Premier essai

Avant de générer les P audios, je génère **`Plan1` puis `Plan2`**, je les écoute et je te dis : la balise s'entend-elle, la voix reste-t-elle la même d'un plan à l'autre, la durée tient-elle dans celle du plan. Si une balise déforme un segment, tu me livres le **`speech.txt` corrigé, `ecraser_speeches.py` en entier et l'entrée JSON correspondante**, toujours **identiques** entre eux ; les noms de plan ne changent jamais.

<a id="e13bis-6"></a>

### 13 bis.6 · Corrections

Un audio déjà généré à refaire : tu me livres, dans la **même réponse**, le JSON de réinitialisation d'AudioGen (`{"reinitialiser": ["Plan3", "Plan17"]}`) pour que je le colle dans l'application, avec la raison de chaque plan. Un texte modifié suit toujours le même chemin : `speech.txt`, script d'écrasement et JSON, **identiques**.

<a id="e13bis-7"></a>

### 13 bis.7 · Après cette étape

- **L'audio part dans `AnimationData.zip`** : quand les P audios sont générés, **je relance `envoyer_animation.py`** (il repousse tout seul : un seul zip, un seul commit). Les `audio/sequenceN/PlanN.<ext>` et les `speech.txt` modifiés partent avec. Tu **télécharges le zip** et tu fais le contrôle « Audio » de l'étape 13 ; **l'étape 14 ne commence qu'une fois ce contrôle passé**.
- **L'audio est intégré directement dans la page HTML de chaque plan** (étape 14), et **la durée de chaque page est calée sur celle de sa voix** (étape 14, « La durée du plan = la durée de la voix »), sans caler chaque geste sur chaque mot : les `speech.txt` contiennent maintenant des **balises `[...]`** et du texte en anglais ; tu **ignores les balises** et tu te sers du texte seulement pour le **sens**.

**Étape suivante : l'étape 14 (réalisation de l'animation de chaque plan).**

---

<a id="e14"></a>

## Étape 14 : réaliser l'animation de chaque plan (rendu web, directement ici)

Cette étape commence quand **l'archive de l'étape 13 est validée**, que **l'audio de l'étape 13 bis est généré** et que **l'archive a été repoussée avec l'audio** (`audio/` dans `AnimationData.zip`). Le but : **tu animes, plan par plan, directement en web** (HTML, CSS, JavaScript), **et c'est toi qui me montres le rendu dans la conversation**, sous forme d'une **page web animée par plan**, publiée en artefact. Je regarde, je te dis ce qui marche ou non, tu corriges, on passe au plan suivant. **Aucun logiciel externe n'est utilisé pour animer.** **C'est toi qui écris tout, y compris le détourage** : je n'écris, ne règle et ne lance rien, je regarde et je décide. **Les plans sont répartis et suivis par IngXAi** (voir « Les tâches dans IngXAi : comment elles sont rangées ») : **cette section prime sur tout ce qui suit là où elles diffèrent** (livraison en fichier joint au lieu d'un artefact, plan attribué par le logiciel, directives lues dans le Director cloné depuis `Autoniax`, validation faite par moi avec « Définir comme résultat »).

> **RÈGLE N°0 DE L'ÉTAPE 14 : LE REGISTRE D'ABORD, AVANT TOUT (hors IngXAi).**
> Dès qu'on te demande d'animer un plan (« fais le plan 15 », « faisons l'animation 14 », etc.), **ta toute première action est de me demander le fichier `Registre_exigences_animation.md`**, avec cette phrase, mot pour mot : **« Envoie-moi d'abord `Registre_exigences_animation.md` (dans le dossier `Animation/` du projet). »** Tu ne lis rien d'autre, tu ne clones rien, tu ne cherches rien, tu n'écris aucune ligne **avant** d'avoir envoyé cette phrase et d'avoir reçu le fichier.
> - **Tu ne le cherches pas toi-même** : il n'est ni dans le dépôt `ShaderiaxAnim` ni dans `AnimationData.zip`, il est sur mon ordinateur. Tu me le demandes, tu n'essaies pas de le deviner ni de t'en passer.
> - **Tu ne supposes jamais** que je te l'ai déjà donné : tu n'as aucune mémoire d'une session à l'autre. Si le fichier n'est **pas dans cette conversation**, tu me le demandes, même si les plans précédents semblent bien se passer.
> - **S'il n'existe pas encore** (première fois), je te le dis et tu le crées toi-même, puis tu me le livres.
> - **Tu ne livres aucun plan** tant que tu ne l'as pas lu en entier et repassé ligne par ligne. Ne pas l'avoir demandé est **une faute grave**, au même titre qu'un défaut d'animation.
> - **Tu écris dans ta première ligne de livraison** : « Registre lu et repassé. » Si tu ne peux pas l'écrire honnêtement, tu ne livres pas.

**Hors périmètre, toujours** : le montage (logo, polices, cartons, étiquettes de date, de lieu et de source, badges) et la **synchronisation fine de l'animation sur l'audio** (gestes calés mot par mot). **La durée de la page, elle, est toujours celle de la voix.** **L'audio, lui, est intégré directement dans le HTML de chaque plan** (voir « L'audio du plan, intégré dans la page »). Les consignes de montage restent dans les fiches, sans être animées. **En revanche, chaque page doit pouvoir être transformée en vidéo sans retouche** : elle suit le **contrat de la page** (voir « Contrat de la page : la structure imposée »), vérifié avant chaque livraison.

<a id="e14-1"></a>

### 14.1 · Les tâches dans IngXAi : comment elles sont rangées

IngXAi (`IngXAi.pyw`, « le logiciel ») range les N plans en **tâches** (**un plan = une tâche**), les attribue à des **agents** (un agent = une conversation claude.ai pilotée par le logiciel) et garde la trace de ce qui est fait. Dans ce mode :

- **chaque agent anime un seul plan**. Le **prompt de la tâche est minimal** : le numéro du plan et l'ordre de **cloner le dépôt `Autoniax`** (`Director.md` et `Registre_exigences_animation.md`), de lire **seulement l'étape 14 du Director** et le registre, puis d'animer le plan. Tout le reste est dans le Director (cette étape 14 tient lieu de directives) ; dans `references`, joints au **premier message** de la tâche : le `speech.txt` de la séquence et, si le plan en continue d'autres, **la page de ces plans (jointe automatiquement par le logiciel)**. **Le registre n'est pas joint : il est dans le dépôt `Autoniax`, que l'agent clone.** Le dossier des SVG n'est pas envoyé non plus : l'agent le prend dans son clone de `ShaderiaxAnim` (`AnimationData/assets/PlanN/`). **L'agent ne demande rien** (ni le registre, ni le plan précédent) ;
- après l'attribution, **j'insère le prompt avec « Valeurs par défaut » et j'envoie** ;
- l'agent livre **`planN.html` comme fichier joint**, sans artefact ni lien, et, **s'il y en a**, **ses ajouts au registre** (un petit fichier `.md`, **jamais le registre complet**) ;
- **je regarde la page, puis c'est moi qui la valide** : « Définir comme résultat » sur la carte du fichier reçu. Elle est rangée dans `Animation/Plan N – rendu animé.html`, et l'ancienne version, s'il y en avait une, est archivée dans `Animation/_versions`. Un **double-clic sur la tâche** ouvre la fenêtre « Résultats » (état, ouverture du fichier, « Réinitialiser la tâche… »). Si la page n'est pas bonne, je le dis à l'agent dans le chat : il corrige **la même page** et je la redéfinis comme résultat. **Les ajouts au registre** sont rangés de la même façon (« Définir comme résultat »), dans `Animation/Registre_ajouts/`, **avant ou après la page**.

#### Les états d'une tâche

| État affiché | Sens | Attribuable à un agent ? |
| --- | --- | --- |
| **À faire** | résultat non défini, aucun agent dessus | **oui** |
| **🔒 En attente** | à faire, mais une tâche dont elle dépend n'est **pas encore terminée** | **non, jamais** |
| **Désactivée** | mise de côté par moi (voir plus bas) | **non, jamais** |
| **Attribuée** | un agent y travaille | non |
| **Terminée** | le résultat **obligatoire** (la page `.html`) est défini : **un plan déjà animé est une tâche terminée** ; les résultats facultatifs ne comptent pas | non (je peux la réinitialiser) |

« 🔒 En attente » se **calcule** tout seul (il disparaît dès que les tâches dont dépend la tâche sont terminées) ; « Désactivée » est **enregistré** dans le projet.

#### L'attribution

1. J'attribue les tâches **à la main** (bouton « ＋👤 », une tâche à un agent libre) ou **automatiquement** (bouton « ⚡ » : tâches attribuables ↔ agents libres). Un agent libre est en ligne, avec le chat prêt et sans tâche en cours.
2. Une tâche **en attente ou désactivée n'est jamais attribuée**, ni à la main ni automatiquement.
3. Une tâche **se débloque toute seule** dès que la dernière tâche dont elle dépend est terminée.
4. Les tâches **indépendantes** avancent **en parallèle** ; les tâches **liées** (une chaîne) avancent **l'une après l'autre**. « De Plan 1 à Plan N » est donc un ordre de préférence, pas un ordre strict : **tu écris les tâches dans le JSON de 1 à N**.
5. Un plan qui **réutilise** un asset d'un autre plan **dépend de son plan source** : le plan source est toujours fait avant, sans que personne ait à y penser.

#### Déclarer les dépendances : le champ `depend_de`

Chaque tâche porte la **liste des tâches qui doivent être terminées avant elle** (`[]` si elle est indépendante), avec les identifiants `p<N>`. **C'est toi qui la remplis**, à partir des fiches : je ne te la dicte pas.

- **Un plan dépend d'un autre quand il le continue** (même scène : même décor, mêmes personnages ou objets, même caméra qui poursuit son mouvement), **ou quand il réutilise un de ses assets** (`_reutilise.txt` : le plan source est celui qui figure dans `Registre_elements_animation.md` et dans la fiche du plan). **Dans le doute, il dépend** (comme dans « Plan qui continue le précédent »).
- **Où tu cherches** : `Sequences.md` et les dossiers `sequenceN` du storyboard (les plans consécutifs d'une même séquence partagent décor et personnages : ils se suivent), la fiche du plan dans `Liste_assets_animation.md`, son `PlanN.txt`, `Registre_elements_animation.md` (plan source et plans qui réutilisent), les `_reutilise.txt`.
- **Le premier plan d'une séquence est indépendant** (`[]`), **sauf** s'il réutilise un asset ou si sa fiche montre la même scène que le plan d'avant malgré le changement de séquence.
- **Dépendances directes seulement** : le plan 12 qui continue le 11, lui-même dépendant du 10, s'écrit `["p11"]`, pas `["p10", "p11"]`. Un plan qui continue **et** réutilise un autre plan en liste les deux : `["p11", "p9"]`.
- **Jamais de boucle, jamais la tâche elle-même.** Un plan `_rien_a_generer.txt` est aussi une tâche (une page courte) et suit la même règle.
- **N'enchaîne pas ce qui n'a pas de lien** : tout chaîner reviendrait à n'avoir qu'un agent à la fois. Mais **n'omets pas une vraie continuité** : un raccord cassé coûte plus cher qu'une attente.
- **Un plan déjà animé est une tâche terminée** : il est dans le JSON comme les autres (**les N plans y sont toujours**), avec le champ **`existant`** sur son résultat (le chemin de sa page déjà validée, voir plus bas), donc il apparaît « Terminée » dès la création du projet. C'est la relation de dépendance qui **fournit le plan précédent** au plan suivant : le plan qui le continue ou le réutilise le met dans son `depend_de`, comme n'importe quel autre.

Quand une tâche dépend d'une autre, **le logiciel joint lui-même la page de la tâche précédente** (son résultat obligatoire, jamais ses ajouts au registre) au premier message : tu n'as pas à l'ajouter dans `references`.

#### Désactiver un plan : le champ `desactive`

- Il vaut **`false` pour toutes les tâches** dans le JSON : c'est moi qui désactive ensuite, dans le logiciel (**bouton « ⊘ » : « Désactiver / réactiver la tâche »**, possible seulement sur une tâche « À faire »). Le choix est **enregistré dans le projet**.
- Une tâche **désactivée n'est jamais attribuée**. **Les tâches qui en dépendent restent en attente (🔒) tant qu'elle n'est pas terminée** : on n'anime pas la suite d'un plan qui n'existe pas. Je la réactive, ou tu retires la dépendance si elle était fausse.
- Sert à **mettre de côté** un plan (en attente d'une décision de ma part, ou problématique) sans bloquer les plans indépendants.
- **Réinitialiser une tâche terminée** (bouton ↺ ou « Réinitialiser la tâche… » dans la fenêtre « Résultats ») la remet « À faire » : ses dépendantes **pas encore commencées** repassent en attente ; celles **déjà terminées restent terminées**, mais leur raccord est à revoir, et c'est alors à moi de décider de les refaire. La page déjà rangée reste dans son dossier et sera archivée dans `_versions` au remplacement.

#### Ce que reçoit chaque agent

- **Toujours** (dans `references`, joints au premier message de la tâche, et de nouveau après un « Nouveau chat ») : le speech de la séquence. **Le Director et le registre des exigences viennent du dépôt `Autoniax`** : l'agent le clone, lit **seulement l'étape 14 du Director** et **le registre en entier** avant de commencer.
- **Dans le prompt** : le numéro du plan, et rien d'autre.
- **Plan avec dépendances** : la page **terminée** de **chacune** des tâches dont il dépend, jointe par le logiciel. L'agent reprend leur état final tel quel et contrôle le raccord. **Le logiciel ne lui attribue la tâche qu'après leur fin** : il ne peut donc jamais travailler sur un plan dont le précédent manque.
- **Plan indépendant** : rien de plus ; il part de l'état décrit par sa fiche. Si sa fiche montre pourtant la même scène qu'un plan d'avant, l'agent le dit en une phrase avant de livrer (la dépendance est alors à corriger).
- **Reprise après interruption** : si l'agent s'arrête (limite de messages), le logiciel peut joindre un `contexte.md` à la reprise ; l'agent s'en sert pour ne pas refaire ce qui est fait.

#### Le dépôt `Autoniax` : le Director et le registre, clonés par l'agent

**Il n'y a plus de fichier de directives à part.** Le Director lui-même fait office de directives : il est dans le dépôt `https://github.com/officecenter632-maker/Autoniax` (deux fichiers à la racine : `Director.md` et `Registre_exigences_animation.md`), que l'agent clone. **Le prompt de chaque tâche est donc minimal** :

> Plan {N}. Clone https://github.com/officecenter632-maker/Autoniax (git clone --depth 1). Dans Director.md, lis uniquement la section « Étape 14 » (de « ## Étape 14 » à « ## Étape 15 ») et le tableau « Erreurs de méthode à ne jamais refaire ». Lis Registre_exigences_animation.md en entier. Puis anime ce plan.

**Ce que le Director dit à l'agent** (cette étape 14, lue par l'agent, rédigée sans rien inventer) :
- son rôle : **il anime un seul plan** (celui du prompt), livre **`planN.html` en fichier joint**, sans artefact ni lien, et ne demande rien ;
- ce qu'il lit d'abord : le registre des exigences **cloné depuis `Autoniax`** (en entier, « Registre lu et repassé. » en première ligne de sa livraison), le speech joint, la page du plan précédent s'il y en a une ;
- ce qu'il fait lui-même : **cloner `ShaderiaxAnim`**, télécharger `AnimationData.zip`, prendre les SVG dans `AnimationData/assets/PlanN/`, lire `Plan_animation.md` et `Sequences.md` ; **si un clone échoue, il ne prend aucun autre dépôt** (« Erreurs de méthode à ne jamais refaire ») ;
- les règles de la page : le **contrat de la page**, **« La durée du plan = la durée de la voix »** (14.7 bis), « L'audio du plan, intégré dans la page », « Vérifier avant de livrer » ;
- les **consignes anti-perte** : il écrit ses fichiers avec l'outil d'écriture de fichiers (jamais un gros `cat > fichier <<EOF`, une commande = une trentaine de lignes au plus) ; il livre ses fichiers de travail en pièces jointes après chaque étape importante ; il tient à jour `notes_<id de la tâche>.md` (mesures, décisions, point d'arrêt, prochaine étape) et le livre ; il livre **ses ajouts au registre** dans un fichier `Ajouts registre – Plan N.md` (voir ci-dessous) ; il n'affiche jamais un fichier entier (`| head -40`) ; il écrit après chaque étape une phrase avec le résultat chiffré.

**Le dépôt doit être lisible par l'agent sans identifiants** (dépôt public, comme `ShaderiaxAnim`) : sinon son clone échoue et il s'arrête (il ne prend aucun autre dépôt).

**Le script `envoyer_autoniax.py`** : tu me l'écris **à partir de l'arborescence réelle** (elle te donne les chemins de `Director.md` et de `Registre_exigences_animation.md` ; tu ne les écris jamais de mémoire). Il fait tout seul, avec la méthode d'envoi du modèle `envoyer_storyboard.py` (dépôt neuf, un seul commit, push forcé, vérification de la branche distante, jeton jamais affiché) : il contrôle que les deux fichiers existent et sont les bons, puis les pousse **à la racine** de `Autoniax` et affiche les liens directs. **Modèle : voir [Annexe A10](#annexe-a10) (en fin de document), à recopier, pas à réécrire.** Je le relance chaque fois que le Director ou le registre change ; je te dis seulement que c'est fait.

**Le registre des exigences** est dans le dépôt **`Autoniax`** : l'agent le **clone**, il ne le reçoit pas en pièce jointe et **ne le modifie pas**. Plusieurs agents travaillent en parallèle : s'ils renvoyaient chacun le registre complet, chacun écraserait le travail des autres. **Chaque agent livre donc seulement ses ajouts**, dans un fichier `Ajouts registre – Plan N.md` : **uniquement ce qu'il faut ajouter ou changer** (chaque défaut ou demande que je signale, avec sa portée), **jamais le registre complet**. C'est un **résultat facultatif** de la tâche (`"facultatif": true`) : il peut exister ou non, et **ce n'est pas lui qui décide que la tâche est terminée** (seule la page le décide). Je le définis comme résultat comme la page ; il est sauvegardé dans `Animation/Registre_ajouts/` (les anciennes versions dans `_versions`). **Toi**, dans cette conversation, tu **fusionnes ces ajouts dans `Registre_exigences_animation.md`** (sans doublon : un sujet qui revient gagne une ★), quand je te donne les fichiers, puis tu me livres le registre à jour ; **je le range dans `Animation/` et je relance `envoyer_autoniax.py`**, qui le repousse dans `Autoniax`. Les agents qui démarrent ensuite clonent le registre à jour.

**Je peux modifier le Director à tout moment.** Chaque fois que cette étape 14 change, **tu me livres le `Director.md` à jour** ; je le range dans `Bibliotheque/Reference/` et je relance `envoyer_autoniax.py` : une tâche **pas encore commencée** (ou un agent qui ouvre un « Nouveau chat » et reclone) reçoit toujours la dernière version. Un agent **déjà en cours** garde celle qu'il a clonée : je lui dis dans le chat ce qui a changé.

#### Ton travail avant les agents : `projet_animation.json`

**Ce que je te fournis** : l'**arborescence réelle** du projet (chemin complet inclus). Rien d'autre : tu ne me demandes ni les dépendances ni les chemins.

**Ce que tu fais** : tu écris **`projet_animation.json`**, un seul bloc JSON livré **comme fichier** (même nom), que je charge dans le logiciel (**« Nouveau projet »**, puis « Charger un fichier .json… » ou je colle le JSON, puis **« Valider et créer »**). Le logiciel vérifie les chemins à la validation et affiche les erreurs. **Il faut la version d'IngXAi qui gère les résultats `facultatif` et `existant`** (`IngXAi.pyw` mis à jour).

```json
{
  "projet": "6-musk_starlink",
  "taches": [
    {
      "id": "p10",
      "titre": "Plan 10",
      "prompt": "Plan 10. Clone https://github.com/officecenter632-maker/Autoniax (git clone --depth 1). Dans Director.md, lis uniquement la section « Étape 14 » (de « ## Étape 14 » à « ## Étape 15 ») et le tableau « Erreurs de méthode à ne jamais refaire ». Lis Registre_exigences_animation.md en entier. Puis anime ce plan.",
      "references": [
        "D:/ScaleTube/CHANNELS/IngeniaX/<chemin recopié de l'arborescence>/Video/6-musk_starlink/Storyboard/sequence9/speech.txt"
      ],
      "depend_de": [],
      "desactive": false,
      "resultats": [
        { "nom": "Plan 10 – rendu animé", "types": ["html"],
          "dossier": "D:/ScaleTube/CHANNELS/IngeniaX/<chemin recopié de l'arborescence>/Video/6-musk_starlink/Animation",
          "existant": "D:/ScaleTube/CHANNELS/IngeniaX/<chemin recopié de l'arborescence>/Video/6-musk_starlink/Animation/<nom exact de la page déjà validée>.html" },
        { "nom": "Ajouts registre – Plan 10", "types": ["md"], "facultatif": true,
          "dossier": "D:/ScaleTube/CHANNELS/IngeniaX/<chemin recopié de l'arborescence>/Video/6-musk_starlink/Animation/Registre_ajouts" }
      ]
    },
    {
      "id": "p12",
      "titre": "Plan 12",
      "prompt": "Plan 12. Clone https://github.com/officecenter632-maker/Autoniax (git clone --depth 1). Dans Director.md, lis uniquement la section « Étape 14 » (de « ## Étape 14 » à « ## Étape 15 ») et le tableau « Erreurs de méthode à ne jamais refaire ». Lis Registre_exigences_animation.md en entier. Puis anime ce plan.",
      "references": [ "…/Storyboard/sequence10/speech.txt" ],
      "depend_de": ["p11"],
      "desactive": false,
      "resultats": [
        { "nom": "Plan 12 – rendu animé", "types": ["html"], "dossier": "…/Animation" },
        { "nom": "Ajouts registre – Plan 12", "types": ["md"], "facultatif": true, "dossier": "…/Animation/Registre_ajouts" }
      ]
    }
  ]
}
```

| Champ | Règle |
| --- | --- |
| `projet` | le nom du dossier du projet. |
| `id` | `p<N>`, **de 1 à N, dans l'ordre, sans en oublier** (seulement lettres, chiffres, `_ . -`, unique). |
| `titre` | `Plan N` (suivi du nom du plan si l'arborescence le donne). |
| `prompt` | **le prompt minimal ci-dessus, avec le numéro du plan, rien d'autre** : le dépôt `Autoniax` à cloner, la partie du Director à lire, le registre ; tout le reste est dans le Director. |
| `references` | **un seul fichier** : le `speech.txt` de la **séquence qui contient** le `PlanN.txt` de ce plan. **Chemin absolu**, avec des `/`, **recopié de l'arborescence** ; il doit **exister** au moment de « Valider et créer ». **Ni Director ni registre ici** : ils sont dans le dépôt `Autoniax`, que l'agent clone. |
| `depend_de` | **obligatoire pour chaque tâche** (voir plus haut), liste d'identifiants `p<N>`. |
| `desactive` | `false` pour toutes. |
| `resultats` | **deux résultats** : **(1) la page**, obligatoire : `nom` = `Plan N – rendu animé` (le nom du fichier sans extension), `types` = `["html"]`, `dossier` = le dossier `Animation/` du projet (chemin absolu), la page validée y est rangée sous le nom `<nom>.html` ; **(2) les ajouts au registre**, **facultatif** : `nom` = `Ajouts registre – Plan N`, `types` = `["md"]`, `"facultatif": true`, `dossier` = `Animation/Registre_ajouts` (chemin absolu). Un résultat facultatif peut exister ou non et ne décide jamais qu'une tâche est terminée. |
| `existant` | **seulement sur la page d'un plan déjà animé et validé** : le chemin absolu de sa page (le nom **exact** dans `Animation/` ; les noms ne sont pas uniformes : `plan 9.html`, `plan12.html`…). Le résultat est alors **défini dès la création** : la tâche est « Terminée » et fournit sa page aux plans qui en dépendent. Les plans pas encore animés n'ont pas ce champ. |

Tous les chemins sont **absolus**, avec des `/` (jamais de `\`) ; les fichiers `.part-*` sont ignorés ; **aucun chemin n'est écrit de mémoire**, seulement ceux de l'arborescence. **Le dossier des SVG n'est pas dans le JSON** (il est dans le clone de l'agent).

**Ce que tu contrôles par programme avant de livrer** : N tâches de `p1` à `pN` sans doublon, **y compris les plans déjà animés** ; chaque fichier de `references` et chaque `existant` existe dans l'arborescence ; chaque `depend_de` ne cite que des tâches existantes, autres que la tâche elle-même, **sans boucle** ; **chaque plan dont le dossier contient `_reutilise.txt` a son plan source dans `depend_de`** ; tous les `desactive` valent `false` ; chaque `nom` de résultat est unique et sans `\ / : * ? " < > |` ; **chaque tâche a au moins un résultat non facultatif** (la page).

**Ton bilan** (court) : les **chaînes** de plans liés (par exemple p10 → p11 → p12), le nombre de plans **indépendants** (qui pourront partir en parallèle), et le nombre de plans **déjà terminés** (`existant`), et les **cas douteux** que tu as traités en « dépend », chacun avec sa raison en une phrase. **Je te corrige si besoin**, tu mets le fichier à jour et tu me le livres de nouveau.

<a id="e14-2"></a>

### 14.2 · Le travail à faire, en résumé

**Avant le premier plan (une seule fois)**

1. Tu clones `ShaderiaxAnim`, tu télécharges `AnimationData.zip` et tu le décompresses. **Si le clone échoue ou si le dépôt n'a pas les SVG attendus, applique « Erreurs de méthode à ne jamais refaire » : tu ne prends aucun autre dépôt à la place.**
2. **Tu apprends le scénario** : tu lis `Plan_animation.md` et `Sequences.md` en entier et tu en tires `scenario_notes.md` (voir « Avant le premier plan : tu apprends le scénario »).
3. Tu écris le **moteur commun** (`moteur_plan.js` et le générateur `generer_plan.py`, dans ton espace de travail) : lecture de la chronologie, caméra, détourage, calques, contrôle lecture / pause / barre de temps. Tu notes ses règles dans `animation_notes.md` et tu crées `animation_status.md`. **Tu me demandes `Registre_exigences_animation.md` et tu le lis en entier** (dans IngXAi : tu le **clones depuis GitHub**, tu ne me le demandes pas) (voir « Le registre des exigences : ne jamais refaire une erreur, ne jamais oublier une demande »).
4. Tu me dis en une phrase si quelque chose bloque (par exemple une méthode de détourage impossible), **avant** de livrer un plan.

**Pour chaque plan, de Plan 1 à Plan N**

1. **Si le plan continue le précédent, tu exiges d'abord le plan précédent** (voir « Plan qui continue le précédent »). Tu repasses **le registre des exigences**, puis **la ligne du plan dans le scénario, celles du plan précédent et du plan suivant**, sa fiche dans `Liste_assets_animation.md`, son entrée du registre, son `PlanN.txt` et le `speech.txt` de sa séquence, et son image de `storyboard/`.
2. Tu formules **l'intention du plan en une phrase** (ce que le spectateur doit comprendre ou ressentir) : l'animation est là pour la servir.
3. Tu génères la page du plan avec les valeurs des fiches.
4. **Tu la regardes toi-même** (voir « Vérifier avant de livrer »), puis tu la publies et tu me donnes le lien avec **une ligne**.
5. Je regarde et je te réponds ; **chaque défaut ou demande que je te signale est noté par toi dans le registre des exigences**, puis tu corriges **dans la même page** ; **tu n'enchaînes qu'après mon « ça marche »**, et tu mets `animation_status.md` à jour (avec le lien de la page).

**À la fin** : un bilan court (voir « Fin de l'étape »).

<a id="e14-3"></a>

### 14.3 · Ce que je te fournis

**Dans IngXAi**, je te fournis seulement, une fois, l'**arborescence réelle** du projet pour `projet_animation.json` ; ensuite chaque agent reçoit, par les `references` de sa tâche, son speech, et clone `Autoniax` (Director et registre). **Sinon : rien**, sauf mon verdict après chaque plan, le registre des exigences au début de la session et, pour un plan qui **continue** le précédent, **le plan précédent** (voir « Plan qui continue le précédent : tu exiges le plan précédent »). L'archive est dans le dépôt `ShaderiaxAnim` : tu **clones le dépôt et tu télécharges le zip toi-même**, tu **gardes la copie** dans ton espace de travail. Tu ne me demandes **jamais** un chemin de fichier (le `manifest.json` donne tout), ni une explication, ni une décision déjà prise (les fiches et le `README.md` la donnent, ou la lecture par défaut).

<a id="e14-4"></a>

### 14.4 · Le détourage et le moteur commun

1. Les SVG gardent leur fond de détourage plein cadre (vert `#00FF00` ou magenta `#FF00FF`, le premier `<path>`), et **ce fond ne doit jamais être visible dans l'animation**. **Tu retires toi-même ce premier `<path>` dans la copie intégrée à la page** : la méthode est simple, fiable et sans frange colorée sur les bords. **Les SVG d'origine ne sont jamais modifiés.** Les fonds de décor (`01_fond_…`) sont opaques par nature et ne sont pas détourés.
2. **Le gros plan reste net** : un SVG est vectoriel, donc il est **redessiné à la bonne taille à chaque image** (SVG en ligne dans la page, ou dessin sur canvas à la résolution d'affichage). Tu ne le convertis jamais en image basse résolution « pour simplifier ».
3. **Recadrage sans perte** : pour ne garder qu'une partie d'un SVG (par exemple un objet isolé dans un SVG qui en contient plusieurs), tu changes le **`viewBox`** de la copie intégrée, jamais le fichier d'origine.
4. **Les SVG d'origine sont « à plat »** (des centaines de chemins sans noms ni groupes). Pour animer un petit élément qui en fait partie (pastille, barre, radar…), tu **mesures** sa position et sa couleur, tu le **masques** dans le fond, puis tu le **redessines** animé en JavaScript **dans le même repère que le fond**, pour qu'il suive la caméra. Si l'élément existe déjà comme asset séparé (fiche de calque), tu l'utilises tel quel.
5. **Ordre de superposition d'abord** : avant de bouger un personnage, tu te demandes ce qui est devant et derrière lui, vu depuis la caméra (un élément du fond qui passe devant un personnage est extrait et redessiné après lui).
6. **Mesurer le corps, pas l'image** : l'échelle d'un personnage se règle sur le dessin visible, pas sur l'image entière qui contient des marges.
7. **Si la page ne permet vraiment aucune méthode** pour un plan, tu me le dis **avant** de le livrer, en une phrase, avec la raison et la seule solution possible.

<a id="e14-5"></a>

### 14.5 · Avant le premier plan : tu apprends le scénario


**Animer sans connaître le scénario donne une animation juste en positions mais fausse en sens.** Avant d'écrire la moindre ligne d'animation, tu dois savoir **comment le scénario a été rédigé** et **ce qu'il veut dire**, plan par plan. Le scénario, c'est **`directives/Plan_animation.md`** (et non une simple « charte de couleurs » : il contient tout), complété par `directives/Sequences.md`.

1. **Tu lis `Plan_animation.md` en entier**, une seule fois, dans l'ordre :
   - la **section 0** : charte visuelle et choix de production (durée totale, nombre de plans, durée moyenne), la **palette**, les **éléments qui reviennent**, les **contradictions du registre et mes arbitrages**, et **« ce que j'ai décidé à ta place »** ;
   - les **9 parties**, plan par plan : pour chaque plan, la **durée**, la **voix off** (mot pour mot), le **visuel et la caméra**, le **texte à l'écran** et la **couleur** ;
   - les **annexes** (contrôles effectués, décisions prises, ce qui reste à fournir, rappel sur les faits).
2. **Tu comprends la mécanique de rédaction**, c'est-à-dire : comment un plan est construit (la voix off dit, l'image **traduit** : foules de silhouettes, symboles, objets fil rouge), comment les plans s'enchaînent dans une partie, comment le décor et la teinte changent d'un plan à l'autre, ce qui est **animé** (les assets) et ce qui est **fait au montage** (texte, étiquettes, logo, mouvements de caméra du scénario), et les règles de style (aplats, pas d'ombre portée, ellipse sous les pieds).
3. **Tu lis `Sequences.md`** (les S séquences, leur décor, leur teinte, leur durée) **et `scenario/`** : les `speech.txt` (la voix off de chaque séquence, mot pour mot) et les `PlanN.txt` (ce que chaque plan représente, sa composition, et ce qui est **fait au montage**). Ce sont ces textes qui disent **comment chaque plan a été pensé** ; tu lis aussi `directives/Liste_assets.md` (assets de base, consignes de montage) et, pour un asset dont tu as besoin du détail, son JSON dans `prompts_assets/PlanN/`.
4. **Tu écris `scenario_notes.md`** (dans ton espace de travail, **court**) : le fil de l'histoire en une ligne par partie ; la liste des **éléments récurrents** (opérateur de drone, télécommande, bâtiment à cinq côtés, satellite…) avec **le plan où chacun apparaît pour la première fois, ceux où il revient et ce qu'il devient** ; **l'intention de chaque plan en une phrase** ; les **arbitrages** et décisions de la section 0 ; les règles de style. Ce fichier remplace toute relecture du scénario en entier.
5. **Le speech sert à comprendre le sens et le rythme** ; l'audio est intégré à la page (voir « L'audio du plan, intégré dans la page ») et **la durée de la page est calée sur celle de la voix** (voir « La durée du plan = la durée de la voix »), sans caler chaque geste sur chaque mot ; les `speech.txt` peuvent contenir des **balises `[...]`** et du texte en anglais (étape 13 bis) : **tu ignores les balises** et tu t'en sers pour le **sens** (ce qui doit être mis en valeur) et le **rythme** (un plan de 3 s ne s'anime pas comme un plan de 8 s). Les durées de `Sequences.md` sont des estimations : la durée réelle d'un plan parlé est celle de son audio.
6. **En cas de désaccord** entre la ligne du scénario et la fiche d'un plan : pour les **valeurs** (positions, tailles, instants), la fiche l'emporte, car elle applique les arbitrages ; pour le **sens**, le scénario l'emporte. Tu notes l'écart dans `animation_notes.md`. Tu ne me poses la question que s'il bloque vraiment, et tu appliques sinon la **lecture par défaut** des fiches.
7. **Tu n'inventes rien** qui ne soit dans le scénario, les fiches ou le registre. Une animation qui « embellit » le scénario (un élément en plus, un geste qui change le sens) est une erreur, au même titre qu'un élément oublié.

<a id="e14-6"></a>

### 14.6 · Un fichier média est intégré à la page ; un élément créé de zéro est dessiné en JavaScript

**Deux cas, et un seul critère : l'élément a-t-il un fichier média dans l'archive ?**

- **Oui (un SVG de `assets/PlanN/`) : tu le lis dans ton clone** (avec `chemin_relatif` du `manifest.json`) **et tu l'intègres à la page**, en base64 (`data:`), parce que la page publiée est **autonome** : elle ne peut charger aucun fichier extérieur. Tu n'écris jamais un SVG à la main à la place de l'asset existant.
- **Non (un élément à créer de zéro, sans fichier média) : tu le dessines directement en JavaScript** (canvas ou SVG en ligne). C'est le cas des éléments de la technique 4 (une fiche `NN_nom_code.md`, jamais une image) : trait qui se trace, pointillés, barres ou jauges, particules, pixellisation, effets. Il est **complet dans la page** (forme, couleurs, mouvement, paramètres), jamais décrit ni laissé à compléter.
- **Interdit dans les deux sens** : redessiner en code un élément qui a déjà un fichier SVG, et inventer un élément que la fiche ne prévoit pas.
- **Un chemin du manifest qui ne mène à rien est un défaut de l'archive** : tu me le signales, tu ne me demandes pas de te le dicter.

<a id="e14-7"></a>

### 14.7 · L'audio du plan, intégré dans la page

**Chaque page `planN.html` contient l'audio de son plan, directement dans le fichier.** C'est le même principe que pour les SVG : la page est **autonome** et ne peut charger aucun fichier extérieur.

1. **Où il est** : `audio/sequenceN/PlanN.<ext>` dans ton clone (clé `audio` du `manifest.json`, `chemin_relatif`). Tu ne me demandes jamais l'audio ni son chemin.
2. **Comment tu l'intègres** : en **base64 dans une balise `<audio>`** (`data:audio/<type>;base64,…`), le type MIME venant de l'**extension réelle** du fichier (`.wav` → `audio/wav`, `.mp3` → `audio/mpeg`, `.ogg` → `audio/ogg`, `.flac` → `audio/flac`, `.m4a` → `audio/mp4`). **Tu ne modifies, ne coupes et ne convertis jamais l'audio.**
3. **Comment il joue** : il est **dans le lecteur de la page**. Le bouton lecture lance l'animation **et** l'audio ensemble ; la pause, la reprise et le retour au début les concernent tous les deux ; la barre de temps suit l'animation. **La durée de la page est celle de la voix** (voir « La durée du plan = la durée de la voix » ci-dessous) : l'audio joue toujours à vitesse normale (`playbackRate = 1`), du début à la fin de la page, sans jamais être accéléré, ralenti ni coupé.
4. **Un plan sans voix off** (par exemple l'écran de fin) : il n'a **pas de voix off**, donc pas d'audio ni de balise `<audio>`.
5. **Audio manquant ou trop lourd** : si l'audio d'un plan parlé est absent de l'archive, c'est un **défaut de l'archive** (tu me le signales en une phrase, sans animer ce plan sans voix). S'il rend la page trop lourde pour être livrée (plus de 5 Mo), tu me le dis en une phrase avant de livrer.
6. **Contrôle avant livraison** : la page contient **une seule** balise `<audio>`, dont la source est bien celle du bon plan (`PlanN`), et elle se lit.

<a id="e14-7bis"></a>

### 14.7 bis · La durée du plan = la durée de la voix (règle absolue, tous les plans parlés)

**Vidéo et voix sont synchronisées : la page dure exactement le temps de la voix, et il n'y a plus de silence à la fin.** Les durées écrites dans `Sequences.md`, `PlanN.txt`, `Plan_animation.md` et les fiches sont des **estimations faites avant que la voix existe** : ce sont des **approximations, jamais des valeurs absolues**. Pour un plan parlé, la seule durée qui fait foi est celle du **fichier audio**.

1. **Tu mesures l'audio par programme** (`ffprobe`, `mutagen` ou lecture de l'en-tête du fichier, jamais « à l'oreille » ni à partir du texte) : `DUREE_AUDIO` en secondes.
2. **`DUREE = DUREE_AUDIO` arrondie au centième de seconde supérieur** (par exemple 4,752 s donne `4.76`). Pas de marge, pas de « respiration » ajoutée : au plus 0,01 s de plus que la voix. Cette valeur est **la même** dans la constante de durée de la page, dans `seek.max`, dans l'en-tête de la page et dans la ligne de livraison.
3. **Tu ne règles jamais `playbackRate` pour faire entrer la voix dans le plan** : il reste à `1`. C'est **le plan qui s'adapte à la voix**, jamais la voix au plan (qu'elle soit plus courte ou plus longue que la durée de la fiche). Tu ne coupes, ne ralentis, n'accélères ni ne rallonges l'audio avec du silence.
4. **La chronologie s'adapte à `DUREE`.** Tu gardes les intentions de la fiche (ordre, enchaînement, proportions) mais tu **recalcules tous les instants** : soit tu les écris en fraction de la durée (`u = t / DUREE`), soit tu les écris en secondes de la fiche et tu les multiplies par `K = DUREE / DUREE_FICHE`. Cela vaut pour la caméra, les entrées et sorties d'éléments, les jauges, les clignements, les mouvements de tête. **Les cadences de bouche et de tremblement restent en temps réel** (pas multipliées par `K`). Les oscillations permanentes ont un **nombre entier de cycles** sur `DUREE`, pour que la boucle ne saute pas.
5. **Aucun silence en fin de plan** : la dernière image de la page est celle où la voix se termine. Tout élément qui doit rester visible reste dans son état final **jusqu'à cette dernière image**, mais **la page ne s'allonge pas** pour le laisser vivre. Si le fichier audio contient lui-même un silence de plus de 0,3 s en fin de fichier, tu **ne le coupes pas** (l'audio n'est jamais modifié) : tu le **signales en une phrase** et je décide de régénérer l'audio ou non.
6. **Un plan sans voix off** garde la durée de sa fiche (rien à caler).
7. **La page prime sur la fiche.** Quand `DUREE` diffère de la durée de `Sequences.md`, **tu ne touches pas à `Sequences.md`** : tu écris dans ta ligne de livraison « **durée réelle X s (fiche Y s)** » et tu le consignes dans `animation_status.md`. Les chapitres de l'étape 15 sont calculés avec les **durées réelles des pages**, pas avec celles de `Sequences.md`.
8. **Plan qui continue le précédent** : le raccord (état final repris tel quel) ne change pas ; seule la durée change.

<a id="e14-8"></a>

### 14.8 · Contrat de la page : la structure imposée (pour que l'export en vidéo marche sans retouche)

Plus tard, les pages sont transformées en **vidéo 1920×1080** par le notebook `html_to_video_kaggle.ipynb` (je le lance moi-même sur Kaggle, à partir du dépôt `Export` de l'étape 15). Ce notebook **ne connaît pas ta page** : il la pilote **de l'extérieur**, comme un spectateur qui ferait avancer le temps **image par image**, puis photographie la scène. Il ne marche donc que si la page respecte **ce contrat**. **Une page qui ne le respecte pas n'est pas livrée**, même si elle a l'air bonne à l'écran. Le contrat vaut pour **toutes les pages**, y compris celles d'un plan sans asset à animer (`_rien_a_generer.txt`, `_reutilise.txt` seul). *(Les plans déjà validés avant ce contrat, par exemple les plans 1 à 3 en canvas fixe 1280×720, sont lus par un cas particulier du notebook : on ne les refait pas pour cette seule raison.)*

**Ce que fait le notebook, pour que tu comprennes les règles** : (1) il remplace l'horloge du navigateur par une horloge virtuelle (`requestAnimationFrame`, `performance.now`, `Date.now`) qui avance de 1/cadence à chaque image ; (2) il cherche la scène, masque **tout le reste de la page** (boutons, barre, en-tête) et agrandit la scène à la taille de la vidéo ; (3) il clique sur le bouton Lecture ; (4) il lit la durée sur la barre de lecture ; (5) il capture la scène à chaque image ; (6) il lit la vitesse de lecture de la balise `<audio>` (toujours `1`, la page durant déjà autant que la voix).

**Les règles**

| # | Règle | Pourquoi |
| --- | --- | --- |
| C1 | **Une seule scène : un élément `id="stage"`**, qui contient **tout ce qui apparaît dans la vidéo** (fonds, personnages, SVG, canvas, éléments en code). **Tout ce qui n'apparaît pas dans la vidéo** (boutons, barre de temps, en-tête, légendes d'aide) est **hors de `#stage`**. Rien de filmé n'est hors de `#stage`. | Le notebook ne photographie que `#stage` et masque le reste. |
| C2 | **Rapport 16:9**, et la scène **se dimensionne en unités relatives** (`%`, `vw`, `vh`, `viewBox`), jamais en pixels fixes (pas de `1280px × 720px` en dur). Les **parents de `#stage`** n'ont **ni `transform`, ni `filter`, ni `overflow` qui rogne, ni taille fixe**. | La scène est agrandie plein cadre : un parent qui la rogne ou la déforme ferait une vidéo rognée. |
| C3 | **Un canvas se redimensionne avec sa scène** : à chaque `resize`, sa résolution interne suit sa taille affichée (`clientWidth × clientHeight`, multipliée par `devicePixelRatio`), puis il est redessiné. Un SVG en ligne garde son `viewBox`. | Le gros plan reste net en 1920×1080 (règle du détourage). |
| C4 | **Le temps vient d'une seule source** : l'horodatage reçu par `requestAnimationFrame(t)` ou `performance.now()`. **Interdits pour animer** : `setInterval`, `setTimeout`, CSS `@keyframes` / `transition` / `animation`, Web Animations (`.animate()`), SMIL (`<animate>`, `<animateTransform>`), `<video>`, GIF ou image animée, bibliothèque d'animation avec sa propre horloge. | Ces mécanismes ne suivent pas l'horloge virtuelle : la vidéo serait figée ou fausse. |
| C5 | **La page est une fonction du temps** : l'image à l'instant *T* dépend **seulement de *T*** (pas d'état qui s'accumule d'image en image, pas de `Math.random()` sans graine : un générateur à **graine fixe** pour les particules et les irrégularités). Chaque image se calcule **depuis** la position dans la chronologie (`position = (t − t0) / 1000`, repliée sur la durée du plan si la lecture boucle). | Le rendu doit être **identique** à chaque exécution, et la barre de temps (saut à un instant) doit marcher. |
| C6 | **Barre de lecture** : un `<input type="range" id="seek">` dont `min="0"` et **`max` = `DUREE` en secondes** (décimales permises, par exemple `4.76`), **égale** à la durée de l'audio arrondie au centième supérieur (voir « La durée du plan = la durée de la voix ») et à celle de l'en-tête ; pour un plan sans voix off, celle de la fiche. | Le notebook lit la durée de la vidéo ici : c'est elle qui fait la durée exacte, donc la vidéo se termine avec la voix. |
| C7 | **Bouton lecture / pause** : un `<button id="play">`. **La page peut démarrer seule ou attendre le clic, les deux sont acceptés** ; le bouton existe et un clic **lance** l'animation **et** l'audio depuis le début. | Le notebook clique dessus (certains plans attendent ce clic). |
| C8 | **Une seule balise `<audio>`** (celle du plan, en `data:audio/…;base64`), **sauf les plans sans voix off** (aucune). **`playbackRate` reste à `1`, toujours** : l'audio n'est jamais accéléré, ralenti ni coupé ; c'est la page qui dure autant que la voix (C6). | La voix et la vidéo ont la même durée ; aucun silence à la fin. |
| C9 | **Aucune dépendance à l'utilisateur** : rien qui exige souris, clavier, survol, focus ou taille de fenêtre particulière ; **aucune fenêtre** (`alert`, `confirm`, `prompt`), **aucun écran de chargement** ou bandeau qui recouvre la scène ; aucune requête réseau, aucun `localStorage` nécessaire. | La capture est automatique : une boîte de dialogue la bloquerait. |
| C10 | **Prête dès le premier dessin** : tous les SVG, images et l'audio sont **intégrés en `data:`** ; **polices système seulement** (aucun `@import`, aucun Google Fonts) ; la scène est complète dès le premier appel de `requestAnimationFrame`. | Le notebook ne laisse aucun temps d'attente au chargement. |
| C11 | **État final propre** : à la fin de la durée, la page est dans l'état final du plan (pas de saut, pas d'élément disparu à la dernière image). | La dernière image sert de raccord au plan suivant. |

**Squelette minimal** (la structure à respecter ; le reste est ton animation) :

> **Modèle : voir [Annexe A7](#annexe-a7) (en fin de document).**

**Ce que tu contrôles par programme avant chaque livraison** (un petit script, `controle_contrat.py`, que tu écris une fois dans ton espace de travail et que tu relances pour chaque page) :

1. **Structure** : `id="stage"` présent **une seule fois** ; `id="seek"` de type `range`, avec `max` = `DUREE` (durée de l'audio arrondie au centième supérieur ; durée de la fiche pour un plan sans voix) ; `id="play"` présent ; **une seule** `<audio` (aucune pour un plan sans voix off), dont la source est celle du bon plan.
2. **Mots interdits** (hors du code intégré des SVG et de l'audio) : aucun `setInterval`, `@keyframes`, `transition:`, `.animate(`, `<animate`, `<video`, `src="http`, `@import` ; aucun `Math.random` sans graine.
3. **Rendu piloté de l'extérieur**, avec l'**horloge de test** ci-dessous : tu charges la page dans un navigateur sans interface (Playwright), tu fais avancer le temps de 1/60 s à la fois, tu captures **`#stage`** à **0 s, au milieu et à la dernière image**. Tu vérifies que : (a) les captures **diffèrent entre elles** (l'animation avance, rien de figé) ; (b) **deux exécutions donnent la même image** à un même instant (C5) ; (c) la scène **remplit le cadre** et aucun bouton n'y apparaît (C1, C2).
4. **Résultat** : tu écris dans ta ligne de livraison **« Contrat de page vérifié. »** Si un contrôle échoue, **tu corriges la page (ou le moteur commun, une fois pour tous) avant de livrer**.

```javascript
// Horloge de test : à injecter AVANT le chargement de la page (page.add_init_script).
(() => {
  let now = 0, id = 0; const q = new Map();
  window.__vt = { step(dt) { now += dt; const cbs = [...q.values()]; q.clear();
                  for (const cb of cbs) { try { cb(now); } catch (e) {} } } };
  try { Object.defineProperty(performance, 'now', { value: () => now, configurable: true }); } catch (e) {}
  Date.now = () => 1.7e12 + now;
  window.requestAnimationFrame = cb => { q.set(++id, cb); return id; };
  window.cancelAnimationFrame = i => { q.delete(i); };
})();
// Ensuite : cliquer #play, puis appeler window.__vt.step(1000/60) autant de fois que nécessaire.
```

<a id="e14-9"></a>

### 14.9 · Plan qui continue le précédent : tu exiges le plan précédent

**Dans IngXAi**, la continuité est **déclarée** (`depend_de`) et **garantie par le logiciel** : il n'attribue la tâche qu'une fois les tâches dont elle dépend terminées, et il joint leur page à l'agent. Les points 1 et 6 ci-dessous se font donc **sans rien me demander** ; les points 2 à 5 (état final repris tel quel, raccord contrôlé, plan précédent jamais modifié) **s'appliquent tels quels**.

**Quand un plan continue le précédent, son début doit être parfaitement synchronisé avec la fin de celui-ci, sans aucun écart.** Un plan **continue** le précédent quand son `PlanN.txt`, sa fiche, sa ligne dans le scénario ou le storyboard montrent la **même scène** (même décor, mêmes personnages ou objets, même caméra qui poursuit son mouvement), quand il **réutilise** un asset du précédent (`_reutilise.txt`) ou quand un doute existe. **Dans le doute, tu le traites comme un plan qui continue.**

1. **Tu exiges le plan précédent avant d'écrire la moindre ligne.** Si la page du plan précédent n'est **pas dans cette conversation** (nouvelle session), tu me demandes, en **une phrase**, de te la donner (le lien de la page, ou le fichier `planN-1.html`). Si elle est déjà dans la conversation, ou si son lien est dans `animation_status.md`, tu l'utilises sans me la demander. **Tu ne commences pas le plan tant que tu ne l'as pas.**
2. **Tu lis l'état final du plan précédent**, pas une estimation : **position, taille et rotation de chaque élément**, **pose des personnages**, **état des écrans, cartes et jauges**, **caméra** (position, zoom, inclinaison, oscillation en cours), **ordre des calques**. Tu notes ces valeurs dans `animation_status.md`.
3. **Le plan commence exactement dans cet état** : chaque valeur de départ est reprise **telle quelle**, sauf ce que la fiche du plan change **volontairement** au tout début. Tu ne « reconstruis » pas le décor de mémoire ou à partir du storyboard.
4. **Tu contrôles le raccord** : tu captures la **dernière image du plan précédent** et la **première image du plan**, tu les compares de près (cadrage, échelle, position, détourage, états), et tu corriges tout écart non voulu **avant** de me livrer. Un saut visible au raccord est une erreur.
5. **Tu ne modifies jamais le plan précédent** (règle des plans validés) : si le raccord montre qu'il faudrait le changer, tu me le dis en une phrase et tu attends mon accord.
6. **Les liens des pages** de tous les plans validés sont dans `animation_status.md`, pour retrouver sans effort le plan précédent.

<a id="e14-10"></a>

### 14.10 · Le format que j'attends (à respecter à chaque livraison)

- **Une page par plan, `planN.html`** : **un seul fichier HTML autonome** (CSS et JavaScript dedans, SVG intégrés), **publié en artefact** (dans IngXAi : **livré comme fichier joint**, sans artefact ni lien). Une page ne dépasse pas 16 Mo ; les bibliothèques éventuelles viennent uniquement d'un hôte autorisé, en version précise. Les corrections se font **dans la même page** (même lien), jamais dans une seconde page.
- **Contenu de la page** : (1) l'en-tête du plan (nom, durée, caméra), (2) le moteur commun et le détourage, (3) les objets, du fond vers le devant, nommés `NN_nom` comme dans `assets/PlanN/`, (4) les éléments dessinés en code, (5) la chronologie complète, (6) un **lecteur** avec lecture / pause et barre de temps (`#play`, `#seek`, voir le contrat de la page), et une lecture en boucle de la durée du plan.
- **Un plan parlé = la durée exacte de sa voix** (durée de l'audio arrondie au centième supérieur, voir « La durée du plan = la durée de la voix ») ; la durée de `Sequences.md` ou de la fiche n'est qu'une approximation. Un plan sans voix off garde la durée de sa fiche. La boucle ne doit pas produire de saut visible quand c'est évitable.
- **Aucune phrase d'explication dans la page**, aucun « à compléter », aucun « idem plan précédent » : la page est complète à elle seule.
- **Nommage** : un objet = `NN_nom` ; le groupe = `Plan N` ; aucun nom en double.
- **Ma seule consigne par plan** : le lien de la page, **une ligne**, et, si besoin, **une phrase** sur ce que tu n'as pas pu vérifier.
- **Le résultat est une page web, pas un fichier vidéo.** Tu **ne produis jamais la vidéo** toi-même (c'est le notebook d'export, plus tard) ; **mais la page doit respecter le contrat de la page** (« Contrat de la page : la structure imposée »), pour que ce notebook la transforme **sans retouche**.

<a id="e14-11"></a>

### 14.11 · Vérifier avant de livrer

**Tu ne dis jamais « terminé » sans avoir regardé.** Avant de me donner le lien :

00. **Si le plan continue le précédent, tu contrôles le raccord** : tu captures **la dernière image du plan précédent** et **la première du plan** et tu les compares (voir « Plan qui continue le précédent »). Tu ne livres pas tant qu'un écart non voulu subsiste.
000. **Tu vérifies que tu as bien reçu et lu `Registre_exigences_animation.md` dans cette conversation** (voir la règle n°0). Si ce n'est pas le cas, tu **t'arrêtes**, tu me le demandes, et tu ne livres rien.
0. Tu **repasses le registre des exigences ligne par ligne** sur ce plan : pour chaque règle, tu vérifies qu'elle est respectée, et tu ne livres pas tant qu'une règle est violée.
0 ter. **Tu contrôles la synchronisation voix / vidéo par programme** : tu mesures la durée du fichier audio, tu vérifies que `DUREE` = cette durée arrondie au centième supérieur, que `seek.max`, l'en-tête et la constante de la page sont identiques, que `playbackRate` vaut `1`, et que la dernière image tombe à la fin de la voix (**aucun silence à la fin**). Tu écris « **Durée calée sur la voix : X s (fiche Y s).** » dans ta ligne de livraison.
0 bis. **Tu contrôles le contrat de la page par programme** (voir « Contrat de la page : la structure imposée ») et tu écris dans ta ligne de livraison : **« Contrat de page vérifié. »** Tu ne livres pas tant qu'un point du contrat échoue.
1. Tu **captures au moins 4 images** à des instants clés (début, milieu du mouvement principal, plan large ou état final, fin) et tu **les regardes vraiment, de près**.
2. Tu **compares** avec l'image du plan dans `storyboard/` : position, échelle, perspective, ordre des calques, cadrage au début du plan.
3. Tu **cherches toi-même** les défauts (personnage flottant, mauvaise échelle, élément devant ou derrière à tort, frange de détourage, animation qui se fige, saut au retour de boucle) : **je ne dois pas avoir à te les signaler**.
4. Un **mouvement trop faible ne compte pas** : s'il est invisible à l'écran, il est trop petit. Tu vises un mouvement lisible, puis tu le gardes « léger » par la lenteur et l'irrégularité.
5. **Le mouvement ne se fige pas** : si le temps est borné pour la caméra, les autres mouvements continuent jusqu'à la fin du plan.
6. Tu me dis **honnêtement ce que tu n'as pas pu vérifier**.

<a id="e14-12"></a>

### 14.12 · Le registre des exigences : ne jamais refaire une erreur, ne jamais oublier une demande

**Principe : tout ce que je te dis qui doit compter dans la suite doit être noté et respecté : les erreurs que j'ai dû te signaler, et aussi mes remarques, mes demandes de modification, mes détails et mes préférences.** Si j'ai dû te montrer du doigt un défaut, c'est une faute de ta part ; si j'ai dû te répéter une demande, c'en est une aussi. Ni l'un ni l'autre ne doit se reproduire, ni dans ce plan, ni dans les suivants, ni dans une autre session. Tu n'as pas de mémoire d'une conversation à l'autre : le fichier `Registre_exigences_animation.md` est donc **ta mémoire**, et tu le tiens avec rigueur. Il a **deux parties** : **A. Erreurs à ne plus commettre** et **B. Exigences, remarques et détails voulus**.

1. **Tu me le demandes d'abord, toujours, avant toute autre chose** (sauf dans IngXAi : le registre est dans le dépôt `Autoniax`, l'agent le clone, il ne le demande pas). **Au début de chaque session, et avant le premier plan que je te demande**, ta **première réponse** est : **« Envoie-moi d'abord `Registre_exigences_animation.md` (dans le dossier `Animation/` du projet). »** Tu le demandes **même si je t'envoie en même temps d'autres fichiers** (plans, pages HTML), et **même si je dis seulement « fais le plan N »**. **Tu ne commences aucun plan tant que tu ne l'as pas reçu et lu.** C'est, avec **le plan précédent** quand le plan continue (voir « Plan qui continue le précédent »), la **seule chose** que tu as le droit de me demander avant d'animer. Hors IngXAi, tu ne le cherches pas dans `ShaderiaxAnim` ou l'archive (il n'y est pas). S'il n'existe pas encore (première fois), tu le crées toi-même et tu me le livres.
2. **Tu le lis en entier**, puis tu le **repasses comme une liste de contrôle, en commençant par les priorités les plus hautes** : avant chaque nouveau plan, et avant chaque livraison (étape 0 de « Vérifier avant de livrer »). Tu fais le maximum pour qu'aucune erreur déjà notée ne revienne et qu'aucune demande déjà notée ne soit oubliée.
3. **Quand tu notes.** **Chaque fois que je te signale un défaut, une erreur ou une exigence non respectée, et chaque fois que je te fais une remarque, une demande de modification, un détail ou une préférence** (même petite), tu la notes **dans la même réponse**, **avant ou en même temps que la correction**, sans attendre que je te le demande. Ce que j'ai dit et que tu n'as pas noté est une faute de plus.
4. **Jamais de doublon : un sujet = une seule ligne.** **Avant d'écrire**, tu cherches si le sujet (même cause, même demande, même contrôle) est déjà dans le registre.
   - **S'il y est déjà** et que l'erreur est recommise, ou que je dois répéter la demande : **tu n'ajoutes pas de ligne**. Tu **augmentes sa priorité d'une étoile (★)**, tu mets à jour la colonne « Signalée » (plans et nombre de fois), tu précises la règle ou la portée si besoin, et tu retries le tableau **par priorité décroissante**.
   - **S'il n'y est pas** : tu ajoutes une ligne à **★**. Dans **A** (erreur) : le **plan**, **ce que j'ai vu de faux** (mes mots), **la vraie cause** (pas « j'ai oublié » : ce qui, dans ta méthode, a permis l'erreur), la **règle + le contrôle précis** qui l'aurait détectée avant moi. Dans **B** (exigence) : **ce que je veux, dans mes mots**, et **comment l'appliquer**.
   - **Si je change d'avis**, tu **modifies la ligne existante** (jamais deux lignes contradictoires) et tu notes « remplace : … ».
5. **La portée.** Chaque ligne dit si elle vaut pour **tous les plans**, une **famille d'éléments** (décor, personnages, caméra…) ou **un plan précis**. Une demande propre à un plan ne s'applique pas aux autres ; une règle qui vaut pour tous les plans, tu l'appliques **sans que je te la redise**.
6. **Les niveaux de priorité.** **★** : sujet noté. **★★ ou plus** : il est revenu ; tu cherches **la cause profonde** et tu **corriges le moteur commun ou le générateur** pour que cela devienne impossible, au lieu de corriger plan par plan, et tu me le dis en une phrase. **★★★ ou plus** : grave ; son contrôle est fait **en premier** avant chaque livraison et il est relu **en tête** à chaque plan.
7. **Tu me livres le registre à jour.** À chaque fois que tu l'as modifié, tu me le livres **comme fichier** (même nom), avec la correction, en **une ligne** (« registre à jour »). **Mon seul geste** : garder cette dernière version et te la renvoyer au début de la prochaine session. Tu me préviens de ce geste **avant** (une phrase), et tu ne me le fais faire qu'ici.
8. **Tu cherches seul les défauts de même famille.** Quand je signale un défaut sur un plan, tu **cherches le même défaut dans les plans déjà livrés et dans le plan en cours**, et tu le corriges **avant** que j'aie à le redire (échelle, perspective, ordre des calques, mouvement figé ou trop faible, objet non demandé…).
9. **Je n'ai jamais à te répéter une règle ou une demande déjà notée.**

<a id="e14-13"></a>

### 14.13 · Ménager mes crédits (règle de toute l'étape 14)

L'étape 14 est longue (N plans) : **je ne dois pas arriver à court de crédits avant le dernier plan**. Tu travailles donc de façon économe, **sans jamais sacrifier l'exactitude** :

- **Tu lis une fois, tu notes, tu ne relis pas.** Le README, `manifest.json` et les directives sont lus **une seule fois** ; tu en tires `animation_notes.md` (conventions, méthode de détourage, règles du moteur commun, pièges) et tu t'appuies ensuite sur lui.
- **Tu lis le strict nécessaire** : pour un plan, seulement sa fiche dans `Liste_assets_animation.md`, son entrée du registre, son `PlanN.txt` et le `speech.txt` de sa séquence, son image de `storyboard/` et ses fichiers de `assets/PlanN/`. **Jamais** les N fiches d'un coup (le scénario, lui, est lu **en entier une seule fois** et résumé dans `scenario_notes.md`), jamais un SVG en entier (tu lis son en-tête, ou tu le rends en petit).
- **Tu écris par script** : un petit programme (`generer_plan.py`) lit le manifest et la fiche et produit la page ; **le moteur commun** (caméra, détourage, recadrage, perspective, découpe d'un personnage en parties, lecteur) **sert à tous les plans** : tu le corriges une fois, tous les plans en profitent. Chaque plan reste du travail sur mesure pour sa chronologie, mais les parties répétées sont mises en commun.
- **Les petites modifications se font par édition de la page publiée** (remplacer un passage) plutôt qu'en tout régénérer.
- **Pas d'essais inutiles** : tu ne livres pas deux versions d'un plan « pour voir », tu ne refais pas un plan validé, tu ne livres pas un plan que tu sais incomplet. **Un plan correct du premier coup coûte moins cher que trois corrections.**
- **Réponses courtes** : le lien, une ligne, une phrase sur ce qui n'est pas vérifié, rien d'autre. Pas de récapitulatif, pas de tableau, pas de relecture à voix haute.
- **Tu me préviens avant un travail lourd** : si une étape va coûter nettement plus que la moyenne (un plan à très nombreux éléments, une réécriture de plusieurs plans), tu me le dis **en une phrase avant de la faire**, avec la raison et une alternative moins chère.
- **Tu travailles pour pouvoir reprendre** : après chaque plan validé, tu mets à jour `animation_status.md` (plans validés avec leur lien, plan en cours, décisions, pièges rencontrés), pour qu'une nouvelle session reparte **sans tout relire** : elle lit `animation_notes.md` et `animation_status.md`, pas toute l'archive.

<a id="e14-14"></a>

### 14.14 · Ce que contient la page d'un plan

Une **page complète par plan**, `planN.html`, qui **donne à elle seule l'animation entière du plan**. Elle contient :

- **tous les objets** du plan (fonds, personnages, groupes d'assets, parties décomposées, feuilles de sprites découpées, éléments en code), **rangés dans un groupe nommé** `Plan N`, chaque SVG étant **intégré** à la page ;
- **le détourage** de chaque SVG qui en a besoin ;
- **la chronologie** du plan : caméra, durée, placement initial de chaque élément, ordre des calques, et **toute la chronologie** de `Liste_assets_animation.md` (ce qui apparaît, bouge, change d'état, disparaît, à quelle seconde) ;
- **les fiches de code** (`NN_nom_code.md`, technique 4, éléments sans fichier média) **dessinées en JavaScript, complètes**, jamais laissées en description ;
- **les assets réutilisés d'un autre plan** (`_reutilise.txt`), repris au bon endroit avec la retouche demandée, jamais regénérés ni redessinés à la main ;
- **les éléments communs** (le moteur, le détourage) **inclus dans chaque page** : chaque page est **autonome**.

**Les valeurs viennent des fiches, jamais de ton imagination** : positions en % de la largeur (x) et de la hauteur (y), taille en % de la hauteur, rotation en degrés (sens horaire), image de 1672×941, durées de `Sequences.md`, couleurs et caméra de `Plan_animation.md`, **lecture par défaut** des points à trancher. Tu n'inventes aucun élément, tu n'en oublies aucun, tu n'ajoutes aucun son qui ne soit pas dans le fichier audio du plan (ni musique, ni bruitage), ni montage. **Tu ne dessines rien que je n'ai pas demandé** (objet dans une main, clavier animé…).

<a id="e14-15"></a>

### 14.15 · Comment on avance : un plan à la fois

1. Tu relis **la ligne du plan dans `scenario_notes.md` (et dans `Plan_animation.md` si un détail manque), avec le plan précédent et le suivant**, puis tu écris le plan **complet** (jamais un morceau « à compléter ») ; tu **vérifies tout ce qui peut l'être** avant de me le livrer (voir « Vérifier avant de livrer ») : fichiers cités existants dans le clone, durées et positions venant des fiches, rien en double, aucune erreur dans la page.
2. Tu me livres **le lien de la page**, avec **une ligne**, sans rien d'autre à faire pour moi.
3. Je regarde et je te dis : **« ça marche »**, ou ce que je vois de faux (une phrase, ou une capture).
4. Si quelque chose est faux, tu **corriges la même page** (même lien) et tu me redis en une ligne ce qui a changé. Tu n'enchaînes sur le plan suivant **qu'après mon « ça marche »**.
5. Ordre : **dans IngXAi, l'ordre est géré par le logiciel** (dépendances : une tâche n'est attribuée qu'une fois terminées celles dont elle dépend ; plans indépendants en parallèle). Sinon, de **Plan 1 à Plan N**, sauf si un plan en réutilise un autre qui n'est pas encore fait (tu fais alors le plan source d'abord, et tu me le dis en une phrase). Un plan sans asset à animer (`_rien_a_generer.txt`, `_reutilise.txt` seul) se traite aussi : tu me livres sa page, même courte.
6. Un plan qui réutilise ou continue un autre ne **casse jamais** un plan déjà validé : tu ne modifies un plan validé que si je te le demande.

**Aucun travail manuel pour moi** (règle de tout ce document) : pas de fichier à copier, de dossier à créer, de chemin à écrire, de SVG à préparer. Mon seul geste : regarder la page et te dire ce que je vois.

<a id="e14-16"></a>

### 14.16 · Fin de l'étape

Quand les N plans sont validés, tu me livres un bilan court : plans validés (avec leurs liens), plans qui en réutilisent d'autres, limites connues, et, si tu peux le faire, une page qui enchaîne les N plans. L'étape suivante est l'étape 15 (export des pages et métadonnées) ; le montage reste hors périmètre (l'audio a été généré à l'étape 13 bis).

---

> **Phase 7 – Publication (étape 15)**

<a id="e15"></a>

## Étape 15 : exporter les animations et préparer les métadonnées de la vidéo

Cette étape commence quand **les N plans sont validés** (étape 14). Elle a **deux livraisons indépendantes, et tu ne fais que celle que je demande** : **(A) le kit de publication YouTube**, `Metadonnees_video.html`, une page **courte** avec seulement ce qui se colle dans YouTube (titres candidats, description, chapitres, tags) **et le prompt de génération de la miniature** ; **(B) l'export** : identifier les pages `.html` de `Animation/`, les **zipper** et les **pousser** dans le dépôt dédié **`Export`** (`https://github.com/officecenter632-maker/Export`, branche `main`). `Export` est indépendant des autres dépôts : un seul commit, un nouvel envoi **remplace** le précédent. **Aucun travail manuel pour moi.** **(A) ne déclenche jamais (B)** : « les métadonnées » ne veut pas dire « l'export ».

**Hors périmètre** : le montage (logo, cartons, étiquettes), l'export en vidéo (fait ensuite par le notebook `html_to_video_kaggle.ipynb`, que je lance moi-même : **cette étape ne le produit ni ne le modifie**), et la **rédaction de la description** (cette étape en prépare la matière ; elle propose en revanche des **titres candidats**, en miroir des miniatures).

<a id="e15-1"></a>

### 15.1 · Ce que je te fournis

1. L'**arborescence réelle du projet** (chemin complet en première ligne, emojis inclus), qui montre le dossier `Animation/` avec ses `.html`. **Si je ne te l'ai pas donnée, ou si tu doutes qu'elle soit à jour, tu me la demandes avant d'écrire quoi que ce soit** : tu n'écris jamais un chemin de mémoire.
2. Comment je m'authentifie auprès de GitHub (`git` déjà connecté, ou jeton), comme pour `envoyer_storyboard.py`.
3. Mes décisions sur les **points à trancher** de la page de métadonnées (langue de publication, chaîne, public visé). Sans réponse, tu appliques la **lecture par défaut** notée dans la page (langue de la voix off générée à l'étape 13 bis, publication dans cette même langue).

<a id="e15-2"></a>

### 15.2 · Première partie : identifier les pages HTML générées

À partir de l'arborescence, tu repères **les pages animées de chaque plan** et tu me les listes dans un tableau `Plan | Fichier | État`, **avant d'écrire le script**.

- **Où** : seulement les `.html` placés **directement** dans `Animation/`. Les sous-dossiers (`_versions`…), les `.md` (`Registre_exigences_animation.md`, notes, statut) et tout autre fichier ne sont **pas** des pages de plan : ils sont listés comme exclus.
- **Comment on reconnaît le numéro** (les noms ne sont pas uniformes : `Plan 10 – un nerf de la guerre.html`, `plan12.html`, `Plan 5 – rendu animé (avec audio).html`) : le numéro est **l'entier placé juste après le mot « plan »** (sans tenir compte de la casse, avec ou sans espace), **jamais un autre nombre du titre** (`Plan 18 – règle à 50.html` est le plan 18). S'il n'y a pas le mot « plan », c'est le **premier entier compris entre 1 et N**. Un fichier dont le numéro est ambigu est signalé, pas deviné.
- **États** : « trouvé » ; « absent » (aucun fichier pour ce plan) ; « doublon » (deux fichiers ou plus pour le même numéro : le **plus récent** est retenu, les autres sont listés comme exclus, **sauf si l'arborescence ne permet pas de les départager : tu me poses alors la question**) ; « suspect » (taille anormalement petite).
- **Tous les plans de 1 à N doivent être « trouvés »**. Un plan absent bloque l'envoi (voir les contrôles), sauf si je le décide avec `FORCER`. **Tu ne produis aucune page toi-même ici** : les pages viennent de l'étape 14.

<a id="e15-3"></a>

### 15.3 · Deuxième partie : le script `envoyer_export.py`

Tu m'écris **un seul script Python**. **Même règle d'or qu'aux étapes 9, 11 et 13 : tu ne le réécris pas de zéro.** Tu pars du modèle `envoyer_storyboard.py` (contrôle de structure, dépôt neuf, un seul commit, push forcé, vérification de la branche distante, jeton jamais affiché) et tu ne changes que ce que ma situation impose : le chemin `PROJET` (copié de mon arborescence, emojis en codes `\U`), le dépôt `Export`, les contrôles de structure, la **sélection** des fichiers, et l'**envoi de plusieurs fichiers** (le modèle n'en pousse qu'un : le commit unique contient ici toutes les parties du zip et les deux fichiers du dépôt). Mêmes règles d'écriture : il s'exécute n'importe où, se lance depuis un éditeur sans argument ni question, un `print` qui ne plante pas, tu le **testes** (faux dossier `Animation`, doublon, plan manquant, page sans audio, faux dépôt `git` local) et tu le livres **dans un seul bloc de code**.

**Constantes** : `PROJET`, `DOSSIER_ANIMATION = PROJET / "Animation"`, `DEPOT_URL = "https://github.com/officecenter632-maker/Export.git"`, `BRANCHE = "main"`, `GITHUB_TOKEN = ""`, `NB_PLANS = N  # N = nombre de plans de la vidéo, calculé depuis Plan_animation.md`, `FORCER = False`, `TAILLE_PARTIE_MAX` (voir « Découpage »), et `METADONNEES_B64` (la page de métadonnées, intégrée au script pour que je n'aie **aucun fichier à placer**).

**Ce qu'il fait, dans cet ordre :**

1. **Identification** : mêmes règles que la première partie (numéro après « plan », plus récent en cas de doublon). Il liste dans le bilan **chaque fichier de `Animation/` non retenu, avec la raison**.
2. **Contrôles avant tout envoi** (en cas d'écart, il l'affiche et n'envoie rien, sauf `FORCER`) :

| Contrôle | Ce qu'il vérifie |
| --- | --- |
| Plans | Les N plans ont une page ; aucun numéro hors 1 à N ; aucun plan en double non résolu |
| Pages lisibles | Chaque page est non vide, commence par un `<!doctype html>` ou `<html`, contient `</html>` et une balise `<script` |
| Audio | Les pages des **plans parlés** contiennent **une seule** balise `<audio` avec une source `data:audio/` ; la page d'un plan sans voix off n'en contient pas |
| Autonomie | Aucune page ne charge de ressource distante (`src="http`, `href="http` vers un fichier, `@import url(http`) : un écart est signalé (avertissement, non bloquant) |
| Taille | Aucune page ne dépasse la limite d'un fichier GitHub (100 Mo), et aucune partie du zip ne dépasse `TAILLE_PARTIE_MAX` |
| Métadonnées | `METADONNEES_B64` se décode en une page HTML valide (`<!doctype html>`, `</html>`) |
| Secrets | Le garde-fou de l'étape 13 s'applique à la page de métadonnées : aucun jeton ni identifiant ; le fichier concerné est exclu et listé (fichier, ligne, nom de la variable, **jamais la valeur**) ; `FORCER` ne le contourne pas |

3. **Zip(s)** : les pages sont **copiées**, jamais modifiées ni déplacées ; les originaux restent dans `Animation/`. Chaque page est rangée sous un nom **normalisé** `animations/Plan01.html` … `animations/PlanN.html` (deux chiffres), le nom d'origine étant gardé dans le manifest. Dossier racine du zip : `Export/`.
4. **Découpage** : une page animée avec audio peut peser plusieurs Mo ; N pages dépassent donc facilement les **100 Mo** autorisés par GitHub pour un fichier. Le script remplit les zips **dans l'ordre des plans** (`Export_part01.zip`, `Export_part02.zip`…, **toujours numérotés, même s'il n'y en a qu'un**), avec un budget de **85 Mo non compressés** par partie (`TAILLE_PARTIE_MAX`), puis **mesure le zip réel** : si une partie dépasse **95 Mo**, il recommence avec un budget plus bas. Une page seule trop lourde pour GitHub arrête l'envoi et le dit.
5. **Manifest** : il écrit **`manifest_export.json`** (JSON UTF-8, `ensure_ascii=False`, chemins avec des `/`) :

> **Modèle : voir [Annexe A8](#annexe-a8) (en fin de document).**

   La **partie 1** contient aussi, à la racine de `Export/`, `Metadonnees_video.html` et `manifest_export.json`.
6. **Envoi** : même méthode que le modèle (dépôt neuf dans un dossier temporaire, **un seul commit**, push forcé, vérification de la branche distante, jeton jamais affiché), mais le commit contient **toutes les parties du zip**, plus, **à la racine du dépôt et non zippés**, `Metadonnees_video.html` et `manifest_export.json` : je peux ainsi les lire directement sur GitHub, sans ouvrir de zip. L'ancien contenu du dépôt disparaît. L'envoi peut être long (plusieurs centaines de Mo) : le script le dit avant de commencer. Il ne touche **jamais** aux autres dépôts.
7. **Bilan** : nombre de pages retenues et exclues (avec la raison), taille de chaque partie, résultat du push, lien de chaque zip et de la page de métadonnées. S'il n'y a aucun écart, il écrit « Aucun ecart. ».

**Liens** (le dépôt est public) :
- Page du dépôt : `https://github.com/officecenter632-maker/Export`
- Zips : `https://github.com/officecenter632-maker/Export/raw/main/Export_part01.zip` (puis `…part02.zip`)
- Métadonnées : `https://github.com/officecenter632-maker/Export/raw/main/Metadonnees_video.html`

<a id="e15-4"></a>

### 15.4 · Troisième partie : le kit de publication `Metadonnees_video.html`

**Principe : on veut seulement ce qui sert à PUBLIER sur YouTube, pas un dossier exhaustif.** La page est **courte** : l'utilisateur la lit en une minute, copie chaque bloc et publie. Tu n'écris ni transcription complète, ni liste de faits, ni tableau de noms, ni matière de recherche détaillée, ni identité visuelle : **rien qui ne soit un champ à coller dans YouTube** (ou la miniature). **Elle ne doit pas te prendre plus de temps que la rédaction des textes eux-mêmes.**

**Sources (lecture minimale)** : tu clones `ShaderiaxAnim` **une seule fois** et tu lis `directives/Plan_animation.md` (voix off, durées, parties) et `directives/Sequences.md`. Tu n'ouvres `scenario/`, `Liste_assets.md` ou `assets_base/` que pour les images de la miniature. **Si l'accès échoue, la règle de la zone « Erreurs de méthode à ne jamais refaire » s'applique.**

**Contenu imposé, dans cet ordre** (chaque bloc a son bouton « Copier ») :

| # | Bloc | Contenu |
| --- | --- | --- |
| 1 | **Titres** | **3 titres candidats** (modèle de titres de la chaîne), chacun avec son nombre de caractères ; chiffres et noms **repris de la voix off** |
| 2 | **Description** | **Prête à coller** : 2 à 3 phrases d'accroche (la 1re contient le mot-clé principal), les **chapitres** ci-dessous, 3 à 5 hashtags ; **aucun fait absent de la vidéo** |
| 3 | **Chapitres** | Une ligne par **partie** du scénario, au format `MM:SS Titre` ; horodatage = somme des **durées réelles des pages** (`seek.max`, égales aux durées des voix) des plans précédents, **calculée par script** ; le premier à `00:00` |
| 4 | **Tags** | Une ligne de mots-clés séparés par des virgules (500 caractères au plus), **seulement ce que la vidéo traite** |
| 5 | **Miniature** | **Projet ImGen (un JSON, en premier)**, puis **3 variantes** (A, B, C) avec, pour chacune : texte de l'image, titre associé, **prompt** et **images à joindre**, chaque zone avec son bouton « Copier ». Voir plus bas |
| 6 | **Points à trancher** | Au plus 3 lignes (langue de publication, ton), avec la **lecture par défaut** retenue |

**Hors contenu (ne les écris pas, sauf demande explicite)** : transcription par plan, tableau des faits, noms/lieux/dates/chiffres, interdits du scénario, matière de recherche, identité visuelle, « dossier complet ». Si un titre ou la description cite un fait, tu le **retrouves toi-même dans la voix off** avant de l'écrire ; **tu n'en fais pas une section**.

#### Le pattern de la chaîne : miniatures et titres (à suivre fidèlement)

Il vient des miniatures déjà publiées par la chaîne (« It's starting », « Doomsday », « Can't stop », « Fatal error », « Exposed », « It's happening again », « Too late », « Trapped », « You have no idea », « It's a trap », « Lost it all », « Google lies », « Dirty secret », « No escape », « $400,000 mistake »). **Tu ne t'en écartes pas** : une miniature de cette chaîne est reconnaissable au premier coup d'œil.

**La formule visuelle (constante sur toutes les miniatures de référence)**

| Élément | Règle observée |
| --- | --- |
| **Texte dans l'image** | **1 à 3 mots** (4 au plus, 20 caractères environ), **en haut**, sur une seule ligne centrée qui occupe **au moins 70 % de la largeur**, **capitales très épaisses** sans empattement, **blanc** avec un **épais contour sombre** et une légère ombre. **Un seul mot ou chiffre peut être accentué** en couleur (jaune ou rouge, par exemple `$400,000`). Le texte **fait partie de l'image générée** |
| **Personnage** | **Un seul personnage humain en illustration cartoon**, en **gros plan** (la moitié à plus des deux tiers de la hauteur), dans une **émotion extrême et lisible** : bouche ouverte, yeux écarquillés, sueur, larmes, mains sur la tête ou sur le visage. Placé d'un côté, souvent à gauche. Un personnage **inventé** (jamais la ressemblance d'une personne réelle) |
| **Menace ou objet-symbole** | **Un seul grand objet** qui résume le sujet, **de l'autre côté**, dans un **état dramatique** (une puce qui explose, un radar rouge, un cadenas brisé, une planète encerclée de débris, un bouton d'alarme). Il est **reconnaissable sans lire une ligne** |
| **Fond** | **Saturé et très contrasté** : dégradé du sombre vers le vif, **une dominante unique** (rouge ou orange pour l'alarme, bleu ou violet pour le piège et le secret) et **un accent complémentaire**, avec une **lueur ou un éclairage de contour** (néon, soleil, lumière d'alarme) |
| **Style** | Illustration **cartoon vectorielle**, **contours épais**, aplats, détails réduits au nécessaire. Jamais photo, jamais 3D, jamais un fond chargé |
| **Lisibilité** | **Un seul point d'intérêt dominant** et **trois éléments au plus** (personnage, objet, texte). La miniature doit rester claire **réduite à 170 px de large** |
| **Zone libre** | **Le coin bas droit** reste dégagé : la durée de la vidéo le recouvre |

**Le texte de l'image : quatre familles, trois mots-clés au plus par miniature.** Il dit **l'émotion et l'enjeu**, jamais le sujet en détail (c'est le rôle du titre).

| Famille | Mots observés |
| --- | --- |
| **Alarme, imminence** | `IT'S STARTING`, `DOOMSDAY`, `TOO LATE`, `IT'S HAPPENING AGAIN` |
| **Piège, impossibilité** | `CAN'T STOP`, `TRAPPED`, `NO ESCAPE`, `IT'S A TRAP` |
| **Révélation** | `EXPOSED`, `DIRTY SECRET`, `GOOGLE LIES`, `YOU HAVE NO IDEA` |
| **Perte, erreur** | `LOST IT ALL`, `FATAL ERROR`, `$400,000 MISTAKE` |

**Le titre, en miroir de la miniature.** Les 16 titres observés suivent le même modèle, que la page reprend pour les **titres candidats** :
- **Anglais**, **35 à 90 caractères**, **une phrase** (parfois deux très courtes : « Karma Just Hit Roblox. Hard. »), sans point final sauf effet voulu ; la **première moitié contient l'entité ou le mot-clé** de recherche.
- **Un enjeu concret** : chiffre, durée, somme, lieu (« Lost $35 BILLION in 72 Hours », « JUST 4 Minutes to WW3 », « 120° Heat », « 50 Insane Facts », « $80,000 Trucks on $70,000 Salary »), **plus une tension non résolue** : l'alarme, la question ou l'avertissement.
- **Un ou deux mots en capitales pour l'emphase** (`BROKEN`, `JUST`, `BILLION`, `WAY BIGGER`, `INCOGNITO`, `ROGUE`), jamais le titre entier.
- **Formes qui reviennent** : « How … » ; « [Sujet] is [état alarmant] » ; l'avertissement « You Need to stop … Right Now » ; « [A] vs [B] - Follow The Math! » ; le déroulé « … Hour by Hour … » ; la liste « 50 Insane Facts … ».
- **Le titre ne répète jamais le texte de la miniature** : la miniature donne l'émotion (`EXPOSED`), le titre donne le fait concret. Ensemble, ils ouvrent une **question** à laquelle seule la vidéo répond.
- **Le titre et la miniature tiennent leur promesse** : tout ce qu'ils annoncent est dans la vidéo, **aucun chiffre ni fait absent de la voix off**. On accroche fort, on ne ment pas.

#### La miniature : comment la construire et son prompt de génération

**Marche à suivre (dans cet ordre, sans en sauter)**

1. **Trouver le moment d'enjeu** : tu relis la voix off des plans 1 à 3 et le plan du moment fort, et tu repères **le plan ou le fait qui fait peur, choque ou intrigue le plus** (ce que le public viendra voir). Tu en tires **l'émotion** du personnage et **l'objet-symbole**.
2. **Choisir trois familles de texte différentes**, une par variante (A, B, C), puis **le mot-pivot** de chacune. Les variantes **diffèrent par le texte, la composition et la dominante de couleur** (pas seulement par un détail), pour que la comparaison compte.
3. **Écrire le texte** : 1 à 3 mots, pris dans la famille, **fidèle au contenu de la vidéo**. Test : si on lit seulement ce mot, **on ressent l'enjeu** sans savoir le sujet précis.
4. **Composer** selon la formule ci-dessus : personnage à gauche ou à droite, objet-symbole à l'opposé, texte en haut, fond saturé à une dominante, coin bas droit libre.
5. **Écrire le prompt** (modèle ci-dessous), puis **le titre candidat** de la variante.
6. **Contrôler** (tableau plus bas), avant de livrer.

**Pour chaque variante, la page donne un bloc de ce modèle :**

> **Modèle : voir [Annexe A9](#annexe-a9) (en fin de document).**

- Les **images à joindre** ont leur **chemin complet** (lecteur, dossiers et nom de fichier, jamais relatif) ; **tu ne décris pas leur visuel**, on cite leur nom. Elles donnent **l'identité** du personnage et de l'objet ; **l'expression, l'éclairage et le texte sont poussés** comme dans le pattern.
- **Si l'arborescence montre un dossier de miniatures de référence** de la chaîne, tu en joins une ou deux en **références de style** (`local`, dans la limite de 10 références) ; sinon, le pattern écrit ci-dessus suffit. Tu ne me demandes pas ces images.
- **Titre candidat** : un par variante, **respectant le modèle de titres**, avec ses chiffres et ses noms **repris de la voix off**.

**Le projet ImGen est le livrable principal de la miniature : il est dans la page, EN PREMIER, avant les variantes.** Un seul JSON (`projet` `<nom>_miniatures`), zone de copie + bouton « Copier le JSON », livré aussi comme fichier `miniature_imgen.json`, au même format que le `projet_imgen.json` de l'étape 8, **une image par variante** (`Miniature_A`, `Miniature_B`, `Miniature_C`) : `chemin_sauvegarde` = `<racine du projet>/Miniatures/Miniature_A.webp` (dossier `Miniatures`, **jamais `Export`** : l'export est une autre livraison ; avec des `/`, emojis recopiés tels quels), `prompt` **identique** à la rubrique « PROMPT DE GÉNÉRATION » de la page (texte de l'image compris), `references` : l'**image du plan** en `depot` (dépôt `Storyboard`, chemin vu dans le zip que tu **clones et vérifies**, casse exacte) et les **assets** en `local` (chemins complets de `assetsBrute1`), **jamais la même image dans les deux**, 10 références au plan au plus. Tant qu'ImGen génère, le dépôt `Storyboard` doit contenir `Storyboard.zip` à jour. **La page garde aussi, par variante, le prompt seul et les chemins des images, chacun avec son bouton « Copier »**, pour une génération à la main. Si tu ne peux pas passer le JSON dans `parse_project_text` d'`ImGen.pyw`, tu le dis.

**Ce que tu contrôles avant de livrer la section** :

| Contrôle | Ce qui est attendu |
| --- | --- |
| Texte | 1 à 3 mots (4 au plus), 20 caractères au plus, en capitales, **écrit à l'identique** dans le bloc « TEXTE », dans le prompt et dans le JSON ; **aucun texte en dehors de celui-là** |
| Familles | Les trois variantes sont de **trois familles différentes** (alarme, piège, révélation, perte), avec chacune sa composition et sa dominante |
| Formule | Chaque prompt contient : **un seul personnage** cartoon à l'émotion nommée, **un seul objet-symbole** dans un état dramatique, un fond à **une dominante** avec codes couleur, la **position du texte**, le **coin bas droit libre**, « lisible à 170 px », « aucun logo réel » |
| Promesse | Le texte et le titre candidat ne contiennent **aucun fait absent de la voix off** ; le titre **ne répète pas** le texte de l'image |
| Titres | Chaque titre fait 35 à 90 caractères, suit l'une des formes du modèle, a un enjeu concret et **un ou deux mots** en capitales |
| Références | Chaque chemin `local` existe dans l'arborescence ; chaque chemin `depot` existe dans le `Storyboard.zip` cloné, casse exacte ; aucune image n'est à la fois en `local` et en `depot` |
| ImGen | Le JSON passe `parse_project_text` d'`ImGen.pyw` **sans erreur** |

**Après la génération** : quand j'ai généré les trois miniatures, **je te les envoie** (mon seul geste, et il est facultatif : sans elles, la page reste valable). Tu les regardes **à pleine taille puis réduites à 170 px de large** et tu me donnes un **bilan court, limité aux problèmes graves** : texte **mal orthographié ou illisible**, personnage sans émotion lisible, plusieurs points d'intérêt, coin bas droit chargé, logo ou ressemblance avec une personne réelle. Un défaut grave se règle par le **JSON de réinitialisation** (comme à l'étape 9) et un **prompt renforcé**, livrés dans la même réponse. Tu recommandes **la variante la plus convaincante**, en une phrase et avec la raison. Les défauts mineurs ne sont pas signalés.

#### Règles d'écriture de la page

- Un seul fichier HTML, **CSS et JavaScript dedans**, UTF-8, aucune ressource externe, lisible en mode clair et sombre, zones de copie en police à chasse fixe.
- **Un bouton « Copier » par zone**, avec le gestionnaire de la règle de l'étape 9 (`execCommand("copy")` d'abord, directement dans le clic ; `navigator.clipboard` en plan B).
- **Les durées et horodatages sont calculés par script** à partir des **durées réelles des pages** (`seek.max` de chaque `planN.html`), pas de `Sequences.md`. Les textes (titres, description, tags) sont **rédigés par toi**, pas générés par un gros script de contenu.
- **Aucune information inventée** : un doute va dans « Points à trancher ».

#### Ce que tu contrôles avant de livrer (court)

| Contrôle | Ce qui est attendu |
| --- | --- |
| Chapitres | Croissants, le premier à `00:00`, le dernier avant la durée totale (somme des durées réelles des pages) |
| Titres | 35 à 90 caractères, un enjeu concret, 1 à 2 mots en capitales, **chiffres et noms retrouvés dans la voix off** |
| Miniature | Le tableau de contrôle de la miniature ci-dessus ; le JSON passe `parse_project_text` d'`ImGen.pyw` |
| Page | Chaque bouton « Copier » a sa zone ; aucune ressource externe ; aucun jeton ni identifiant |

**Pas de contrôle de couleurs, pas de `node --check` détaillé, pas de comparaison de transcription** : ils n'ont pas d'impact sur la publication. Tu me dis honnêtement si tu n'as pas pu essayer la page dans un vrai navigateur.

<a id="e15-5"></a>

### 15.5 · Ce que tu fais, dans l'ordre

**Règle n°0 de l'étape 15 : tu ne fais QUE ce que je demande.** L'étape 15 a **deux livraisons indépendantes** : **(A) le kit de publication** (`Metadonnees_video.html`) et **(B) l'export** (`envoyer_export.py`, dépôt `Export`). Si je dis « les métadonnées », « les infos pour YouTube » ou « la miniature », tu fais **(A) seulement** : tu n'identifies pas les pages HTML, tu n'écris pas `envoyer_export.py`, tu ne le mentionnes pas. Tu ne fais (B) que si je le demande (« l'export », « envoie les pages »). **Si une demande est ambiguë, tu fais la plus petite des deux et tu le dis en une phrase.** Si j'écris « stop » ou que je te reproche de dépasser ma demande, tu **arrêtes tout** ce qui n'a pas été demandé et tu livres immédiatement ce que tu as pour (A).

**Pour (A), le kit de publication :**

1. Tu clones `ShaderiaxAnim` (une fois), tu lis `Plan_animation.md` et `Sequences.md`.
2. Tu rédiges les blocs 1 à 4 et 6, puis tu construis la miniature (bloc 5).
3. **Tu livres une première version tout de suite**, avec les blocs 1 à 4 et 6 (titres, description, chapitres, tags), **avant** de faire la miniature : l'utilisateur peut publier sans attendre. La miniature suit comme **seconde livraison**, dans le même fichier mis à jour.
4. Bilan de **deux lignes** : ce qui est livré, ce qui reste à trancher.

**Pour (B), l'export (seulement si demandé) :**

1. **Tu me demandes l'arborescence** si tu ne l'as pas, puis tu me donnes le **tableau des pages identifiées** (première partie), en signalant les plans absents, les doublons et les noms ambigus. **Tu n'écris le script qu'une fois ce tableau sans problème bloquant**, ou après mes décisions.
2. Tu écris **`envoyer_export.py`** (avec `Metadonnees_video.html` intégrée en `METADONNEES_B64` si elle existe déjà), tu le testes et tu le livres dans un seul bloc de code, avec la consigne : « lance-le par Run dans ton éditeur et dis-moi quand c'est fait ». **Pas d'autre geste de ma part.**
3. Quand je te dis que c'est fait, tu **télécharges** les zips et les deux fichiers du dépôt `Export` et tu **contrôles par programme** : chaque zip s'ouvre (`testzip`) ; les N pages sont présentes, aux bonnes parties ; taille et `sha256` identiques au manifest ; les pages des plans parlés contiennent leur audio, celles des plans sans voix off non ; aucun fichier en trop. Bilan court, limité aux problèmes graves. Pour un écart, je relance le **même script**.

**Règle de toute l'étape** : tu ne signales pas les défauts mineurs. Seules les erreurs graves (plan manquant, page vide, audio absent, zip corrompu, fichier trop lourd) méritent d'être remontées.

---

# Partie D – Contrôle final

<a id="controle-final"></a>

## Contrôle final

- [ ] Étape 0 : le sujet a été choisi **à partir des données de scraping** (dédoublonnage par `id`, regroupement par thème, mesure de l'intérêt, filtre « Infographics Show »), et `Sujet_choisi.md` a été livré après mon choix.
- [ ] Étape 0 bis : la liste de liens est **100 % Reddit**, tirée de l'archive de l'étape 0 (`permalink`), **tous** les liens ont été lus, chaque chiffre de `Dossier_sujet.md` a une **source**, les contradictions sont listées et tranchées, et les faits de ta mémoire sont séparés et signalés.
- [ ] Étape 0 ter : le speech est en anglais, dans le style des speechs de référence, et `Plan_animation.md` suit **la procédure « Copier la créativité du JSON, ne rien inventer »** : annexe E (une ligne par plan, recette, `id` de règles, ce qui est copié), annexe F (passages mal couverts, recettes non utilisées avec la raison), **script de contrôle lancé et résultat donné** (tous les `id` existent, au moins une règle par plan, aucune règle d'archive, valeurs conformes), **aucun visuel ni aucune logique inventés**.
- [ ] Étape 0 ter (livraison) : phases respectées (avis, structure, speech, plan idée par idée), **un seul fichier** `Plan_animation.md` **livré en entier après chaque idée**, section **Suivi** à jour pendant le travail (idées « fait et livré », état du dernier plan, fil rouge, règles utilisées) et **retirée à la clôture**, structure toujours **identique** au speech et au plan (annexe G), et plus aucune partie « (à faire) » dans le fichier livré à l'étape 1.
- [ ] Étape 1 : chaque asset vient d'un plan, aucun n'est inventé, et les éléments prescrits par les recettes et règles citées (annexe E) sont dans la liste.
- [ ] **Tous les envois sur Git ont été faits par les scripts** (sélection, contrôle, zip, push, vérification) : aucun zip glissé dans Lexiax, aucun clic sur « Push sur GitHub », aucune commande `git` tapée par moi.
- [ ] **Je n'ai eu à faire aucun travail manuel** : aucun fichier copié, déplacé, renommé ou rangé à la main, aucun dossier créé à la main ; mon seul geste a été de lancer les scripts livrés.
- [ ] La collecte Lexiax a été faite en **une seule passe** : un seul script, un seul zip, tous les assets.
- [ ] Le zip a été téléchargé depuis https://github.com/officecenter632-maker/ImageReferenceData et sa **structure a été vérifiée** (assets, mots, images, `index.json`) par rapport à la recherche.
- [ ] Peu de mots par asset (3 à 5 pour un élément clé, 2 à 4 pour un petit élément), tous précis, sans saturation.
- [ ] Le fichier `Liste_assets.md` a été envoyé à l'étape 1.
- [ ] Chaque asset de la liste de l'étape 1 est couvert : soit par son propre dossier (élément clé), soit par une planche (petit élément).
- [ ] Chaque dossier contient un sous-dossier `generation`.
- [ ] Un élément clé a exactement deux fichiers : `reference.<extension>` et `prompt.txt`.
- [ ] Une planche a une image de référence par petit élément, plus un seul `prompt.txt` qui dit quelle référence correspond à quel élément.
- [ ] Aucun nom de dossier ne contient `\ / : * ? " < > |`.
- [ ] Chaque prompt est complet et correspond à son asset ou à sa planche.
- [ ] Un seul `copier_assets.pyw`, livré à la racine du lot 1 (donc à la racine de `assets`) : grille « label + Copier » (label vert quand l'image générée existe), bouton « Move » (Permuter, Valider) qui range et renomme les images d'après leur dossier, fenêtre étirée en largeur ; il a été testé sur de faux dossiers.
- [ ] Le travail a été **livré par lots** (`assets_lot_NN.zip`), avec `Images_deja_validees_NE_PAS_RETRIER.md` à jour à chaque lot.
- [ ] Une fois les images générées, l'**arborescence réelle** du dossier `Assets` (chemin complet inclus) a été fournie et comparée à `Liste_assets.md`.
- [ ] Le script `collecter_images.py` utilise les **chemins et noms de fichiers réels** de l'arborescence (chemin en dur, dictionnaire `IMAGES`), se lance depuis un éditeur sans ligne de commande, a été testé, puis livré en un seul bloc de code, à placer dans le dossier parent de `assets`.
- [ ] Après exécution, les images ont été **copiées** (les originaux restent dans `assets`) : `assetsBrute1` contient une image par asset, nommée d'après son dossier, plus `index.csv` avec la colonne `chemin_copie`, et le bilan ne signale aucun écart.
- [ ] Le zip produit s'appelle `assetsBrute1.zip` (puis `assetsBrute2`, etc. pour une nouvelle version) et contient un dossier du même nom avec les images copiées et `index.csv`.
- [ ] `assetsBrute1.zip` a été poussé sur GitHub (par le script de l'étape 5, sans aucun geste manuel) et téléchargé au lien direct de l'étape 6 ; le checkup (structure, 30 images, comparaison aux prompts) a été fait et son bilan par asset m'a été remis.
- [ ] Le découpage en **séquences** a été proposé puis **validé par moi** avant toute création de dossier.
- [ ] Le dossier `Storyboard` contient un dossier `sequenceN` par séquence, chacun avec `speech.txt` (voix off mot pour mot, une ligne par plan) et un `PlanN.txt` par plan (tous remplis). Il n'y a pas de dossier `temp`.
- [ ] Les plans sont numérotés de façon **continue de 1 à N**, sans réinitialisation ; chaque prompt rappelle le numéro d'origine du scénario.
- [ ] Chaque `PlanN.txt` liste les images à joindre (assets, et l'image du plan précédent de la même séquence), donne le prompt et précise que l'image ne contient aucun texte ni logo.
- [ ] Les images sont posées dans le dossier de leur séquence, dans l'ordre de chaque séquence, avec l'image du plan précédent jointe à chaque plan suivant. Aucune validation ni vérification : c'est un storyboard pour se faire une idée.
- [ ] Pour ImGen : j'ai fourni l'arborescence réelle de `Storyboard` (et de `Assets` si elle a changé) et le lien du dépôt GitHub, qui contient le zip des assets (aucun autre push pendant la génération).
- [ ] `projet_imgen.json` contient N images (`Plan1` à `PlanN`), chacune avec son chemin de sauvegarde complet en `.webp` dans `Storyboard\sequenceN`, son prompt identique à celui de `PlanN.txt`, et ses références (assets en `depot` avec les chemins vus dans le zip, plan précédent et plans repris en `local` en `.webp`, jamais la même image dans les deux, 10 références au plus par plan).
- [ ] Le JSON a passé `parse_project_text` d'ImGen sans erreur, tous les chemins du dépôt ont été vérifiés par clonage et extraction du zip, et les images sont ordonnées par vagues de dépendance, avec le plan qui ouvre chaque vague indiqué dans le bilan.
- [ ] Premier essai fait sur `Plan1` puis `Plan2` (référence reçue, format d'enregistrement vérifié) avant de lancer les N plans.
- [ ] `envoyer_storyboard.py` a été **recopié du modèle du Director** (aucune réécriture) : seuls le chemin, les compteurs et le dépôt ont été adaptés ; une demande de mise à jour renvoie ce même modèle.
- [ ] J'ai fourni l'**arborescence réelle** du projet (chemin complet inclus) ; `envoyer_storyboard.py` utilise ce chemin en dur, a été testé, et a été livré en un seul bloc de code. Il ne zippe que le storyboard (`Sequences.md`, `speech.txt`, `PlanN.txt`, images des plans) et pousse vers le dépôt dédié **`Storyboard`** (pas `ImageReferenceData`) : `assetsBrute1.zip` reste intact, et j'ai gardé ma copie locale de `assetsBrute1`.
- [ ] `Storyboard.zip` a été poussé sur GitHub dans le dépôt `Storyboard` par `envoyer_storyboard.py` (contrôle de structure passé avant l'envoi), téléchargé au lien direct de l'étape 9, et sa structure a été vérifiée (S séquences, N `PlanN.txt`, N images, S `speech.txt`) ; **les images suspectes (noires, blanches, vides, minuscules, de mauvaise taille, ou qui ne correspondent pas à leur plan) ont été cherchées par programme puis à l'œil, et listées dans un tableau avant l'analyse** ; les écarts m'ont été signalés avant l'analyse, et aucun plan suspect n'a été analysé avant d'être regénéré.
- [ ] Les **défauts de détail** (texte ou chiffre dessiné, élément coupé, en trop, déformé, mauvaise pose) n'ont **pas** fait regénérer d'image : chacun est corrigé dans le prompt concerné et listé dans la section G du registre. Seuls les écarts bloquants (image noire, blanche, vide, sans rapport avec son plan) sont allés dans `reinitialisation_imgen.html`.
- [ ] **Avant la passe d'inventaire**, je t'ai confirmé si j'avais regénéré les images signalées ; si oui, tu m'as **renvoyé `envoyer_storyboard.py` en entier**, j'ai poussé, tu as **re-téléchargé** `Storyboard.zip`, refait les contrôles et validé (ou renvoyé en vague) chaque plan regénéré. Aucun prompt n'a été écrit à partir d'une image périmée.
- [ ] Pour chaque plan « à regénérer » ou « à confirmer », `reinitialisation_imgen.html` a été livré **dans la même réponse que le tableau des écarts**, sans que je le demande : une carte par vague (zone de texte en lecture seule + bouton « Copier »), JSON générés par script, passés dans `parse_reset_json` d'ImGen sans erreur ni avertissement, une raison par plan, vagues ordonnées selon les `references.local`, plans « à confirmer » à part, et prompts fautifs corrigés d'abord.
- [ ] **Avant tout prompt**, les N plans ont été parcourus asset par asset et `Registre_elements_animation.md` a été livré (**sans attendre ma validation**) : pour chaque asset, sa configuration et son rôle dans chaque plan, la technique choisie (tel quel, calque séparé, décomposé, animation en code, feuille de sprites, nouvelle configuration), le schéma de décomposition (sous-assets, points d'attache, zones cachées, mouvements, calques), les feuilles de sprites (grille, images, cadence), les fiches de code, le plan source, les plans qui le réutilisent et les retouches de montage ; les fonds ; les plans à regénérer.
- [ ] Chacun des N plans a été **regardé image par image**, visualisé comme une suite de scènes (de la fin du précédent au début du suivant), et chaque chose visible est classée : FOND (statique), ASSET (dynamique) ou MONTAGE, sans rien d'oublié ni d'inventé. Le speech n'a servi qu'à comprendre la scène, pas à caler les plans.
- [ ] L'archive `animation_lot_NN.zip` a un dossier par plan du lot ; chaque dossier a un JSON par **nouvelle** génération (fond vide, asset ou groupe d'assets), ou `_reutilise.txt` / `_rien_a_generer.txt` ; chaque JSON a `nom`, `prompt` et une seule référence `depot` (l'image du plan dans le dépôt `Storyboard`, casse exacte), sans `chemin_sauvegarde`.
- [ ] Un élément qui revient dans plusieurs plans est **généré une seule fois**, dans le dossier de son plan source ; les autres plans écrivent « réutilise `PlanN/NN_nom` » avec la retouche de montage, et ne reçoivent un nouveau JSON que pour une **variante** (autre pose, autre état).
- [ ] Les feuilles de sprites sont demandées en **une image à grille régulière** (cellules de même taille, même ancrage), et les éléments en code ont une **fiche de code** complète à la place d'un JSON d'image.
- [ ] Chaque prompt d'asset donne la couleur de détourage (vert `#00FF00` par défaut), « aplat », « sans ombre », « aucun texte » ; chaque prompt de fond liste les éléments à retirer et les zones à reconstruire.
- [ ] `Liste_assets_animation.md` a une fiche complète par plan (ce qui se passe, fond, assets avec tous leurs champs, chronologie, montage, couverture, points à trancher), livrée **par lots cumulatifs**, et les contrôles programmatiques sont passés (couverture, JSON valides, références existantes dans `Storyboard.zip`, noms sans caractère interdit).
- [ ] Le travail a été **livré progressivement** (tous les 3 plans environ, archive cumulative) avec `asset_profond_status.md` à jour, pour pouvoir reprendre dans une autre session.
- [ ] Les lots ont été enchaînés sans attendre ma validation (le registre non plus n'a pas attendu ma validation) ; ce que j'ai corrigé a été mis à jour dans la fiche **et** dans le JSON, sans changer les noms de fichiers ; aucune image n'a été générée par l'IA.
- [ ] `AssetAnimation.zip` contient un dossier racine `AssetAnimation/` avec exactement N dossiers `Plan1` à `PlanN`, les JSON, fiches de code et fichiers `_reutilise.txt` / `_rien_a_generer.txt` des lots **recopiés sans modification**, et rien d'autre ; les contrôles programmatiques (dossiers, JSON, références dans `Storyboard.zip`, fichiers, `testzip`) sont passés.
- [ ] J'ai fourni le **chemin réel** et l'arborescence de `AssetAnimation` ; `projet_imgen_assets.json` a une image par fichier JSON de génération, avec `nom`, `prompt` et `references` identiques au JSON d'origine, et un `chemin_sauvegarde` en `.webp` à côté du JSON, dans le bon dossier de plan ; il a passé `parse_project_text` d'ImGen, sans vague ni référence locale.
- [ ] Premier essai fait sur la première image du `Plan1` puis du `Plan2` avant de lancer toutes les générations.
- [ ] Étape 11 : j'ai fourni l'arborescence réelle du dossier des assets d'animation générés ; le script d'envoi a poussé le zip dans `Assets_Animation`, tu l'as téléchargé et contrôlé, et tu m'as signalé **uniquement les générations graves** (avec `reinitialisation_imgen.html` si besoin), sans parler des défauts mineurs.
- [ ] Étape 12 : la vectorisation commence seulement quand plus aucune génération grave ne reste ; j'ai fourni l'**arborescence réelle** de `AssetAnimation` (tu me l'as demandée si tu ne l'avais pas) ; `projet_gensvg.json` a une ligne par image `.webp`, avec `nom` identique à celui de l'étape 10, `source.depot` (dépôt `Assets_Animation`, chemin vu dans le zip, jamais `local`) et `chemin_sauvegarde` (chemin sur mon PC en `.svg`), a passé `parse_project_text` de GenSVG sans erreur, et un premier essai a été fait sur `Plan1` puis `Plan2`.
- [ ] Étape 13 : j'ai fourni l'**arborescence réelle** du projet (tu me l'as demandée si elle manquait) ; mes décisions sur les points à trancher sont dans le `README.md`, ou la lecture par défaut y est notée.
- [ ] Étape 13 : `envoyer_animation.py` a été **recopié du modèle `envoyer_storyboard.py`** (seuls chemins, contenu, zip et dépôt adaptés), testé, livré en un seul bloc de code ; ses contrôles (N plans, un `.svg` par `.webp`, SVG lisibles, aucun `.part*`, N images de storyboard, documents présents) sont passés avant l'envoi.
- [ ] Étape 13 : `manifest.json` donne, pour **chaque SVG**, `chemin_zip`, `chemin_relatif` et `taille` (plus les images du storyboard) ; le script les a générés à partir de `PROJET` et a vérifié que les fichiers existent sur mon disque ; tu ne me demandes **jamais un chemin**.
- [ ] Étape 13 : `AnimationData.zip` a été poussé dans le dépôt `ShaderiaxAnim` (un seul zip, un seul commit) et contient `assets/` (N dossiers `PlanN`), `directives/` (les quatre documents, `Liste_assets.md`, `Director.md`), `scenario/` (S `speech.txt`, N `PlanN.txt`), `prompts_assets/`, `assets_images/`, `assets_base/`, `storyboard/` (N images), **`audio/` (P audios, les `PlanN` des plans parlés, après l'étape 13 bis)**, `README.md` et `manifest.json`, **sans montage** ; **rien n'a été omis en silence** : le bilan du script liste tout ce qui n'est pas envoyé, avec la raison.
- [ ] Étape 13 : le zip a été téléchargé et contrôlé (structure, références, rendu des SVG ; le fond de détourage est retiré plus tard, dans l'animation) ; le bilan est limité aux problèmes graves ; **aucun code d'animation n'a été écrit à cette étape**.
- [ ] Étape 13 : le garde-fou des secrets est passé sur tous les textes ajoutés (fichier concerné exclu et listé, jamais la valeur affichée).
- [ ] Étape 13 bis : j'ai fourni l'**arborescence réelle** du projet et mes décisions (langue, voix) ; tu as **cloné le dépôt `Storyboard`** toi-même, relu les règles de traduction et de balisage de l'étape 13 bis, et traduit puis balisé **un speech par plan** (P plans parlés ; les plans sans voix off ignorés) : une seule balise au début de chaque segment, balises autorisées uniquement, durées contrôlées à 2,5 à 3 mots par seconde, dépassements signalés.
- [ ] Étape 13 bis : j'ai reçu **`Speech_audio.zip`** (S `speech.txt` modifiés, format `PlanN : [balise] texte`), **`ecraser_speeches.py`** (chemin en dur, textes intégrés, sauvegarde des originaux dans `Audio\speech_originaux_fr`, testé, un seul bloc de code, aucun geste manuel) et **`projet_audiogen.json`** (P speeches les `PlanN` des plans parlés, `chemin_sauvegarde` en `.wav` dans `Audio/sequenceN`) ; **aucune page HTML** n'a été produite.
- [ ] Étape 13 bis : `projet_audiogen.json` a passé `lire_liste_speech` d'AudioGen sans erreur ni avertissement, ses textes sont identiques aux `speech.txt` modifiés, et un **premier essai** a été fait sur `Plan1` puis `Plan2` avant de générer les P audios.
- [ ] Étape 14 : **chaque page parlée dure exactement le temps de sa voix** (`DUREE` = durée de l'audio arrondie au centième supérieur, `seek.max` identique, `playbackRate = 1`, aucun silence à la fin ; la fiche n'est qu'une approximation, l'écart est signalé).
- [ ] Étape 14 : l'animation est faite **directement en web**, sans aucun logiciel externe ; **avant le plan 1**, tu as lu **en entier** `Plan_animation.md` (section 0, les 9 parties, annexes) et `Sequences.md`, et écrit `scenario_notes.md` (fil de l'histoire, éléments récurrents avec premier plan et retours, intention de chaque plan en une phrase, arbitrages, style) ; **chaque plan** a été animé après relecture de sa ligne, de la précédente et de la suivante, au service de son intention, **sans rien inventer** ni oublier.
- [ ] Étape 14 : chaque plan est livré en **une page `planN.html` autonome** publiée en artefact (SVG intégrés, détourage, objets du fond vers le devant, éléments en code, chronologie complète, lecteur avec pause et barre de temps), **avec l'audio du plan intégré en base64 dans la page** (sauf les plans sans voix off), **sans montage** ; les SVG d'origine ne sont jamais modifiés, le fond de détourage n'est jamais visible ; aucun élément n'a été dessiné sans être demandé.
- [ ] Étape 14 : **avant chaque livraison**, tu as capturé au moins 4 images clés, les as **regardées de près** et comparées au storyboard ; tu as trouvé toi-même les défauts (échelle, perspective, ordre des calques, mouvement figé ou trop faible) et tu n'as jamais dit « terminé » sans vérifier.
- [ ] Étape 14 : **mes crédits ont été ménagés** : lecture unique du README et des directives avec `animation_notes.md`, lecture limitée à la fiche du plan, moteur commun partagé, petites modifications par édition de la page, réponses courtes, `animation_status.md` à jour (avec les liens), et tu m'as prévenu avant tout travail lourd.
- [ ] Étape 14 : pour **chaque plan qui en continue un autre**, tu as exigé le **plan précédent** avant de commencer (sans me le redemander s'il était déjà disponible), repris son **état final tel quel**, et contrôlé le **raccord** (dernière image du précédent comparée à la première du plan), sans écart non voulu et sans modifier le plan précédent.
- [ ] Étape 14 : tu as eu `Registre_exigences_animation.md` **avant tout plan** (demandé hors IngXAi ; cloné depuis `Autoniax` dans IngXAi), tu l'as lu en entier et repassé avant chaque plan et chaque livraison ; **chaque défaut, remarque, demande de modification ou détail que j'ai donné y a été noté par toi, sans doublon** (un sujet qui revient a gagné une ★ au lieu d'une nouvelle ligne), avec sa portée, dans la même réponse que la correction, et tu m'as livré le fichier à jour ; **aucune erreur déjà notée n'est revenue et je n'ai jamais eu à répéter une demande notée** (sinon, le moteur commun a été corrigé).
- [ ] Étape 14 : après chaque plan, une correction est faite **dans la même page** ; le plan suivant n'est commencé qu'après mon « ça marche » ; les N plans sont validés.
- [ ] Étape 14 (IngXAi) : j'ai fourni l'**arborescence réelle** ; `projet_animation.json` a **N tâches** `p1` à `pN`, dont le **prompt est le prompt minimal** (numéro du plan, clone de `Autoniax`, étape 14 du Director, registre) ; le `references` de chaque tâche est le seul `speech.txt` de la séquence, en **chemin absolu** recopié de l'arborescence, avec des `/`, et existant ; chaque tâche a **deux résultats** : `Plan N – rendu animé` (obligatoire, type `html`, dossier `Animation/`, avec `existant` pour un plan déjà animé) et `Ajouts registre – Plan N` (`"facultatif": true`, type `md`, dossier `Animation/Registre_ajouts`) ; les **N plans** sont dans le JSON, y compris ceux déjà animés ; **`envoyer_autoniax.py` m'a été livré** (et relancé : `Autoniax` contient le `Director.md` et le registre à jour).
- [ ] Étape 14 (IngXAi) : chaque tâche a son champ **`depend_de`** (liste, `[]` si indépendant), rempli **par toi** d'après les fiches, `Sequences.md`, `Registre_elements_animation.md` et les `_reutilise.txt` : dépendances **directes**, **sans boucle**, aucun plan cité inexistant, **chaque plan `_reutilise` dépend de son plan source** (ou, s'il est déjà validé, sa page est dans les `references`), le premier plan d'une séquence indépendant sauf réutilisation ou continuité ; **dans le doute, le plan dépend**.
- [ ] Étape 14 (IngXAi) : tous les `desactive` valent `false` dans le JSON ; tu m'as expliqué la **mise en attente** (🔒 En attente, tâche jamais attribuée avant la fin de celles dont elle dépend, déblocage automatique), la **désactivation** (bouton ⊘ ; une tâche désactivée n'est jamais attribuée et **bloque ses dépendantes**) et la **validation** (« Définir comme résultat », double-clic sur la tâche pour la fenêtre « Résultats », ↺ pour réinitialiser) ; le bilan (chaînes, plans indépendants, cas douteux) m'a été remis, le JSON a passé « Valider et créer » dans le logiciel sans erreur.
- [ ] Étape 15 (B, seulement si demandé) : j'ai fourni l'**arborescence réelle** (tu me l'as demandée si elle manquait) ; tu m'as donné le **tableau des pages identifiées** (numéro lu après le mot « plan », jamais un autre nombre du titre ; absents, doublons, noms ambigus signalés) avant d'écrire le script ; les N plans ont une page. **Si j'ai seulement demandé les métadonnées, rien de (B) n'a été fait.**
- [ ] Étape 15 : `envoyer_export.py` a été **recopié du modèle `envoyer_storyboard.py`** (seuls chemin, dépôt, sélection, découpage en parties et envoi multi-fichiers adaptés), testé, livré en un seul bloc de code, avec `Metadonnees_video.html` intégrée en base64 : **je n'ai eu aucun fichier à placer ni aucun clic à faire**.
- [ ] Étape 15 : le script a contrôlé avant l'envoi (N pages lisibles, audio dans les plans parlés et pas dans les plans sans voix off, aucune ressource distante, taille des parties < 95 Mo, garde-fou des secrets) ; les pages sont **copiées sous `animations/PlanNN.html`**, jamais modifiées ; le bilan liste tout fichier non retenu avec sa raison.
- [ ] Étape 15 : le dépôt `Export` contient **un seul commit** : `Export_part01.zip`…, `Metadonnees_video.html` et `manifest_export.json` à la racine ; tu les as téléchargés et contrôlés (`testzip`, N pages, taille et `sha256` du manifest, audio présent) ; bilan limité aux problèmes graves.
- [ ] Étape 15 (A) : `Metadonnees_video.html` est **courte** et contient seulement : 3 titres candidats, la description prête à coller, les chapitres horodatés (calculés par script), les tags, la miniature et au plus 3 points à trancher ; **pas de transcription, de tableau de faits ni de matière de recherche** ; boutons « Copier » fonctionnels en fichier local (`execCommand` d'abord) ; textes livrés **avant** la miniature.
- [ ] Étape 15 : la miniature suit le **pattern de la chaîne** : **3 variantes de 3 familles différentes** (alarme, piège, révélation, perte), chacune avec **1 à 3 mots en capitales écrits dans l'image** (en haut, ≥ 70 % de la largeur, blanc à contour sombre), **un seul personnage cartoon en émotion extrême**, **un seul objet-symbole** dramatique, fond saturé à une dominante, coin bas droit libre, lisible à 170 px, aucun logo réel ni ressemblance réelle ; chemins complets des images à joindre ; **titre candidat** par variante selon le modèle de titres (35 à 90 caractères, enjeu concret, 1 à 2 mots en capitales, sans répéter le texte de l'image, sans fait absent de la vidéo) ; le JSON ImGen (`miniature_imgen.json`) passe `parse_project_text` sans erreur ; après génération, texte vérifié et variante la plus convaincante recommandée.

---

# Annexes – Modèles de scripts et de fichiers

Ces blocs sont recopiés **à l'identique** depuis les étapes qui les citent. Chaque étape renvoie ici par « Modèle : voir Annexe ... ».

<a id="annexe-a1"></a>

## Annexe A1 – Modèle de `envoyer_creative_data.py` (étape 0 ter)

```python
# -*- coding: utf-8 -*-
"""
envoyer_creative_data.py

Rassemble dans UNE SEULE archive, CreativeData.zip :
  - json_maitre.json        (chemin fixe, toujours le meme)
  - mots_reference.json     (chemin fixe, toujours le meme)
  - scraping/               (contenu de l'archive de scraping du projet en cours)
  - manifest.json           (liste des fichiers, tailles, empreintes)
puis la pousse dans le depot GitHub "CreativeData".

Comme ca, les nouvelles conversations clonent ce depot au lieu de recevoir les
fichiers a la main.

Ce script s'execute N'IMPORTE OU sur l'ordinateur : range-le dans n'importe
quel dossier et lance-le depuis un editeur (IDLE, Thonny, VS Code, PyCharm...)
avec "Run" / "Executer". Il n'utilise ni chemin relatif, ni __file__, ni
dossier courant : tout part de chemins ABSOLUS.

Seule chose a changer d'un projet a l'autre : ARCHIVE_SCRAPING (le zip du
bouton "Copier archive scrapping" de Marketing_manager.pyw, ou un dossier).
Si ARCHIVE_SCRAPING est vide, une fenetre s'ouvre pour choisir le zip.

Resultat :
  <dossier temporaire>/CreativeData.zip   (dossier racine CreativeData/ dans le zip)
  depot GitHub CreativeData               un seul commit, un seul fichier : CreativeData.zip

Le depot ne garde qu'un seul zip : chaque envoi REMPLACE le precedent
(historique reduit a un commit, push force).

Authentification GitHub : par defaut, git utilise les identifiants deja
enregistres sur l'ordinateur. Sinon, renseigne GITHUB_TOKEN (jeton d'acces).
Le jeton n'est jamais affiche.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# FICHIERS FIXES (toujours les memes, ne changent pas d'un projet a l'autre)
# ---------------------------------------------------------------------------
JSON_MAITRE = Path(
    r"D:\ScaleTube\CHANNELS\IngeniaX\Code\Lexiax\Bibliotheque"
    r"\InfographicsShowData\json_maitre.json")
MOTS_REFERENCE = Path(
    r"D:\ScaleTube\CHANNELS\IngeniaX\Code\Lexiax\Bibliotheque"
    r"\InfographicsShowData\mots_reference.json")

# ---------------------------------------------------------------------------
# ARCHIVE DE SCRAPING (change a chaque projet)
# Chemin absolu du zip (ou du dossier) de l'archive de scraping.
# Vide = une fenetre s'ouvre pour choisir le zip.
# Un chemin peut aussi etre donne en argument : python envoyer_creative_data.py "<chemin>"
# ---------------------------------------------------------------------------
ARCHIVE_SCRAPING = ""

# ---------------------------------------------------------------------------
# DEPOT GITHUB
# ---------------------------------------------------------------------------
DEPOT_URL = "https://github.com/officecenter632-maker/CreativeData.git"
BRANCHE = "main"
NOM_ZIP = "CreativeData.zip"
RACINE_ZIP = "CreativeData"
LIEN_DIRECT = ("https://github.com/officecenter632-maker/CreativeData/"
               "raw/main/CreativeData.zip")
GITHUB_TOKEN = ""          # vide = identifiants git deja enregistres

TAILLE_MAX = 100 * 1024 * 1024   # limite GitHub par fichier
IGNORES = {"__macosx", ".ds_store", "thumbs.db", "desktop.ini"}


def afficher(texte=""):
    """print sans plantage, meme si l'editeur ne sait pas afficher certains caracteres."""
    try:
        print(texte)
    except UnicodeEncodeError:
        print(texte.encode("ascii", "replace").decode("ascii"))


def masquer(texte):
    """Retire le jeton de tout texte affiche."""
    if GITHUB_TOKEN:
        texte = texte.replace(GITHUB_TOKEN, "***")
    return texte


def choisir_archive():
    """Retourne le chemin de l'archive de scraping (constante, argument ou fenetre)."""
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return Path(sys.argv[1].strip().strip('"'))
    if ARCHIVE_SCRAPING.strip():
        return Path(ARCHIVE_SCRAPING.strip().strip('"'))
    try:
        import tkinter
        from tkinter import filedialog
        racine = tkinter.Tk()
        racine.withdraw()
        racine.attributes("-topmost", True)
        choix = filedialog.askopenfilename(
            title="Choisis l'archive de scraping (zip)",
            filetypes=[("Archive zip", "*.zip"), ("Tous les fichiers", "*.*")])
        racine.destroy()
        if choix:
            return Path(choix)
    except Exception:
        pass
    saisie = input("Chemin de l'archive de scraping (zip ou dossier) : ").strip()
    return Path(saisie.strip('"')) if saisie else None


def ignorer(nom_relatif):
    return any(partie.lower() in IGNORES for partie in nom_relatif.split("/"))


def empreinte(octets):
    return hashlib.sha256(octets).hexdigest()


def lire_scraping(chemin):
    """Retourne (liste de (nom_dans_scraping, octets), ecarts). Zip ou dossier."""
    entrees, ecarts = [], []
    if chemin.is_dir():
        for p in sorted(chemin.rglob("*")):
            if p.is_file():
                rel = p.relative_to(chemin).as_posix()
                if not ignorer(rel):
                    entrees.append((rel, p.read_bytes()))
    elif zipfile.is_zipfile(chemin):
        with zipfile.ZipFile(chemin) as z:
            if z.testzip() is not None:
                ecarts.append("l'archive de scraping est corrompue")
                return entrees, ecarts
            for info in z.infolist():
                if info.is_dir():
                    continue
                nom = info.filename.replace("\\", "/")
                if not ignorer(nom):
                    entrees.append((nom, z.read(info)))
    else:
        ecarts.append("l'archive de scraping n'est ni un zip valide ni un dossier : "
                      + str(chemin))
        return entrees, ecarts

    noms = [n.lower() for n, _ in entrees]
    nb_pub = sum(1 for n in noms if "/publications/" in "/" + n and n.endswith("_publication.json"))
    nb_com = sum(1 for n in noms if "/commentaires/" in "/" + n and n.endswith(".json"))
    if nb_pub == 0:
        ecarts.append("aucun fichier *_publication.json dans le dossier Publications")
    if nb_com == 0:
        ecarts.append("aucun fichier de commentaires .json dans le dossier Commentaires")
    return entrees, ecarts


def controler_json(chemin, cles):
    """Verifie que le fichier existe, est un JSON valide et contient les rubriques."""
    if not chemin.is_file():
        return None, ["fichier introuvable : " + str(chemin)]
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except Exception as e:
        return None, ["JSON invalide (%s) : %s" % (chemin.name, e)]
    manque = [c for c in cles if not isinstance(donnees, dict) or c not in donnees]
    if manque:
        return chemin.read_bytes(), ["%s : rubriques absentes : %s"
                                     % (chemin.name, ", ".join(manque))]
    return chemin.read_bytes(), []


def creer_zip(dossier_tmp, maitre, mots, scraping, archive):
    """Cree CreativeData.zip et retourne (chemin, taille, manifeste)."""
    fichiers = [("json_maitre.json", maitre), ("mots_reference.json", mots)]
    fichiers += [("scraping/" + nom, octets) for nom, octets in scraping]
    manifeste = {
        "cree_le": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "archive_scraping_source": archive.name,
        "nb_fichiers": len(fichiers),
        "fichiers": [{"chemin": n, "octets": len(o), "sha256": empreinte(o)}
                     for n, o in fichiers],
    }
    chemin_zip = dossier_tmp / NOM_ZIP
    with zipfile.ZipFile(chemin_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for nom, octets in fichiers:
            z.writestr(RACINE_ZIP + "/" + nom, octets)
        z.writestr(RACINE_ZIP + "/manifest.json",
                   json.dumps(manifeste, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(chemin_zip) as z:
        if z.testzip() is not None:
            raise RuntimeError("zip corrompu")
    return chemin_zip, chemin_zip.stat().st_size, manifeste


def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       timeout=900,
                       env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    return r.returncode, masquer((r.stdout or "") + (r.stderr or "")).strip()


def pousser(chemin_zip):
    """Depot neuf, un seul commit, push force. Retourne (ok, message)."""
    if shutil.which("git") is None:
        return False, "git est introuvable sur cet ordinateur."
    url = DEPOT_URL
    if GITHUB_TOKEN:
        url = DEPOT_URL.replace("https://",
                                "https://x-access-token:" + GITHUB_TOKEN + "@", 1)
    tmp = Path(tempfile.mkdtemp(prefix="creativedata_push_"))
    try:
        shutil.copy2(chemin_zip, tmp / NOM_ZIP)
        for etape in (["init", "-q"],
                      ["symbolic-ref", "HEAD", "refs/heads/" + BRANCHE],
                      ["add", NOM_ZIP],
                      ["-c", "user.name=CreativeData Script",
                       "-c", "user.email=creativedata@local",
                       "commit", "-q", "-m", NOM_ZIP]):
            code, sortie = git(etape, tmp)
            if code != 0:
                return False, "git " + etape[-1 if etape[0] == "-c" else 0] \
                    + " a echoue : " + sortie
        code, sortie = git(["-c", "http.postBuffer=524288000", "push",
                            "--force", url, "HEAD:refs/heads/" + BRANCHE], tmp)
        if code != 0:
            return False, "push refuse : " + sortie
        code, local = git(["rev-parse", "HEAD"], tmp)
        code2, distant = git(["ls-remote", url, "refs/heads/" + BRANCHE], tmp)
        if code != 0 or code2 != 0 or not distant.startswith(local.strip()):
            return False, ("push passe, mais la branche distante ne montre pas "
                           "le commit attendu : " + distant)
        return True, "commit " + local.strip()[:8] + " present sur " + BRANCHE
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ecarts = []

    maitre, e = controler_json(JSON_MAITRE, ["regles", "recettes", "codes_de_sens",
                                              "corpus_idees"])
    ecarts += e
    mots, e = controler_json(MOTS_REFERENCE, [])
    ecarts += e

    archive = choisir_archive()
    if archive is None or not archive.exists():
        ecarts.append("archive de scraping introuvable : " + str(archive))
        scraping = []
    else:
        scraping, e = lire_scraping(archive)
        ecarts += e

    if ecarts:
        afficher("ECARTS (rien n'est envoye) :")
        for e in ecarts:
            afficher("  - " + e)
        afficher("Corrige le chemin ou le fichier concerne, puis relance le script.")
        return

    dossier_tmp = Path(tempfile.mkdtemp(prefix="creativedata_zip_"))
    try:
        chemin_zip, taille, manifeste = creer_zip(dossier_tmp, maitre, mots,
                                                  scraping, archive)
        afficher("json_maitre.json : %.0f Ko | mots_reference.json : %.0f Ko"
                 % (len(maitre) / 1024.0, len(mots) / 1024.0))
        afficher("Archive de scraping : %s (%d fichiers)" % (archive.name, len(scraping)))
        afficher("Zip cree : %s (%.1f Mo, %d fichiers)"
                 % (NOM_ZIP, taille / 1048576.0, manifeste["nb_fichiers"] + 1))
        if taille >= TAILLE_MAX:
            afficher("ERREUR : le zip depasse 100 Mo, limite de GitHub. Rien n'est envoye.")
            return

        ok, message = pousser(chemin_zip)
        if ok:
            afficher("Envoi reussi : " + message)
            afficher("Depot : " + DEPOT_URL)
            afficher("Lien direct : " + LIEN_DIRECT)
            afficher("Aucun ecart.")
        else:
            afficher("ENVOI ECHOUE : " + message)
            afficher("Si c'est un probleme d'identifiants, renseigne GITHUB_TOKEN.")
            copie = Path(tempfile.gettempdir()) / NOM_ZIP
            shutil.copy2(chemin_zip, copie)
            afficher("Une copie du zip est conservee : " + str(copie))
    finally:
        shutil.rmtree(dossier_tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
```

<a id="annexe-a2"></a>

## Annexe A2 – Modèle du fichier de départ `Plan_animation.md` (étape 0 ter)

```
# Scénario – <sujet>

Date : <date>

## Suivi (à lire en premier)

**Reprise : lis cette section d'abord.**

- **Phase en cours : A. État : NON COMMENCÉ.** Rien n'est écrit, rien n'est validé. Tu pars du début de l'étape 0 ter.
- **Sujet de la vidéo** : <sujet>.
- **Durée cible de la vidéo** : <durée> (choisie par moi ; tolérance 10 %).
- **Source des entrées** (dépôt `CreativeData`) : archive de scraping `<archive>` ; date du manifest : <manifest>.
- **Validé par moi** : rien pour l'instant.

| Idée | Genre | Plans | État | Remarque |
| --- | --- | --- | --- | --- |
| (aucune idée : la structure n'est pas écrite) | | | | |

- **Fil rouge déjà introduit (personnages, objets)** : aucun.
- **État du dernier plan écrit** : aucun plan écrit.
- **Décisions déjà prises** : aucune. **Questions ouvertes** : aucune.
- **Règles du JSON déjà utilisées** : aucune. **Passages signalés pour l'annexe F** : aucun.
- **Vidéos de référence lues pour le style** : aucune.
- **Nombres calculés** : 0 idée, 0 plan, 0 s.

## Structure globale

(à faire, phase B)

## 0. Charte visuelle et choix de production

(à faire, phase B : charte provisoire avec la palette et le tableau « Couleurs des éléments qui reviennent » ; phase D : charte définitive)

## Parties

(à faire : les parties et leurs tableaux de plans apparaîtront ici, de `## 1.` à `## M.`)

## Annexes

### A. Contrôles effectués
(à faire, phase E)

### B. Décisions prises
(à faire, phase E)

### C. À fournir de ton côté
(à faire, phase E)

### D. Rappel sur les faits
(à faire, phase E)

### E. Traçabilité créative
(à faire, rempli au fur et à mesure, phase D)

### F. Passages mal couverts par le registre
(à faire, phase E)

### G. Structure globale
(à faire, phase E : reprise de la section « Structure globale »)
```

<a id="annexe-a3"></a>

## Annexe A3 – Format du fichier `Liste_assets.md` (étape 1)

```
# Liste des assets de l'animation

## Éléments clés (une génération chacun)

| # | Asset | Plans |
| --- | --- | --- |
| 1 | Opérateur de drone, de dos, en camouflage | 1.1, 1.2, 9.1 |

## Petits éléments (planches)

### Planche 1 : télécom

| Élément | Plans |
| --- | --- |
| Parabole blanche sur maison | 2.5 |
```

<a id="annexe-a4"></a>

## Annexe A4 – Exemple de script `collecter_images.py` (étape 5)

```python
# -*- coding: utf-8 -*-
"""
collecter_images.py - projet 6-musk_starlink

Rassemble les images GENEREES de tous les assets dans un seul dossier,
avec des noms sans ambiguite. Les images sont COPIEES : les originaux restent
a leur place dans assets/, rien n'est deplace ni modifie.

A lancer depuis un editeur (IDLE, Thonny, VS Code, PyCharm...) : ouvrir ce
fichier et cliquer sur "Run" / "Executer". Aucune ligne de commande.

Resultat (le dossier et le zip portent le meme nom, NOM_ZIP) :
  <Assets>/assetsBrute1/      01_operateur_drone.png, ..., planche_01_telecom.png, index.csv
  <Assets>/assetsBrute1.zip   le meme contenu, dans un dossier assetsBrute1/ a l'interieur du zip

index.csv donne, pour chaque image, le chemin de la COPIE (dossier assetsBrute1).

Le dossier assetsBrute1, index.csv et le zip sont recrees a chaque lancement.
Change NOM_ZIP pour assetsBrute2, assetsBrute3... a chaque nouvelle version
(le dossier et le zip precedents sont alors conserves).
"""
import csv
import shutil
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# CHEMINS REELS (copies de l'arborescence fournie)
# Les emojis du chemin sont ecrits en codes \U pour que tous les editeurs
# acceptent ce fichier : 1F449 = main qui pointe, 1F4DA = livres,
# 1F4E6 = colis, 1F9E0 = cerveau.
# ---------------------------------------------------------------------------
DOSSIER_ASSETS_PARENT = Path(
    "D:/ScaleTube/CHANNELS/IngeniaX/"
    "\U0001F449 \U0001F4DA\U0001F4E6 Contents \U0001F9E0/"
    "Video/6-musk_starlink/Assets"
)
DOSSIER_ASSETS = DOSSIER_ASSETS_PARENT / "assets"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

# Nom du livrable : assetsBrute1, puis assetsBrute2... pour une nouvelle version.
# Le dossier des images et le zip portent ce meme nom.
NOM_ZIP = "assetsBrute1"
DOSSIER_SORTIE = DOSSIER_ASSETS_PARENT / NOM_ZIP
FICHIER_ZIP = DOSSIER_ASSETS_PARENT / (NOM_ZIP + ".zip")

# ---------------------------------------------------------------------------
# IMAGE GENEREE DE CHAQUE ASSET : dossier -> nom exact du fichier (arborescence)
# ---------------------------------------------------------------------------
IMAGES = {
    "01_operateur_drone": "Comparaison de deux soldats assis.png",
    "02_proprietaire_reseau": "Cinq poses d\u2019un homme d\u2019affaires cartoon.png",
    "03_soldat_generique": "Soldat en uniforme olive minimaliste.png",
    "04_personnage_pupitre": "Trois personnages en style vectoriel flat.png",
    "05_responsable_ukrainien": "Officier militaire en uniforme d\u00e9cor\u00e9.png",
    "06_silhouettes_foule": "Planche d\u2019infographie de silhouettes bleues.png",
    "07_silhouette_couronnee_levier": "Personnage couronn\u00e9 actionnant un levier g\u00e9ant.png",
    "08_telecommande_geante": "Bouton d\u2019urgence rouge entre les mains.png",
    "09_batiment_cinq_cotes": "Complexe pentagonal en vue a\u00e9rienne.png",
    "10_satellite_constellation": "Grand satellite et constellation en orbite.png",
    "11_carte_ukraine": "Carte vectorielle de l\u2019Ukraine en bleu.png",
    "12_drone": "Deux vues d\u2019un drone quadricopt\u00e8re.png",
    "13_document": "Certificat officiel stylis\u00e9.png",
    "14_balance_geante": "Balance dor\u00e9e parfaitement \u00e9quilibr\u00e9e.png",
    "15_poste_pilotage_ecrans": "Poste de contr\u00f4le cartographique\u0d47\u0d27.png",
    "16_poste_commandement_nuit": "Centre de contr\u00f4le futuriste violet et vert.png",
    "17_bureau_angle_vitre": "Bureau moderne face \u00e0 la ville.png",
    "18_salle_presse": "Tribune de presse minimaliste en vert-de-gris.png",
    "19_table_negociation_ronde": "R\u00e9union minimaliste vue du dessus.png",
    "20_tranchee": "Coupe transversale d\u2019une tranch\u00e9e militaire.png",
    "21_mur_panneaux_arches_rideaux": "D\u00e9cor de sc\u00e8ne bleu sym\u00e9trique.png",
    "22_bureau_turquoise_dossiers": "Bureau organis\u00e9 aux dossiers color\u00e9s.png",
    "23_console_nuit_fenetre_lune": "Console lunaire sous ciel \u00e9toil\u00e9.png",
    "24_brouillard_gris": "Cadre de fum\u00e9e nuageuse monochrome.png",
    "planche_01_telecom": "Planche d\u2019ic\u00f4nes de communication et d\u00e9fense.png",
    "planche_02_militaire": "Ic\u00f4nes militaires et spatiales en flat design.png",
    "planche_03_bureau": "Ic\u00f4nes administratives en grille \u043c\u0438\u043d\u0438\u043caliste.png",
    "planche_04_interface": "Ic\u00f4nes infographiques modernes et color\u00e9es.png",
    "planche_05_symboles": "Ensemble d\u2019ic\u00f4nes color\u00e9es en grille.png",
    "planche_06_objets_de_scene": "Restrictions, temps et \u00e9quipement.png",
}


def afficher(texte=""):
    """print sans plantage, meme si l'editeur ne sait pas afficher certains caracteres."""
    try:
        print(texte)
    except UnicodeEncodeError:
        print(texte.encode("ascii", "replace").decode("ascii"))


def type_asset(nom):
    return "planche" if nom.startswith("planche_") else "element_cle"


def images_du_dossier(dossier):
    """Images posees directement dans le dossier (le sous-dossier generation est ignore)."""
    trouvees = [p for p in dossier.iterdir()
                if p.is_file() and p.suffix.lower() in EXTENSIONS]
    return sorted(trouvees, key=lambda p: (p.stat().st_mtime, p.name))


def main():
    if not DOSSIER_ASSETS.is_dir():
        afficher("ERREUR : dossier introuvable : " + str(DOSSIER_ASSETS))
        afficher("Verifie DOSSIER_ASSETS_PARENT en haut du script.")
        return

    if DOSSIER_SORTIE.exists():
        assert DOSSIER_SORTIE.name == NOM_ZIP and NOM_ZIP != "assets"  # garde-fou
        shutil.rmtree(DOSSIER_SORTIE)                  # simple dossier de copies
    DOSSIER_SORTIE.mkdir()

    lignes = []
    absents, sans_image, repli, restes = [], [], [], []

    dossiers_presents = {p.name for p in DOSSIER_ASSETS.iterdir() if p.is_dir()}
    non_prevus = sorted(dossiers_presents - set(IMAGES))

    for nom, fichier in IMAGES.items():
        dossier = DOSSIER_ASSETS / nom
        if not dossier.is_dir():
            absents.append(nom)
            continue

        exact = dossier / fichier
        if exact.is_file():
            # Chemin exact de l'arborescence : c'est l'image de l'asset.
            sources = [exact]
            autres = [p.name for p in images_du_dossier(dossier) if p != exact]
            if autres:
                restes.append((nom, autres))
        else:
            # Nom different de l'arborescence : on prend ce qui est dans le dossier.
            sources = images_du_dossier(dossier)
            if not sources:
                sans_image.append(nom)
                continue
            repli.append((nom, [p.name for p in sources]))

        for n, src in enumerate(sources, start=1):
            suffixe = "" if len(sources) == 1 else "_v" + str(n)
            nouveau = nom + suffixe + src.suffix.lower()
            copie = DOSSIER_SORTIE / nouveau
            shutil.copy2(src, copie)                              # COPIE
            lignes.append([nouveau, nom, type_asset(nom), str(copie)])

    # index.csv : le chemin de chaque copie.
    with open(DOSSIER_SORTIE / "index.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["fichier", "asset", "type", "chemin_copie"])
        w.writerows(lignes)

    # Zip : un dossier NOM_ZIP/ avec les images copiees et index.csv.
    if FICHIER_ZIP.exists():
        FICHIER_ZIP.unlink()
    with zipfile.ZipFile(FICHIER_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(DOSSIER_SORTIE.iterdir()):
            z.write(f, NOM_ZIP + "/" + f.name)

    afficher(str(len(lignes)) + " image(s) copiee(s) sur " + str(len(IMAGES))
             + " assets attendus.")
    afficher("Dossier des images : " + str(DOSSIER_SORTIE))
    afficher("Index des chemins : " + str(DOSSIER_SORTIE / "index.csv"))
    afficher("Zip cree : " + str(FICHIER_ZIP))
    if absents:
        afficher("\nDOSSIERS D'ASSET ABSENTS :")
        for a in absents:
            afficher("  - " + a)
    if sans_image:
        afficher("\nASSETS SANS IMAGE GENEREE :")
        for a in sans_image:
            afficher("  - " + a)
    if repli:
        afficher("\nNOM DE FICHIER DIFFERENT DE L'ARBORESCENCE (image prise dans le dossier) :")
        for a, noms in repli:
            afficher("  - " + a + " -> " + ", ".join(noms))
    if restes:
        afficher("\nAUTRES IMAGES PRESENTES, NON COPIEES :")
        for a, noms in restes:
            afficher("  - " + a + " -> " + ", ".join(noms))
    if non_prevus:
        afficher("\nDOSSIERS NON PREVUS DANS LA LISTE :")
        for a in non_prevus:
            afficher("  - " + a)
    if not (absents or sans_image or repli or restes or non_prevus):
        afficher("Aucun ecart.")


if __name__ == "__main__":
    main()
```

<a id="annexe-a5"></a>

## Annexe A5 – Modèle de `envoyer_storyboard.py` (étape 9)

```python
# -*- coding: utf-8 -*-
"""
envoyer_storyboard.py - projet 6-musk_starlink

Selectionne UNIQUEMENT le storyboard (Sequences.md, speech.txt, PlanN.txt et
images des plans), controle sa structure, le zippe en Storyboard.zip et le
pousse dans le depot GitHub "Storyboard".

Ce script s'execute N'IMPORTE OU sur l'ordinateur : range-le dans n'importe
quel dossier (Bureau, Telechargements...) et lance-le depuis un editeur
(IDLE, Thonny, VS Code, PyCharm...) avec "Run" / "Executer". Il n'utilise ni
chemin relatif, ni __file__, ni dossier courant : tout part du chemin ABSOLU du
projet (constante PROJET).

Resultat :
  <PROJET>/Storyboard.zip      (dossier racine Storyboard/ a l'interieur du zip)
  depot GitHub Storyboard      un seul commit, un seul fichier : Storyboard.zip

Le depot ne garde qu'un seul zip : chaque envoi REMPLACE le precedent
(historique reduit a un commit, push force). ImageReferenceData n'est jamais
touche.

Authentification GitHub : par defaut, git utilise les identifiants deja
enregistres sur l'ordinateur. Sinon, renseigne GITHUB_TOKEN (jeton d'acces).
Le jeton n'est jamais affiche.
"""
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# CHEMIN ABSOLU DU PROJET (copie de la premiere ligne de l'arborescence)
# Les emojis sont ecrits en codes \U pour que tous les editeurs acceptent ce
# fichier : 1F449 = main qui pointe, 1F4DA = livres, 1F4E6 = colis,
# 1F9E0 = cerveau.
# ---------------------------------------------------------------------------
PROJET = Path(
    "D:/ScaleTube/CHANNELS/IngeniaX/"
    "\U0001F449 \U0001F4DA\U0001F4E6 Contents \U0001F9E0/"
    "Video/6-musk_starlink"
)
DOSSIER_STORYBOARD = PROJET / "Storyboard"
FICHIER_ZIP = PROJET / "Storyboard.zip"

# ---------------------------------------------------------------------------
# DEPOT GITHUB
# ---------------------------------------------------------------------------
DEPOT_URL = "https://github.com/officecenter632-maker/Storyboard.git"
BRANCHE = "main"
LIEN_DIRECT = ("https://github.com/officecenter632-maker/Storyboard/"
               "raw/main/Storyboard.zip")
GITHUB_TOKEN = ""          # vide = identifiants git deja enregistres

# ---------------------------------------------------------------------------
# ATTENDU
# ---------------------------------------------------------------------------
NB_SEQUENCES = S  # S = nombre de séquences, calculé depuis Sequences.md
NB_PLANS = N  # N = nombre de plans de la vidéo, calculé depuis Plan_animation.md
FORCER = False             # True : envoie meme s'il y a des ecarts de structure
TAILLE_MAX = 100 * 1024 * 1024   # limite GitHub par fichier

RE_SEQ = re.compile(r"^sequence(\d+)$", re.IGNORECASE)
RE_TXT = re.compile(r"^plan(\d+)\.txt$", re.IGNORECASE)
RE_IMG = re.compile(r"^plan(\d+)\.(webp|png|jpg|jpeg)$", re.IGNORECASE)


def afficher(texte=""):
    """print sans plantage, meme si l'editeur ne sait pas afficher certains caracteres."""
    try:
        print(texte)
    except UnicodeEncodeError:
        print(texte.encode("ascii", "replace").decode("ascii"))


def masquer(texte):
    """Retire le jeton de tout texte affiche."""
    if GITHUB_TOKEN:
        texte = texte.replace(GITHUB_TOKEN, "***")
    return texte


def selectionner():
    """Retourne (fichiers a zipper, exclus, ecarts)."""
    inclus, exclus, ecarts = [], [], []
    txt, img, speech = {}, {}, {}

    seq_dossiers = sorted(
        (p for p in DOSSIER_STORYBOARD.iterdir()
         if p.is_dir() and RE_SEQ.match(p.name)),
        key=lambda p: int(RE_SEQ.match(p.name).group(1)))

    # Racine du storyboard : Sequences.md seulement.
    seq_md = DOSSIER_STORYBOARD / "Sequences.md"
    for p in sorted(DOSSIER_STORYBOARD.iterdir()):
        if p.is_file() and p.name.lower() == "sequences.md":
            inclus.append(p)
            seq_md = p
        elif p.is_file() or not RE_SEQ.match(p.name):
            exclus.append(p.relative_to(DOSSIER_STORYBOARD).as_posix())
    if not seq_md.is_file():
        ecarts.append("Sequences.md absent de la racine de Storyboard")

    for d in seq_dossiers:
        a_speech = False
        for p in sorted(d.iterdir()):
            rel = p.relative_to(DOSSIER_STORYBOARD).as_posix()
            if not p.is_file():
                exclus.append(rel + "/")
                continue
            m_txt, m_img = RE_TXT.match(p.name), RE_IMG.match(p.name)
            if p.name.lower() == "speech.txt":
                inclus.append(p)
                a_speech = True
                speech[d.name] = p
            elif m_txt:
                n = int(m_txt.group(1))
                if n in txt:
                    ecarts.append("Plan%d.txt en double (%s et %s)"
                                  % (n, txt[n][0].name, d.name))
                txt[n] = (d, p)
                inclus.append(p)
            elif m_img:
                n = int(m_img.group(1))
                if n in img:
                    ecarts.append("image du plan %d en double (%s et %s)"
                                  % (n, img[n][1].name, p.name))
                img[n] = (d, p)
                inclus.append(p)
            else:
                exclus.append(rel)
        if not a_speech:
            ecarts.append("speech.txt absent de " + d.name)

    # Controles de structure.
    if len(seq_dossiers) != NB_SEQUENCES:
        ecarts.append("%d dossiers sequenceN trouves, %d attendus"
                      % (len(seq_dossiers), NB_SEQUENCES))
    attendus = set(range(1, NB_PLANS + 1))
    manque_txt = sorted(attendus - set(txt))
    manque_img = sorted(attendus - set(img))
    if manque_txt:
        ecarts.append("PlanN.txt manquants : " + ", ".join(map(str, manque_txt)))
    if manque_img:
        ecarts.append("images manquantes : "
                      + ", ".join("plan%d" % n for n in manque_img))
    en_trop = sorted((set(txt) | set(img)) - attendus)
    if en_trop:
        ecarts.append("plans hors 1.." + str(NB_PLANS) + " : "
                      + ", ".join(map(str, en_trop)))
    for n in sorted(set(txt) & set(img)):
        if txt[n][0] != img[n][0]:
            ecarts.append("plan %d : texte dans %s, image dans %s"
                          % (n, txt[n][0].name, img[n][0].name))
    for n in sorted(set(img) - set(txt)):
        ecarts.append("image du plan %d sans PlanN.txt" % n)

    stats = {"sequences": len(seq_dossiers), "txt": len(txt),
             "images": len(img), "speech": len(speech)}
    return inclus, exclus, ecarts, stats


def creer_zip(fichiers):
    if FICHIER_ZIP.exists():
        FICHIER_ZIP.unlink()
    with zipfile.ZipFile(FICHIER_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(fichiers):
            arc = "Storyboard/" + p.relative_to(DOSSIER_STORYBOARD).as_posix()
            z.write(p, arc)
    with zipfile.ZipFile(FICHIER_ZIP) as z:
        if z.testzip() is not None:
            raise RuntimeError("zip corrompu")
    return FICHIER_ZIP.stat().st_size


def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       timeout=900,
                       env=dict(__import__("os").environ,
                                GIT_TERMINAL_PROMPT="0"))
    return r.returncode, masquer((r.stdout or "") + (r.stderr or "")).strip()


def pousser():
    """Depot neuf, un seul commit, push force. Retourne (ok, message)."""
    if shutil.which("git") is None:
        return False, "git est introuvable sur cet ordinateur."
    url = DEPOT_URL
    if GITHUB_TOKEN:
        url = DEPOT_URL.replace("https://",
                                "https://x-access-token:" + GITHUB_TOKEN + "@", 1)
    tmp = Path(tempfile.mkdtemp(prefix="storyboard_push_"))
    try:
        shutil.copy2(FICHIER_ZIP, tmp / "Storyboard.zip")
        for etape in (["init", "-q"],
                      ["symbolic-ref", "HEAD", "refs/heads/" + BRANCHE],
                      ["add", "Storyboard.zip"],
                      ["-c", "user.name=Storyboard Script",
                       "-c", "user.email=storyboard@local",
                       "commit", "-q", "-m", "Storyboard.zip"]):
            code, sortie = git(etape, tmp)
            if code != 0:
                return False, "git " + etape[-1 if etape[0] == "-c" else 0] \
                    + " a echoue : " + sortie
        code, sortie = git(["-c", "http.postBuffer=524288000", "push",
                            "--force", url, "HEAD:refs/heads/" + BRANCHE], tmp)
        if code != 0:
            return False, "push refuse : " + sortie
        code, local = git(["rev-parse", "HEAD"], tmp)
        code2, distant = git(["ls-remote", url, "refs/heads/" + BRANCHE], tmp)
        if code != 0 or code2 != 0 or not distant.startswith(local.strip()):
            return False, ("push passe, mais la branche distante ne montre pas "
                           "le commit attendu : " + distant)
        return True, "commit " + local.strip()[:8] + " present sur " + BRANCHE
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if not DOSSIER_STORYBOARD.is_dir():
        afficher("ERREUR : dossier introuvable : " + str(DOSSIER_STORYBOARD))
        afficher("Verifie PROJET en haut du script.")
        return

    fichiers, exclus, ecarts, stats = selectionner()
    afficher("Selection : %d dossiers sequence, %d PlanN.txt, %d images, "
             "%d speech.txt (%d fichiers au total)."
             % (stats["sequences"], stats["txt"], stats["images"],
                stats["speech"], len(fichiers)))
    if exclus:
        afficher("\nFICHIERS EXCLUS (non envoyes) :")
        for e in exclus:
            afficher("  - " + e)
    if ecarts:
        afficher("\nECARTS DE STRUCTURE :")
        for e in ecarts:
            afficher("  - " + e)
        if not FORCER:
            afficher("\nRien n'est envoye. Corrige les ecarts, ou mets FORCER = True.")
            return
        afficher("\nFORCER = True : on continue malgre les ecarts.")

    taille = creer_zip(fichiers)
    afficher("\nZip cree : %s (%.1f Mo)" % (FICHIER_ZIP, taille / 1048576.0))
    if taille >= TAILLE_MAX:
        afficher("ERREUR : le zip depasse 100 Mo, limite de GitHub. Rien n'est envoye.")
        return

    ok, message = pousser()
    if ok:
        afficher("Envoi reussi : " + message)
        afficher("Depot : " + DEPOT_URL)
        afficher("Lien direct : " + LIEN_DIRECT)
        if not (exclus or ecarts):
            afficher("Aucun ecart.")
    else:
        afficher("ENVOI ECHOUE : " + message)
        afficher("Storyboard.zip reste en place : " + str(FICHIER_ZIP))
        afficher("Si c'est un probleme d'identifiants, renseigne GITHUB_TOKEN.")


if __name__ == "__main__":
    main()
```

<a id="annexe-a6"></a>

## Annexe A6 – Structure du `manifest.json` (étape 13)

```
{
  "projet": "6-musk_starlink",
  "genere_le": "2026-11-02T14:30:00",
  "plans": {
    "Plan1": [
      {
        "fichier": "01_fond_poste_pilotage_vide.svg",
        "type": "svg",
        "taille": 50487,
        "chemin_zip": "AnimationData/assets/Plan1/01_fond_poste_pilotage_vide.svg",
        "chemin_relatif": "Plan1/01_fond_poste_pilotage_vide.svg"
      }
    ]
  },
  "storyboard": {
    "Plan1": {"chemin_relatif": "sequence1/plan1.webp"}
  },
  "audio": {
    "Plan1": {
      "fichier": "Plan1.wav",
      "taille": 412044,
      "chemin_zip": "AnimationData/audio/sequence1/Plan1.wav",
      "chemin_relatif": "sequence1/Plan1.wav"
    }
  }
}
```

<a id="annexe-a7"></a>

## Annexe A7 – Squelette HTML minimal d'une page d'animation (étape 14, contrat de page)

```html
<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Plan N</title>
<style>
  html,body{margin:0;background:#000}
  #stage{position:relative;width:100%;aspect-ratio:16/9;overflow:hidden}
  /* contrôles : HORS de #stage */
</style></head>
<body>
  <div id="stage"><!-- tout ce qui est filmé : fond, personnages, canvas/SVG --></div>
  <div id="controles">
    <button id="play">Lecture</button>
    <input type="range" id="seek" min="0" max="4.76" step="0.01" value="0">
  </div>
  <audio id="voix" src="data:audio/wav;base64,…"></audio>
  <script>
    const DUREE = 4.76;                      // = durée de l'audio (4,752 s) arrondie au centième supérieur = seek.max ; JAMAIS la durée de Sequences.md
    let t0 = null, lecture = false;
    function dessiner(pos){ /* image à l'instant pos (secondes), fonction de pos seulement */ }
    function boucle(t){                      // t = horodatage de requestAnimationFrame
      if (lecture){ if (t0 === null) t0 = t; dessiner(((t - t0) / 1000) % DUREE); }
      requestAnimationFrame(boucle);
    }
    requestAnimationFrame(boucle);
  </script>
</body></html>
```

<a id="annexe-a8"></a>

## Annexe A8 – Structure du `manifest_export.json` (étape 15)

```
{
  "projet": "6-musk_starlink",
  "genere_le": "2026-11-05T12:00:00",
  "parties": [{"zip": "Export_part01.zip", "taille": 91234567, "plans": [1, 2, "…"]}],
  "plans": {
    "Plan1": {
      "fichier_origine": "Plan 1 – rendu animé (avec audio).html",
      "chemin_zip": "Export/animations/Plan01.html",
      "partie": "Export_part01.zip",
      "taille": 4123456,
      "sha256": "…",
      "audio": true
    }
  },
  "metadonnees": "Metadonnees_video.html"
}
```

<a id="annexe-a9"></a>

## Annexe A9 – Modèle du bloc de miniature (étape 15)

```
MINIATURE A · famille « révélation » · 1280×720 (16:9)

CE QUE LA MINIATURE FAIT COMPRENDRE
Une phrase, tirée du moment d'enjeu (jamais d'un élément absent de la vidéo).

TEXTE À ÉCRIRE DANS L'IMAGE (exactement, sans aucune autre lettre)
EXPOSED

IMAGES À JOINDRE
- <chemin complet d'un asset de Assets\assetsBrute1\…> (rôle : identité du personnage ou de l'objet)
- <chemin complet de l'image du plan : Storyboard\sequenceN\planN.webp> (rôle : décor et ambiance)

PROMPT DE GÉNÉRATION
Illustration cartoon vectorielle à contours épais, format 16:9. À gauche, en gros plan, [personnage inventé], bouche grande ouverte, yeux écarquillés, sueur, [geste : mains sur la tête]. À droite, [objet-symbole], [état dramatique]. Fond [dominante en code couleur] avec un accent [couleur en code] et une lueur [type] derrière le personnage. En haut, sur une seule ligne centrée qui occupe au moins 70 % de la largeur, le texte « EXPOSED » en capitales très épaisses sans empattement, blanc, avec un épais contour sombre et une légère ombre ; orthographe exacte, aucun autre texte. Le coin bas droit reste vide et sans détail. Un seul point d'intérêt, trois éléments au plus, lisible réduit à 170 px.

Même famille graphique que les images de référence jointes. Aucun logo réel, aucune ressemblance avec une personne réelle.

TITRE CANDIDAT (selon le modèle de titres)
…

APRÈS LA GÉNÉRATION
Je vérifie l'orthographe du texte et la lisibilité à 170 px ; si le texte est faux, je regénère (voir « Corrections »).
```

<a id="annexe-a10"></a>

## Annexe A10 – Modèle de `envoyer_autoniax.py` (étape 14)

À recopier tel quel ; seuls les chemins (`RACINE`, `PROJET`) et le nom du dépôt changent, **recopiés de l'arborescence réelle**.

```python
# -*- coding: utf-8 -*-
"""
envoyer_autoniax.py - projet 6-musk_starlink

Pousse DEUX fichiers, et seulement eux, dans le depot GitHub "Autoniax" :
  - Director.md                        (Bibliotheque/Reference/)
  - Registre_exigences_animation.md    (Animation/ du projet, version courante ;
                                        pas les anciennes versions de _versions)

Les agents d'IngXAi clonent ce depot : ils lisent l'etape 14 du Director et le
registre des exigences en entier. A relancer chaque fois que le Director ou le
registre change.

Ce script s'execute N'IMPORTE OU sur l'ordinateur : range-le dans n'importe
quel dossier et lance-le depuis un editeur (IDLE, Thonny, VS Code, PyCharm...)
avec "Run" / "Executer". Il n'utilise ni chemin relatif, ni __file__, ni
dossier courant : tout part des chemins ABSOLUS ci-dessous.

Resultat : depot GitHub Autoniax, un seul commit, deux fichiers a la racine.
Chaque envoi REMPLACE le precedent (historique reduit a un commit, push force).

Authentification GitHub : par defaut, git utilise les identifiants deja
enregistres sur l'ordinateur. Sinon, renseigne GITHUB_TOKEN ci-dessous, ou la
variable d'environnement GITHUB_TOKEN. Le jeton n'est jamais affiche.
NE COLLE JAMAIS LE JETON DANS UNE CONVERSATION.
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# CHEMINS ABSOLUS (emojis en codes \U : 1F449 = main qui pointe, 1F4DA = livres,
# 1F4E6 = colis, 1F9E0 = cerveau)
# ---------------------------------------------------------------------------
RACINE = Path(
    "D:/ScaleTube/CHANNELS/IngeniaX/"
    "\U0001F449 \U0001F4DA\U0001F4E6 Contents \U0001F9E0"
)
PROJET = RACINE / "Video/6-musk_starlink"

DIRECTOR = RACINE / "Bibliotheque/Reference/Director.md"

# Chemin du registre tel que copie depuis l'explorateur (essaye en premier).
REGISTRE_MANUEL = Path(
    r"D:\ScaleTube\CHANNELS\IngeniaX\👉 📚📦 Contents 🧠\Video\6-musk_starlink"
    r"\Animation\Registre_exigences_animation.md"
)


def trouver_registre():
    """Registre des exigences : Animation/Registre_exigences_animation.md, sinon tout
    .md de Animation/ dont le nom contient 'registre' et 'exigence' (hors _versions)."""
    if REGISTRE_MANUEL.is_file():
        return REGISTRE_MANUEL
    exact = PROJET / "Animation/Registre_exigences_animation.md"
    if exact.is_file():
        return exact
    dossier = PROJET / "Animation"
    if dossier.is_dir():
        for f in sorted(dossier.glob("*.md")):
            n = f.name.lower()
            if "registre" in n and "exigence" in n:
                return f
    return exact   # introuvable : controler() l'expliquera


# (fichier sur l'ordinateur, nom dans le depot)
FICHIERS = [
    (DIRECTOR, "Director.md"),
    (trouver_registre(), "Registre_exigences_animation.md"),
]

# ---------------------------------------------------------------------------
# DEPOT GITHUB
# ---------------------------------------------------------------------------
DEPOT_URL = "https://github.com/officecenter632-maker/Autoniax.git"
BRANCHE = "main"
LIEN_PAGE = "https://github.com/officecenter632-maker/Autoniax"
LIEN_RAW = "https://github.com/officecenter632-maker/Autoniax/raw/main/"
GITHUB_TOKEN = ""          # vide = identifiants git deja enregistres
TAILLE_MAX = 100 * 1024 * 1024   # limite GitHub par fichier


def afficher(texte=""):
    """print sans plantage, meme si l'editeur ne sait pas afficher certains caracteres."""
    try:
        print(texte)
    except UnicodeEncodeError:
        print(texte.encode("ascii", "replace").decode("ascii"))


def jeton():
    return GITHUB_TOKEN or os.environ.get("GITHUB_TOKEN", "")


def masquer(texte):
    """Retire le jeton de tout texte affiche."""
    t = jeton()
    if t:
        texte = texte.replace(t, "***")
    return texte


def diagnostiquer(chemin):
    """Affiche le premier niveau du chemin qui n'existe pas, et ce que contient son parent."""
    courant = Path(chemin.parts[0])
    for part in chemin.parts[1:]:
        suivant = courant / part
        if not suivant.exists():
            afficher("Le chemin s'arrete ici : %r n'existe pas dans %s" % (part, courant))
            try:
                afficher("Contenu reel de ce dossier : " + ", ".join(
                    repr(x.name) for x in sorted(courant.iterdir())[:40]))
            except OSError as e:
                afficher("(dossier illisible : %s)" % e)
            return
        courant = suivant
    afficher("Le chemin existe en entier.")


def controler():
    """Retourne la liste des erreurs (vide = on peut envoyer)."""
    erreurs = []
    for src, nom in FICHIERS:
        if not src.is_file():
            erreurs.append("fichier introuvable : " + str(src))
            continue
        taille = src.stat().st_size
        if taille == 0:
            erreurs.append("fichier vide : " + str(src))
        elif taille >= TAILLE_MAX:
            erreurs.append("fichier trop gros (> 100 Mo) : " + str(src))
        texte = src.read_text(encoding="utf-8", errors="replace")
        if nom == "Director.md" and "## Étape 14" not in texte:
            erreurs.append("Director.md ne contient pas « ## Étape 14 » : "
                           "ce n'est pas le bon fichier.")
        if nom.startswith("Registre_exigences") and "Partie A" not in texte:
            erreurs.append("le registre ne contient pas « Partie A » : "
                           "ce n'est pas le bon fichier.")
    return erreurs


def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       timeout=900,
                       env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    return r.returncode, masquer((r.stdout or "") + (r.stderr or "")).strip()


def pousser():
    """Depot neuf, un seul commit, push force. Retourne (ok, message)."""
    if shutil.which("git") is None:
        return False, "git est introuvable sur cet ordinateur."
    url = DEPOT_URL
    if jeton():
        url = DEPOT_URL.replace("https://",
                                "https://x-access-token:" + jeton() + "@", 1)
    tmp = Path(tempfile.mkdtemp(prefix="autoniax_push_"))
    try:
        for src, nom in FICHIERS:
            shutil.copy2(src, tmp / nom)
        noms = [nom for _, nom in FICHIERS]
        for etape in (["init", "-q"],
                      ["symbolic-ref", "HEAD", "refs/heads/" + BRANCHE],
                      ["add"] + noms,
                      ["-c", "user.name=Autoniax Script",
                       "-c", "user.email=autoniax@local",
                       "commit", "-q", "-m", "Director + registre des exigences"]):
            code, sortie = git(etape, tmp)
            if code != 0:
                return False, "git " + etape[-1 if etape[0] == "-c" else 0] \
                    + " a echoue : " + sortie
        code, sortie = git(["-c", "http.postBuffer=524288000", "push",
                            "--force", url, "HEAD:refs/heads/" + BRANCHE], tmp)
        if code != 0:
            return False, "push refuse : " + sortie
        code, local = git(["rev-parse", "HEAD"], tmp)
        code2, distant = git(["ls-remote", url, "refs/heads/" + BRANCHE], tmp)
        if code != 0 or code2 != 0 or not distant.startswith(local.strip()):
            return False, ("push passe, mais la branche distante ne montre pas "
                           "le commit attendu : " + distant)
        return True, "commit " + local.strip()[:8] + " present sur " + BRANCHE
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    erreurs = controler()
    for src, nom in FICHIERS:
        if src.is_file():
            afficher("%-34s %8.1f Ko   <- %s"
                     % (nom, src.stat().st_size / 1024.0, src))
    if erreurs:
        afficher("\nERREURS (rien n'est envoye) :")
        for e in erreurs:
            afficher("  - " + e)
        afficher("Verifie les chemins en haut du script.")
        diagnostiquer(REGISTRE_MANUEL)
        for d in (PROJET / "Animation", PROJET / "Meta"):
            if d.is_dir():
                noms = sorted(f.name for f in d.glob("*.md"))
                afficher("Fichiers .md dans %s : %s" % (d, ", ".join(noms) or "aucun"))
        return

    ok, message = pousser()
    if ok:
        afficher("\nEnvoi reussi : " + message)
        afficher("Depot : " + LIEN_PAGE)
        for _, nom in FICHIERS:
            afficher("Lien direct : " + LIEN_RAW + nom)
    else:
        afficher("\nENVOI ECHOUE : " + message)
        afficher("Si c'est un probleme d'identifiants, renseigne GITHUB_TOKEN.")
        afficher("Si le depot n'existe pas encore, cree-le vide sur GitHub (nom : Autoniax).")


if __name__ == "__main__":
    main()
```

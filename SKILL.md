---
name: repartition-equipe
description: Répartit une liste de tâches entre plusieurs collègues qui travaillent en parallèle avec Claude sur le même projet, en deux temps : d'abord un partage équilibré par charge sans tenir compte des conflits, puis l'analyse des conflits attendus (fichiers, migrations, routes, dépendances) et une variante sans conflit au choix de Prude. Vérifie sur GitHub qui est sur le dépôt, puis produit un plan par personne avec ordre d'exécution et points de synchronisation. À utiliser dès que Prude (ou un collègue) soumet une liste de tâches/fonctionnalités/bugs en disant « on est N », « répartis les tâches », « qui fait quoi », ou quand plusieurs personnes vont lancer Claude en même temps sur le même dépôt.
---

# Répartir les tâches d'une équipe, puis maîtriser les conflits

Contexte : chaque membre de l'équipe a son propre Claude, donc n'importe qui peut tout faire.
Le vrai risque n'est plus « qui sait faire quoi » mais **deux personnes qui modifient les mêmes
fichiers** (conflits git, migrations en double, doublons de code). Ce skill partage d'abord
le travail équitablement, puis met les conflits attendus sur la table et propose, sans
l'imposer, une variante qui les évite.

## Premier lancement sur une machine

Si `~/.claude/repartition-equipe.json` n'existe pas, c'est une nouvelle installation :
avant de commencer, résume en quelques lignes à la personne les prérequis détaillés dans
`INSTALLATION.md` (même dossier que ce fichier) : accès contributeur à la page de suivi,
présence sur le dépôt GitHub, `gh` installé et connecté (avec le code à 8 caractères
`XXXX-XXXX` à saisir sur github.com/login/device), et confirmation du nom affiché. Lis
`INSTALLATION.md` si elle a une question ou un blocage.

## Étape 0 — Prérequis : GitHub CLI (`gh`) installé et connecté

La vérification des personnes sur le dépôt (étape 1) et leur identité reposent sur `gh`.
Avant tout, sur la machine de la personne qui lance le skill :

1. `command -v gh`. S'il est absent, **installe-le** après avoir dit à la personne ce que
   tu vas lancer (l'installation demande souvent `sudo`) :
   - Fedora/RHEL : `sudo dnf install -y gh`
   - Debian/Ubuntu : `sudo apt install -y gh` (si le paquet manque, suis l'installation
     officielle de https://github.com/cli/cli/blob/trunk/docs/install_linux.md)
   - macOS : `brew install gh`
   - Windows : `winget install --id GitHub.cli`
   Si la commande exige un mot de passe ou un terminal interactif, demande à la personne de
   la lancer elle-même avec le préfixe `!` (ex. `! sudo dnf install -y gh`) et attends.
2. `gh auth status`. S'il n'est pas connecté, **demande à la personne de se connecter** :
   la connexion est interactive (navigateur ou code), tu ne peux pas la faire à sa place.
   Dis-lui de taper `! gh auth login` (GitHub.com, HTTPS, connexion par navigateur), puis
   relance `gh auth status` pour confirmer.
3. Vérifie l'accès au dépôt du projet : `gh api repos/<owner>/<repo> --jq .full_name`. Si
   l'accès est refusé, la personne n'est pas sur le dépôt : dis-le et arrête-toi pour elle.
4. Ne continue pas tant que `gh` n'est pas installé et connecté. Si la personne refuse ou ne
   peut pas, utilise seulement le repli par `git shortlog` (étape 1) en le disant
   explicitement, car la vérification est alors incomplète.
Une fois `gh` prêt, ne redemande rien aux sessions suivantes.

## Étape 1 — Poser la question (toujours, avant de planifier)

**Qui travaille ?** Ne devine jamais l'équipe. Demande à Prude les noms des personnes qui
doivent travailler sur ces tâches (ou le nombre, si c'est tout ce qu'il donne, puis les
noms). Prude peut aussi travailler seul : dans ce cas il n'y a rien à répartir, applique
juste l'étape 5 (suivi) à ses tâches.

**Vérifie chaque personne sur le dépôt GitHub avant de lui confier quoi que ce soit.**
Une personne qui n'est pas sur le dépôt ne travaille pas sur le projet : elle ne reçoit
aucune tâche, et tu le dis clairement (« X n'est pas sur le dépôt, je ne lui confie rien »).
Récupère le dépôt avec `git remote get-url origin` (plusieurs dépôts dans un projet, ex.
app + backend : vérifie chacun de ceux que les tâches touchent). Méthodes, dans l'ordre :
1. `gh` (installé et connecté à l'étape 0) :
   `gh api repos/<owner>/<repo>/collaborators --jq '.[].login'` (membres réels du dépôt, même
   sans commit). Cette liste exige des droits d'écriture sur le dépôt ; en cas de refus
   (403), essaie `gh api repos/<owner>/<repo>/contributors --jq '.[].login'`.
2. En dernier recours seulement (étape 0 refusée ou impossible), les auteurs de commits : `git shortlog -sne --all`. Cette méthode est plus faible
   (un collaborateur qui n'a encore jamais commité n'apparaît pas) : dis-le, et demande
   confirmation à Prude pour ceux qui ne ressortent pas.
Rapproche le nom donné d'un login, d'un nom ou d'un e-mail ; si le rapprochement est
ambigu (plusieurs auteurs possibles), demande, ne choisis pas. Seules les personnes
confirmées sur le dépôt forment l'équipe : N = leur nombre, et la répartition se fait
uniquement entre elles, selon ce que Prude a dit (qui fait quoi, s'il l'a précisé).

Si aucune liste de tâches n'est fournie (le skill est invoqué seul, ou avec seulement un
nombre de personnes), demande-la avant de continuer. N'invente des tâches que si Prude
demande explicitement un test à blanc, et dis alors clairement qu'elles sont fictives.

Demande aussi, seulement si ce n'est pas évident, en un seul message :
- le nom d'affichage de chaque personne confirmée sur le dépôt (il s'affiche sur la page de
  suivi ; n'écris jamais « Personne 1, 2, 3 » dans le plan ni dans la base, sauf pour un
  test à blanc annoncé comme tel) ;
- si le travail se fait sur **une branche par personne** (par défaut : oui, une branche
  `feat/<prenom>-<sujet>` par personne, depuis la branche de dev commune) ;
- si certains sont plus à l'aise sur une partie (front, back, mobile) — un critère de
  préférence, jamais une contrainte.

## Étape 2 — Cartographier les tâches

Pour chaque tâche soumise, lis le code **de façon ciblée** (grep/glob, pas de lecture
exhaustive) et note :
- les **fichiers/dossiers** qu'elle touchera (par module, pas seulement par nom) ;
- les **ressources partagées** : schéma de base de données / migrations Prisma, fichiers de
  routes ou de navigation, `pubspec.yaml` / `package.json` et lockfiles, fichiers de
  config, thèmes/constantes globales, fichiers générés, barrels (`index`), injection de
  dépendances, fichiers de traduction ;
- les **dépendances entre tâches** (B a besoin de ce que A produit : endpoint, modèle,
  composant).

Si une tâche est trop vague pour être cartographiée, pose la question au lieu d'inventer.

## Étape 3 — Répartir en deux temps : d'abord la charge, ensuite les conflits

**3a. Répartition initiale, sans tenir compte des conflits.** Partage les tâches entre les
personnes confirmées uniquement selon la **charge** : estime chaque tâche (`seniorEstimateH`,
voir étape 5) et équilibre le total par personne. Respecte ce que Prude a demandé (« telle
tâche à telle personne », préférences) avant tout autre critère. Ne regroupe pas par fichier
ou par module et n'écarte aucune répartition parce que deux personnes toucheraient les mêmes
fichiers : à ce stade, les conflits ne comptent pas. Une tâche garde sa personne tant que
l'équilibre n'impose pas de la déplacer, et les moins de mouvements possibles sont préférés.

**3b. Ensuite seulement, analyse les conflits de ce partage.** Avec la cartographie de
l'étape 2, liste chaque point de friction :
- **fichier ou dossier touché par deux personnes** (ou plus) : le fichier, les tâches et les
  personnes concernées, et si les modifications risquent d'être aux mêmes endroits ou à des
  endroits différents du fichier ;
- **ressource partagée** (migrations, `pubspec`/`package.json` et lockfiles, routes, config,
  fichiers générés, injection de dépendances, traductions) touchée par plusieurs personnes ;
- **dépendance entre tâches** de personnes différentes (B a besoin de ce que A produit) : définis
  le contrat (signature d'endpoint, modèle, nom de composant) pour que B démarre sur un mock,
  ou mets A en vague 1 et B en vague 2.
Dis honnêtement ce que tu n'as pas vérifié (cartographie faite par lecture ciblée, pas par
mesure).

**3c. Propose, sans l'imposer, une variante sans conflit** quand l'analyse en trouve : même
liste de tâches, mais selon ces règles, par ordre de priorité :
1. un fichier n'appartient qu'à UNE personne : deux tâches qui touchent le même fichier vont à
   la même personne ;
2. chaque ressource partagée a un seul propriétaire ;
3. regrouper par module ou fonctionnalité, puis rééquilibrer la charge sans casser 1 et 2 ;
4. si N > nombre de lots indépendants, dis-le plutôt que de forcer un découpage.
Indique pour la variante : les tâches qui changent de personne, la charge par personne avant
et après, et ce que ça coûte en équilibre. **Prude choisit** : répartition initiale (conflits
assumés, avec la liste des fichiers à coordonner) ou variante sans conflit. N'applique jamais la
variante de toi-même, et ne l'écris pas dans le suivi tant qu'il n'a pas choisi.

## Étape 4 — Livrable (présenter dans le chat, court)

Présente dans cet ordre : (1) la **répartition initiale** par charge (3a), (2) les
**conflits attendus** (3b) sous forme de tableau « fichier ou ressource → tâches → personnes »,
(3) la **variante sans conflit** (3c) s'il y en a une, avec son effet sur la charge, puis
(4) demande à Prude laquelle il retient. Les blocs ci-dessous ne sont produits qu'après son
choix, pour la répartition retenue.

Écris les périmètres en **dossiers** (`lib/pages/x/`) dès qu'un dossier entier appartient à
une seule personne ; descends au fichier uniquement quand un dossier est partagé entre
plusieurs lots (ex. `lib/pages/` ou `lib/cubit/` dans un projet à plat). Un périmètre en
dossiers est plus lisible et couvre aussi les futurs fichiers créés dedans.

Pour chaque personne :

```
### <Prénom> — <thème du lot>  (charge : S/M/L)
Branche : feat/<prenom>-<sujet>
Tâches : 1. … 2. …
Périmètre (à toi seul) : lib/pages/x/, lib/cubit/x/ …
Fichiers partagés (à coordonner avec <Prénom>) : <fichier> — <tâches concernées>
Interdit de toucher : le périmètre exclusif des autres, sauf accord sur les fichiers partagés
Dépend de : <rien | tâche de Y, contrat : …>
```

Puis :
- **Ressources partagées** : tableau « ressource → propriétaire » (migrations, deps, routes…).
- **Ordre** : vague 1 (en parallèle) → point de sync/merge → vague 2.
- **Ordre de merge** recommandé (le plus « fondation » d'abord) et qui rebase sur quoi.
- **Prompt prêt à coller** pour le Claude de chaque personne : un bloc court qui rappelle ses
  tâches, son périmètre exclusif, les fichiers partagés et avec qui les coordonner (« préviens
  <Prénom> avant d'y toucher, fais des changements petits et localisés, rebase souvent »), ce
  qu'elle ne doit pas toucher, et « si tu dois modifier un fichier hors périmètre, arrête-toi
  et dis-le à l'équipe ».
- **Conflits résiduels** à surveiller (fichiers qu'on n'a pas pu isoler) et comment les
  gérer (ex. : une seule personne édite, les autres envoient leur ajout).

## Étape 5 — Suivi (page web en direct + copie privée dans le dépôt)

Le suivi existe en **deux exemplaires qui doivent rester identiques**. Personne ne coche à la
main : c'est Claude qui tient les deux à jour.

1. **Page web en direct, une par projet** (collection `tasks`, écrite avec l'outil
   `ArtifactData`, à charger via ToolSearch si besoin). Chaque projet a sa propre page, donc
   ses propres données et sa propre liste de personnes autorisées : une équipe ne voit pas les
   tâches des autres projets. L'adresse de la page est dans **`suivi/config.json`** du dépôt
   (`{"projet": "…", "page": "https://claude.ai/artifact/…"}`), versionné avec le projet : c'est
   ainsi que le skill de chaque collègue retrouve la bonne page. Ne mélange jamais deux
   projets sur une même page.
2. **Copie privée dans le dépôt** : `suivi/tasks/<doc_id>.json`, un fichier par tâche (même
   contenu que le document de la page, sans l'identifiant, qui est le nom du fichier). Un
   fichier par tâche évite les conflits de fusion. Pour un projet à plusieurs dépôts (app +
   backend), la tâche va dans le dépôt qu'elle modifie. Le dépôt reste privé comme le projet.

À **chaque** écriture sur la page (création, démarrage, fin, correction, réouverture), réécris
aussi le fichier JSON correspondant, avec le même contenu. Si l'une des deux écritures
échoue, dis-le : ne laisse pas les deux copies diverger en silence. Ne fais ni commit ni push
des fichiers `suivi/` toi-même : propose-le à la personne (ils partent naturellement avec le
commit de la fonctionnalité, ce qui garde l'historique de qui a changé quoi dans git).

**Copie HTML partageable** : `python3 ~/.claude/skills/repartition-equipe/generer-suivi.py
<dépôt>` lit `suivi/tasks/*.json` et écrit `suivi/suivi.html`, un fichier autonome (ignoré
par git) qui s'ouvre dans un navigateur ou s'envoie en pièce jointe. Lance-le quand on te
demande « le suivi en HTML », après un `git pull` pour avoir les dernières tâches de
l'équipe. Il n'est pas mis à jour en direct et la page l'indique.

Après un `git pull`, si des fichiers `suivi/tasks/` diffèrent de la page, la page web fait foi
pour le statut courant, les fichiers font foi pour l'historique déjà commité.

**Qui est la personne de cette session ?** Chaque collègue a son propre Claude avec ce
skill installé : le nom écrit sur la page doit être le sien, jamais celui d'un autre ni un
nom générique. Détermine-le ainsi, avant toute écriture sur la page :
1. Lis `~/.claude/repartition-equipe.json` (`{"nom": "…"}`). S'il existe, utilise ce nom.
2. Sinon, lis `git config user.name` (et le login GitHub si `gh` répond), puis demande une
   fois : « Je t'enregistre sous le nom X sur la page de suivi ? » (ou demande le prénom si
   git n'en donne pas).
3. Enregistre la réponse dans `~/.claude/repartition-equipe.json` pour ne plus redemander.
Ce nom doit être celui sous lequel la personne figure dans l'équipe vérifiée sur le dépôt
(étape 1) : sinon, signale-le avant d'écrire.
Ce nom est `doneBy` pour toutes les tâches terminées dans cette session, même si la tâche
était assignée à quelqu'un d'autre. Il doit aussi correspondre, orthographe comprise, au
prénom utilisé dans `assignee` quand c'est la même personne (sinon la page affiche deux
personnes différentes).

**Trouver ou créer la page du projet.**
1. Lis `suivi/config.json` à la racine du dépôt. S'il existe, utilise sa `page` et son
   `projet` (réutilise ce nom **exactement** dans le champ `project` de chaque tâche).
2. S'il n'existe pas, c'est un nouveau projet : pars du nom du dépôt GitHub (ex.
   `tinwinlinwin-mobile` → « Tinwin mobile ») et confirme-le à Prude. Si le projet a
   plusieurs dépôts (app + backend), demande si une page existe déjà pour ce projet et
   réutilise-la.
3. Pour créer la page : charge le skill `artifact-capabilities`, copie
   `suivi-template.html` (même dossier que ce fichier) dans un fichier temporaire en
   remplaçant `<title>Suivi des lots</title>` par `<title>Suivi <Projet></title>`, puis
   publie-le avec l'outil Artifact : `icon: "checklist"`, une `description` d'une phrase, et
   `capabilities: {"db": {"rules": [{"path": "tasks", "read": "view", "write": "interact"}]}}`.
4. Écris l'adresse obtenue dans `suivi/config.json` (et le même fichier dans chaque autre dépôt
   du projet). Dis à Prude qu'il doit **partager la page** avec l'équipe du projet, avec le
   droit de contribuer, depuis son menu Partager : tu ne peux pas le faire. Seules les
   personnes confirmées sur le dépôt (étape 1) doivent y avoir accès.

**Numérotation (évite d'écraser d'autres tâches).**
1. Liste d'abord les tâches déjà sur la page du projet (`list`/`query` sur `tasks`, par pages).
2. `doc_id` = `<slug-du-projet>-<n>`, où `n` continue après le plus grand numéro déjà utilisé
   pour ce projet. Ne fais jamais un `set` sur un `doc_id` existant (il écraserait la tâche,
   son statut et son historique) : une nouvelle tâche reçoit un nouvel identifiant.
3. Ajouter des tâches à un projet en cours ne touche pas aux tâches existantes.

**À la validation du plan**, écris une tâche par document (`batch`, `doc_id` = `<projet>-<n>`),
sans le champ `example` :
`project` (nom du projet), `title`, `description`, `assignee`, `lot`, `wave`, `order`,
`branch`, `perimeter`, `size` (S/M/L), `seniorEstimateH` (nombre), `status: "todo"`.

**Heures** : `seniorEstimateH` est le temps qu'un développeur **senior** mettrait à la
main sur cette fonctionnalité (code + tests + revue). Ce n'est jamais le temps passé par
Claude. Estime à partir du périmètre réel, arrondis à 0,5 h.

**Quand une personne commence** une tâche : `update` → `status: "doing"`.

**Quand une tâche est terminée** dans la session (code écrit ET vérifié), fais toi-même un
`update` avec :
- `status: "done"`, `doneBy` (le nom de la personne de la session, voir ci-dessus),
  `doneAt` (ISO 8601 avec fuseau, heure réelle : `date -Iseconds`) ;
- `testLevel` : `aucun` | `unitaire` | `intégration` | `e2e`, plus `testsPassed` et
  `testsTotal` si des tests ont été lancés. N'écris que ce qui a réellement été exécuté ;
- `securityStatus` : `aucune faille` | `à corriger` | `corrigée` | `non vérifié`. Passe
  d'abord une vraie revue de sécurité des fichiers modifiés (autorisations et règles
  d'accès, validation des entrées, secrets en dur, injection, données d'une autre
  équipe/chorale/organisation exposées, dépendances ajoutées). Liste chaque problème dans
  `securityFindings` (tableau de phrases). Sans revue faite, mets `non vérifié`, jamais
  `aucune faille` par défaut ;
- `commit` et `notes` si utiles.

**Historique obligatoire.** Chaque document porte `history` : un tableau d'événements
`{at, by, action, note}` (`action` : `créée` | `démarrée` | `terminée` | `correction` |
`réouverte`). À chaque changement de statut, ajoute un événement avec le nom de la
personne de la session et l'heure réelle (lis le document, ajoute à la fin du tableau,
écris avec `if_version`).

**Si quelqu'un d'autre touche une tâche déjà terminée** (correction, retouche, bug
corrigé) : ne change pas `doneBy` (l'auteur d'origine reste), mets à jour `lastTouchedBy`
et `lastTouchedAt`, ajoute un événement `correction` avec une `note` qui dit ce qui a été
corrigé, et refais la revue de sécurité et les tests des fichiers touchés (mets à jour
`testLevel` et `securityStatus` en conséquence). Si tu rouvres la tâche, repasse
`status: "doing"` et ajoute `réouverte`. La page affiche cet historique et signale « repris
par … » : c'est ainsi que l'équipe sait que la tâche a été touchée.

Ne coche jamais une tâche dont le code n'a pas été relu ou testé. En cas de doute, laisse
`doing` et dis pourquoi. Pour modifier un document existant, lis-le d'abord et passe
`if_version`.

## Étape 6 — Garde-fous

- Vérifie avant de rendre le plan : chaque fichier touché par plusieurs personnes figure dans
  la liste des conflits attendus (3b), et dans la variante sans conflit aucun fichier
  n'apparaît dans deux périmètres. Fais la vérification explicitement (liste croisée) et
  mentionne que tu l'as faite.
- Ne lance aucune implémentation tant que Prude n'a pas validé la répartition.
- Respecte les conventions des autres skills du projet (ex. `flutter-conventions`,
  `backend-conventions`) pour savoir quels dossiers existent et comment ils sont découpés.
- Si les tâches évoluent en cours de route (nouvelle tâche, retard), propose une
  **re-répartition minimale** : ne déplace que ce qui est nécessaire.
- Ne crée pas de commits, branches ou pushes toi-même sauf demande explicite.

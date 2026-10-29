---
name: repartition-equipe
description: Répartit une liste de tâches entre plusieurs collègues qui travaillent en parallèle avec Claude sur le même projet, de façon proportionnelle à la charge et sans tenir compte des conflits, puis encadre l'intégration vers la branche commune (dev) : branche à jour avant chaque nouvelle tâche, et verrou de fusion pendant qu'une personne résout des conflits. Vérifie sur GitHub qui est sur le dépôt et tient le suivi des tâches. À utiliser dès que Prude (ou un collègue) soumet une liste de tâches/fonctionnalités/bugs en disant « on est N », « répartis les tâches », « qui fait quoi », ou avant de pousser/fusionner vers la branche commune quand plusieurs personnes travaillent sur le dépôt.
---

# Répartir les tâches d'une équipe et encadrer la fusion

Contexte : chaque membre de l'équipe a son propre Claude, donc n'importe qui peut tout faire.
La question n'est plus « qui sait faire quoi » mais « comment se partager le travail
équitablement et le réunir proprement ». Ce skill partage les tâches **proportionnellement à
la charge, sans se soucier des conflits de fichiers**. Les conflits se traitent au moment de
la fusion vers la branche commune, avec des règles simples (étape 4) : chacun repart d'une
base à jour, et un seul résout ses conflits à la fois pendant que les push sont bloqués.

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

## Étape 2 — Estimer les tâches

Pour chaque tâche soumise, lis le code **de façon ciblée** (grep/glob, pas de lecture
exhaustive) pour comprendre ce qu'elle demande, puis estime sa taille (S/M/L) et son effort
`seniorEstimateH` (voir étape 5). Note aussi les **dépendances** (B a besoin de ce que A
produit : endpoint, modèle, composant) : ce ne sont pas des conflits, elles servent à ordonner.
Les fichiers que chaque tâche touchera **ne sont pas analysés** ici.

Si une tâche est trop vague pour être estimée, pose la question au lieu d'inventer.

## Étape 3 — Répartir proportionnellement à la charge

Partage les tâches entre les personnes confirmées sur le dépôt (étape 1) de façon
**proportionnelle** : le total d'heures senior de chacun doit être aussi proche que possible de
`total / N` (si Prude a fixé des parts inégales, respecte-les). Règles :
1. Ce que Prude a demandé explicitement (« telle tâche à telle personne ») passe avant tout.
2. **Ne tiens pas compte des conflits** : ne regroupe pas par fichier ou par module, n'écarte
   pas un partage parce que deux personnes toucheraient les mêmes fichiers.
3. Une dépendance entre deux tâches de personnes différentes se traite par l'ordre (la tâche
   dont l'autre dépend en vague 1) ou par un contrat (signature, nom de composant) pour
   travailler sur un faux en attendant.
4. Si N est plus grand que ce que la charge justifie, dis-le plutôt que de donner des
   miettes de tâches.

## Étape 4 — Livrable, puis règles d'intégration

Présente dans le chat, court : pour chaque personne,

```
### <Prénom> — <thème du lot>  (charge : X h senior, Y % du total)
Branche : feat/<prenom>-<sujet>, créée depuis <branche commune> à jour
Tâches : 1. … 2. …
Dépend de : <rien | tâche de Y, contrat : …>
```

puis les totaux (la somme des heures de tous doit égaler le total), l'ordre si des
dépendances existent, et un **prompt prêt à coller** pour le Claude de chaque personne : ses
tâches, sa branche et le rappel des règles ci-dessous.

### Règles d'intégration (branche commune)

La branche commune est le champ `brancheCommune` de `suivi/config.json` (ex. `dev`). S'il
n'existe pas, détecte la branche par défaut du dépôt (`gh repo view --json
defaultBranchRef`), confirme-la à Prude et enregistre-la dans `suivi/config.json`.

**A. Être à jour avant de prendre une tâche.** Avant de passer une tâche à `doing`, et avant
d'en prendre une nouvelle :
1. `git fetch origin`, puis vérifie `git merge-base --is-ancestor origin/<commune> HEAD`.
2. Si la réponse est non, la branche est en retard : mets-la à jour avec `origin/<commune>`
   (merge) et règle les conflits éventuels, puis seulement démarre. Une tâche nouvelle part
   toujours de la branche commune distante à jour.
3. Si un verrou de fusion existe (B ci-dessous), attends qu'il soit libéré puis refais le
   `fetch` : la base va changer.
4. Ne démarre pas la tâche tant que ce n'est pas vrai. Dis à la personne ce qui bloque.

**B. Fusion vers la branche commune : celui qui arrive après résout, et les push sont
bloqués pendant ce temps.** Quand la personne demande de pousser ou de fusionner vers la
branche commune :
1. `git fetch origin`. Lis le document `locks/<commune>` de la page de suivi. S'il existe,
   quelqu'un résout des conflits : **ne pousse rien**. Dis qui (`holder`) et depuis quand
   (`since`), et propose de réessayer. Un verrou de plus de 2 h : demande à Prude avant de le
   considérer comme périmé et de le supprimer.
2. Si la branche commune distante n'a pas avancé depuis ta dernière mise à jour, pousse :
   pas de conflit possible.
3. Si elle a avancé (quelqu'un a déjà fusionné) : fusionne-la dans ta branche.
   - Sans conflit : relance les tests, puis pousse.
   - **Avec conflits** : pose le verrou avant de les résoudre. Crée le document
     `locks/<commune>` avec `holder` (le nom de la personne), `branch`, `tasks` (les
     `doc_id`), `reason: "résolution de conflits"`, `since` (heure réelle). Écris-le **sans**
     `if_version` : si le document existe déjà, l'écriture est refusée, donc deux personnes
     ne peuvent pas poser le verrou en même temps (retombe alors sur l'étape 1). Résous les
     conflits, relance les tests, pousse, puis **supprime le verrou** (`delete` avec
     `if_version`).
4. Libère toujours le verrou, même en cas d'abandon ou d'échec, et dis-le.
5. Après un push réussi, ajoute à chaque tâche concernée un événement `fusionnée` dans son
   `history` (nom de la personne, heure, note avec le commit).

**Limite à dire clairement :** ce verrou est coopératif. Il bloque les sessions qui utilisent
ce skill, pas un `git push` tapé à la main. Pour un blocage réel côté GitHub, propose à Prude
d'activer la protection de la branche commune avec « Require branches to be up to date
before merging » (et pull requests obligatoires), via `gh api` : droits d'administrateur
requis, et ne le fais que s'il le demande.

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
   `capabilities: {"db": {"rules": [{"path": "tasks", "read": "view", "write": "interact"}, {"path": "locks", "read": "view", "write": "interact"}]}}`.
4. Écris l'adresse obtenue dans `suivi/config.json` (et le même fichier dans chaque autre dépôt
   du projet) et ajoute au `README.md` du dépôt une section « Suivi des tâches » avec l'adresse,
   la mention que la page est privée (à partager avec le droit de contribuer) et le lien du
   skill : c'est ce que les collègues liront. Rappelle à Prude de **commiter et pousser**
   `suivi/config.json` et le README : sans cela personne d'autre ne retrouve la page. Dis à Prude qu'il doit **partager la page** avec l'équipe du projet, avec le
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
`branch`, `size` (S/M/L), `seniorEstimateH` (nombre), `status: "todo"`.

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

- Vérifie avant de rendre le plan : la somme des heures par personne égale le total, chaque
  personne est confirmée sur le dépôt, et chaque tâche est attribuée une seule fois.
- Ne lance aucune implémentation tant que Prude n'a pas validé la répartition.
- Respecte les conventions des autres skills du projet (ex. `flutter-conventions`,
  `backend-conventions`) pour estimer les tâches.
- Si les tâches évoluent en cours de route (nouvelle tâche, retard), propose une
  **re-répartition minimale** : ne déplace que ce qui est nécessaire.
- Ne crée pas de commits, branches ou pushes toi-même sauf demande explicite. Quand la
  personne demande un push ou une fusion vers la branche commune, applique les règles
  d'intégration (étape 4) sans les sauter. Quand la
personne demande un push ou une fusion vers la branche commune, applique les règles
d'intégration (étape 4) sans les sauter.

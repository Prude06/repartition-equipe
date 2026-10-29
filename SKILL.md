---
name: repartition-equipe
description: Répartit une liste de tâches entre plusieurs collègues qui travaillent en parallèle avec Claude sur le même projet, sans conflit de travail (fichiers, migrations, routes, dépendances). Demande d'abord combien de personnes sont sur le projet, puis produit un plan par personne avec périmètre de fichiers exclusif, ordre d'exécution et points de synchronisation. À utiliser dès que Prude (ou un collègue) soumet une liste de tâches/fonctionnalités/bugs en disant « on est N », « répartis les tâches », « qui fait quoi », ou quand plusieurs personnes vont lancer Claude en même temps sur le même dépôt.
---

# Répartir les tâches d'une équipe sans conflit

Contexte : chaque membre de l'équipe a son propre Claude, donc n'importe qui peut tout faire.
Le vrai risque n'est plus « qui sait faire quoi » mais **deux personnes qui modifient les mêmes
fichiers** (conflits git, migrations en double, doublons de code). Ce skill découpe le travail
pour que chacun avance en parallèle sans se marcher dessus.

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

## Étape 3 — Répartir

Règles, par ordre de priorité :

1. **Périmètre exclusif** : un fichier n'appartient qu'à UNE personne. Si deux tâches
   touchent le même fichier, elles vont à la même personne — sans exception.
2. **Regrouper par module/fonctionnalité**, pas par nombre de tâches : mieux vaut une charge
   déséquilibrée sans conflit qu'une charge égale avec des collisions.
3. **Ressources partagées = un seul propriétaire** : une personne seule gère les migrations,
   les dépendances (`pubspec`/`package.json`), le routeur et la config. Les autres lui
   demandent l'ajout, ou le font via la « zone de contact » (étape 4).
4. **Dépendances** : si B dépend de A, soit même personne, soit A est livrée d'abord
   (vague 1) et B passe en vague 2 après merge. Définis le **contrat** (signature de l'endpoint,
   modèle, nom du composant) pour que B puisse démarrer en parallèle sur un faux/mock.
5. **Équilibrer ensuite** la charge (estimation S/M/L) entre les personnes, sans casser 1–4.
6. Si N > nombre de lots indépendants, dis-le : mieux vaut que certains soient en
   revue/test/documentation que de forcer un découpage qui crée des conflits.

## Étape 4 — Livrable (présenter dans le chat, court)

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
Interdit de toucher : tout ce qui est dans le périmètre des autres + ressources partagées
Dépend de : <rien | tâche de Y, contrat : …>
```

Puis :
- **Ressources partagées** : tableau « ressource → propriétaire » (migrations, deps, routes…).
- **Ordre** : vague 1 (en parallèle) → point de sync/merge → vague 2.
- **Ordre de merge** recommandé (le plus « fondation » d'abord) et qui rebase sur quoi.
- **Prompt prêt à coller** pour le Claude de chaque personne : un bloc court qui rappelle ses
  tâches, son périmètre exclusif, ce qu'elle ne doit pas toucher, et « si tu dois modifier un
  fichier hors périmètre, arrête-toi et dis-le à l'équipe ».
- **Conflits résiduels** à surveiller (fichiers qu'on n'a pas pu isoler) et comment les
  gérer (ex. : une seule personne édite, les autres envoient leur ajout).

## Étape 5 — Suivi sur la page web (après validation de la répartition)

Page : https://claude.ai/artifact/J5zvqXDWLJv5nx2K4mo1DN (collection `tasks`, écrite avec
l'outil `ArtifactData`, à charger via ToolSearch si besoin). Personne ne coche à la main :
c'est Claude qui tient la page à jour.

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

- Vérifie avant de rendre le plan : aucun fichier n'apparaît dans deux périmètres. Fais
  la vérification explicitement (liste croisée) et mentionne que tu l'as faite.
- Ne lance aucune implémentation tant que Prude n'a pas validé la répartition.
- Respecte les conventions des autres skills du projet (ex. `flutter-conventions`,
  `backend-conventions`) pour savoir quels dossiers existent et comment ils sont découpés.
- Si les tâches évoluent en cours de route (nouvelle tâche, retard), propose une
  **re-répartition minimale** : ne déplace que ce qui est nécessaire.
- Ne crée pas de commits, branches ou pushes toi-même sauf demande explicite.

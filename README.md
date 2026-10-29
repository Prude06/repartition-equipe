# repartition-equipe

Un skill pour [Claude Code](https://claude.com/claude-code) qui répartit les tâches d'une équipe
sans conflit, et garde une trace honnête de qui a fait quoi.

## Pourquoi ce skill existe

Quand toute l'équipe travaille avec Claude, la question « qui sait faire quoi ? » disparaît :
chacun peut tout faire. Un autre problème prend sa place.

- **On ne sait plus se répartir le travail.** Sans compétences qui départagent, chacun prend ce
  qui lui passe par la tête, ou deux personnes prennent la même chose.
- **Les conflits arrivent vite.** Deux Claude qui modifient en parallèle les mêmes fichiers, la
  même migration ou le même `pubspec.yaml` produisent des conflits git, du code en double et des
  heures de fusion.
- **On perd la trace.** Quand tout va vite, personne ne sait ce qui est fini, par qui, si c'est
  testé, ni si quelqu'un est revenu corriger après coup.
- **Le temps de Claude ne dit rien.** Une fonctionnalité faite en dix minutes par Claude ne
  renseigne ni sur son ampleur, ni sur ce qu'elle aurait coûté à la main.

Ce skill partage le travail équitablement, encadre la fusion vers la branche commune, puis
suit l'avancement de façon fiable.

## Ce qu'il fait

### 1. Il vérifie qui travaille vraiment
Tu donnes les noms des personnes. Le skill vérifie sur le dépôt GitHub (via `gh`) que chacune
en est collaboratrice ou collaborateur. Quelqu'un qui n'est pas sur le dépôt ne travaille pas
sur le projet : aucune tâche ne lui est confiée, et le skill te le dit.

### 2. Il répartit proportionnellement à la charge
Il partage les tâches selon l'estimation senior de chacune, pour que chacun ait une part
équivalente (ou celle que tu fixes), et **sans tenir compte des conflits de fichiers**. Chaque
personne reçoit sa branche, ses tâches, et un prompt prêt à coller dans son Claude.

### 3. Il encadre la fusion vers la branche commune
Les conflits se règlent au moment de la fusion, avec trois règles :

- **Être à jour avant chaque nouvelle tâche.** Avant de démarrer, chacun fait `git fetch` et
  vérifie qu'il a tout ce que `dev` contient. Sinon il met sa branche à jour d'abord.
- **Celui qui arrive après résout.** Si quelqu'un a déjà fusionné et que ta fusion crée des
  conflits, c'est toi qui les résous.
- **Aucun push pendant ce temps.** Dès que quelqu'un commence à résoudre des conflits, il pose
  un verrou visible sur la page de suivi. Personne d'autre ne pousse vers `dev` avant sa
  libération, puis chacun se remet à jour.

Le verrou est coopératif : il protège les sessions qui utilisent le skill, pas un `git push`
tapé à la main. Pour un blocage côté GitHub, active la protection de branche « Require branches
to be up to date before merging ».

### 4. Il tient une page de suivi
Après ta validation, les tâches sont enregistrées sur une page web partagée. Personne ne coche à
la main : c'est le Claude de la personne qui termine, après avoir vérifié son travail.

Pour chaque tâche, la page affiche :

- le statut (à faire, en cours, terminé) ;
- **qui l'a faite et quand** ;
- **l'estimation d'un développeur senior** pour cette fonctionnalité, jamais le temps de Claude ;
- le **niveau de test** réellement exécuté (aucun, unitaire, intégration, e2e) ;
- le résultat de la **revue de sécurité** (aucune faille, à corriger, corrigée, non vérifié) ;
- l'**historique** : si quelqu'un d'autre retouche une tâche terminée, la page signale « Repris
  par … » et garde l'auteur d'origine.

Chaque projet a **sa propre page**, partagée seulement avec son équipe : personne ne voit les
tâches d'un projet auquel il n'appartient pas. L'adresse de la page est dans `suivi/config.json`
du dépôt, ce qui permet à chaque collègue de la retrouver.

### 5. Il garde une copie privée dans chaque dépôt
En plus de la page en direct, chaque tâche est écrite dans `suivi/tasks/<id>.json` du dépôt
concerné, donc privée comme le dépôt et suivie par git. Un fichier par tâche évite les conflits
de fusion. Le script `generer-suivi.py` en tire un fichier HTML autonome (`suivi/suivi.html`) à
ouvrir dans un navigateur ou à envoyer. Ce fichier ne se met pas à jour tout seul : il est
régénéré à la demande, après un `git pull`.

## Les règles auxquelles il tient

- Il ne devine jamais l'équipe et demande les noms.
- Il n'écrit rien dans le suivi sans que la répartition ait été validée.
- Il ne coche jamais une tâche dont le code n'a pas été relu ou testé. Un contrôle de sécurité
  non fait reste « non vérifié », il n'est jamais déclaré « aucune faille » par défaut.
- Il n'écrase jamais une tâche existante en ajoutant de nouvelles tâches.
- Il ne pousse jamais vers la branche commune quand un verrou de fusion est posé.
- Il ne crée ni commit, ni branche, ni push de lui-même.

## Où trouver la page de suivi de mon projet

Chaque projet a sa propre page, et son adresse n'est pas dans ce dépôt. Pour la trouver :

1. Dans le dépôt de **ton projet** (pas celui du skill), ouvre `suivi/config.json` : le champ
   `page` contient l'adresse. Elle figure aussi dans le `README.md` du projet, section « Suivi des
   tâches ».
2. Si ces fichiers n'existent pas chez toi, fais un `git pull` : ils sont versionnés avec le
   projet. S'ils n'y sont toujours pas, personne ne les a encore poussés : demande-le à celui qui
   a lancé la répartition.
3. La page est privée : demande à son propriétaire de te la partager avec le droit de contribuer.
   Tu ne verras que les pages des projets sur lesquels tu as été ajouté.

Quand le skill crée la page d'un nouveau projet, il écrit son adresse dans `suivi/config.json` et
dans le `README.md` du projet. Il te rappelle de les commiter et de partager la page.

## Installation

```
git clone https://github.com/Prude06/repartition-equipe ~/.claude/skills/repartition-equipe
```

Le détail complet (accès à la page de suivi, GitHub CLI, connexion, nom affiché, dépannage) est
dans [INSTALLATION.md](INSTALLATION.md). Le comportement exact du skill est décrit dans
[SKILL.md](SKILL.md).

## Limites

- Les estimations « senior » sont des ordres de grandeur faits à partir du périmètre, pas des
  mesures.
- Si `gh` n'est pas disponible, la vérification se rabat sur les auteurs de commits : elle est
  alors incomplète, car un collaborateur qui n'a jamais commité n'apparaît pas.
- Le partage ignore les conflits : ils arrivent à la fusion, où le skill les encadre sans les
  supprimer. Plus deux personnes touchent les mêmes fichiers, plus la fusion coûte.
- Le verrou de fusion ne bloque pas un `git push` fait hors du skill.

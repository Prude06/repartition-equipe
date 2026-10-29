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

Ce skill partage le travail équitablement, met les conflits attendus sur la table, puis suit
l'avancement de façon fiable.

## Ce qu'il fait

### 1. Il vérifie qui travaille vraiment
Tu donnes les noms des personnes. Le skill vérifie sur le dépôt GitHub (via `gh`) que chacune
en est collaboratrice ou collaborateur. Quelqu'un qui n'est pas sur le dépôt ne travaille pas
sur le projet : aucune tâche ne lui est confiée, et le skill te le dit.

### 2. Il répartit d'abord, puis il regarde les conflits
Il partage les tâches selon la **charge** (estimation senior de chacune), en respectant ce que
tu as demandé, sans se préoccuper des conflits à ce stade. Ensuite seulement, il liste ce que
ce partage risque : fichiers touchés par deux personnes, ressources partagées (migrations,
dépendances, routes, config), dépendances entre tâches.

S'il trouve des conflits, il propose une **variante sans conflit** : un fichier n'appartient
qu'à une personne, chaque ressource partagée a un propriétaire. Il indique ce qui change de
main et ce que ça coûte en équilibre. **Tu choisis** : partage équilibré avec les fichiers à
coordonner, ou variante sans conflit. Rien n'est appliqué ni écrit dans le suivi avant ton choix.

Chaque personne reçoit ensuite sa branche, son périmètre, les fichiers à coordonner avec qui,
et un prompt prêt à coller dans son Claude.

### 3. Il tient une page de suivi
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

### 4. Il garde une copie privée dans chaque dépôt
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
- Il ne crée ni commit, ni branche, ni push de lui-même.

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
- Le skill réduit les risques de conflit, il ne les supprime pas : les fichiers impossibles à
  isoler sont signalés dans le plan, avec la personne qui en est responsable.

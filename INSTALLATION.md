# Installer le skill `repartition-equipe`

Ce skill répartit des tâches entre collègues sans conflit, puis tient à jour une page de suivi
(coché par Claude, avec le nom de la personne, la date, les tests, la sécurité et l'historique).
À faire une seule fois par personne, sur sa machine.

## 1. Copier le skill

Le plus simple, avec git :
```
git clone https://github.com/Prude06/repartition-equipe ~/.claude/skills/repartition-equipe
```
(pour mettre à jour plus tard : `git -C ~/.claude/skills/repartition-equipe pull`)

Sans git, copie tout le dossier `repartition-equipe/` (ce fichier, `SKILL.md`) dans :
- Linux / macOS : `~/.claude/skills/repartition-equipe/`
- Windows : `%USERPROFILE%\.claude\skills\repartition-equipe\`

Relance Claude Code. Le skill s'appelle ensuite avec `/repartition-equipe`, ou se déclenche
quand tu soumets une liste de tâches (« on est 3 », « répartis les tâches »).

## 2. Obtenir l'accès à la page de suivi

Page : https://claude.ai/artifact/J5zvqXDWLJv5nx2K4mo1DN

- Demande au propriétaire de te partager la page (menu **Partager**) avec le droit de
  **contribuer** : sans ça, ton Claude ne pourra pas cocher tes tâches.
- Utilise un compte Claude de la même organisation que le propriétaire, ou celui qu'il a invité.
- Ouvre la page une fois pour vérifier que tu la vois.

## 3. Être sur le dépôt GitHub du projet

Le skill ne confie des tâches qu'aux personnes présentes sur le dépôt GitHub. Si tu n'es pas
collaborateur du dépôt, aucune tâche ne te sera donnée. Demande à être ajouté au propriétaire
du dépôt (Settings → Collaborators).

## 4. Installer GitHub CLI (`gh`) et te connecter

Le skill le fait pour toi au premier lancement, mais voici ce qu'il va faire :

1. **Installer `gh`** :
   - Fedora : `sudo dnf install -y gh`
   - Debian / Ubuntu : `sudo apt install -y gh`
   - macOS : `brew install gh`
   - Windows : `winget install --id GitHub.cli`

   Si la commande demande un mot de passe, tape-la toi-même dans Claude avec le préfixe `!` :
   `! sudo dnf install -y gh`
2. **Te connecter** : tape `! gh auth login`, puis choisis **GitHub.com**, **HTTPS**, et la
   connexion **par navigateur**.
3. **Le code à 8 caractères** : le terminal affiche une ligne
   `First copy your one-time code: ABCD-1234`. Copie ce code, appuie sur Entrée, et colle-le
   sur https://github.com/login/device (la page s'ouvre toute seule, sinon va à cette adresse),
   puis autorise l'accès. Le code expire au bout de quelques minutes : relance
   `! gh auth login` si besoin. Si GitHub te demande en plus un code à 6 chiffres, c'est celui
   de ton application d'authentification.
4. Vérifie : `gh auth status` doit afficher « Logged in to github.com ».

## 5. Ton nom sur la page

Au premier usage, Claude te propose le nom pris dans `git config user.name` (ou ton login
GitHub) et te demande de le confirmer. Il l'enregistre dans `~/.claude/repartition-equipe.json`.
Ce nom apparaît dans « Fait par » : vérifie qu'il est correct (ton vrai nom, pas un pseudo
générique) avant de confirmer. Pour le changer plus tard, modifie ce fichier.

## 6. Ce que fait ensuite le skill

- Il te demande qui travaille, vérifie chaque personne sur le dépôt, et ne donne rien à
  quelqu'un qui n'y est pas.
- Il partage les tâches avec des périmètres de fichiers exclusifs, et attend ta validation.
- À la validation, il enregistre les tâches sur la page. Quand tu termines une fonctionnalité,
  ton Claude la coche avec ton nom, la date, l'estimation d'un développeur senior, le niveau de
  test et le résultat de la revue de sécurité.
- Si quelqu'un d'autre retouche une tâche terminée, la page affiche « Repris par … » avec
  l'historique.

## En cas de problème

| Symptôme | Cause probable |
|---|---|
| Le skill n'apparaît pas | Dossier mal placé, ou Claude Code pas relancé |
| La page est visible mais Claude ne peut pas y écrire | Droit de contribuer manquant (étape 2) |
| « Tu n'es pas sur le dépôt » | Pas collaborateur GitHub (étape 3) |
| `gh auth login` échoue | Code expiré : relance la commande |
| Un mauvais nom s'affiche | Corrige `~/.claude/repartition-equipe.json` |

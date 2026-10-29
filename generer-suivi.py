#!/usr/bin/env python3
"""Génère un fichier HTML autonome du suivi des tâches d'un dépôt.

Usage : python3 generer-suivi.py [chemin-du-depot] [-o sortie.html]

Lit <depot>/suivi/tasks/*.json (un fichier par tâche, l'identifiant est le nom du fichier)
et écrit <depot>/suivi/suivi.html (ignoré par git). Le fichier ne dépend de rien d'autre :
il s'ouvre dans un navigateur et peut être envoyé tel quel.
"""
import argparse, json, sys
from datetime import datetime
from pathlib import Path

ICI = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument("depot", nargs="?", default=".")
    p.add_argument("-o", "--sortie")
    a = p.parse_args()

    suivi = Path(a.depot).resolve() / "suivi"
    dossier = suivi / "tasks"
    if not dossier.is_dir():
        sys.exit(f"Introuvable : {dossier}")

    taches = []
    for f in sorted(dossier.glob("*.json")):
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"JSON invalide dans {f.name} : {e}")
        t["id"] = f.stem
        taches.append(t)

    # "</" fermerait la balise <script> ; "&" et les séparateurs U+2028/9 sont neutralisés aussi.
    donnees = (json.dumps(taches, ensure_ascii=False)
               .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
               .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))
    genere = datetime.now().astimezone().isoformat(timespec="seconds")

    page = (ICI / "suivi-template.html").read_text(encoding="utf-8")
    entete = ('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
              '<style>html{color-scheme:light}body{margin:0}</style>\n</head>\n<body>\n')
    injection = f"<script>window.__TASKS__={donnees};window.__GENERATED__={json.dumps(genere)};</script>\n"
    # Les données doivent exister avant le script de la page.
    marque = "<script>\nconst $ ="
    if marque not in page:
        sys.exit("Modèle inattendu : début du script introuvable.")
    page = page.replace(marque, injection + marque, 1)

    sortie = Path(a.sortie) if a.sortie else suivi / "suivi.html"
    sortie.write_text(entete + page + "\n</body>\n</html>\n", encoding="utf-8")
    ignore = suivi / ".gitignore"
    if not ignore.exists():
        ignore.write_text("suivi.html\n", encoding="utf-8")
    print(f"{len(taches)} tâche(s) -> {sortie}")


if __name__ == "__main__":
    main()

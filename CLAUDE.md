# CLAUDE.md — InduSense

Projet pédagogique (formation « Concevoir et implémenter une solution d'IA »). InduSense 4.0 :
données industrielles (télémétrie machines, relevés d'incidents, référentiel machines).

## Stack
- Python **3.15** géré par **uv** (`.python-version`, `pyproject.toml`)
- pandas, Jupyter (ipykernel en dépendance dev), notebooks ouverts dans VS Code
- Ajouter une dépendance : `uv add <pkg>` (dev : `uv add --dev <pkg>`). Jamais `pip install`.
- Lancer du code : `uv run python ...`
- PostgreSQL 15 + pgAdmin via `docker compose up -d db admin` (seuls services utilisés ;
  Prometheus/Grafana du compose ne sont pas lancés). Base sur `localhost:5434`, pgAdmin sur `localhost:8081`.
- Connexion Python : SQLAlchemy + psycopg 3, variables lues dans `.env` avec python-dotenv.
- `.env` (créé depuis `env.sample`) contient le sel `ANONYMISATION_SALT` : **jamais versionné**, jamais affiché.

## Structure
- `datas/` : fichiers sources (CSV, SQL), **couche Bronze : données brutes immuables**.
  Lecture seule : ne jamais modifier, nettoyer, renommer ni réécrire ces fichiers.
  Tout résultat va dans `artifacts/`. **Versionné** : le formateur clone et relance le notebook.
- `*.ipynb` : notebooks à la racine, au même niveau que `datas/`
- `artifacts/ingestion/identities/AAAAMMJJ/<fichier>_HHMMSS.md` : cartes d'identité générées
  (**non versionné**, recréé par le notebook)

## Sprint 1 — cartes d'identité des CSV
Pour chaque CSV : source, taille (Ko/Mo), ProcessBeginAt/EndAt, charset, nb lignes/colonnes,
tableau colonnes + type inféré, et min/max (+ mean/median si numérique) pour colonnes numériques et dates.
- Le séparateur n'est pas toujours `,` (`;`, `\t`) → le détecter.
- Le script SQL (`machine.sql.txt`) est lu avec **sqlglot** (dialecte postgres, jamais exécuté) :
  une seule carte pour le fichier, une section par table (types déclarés du CREATE TABLE, valeurs des INSERT).

## Conventions
- Ne pas faire plus que ce qui est demandé, mais pas moins.
- Code factorisé en fonctions dans le notebook.
- Git : jamais de travail direct sur `main`. Une branche par incrément (`feat/...`),
  commits fréquents avec messages explicites, merge dans `main` puis push de `main`.
- Commits au nom de l'utilisateur uniquement : pas de ligne `Co-Authored-By`.

# InduSense

Pipeline de données pour la maintenance prédictive (architecture Bronze → Silver → Gold).

- `identity_cards.ipynb` : cartes d'identité des fichiers sources (`datas/`)
- `bronze_ingestion.ipynb` : ingestion des données brutes dans PostgreSQL (couche Bronze)

## Prérequis

- [uv](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/get-docker/) avec Docker Compose
- VS Code avec les extensions Python et Jupyter

## Installation

### 1. Cloner le projet et installer l'environnement Python

```shell
git clone https://github.com/keziah974/indusense.git
cd indusense
uv sync
```

`uv sync` installe Python 3.15 si besoin, puis toutes les dépendances du projet.

### 2. Créer le fichier `.env`

```shell
cp env.sample .env
```

Remplacer ensuite le sel d'anonymisation de l'exemple par une valeur secrète. Générer une valeur :

```shell
openssl rand -hex 32
```

et la coller dans `.env` :

```
ANONYMISATION_SALT=<valeur générée>
```

Le `.env` n'est jamais versionné (il est dans le `.gitignore`). Si les ports `5434` (PostgreSQL) ou `8081` (pgAdmin)
sont déjà utilisés sur la machine, modifier `DB_PORT` et `GUI_PORT` dans le `.env`.

### 3. Lancer PostgreSQL et pgAdmin

```shell
docker compose up -d --wait db admin
```

Seuls les services `db` (PostgreSQL) et `admin` (pgAdmin) sont utilisés pour l'instant ; les autres services du
`docker-compose.yml` (Prometheus, Grafana…) ne sont pas lancés.

Vérifier que la base répond :

```shell
docker compose ps
docker compose exec db psql -U indusense_user -d indusense_db -c "select version();"
```

### 4. Se connecter à pgAdmin (optionnel)

1. Ouvrir http://localhost:8081 et se connecter avec `GUI_EMAIL` / `GUI_PASSWORD` du `.env`.
2. Clic droit sur **Servers** → **Register** → **Server** :
   - **General** → Name : `indusense`
   - **Connection** → Host : `db`, Port : `5432`, Database : `indusense_db`,
     Username : `DB_USER`, Password : `DB_PASSWORD` (valeurs du `.env`)

> L'hôte est `db` et le port `5432` (et non `localhost:5434`) : pgAdmin tourne dans Docker, sur le même réseau que la base.

### 5. Lancer les notebooks

Ouvrir le projet dans VS Code (`code .`), ouvrir un notebook, sélectionner le kernel `.venv` puis **Run All**.

## Arrêter et nettoyer

```shell
docker compose stop db admin          # arrêter (les données sont conservées)
docker compose down                   # supprimer les conteneurs (les données sont conservées)
docker compose down -v                # supprimer aussi les volumes : la base est effacée
```

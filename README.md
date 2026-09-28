# Gestion des Groupes Scolaires (Mali)

Application web de gestion d'une école fondamentale au Mali (1ère → 9ème année)
développée avec **Python + Django 6** et **PostgreSQL**.

## Fonctionnalités

- **Tableau de bord** : effectifs, enseignants, classes, présences du jour, résultats, encaissements.
- **Élèves** : matricule, identité, photo, parent/tuteur, statut, historique scolaire.
- **Classes** : 1ère–9ème, distinction automatique des cycles (1er : 1ère–6ème, 2ème : 7ème–9ème), titulaire, effectif.
- **Enseignants** : fiches + création de compte, matières, classes affectées.
- **Matières & affectations** : coefficient, enseignant responsable par classe.
- **Notes & résultats** : évaluations (devoir / composition / examen), saisie des notes, moyennes pondérées,
  classement, bulletins, décisions de fin d'année (logique centralisée dans `apps/notes/services.py`).
- **Présences** : feuille d'appel quotidienne, absences / retards, justification, historique.
- **Inscriptions / réinscriptions** liées à l'année scolaire.
- **Finance** : frais, paiements (espèces, Orange Money, MoMo, Wave…), reçu, reste à payer.
- **Documents imprimables** : bulletin, reçu, certificat de scolarité, liste d'élèves.
- **Rôles** : `direction` (gestion complète) et `enseignant` (accès limité à ses classes/matières).

## Installation

Prérequis : Python 3.12+, PostgreSQL 17.

### Option A — Docker Compose (recommandé pour un autre environnement)

```bash
cp .env.example .env          # modifier DB_PASSWORD (mot de passe PostgreSQL)
docker compose up -d --build
docker compose run --rm web python manage.py createsuperuser
```
L'application est alors disponible sur http://localhost:8000 (PostgreSQL 17 dans un conteneur).
La migration est appliquée automatiquement au démarrage du conteneur `web` ;
`RUN_SEED=true` (variable d'environnement) charge les niveaux 1-9 et les matières.

Arrêt / nettoyage :
```bash
docker compose down                    # arrêter
docker compose down -v                 # arrêter et purger la base (pgdata)
```

### Option B — Installation native avec PostgreSQL

```bash
# 1. Environnement virtuel + dépendances
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Variables d'environnement
cp .env.example .env
#   → éditer .env (SECRET_KEY, mots de passe base de données)

# 3. Créer la base et l'utilisateur PostgreSQL
sudo -u postgres psql -c "CREATE USER groupe_scolaire WITH PASSWORD 'votre_mot_de_passe';"
sudo -u postgres psql -c "CREATE DATABASE groupes_scolaires OWNER groupe_scolaire;"

# 4. Migrations + données de base (niveaux 1ère-9ème et matières)
python manage.py migrate
python manage.py seed

# 5. Compte administrateur
python manage.py createsuperuser

# 6. Lancer
python manage.py runserver
```

> Utilisateur avec `uv` : `uv venv .venv` puis `uv pip install -r requirements.txt`.

## Données de démonstration (optionnel)

```bash
python manage.py seed_demo
# Crée une année 2025-2026, des classes, 50 élèves, évaluations, paiements…
# Comptes : admin/admin123 (direction) · prof/prof123 (enseignant)
```

## Test de fumée

```bash
python manage.py shell -c "exec(open('smoke.py').read())"
```

## Structure du projet

```
config/           → paramètres (settings.py, urls.py)
apps/
  accounts/       → utilisateurs, rôles, gestion des comptes
  core/           → tableau de bord, permissions, seed, contexte global
  scolarite/      → années scolaires, niveaux 1-9, classes, matières, affectations
  enseignants/    → fiches enseignants
  eleves/         → élèves, parents/tuteurs, inscriptions
  notes/          → évaluations, notes, bulletins (services.py = logique de calcul)
  presences/      → appels et historique
  finance/        → frais, paiements, reste à payer
templates/        → gabarits (base, CRUD, documents imprimables)
```

## Commandes utiles

| Commande | Effet |
|---|---|
| `docker compose up -d --build` | Lance l'application (PostgreSQL 17 + Django) |
| `docker compose down` | Arrête les conteneurs |
| `docker compose down -v` | Arrête et supprime la base (données perdues) |
| `python manage.py seed` | Niveaux 1-9 + matières de base |
| `python manage.py seed_demo` | Jeu de données de démonstration |
| `python manage.py makemigrations` / `migrate` | Migrations |
| `python manage.py check` | Vérifications |
| `python manage.py collectstatic --noinput` | Assets (production) |

## Notes

- L'année scolaire « en cours » (`AnneeScolaire.en_cours`) sert de contexte par défaut ;
  toutes les données sont rattachées à une année pour conserver l'historique.
- L'interface utilise Bootstrap 5 (CDN) ; l'application fonctionne hors-ligne
  si les CDN sont bloqués (le CSS local `static/css/app.css` reste appliqué).
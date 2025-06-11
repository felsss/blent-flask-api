# Flask REST API

Développement d'une API REST E-commerce avec Python/Flask et SQLAlchemy

## Prérequis

- Python 3.8 ou supérieur
- Git
- pip (gestionnaire de paquets Python)

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/felsss/blent-flask-api.git
cd blent-flask-api
```

### 2. Créer un environnement virtuel Python

**Sur Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Sur Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Exécution

### Lancer l'API Flask en mode debug

```bash
flask --app app run --debug
```

L'API sera accessible à l'adresse : `http://localhost:5000`

## Documentation de l'API

### Accès à Swagger UI

Une fois l'API lancée, vous pouvez accéder à la documentation interactive de l'API via Swagger UI à l'adresse suivante :

```
http://localhost:5000/apidocs
```

## Tests

### Lancer les tests

Pour exécuter la suite de tests complète :

```bash
python tests.py
```

Lors de la première requête, l'API préparera des données de tests si nécessaire. Les requêtes de tests servent elles-mêmes à créer des données nécessaires à certains tests.
Aucun fichier de base de données SQLite n'est nécessaire au démarrage.

## Structure du projet

```
blent-flask-api/
├── app.py              # Point d'entrée de l'API
├── blueprints/         # Les différents modules de l'API
├── config.py           # Constantes de config
├── digimarket.db       # Schéma de la base de données au format sqlite
├── models.py           # Les modèles des différents objets (Utilisateurs, Produits, Commandes, Items de commande)
├── requirements.txt    # Dépendances Python
├── tests.py            # Tests unitaires
├── README.md           # Ce fichier
├── venv/               # Environnement virtuel (généré)
└── ...
```

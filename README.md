# Projet Django - Gestion des Notes

Plateforme de gestion de notes pour les étudiants avec interface AdminLTE.

## 🎨 Fonctionnalités

- **Dashboard AdminLTE** - Interface moderne et responsive
- **Gestion des étudiants** - Création, modification, suppression
- **Tableau des notes** - Vue d'ensemble avec filtres en cascade
- **Import/Export Excel** - Importez et exportez les notes facilement
- **Édition inline** - Modifiez les notes directement dans le tableau
- **Pagination** - Navigation fluide entre les pages
- **Authentification** - Système de login/logout sécurisé
- **Filtres cascadants** - Département → Filière → Niveau

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip
- virtualenv

### Setup

1. **Cloner le repo**
```bash
git clone https://github.com/ton-username/Projet-Django.git
cd "Projet Django"
```

2. **Créer et activer l'environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Migrations**
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser  # Créer un admin
```

5. **Lancer le serveur**
```bash
python manage.py runserver
```

Accès : http://localhost:8000

## 📁 Structure

```
backend/
├── manage.py
├── db.sqlite3
├── backend/          # Config Django
├── notes/            # App principale
│   ├── models.py     # Models (Etudiant, Note, UE, etc.)
│   ├── views.py      # Vues et APIs
│   ├── urls.py       # Routes
│   ├── templates/    # Templates HTML
│   ├── static/       # CSS, JS
│   └── tests.py      # Tests unitaires
└── static/           # Static files
```

## 🧪 Tests

```bash
cd backend
python manage.py test notes
```

## 🔍 APIs disponibles

- `GET /api/notes/` - Liste des notes (avec filtres)
- `POST /api/note/create/` - Créer une note
- `POST /api/note/<id>/update/` - Modifier une note
- `POST /api/notes/import/` - Importer Excel
- `GET /api/notes/export/` - Exporter Excel
- `GET /api/filieres/?departement=X` - Cascade filieres
- `GET /api/niveaux/?filiere=X` - Cascade niveaux

## 🎯 Technos

- **Backend** : Django 4+
- **Frontend** : Bootstrap 5.3, AdminLTE 4
- **Database** : SQLite (changeable)
- **API** : JSON REST
- **JS** : Vanilla ES6

## 📝 License

MIT

## 👤 Auteur

T4zor

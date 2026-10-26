# AJI TSTAJI

Application Python de recherche de stage/emploi et de suivi de candidatures, destinée aux étudiants à Marrakech.

## Objectif

Centraliser en une seule application :
- la découverte d'entreprises locales (secteur numérique) ;
- la génération d'un CV et d'une lettre de motivation ;
- le suivi des candidatures envoyées.

Voir `docs/objectif.md` pour le détail complet.

## Technologies (100% Python)

| Bibliothèque | Rôle |
|---|---|
| Tkinter / ttk | Interface graphique |
| Pandas | Manipulation des données |
| Matplotlib | Graphiques (page Analyse) |
| SQLite (`sqlite3`) | Profil et candidatures |
| Requests | Appels à l'API Google Places |
| openpyxl | Lecture/écriture Excel, génération du CV |
| Pillow | Images de l'interface |
| python-dotenv | Lecture des clés/API depuis `.env` |
| smtplib | Envoi d'email de confirmation |

Aucune dépendance web (pas de React, FastAPI, Node.js).

## Structure du projet

```
aji-tstaji-v2/
├── data/
│   ├── raw/          → données avant nettoyage (data_brute.xlsx)
│   ├── cleaned/       → données après nettoyage (data_nettoyee.xlsx, 16 colonnes)
│   ├── reports/        → rapport qualité, CV et lettres générés
│   └── aji_tstaji.db    → base SQLite (profil, candidatures)
├── src/
│   ├── data_collection/   → collecte via Google Places API
│   ├── data_cleaning/      → nettoyage des données
│   ├── database/            → base SQLite (fonctions profil/candidatures)
│   ├── analysis/              → analyses complémentaires
│   └── utils/                    → chargement des données, génération CV/lettre/email
├── app/
│   ├── main.py           → fenêtre principale, navigation
│   ├── theme.py           → couleurs, polices
│   ├── widgets.py          → composants réutilisables (boutons)
│   ├── assets/               → images (ex. hero.png)
│   └── pages/                → une page = un fichier
├── docs/objectif.md    → objectif détaillé du projet
├── .env                  → clés/API (jamais partagé)
├── .env.example           → variables attendues, sans valeurs
├── requirements.txt        → bibliothèques nécessaires
└── README.md                → ce fichier
```

## Installation

### 1. Créer et activer l'environnement virtuel

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Installer les bibliothèques

```powershell
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Copier `.env.example` en `.env`, puis renseigner :

```
GOOGLE_PLACES_API_KEY=ta_cle_google_places
SMTP_EMAIL=ton.adresse@gmail.com
SMTP_MOT_DE_PASSE=ton_mot_de_passe_application
SMTP_SERVEUR=smtp.gmail.com
SMTP_PORT=587
```

- `GOOGLE_PLACES_API_KEY` : nécessaire uniquement pour relancer une collecte (`src/data_collection/google_places.py`).
- Les variables `SMTP_*` sont nécessaires pour l'email de confirmation de candidature. Pour Gmail, utiliser un **mot de passe d'application** (pas le mot de passe
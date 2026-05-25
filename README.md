# Smart Kitchen

Smart Kitchen ist eine moderne Rezeptplattform mit einem SvelteKit-Frontend und einem FastAPI-Backend. Nutzer können sich registrieren, Rezepte erstellen, öffentliche oder private Rezepte verwalten und Rezepte bewerten.

## Technologie-Stack

- **Frontend:** SvelteKit, TypeScript, Tailwind-ähnliches UI-Design
- **Backend:** FastAPI, SQLAlchemy, JWT-Authentifizierung
- **Datenbank:** MySQL
- **Infrastruktur:** Docker Compose

## Features

- Benutzerregistrierung und Login
- JWT-basierte Authentifizierung
- Rezept-Erstellung mit Zutaten, Schritten, Kategorie, Tags und Sichtbarkeit
- Öffentliche Rezeptliste und einzelne Rezeptdetailseiten
- Bewertungssystem für Rezepte
- Eigene Rezepte verwalten

## Schnellstart

```bash
cp .env.example .env

# SECRET_KEY generieren und in .env einfügen
openssl rand -hex 32

# Container bauen und starten
docker compose up -d --build
```

Dann im Browser öffnen:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API-Dokumentation: `http://localhost:8000/docs`

## Umgebungsvariablen

Erstelle ` .env` basierend auf `.env.example` und passe die Werte an.

Wichtige Variablen:

- `MYSQL_ROOT_PASSWORD` – Root-Passwort für die MySQL-Datenbank
- `MYSQL_DATABASE` – Datenbankname
- `MYSQL_USER` – App-Benutzername
- `MYSQL_PASSWORD` – App-Passwort
- `DATABASE_URL` – Optional: vollständige DB-Verbindung
- `SECRET_KEY` – Schlüssel für JWT-Signaturen
- `ALGORITHM` – JWT-Algorithmus (standardmäßig `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` – Ablaufzeit des Tokens in Minuten

## Architektur

Die App besteht aus drei Kernkomponenten:

- `frontend/` – SvelteKit-UI, ruft API-Endpunkte auf
- `backend/` – FastAPI-Server, verarbeitet Authentifizierung und Rezeptlogik
- `db` – MySQL-Datenbank, speichert Nutzer, Rezepte, Zutaten, Schritte, Bewertungen und Tags

Siehe auch [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Projektstruktur

```text
Smart-Kitchen-main/
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── lib/api.ts
│   │   └── routes/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Testprotokoll

Für manuelle Prüfungen siehe [`TESTING.md`](TESTING.md).

## API-Übersicht

- `POST /auth/register` – Benutzer registrieren
- `POST /token` – Login und JWT erhalten
- `GET /my-profile` – eigenes Profil abrufen
- `POST /recipes` – Rezept anlegen
- `GET /recipes` – öffentliche Rezepte erhalten
- `GET /recipes/{id}` – Rezeptdetail
- `POST /recipes/{id}/ratings` – Rezept bewerten

## Betriebshinweise

- Das Frontend ruft das Backend unter `http://localhost:8000` auf.
- Der `SECRET_KEY` muss in `.env` gesetzt sein, damit JWT-Token funktionieren.
- Private Rezepte sind nur für den Ersteller sichtbar.

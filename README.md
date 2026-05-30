# Smart Kitchen

Smart Kitchen ist eine moderne Rezeptplattform mit einem SvelteKit-Frontend und einem FastAPI-Backend. Nutzer können sich registrieren, Rezepte erstellen, öffentliche und private Rezepte verwalten, Rezepte bewerten, Favoriten sammeln und eine Einkaufsliste nutzen.

## Technologie-Stack

- **Frontend:** SvelteKit, TypeScript
- **Backend:** FastAPI, SQLAlchemy, JWT-Authentifizierung
- **Datenbank:** MySQL
- **Infrastruktur:** Docker Compose

## Features

- Benutzerregistrierung und Login
- JWT-basierte Authentifizierung
- Rezept-Erstellung mit strukturierten Zutaten, Schritten, Kategorie, Tags, Bild-URL und Sichtbarkeit
- Öffentliche Rezeptliste und Detailseiten
- Eigene Rezepte ansehen, bearbeiten und löschen
- Rezeptbewertung und Favoriten
- Einkaufsliste mit manuellen Items und Rezeptimport

## Schnellstart

```bash
cp .env.example .env

# SECRET_KEY generieren und in .env einfügen
openssl rand -hex 32

# Docker-Container bauen und starten
docker compose up -d --build
```

Dann im Browser öffnen:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API-Dokumentation: `http://localhost:8000/docs`

## Umgebungsvariablen

Erstelle `.env` basierend auf `.env.example` und passe die Werte an.

Wichtige Variablen:

- `MYSQL_ROOT_PASSWORD` – Root-Passwort für die MySQL-Datenbank
- `MYSQL_DATABASE` – Datenbankname
- `MYSQL_USER` – App-Benutzername
- `MYSQL_PASSWORD` – App-Passwort
- `DATABASE_URL` – Optional: vollständige DB-Verbindung
- `SECRET_KEY` – Schlüssel für JWT-Signaturen
- `ALGORITHM` – JWT-Algorithmus (`HS256` ist im Code aktuell festgelegt)
- `ACCESS_TOKEN_EXPIRE_MINUTES` – Token-Lebensdauer (`480` Minuten ist im Code aktuell festgelegt)

## Architektur

Die App besteht aus drei Kernkomponenten:

- `frontend/` – SvelteKit-UI, die API-Aufrufe über `frontend/src/lib/api.ts` ausführt
- `backend/` – FastAPI-Server, der Authentifizierung, Rezeptlogik, Favoriten und Einkaufsliste bereitstellt
- `db` – MySQL-Datenbank, gespeichert über Docker und verbunden über `docker-compose.yml`

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
│   ├── Dockerfile
│   └── alembic/
├── frontend/
│   ├── src/
│   │   ├── lib/api.ts
│   │   └── routes/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── TESTING.md
```

## Testprotokoll

Für manuelle Prüfungen siehe [`TESTING.md`](TESTING.md).

## API-Übersicht

- `POST /auth/register` – Benutzer registrieren
- `POST /token` – Login und JWT erhalten
- `GET /my-profile` – eigenes Profil abrufen
- `POST /recipes` – Rezept anlegen
- `GET /recipes` – Rezepte auflisten und filtern
- `GET /recipes/{id}` – Rezeptdetail
- `PUT /recipes/{id}` – Rezept aktualisieren
- `DELETE /recipes/{id}` – Rezept löschen
- `POST /recipes/{id}/favorite` – Rezept favorisieren
- `DELETE /recipes/{id}/favorite` – Favorit entfernen
- `GET /recipes/favorites` – eigene Favoriten
- `GET /recipes/mine` – eigene Rezepte
- `POST /recipes/{id}/ratings` – Rezept bewerten
- `GET /shopping-list` – Einkaufsliste abrufen
- `POST /shopping-list/items` – manuelles Item hinzufügen
- `POST /shopping-list/from-recipe/{id}` – Zutaten aus Rezept übernehmen
- `PATCH /shopping-list/items/{id}` – Item ändern
- `DELETE /shopping-list/items/{id}` – Item löschen
- `DELETE /shopping-list/checked` – abgehakte Items löschen
- `DELETE /shopping-list` – komplette Einkaufsliste leeren

## Betriebshinweise

- Das Frontend kommuniziert mit dem Backend unter `http://localhost:8000`.
- `SECRET_KEY` muss in `.env` gesetzt sein.
- Private Rezepte sind nur für den Ersteller sichtbar.

# Projekt-Template – SvelteKit + FastAPI + MySQL

Startpunkt für euer Semester-4-Projekt. Enthält eine lauffähige Boilerplate mit:

- **Backend**: FastAPI + SQLAlchemy + MySQL + JWT-Authentifizierung (Argon2)
- **Frontend**: SvelteKit mit API-Hilfsfunktionen
- **Infrastruktur**: Docker Compose für alle Services

## Quickstart

```bash
# 1. .env aus Vorlage erstellen und Werte anpassen
cp .env.example .env

# 2. SECRET_KEY generieren (für JWT) – z.B. mit:
openssl rand -hex 32
# Den Output in die `.env`-Datei als `SECRET_KEY` eintragen.

# 3. Alle Services bauen und starten
docker compose up -d --build

# 4. Fertig!
#    Frontend:  http://localhost:5173
#    Backend:   http://localhost:8000
#    API-Docs:  http://localhost:8000/docs
```

## Projektstruktur

```
projekt-template/
├── backend/
│   ├── main.py          # FastAPI-App (Endpoints)
│   ├── auth.py          # JWT + Argon2 Passwort-Hashing
│   ├── database.py      # SQLAlchemy Engine + Session
│   ├── models.py        # ORM-Modelle (User + eure Tabellen)
│   ├── schemas.py       # Pydantic-Schemas (Request/Response)
│   ├── requirements.txt # Python-Abhängigkeiten
│   └── Dockerfile       # Bauanleitung für Backend-Container
├── frontend/
│   ├── src/
│   │   ├── lib/api.ts          # API-Hilfsfunktionen (login, fetch...)
│   │   └── routes/+page.svelte # Startseite
│   ├── package.json            # NodeJS-Abhängigkeiten
│   └── Dockerfile              # Bauanleitung für Frontend-Container
├── docker-compose.yml          # Orchestrierung aller Container
├── .env.example                # Vorlage für Umgebungsvariablen
└── .gitignore                  # Git-Ignore-Datei
```

## Wo anfangen?

1. **Backend erweitern**: Eigene Modelle in `backend/models.py` anlegen, Pydantic-Schemas für API in `backend/schemas.py` anpassen, Endpoints in `backend/main.py` anlegen. Testen mit Swagger UI (`http://localhost:8000/docs`)
2. **Frontend erweitern**: API-Aufrufe (Kommunikation Svelte <-> Backend) in `frontend/src/lib/api.ts`, UI in `frontend/src/routes/`
3. **Datenbank**: Tabellen werden beim Start automatisch angelegt (`Base.metadata.create_all`)

## Authentifizierung testen

Die Swagger UI unter `http://localhost:8000/docs` hat einen eingebauten **Authorize**-Button:

1. Benutzer anlegen: `POST /auth/register`
2. Einloggen: Authorize-Button klicken → username + password eingeben
3. Geschützte Endpoints wie `GET /my-profile` aufrufen
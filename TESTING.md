# Testprotokoll für Smart Kitchen

## Vorbereitung

1. `.env` aus `.env.example` erstellen.
2. `SECRET_KEY` generieren und in `.env` eintragen.
3. Docker-Container starten:

```bash
docker compose up -d --build
```

4. Browser öffnen:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API-Doku: `http://localhost:8000/docs`

---

## 1. Login / Registrierung

### 1.1 Registrierung

- Gehe zu `/auth/register`.
- Fülle Username, E-Mail und Passwort aus.
- Erwartet: Weiterleitung zur Login-Seite.

### 1.2 Login

- Gehe zu `/auth/login`.
- Melde dich mit dem gerade erstellten Nutzer an.
- Erwartet: Weiterleitung zur Startseite.
- Prüfe: `localStorage` enthält `token` und `username`.

---

## 2. Rezept erstellen

### 2.1 Neues Rezept

- Gehe zu `/recipes/new`.
- Fülle Titel, Kategorie, Beschreibung und mindestens eine Zutat sowie einen Schritt aus.
- Wähle `Öffentlich` oder `Privat`.
- Klicke `Rezept veröffentlichen →`.

### 2.2 Erwartetes Verhalten

- Bei Erfolg: Weiterleitung zu `/recipes`.
- Bei Fehler: Fehlermeldung im Formular.
- Prüfe: Öffentliches Rezept erscheint in der Rezeptliste.
- Prüfe: Privates Rezept erscheint nur für den Ersteller.

---

## 3. Rezeptliste prüfen

- Gehe zu `/recipes`.
- Erwartet: öffentliche Rezepte werden angezeigt.
- Klicke ein Rezept an, um zur Detailseite zu gelangen.
- Prüfe: Titel, Beschreibung, Zutaten, Schritte und Tags werden angezeigt.

---

## 4. Rezeptdetails und Bewertung

### 4.1 Detailseite

- Öffne `/recipes/{id}` für ein öffentliches Rezept.
- Erwartet: Detailansicht lädt ohne Fehler.
- Prüfe: Kategorie, Zeit, Bewertung und Tag-Liste.

### 4.2 Bewertung

- Klicke auf einen Stern.
- Erwartet: Bewertung wird gespeichert.
- Prüfe: Durchschnittsbewertung aktualisiert sich.

---

## 5. Backend-API testen

### 5.1 Authentifizierung

- `POST /auth/register` mit JSON `username`, `email`, `password`
- `POST /token` mit Formular-Daten `username`, `password`, `grant_type=password`
- Erwartet: gültiger JWT im Feld `access_token`

### 5.2 Rezept erstellen

- `POST /recipes` mit Authorization Header `Bearer <token>` und JSON:

```json
{
  "title": "Test Rezept",
  "description": "Testbeschreibung",
  "is_public": true,
  "ingredients": [{ "name": "Zutat 1" }],
  "steps": [{ "step_number": 1, "instruction": "Anleitung" }],
  "tags": ["schnell"]
}
```

- Erwartet: HTTP 201 und Rezeptdaten im Response.

### 5.3 Öffentliche Rezeptliste

- `GET /recipes`
- Erwartet: Liste öffentlicher Rezepte.

### 5.4 Einzelnes Rezept

- `GET /recipes/{id}`
- Erwartet: Rezeptdetails, sofern das Rezept öffentlich ist oder der Nutzer der Ersteller ist.

---

## 6. Fehlerfälle

- Prüfe ungültiges Login: falsches Passwort → `401`.
- Prüfe privaten Zugriff: `GET /recipes/{id}` für privates Rezept als Fremder → `403`.
- Prüfe Bewertung ohne Token → Weiterleitung zur Login-Seite oder Fehlermeldung.

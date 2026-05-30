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
- API-Dokumentation: `http://localhost:8000/docs`

> Hinweis: Beim Start wird automatisch ein Testnutzer `testuser` mit Passwort `test1234` angelegt, falls er noch nicht existiert.

---

## 1. Login / Registrierung

### 1.1 Registrierung

- Gehe zu `/auth/register`.
- Fülle Nutzername, E-Mail und Passwort aus.
- Erwartet: Erfolgreiche Registrierung und Hinweis zur Anmeldung.

### 1.2 Login

- Gehe zu `/auth/login`.
- Melde dich mit dem registrierten Nutzer an.
- Erwartet: Weiterleitung zur Rezeptliste.
- Prüfe: Der Token wird im `localStorage` gespeichert.

---

## 2. Rezept erstellen

### 2.1 Neues Rezept

- Gehe zu `/recipes/new`.
- Fülle Titel, Kategorie, Beschreibung und mindestens eine Zutat sowie einen Schritt aus.
- Wähle `Öffentlich` oder `Privat`.
- Optional: Füge Tags hinzu.
- Klicke auf `Rezept veröffentlichen`.

### 2.2 Erwartetes Verhalten

- Bei Erfolg: Weiterleitung zur Rezeptliste oder Detailseite.
- Bei Fehler: Fehlermeldung im Formular.
- Prüfe: Öffentliches Rezept erscheint in der öffentlichen Liste.
- Prüfe: Privates Rezept erscheint in der eigenen Rezeptübersicht (`/recipes/mine`).

---

## 3. Rezeptliste prüfen

- Gehe zu `/recipes`.
- Erwartet: öffentliche Rezepte werden angezeigt.
- Optional: Filtere nach Kategorie, Schwierigkeit oder Tag.
- Klicke ein Rezept an, um zur Detailseite zu gelangen.
- Prüfe: Titel, Beschreibung, Zutaten, Schritte, Tags, Schwierigkeit und Zubereitungszeit werden angezeigt.

---

## 4. Eigene Rezepte und Favoriten

### 4.1 Eigene Rezepte

- Gehe zu `/recipes/mine`.
- Erwartet: Liste aller eigenen Rezepte, inklusive privater Rezepte.
- Prüfe: Bearbeiten und Löschen ist möglich, wenn das Feature im Frontend verfügbar ist.

### 4.2 Favoriten

- Favorisiere ein öffentliches Rezept.
- Erwartet: das Rezept erscheint in der Favoritenliste.
- Entferne ein Favorit wieder.
- Prüfe: `GET /recipes/favorites` liefert die korrekte Liste.

---

## 5. Rezeptdetails und Bewertung

### 5.1 Detailseite

- Öffne `/recipes/{id}` für ein öffentliches Rezept.
- Erwartet: Detailansicht lädt ohne Fehler.
- Prüfe: Kategorie, Zubereitungszeit, Bewertung und Tags werden angezeigt.

### 5.2 Bewertung

- Klicke auf einen Stern oder sende eine Bewertung ab.
- Erwartet: Bewertung wird gespeichert.
- Prüfe: Durchschnittsbewertung und Bewertungsanzahl aktualisieren sich.

---

## 6. Einkaufsliste

### 6.1 Manuelles Item hinzufügen

- Gehe zu `/shopping-list`.
- Füge ein Item mit Name, Menge und Einheit hinzu.
- Erwartet: Item wird in der Liste angezeigt.

### 6.2 Item bearbeiten

- Markiere ein Item als erledigt.
- Ändere Menge oder Einheit.
- Erwartet: Aktualisierte Werte erscheinen korrekt.

### 6.3 Rezeptzutaten übernehmen

- Wähle ein Rezept aus und übernehme die Zutaten.
- Optional: Skaliere die Mengen (z. B. `2.0` für doppelte Portion).
- Prüfe: hinzugefügte Zutaten erscheinen in der Einkaufsliste.

### 6.4 Liste aufräumen

- Lösche ein einzelnes Item.
- Lösche alle abgehakte Items.
- Lösche die gesamte Einkaufsliste.

---

## 7. Backend-API testen

### 7.1 Authentifizierung

- `POST /auth/register` mit JSON `username`, `email`, `password`
- `POST /token` mit Formular-Daten `username`, `password`, `grant_type=password`
- Erwartet: gültiger JWT im Feld `access_token`

### 7.2 Profil abrufen

- `GET /my-profile` mit Authorization Header `Bearer <token>`.
- Erwartet: Nutzerinformationen im Response.

### 7.3 Rezept erstellen

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

### 7.4 Öffentliche Rezeptliste und Filter

- `GET /recipes`
- Optional: `?q=`, `?category=`, `?tag=`, `?difficulty=`, `?max_time=`.
- Erwartet: Liste von Rezepten.

### 7.5 Einzelnes Rezept

- `GET /recipes/{id}`
- Erwartet: Rezeptdetails, sofern das Rezept öffentlich ist oder der Nutzer der Ersteller ist.

### 7.6 Lieblingsrezepte

- `POST /recipes/{id}/favorite` – Rezept favorisieren.
- `DELETE /recipes/{id}/favorite` – Favorit entfernen.
- `GET /recipes/favorites` – Liste der eigenen Favoriten.

### 7.7 Bewertung

- `POST /recipes/{id}/ratings` mit JSON `{ "recipe_id": <id>, "rating": 4 }`.
- Erwartet: HTTP 201 und Bewertungsdaten.

### 7.8 Einkaufsliste

- `GET /shopping-list`
- `POST /shopping-list/items` mit JSON `{ "name": "Milch", "amount": 1, "unit": "L" }`
- `POST /shopping-list/from-recipe/{id}` mit JSON `{ "scale": 1.0 }`
- `PATCH /shopping-list/items/{id}` zum Aktualisieren
- `DELETE /shopping-list/items/{id}` zum Löschen
- `DELETE /shopping-list/checked` zum Entfernen abgehakter Items
- `DELETE /shopping-list` zum Leeren der Liste

---

## 8. Fehlerfälle

- Ungültiges Login: falsches Passwort → `401`.
- Privates Rezept abfragen als Fremder → `403`.
- Rezept bewerten ohne Token → `401`.
- Favoriten-Operationen ohne Token → `401`.

---

## 9. Gesundheit prüfen

- `GET /health` sollte `{ "status": "ok" }` zurückgeben.

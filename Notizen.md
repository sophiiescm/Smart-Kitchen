# Dokumentation & Erläuterung: backend/models.py

Dieses Dokument dröselt unsere finale Datenbankstruktur (implementiert mittels SQLAlchemy ORM) Zeile für Zeile auf. Es dokumentiert die Evolution von der ersten rohen Test-Struktur (Phase 1) hin zum ausformulierten, reduzierten MVP-Schema (Phase 2), das exakt auf das vom Frontend-Team ausgearbeitete Layout angepasst wurde.

---

```python
from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Float, DateTime, Table, BigInteger, Integer
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Das Fundament für alle Tabellenklassen
Base = declarative_base()
```
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Die Imports:** * Aus dem Kern von `sqlalchemy` importieren wir die Bausteine für unsere Tabellen-Spalten: `Column` (definiert, dass hier eine Spalte hinkommt), `Integer` (für Ganzzahlen wie Mengen oder Schritte), `String` (für kürzere Texte wie Benutzernamen), `Text` (für sehr lange Texte wie Beschreibungen) und `ForeignKey` (der Fremdschlüssel für die Tabellen-Verknüpfung).
* **Neu dazugekommen für das reduzierten Schema:** `Boolean` (für Ja/Nein-Werte wie "Ist das Rezept öffentlich?"), `Float` (für Kommazahlen bei den Zutaten wie 1.5 Liter), `DateTime` (für Zeitstempel), `Table` (für die Verknüpfungstabelle der Gruppen) und `BigInteger` (für extrem große ID-Zahlen, was der Standard bei modernen PostgreSQL-Datenbanken ist).
* Aus `datetime` importieren wir das Python-eigene `datetime`, damit die Datenbank automatisch mitschreiben kann, an welchem Tag und zu welcher Uhrzeit ein Rezept erstellt wurde.
* Aus `sqlalchemy.orm` (dem Object-Relational-Mapping-Teil) importieren wir `declarative_base` und `relationship`.

**Base = declarative_base():**
* Das ist der absolute Startpunkt für SQLAlchemy. Diese Funktion erstellt eine Basisklasse (`Base`). Jede Python-Klasse, die wir gleich schreiben, "erbt" von dieser Basisklasse (erkennbar an dem `(Base)` hinter dem Klassennamen). 
* Dadurch weiß SQLAlchemy: *"Aha, diese Klasse ist nicht einfach irgendein Python-Code, sondern sie soll eine echte Tabelle in der Datenbank werden!"*
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```python
# Hilfskonstrukt: group_recipes (Die Brücke zwischen Rezepten und Gruppen)
group_recipes = Table(
    'group_recipes', Base.metadata,
    Column('group_id', BigInteger, ForeignKey('groups.id'), primary_key=True),
    Column('recipe_id', BigInteger, ForeignKey('recipes.id'), primary_key=True)
)
```
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**group_recipes:**
* Das ist eine Besonderheit: Es ist keine eigene Klasse, sondern ein direktes `Table`-Objekt. Wir brauchen das für eine sogenannte **Many-to-Many (N:M) Beziehung**. 
* **Die Logik dahinter:** Ein Rezept kann in vielen verschiedenen Kochgruppen/Sammlungen landen, und eine Kochgruppe hat natürlich viele verschiedene Rezepte. 
* Diese Tabelle ist die reine "Brücke". Sie speichert einfach nur stumpf paarweise ab, welche `group_id` mit welcher `recipe_id` verheiratet ist. Beide Spalten zusammen bilden den Primärschlüssel, damit kein Rezept doppelt in derselben Gruppe landen kann.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Beziehungen (Relationships) zu Rezepten, Bewertungen und Gruppen
    recipes = relationship("Recipe", back_populates="owner")
    ratings = relationship("RecipeRating", back_populates="user")
    owned_groups = relationship("Group", back_populates="owner")
```
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**__tablename__ = "users":** Sagt der Datenbank exakt, wie die Tabelle im Hintergrund heißen soll.

**id:** Jedes Datenbank-Modell braucht zwingend einen eindeutigen Schlüssel (`primary_key=True`), um Zeilen eindeutig zu identifizieren. `BigInteger` sorgt dafür, dass uns niemals die IDs ausgehen. `index=True` sorgt dafür, dass die Datenbank nach IDs rasend schnell suchen kann.

**username & email:** Die Profildaten des Benutzers. `email` hat ein `unique=True`, damit sich niemand mit derselben E-Mail-Adresse doppelt registrieren kann. `nullable=False` bedeutet: Das sind absolute Pflichtfelder, die niemals leer sein dürfen. Zusätzliche Felder (wie Biografie oder Avatare) wurden gestrichen, um Schnittstellen-Overhead einzusparen.

**password_hash:** Hier reservierst du den Platz für Person 2 (Security-Experte). Da Passwörter niemals im Klartext, sondern verschlüsselt als langer "Hash" gespeichert werden, nutzen wir ein stabiles String-Feld, um genug Platz für das verschlüsselte Passwort zu haben.

**recipes, ratings & owned_groups:** Das sind keine echten Spalten in der SQL-Tabelle! Das sind rein virtuelle Verbindungen für Python (`relationship`). Sie sagen SQLAlchemy: *"Wenn ich einen User abrufe, lade mir über .recipes automatisch alle Rezepte mit, die dieser User je erstellt hat, alle seine abgegebenen Sterne sowie seine erstellten Kochgruppen."* Das Gegenstück dazu definieren wir gleich in den anderen Klassen via `back_populates`.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```python
class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    prep_time_minutes = Column(Integer)
    servings = Column(Integer)
    difficulty = Column(String)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Die Python-Verbindungen (Relationships)
    owner = relationship("User", back_populates="recipes")
    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    steps = relationship("RecipeStep", back_populates="recipe")
    ratings = relationship("RecipeRating", back_populates="recipe")
```
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**title, description, prep_time_minutes, servings, difficulty:** Das sind die Kerndaten eines Rezepts, die vom Frontend-Team im reduzierten Schema gewünscht wurden. Der Titel darf nicht leer sein. Die Zubereitungszeit (`prep_time_minutes`) und die Portionen (`servings`) sind einfache Zahlen, perfekt für die UI-Icons im Frontend (z.B. eine kleine Uhr oder ein Teller-Symbol). `difficulty` speichert Texte wie "Einfach" oder "Schwer". Kalorien oder Rezeptbilder wurden im Sinne des 1-Wochen-Fahrplans gestrichen.

**is_public:** Ein Ja/Nein-Feld (`Boolean`). Standardmäßig steht es auf `False` (privat). Wenn der User es anklickt, wird es auf `True` gesetzt und ist für alle in der App sichtbar.

**created_at:** Nutzt `default=datetime.utcnow`. Das bedeutet: Wenn ein Rezept gespeichert wird, trägt Python dort vollautomatisch das aktuelle Datum und die Uhrzeit ein, ohne dass das Frontend irgendwas mitsenden muss.

**user_id & owner:** `user_id` ist der technische Fremdschlüssel (`ForeignKey`). Er kettet das Rezept an den User, der es erstellt hat. `owner` ist die Python-Verbindung: Schreibst du später im Code `recipe.owner.username`, spuckt er dir sofort den Namen des Kochs aus.

**ingredients, steps & ratings:** Verbindet das Rezept virtuell mit seinen Zutatenlisten, den einzelnen Zubereitungsschritten und den Sternen, die andere User dafür abgegeben haben. Im Vergleich zum allerersten Test-Entwurf sind Zutaten und Schritte hier sauber in eigene Tabellen ausgelagert.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```python
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    
    id = Column(BigInteger, primary_key=True, index=True)
    recipe_id = Column(BigInteger, ForeignKey("recipes.id"))
    name = Column(String, nullable=False) 
    amount = Column(Float)
    unit = Column(String)

    recipe = relationship("Recipe", back_populates="ingredients")
```
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**name, amount, unit:** Um das Rezept sauber zu strukturieren, wurde die Zutatenliste aus dem Rezept-Hauptmodell in diese Tabelle ausgelagert. `name` speichert die Zutat (z.B. "Mehl"), `amount` ist eine Kommazahl (`Float`, z.B. "1.5") und `unit` speichert die Maßeinheit als Text (z.B. "Gramm"). Dadurch kann das Frontend später Portionen mathematisch hochrechnen, was mit einem reinen Freitextfeld unmöglich wäre.

**recipe_id & recipe:** Jede Zutat muss natürlich wissen, zu welchem Rezept sie gehört. Wenn ein Rezept gelöscht wird, weiß die Datenbank über den Fremdschlüssel `ForeignKey("recipes.id")` genau, welche Zutaten ebenfalls mitgelöscht werden müssen.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```python
class RecipeStep(Base):
    __tablename__ = "recipe_steps"
    
    id = Column(BigInteger, primary_key=True, index=True)
    recipe_id = Column(BigInteger, ForeignKey("recipes.id"))
    step_number = Column(Integer)
    instruction = Column(Text, nullable=False)

    recipe = relationship("Recipe", back_populates="steps")
```
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**step_number & instruction:** Für die Kochanleitung. `step_number` sorgt für die richtige Reihenfolge (Schritt 1, Schritt 2, Schritt 3). `instruction` ist ein langes Textfeld für die eigentliche Erklärung (z.B. *"Den Ofen auf 180°C vorheizen."*). Laut dem reduzierten Schema wurden Timer-Sekunden und Bilder für Einzelschritte gestrichen.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```python
class RecipeRating(Base):
    __tablename__ = "recipe_ratings"
    
    id = Column(BigInteger, primary_key=True, index=True)
    recipe_id = Column(BigInteger, ForeignKey("recipes.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    rating = Column(Integer, nullable=False)

    recipe = relationship("Recipe", back_populates="ratings")
    user = relationship("User", back_populates="ratings")
```
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**rating:** Eine einfache Ganzzahl-Spalte (`Integer`) für die Bewertung von 1 bis 5 Sternen. Textkommentare wurden gestrichen. Es wird nur der reine Zahlenwert gespeichert, was die Aggregation (Berechnung der Durchschnittsbewertung eines Rezepts) massiv vereinfacht.

**recipe_id & user_id:** Diese Tabelle verbindet zwei Welten. Sie braucht die ID des Users, der bewertet, und die ID des Rezepts, das bewertet wird. Das ist eine klassische Zuordnungstabelle im relationalen Datenbankdesign.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```python
class Group(Base):
    __tablename__ = "groups"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(BigInteger, ForeignKey("users.id"))

    owner = relationship("User", back_populates="owned_groups")
    recipes = relationship("Recipe", secondary=group_recipes)
```
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**name & owner_id:** Da im Frontend-Layout die Route `/groups` existiert, wurde ein radikal vereinfachtes Gruppenkonzept eingebaut. Eine Gruppe ist hierbei eine simple "Rezeptsammlung" (z.B. *"Familien-Rezepte"* oder *"Wochenend-Auswahl"*). Sie hat einen Namen und gehört einem Besitzer (`owner_id`).

**recipes = relationship(..., secondary=group_recipes):** Hier schließt sich der Kreis zur Brücken-Tabelle ganz oben! Das `secondary=group_recipes` sagt SQLAlchemy: *"Wenn ich die Rezepte einer Gruppe abrufe, schau in der Tabelle group_recipes nach, welche IDs dort verknüpft sind, und liefere mir die passenden Rezepte aus."*
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


### Wichtige Architektur-Konzepte & Theorie (Hintergrundwissen für das Team & die Abgabe)

1. **Was ist ein ORM (Object-Relational Mapping)?**
   * *Theorie:* SQL-Datenbanken arbeiten in zweidimensionalen Tabellen (Zeilen und Spalten). Python arbeitet objektorientiert (mit Klassen und Objekten). Diese beiden Welten passen nativ nicht zusammen.
   * *Die Lösung:* SQLAlchemy ist unser ORM. Es agiert als automatischer Übersetzer. Wir schreiben sauberen Python-Code (unsere Klassen), und das ORM übersetzt diesen Code im Hintergrund in die passenden SQL-Befehle (`CREATE TABLE ...`), um die Tabellen in der PostgreSQL-Datenbank anzulegen.

2. **Was bedeutet Base.metadata.create_all?**
   * *Theorie:* Das ist der "Zündschlüssel" für unsere Datenbankstruktur.
   * *Die Lösung:* Wenn unser Backend über Docker startet, wird dieser Befehl ausgeführt. SQLAlchemy scannt dann alle Klassen, die von unserer `Base` geerbt haben (`User`, `Recipe`, `RecipeIngredient` etc.), verbindet sich mit der Datenbank und schaut nach, ob diese Tabellen schon da sind. Wenn nicht, erstellt es sie in diesem exakten Moment vollautomatisch.

3. **Der Unterschied zwischen Foreign Key und Relationship**
   * *Foreign Key (Fremdschlüssel):* Das ist die rein technische Ebene in der SQL-Datenbank. Es ist eine Spalte, die stumpf eine Zahl speichert (z.B. `user_id = 3`). Sie sorgt in der Datenbank für "Referenzielle Integrität" – das heißt, man kann kein Rezept für einen User anlegen, den es in der Realität gar nicht gibt.
   * *Relationship (Beziehung):* Das ist der reine Komfort-Weg auf der Python-Ebene. Es ist keine echte Spalte in der Datenbank. Es erlaubt uns Programmierern, im Code einfach mit Punkten durch die Daten zu wandern (z.B. `recipe.owner.username` oder `group.recipes`), ohne dass wir komplizierte SQL-JOIN-Befehle schreiben müssen.
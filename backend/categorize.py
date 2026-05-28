"""Supermarkt-Abteilungs-Mapping für Einkaufslisten-Items.

Pragmatisches Keyword-Matching: wir prüfen ob ein Stichwort als Teilstring
im Zutatennamen vorkommt. Das ist robuster als exaktes Matching ("Tomaten"
matched dann auch "Cherry-Tomaten") und für deutsche Lebensmittel-Begriffe
gut genug. Wer's perfekt will, kann später auf ML oder eine API umsteigen.

Reihenfolge: spezifischer vor allgemein. "Tomatensauce" matched zuerst
"Konserven & Saucen" (über das Stichwort "sauce"), nicht "Obst & Gemüse".
"""
from __future__ import annotations

# Reihenfolge der Kategorien ist wichtig — die erste, die matched, gewinnt.
CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    (
        "Backwaren & Backzutaten",
        [
            "mehl", "zucker", "hefe", "backpulver", "vanillezucker",
            "vanille", "kakao", "schokolade", "stärke", "brot",
            "brötchen", "toast", "haferflocken", "puddingpulver",
        ],
    ),
    (
        "Milchprodukte & Eier",
        [
            "milch", "joghurt", "quark", "frischkäse", "käse",
            "sahne", "schmand", "butter", "margarine", "ei", "eier",
            "kefir", "mascarpone", "ricotta", "mozzarella", "parmesan",
        ],
    ),
    (
        "Fleisch & Fisch",
        [
            "hack", "rind", "rinder", "schwein", "schweine", "huhn",
            "hähnchen", "pute", "puten", "speck", "wurst", "salami",
            "schinken", "bacon", "kotelett", "steak", "filet",
            "fisch", "lachs", "thunfisch", "shrimps", "garnelen",
            "tofu", "seitan",
        ],
    ),
    (
        "Konserven & Saucen",
        [
            "konserve", "dose", "passierte tomaten", "tomatensauce",
            "sauce", "ketchup", "mayonnaise", "senf", "essig",
            "öl", "ol ", "olivenöl", "rapsöl", "sonnenblumenöl",
            "brühe", "fond", "bouillon", "sojasauce", "soja-sauce",
        ],
    ),
    (
        "Tiefkühl",
        ["tk-", "tiefkühl", "tiefgefroren", "gefroren", "eis"],
    ),
    (
        "Getränke",
        [
            "wasser", "saft", "limonade", "cola", "bier", "wein",
            "sekt", "kaffee", "tee", "milch ", "smoothie",
        ],
    ),
    (
        "Gewürze & Kräuter",
        [
            "salz", "pfeffer", "paprika", "curry", "kümmel", "muskat",
            "zimt", "oregano", "basilikum", "thymian", "rosmarin",
            "petersilie", "schnittlauch", "dill", "lorbeer", "ingwer",
            "knoblauch", "chili", "kurkuma", "gewürz",
        ],
    ),
    (
        "Nudeln, Reis & Getreide",
        [
            "nudel", "spaghetti", "pasta", "penne", "fusilli", "tagliatelle",
            "lasagne", "reis", "couscous", "bulgur", "quinoa", "linsen",
            "bohnen", "kichererbsen", "haferflocken",
        ],
    ),
    (
        "Obst & Gemüse",
        [
            # Gemüse
            "tomate", "gurke", "salat", "kartoffel", "möhre", "karotte",
            "zwiebel", "knoblauch", "paprika", "zucchini", "aubergine",
            "brokkoli", "blumenkohl", "spinat", "lauch", "fenchel",
            "kohl", "spargel", "pilz", "champignon", "rucola",
            "avocado", "mais",
            # Obst
            "apfel", "äpfel", "banane", "orange", "zitrone", "limette",
            "beere", "erdbeer", "himbeer", "blaubeer", "trauben",
            "kirsche", "pfirsich", "melone", "ananas", "kiwi", "mango",
        ],
    ),
    (
        "Süßes & Snacks",
        ["bonbon", "schokoriegel", "chips", "kekse", "keks", "gummi"],
    ),
    (
        "Haushalt & Drogerie",
        [
            "spülmittel", "küchenrolle", "klopapier", "toilettenpapier",
            "waschmittel", "müllbeutel", "alufolie", "frischhaltefolie",
            "shampoo", "duschgel", "zahnpasta",
        ],
    ),
]

DEFAULT_CATEGORY = "Sonstiges"


def categorize_ingredient(name: str) -> str:
    """Gibt die Supermarkt-Abteilung für einen Zutatennamen zurück.

    Beispiele:
        >>> categorize_ingredient("Mehl Type 405")
        'Backwaren & Backzutaten'
        >>> categorize_ingredient("Cherrytomaten")
        'Obst & Gemüse'
        >>> categorize_ingredient("Spülmittel")
        'Haushalt & Drogerie'
        >>> categorize_ingredient("Einhornpulver")  # nicht gemappt
        'Sonstiges'
    """
    if not name:
        return DEFAULT_CATEGORY
    lowered = name.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in lowered:
                return category
    return DEFAULT_CATEGORY

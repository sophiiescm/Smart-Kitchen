<script lang="ts">
  // Später kommen echte Daten vom Backend.
  // Fürs Erste arbeiten wir mit Platzhalterdaten ("Mock-Daten"),
  // damit wir das Design sehen und testen können.

  // Das ist ein TypeScript-Typ — beschreibt wie ein Rezept aussieht
  type Recipe = {
    id: number;
    title: string;
    description: string;
    category: string;
    rating: number;
    ratingCount: number;
    author: string;
    timeMinutes: number;
    emoji: string;
  };

  // Platzhalterdaten
  const recipes: Recipe[] = [
    {
      id: 1,
      title: 'Spaghetti Carbonara',
      description: 'Cremige Pasta mit knusprigem Speck, Ei und Parmesan — ein italienischer Klassiker.',
      category: 'Pasta',
      rating: 4.8,
      ratingCount: 124,
      author: 'Maria K.',
      timeMinutes: 25,
      emoji: '🍝',
    },
    {
      id: 2,
      title: 'Avocado Toast',
      description: 'Knuspriges Sauerteigbrot mit cremiger Avocado, Chili und Limette.',
      category: 'Frühstück',
      rating: 4.5,
      ratingCount: 87,
      author: 'Jonas M.',
      timeMinutes: 10,
      emoji: '🥑',
    },
    {
      id: 3,
      title: 'Kürbissuppe',
      description: 'Samtiger Hokkaido-Kürbis mit Ingwer und Kokosmilch, perfekt für den Herbst.',
      category: 'Suppe',
      rating: 4.7,
      ratingCount: 63,
      author: 'Sara L.',
      timeMinutes: 40,
      emoji: '🎃',
    },
    {
      id: 4,
      title: 'Schokoladenkuchen',
      description: 'Saftig, dunkel, intensiv. Mit flüssigem Kern und Vanilleeis servieren.',
      category: 'Dessert',
      rating: 4.9,
      ratingCount: 201,
      author: 'Tom R.',
      timeMinutes: 55,
      emoji: '🍫',
    },
    {
      id: 5,
      title: 'Caesar Salad',
      description: 'Knackiger Römersalat mit hausgemachtem Dressing, Croutons und Parmesan.',
      category: 'Salat',
      rating: 4.3,
      ratingCount: 45,
      author: 'Lena W.',
      timeMinutes: 20,
      emoji: '🥗',
    },
    {
      id: 6,
      title: 'Shakshuka',
      description: 'Eier in würziger Tomatensauce mit Paprika und Feta — nahöstlicher Klassiker.',
      category: 'Frühstück',
      rating: 4.6,
      ratingCount: 92,
      author: 'Ali H.',
      timeMinutes: 30,
      emoji: '🍳',
    },
  ];

  // Kategorien für den Filter
  const categories = ['Alle', 'Pasta', 'Frühstück', 'Suppe', 'Dessert', 'Salat'];

  // Welche Kategorie ist gerade ausgewählt?
  let selectedCategory = $state('Alle');

  // Suchbegriff
  let searchTerm = $state('');

  // Gefilterte Rezepte (berechnet sich automatisch neu)
  let filteredRecipes = $derived(
    recipes.filter((r) => {
      const matchesCategory = selectedCategory === 'Alle' || r.category === selectedCategory;
      const matchesSearch =
        searchTerm === '' ||
        r.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.description.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesCategory && matchesSearch;
    })
  );

  // Sterne anzeigen (z.B. 4.8 → "★★★★★")
  function renderStars(rating: number): string {
    const full = Math.round(rating);
    return '★'.repeat(full) + '☆'.repeat(5 - full);
  }
</script>

<!-- ═══════════════════════════════════════════ -->
<!--  HERO-BEREICH (oben auf der Startseite)    -->
<!-- ═══════════════════════════════════════════ -->
<section class="hero">
  <div class="hero-content">
    <h1>Kochen, teilen,<br /><em>genießen.</em></h1>
    <p class="hero-subtitle">
      Entdecke tausende Rezepte oder teile deine eigenen Kreationen mit der Community.
    </p>

    <!-- Suchleiste -->
    <div class="search-bar">
      <span class="search-icon">🔍</span>
      <input
        type="text"
        placeholder="Rezept suchen..."
        bind:value={searchTerm}
      />
    </div>
  </div>
</section>

<!-- ═══════════════════════════════════════════ -->
<!--  HAUPTBEREICH: Filter + Rezeptkarten       -->
<!-- ═══════════════════════════════════════════ -->
<section class="content">
  <div class="container">

    <!-- Kategoriefilter -->
    <div class="filters">
      {#each categories as cat}
        <button
          class="filter-btn"
          class:selected={selectedCategory === cat}
          onclick={() => selectedCategory = cat}
        >
          {cat}
        </button>
      {/each}
    </div>

    <!-- Ergebnisanzahl -->
    <p class="results-count">
      {filteredRecipes.length} Rezept{filteredRecipes.length !== 1 ? 'e' : ''} gefunden
    </p>

    <!-- Rezeptkarten-Raster -->
    {#if filteredRecipes.length > 0}
      <div class="recipes-grid">
        {#each filteredRecipes as recipe (recipe.id)}
          <a href="/recipes/{recipe.id}" class="recipe-card">
            <!-- Emoji als "Bild-Platzhalter" -->
            <div class="card-image">
              <span class="card-emoji">{recipe.emoji}</span>
              <span class="card-category">{recipe.category}</span>
            </div>

            <div class="card-body">
              <h2 class="card-title">{recipe.title}</h2>
              <p class="card-desc">{recipe.description}</p>

              <div class="card-meta">
                <span class="stars">{renderStars(recipe.rating)}</span>
                <span class="rating-num">{recipe.rating} ({recipe.ratingCount})</span>
              </div>

              <div class="card-footer">
                <span class="author">von {recipe.author}</span>
                <span class="time">⏱ {recipe.timeMinutes} Min.</span>
              </div>
            </div>
          </a>
        {/each}
      </div>
    {:else}
      <!-- Kein Ergebnis -->
      <div class="empty">
        <p>😕 Keine Rezepte gefunden.</p>
        <button onclick={() => { searchTerm = ''; selectedCategory = 'Alle'; }}>
          Filter zurücksetzen
        </button>
      </div>
    {/if}

  </div>
</section>

<style>
  /* ── Hero ── */
  .hero {
    background: linear-gradient(135deg, #fff8f6 0%, #faf9f6 60%, #f5f0e8 100%);
    padding: 5rem 2rem 4rem;
    text-align: center;
    border-bottom: 1px solid #e8e4db;
  }

  .hero-content {
    max-width: 640px;
    margin: 0 auto;
  }

  .hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 5vw, 3.6rem);
    line-height: 1.15;
    color: #1a1a1a;
    margin-bottom: 1rem;
  }

  .hero h1 em {
    font-style: italic;
    color: #c0392b;
  }

  .hero-subtitle {
    font-size: 1.05rem;
    color: #666;
    line-height: 1.6;
    margin-bottom: 2rem;
  }

  /* Suchleiste */
  .search-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: white;
    border: 1.5px solid #e8e4db;
    border-radius: 16px;
    padding: 0.75rem 1.25rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    transition: border-color 0.2s;
  }

  .search-bar:focus-within {
    border-color: #c0392b;
  }

  .search-icon {
    font-size: 1.1rem;
    flex-shrink: 0;
  }

  .search-bar input {
    border: none;
    outline: none;
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    width: 100%;
    background: transparent;
    color: #1a1a1a;
  }

  .search-bar input::placeholder {
    color: #bbb;
  }

  /* ── Content-Bereich ── */
  .content {
    padding: 3rem 2rem;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
  }

  /* ── Kategorie-Filter ── */
  .filters {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
  }

  .filter-btn {
    padding: 0.4rem 1.1rem;
    border-radius: 999px;
    border: 1.5px solid #e8e4db;
    background: white;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    color: #666;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .filter-btn:hover {
    border-color: #c0392b;
    color: #c0392b;
  }

  .filter-btn.selected {
    background: #c0392b;
    border-color: #c0392b;
    color: white;
  }

  .results-count {
    font-size: 0.875rem;
    color: #999;
    margin-bottom: 1.5rem;
  }

  /* ── Rezept-Karten-Raster ── */
  .recipes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .recipe-card {
    background: white;
    border-radius: 16px;
    border: 1px solid #e8e4db;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    flex-direction: column;
  }

  .recipe-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.1);
  }

  /* Karten-Bild (Emoji-Platzhalter) */
  .card-image {
    background: linear-gradient(135deg, #fff8f6, #fdf0ee);
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    border-bottom: 1px solid #f5ede8;
  }

  .card-emoji {
    font-size: 4rem;
  }

  .card-category {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    background: white;
    border: 1px solid #e8e4db;
    border-radius: 999px;
    padding: 0.2rem 0.65rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: #666;
  }

  /* Karten-Inhalt */
  .card-body {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    flex: 1;
  }

  .card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: #1a1a1a;
    line-height: 1.3;
  }

  .card-desc {
    font-size: 0.875rem;
    color: #777;
    line-height: 1.5;
    flex: 1;
  }

  .card-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.25rem;
  }

  .stars {
    color: #f0a500;
    font-size: 0.85rem;
    letter-spacing: -1px;
  }

  .rating-num {
    font-size: 0.8rem;
    color: #999;
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 0.75rem;
    border-top: 1px solid #f5f0e8;
    font-size: 0.8rem;
    color: #aaa;
  }

  /* ── Leerer Zustand ── */
  .empty {
    text-align: center;
    padding: 4rem 2rem;
    color: #aaa;
  }

  .empty p {
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }

  .empty button {
    padding: 0.5rem 1.5rem;
    border-radius: 8px;
    border: 1.5px solid #e8e4db;
    background: white;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    cursor: pointer;
    color: #666;
    transition: all 0.15s;
  }

  .empty button:hover {
    border-color: #c0392b;
    color: #c0392b;
  }
</style>

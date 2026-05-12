<script lang="ts">
  import { page } from '$app/stores';

  let { children } = $props();

  // Navigationspunkte
  const navLinks = [
    { href: '/', label: 'Startseite' },
    { href: '/recipes', label: 'Rezepte' },
    { href: '/recipes/new', label: '+ Rezept erstellen' },
  ];
</script>

<div class="app">
  <header>
    <nav>
      <a href="/" class="logo">
        <span class="logo-icon">🍳</span>
        <span class="logo-text">Kochbuch</span>
      </a>

      <ul class="nav-links">
        {#each navLinks as link}
          <li>
            <a
              href={link.href}
              class:active={$page.url.pathname === link.href}
              class:cta={link.label.startsWith('+')}
            >
              {link.label}
            </a>
          </li>
        {/each}
      </ul>

      <div class="nav-auth">
        <a href="/auth/login" class="btn-ghost">Anmelden</a>
        <a href="/auth/register" class="btn-primary">Registrieren</a>
      </div>
    </nav>
  </header>

  <main>
    {@render children()}
  </main>

  <footer>
    <p>© 2025 Kochbuch · Verteilte Systeme Projekt</p>
  </footer>
</div>

<style>
  /* ── Google Font laden ── */
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap');

  /* ── CSS Variablen (Farben, Abstände) ── */
  :global(*) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  :global(body) {
    font-family: 'DM Sans', sans-serif;
    background-color: #faf9f6;
    color: #1a1a1a;
    min-height: 100vh;
  }

  :global(a) {
    text-decoration: none;
    color: inherit;
  }

  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  /* ── Header / Navbar ── */
  header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(250, 249, 246, 0.92);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #e8e4db;
  }

  nav {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
    height: 64px;
    display: flex;
    align-items: center;
    gap: 2rem;
  }

  /* Logo */
  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: #1a1a1a;
    flex-shrink: 0;
  }

  .logo-icon {
    font-size: 1.6rem;
  }

  /* Navigationslinks */
  .nav-links {
    list-style: none;
    display: flex;
    gap: 0.25rem;
    flex: 1;
  }

  .nav-links a {
    padding: 0.4rem 0.9rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #555;
    transition: all 0.15s ease;
  }

  .nav-links a:hover {
    color: #1a1a1a;
    background: #f0ede6;
  }

  .nav-links a.active {
    color: #c0392b;
    background: #fdf0ee;
  }

  .nav-links a.cta {
    color: #c0392b;
    font-weight: 600;
  }

  /* Auth Buttons */
  .nav-auth {
    display: flex;
    gap: 0.75rem;
    flex-shrink: 0;
  }

  .btn-ghost {
    padding: 0.4rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #555;
    transition: all 0.15s ease;
  }

  .btn-ghost:hover {
    background: #f0ede6;
    color: #1a1a1a;
  }

  .btn-primary {
    padding: 0.4rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    background: #c0392b;
    color: white;
    transition: all 0.15s ease;
  }

  .btn-primary:hover {
    background: #a93226;
  }

  /* ── Main Content ── */
  main {
    flex: 1;
  }

  /* ── Footer ── */
  footer {
    text-align: center;
    padding: 2rem;
    font-size: 0.85rem;
    color: #999;
    border-top: 1px solid #e8e4db;
    margin-top: 4rem;
  }
</style>


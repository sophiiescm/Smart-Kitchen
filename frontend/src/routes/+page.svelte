<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    // In runes mode müssen reaktive Werte mit $state() deklariert werden,
    // sonst aktualisiert sich die UI nicht.
    let username = $state('Gast');
    let recipes = $state<any[]>([]);
    let loading = $state(true);
    let searchQuery = $state('');
    let isLoggedIn = $state(false);

    onMount(async () => {
        const storedUser = localStorage.getItem('username');
        const token = localStorage.getItem('token');
        if (storedUser && token) {
            username = storedUser;
            isLoggedIn = true;
        }

        try {
            // Token mitschicken, damit eigene private Rezepte auch im Dashboard erscheinen
            const token = localStorage.getItem('token');
            const headers: Record<string, string> = {};
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const res = await fetch('http://localhost:8000/recipes', { headers });
            if (res.ok) {
                recipes = await res.json();
            }
        } catch (error) {
            console.error('Fehler beim Laden der Rezepte:', error);
        } finally {
            loading = false;
        }
    });

    function handleLogout() {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        document.cookie = 'token=; Max-Age=0; path=/';
        goto('/auth/login');
    }

    function handleSearch() {
        const q = searchQuery.trim();
        if (q) {
            goto(`/recipes?q=${encodeURIComponent(q)}`);
        } else {
            goto('/recipes');
        }
    }
</script>

<div class="dashboard-container">
	<!-- Background -->
	<div class="background-blur blur-1"></div>
	<div class="background-blur blur-2"></div>

	<!-- Navigation -->
	<nav class="glass-nav">
		<div class="logo">
			Smart<span>Kitchen</span>
		</div>

		<div class="nav-actions">
			<a href="/recipes" class="nav-link">Alle Rezepte</a>

			{#if isLoggedIn}
				<a href="/shopping-list" class="nav-link">🛒 Einkaufsliste</a>
				<a href="/recipes/new" class="create-btn">
					+ Neues Rezept
				</a>
				<button class="logout-btn" onclick={handleLogout}>
					Abmelden
				</button>
			{:else}
				<a href="/auth/login" class="nav-link">Anmelden</a>
				<a href="/auth/register" class="create-btn">
					Registrieren
				</a>
			{/if}
		</div>
	</nav>

	<!-- Main -->
	<main class="content">
		<!-- Welcome -->
		<section class="hero">
			<div class="hero-content">
				<div class="badge">
					🍳 Community Rezepte
				</div>

				<h1>
					Hallo, <span>{username}</span>
				</h1>

				<p>
					Entdecke moderne Rezepte, teile deine Lieblingsgerichte und finde neue Inspiration.
				</p>
			</div>

			<div class="hero-stats">
				<div class="stat-card">
					<div class="stat-number">{recipes.length}</div>
					<div class="stat-label">Rezepte</div>
				</div>
			</div>
		</section>

		<!-- Search -->
		<div class="searchbar">
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Was möchtest du heute kochen?"
				onkeydown={(e) => { if (e.key === 'Enter') handleSearch(); }}
			/>

			<button onclick={handleSearch}>
				Suchen
			</button>
		</div>

		<!-- Recipes -->
		<section class="recipes-section">
			<div class="section-header">
				<div>
					<h2>Beliebte Rezepte</h2>
					<p>Die neuesten Gerichte aus der Community</p>
				</div>

				<a href="/recipes" class="see-all">
					Alle ansehen →
				</a>
			</div>

			{#if loading}
				<div class="empty-state">
					Lade Rezepte...
				</div>

			{:else if recipes.length === 0}
				<div class="empty-state">
					Noch keine Rezepte vorhanden.
				</div>

			{:else}
				<div class="recipes-grid">
					{#each recipes.slice(0, 6) as recipe}
						<a
							href={`/recipes/${recipe.id}`}
							class="recipe-card"
						>
							<div class="recipe-image">
								{#if recipe.image_url}
									<img src={recipe.image_url} alt={recipe.title} />
								{:else}
									<div class="img-placeholder">🍽️</div>
								{/if}
								<div class="image-overlay"></div>
								{#if recipe.category}
									<span class="category-badge">{recipe.category}</span>
								{/if}
							</div>

							<div class="recipe-content">
								<h3>{recipe.title}</h3>

								<p>{recipe.description ?? 'Keine Beschreibung verfügbar.'}</p>

								<div class="recipe-footer">
									<span>⏱ {recipe.prep_time_minutes ?? '–'} Min</span>
									<span class="open-link">Öffnen →</span>
								</div>
							</div>
						</a>
					{/each}
				</div>
			{/if}
		</section>
	</main>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
		background: #04070a;
		color: white;
	}

	.dashboard-container {
		position: relative;
		min-height: 100vh;
		overflow: hidden;
		background: #04070a;
	}

	.background-blur {
		position: fixed;
		border-radius: 9999px;
		filter: blur(120px);
		pointer-events: none;
		z-index: 0;
	}

	.blur-1 {
		top: -200px;
		left: -150px;
		width: 500px;
		height: 500px;
		background: rgba(34, 197, 94, 0.15);
	}

	.blur-2 {
		bottom: -200px;
		right: -150px;
		width: 500px;
		height: 500px;
		background: rgba(16, 185, 129, 0.12);
	}

	.glass-nav {
		position: sticky;
		top: 0;
		z-index: 100;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 24px 40px;
		background: rgba(0, 0, 0, 0.35);
		backdrop-filter: blur(18px);
		border-bottom: 1px solid rgba(255, 255, 255, 0.06);
	}

	.logo {
		font-size: 28px;
		font-weight: 900;
		letter-spacing: -1px;
	}

	.logo span {
		color: #22c55e;
	}

	.nav-actions {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.nav-link {
		padding: 12px 18px;
		border-radius: 16px;
		color: #cbd5e1;
		text-decoration: none;
		font-weight: 600;
		font-size: 14px;
		transition: 0.2s;
	}

	.nav-link:hover {
		color: white;
		background: rgba(255, 255, 255, 0.05);
	}

	.create-btn {
		padding: 12px 20px;
		border-radius: 16px;
		background: linear-gradient(to right, #16a34a, #065f46);
		color: white;
		font-weight: 600;
		text-decoration: none;
		transition: 0.3s;
		box-shadow: 0 10px 30px rgba(22, 163, 74, 0.3);
	}

	.create-btn:hover {
		transform: translateY(-2px);
	}

	.logout-btn {
		padding: 12px 18px;
		border-radius: 16px;
		background: rgba(255, 255, 255, 0.06);
		border: 1px solid rgba(255, 255, 255, 0.08);
		color: white;
		cursor: pointer;
		font-family: inherit;
		font-size: 14px;
		font-weight: 600;
		transition: 0.3s;
	}

	.logout-btn:hover {
		background: rgba(239, 68, 68, 0.15);
		border-color: rgba(239, 68, 68, 0.2);
	}

	/* CONTENT */
	.content {
		position: relative;
		z-index: 1;
		max-width: 1400px;
		margin: 0 auto;
		padding: 50px 32px 100px;
	}

	/* HERO */
	.hero {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 40px;
		margin-bottom: 50px;
		flex-wrap: wrap;
	}

	.hero-content {
		max-width: 700px;
	}

	.badge {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		padding: 10px 18px;
		border-radius: 999px;
		background: rgba(34, 197, 94, 0.1);
		color: #4ade80;
		font-size: 14px;
		font-weight: 600;
		margin-bottom: 24px;
	}

	.hero h1 {
		font-size: 72px;
		line-height: 0.95;
		font-weight: 900;
		margin: 0;
		letter-spacing: -3px;
	}

	.hero h1 span {
		background: linear-gradient(to right, #4ade80, #065f46);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
	}

	.hero p {
		margin-top: 24px;
		font-size: 20px;
		line-height: 1.7;
		color: #94a3b8;
		max-width: 600px;
	}

	.stat-card {
		padding: 40px;
		border-radius: 32px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.06);
		backdrop-filter: blur(20px);
		min-width: 220px;
		text-align: center;
	}

	.stat-number {
		font-size: 56px;
		font-weight: 900;
		color: #4ade80;
	}

	.stat-label {
		margin-top: 10px;
		color: #94a3b8;
	}

	/* SEARCH */
	.searchbar {
		display: flex;
		align-items: center;
		gap: 16px;
		margin-bottom: 60px;
		padding: 16px;
		border-radius: 32px;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		backdrop-filter: blur(18px);
	}

	.searchbar input {
		flex: 1;
		background: transparent;
		border: none;
		outline: none;
		font-size: 18px;
		color: white;
		padding: 10px 16px;
		font-family: inherit;
	}

	.searchbar input::placeholder {
		color: #64748b;
	}

	.searchbar button {
		border: none;
		padding: 16px 28px;
		border-radius: 20px;
		background: linear-gradient(to right, #16a34a, #065f46);
		color: white;
		font-weight: 700;
		cursor: pointer;
		transition: 0.3s;
		font-family: inherit;
	}

	.searchbar button:hover {
		transform: scale(1.02);
	}

	/* SECTION */
	.section-header {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		margin-bottom: 30px;
	}

	.section-header h2 {
		margin: 0;
		font-size: 38px;
		font-weight: 800;
	}

	.section-header p {
		margin-top: 10px;
		color: #64748b;
	}

	.see-all {
		color: #4ade80;
		text-decoration: none;
		font-weight: 600;
	}

	/* GRID */
	.recipes-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 24px;
	}

	.recipe-card {
		overflow: hidden;
		border-radius: 24px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.07);
		backdrop-filter: blur(20px);
		text-decoration: none;
		color: inherit;
		transition: 0.3s;
		display: flex;
		flex-direction: column;
	}

	.recipe-card:hover {
		transform: translateY(-6px);
		border-color: rgba(34, 197, 94, 0.25);
		box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
	}

	.recipe-image {
		position: relative;
		aspect-ratio: 16 / 10;
		overflow: hidden;
	}

	.recipe-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		transition: transform 0.5s;
	}

	.recipe-card:hover .recipe-image img {
		transform: scale(1.05);
	}

	.img-placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 60px;
		background: linear-gradient(135deg, rgba(34, 197, 94, 0.08), rgba(16, 185, 129, 0.05));
	}

	.image-overlay {
		position: absolute;
		inset: 0;
		background: linear-gradient(to top, rgba(0, 0, 0, 0.55), transparent 60%);
	}

	.category-badge {
		position: absolute;
		top: 14px;
		left: 14px;
		padding: 6px 12px;
		border-radius: 999px;
		background: rgba(0, 0, 0, 0.55);
		backdrop-filter: blur(8px);
		color: #4ade80;
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
	}

	.recipe-content {
		padding: 22px;
		display: flex;
		flex-direction: column;
		flex: 1;
		gap: 12px;
	}

	.recipe-content h3 {
		margin: 0;
		font-size: 20px;
		font-weight: 800;
		line-height: 1.3;
	}

	.recipe-content p {
		margin: 0;
		line-height: 1.55;
		color: #94a3b8;
		font-size: 14px;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.recipe-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 12px;
		margin-top: auto;
		border-top: 1px solid rgba(255, 255, 255, 0.06);
		font-size: 13px;
		color: #94a3b8;
	}

	.open-link {
		color: #4ade80;
		font-weight: 700;
	}

	/* EMPTY */
	.empty-state {
		padding: 60px;
		text-align: center;
		border-radius: 24px;
		background: rgba(255, 255, 255, 0.03);
		border: 1px solid rgba(255, 255, 255, 0.05);
		color: #64748b;
	}

	/* MOBILE */
	@media (max-width: 900px) {
		.glass-nav {
			padding: 20px;
		}

		.content {
			padding: 32px 20px 100px;
		}

		.hero {
			flex-direction: column;
			align-items: flex-start;
		}

		.hero h1 {
			font-size: 44px;
		}

		.recipes-grid {
			grid-template-columns: 1fr;
		}

		.searchbar {
			flex-direction: column;
		}

		.searchbar button {
			width: 100%;
		}

		.section-header h2 {
			font-size: 28px;
		}
	}
</style>

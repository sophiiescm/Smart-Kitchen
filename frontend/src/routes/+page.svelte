<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    // Variablen für das Dashboard
    let username = 'Gast';
    let recipes: any[] = [];
    let loading = true;

    onMount(async () => {
        // 1. Prüfen, ob der User eingeloggt ist (Name aus dem localStorage holen)
        const storedUser = localStorage.getItem('username');
        if (storedUser) {
            username = storedUser;
        }

        // 2. Rezepte vom FastAPI-Backend abrufen
        try {
            const res = await fetch('http://localhost:8000/recipes');
            if (res.ok) {
                recipes = await res.json();
            }
        } catch (error) {
            console.error('Fehler beim Laden der Rezepte:', error);
        } finally {
            loading = false;
        }
    });

    // Abmelde-Funktion für den Logout-Button unten
    function handleLogout() {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        goto('/auth/login');
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
			<a href="/recipes/new" class="create-btn">
				+ Neues Rezept
			</a>

			<button class="logout-btn" onclick={handleLogout}>
				Abmelden
			</button>
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
					<div class="stat-number">
						{recipes.length}
					</div>

					<div class="stat-label">
						Rezepte
					</div>
				</div>
			</div>
		</section>

		<!-- Search -->
		<div class="searchbar">
			<input
				type="text"
				placeholder="Was möchtest du heute kochen?"
			/>

			<button>
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

				<a href="/recipes">
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
					{#each recipes as recipe}
						<a
							href={`/recipes/${recipe.id}`}
							class="recipe-card"
						>
							<div class="recipe-image">
								<img
									src={recipe.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=1200'}
									alt={recipe.title}
								/>
								<div class="image-overlay"></div>
							</div>

							<div class="recipe-content">
								<h3>{recipe.title}</h3>

								<p>{recipe.description}</p>

								<div class="recipe-footer">
									<span>
										⏱ {recipe.cooking_time || 20} Min
									</span>

									<span class="open-link">
										Öffnen →
									</span>
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
		font-family:
			Inter,
			-apple-system,
			BlinkMacSystemFont,
			'Segoe UI',
			sans-serif;
		background: #04070a;
		color: white;
	}
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
			gap: 18px;
		min-height: 100vh;
		overflow: hidden;
		background: #04070a;
			display: block;
			border-radius: 16px;
			overflow: hidden;
			text-decoration: none;
			color: inherit;
			background: rgba(255,255,255,0.03);
			border: 1px solid rgba(255,255,255,0.04);
			transition: transform 0.16s, box-shadow 0.16s;
	}

	.blur-1 {
			transform: translateY(-6px);
			box-shadow: 0 12px 30px rgba(2,6,23,0.6);
		width: 500px;
		height: 500px;
		background: rgba(34, 197, 94, 0.15);
			position: relative;
			width: 100%;
			height: 160px;
			overflow: hidden;
			flex-shrink: 0;
		right: -150px;
		width: 500px;
		height: 500px;
			width: 100%;
			height: 100%;
			object-fit: cover;
			display: block;

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
		transition: 0.3s;
	}

	.logout-btn:hover {
		background: rgba(239, 68, 68, 0.15);
		border-color: rgba(239, 68, 68, 0.2);
	}

	/* CONTENT */

	.content {
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
		font-size: 38px;
		margin: 0;
		font-weight: 800;
	}

	.section-header p {
		margin-top: 10px;
		color: #64748b;
	}

	.section-header a {
		color: #4ade80;
		text-decoration: none;
		font-weight: 600;
	}

	/* GRID */

	.recipes-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
		gap: 28px;
	}

	.recipe-card {
		overflow: hidden;
		border-radius: 32px;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		backdrop-filter: blur(20px);
		text-decoration: none;
		color: inherit;
		transition: 0.35s;
	}

	.recipe-card:hover {
		transform: translateY(-8px);
		border-color: rgba(34, 197, 94, 0.25);
		box-shadow: 0 25px 60px rgba(0, 0, 0, 0.35);
	}

	.recipe-image {
		position: relative;
		height: 240px;
		overflow: hidden;
	}

	.recipe-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		transition: transform 0.7s ease;
	}

	.recipe-card:hover img {
		transform: scale(1.08);
	}

	.image-overlay {
		position: absolute;
		inset: 0;
		background: linear-gradient(to top, rgba(0,0,0,.7), transparent);
	}

	.recipe-content {
		padding: 28px;
	}

	.recipe-content h3 {
		margin: 0 0 12px;
		font-size: 28px;
		font-weight: 800;
	}

	.recipe-content p {
		margin: 0 0 24px;
		line-height: 1.7;
		color: #94a3b8;
	}

	.recipe-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding-top: 18px;
		border-top: 1px solid rgba(255,255,255,0.06);
		font-size: 14px;
		color: #64748b;
	}

	.open-link {
		color: #4ade80;
		font-weight: 700;
	}

	/* EMPTY */

	.empty-state {
		padding: 80px;
		text-align: center;
		border-radius: 32px;
		background: rgba(255,255,255,0.04);
		border: 1px solid rgba(255,255,255,0.05);
		color: #64748b;
	}

	/* MOBILE */

	@media (max-width: 900px) {
		.hero {
			flex-direction: column;
			align-items: flex-start;
		}

		.hero h1 {
			font-size: 48px;
		}

		.glass-nav {
			padding: 20px;
		}

		.content {
			padding: 32px 20px 120px;
		}

		.searchbar {
			flex-direction: column;
		}

		.searchbar button {
			width: 100%;
		}
	}
</style>
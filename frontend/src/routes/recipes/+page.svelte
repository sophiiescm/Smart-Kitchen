<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { Flame, Search, Star, Clock3, ChefHat, Plus, Heart } from 'lucide-svelte';
	import { favoriteRecipe, unfavoriteRecipe } from '$lib/api';

	type Ingredient = { name: string; amount?: number; unit?: string };
	type Recipe = {
		id: number;
		user_id?: number;
		title: string;
		description?: string;
		category?: string;
		prep_time_minutes?: number;
		image_url?: string;
		is_public?: boolean;
		is_favorited?: boolean;
		average_rating?: number;
		rating_count?: number;
		ingredients?: Ingredient[];
		tags?: { name: string }[];
	};

	let recipes = $state<Recipe[]>([]);
	let loading = $state(true);
	let errorMessage = $state('');
	let search = $state('');
	let selectedCategory = $state('');
	let showOnlyMine = $state(false);
	let showOnlyFavorites = $state(false);
	let isLoggedIn = $state(false);
	let currentUserId = $state<number | null>(null);

	const categories = ['Frühstück', 'Hauptspeise', 'Dessert', 'Backen'];

	onMount(async () => {
		// Suche aus URL-Parameter (?q=...) übernehmen
		const urlQuery = $page.url.searchParams.get('q');
		if (urlQuery) search = urlQuery;

		// Token-Check für UI-Anpassungen
		const token = localStorage.getItem('token');
		isLoggedIn = !!token;

		try {
			const headers: Record<string, string> = {};
			if (token) headers['Authorization'] = `Bearer ${token}`;

			// Eigene User-ID herausfinden (nur wenn eingeloggt) — wird für
			// den "Nur meine Rezepte"-Filter und Owner-Erkennung gebraucht.
			if (token) {
				try {
					const profileRes = await fetch('http://localhost:8000/my-profile', { headers });
					if (profileRes.ok) {
						const profile = await profileRes.json();
						currentUserId = profile.id;
					}
				} catch { /* ignore */ }
			}

			const res = await fetch('http://localhost:8000/recipes', { headers });
			if (res.ok) {
				recipes = await res.json();
			} else {
				errorMessage = 'Rezepte konnten nicht geladen werden.';
			}
		} catch (error) {
			console.error(error);
			errorMessage = 'Verbindung zum Server fehlgeschlagen.';
		} finally {
			loading = false;
		}
	});

	// Filter durchsucht zusätzlich Zutaten (Spec-Anforderung: "Volltextsuche,
	// Filterung nach Kategorie oder Zutat")
	let filteredRecipes = $derived(
		recipes.filter((recipe) => {
			const q = search.trim().toLowerCase();

			const matchesSearch =
				q === '' ||
				recipe.title?.toLowerCase().includes(q) ||
				recipe.description?.toLowerCase().includes(q) ||
				recipe.category?.toLowerCase().includes(q) ||
				recipe.tags?.some((t) => t.name?.toLowerCase().includes(q)) ||
				recipe.ingredients?.some((i) => i.name?.toLowerCase().includes(q));

			const matchesCategory =
				selectedCategory === '' ||
				recipe.category?.toLowerCase() === selectedCategory.toLowerCase();

			const matchesOwner =
				!showOnlyMine ||
				(currentUserId !== null && recipe.user_id === currentUserId);

			const matchesFavorite = !showOnlyFavorites || recipe.is_favorited === true;

			return matchesSearch && matchesCategory && matchesOwner && matchesFavorite;
		})
	);

	async function toggleFavorite(event: MouseEvent, recipe: Recipe) {
		// Klick auf das Herz darf nicht zur Detailseite navigieren
		event.preventDefault();
		event.stopPropagation();

		if (!isLoggedIn) {
			window.location.href = '/auth/login?redirect=/recipes';
			return;
		}

		const wasFav = recipe.is_favorited === true;
		// Optimistic update
		recipes = recipes.map((r) =>
			r.id === recipe.id ? { ...r, is_favorited: !wasFav } : r
		);

		try {
			if (wasFav) {
				await unfavoriteRecipe(recipe.id);
			} else {
				await favoriteRecipe(recipe.id);
			}
		} catch (err) {
			console.error(err);
			// Rollback
			recipes = recipes.map((r) =>
				r.id === recipe.id ? { ...r, is_favorited: wasFav } : r
			);
			errorMessage = 'Favoriten konnten nicht aktualisiert werden.';
		}
	}

	function clearFilters() {
		search = '';
		selectedCategory = '';
	}
</script>

<div class="page-bg">
	<div class="background-blur blur-1"></div>
	<div class="background-blur blur-2"></div>

	<nav class="glass-nav">
		<a href="/" class="logo">Smart<span>Kitchen</span></a>
		<div class="nav-actions-row">
			{#if isLoggedIn}
				<a href="/shopping-list" class="back-btn">🛒 Einkaufsliste</a>
			{/if}
			<a href="/" class="back-btn">← Dashboard</a>
		</div>
	</nav>

	<section class="container">
		<!-- HEADER -->
		<div class="page-header">
			<div class="header-left">
				<div class="badge">
					<Flame class="badge-icon" />
					Community Rezepte
				</div>

				<h1>Rezepte entdecken</h1>

				<p class="subtitle">
					Durchstöbere beliebte Community-Rezepte und finde neue Inspiration.
				</p>
			</div>

			{#if isLoggedIn}
				<a href="/recipes/new" class="create-btn">
					<Plus class="btn-icon" />
					Rezept erstellen
				</a>
			{:else}
				<a href="/auth/login" class="create-btn">
					Anmelden zum Erstellen
				</a>
			{/if}
		</div>

		<!-- SEARCH -->
		<div class="search-bar">
			<Search class="search-icon" />
			<input
				bind:value={search}
				type="text"
				placeholder="Rezepte, Tags oder Kategorien durchsuchen..."
			/>
			{#if search}
				<button class="clear-search" onclick={() => (search = '')}>✕</button>
			{/if}
		</div>

		<!-- CATEGORIES -->
		<div class="category-row">
			<button
				class="category-chip"
				class:active={selectedCategory === ''}
				onclick={() => (selectedCategory = '')}
			>
				Alle
			</button>

			{#each categories as category}
				<button
					class="category-chip"
					class:active={selectedCategory === category}
					onclick={() => (selectedCategory = category)}
				>
					{category}
				</button>
			{/each}

			{#if isLoggedIn}
				<button
					class="category-chip mine-chip"
					class:active={showOnlyMine}
					onclick={() => (showOnlyMine = !showOnlyMine)}
					title="Nur eigene Rezepte anzeigen"
				>
					{showOnlyMine ? '✓ Meine Rezepte' : '👤 Meine Rezepte'}
				</button>

				<button
					class="category-chip fav-chip"
					class:active={showOnlyFavorites}
					onclick={() => (showOnlyFavorites = !showOnlyFavorites)}
					title="Nur Favoriten anzeigen"
				>
					{showOnlyFavorites ? '❤ Favoriten' : '🤍 Favoriten'}
				</button>
			{/if}
		</div>

		<!-- ERROR -->
		{#if errorMessage}
			<div class="error-banner">⚠ {errorMessage}</div>
		{/if}

		<!-- LOADING SKELETON -->
		{#if loading}
			<div class="recipe-grid">
				{#each Array(6) as _}
					<div class="recipe-card skeleton">
						<div class="skeleton-img"></div>
						<div class="skeleton-body">
							<div class="skeleton-line short"></div>
							<div class="skeleton-line"></div>
							<div class="skeleton-line"></div>
						</div>
					</div>
				{/each}
			</div>
		{/if}

		<!-- EMPTY STATE -->
		{#if !loading && filteredRecipes.length === 0}
			<div class="empty-state">
				<ChefHat class="empty-icon" />
				<h3>Keine Rezepte gefunden</h3>
				{#if search || selectedCategory}
					<p>Versuche andere Suchbegriffe oder Filter.</p>
					<button class="reset-btn" onclick={clearFilters}>Filter zurücksetzen</button>
				{:else}
					<p>Sei der erste und teile dein Lieblingsrezept!</p>
					<a href="/recipes/new" class="reset-btn">+ Rezept erstellen</a>
				{/if}
			</div>
		{/if}

		<!-- GRID -->
		{#if !loading && filteredRecipes.length > 0}
			<div class="recipe-grid">
				{#each filteredRecipes as recipe (recipe.id)}
					<a href={`/recipes/${recipe.id}`} class="recipe-card">
						<div class="card-img">
							{#if recipe.image_url}
								<img src={recipe.image_url} alt={recipe.title} />
							{:else}
								<div class="img-placeholder">
									<ChefHat class="placeholder-icon" />
								</div>
							{/if}
							<div class="img-overlay"></div>
							{#if recipe.category}
								<span class="category-badge">{recipe.category}</span>
							{/if}
							{#if recipe.is_public === false}
								<span class="private-badge" title="Privates Rezept — nur für dich sichtbar">🔒 Privat</span>
							{/if}

							{#if isLoggedIn}
								<button
									type="button"
									class="fav-btn"
									class:active={recipe.is_favorited === true}
									onclick={(e) => toggleFavorite(e, recipe)}
									aria-label={recipe.is_favorited ? 'Aus Favoriten entfernen' : 'Zu Favoriten hinzufügen'}
									title={recipe.is_favorited ? 'Aus Favoriten entfernen' : 'Zu Favoriten hinzufügen'}
								>
									<Heart class="fav-icon" />
								</button>
							{/if}
						</div>

						<div class="card-body">
							<div class="card-top">
								<h2>{recipe.title}</h2>
								<div class="rating-pill">
									<Star class="star-icon" />
									{recipe.average_rating?.toFixed(1) ?? '0.0'}
								</div>
							</div>

							<p class="card-desc">
								{recipe.description ?? 'Keine Beschreibung verfügbar.'}
							</p>

							{#if recipe.tags && recipe.tags.length > 0}
								<div class="card-tags">
									{#each recipe.tags.slice(0, 3) as tag}
										<span class="tag-chip">#{tag.name}</span>
									{/each}
								</div>
							{/if}

							<div class="card-footer">
								<div class="time-info">
									<Clock3 class="time-icon" />
									{recipe.prep_time_minutes ?? '–'} Min
								</div>
								<span class="open-link">Details →</span>
							</div>
						</div>
					</a>
				{/each}
			</div>
		{/if}
	</section>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
		background: #04070a;
		color: white;
	}

	.page-bg {
		position: relative;
		min-height: 100vh;
		background: #04070a;
		overflow: hidden;
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
		width: 520px;
		height: 520px;
		background: rgba(34, 197, 94, 0.15);
	}

	.blur-2 {
		bottom: -200px;
		right: -150px;
		width: 520px;
		height: 520px;
		background: rgba(16, 185, 129, 0.12);
	}

	.glass-nav {
		position: sticky;
		top: 0;
		z-index: 10;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 24px 40px;
		background: rgba(0, 0, 0, 0.35);
		backdrop-filter: blur(18px);
		border-bottom: 1px solid rgba(255, 255, 255, 0.06);
	}

	.logo {
		font-size: 26px;
		font-weight: 900;
		letter-spacing: -1px;
		color: white;
		text-decoration: none;
	}

	.logo span {
		color: #22c55e;
	}

	.nav-actions-row {
		display: flex;
		gap: 10px;
		align-items: center;
	}

	.back-btn {
		padding: 12px 18px;
		border-radius: 16px;
		background: rgba(255, 255, 255, 0.06);
		border: 1px solid rgba(255, 255, 255, 0.08);
		color: white;
		text-decoration: none;
		font-weight: 600;
		font-size: 14px;
	}

	.back-btn:hover {
		background: rgba(255, 255, 255, 0.1);
	}

	.container {
		position: relative;
		z-index: 1;
		max-width: 1400px;
		margin: 0 auto;
		padding: 48px 32px 100px;
	}

	/* HEADER */
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		gap: 24px;
		margin-bottom: 40px;
		flex-wrap: wrap;
	}

	.header-left {
		max-width: 700px;
	}

	.badge {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 8px 14px;
		border-radius: 999px;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		color: #cbd5e1;
		font-size: 13px;
		font-weight: 600;
		margin-bottom: 16px;
	}

	.badge :global(.badge-icon) {
		width: 16px;
		height: 16px;
		color: #fb923c;
	}

	.page-header h1 {
		font-size: 48px;
		font-weight: 900;
		margin: 0 0 12px;
		letter-spacing: -2px;
		line-height: 1.05;
	}

	.subtitle {
		margin: 0;
		font-size: 16px;
		color: #94a3b8;
		line-height: 1.6;
	}

	.create-btn {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 14px 22px;
		border-radius: 16px;
		background: linear-gradient(to right, #16a34a, #065f46);
		color: white;
		font-weight: 700;
		font-size: 14px;
		text-decoration: none;
		box-shadow: 0 10px 30px rgba(22, 163, 74, 0.3);
		transition: 0.2s;
	}

	.create-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 14px 40px rgba(22, 163, 74, 0.4);
	}

	.create-btn :global(.btn-icon) {
		width: 16px;
		height: 16px;
	}

	/* SEARCH */
	.search-bar {
		position: relative;
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 14px 20px;
		border-radius: 16px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.08);
		margin-bottom: 18px;
		transition: border 0.2s;
	}

	.search-bar:focus-within {
		border-color: rgba(74, 222, 128, 0.3);
	}

	.search-bar :global(.search-icon) {
		width: 20px;
		height: 20px;
		color: #64748b;
		flex-shrink: 0;
	}

	.search-bar input {
		flex: 1;
		background: transparent;
		border: none;
		outline: none;
		color: white;
		font-size: 15px;
		font-family: inherit;
	}

	.search-bar input::placeholder {
		color: #64748b;
	}

	.clear-search {
		flex-shrink: 0;
		width: 24px;
		height: 24px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.08);
		border: none;
		color: #cbd5e1;
		cursor: pointer;
		font-size: 12px;
	}

	/* CATEGORIES */
	.category-row {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-bottom: 36px;
	}

	.category-chip {
		padding: 10px 18px;
		border-radius: 12px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.08);
		color: #cbd5e1;
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
		transition: 0.2s;
	}

	.category-chip:hover {
		background: rgba(255, 255, 255, 0.08);
		color: white;
	}

	.category-chip.active {
		background: rgba(34, 197, 94, 0.15);
		border-color: rgba(34, 197, 94, 0.3);
		color: #4ade80;
	}

	.mine-chip {
		margin-left: auto;
		background: rgba(59, 130, 246, 0.06);
		border-color: rgba(59, 130, 246, 0.18);
		color: #93c5fd;
	}

	.mine-chip.active {
		background: rgba(59, 130, 246, 0.18);
		border-color: rgba(59, 130, 246, 0.35);
		color: #bfdbfe;
	}

	.fav-chip {
		background: rgba(244, 63, 94, 0.06);
		border-color: rgba(244, 63, 94, 0.18);
		color: #fda4af;
	}

	.fav-chip.active {
		background: rgba(244, 63, 94, 0.18);
		border-color: rgba(244, 63, 94, 0.4);
		color: #fecdd3;
	}

	/* ERROR */
	.error-banner {
		padding: 14px 18px;
		border-radius: 14px;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		color: #fca5a5;
		margin-bottom: 20px;
		font-size: 14px;
	}

	/* RECIPE GRID */
	.recipe-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 24px;
	}

	.recipe-card {
		display: flex;
		flex-direction: column;
		border-radius: 24px;
		overflow: hidden;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.07);
		text-decoration: none;
		color: inherit;
		transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
	}

	.recipe-card:hover {
		transform: translateY(-6px);
		border-color: rgba(34, 197, 94, 0.25);
		box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
	}

	.card-img {
		position: relative;
		aspect-ratio: 16 / 10;
		overflow: hidden;
		background: rgba(255, 255, 255, 0.02);
	}

	.card-img img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		transition: transform 0.5s;
	}

	.recipe-card:hover .card-img img {
		transform: scale(1.05);
	}

	.img-placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, rgba(34, 197, 94, 0.08), rgba(16, 185, 129, 0.05));
	}

	.img-placeholder :global(.placeholder-icon) {
		width: 64px;
		height: 64px;
		color: rgba(74, 222, 128, 0.4);
	}

	.img-overlay {
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
		letter-spacing: 0.04em;
	}

	.private-badge {
		position: absolute;
		top: 14px;
		right: 14px;
		padding: 6px 12px;
		border-radius: 999px;
		background: rgba(244, 114, 182, 0.85);
		color: white;
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		backdrop-filter: blur(8px);
	}

	.fav-btn {
		position: absolute;
		bottom: 14px;
		right: 14px;
		width: 40px;
		height: 40px;
		border-radius: 50%;
		background: rgba(0, 0, 0, 0.55);
		backdrop-filter: blur(8px);
		border: 1px solid rgba(255, 255, 255, 0.15);
		color: rgba(255, 255, 255, 0.7);
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s;
		z-index: 2;
	}

	.fav-btn:hover {
		transform: scale(1.1);
		background: rgba(0, 0, 0, 0.7);
		color: #fb7185;
	}

	.fav-btn.active {
		background: rgba(244, 63, 94, 0.95);
		border-color: rgba(244, 63, 94, 0.5);
		color: white;
		box-shadow: 0 4px 16px rgba(244, 63, 94, 0.4);
	}

	.fav-btn.active :global(.fav-icon) {
		fill: currentColor;
	}

	.fav-btn :global(.fav-icon) {
		width: 18px;
		height: 18px;
	}

	.card-body {
		padding: 20px 22px 22px;
		display: flex;
		flex-direction: column;
		gap: 12px;
		flex: 1;
	}

	.card-top {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 12px;
	}

	.card-body h2 {
		margin: 0;
		font-size: 18px;
		font-weight: 800;
		line-height: 1.3;
		flex: 1;
	}

	.rating-pill {
		display: flex;
		align-items: center;
		gap: 4px;
		color: #facc15;
		font-size: 13px;
		font-weight: 700;
		flex-shrink: 0;
	}

	.rating-pill :global(.star-icon) {
		width: 14px;
		height: 14px;
		fill: currentColor;
	}

	.card-desc {
		margin: 0;
		font-size: 14px;
		line-height: 1.55;
		color: #94a3b8;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.card-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
	}

	.tag-chip {
		padding: 3px 8px;
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.05);
		color: #cbd5e1;
		font-size: 11px;
		font-weight: 600;
	}

	.card-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 12px;
		margin-top: auto;
		border-top: 1px solid rgba(255, 255, 255, 0.06);
		font-size: 13px;
	}

	.time-info {
		display: flex;
		align-items: center;
		gap: 6px;
		color: #94a3b8;
	}

	.time-info :global(.time-icon) {
		width: 14px;
		height: 14px;
	}

	.open-link {
		color: #4ade80;
		font-weight: 700;
		transition: transform 0.2s;
	}

	.recipe-card:hover .open-link {
		transform: translateX(3px);
	}

	/* EMPTY */
	.empty-state {
		padding: 80px 40px;
		text-align: center;
		border-radius: 24px;
		background: rgba(255, 255, 255, 0.03);
		border: 1px solid rgba(255, 255, 255, 0.06);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 12px;
	}

	.empty-state :global(.empty-icon) {
		width: 56px;
		height: 56px;
		color: #475569;
	}

	.empty-state h3 {
		margin: 0;
		font-size: 22px;
		font-weight: 700;
	}

	.empty-state p {
		margin: 0;
		color: #64748b;
		font-size: 14px;
	}

	.reset-btn {
		margin-top: 8px;
		padding: 12px 22px;
		border-radius: 12px;
		background: rgba(34, 197, 94, 0.1);
		border: 1px solid rgba(34, 197, 94, 0.25);
		color: #4ade80;
		font-size: 13px;
		font-weight: 700;
		cursor: pointer;
		font-family: inherit;
		text-decoration: none;
		display: inline-block;
	}

	.reset-btn:hover {
		background: rgba(34, 197, 94, 0.18);
	}

	/* SKELETON */
	.skeleton {
		pointer-events: none;
	}

	.skeleton-img {
		aspect-ratio: 16 / 10;
		background: linear-gradient(90deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.03));
		background-size: 200% 100%;
		animation: shimmer 1.5s infinite;
	}

	.skeleton-body {
		padding: 20px 22px;
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.skeleton-line {
		height: 12px;
		border-radius: 6px;
		background: linear-gradient(90deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.04));
		background-size: 200% 100%;
		animation: shimmer 1.5s infinite;
	}

	.skeleton-line.short {
		width: 40%;
	}

	@keyframes shimmer {
		0% {
			background-position: 200% 0;
		}
		100% {
			background-position: -200% 0;
		}
	}

	@media (max-width: 900px) {
		.glass-nav {
			padding: 20px;
		}

		.container {
			padding: 32px 20px 80px;
		}

		.page-header h1 {
			font-size: 36px;
		}

		.page-header {
			align-items: flex-start;
		}
	}
</style>

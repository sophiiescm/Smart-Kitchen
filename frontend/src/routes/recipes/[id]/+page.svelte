<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { Star } from 'lucide-svelte';
	import { getRecipe, rateRecipe } from '$lib/api';

	type Recipe = {
		id: number;
		title: string;
		description?: string;
		category?: string;
		prep_time_minutes?: number;
		servings?: number;
		average_rating?: number;
		rating_count?: number;
		ingredients?: { name: string; amount?: number; unit?: string }[];
		steps?: { step_number: number; instruction: string }[];
		tags?: { name: string }[];
	};

	let recipe: Recipe | null = null;
	let loading = true;
	let errorMessage = '';
	let selectedRating = 0;

	onMount(async () => {
		const recipeId = Number($page.params.id);
		if (!recipeId) {
			errorMessage = 'Ungültige Rezept-ID.';
			loading = false;
			return;
		}

		try {
			recipe = await getRecipe(recipeId);
		} catch (error) {
			console.error(error);
			errorMessage = 'Das Rezept konnte nicht geladen werden.';
		} finally {
			loading = false;
		}
	});

	async function submitRating(rating: number) {
		selectedRating = rating;
		if (!recipe) return;

		try {
			await rateRecipe(recipe.id, rating);
			recipe = await getRecipe(recipe.id);
		} catch (error) {
			console.error(error);
			errorMessage = 'Bewertung konnte nicht gespeichert werden.';
		}
	}
</script>

<div class="page-container">
	<div class="background-blur blur-1"></div>
	<div class="background-blur blur-2"></div>

	<nav class="glass-nav">
		<a href="/" class="logo">Smart<span>Kitchen</span></a>
		<a href="/recipes" class="back-btn">← Alle Rezepte</a>
	</nav>

	<main class="content">
		{#if loading}
			<div class="status-card">Lade Rezept...</div>
		{:else if errorMessage}
			<div class="status-card error">{errorMessage}</div>
		{:else if recipe}
			<section class="hero-card glass-card">
				<div class="hero-label">{recipe.category ?? 'Allgemein'}</div>
				<h1>{recipe.title}</h1>
				<p>{recipe.description}</p>

				<div class="hero-meta">
					<span>⏱ {recipe.prep_time_minutes ?? '-'} Min</span>
					<span>⭐ {recipe.average_rating?.toFixed(1) ?? '0.0'} ({recipe.rating_count ?? 0})</span>
				</div>

				<div class="tag-row">
					{#each recipe.tags ?? [] as tag}
						<span class="tag-pill">{tag.name}</span>
					{/each}
				</div>

				<div class="rating-box">
					<span>Jetzt bewerten:</span>
					<div class="stars">
						{#each [1, 2, 3, 4, 5] as star}
							<button
								on:click={() => submitRating(star)}
								class:selected={selectedRating >= star}
								aria-label={`Bewertung ${star} Sterne`}
							>
								<Star class="star-icon" />
							</button>
						{/each}
					</div>
				</div>
			</section>

			<section class="detail-grid">
				<div class="glass-card">
					<h2>Zutaten</h2>
					<ul>
						{#each recipe.ingredients ?? [] as ingredient}
							<li>{ingredient.name}</li>
						{/each}
					</ul>
				</div>

				<div class="glass-card">
					<h2>Zubereitung</h2>
					<ol>
						{#each recipe.steps ?? [] as step}
							<li>{step.instruction}</li>
						{/each}
					</ol>
				</div>
			</section>
		{/if}
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

	.page-container {
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
	}

	.blur-1 {
		top: -180px;
		left: -140px;
		width: 520px;
		height: 520px;
		background: rgba(34, 197, 94, 0.16);
	}

	.blur-2 {
		bottom: -160px;
		right: -140px;
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
		padding: 24px 32px;
		background: rgba(255, 255, 255, 0.04);
		backdrop-filter: blur(18px);
		border-bottom: 1px solid rgba(255, 255, 255, 0.08);
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

	.back-btn {
		padding: 12px 18px;
		border-radius: 16px;
		background: rgba(255, 255, 255, 0.08);
		border: 1px solid rgba(255, 255, 255, 0.12);
		color: white;
		text-decoration: none;
		font-weight: 600;
	}

	.content {
		position: relative;
		z-index: 1;
		max-width: 1100px;
		margin: 0 auto;
		padding: 40px 32px 80px;
	}

	.glass-card {
		border-radius: 32px;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		backdrop-filter: blur(20px);
		padding: 36px;
	}

	.hero-card {
		margin-bottom: 28px;
	}

	.hero-label {
		display: inline-flex;
		padding: 0.75rem 1rem;
		border-radius: 999px;
		background: rgba(34, 197, 94, 0.15);
		color: #a7f3d0;
		font-size: 0.95rem;
		font-weight: 700;
		margin-bottom: 18px;
	}

	h1 {
		font-size: 48px;
		margin: 0;
		line-height: 1.05;
	}

	.hero-card p {
		margin-top: 20px;
		color: #cbd5e1;
		font-size: 16px;
		line-height: 1.8;
	}

	.hero-meta {
		display: flex;
		flex-wrap: wrap;
		gap: 18px;
		margin-top: 24px;
		color: #94a3b8;
		font-size: 0.95rem;
	}

	.tag-row {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-top: 24px;
	}

	.tag-pill {
		padding: 8px 16px;
		border-radius: 999px;
		border: 1px solid rgba(255, 255, 255, 0.1);
		background: rgba(255, 255, 255, 0.06);
		color: #d1fae5;
		font-size: 0.9rem;
	}

	.detail-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 24px;
	}

	.detail-card h2 {
		margin-top: 0;
		font-size: 22px;
	}

	.detail-card ul,
	.detail-card ol {
		margin: 0;
		padding-left: 1.2rem;
		color: #e2e8f0;
	}

	.detail-card li {
		margin-bottom: 0.85rem;
	}

	.rating-box {
		display: flex;
		flex-direction: column;
		gap: 12px;
		margin-top: 24px;
	}

	.stars {
		display: flex;
		gap: 0.5rem;
	}

	button.selected .star-icon,
	button:hover .star-icon {
		color: #facc15;
	}

	.star-icon {
		width: 2rem;
		height: 2rem;
		color: #6b7280;
	}

	.status-card {
		padding: 3rem;
		border-radius: 30px;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		text-align: center;
	}

	.status-card.error {
		border-color: rgba(239, 68, 68, 0.3);
		background: rgba(239, 68, 68, 0.08);
	}

	@media (max-width: 900px) {
		.content {
			padding: 32px 20px 60px;
		}

		.detail-grid {
			grid-template-columns: 1fr;
		}
	}
</style>

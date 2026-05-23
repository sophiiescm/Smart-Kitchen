<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
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

<div class="detail-page">
	<div class="background-blur blur-1"></div>
	<div class="background-blur blur-2"></div>

	<main class="detail-content">
		{#if loading}
			<div class="loading-state">Lade Rezept...</div>
		{:else if errorMessage}
			<div class="error-state">{errorMessage}</div>
		{:else if recipe}
			<section class="detail-hero">
				<div class="detail-label">{recipe.category ?? 'Allgemein'}</div>
				<h1>{recipe.title}</h1>
				<p>{recipe.description}</p>

				<div class="detail-meta">
					<div>
						<strong>Zubereitung:</strong>
						{recipe.prep_time_minutes ?? '-'} Min
					</div>
					<div>
						<strong>Bewertung:</strong>
						{recipe.average_rating?.toFixed(1) ?? '0.0'} ({recipe.rating_count ?? 0})
					</div>
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
				<div class="detail-card">
					<h2>Zutaten</h2>
					<ul>
						{#each recipe.ingredients ?? [] as ingredient}
							<li>{ingredient.name}</li>
						{/each}
					</ul>
				</div>

				<div class="detail-card">
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
	.detail-page {
		position: relative;
		min-height: 100vh;
		background: #04070a;
		color: white;
		padding: 2rem;
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
		background: rgba(34, 197, 94, 0.14);
	}

	.blur-2 {
		bottom: -160px;
		right: -140px;
		width: 520px;
		height: 520px;
		background: rgba(16, 185, 129, 0.12);
	}

	.detail-content {
		position: relative;
		max-width: 1100px;
		margin: 0 auto;
		z-index: 1;
	}

	.detail-hero {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		backdrop-filter: blur(24px);
		padding: 3rem;
		border-radius: 32px;
		margin-bottom: 2rem;
	}

	.detail-label {
		display: inline-flex;
		padding: 0.65rem 1rem;
		border-radius: 999px;
		background: rgba(34, 197, 94, 0.14);
		color: #a7f3d0;
		font-size: 0.9rem;
		margin-bottom: 1rem;
	}

	.detail-meta {
		display: flex;
		gap: 1.5rem;
		margin-top: 1.75rem;
		font-size: 0.95rem;
		color: #94a3b8;
	}

	.rating-box {
		margin-top: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
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

	.detail-grid {
		display: grid;
		gap: 1.5rem;
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}

	.detail-card {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 32px;
		padding: 2rem;
	}

	.loading-state,
	.error-state {
		padding: 3rem;
		background: rgba(255,255,255,0.04);
		border: 1px solid rgba(255,255,255,0.08);
		border-radius: 32px;
		text-align: center;
	}
</style>

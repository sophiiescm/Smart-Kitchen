<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		getRecipe,
		rateRecipe,
		deleteRecipe,
		updateRecipe,
		getCurrentUser,
		isLoggedIn,
		favoriteRecipe,
		unfavoriteRecipe,
	} from '$lib/api';

	type Recipe = {
		id: number;
		user_id: number;
		title: string;
		description?: string;
		category?: string;
		prep_time_minutes?: number;
		servings?: number;
		image_url?: string;
		is_public?: boolean;
		is_favorited?: boolean;
		average_rating?: number;
		rating_count?: number;
		ingredients?: { name: string; amount?: number; unit?: string }[];
		steps?: { step_number: number; instruction: string }[];
		tags?: { name: string }[];
	};

	// In runes mode (vom svelte.config.js erzwungen) müssen reaktive
	// Werte mit $state() deklariert werden, sonst aktualisiert sich die UI nicht.
	let recipe = $state<Recipe | null>(null);
	let loading = $state(true);
	let errorMessage = $state('');
	let selectedRating = $state(0);
	let hoverRating = $state(0);
	let isOwner = $state(false);
	let isAuthenticated = $state(false);

	// Edit-Modus
	let isEditing = $state(false);
	let editTitle = $state('');
	let editDescription = $state('');
	let editCategory = $state('');
	let editTime = $state('');
	let editImageUrl = $state('');
	let editIsPublic = $state(true);
	let editIngredients = $state<string[]>(['']);
	let editSteps = $state<string[]>(['']);
	let editTags = $state('');
	let isSaving = $state(false);
	let isDeleting = $state(false);

	onMount(async () => {
		isAuthenticated = isLoggedIn();
		const recipeId = Number($page.params.id);
		if (!recipeId || Number.isNaN(recipeId)) {
			errorMessage = 'Ungültige Rezept-ID.';
			loading = false;
			return;
		}

		try {
			recipe = await getRecipe(recipeId);

			// Prüfen, ob der eingeloggte User der Besitzer ist
			if (isAuthenticated && recipe) {
				try {
					const me = await getCurrentUser();
					// Backend muss user_id im Response liefern -> wir vergleichen das
					const profile = me as { id?: number; username: string };
					if (profile?.id && recipe.user_id === profile.id) {
						isOwner = true;
					}
				} catch {
					// Profil-Abruf fehlgeschlagen — kein Eigentümer-Modus
				}
			}
		} catch (error) {
			console.error(error);
			errorMessage = 'Das Rezept konnte nicht geladen werden.';
		} finally {
			loading = false;
		}
	});

	async function submitRating(rating: number) {
		if (!isAuthenticated) {
			errorMessage = 'Bitte melde dich an, um Rezepte zu bewerten.';
			return;
		}
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

	function startEdit() {
		if (!recipe) return;
		editTitle = recipe.title;
		editDescription = recipe.description ?? '';
		editCategory = recipe.category ?? '';
		editTime = recipe.prep_time_minutes ? String(recipe.prep_time_minutes) : '';
		editImageUrl = recipe.image_url ?? '';
		editIsPublic = recipe.is_public ?? true;
		editIngredients = recipe.ingredients?.length
			? recipe.ingredients.map((i) => i.name)
			: [''];
		editSteps = recipe.steps?.length
			? recipe.steps.map((s) => s.instruction)
			: [''];
		editTags = recipe.tags?.map((t) => t.name).join(', ') ?? '';
		isEditing = true;
	}

	function cancelEdit() {
		isEditing = false;
		errorMessage = '';
	}

	function addEditIngredient() {
		editIngredients = [...editIngredients, ''];
	}

	function removeEditIngredient(i: number) {
		editIngredients = editIngredients.filter((_, idx) => idx !== i);
	}

	function addEditStep() {
		editSteps = [...editSteps, ''];
	}

	function removeEditStep(i: number) {
		editSteps = editSteps.filter((_, idx) => idx !== i);
	}

	async function compressImage(file: File, maxSize = 1280, quality = 0.8): Promise<string> {
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = () => {
				const img = new Image();
				img.onload = () => {
					let { width, height } = img;
					if (width > maxSize || height > maxSize) {
						const scale = Math.min(maxSize / width, maxSize / height);
						width = Math.round(width * scale);
						height = Math.round(height * scale);
					}
					const canvas = document.createElement('canvas');
					canvas.width = width;
					canvas.height = height;
					const ctx = canvas.getContext('2d');
					if (!ctx) {
						reject(new Error('Canvas-Kontext nicht verfügbar.'));
						return;
					}
					ctx.drawImage(img, 0, 0, width, height);
					resolve(canvas.toDataURL('image/jpeg', quality));
				};
				img.onerror = () => reject(new Error('Bild konnte nicht geladen werden.'));
				img.src = reader.result as string;
			};
			reader.onerror = () => reject(new Error('Bild konnte nicht gelesen werden.'));
			reader.readAsDataURL(file);
		});
	}

	async function handleEditImageFile(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;
		if (file.size > 10 * 1024 * 1024) {
			errorMessage = 'Bild ist zu groß (max. 10 MB Originaldatei).';
			target.value = '';
			return;
		}
		try {
			editImageUrl = await compressImage(file);
			errorMessage = '';
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'Bild konnte nicht verarbeitet werden.';
		}
	}

	async function saveEdit() {
		if (!recipe) return;
		if (!editTitle.trim()) {
			errorMessage = 'Bitte gib einen Titel ein.';
			return;
		}
		isSaving = true;
		errorMessage = '';

		try {
			const payload = {
				title: editTitle.trim(),
				description: editDescription.trim(),
				category: editCategory || null,
				prep_time_minutes: editTime ? Number(editTime) : null,
				image_url: editImageUrl || null,
				is_public: editIsPublic,
				ingredients: editIngredients
					.filter((s) => s.trim().length > 0)
					.map((name) => ({ name: name.trim() })),
				steps: editSteps
					.filter((s) => s.trim().length > 0)
					.map((instruction, idx) => ({ step_number: idx + 1, instruction: instruction.trim() })),
				tags: editTags
					.split(',')
					.map((t) => t.trim())
					.filter((t) => t.length > 0),
			};
			await updateRecipe(recipe.id, payload);
			recipe = await getRecipe(recipe.id);
			isEditing = false;
		} catch (error) {
			console.error(error);
			errorMessage = error instanceof Error ? error.message : 'Speichern fehlgeschlagen.';
		} finally {
			isSaving = false;
		}
	}

	async function toggleFavorite() {
		if (!recipe) return;
		if (!isAuthenticated) {
			errorMessage = 'Bitte melde dich an, um Rezepte zu favorisieren.';
			return;
		}

		const wasFav = recipe.is_favorited === true;
		// optimistic update
		recipe = { ...recipe, is_favorited: !wasFav };

		try {
			if (wasFav) {
				await unfavoriteRecipe(recipe.id);
			} else {
				await favoriteRecipe(recipe.id);
			}
		} catch (err) {
			console.error(err);
			recipe = { ...recipe, is_favorited: wasFav };
			errorMessage = 'Favoriten konnten nicht aktualisiert werden.';
		}
	}

	async function confirmDelete() {
		if (!recipe) return;
		if (!confirm(`Rezept "${recipe.title}" wirklich löschen?`)) return;

		isDeleting = true;
		try {
			await deleteRecipe(recipe.id);
			await goto('/recipes');
		} catch (error) {
			console.error(error);
			errorMessage = error instanceof Error ? error.message : 'Löschen fehlgeschlagen.';
			isDeleting = false;
		}
	}
</script>

<div class="page-container">
	<div class="background-blur blur-1"></div>
	<div class="background-blur blur-2"></div>

	<nav class="glass-nav">
		<a href="/" class="logo">Smart<span>Kitchen</span></a>
		<div class="nav-right">
			<a href="/recipes" class="back-btn">← Alle Rezepte</a>
			{#if !isAuthenticated}
				<a href="/auth/login" class="back-btn">Anmelden</a>
			{/if}
		</div>
	</nav>

	<main class="content">
		{#if loading}
			<div class="status-card">
				<div class="spinner"></div>
				<p>Lade Rezept...</p>
			</div>
		{:else if errorMessage && !recipe}
			<div class="status-card error">
				⚠ {errorMessage}
				<a href="/recipes" class="back-link">Zurück zur Rezeptliste</a>
			</div>
		{:else if recipe && !isEditing}
			<!-- ANSICHT -->

			{#if errorMessage}
				<div class="inline-error">⚠ {errorMessage}</div>
			{/if}

			<section class="hero-card glass-card">
				{#if recipe.image_url}
					<div class="hero-image">
						<img src={recipe.image_url} alt={recipe.title} />
						<div class="hero-image-overlay"></div>
					</div>
				{/if}

				<div class="hero-body">
					<div class="hero-top">
						<div class="hero-meta-row">
							<span class="hero-label">{recipe.category ?? 'Allgemein'}</span>
							{#if recipe.is_public === false}
								<span class="visibility-badge private">🔒 Privat</span>
							{:else}
								<span class="visibility-badge public">🌐 Öffentlich</span>
							{/if}
						</div>

						<div class="owner-actions">
							{#if isAuthenticated}
								<button
									class="fav-btn-detail"
									class:active={recipe.is_favorited === true}
									onclick={toggleFavorite}
									title={recipe.is_favorited ? 'Aus Favoriten entfernen' : 'Zu Favoriten hinzufügen'}
								>
									{recipe.is_favorited ? '❤ Favorit' : '🤍 Favorisieren'}
								</button>
							{/if}
							{#if isOwner}
								<button class="edit-btn" onclick={startEdit}>
									✏️ Bearbeiten
								</button>
								<button class="delete-btn" onclick={confirmDelete} disabled={isDeleting}>
									{isDeleting ? 'Lösche...' : '🗑 Löschen'}
								</button>
							{/if}
						</div>
					</div>

					<h1>{recipe.title}</h1>

					{#if recipe.description}
						<p class="hero-desc">{recipe.description}</p>
					{/if}

					<div class="hero-stats">
						<div class="stat">
							<span class="stat-label">Kochzeit</span>
							<span class="stat-value">⏱ {recipe.prep_time_minutes ?? '–'} Min</span>
						</div>
						<div class="stat">
							<span class="stat-label">Bewertung</span>
							<span class="stat-value">
								⭐ {recipe.average_rating?.toFixed(1) ?? '0.0'}
								<span class="stat-sub">({recipe.rating_count ?? 0})</span>
							</span>
						</div>
						{#if recipe.servings}
							<div class="stat">
								<span class="stat-label">Portionen</span>
								<span class="stat-value">🍽 {recipe.servings}</span>
							</div>
						{/if}
					</div>

					{#if recipe.tags && recipe.tags.length > 0}
						<div class="tag-row">
							{#each recipe.tags as tag}
								<span class="tag-pill">#{tag.name}</span>
							{/each}
						</div>
					{/if}

					<div class="rating-box">
						<span class="rating-label">Jetzt bewerten:</span>
						<div class="stars">
							{#each [1, 2, 3, 4, 5] as star}
								<button
									type="button"
									class="star-btn"
									class:filled={(hoverRating || selectedRating) >= star}
									onclick={() => submitRating(star)}
									onmouseenter={() => (hoverRating = star)}
									onmouseleave={() => (hoverRating = 0)}
									aria-label={`Bewertung ${star} Sterne`}
								>
									★
								</button>
							{/each}
						</div>
					</div>
				</div>
			</section>

			<section class="detail-grid">
				<div class="glass-card detail-card">
					<h2>🥗 Zutaten</h2>
					{#if recipe.ingredients && recipe.ingredients.length > 0}
						<ul class="ingredient-list">
							{#each recipe.ingredients as ingredient}
								<li>
									{#if ingredient.amount}
										<span class="amount">{ingredient.amount} {ingredient.unit ?? ''}</span>
									{/if}
									{ingredient.name}
								</li>
							{/each}
						</ul>
					{:else}
						<p class="empty">Keine Zutaten angegeben.</p>
					{/if}
				</div>

				<div class="glass-card detail-card">
					<h2>👨‍🍳 Zubereitung</h2>
					{#if recipe.steps && recipe.steps.length > 0}
						<ol class="step-list">
							{#each recipe.steps as step}
								<li>
									<span class="step-num">{step.step_number}</span>
									<span class="step-text">{step.instruction}</span>
								</li>
							{/each}
						</ol>
					{:else}
						<p class="empty">Keine Schritte angegeben.</p>
					{/if}
				</div>
			</section>
		{:else if recipe && isEditing}
			<!-- BEARBEITEN -->
			<section class="glass-card edit-card">
				<div class="edit-header">
					<h1>Rezept bearbeiten</h1>
					<div class="edit-actions">
						<button class="cancel-btn-small" onclick={cancelEdit} disabled={isSaving}>Abbrechen</button>
						<button class="save-btn" onclick={saveEdit} disabled={isSaving}>
							{isSaving ? 'Speichere...' : '💾 Speichern'}
						</button>
					</div>
				</div>

				{#if errorMessage}
					<div class="inline-error">⚠ {errorMessage}</div>
				{/if}

				<div class="edit-grid">
					<div class="field">
						<label for="edit-title">Titel</label>
						<input id="edit-title" type="text" bind:value={editTitle} />
					</div>

					<div class="field">
						<label for="edit-category">Kategorie</label>
						<select id="edit-category" bind:value={editCategory}>
							<option value="">Kategorie wählen</option>
							<option value="Pasta">Pasta</option>
							<option value="Dessert">Dessert</option>
							<option value="Frühstück">Frühstück</option>
							<option value="Vegan">Vegan</option>
							<option value="Vegetarisch">Vegetarisch</option>
							<option value="Fleisch">Fleisch</option>
						</select>
					</div>

					<div class="field">
						<label for="edit-time">Kochzeit (Min)</label>
						<input id="edit-time" type="number" bind:value={editTime} />
					</div>

					<div class="field">
						<label for="edit-tags">Tags (Komma-getrennt)</label>
						<input id="edit-tags" type="text" bind:value={editTags} />
					</div>

					<div class="field full">
						<label for="edit-desc">Beschreibung</label>
						<textarea id="edit-desc" rows="3" bind:value={editDescription}></textarea>
					</div>

					<div class="field full">
						<label>Sichtbarkeit</label>
						<div class="toggle-group">
							<button
								type="button"
								class="toggle-btn"
								class:active={editIsPublic === true}
								onclick={() => (editIsPublic = true)}
							>
								🌐 Öffentlich
							</button>
							<button
								type="button"
								class="toggle-btn"
								class:active={editIsPublic === false}
								onclick={() => (editIsPublic = false)}
							>
								🔒 Privat
							</button>
						</div>
					</div>

					<div class="field full">
						<label>Bild</label>
						{#if editImageUrl}
							<div class="edit-image-preview">
								<img src={editImageUrl} alt="Vorschau" />
								<button type="button" class="image-remove" onclick={() => (editImageUrl = '')}>✕</button>
							</div>
						{/if}
						<input type="file" accept="image/*" onchange={handleEditImageFile} />
						<input
							type="text"
							placeholder="Oder Bild-URL einfügen"
							value={editImageUrl.startsWith('data:') ? '' : editImageUrl}
							oninput={(e) => (editImageUrl = (e.target as HTMLInputElement).value)}
						/>
					</div>
				</div>

				<div class="edit-section">
					<div class="section-row">
						<h3>Zutaten</h3>
						<button class="add-btn" type="button" onclick={addEditIngredient}>+ Hinzufügen</button>
					</div>
					{#each editIngredients as _, i}
						<div class="list-item">
							<span class="list-num">{i + 1}</span>
							<input type="text" bind:value={editIngredients[i]} />
							{#if editIngredients.length > 1}
								<button class="x-btn" type="button" onclick={() => removeEditIngredient(i)}>✕</button>
							{/if}
						</div>
					{/each}
				</div>

				<div class="edit-section">
					<div class="section-row">
						<h3>Zubereitung</h3>
						<button class="add-btn" type="button" onclick={addEditStep}>+ Hinzufügen</button>
					</div>
					{#each editSteps as _, i}
						<div class="list-item">
							<span class="list-num">{i + 1}</span>
							<textarea rows="2" bind:value={editSteps[i]}></textarea>
							{#if editSteps.length > 1}
								<button class="x-btn" type="button" onclick={() => removeEditStep(i)}>✕</button>
							{/if}
						</div>
					{/each}
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
		z-index: 0;
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

	.nav-right {
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

	.content {
		position: relative;
		z-index: 1;
		max-width: 1100px;
		margin: 0 auto;
		padding: 40px 32px 80px;
	}

	.glass-card {
		border-radius: 32px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.07);
		backdrop-filter: blur(20px);
	}

	/* HERO */
	.hero-card {
		overflow: hidden;
		margin-bottom: 28px;
	}

	.hero-image {
		position: relative;
		width: 100%;
		height: 360px;
		overflow: hidden;
	}

	.hero-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.hero-image-overlay {
		position: absolute;
		inset: 0;
		background: linear-gradient(to bottom, rgba(4, 7, 10, 0.1), rgba(4, 7, 10, 0.7));
	}

	.hero-body {
		padding: 36px;
	}

	.hero-top {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16px;
		flex-wrap: wrap;
		margin-bottom: 16px;
	}

	.hero-meta-row {
		display: flex;
		gap: 10px;
		flex-wrap: wrap;
	}

	.hero-label {
		display: inline-flex;
		padding: 8px 16px;
		border-radius: 999px;
		background: rgba(34, 197, 94, 0.15);
		color: #a7f3d0;
		font-size: 13px;
		font-weight: 700;
	}

	.visibility-badge {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		padding: 8px 14px;
		border-radius: 999px;
		font-size: 12px;
		font-weight: 600;
	}

	.visibility-badge.public {
		background: rgba(59, 130, 246, 0.15);
		color: #93c5fd;
		border: 1px solid rgba(59, 130, 246, 0.25);
	}

	.visibility-badge.private {
		background: rgba(244, 114, 182, 0.15);
		color: #fbcfe8;
		border: 1px solid rgba(244, 114, 182, 0.25);
	}

	.owner-actions {
		display: flex;
		gap: 10px;
	}

	.edit-btn,
	.delete-btn {
		padding: 10px 16px;
		border-radius: 12px;
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
		transition: 0.2s;
	}

	.fav-btn-detail {
		padding: 10px 16px;
		border-radius: 12px;
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
		transition: 0.2s;
		background: rgba(244, 63, 94, 0.08);
		border: 1px solid rgba(244, 63, 94, 0.2);
		color: #fda4af;
	}

	.fav-btn-detail:hover {
		background: rgba(244, 63, 94, 0.15);
	}

	.fav-btn-detail.active {
		background: rgba(244, 63, 94, 0.95);
		border-color: rgba(244, 63, 94, 0.5);
		color: white;
		box-shadow: 0 4px 16px rgba(244, 63, 94, 0.3);
	}

	.edit-btn {
		background: rgba(34, 197, 94, 0.1);
		border: 1px solid rgba(34, 197, 94, 0.2);
		color: #4ade80;
	}

	.edit-btn:hover {
		background: rgba(34, 197, 94, 0.18);
	}

	.delete-btn {
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		color: #f87171;
	}

	.delete-btn:hover:not(:disabled) {
		background: rgba(239, 68, 68, 0.18);
	}

	.delete-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.hero-body h1 {
		font-size: 48px;
		margin: 0 0 16px;
		line-height: 1.05;
		font-weight: 900;
		letter-spacing: -2px;
	}

	.hero-desc {
		color: #cbd5e1;
		font-size: 16px;
		line-height: 1.7;
		margin: 0 0 24px;
	}

	.hero-stats {
		display: flex;
		flex-wrap: wrap;
		gap: 24px;
		padding: 20px 0;
		border-top: 1px solid rgba(255, 255, 255, 0.06);
		border-bottom: 1px solid rgba(255, 255, 255, 0.06);
	}

	.stat {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.stat-label {
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: #64748b;
	}

	.stat-value {
		font-size: 16px;
		font-weight: 700;
		color: white;
	}

	.stat-sub {
		font-size: 13px;
		color: #94a3b8;
		font-weight: 500;
	}

	.tag-row {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		margin-top: 20px;
	}

	.tag-pill {
		padding: 6px 12px;
		border-radius: 999px;
		border: 1px solid rgba(255, 255, 255, 0.1);
		background: rgba(255, 255, 255, 0.04);
		color: #d1fae5;
		font-size: 12px;
		font-weight: 600;
	}

	.rating-box {
		display: flex;
		align-items: center;
		gap: 16px;
		margin-top: 24px;
		flex-wrap: wrap;
	}

	.rating-label {
		font-size: 14px;
		color: #94a3b8;
		font-weight: 600;
	}

	.stars {
		display: flex;
		gap: 4px;
	}

	.star-btn {
		background: transparent;
		border: none;
		color: #475569;
		font-size: 28px;
		cursor: pointer;
		padding: 4px;
		line-height: 1;
		transition: color 0.15s, transform 0.15s;
	}

	.star-btn.filled {
		color: #facc15;
	}

	.star-btn:hover {
		transform: scale(1.15);
	}

	/* DETAIL GRID */
	.detail-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 24px;
	}

	.detail-card {
		padding: 32px;
	}

	.detail-card h2 {
		margin: 0 0 20px;
		font-size: 24px;
		font-weight: 800;
	}

	.ingredient-list,
	.step-list {
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.ingredient-list li {
		padding: 12px 0;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		color: #e2e8f0;
		font-size: 15px;
	}

	.ingredient-list li:last-child {
		border-bottom: none;
	}

	.amount {
		display: inline-block;
		min-width: 80px;
		color: #4ade80;
		font-weight: 700;
		margin-right: 8px;
	}

	.step-list li {
		display: flex;
		align-items: flex-start;
		gap: 14px;
		padding: 14px 0;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		color: #e2e8f0;
		font-size: 15px;
		line-height: 1.6;
	}

	.step-list li:last-child {
		border-bottom: none;
	}

	.step-num {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 30px;
		height: 30px;
		border-radius: 50%;
		background: rgba(74, 222, 128, 0.1);
		border: 1px solid rgba(74, 222, 128, 0.2);
		color: #4ade80;
		font-size: 13px;
		font-weight: 700;
	}

	.step-text {
		flex: 1;
		padding-top: 4px;
	}

	.empty {
		color: #64748b;
		font-style: italic;
		margin: 0;
	}

	/* STATUS */
	.status-card {
		padding: 60px 40px;
		border-radius: 30px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.07);
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
	}

	.status-card.error {
		border-color: rgba(239, 68, 68, 0.3);
		background: rgba(239, 68, 68, 0.06);
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 3px solid rgba(74, 222, 128, 0.15);
		border-top-color: #4ade80;
		border-radius: 50%;
		animation: spin 0.9s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.back-link {
		margin-top: 8px;
		color: #4ade80;
		text-decoration: none;
		font-weight: 600;
	}

	.inline-error {
		padding: 14px 18px;
		border-radius: 14px;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		color: #fca5a5;
		margin-bottom: 16px;
	}

	/* EDIT MODE */
	.edit-card {
		padding: 36px;
	}

	.edit-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		margin-bottom: 24px;
		flex-wrap: wrap;
	}

	.edit-header h1 {
		font-size: 32px;
		margin: 0;
		font-weight: 900;
	}

	.edit-actions {
		display: flex;
		gap: 10px;
	}

	.save-btn {
		padding: 12px 22px;
		border-radius: 14px;
		background: linear-gradient(to right, #16a34a, #065f46);
		border: none;
		color: white;
		font-weight: 700;
		font-size: 14px;
		cursor: pointer;
		font-family: inherit;
	}

	.save-btn:disabled,
	.cancel-btn-small:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.cancel-btn-small {
		padding: 12px 22px;
		border-radius: 14px;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		color: #94a3b8;
		font-weight: 600;
		font-size: 14px;
		cursor: pointer;
		font-family: inherit;
	}

	.edit-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 16px;
		margin-bottom: 28px;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.field.full {
		grid-column: 1 / -1;
	}

	.field label {
		font-size: 12px;
		font-weight: 700;
		color: #94a3b8;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	input,
	select,
	textarea {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 12px;
		padding: 12px 16px;
		color: white;
		font-size: 14px;
		font-family: inherit;
		outline: none;
		width: 100%;
		box-sizing: border-box;
	}

	input:focus,
	select:focus,
	textarea:focus {
		border-color: rgba(74, 222, 128, 0.3);
	}

	textarea {
		resize: vertical;
	}

	.toggle-group {
		display: flex;
		gap: 8px;
		padding: 6px;
		border-radius: 14px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.06);
	}

	.toggle-btn {
		flex: 1;
		padding: 10px 16px;
		border-radius: 10px;
		border: 1px solid transparent;
		background: transparent;
		color: #94a3b8;
		cursor: pointer;
		font-size: 13px;
		font-weight: 600;
		font-family: inherit;
		transition: all 0.2s;
	}

	.toggle-btn.active {
		background: rgba(34, 197, 94, 0.15);
		color: #4ade80;
		border-color: rgba(34, 197, 94, 0.3);
	}

	.edit-image-preview {
		position: relative;
		aspect-ratio: 16 / 9;
		border-radius: 12px;
		overflow: hidden;
		margin-bottom: 8px;
		border: 1px solid rgba(255, 255, 255, 0.08);
	}

	.edit-image-preview img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.image-remove {
		position: absolute;
		top: 8px;
		right: 8px;
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: rgba(0, 0, 0, 0.7);
		border: 1px solid rgba(255, 255, 255, 0.15);
		color: white;
		cursor: pointer;
	}

	.edit-section {
		padding-top: 24px;
		border-top: 1px solid rgba(255, 255, 255, 0.06);
		margin-top: 24px;
	}

	.section-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 14px;
	}

	.section-row h3 {
		margin: 0;
		font-size: 18px;
		font-weight: 700;
	}

	.add-btn {
		padding: 8px 14px;
		border-radius: 10px;
		background: rgba(34, 197, 94, 0.1);
		border: 1px solid rgba(34, 197, 94, 0.2);
		color: #4ade80;
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
	}

	.list-item {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 8px;
	}

	.list-num {
		flex-shrink: 0;
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: rgba(74, 222, 128, 0.1);
		border: 1px solid rgba(74, 222, 128, 0.2);
		color: #4ade80;
		font-size: 12px;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.x-btn {
		flex-shrink: 0;
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: rgba(239, 68, 68, 0.08);
		border: 1px solid rgba(239, 68, 68, 0.15);
		color: #f87171;
		cursor: pointer;
		font-size: 11px;
		font-family: inherit;
	}

	@media (max-width: 900px) {
		.content {
			padding: 32px 20px 60px;
		}

		.detail-grid {
			grid-template-columns: 1fr;
		}

		.hero-body {
			padding: 24px;
		}

		.hero-body h1 {
			font-size: 32px;
		}

		.hero-image {
			height: 240px;
		}

		.edit-grid {
			grid-template-columns: 1fr;
		}

		.edit-card {
			padding: 24px;
		}
	}
</style>

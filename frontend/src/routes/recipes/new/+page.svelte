<script lang="ts">
	import { goto } from '$app/navigation';
	import { createRecipe } from '$lib/api';

	// In runes mode (vom svelte.config.js erzwungen) MÜSSEN reaktive
	// Werte mit $state() deklariert werden, sonst aktualisiert sich die UI nicht.
	let title = $state('');
	let description = $state('');
	let category = $state('');
	let time = $state('');
	let imageUrl = $state('');
	let imagePreview = $state('');
	let tags = $state('');
	let isPublic = $state(true);
	let errorMessage = $state('');
	let isSaving = $state(false);

	let ingredients = $state<string[]>(['']);
	let steps = $state<string[]>(['']);

	function addIngredient() {
		ingredients = [...ingredients, ''];
	}

	function removeIngredient(index: number) {
		ingredients = ingredients.filter((_, i) => i !== index);
	}

	function addStep() {
		steps = [...steps, ''];
	}

	function removeStep(index: number) {
		steps = steps.filter((_, i) => i !== index);
	}

	/**
	 * Bild auf max. 1280px Längsseite verkleinern und als JPEG mit ~80%
	 * Qualität encodieren. Verhindert dass 5 MB Handyfotos als 7 MB Base64
	 * in der DB landen.
	 */
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

	async function handleImageFile(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;

		// Hartes Limit auf 10 MB Originalgröße — wir komprimieren danach sowieso.
		if (file.size > 10 * 1024 * 1024) {
			errorMessage = 'Bild ist zu groß (max. 10 MB Originaldatei).';
			target.value = '';
			return;
		}

		try {
			const dataUrl = await compressImage(file);
			imageUrl = dataUrl;
			imagePreview = dataUrl;
			errorMessage = '';
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'Bild konnte nicht verarbeitet werden.';
		}
	}

	function clearImage() {
		imageUrl = '';
		imagePreview = '';
	}

	// Wenn der Nutzer eine URL eingibt, soll auch das Vorschaubild sich aktualisieren
	function onImageUrlInput(value: string) {
		imageUrl = value;
		imagePreview = value;
	}

	async function submitRecipe() {
		errorMessage = '';

		if (!title.trim()) {
			errorMessage = 'Bitte gib einen Titel ein.';
			return;
		}

		isSaving = true;

		const payload = {
			title: title.trim(),
			description: description.trim(),
			category: category || undefined,
			prep_time_minutes: time ? Number(time) : undefined,
			servings: undefined,
			difficulty: undefined,
			image_url: imageUrl || undefined,
			is_public: isPublic === true,
			ingredients: ingredients
				.filter((item) => item.trim().length > 0)
				.map((name) => ({ name: name.trim(), amount: undefined, unit: undefined })),
			steps: steps
				.filter((item) => item.trim().length > 0)
				.map((instruction, index) => ({ step_number: index + 1, instruction: instruction.trim() })),
			tags: tags
				.split(',')
				.map((tag) => tag.trim())
				.filter((tag) => tag.length > 0),
		};

		try {
			const created = await createRecipe(payload);
			// Direkt zur Detailseite des neuen Rezepts, statt zur Liste:
			if (created?.id) {
				await goto(`/recipes/${created.id}`);
			} else {
				await goto('/recipes');
			}
		} catch (error: unknown) {
			if (error instanceof Error) {
				errorMessage = error.message;
			} else {
				errorMessage = 'Fehler beim Erstellen des Rezepts.';
			}
		} finally {
			isSaving = false;
		}
	}
</script>

<div class="page-container">
	<!-- Background -->
	<div class="background-blur blur-1"></div>
	<div class="background-blur blur-2"></div>

	<!-- Navigation -->
	<nav class="glass-nav">
		<a href="/" class="logo">
			Smart<span>Kitchen</span>
		</a>

		<div class="nav-actions">
			<a href="/" class="back-btn">
				← Dashboard
			</a>
		</div>
	</nav>

	<!-- Main Content -->
	<main class="content">

		<!-- Header -->
		<div class="page-header">
			<div class="badge">
				🍽️ Rezept erstellen
			</div>

			<h1>Neues <span>Rezept</span></h1>

			<p>Teile dein Lieblingsgericht mit der Community.</p>
		</div>

		<!-- Error Message -->
		{#if errorMessage}
			<div class="error-box" role="alert">
				⚠ {errorMessage}
			</div>
		{/if}

		<!-- Form -->
		<div class="form-wrapper">

			<!-- Main Info Card -->
			<div class="glass-card">
				<div class="card-header">
					<div>
						<h2>Grundinformationen</h2>
						<p>Titel, Kategorie und weitere Details</p>
					</div>
				</div>

				<div class="two-col">
					<!-- Left Column -->
					<div class="field-group">
						<div class="field">
							<label for="title-input">Titel</label>
							<input
								id="title-input"
								bind:value={title}
								type="text"
								placeholder="z.B. Cremige Carbonara"
							/>
						</div>

						<div class="field">
							<label for="category-input">Kategorie</label>
							<select id="category-input" bind:value={category}>
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
							<label for="tags-input">Tags</label>
							<input
								id="tags-input"
								bind:value={tags}
								type="text"
								placeholder="z. B. schnell, vegan, einfach"
							/>
							<p class="hint">Getrennt durch Kommas eingeben.</p>
						</div>

						<!-- Visibility Toggle (echtes Toggle statt Radio) -->
						<div class="field">
							<label for="visibility-toggle">Rezept sichtbar</label>
							<div class="toggle-group" id="visibility-toggle">
								<button
									type="button"
									class="toggle-btn"
									class:active={isPublic === true}
									onclick={() => (isPublic = true)}
								>
									🌐 Öffentlich
								</button>
								<button
									type="button"
									class="toggle-btn"
									class:active={isPublic === false}
									onclick={() => (isPublic = false)}
								>
									🔒 Privat
								</button>
							</div>
						</div>

						<div class="field-row">
							<div class="field">
								<label for="time-input">Kochzeit (Min)</label>
								<input
									id="time-input"
									bind:value={time}
									type="number"
									placeholder="30"
								/>
							</div>
						</div>
					</div>

					<!-- Right Column -->
					<div class="field-group">
						<div class="field">
							<label for="desc-input">Beschreibung</label>
							<textarea
								id="desc-input"
								bind:value={description}
								rows="5"
								placeholder="Beschreibe dein Rezept..."
							></textarea>
						</div>

						<!-- Image Upload -->
						<div class="field">
							<label>Bild</label>
							<div class="image-uploader">
								{#if imagePreview}
									<div class="image-preview">
										<img src={imagePreview} alt="Vorschau" />
										<button type="button" class="image-remove" onclick={clearImage} aria-label="Bild entfernen">
											✕
										</button>
									</div>
								{:else}
									<label class="image-dropzone" for="image-file-input">
										<div class="dropzone-icon">📷</div>
										<div class="dropzone-text">Klicke um ein Bild auszuwählen</div>
										<div class="dropzone-hint">JPG, PNG · max. 2 MB</div>
									</label>
								{/if}

								<input
									id="image-file-input"
									type="file"
									accept="image/*"
									onchange={handleImageFile}
									style="display: none;"
								/>

								<div class="image-url-row">
									<input
										type="text"
										placeholder="...oder Bild-URL einfügen (https://...)"
										value={imageUrl.startsWith('data:') ? '' : imageUrl}
										oninput={(e) => onImageUrlInput((e.target as HTMLInputElement).value)}
									/>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Ingredients Card -->
			<div class="glass-card">
				<div class="card-header">
					<div>
						<h2>Zutaten</h2>
						<p>Was wird für das Rezept benötigt?</p>
					</div>

					<button class="add-btn" onclick={addIngredient} type="button">
						+ Zutat hinzufügen
					</button>
				</div>

				<div class="list-group">
					{#each ingredients as ingredient, index}
						<div class="list-item">
							<span class="item-number">{index + 1}</span>

							<input
								bind:value={ingredients[index]}
								type="text"
								placeholder={`Zutat ${index + 1}, z.B. 200g Pasta`}
							/>

							{#if ingredients.length > 1}
								<button
									class="remove-btn"
									onclick={() => removeIngredient(index)}
									type="button"
									aria-label="Zutat entfernen"
								>
									✕
								</button>
							{/if}
						</div>
					{/each}
				</div>
			</div>

			<!-- Steps Card -->
			<div class="glass-card">
				<div class="card-header">
					<div>
						<h2>Zubereitung</h2>
						<p>Schritt für Schritt zum Rezept</p>
					</div>

					<button class="add-btn" onclick={addStep} type="button">
						+ Schritt hinzufügen
					</button>
				</div>

				<div class="list-group">
					{#each steps as step, index}
						<div class="list-item step-item">
							<span class="item-number step-number">{index + 1}</span>

							<textarea
								bind:value={steps[index]}
								rows="3"
								placeholder={`Schritt ${index + 1}: Was wird hier gemacht?`}
							></textarea>

							{#if steps.length > 1}
								<button
									class="remove-btn"
									onclick={() => removeStep(index)}
									type="button"
									aria-label="Schritt entfernen"
								>
									✕
								</button>
							{/if}
						</div>
					{/each}
				</div>
			</div>

			<!-- Submit -->
			<div class="submit-row">
				<a href="/" class="cancel-btn">Abbrechen</a>

				<button class="submit-btn" onclick={submitRecipe} type="button" disabled={isSaving}>
					{isSaving ? 'Wird gespeichert...' : 'Rezept veröffentlichen →'}
				</button>
			</div>

		</div>
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

	.page-container {
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

	/* NAV */
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
		text-decoration: none;
		color: white;
	}

	.logo span {
		color: #22c55e;
	}

	.nav-actions {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.back-btn {
		padding: 12px 18px;
		border-radius: 16px;
		background: rgba(255, 255, 255, 0.06);
		border: 1px solid rgba(255, 255, 255, 0.08);
		color: white;
		text-decoration: none;
		font-size: 14px;
		font-weight: 600;
		transition: 0.3s;
	}

	.back-btn:hover {
		background: rgba(255, 255, 255, 0.1);
	}

	/* CONTENT */
	.content {
		position: relative;
		z-index: 1;
		max-width: 1100px;
		margin: 0 auto;
		padding: 50px 32px 100px;
	}

	/* HEADER */
	.page-header {
		margin-bottom: 30px;
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

	.page-header h1 {
		font-size: 64px;
		line-height: 0.95;
		font-weight: 900;
		margin: 0;
		letter-spacing: -3px;
	}

	.page-header h1 span {
		background: linear-gradient(to right, #4ade80, #065f46);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
	}

	.page-header p {
		margin-top: 20px;
		font-size: 18px;
		color: #94a3b8;
	}

	/* ERROR BOX */
	.error-box {
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		color: #fca5a5;
		padding: 16px 20px;
		border-radius: 16px;
		margin-bottom: 24px;
		font-size: 15px;
	}

	/* FORM */
	.form-wrapper {
		display: flex;
		flex-direction: column;
		gap: 28px;
	}

	/* GLASS CARD */
	.glass-card {
		border-radius: 32px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.07);
		backdrop-filter: blur(20px);
		padding: 36px;
	}

	.card-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16px;
		margin-bottom: 32px;
	}

	.card-header h2 {
		font-size: 26px;
		font-weight: 800;
		margin: 0;
	}

	.card-header p {
		margin: 6px 0 0;
		color: #64748b;
		font-size: 14px;
	}

	/* GRID */
	.two-col {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 28px;
	}

	.field-group {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.field-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 16px;
	}

	/* TOGGLE BUTTONS (statt Radio) */
	.toggle-group {
		display: flex;
		gap: 10px;
		padding: 6px;
		border-radius: 16px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.06);
	}

	.toggle-btn {
		flex: 1;
		padding: 12px 18px;
		border-radius: 12px;
		border: 1px solid transparent;
		background: transparent;
		color: #94a3b8;
		cursor: pointer;
		font-size: 14px;
		font-weight: 600;
		font-family: inherit;
		transition: all 0.2s;
	}

	.toggle-btn:hover {
		background: rgba(255, 255, 255, 0.05);
		color: white;
	}

	.toggle-btn.active {
		background: rgba(34, 197, 94, 0.15);
		color: #4ade80;
		border-color: rgba(34, 197, 94, 0.3);
		box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);
	}

	/* FIELDS */
	.field {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.hint {
		margin: 0;
		font-size: 12px;
		color: #64748b;
		text-transform: none;
		letter-spacing: normal;
		font-weight: 400;
	}

	label {
		font-size: 13px;
		font-weight: 600;
		color: #94a3b8;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	input,
	select,
	textarea {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 16px;
		padding: 14px 18px;
		color: white;
		font-size: 15px;
		font-family: inherit;
		outline: none;
		transition: border-color 0.2s, background 0.2s;
		width: 100%;
		box-sizing: border-box;
	}

	input::placeholder,
	textarea::placeholder {
		color: #3f4d5c;
	}

	input:focus,
	select:focus,
	textarea:focus {
		border-color: rgba(74, 222, 128, 0.3);
		background: rgba(255, 255, 255, 0.07);
	}

	select {
		cursor: pointer;
		appearance: none;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: right 16px center;
	}

	select option {
		background: #0f1923;
		color: white;
	}

	textarea {
		resize: vertical;
		line-height: 1.6;
	}

	/* IMAGE UPLOADER */
	.image-uploader {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.image-dropzone {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 8px;
		padding: 32px 20px;
		border: 2px dashed rgba(255, 255, 255, 0.1);
		border-radius: 16px;
		background: rgba(255, 255, 255, 0.02);
		cursor: pointer;
		transition: all 0.2s;
		text-transform: none;
		letter-spacing: normal;
	}

	.image-dropzone:hover {
		border-color: rgba(74, 222, 128, 0.4);
		background: rgba(34, 197, 94, 0.04);
	}

	.dropzone-icon {
		font-size: 36px;
	}

	.dropzone-text {
		color: #cbd5e1;
		font-size: 14px;
		font-weight: 600;
	}

	.dropzone-hint {
		color: #64748b;
		font-size: 12px;
	}

	.image-preview {
		position: relative;
		border-radius: 16px;
		overflow: hidden;
		border: 1px solid rgba(255, 255, 255, 0.08);
		aspect-ratio: 16 / 9;
	}

	.image-preview img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.image-remove {
		position: absolute;
		top: 10px;
		right: 10px;
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: rgba(0, 0, 0, 0.7);
		border: 1px solid rgba(255, 255, 255, 0.15);
		color: white;
		cursor: pointer;
		font-size: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.image-url-row input {
		font-size: 14px;
	}

	/* LIST ITEMS */
	.list-group {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.list-item {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.step-item {
		align-items: flex-start;
	}

	.item-number {
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		width: 34px;
		height: 34px;
		border-radius: 50%;
		background: rgba(74, 222, 128, 0.1);
		border: 1px solid rgba(74, 222, 128, 0.2);
		color: #4ade80;
		font-size: 13px;
		font-weight: 700;
	}

	.step-number {
		margin-top: 14px;
	}

	.remove-btn {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 34px;
		height: 34px;
		border-radius: 50%;
		background: rgba(239, 68, 68, 0.08);
		border: 1px solid rgba(239, 68, 68, 0.15);
		color: #f87171;
		cursor: pointer;
		font-size: 12px;
		transition: 0.2s;
	}

	.remove-btn:hover {
		background: rgba(239, 68, 68, 0.18);
	}

	/* ADD BUTTON */
	.add-btn {
		flex-shrink: 0;
		padding: 12px 20px;
		border-radius: 16px;
		background: rgba(34, 197, 94, 0.1);
		border: 1px solid rgba(34, 197, 94, 0.2);
		color: #4ade80;
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		transition: 0.2s;
		white-space: nowrap;
	}

	.add-btn:hover {
		background: rgba(34, 197, 94, 0.18);
	}

	/* SUBMIT ROW */
	.submit-row {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 16px;
		padding-top: 8px;
	}

	.cancel-btn {
		padding: 16px 26px;
		border-radius: 18px;
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		color: #94a3b8;
		text-decoration: none;
		font-size: 16px;
		font-weight: 600;
		transition: 0.3s;
	}

	.cancel-btn:hover {
		background: rgba(255, 255, 255, 0.09);
		color: white;
	}

	.submit-btn {
		padding: 18px 36px;
		border-radius: 18px;
		background: linear-gradient(to right, #16a34a, #065f46);
		border: none;
		color: white;
		font-size: 16px;
		font-weight: 700;
		cursor: pointer;
		transition: 0.3s;
		box-shadow: 0 10px 30px rgba(22, 163, 74, 0.3);
	}

	.submit-btn:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 16px 40px rgba(22, 163, 74, 0.4);
	}

	.submit-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	/* MOBILE */
	@media (max-width: 900px) {
		.glass-nav {
			padding: 20px;
		}

		.content {
			padding: 32px 20px 100px;
		}

		.page-header h1 {
			font-size: 44px;
		}

		.two-col {
			grid-template-columns: 1fr;
		}

		.field-row {
			grid-template-columns: 1fr;
		}

		.glass-card {
			padding: 24px 20px;
		}

		.card-header {
			flex-direction: column;
			align-items: flex-start;
		}

		.submit-row {
			flex-direction: column-reverse;
		}

		.submit-btn,
		.cancel-btn {
			width: 100%;
			text-align: center;
		}
	}
</style>

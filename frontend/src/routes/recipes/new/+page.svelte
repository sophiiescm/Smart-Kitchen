<script lang="ts">
	import { goto } from '$app/navigation';
	import { createRecipe } from '$lib/api';

	let title = '';
	let description = '';
	let category = '';
	let time = '';
	let image = '';
	let tags = '';
	let isPublic: string = 'true';
	let errorMessage = '';
	let isSaving = false;

	let ingredients: string[] = [''];
	let steps: string[] = [''];

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

	async function submitRecipe() {
		errorMessage = '';
		isSaving = true;

		const payload = {
			title,
			description,
			category,
			prep_time_minutes: time ? Number(time) : undefined,
			servings: undefined,
			difficulty: undefined,
			is_public: isPublic === true || isPublic === 'true',
			ingredients: ingredients
				.filter((item) => item.trim().length > 0)
				.map((name) => ({ name, amount: undefined, unit: undefined })),
			steps: steps
				.filter((item) => item.trim().length > 0)
				.map((instruction, index) => ({ step_number: index + 1, instruction })),
			tags: tags
				.split(',')
				.map((tag) => tag.trim())
				.filter((tag) => tag.length > 0),
		};

		try {
			await createRecipe(payload);
			goto('/recipes');
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

		<!-- Form -->
		<div class="form-wrapper">

			<!-- Main Info Card -->
			<div class="glass-card">
				<div class="card-header">
					<h2>Grundinformationen</h2>
					<p>Titel, Kategorie und weitere Details</p>
				</div>

				<div class="two-col">
					<!-- Left Column -->
					<div class="field-group">
						<div class="field">
							<label>Titel</label>
							<input
								bind:value={title}
								type="text"
								placeholder="z.B. Cremige Carbonara"
							/>
						</div>

						<div class="field">
							<label>Kategorie</label>
							<select bind:value={category}>
								<option value="">Kategorie wählen</option>
								<option>Pasta</option>
								<option>Dessert</option>
								<option>Frühstück</option>
								<option>Vegetarisch</option>
							</select>
						</div>

						<div class="field">
							<label>Tags</label>
							<input
								bind:value={tags}
								type="text"
								placeholder="z. B. schnell, vegan, einfach"
							/>
							<p class="hint">Getrennt durch Kommas eingeben.</p>
						</div>

<div class="field field-inline">
				<label>Rezept sichtbar</label>
				<div class="toggle-group">
								<label class="radio-pill">
									<input type="radio" bind:group={isPublic} value="true" />
									Öffentlich
								</label>
								<label class="radio-pill">
									<input type="radio" bind:group={isPublic} value="false" />
									Privat
								</label>
							</div>
						</div>

						<div class="field-row">
							<div class="field">
								<label>Kochzeit (Min)</label>
								<input
									bind:value={time}
									type="number"
									placeholder="30"
								/>
							</div>

							<div class="field">
								<label>Bild URL</label>
								<input
									bind:value={image}
									type="text"
									placeholder="https://..."
								/>
							</div>
						</div>
					</div>

					<!-- Right Column -->
					<div class="field">
						<label>Beschreibung</label>
						<textarea
							bind:value={description}
							rows="9"
							placeholder="Beschreibe dein Rezept..."
						></textarea>
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

				<button class="submit-btn" onclick={submitRecipe} type="button">
					Rezept veröffentlichen →
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
		margin-bottom: 50px;
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

	.field-inline {
		display: flex;
		align-items: center;
		gap: 22px;
	}

	.field-inline > label {
		margin-bottom: 0;
		white-space: nowrap;
	}

	.toggle-group {
		display: flex;
		flex-wrap: wrap;
		gap: 14px;
		align-items: center;
	}

	.radio-pill {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		flex: 1 1 0;
		min-width: 140px;
		gap: 10px;
		padding: 12px 18px;
		border-radius: 16px;
		border: 1px solid rgba(255, 255, 255, 0.12);
		background: rgba(255, 255, 255, 0.05);
		color: white;
		cursor: pointer;
		transition: background 0.2s, border-color 0.2s, transform 0.08s;
	}

	.radio-pill:hover {
		background: rgba(255, 255, 255, 0.1);
	}

	.radio-pill input {
		accent-color: #4ade80;
	}

	/* FIELDS */

	.field {
		display: flex;
		flex-direction: column;
		gap: 10px;
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

	.submit-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 16px 40px rgba(22, 163, 74, 0.4);
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
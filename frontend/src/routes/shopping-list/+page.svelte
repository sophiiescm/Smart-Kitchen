<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import {
		getShoppingList,
		addShoppingListItem,
		updateShoppingListItem,
		deleteShoppingListItem,
		clearCheckedItems,
		clearAllItems,
		isLoggedIn,
		type ShoppingListItem,
	} from '$lib/api';

	let items = $state<ShoppingListItem[]>([]);
	let loading = $state(true);
	let errorMessage = $state('');
	let newItemName = $state('');
	// Number-Input → Svelte coerced auf number. Daher number|null statt string.
	let newItemAmount = $state<number | null>(null);
	let newItemUnit = $state('');
	let isAdding = $state(false);
	let isWorking = $state(false);

	// Inline-Edit-State
	let editingId = $state<number | null>(null);
	let editName = $state('');
	let editAmount = $state<number | null>(null);
	let editUnit = $state('');
	let isSavingEdit = $state(false);

	onMount(async () => {
		if (!isLoggedIn()) {
			goto('/auth/login?redirect=/shopping-list');
			return;
		}
		await reload();
	});

	async function reload() {
		loading = true;
		errorMessage = '';
		try {
			items = await getShoppingList();
		} catch (err) {
			console.error(err);
			errorMessage = err instanceof Error ? err.message : 'Liste konnte nicht geladen werden.';
		} finally {
			loading = false;
		}
	}

	// Gruppierung nach Kategorie. Abgehakte werden separat unten gerendert.
	type Group = { category: string; items: ShoppingListItem[] };
	let openGroups = $derived(
		Object.entries(
			items
				.filter((i) => !i.is_checked)
				.reduce<Record<string, ShoppingListItem[]>>((acc, item) => {
					const cat = item.category || 'Sonstiges';
					if (!acc[cat]) acc[cat] = [];
					acc[cat].push(item);
					return acc;
				}, {}),
		)
			.map(([category, items]): Group => ({ category, items }))
			.sort((a, b) => a.category.localeCompare(b.category, 'de')),
	);
	let checkedItems = $derived(items.filter((i) => i.is_checked));

	async function handleToggle(item: ShoppingListItem) {
		const previous = item.is_checked;
		// optimistic update
		items = items.map((i) => (i.id === item.id ? { ...i, is_checked: !previous } : i));
		try {
			await updateShoppingListItem(item.id, { is_checked: !previous });
		} catch (err) {
			console.error(err);
			items = items.map((i) => (i.id === item.id ? { ...i, is_checked: previous } : i));
			errorMessage = 'Status konnte nicht aktualisiert werden.';
		}
	}

	async function handleDelete(item: ShoppingListItem) {
		const snapshot = items;
		items = items.filter((i) => i.id !== item.id);
		try {
			await deleteShoppingListItem(item.id);
		} catch (err) {
			console.error(err);
			items = snapshot;
			errorMessage = 'Item konnte nicht gelöscht werden.';
		}
	}

	async function handleAdd(e: SubmitEvent) {
		e.preventDefault();
		const name = String(newItemName ?? '').trim();
		const unit = String(newItemUnit ?? '').trim();
		if (!name) return;

		isAdding = true;
		errorMessage = '';
		try {
			// newItemAmount kann number, null oder string sein (je nach Browser/Eingabe)
			let amount: number | undefined = undefined;
			if (newItemAmount !== null && newItemAmount !== undefined && String(newItemAmount) !== '') {
				const n = Number(newItemAmount);
				if (!Number.isNaN(n)) amount = n;
			}
			await addShoppingListItem(name, amount, unit || undefined);
			newItemName = '';
			newItemAmount = null;
			newItemUnit = '';
			await reload();
		} catch (err) {
			console.error(err);
			errorMessage = err instanceof Error ? err.message : 'Konnte nicht hinzugefügt werden.';
		} finally {
			isAdding = false;
		}
	}

	async function handleClearChecked() {
		if (!confirm('Alle abgehakten Items löschen?')) return;
		isWorking = true;
		try {
			await clearCheckedItems();
			await reload();
		} finally {
			isWorking = false;
		}
	}

	async function handleClearAll() {
		if (!confirm('Komplette Einkaufsliste leeren?')) return;
		isWorking = true;
		try {
			await clearAllItems();
			await reload();
		} finally {
			isWorking = false;
		}
	}

	function formatAmount(item: ShoppingListItem): string {
		if (item.amount === null || item.amount === undefined) return '';
		// hübsche Anzeige: keine Nachkomma wenn ganz, sonst max 2 Nachkommastellen
		const a = Math.round(item.amount * 100) / 100;
		const formatted = Number.isInteger(a) ? String(a) : a.toFixed(2).replace(/\.?0+$/, '');
		return item.unit ? `${formatted} ${item.unit}` : formatted;
	}

	/** Einheitliche Anzeige: "[Menge Einheit] Name" — z.B. "10 ml Öl" oder "300g Steak" */
	function formatItemLabel(item: ShoppingListItem): string {
		const amt = formatAmount(item);
		return amt ? `${amt} ${item.name}` : item.name;
	}

	function startEdit(item: ShoppingListItem) {
		editingId = item.id;
		editName = item.name;
		editAmount = item.amount;
		editUnit = item.unit ?? '';
	}

	function cancelEdit() {
		editingId = null;
		editName = '';
		editAmount = null;
		editUnit = '';
	}

	async function saveEdit(item: ShoppingListItem) {
		const name = String(editName ?? '').trim();
		if (!name) {
			errorMessage = 'Name darf nicht leer sein.';
			return;
		}

		isSavingEdit = true;
		errorMessage = '';
		try {
			let amount: number | null = null;
			if (editAmount !== null && editAmount !== undefined && String(editAmount) !== '') {
				const n = Number(editAmount);
				if (!Number.isNaN(n)) amount = n;
			}
			const unit = String(editUnit ?? '').trim() || null;

			const updated = await updateShoppingListItem(item.id, {
				name,
				amount,
				unit,
			});
			// neue Kategorie kommt aus der Antwort (Backend re-kategorisiert bei Namensänderung)
			items = items.map((i) => (i.id === item.id ? updated : i));
			cancelEdit();
		} catch (err) {
			console.error(err);
			errorMessage = err instanceof Error ? err.message : 'Speichern fehlgeschlagen.';
		} finally {
			isSavingEdit = false;
		}
	}
</script>

<div class="page">
	<div class="bg-blur blur-1"></div>
	<div class="bg-blur blur-2"></div>

	<nav class="glass-nav">
		<a href="/" class="logo">Smart<span>Kitchen</span></a>
		<div class="nav-right">
			<a href="/recipes" class="back-btn">← Rezepte</a>
		</div>
	</nav>

	<main class="content">
		<header class="page-header">
			<div class="badge">🛒 Einkaufsliste</div>
			<h1>Deine <span>Liste</span></h1>
			<p class="subtitle">
				Zutaten aus Rezepten werden automatisch addiert. Eigene Items manuell ergänzen.
			</p>
		</header>

		{#if errorMessage}
			<div class="error-banner">⚠ {errorMessage}</div>
		{/if}

		<!-- Manuelles Hinzufügen -->
		<form class="add-row glass-card" onsubmit={handleAdd}>
			<input
				type="text"
				bind:value={newItemName}
				placeholder="z.B. Spülmittel oder Cherry-Tomaten"
				class="add-name"
				required
			/>
			<input
				type="number"
				bind:value={newItemAmount}
				placeholder="Menge"
				class="add-amount no-spinner"
				step="any"
				min="0"
			/>
			<input
				type="text"
				bind:value={newItemUnit}
				placeholder="Einheit"
				class="add-unit"
			/>
			<button type="submit" class="add-btn" disabled={isAdding || !newItemName.trim()}>
				{isAdding ? '...' : '+ Hinzufügen'}
			</button>
		</form>

		{#if loading}
			<div class="status-card">
				<div class="spinner"></div>
				<p>Lade Einkaufsliste...</p>
			</div>
		{:else if items.length === 0}
			<div class="empty">
				<div class="empty-icon">🛒</div>
				<h2>Deine Einkaufsliste ist leer</h2>
				<p>Füge oben ein Item hinzu oder öffne ein Rezept und klicke auf <strong>"Zutaten auf die Einkaufsliste"</strong>.</p>
				<a href="/recipes" class="empty-btn">Rezepte durchstöbern →</a>
			</div>
		{:else}
			<!-- Offene Items, gruppiert nach Kategorie -->
			{#each openGroups as group (group.category)}
				<section class="category-block glass-card">
					<h2 class="category-title">{group.category}</h2>
					<ul class="item-list">
						{#each group.items as item (item.id)}
							<li class="item">
								{#if editingId === item.id}
									<!-- Inline-Edit-Form: Name | Menge | Einheit | ✓ | ✕ -->
									<div class="edit-row">
										<input
											type="text"
											bind:value={editName}
											placeholder="Name"
											class="edit-name"
											onkeydown={(e) => {
												if (e.key === 'Enter') saveEdit(item);
												if (e.key === 'Escape') cancelEdit();
											}}
										/>
										<input
											type="number"
											bind:value={editAmount}
											placeholder="Menge"
											class="edit-amount no-spinner"
											step="any"
											min="0"
										/>
										<input
											type="text"
											bind:value={editUnit}
											placeholder="Einheit"
											class="edit-unit"
										/>
										<button
											type="button"
											class="save-edit-btn"
											onclick={() => saveEdit(item)}
											disabled={isSavingEdit}
											title="Speichern"
											aria-label="Speichern"
										>✓</button>
										<button
											type="button"
											class="cancel-edit-btn"
											onclick={cancelEdit}
											title="Abbrechen"
											aria-label="Abbrechen"
										>✕</button>
									</div>
								{:else}
									<label class="checkbox-wrap">
										<input
											type="checkbox"
											checked={item.is_checked}
											onchange={() => handleToggle(item)}
										/>
										<span class="checkmark"></span>
									</label>
									<div class="item-body">
										<span class="item-label">{formatItemLabel(item)}</span>
									</div>
									<button
										type="button"
										class="edit-btn"
										onclick={() => startEdit(item)}
										title="Bearbeiten"
										aria-label="Bearbeiten"
									>✎</button>
									<button
										type="button"
										class="del-btn"
										onclick={() => handleDelete(item)}
										title="Löschen"
										aria-label="Löschen"
									>✕</button>
								{/if}
							</li>
						{/each}
					</ul>
				</section>
			{/each}

			<!-- Abgehakte Items -->
			{#if checkedItems.length > 0}
				<section class="category-block glass-card done-block">
					<div class="done-header">
						<h2 class="category-title done">✓ Erledigt ({checkedItems.length})</h2>
						<button
							type="button"
							class="clear-checked-btn"
							onclick={handleClearChecked}
							disabled={isWorking}
						>
							Abgehakte löschen
						</button>
					</div>
					<ul class="item-list">
						{#each checkedItems as item (item.id)}
							<li class="item done">
								<label class="checkbox-wrap">
									<input
										type="checkbox"
										checked={item.is_checked}
										onchange={() => handleToggle(item)}
									/>
									<span class="checkmark"></span>
								</label>
								<div class="item-body">
									<span class="item-label">{formatItemLabel(item)}</span>
								</div>
								<button type="button" class="del-btn" onclick={() => handleDelete(item)} aria-label="Löschen">✕</button>
							</li>
						{/each}
					</ul>
				</section>
			{/if}

			<!-- Globaler "Liste leeren" Button -->
			<div class="bottom-actions">
				<button class="clear-all-btn" onclick={handleClearAll} disabled={isWorking}>
					🗑 Komplette Liste leeren
				</button>
			</div>
		{/if}
	</main>
</div>

<style>
	:global(body) {
		margin: 0;
		font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
		background: #04070a;
		color: white;
	}

	.page {
		position: relative;
		min-height: 100vh;
		background: #04070a;
		overflow: hidden;
	}

	.bg-blur {
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
		background: rgba(244, 114, 182, 0.1);
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

	.content {
		position: relative;
		z-index: 1;
		max-width: 800px;
		margin: 0 auto;
		padding: 48px 24px 100px;
	}

	.page-header {
		margin-bottom: 28px;
	}

	.badge {
		display: inline-flex;
		padding: 8px 14px;
		border-radius: 999px;
		background: rgba(34, 197, 94, 0.1);
		color: #4ade80;
		font-size: 13px;
		font-weight: 600;
		margin-bottom: 16px;
	}

	.page-header h1 {
		font-size: 52px;
		font-weight: 900;
		margin: 0;
		letter-spacing: -2px;
		line-height: 1.05;
	}
	.page-header h1 span {
		background: linear-gradient(to right, #4ade80, #065f46);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
	}

	.subtitle {
		margin: 16px 0 0;
		font-size: 16px;
		color: #94a3b8;
	}

	.error-banner {
		padding: 14px 18px;
		border-radius: 14px;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		color: #fca5a5;
		margin-bottom: 16px;
		font-size: 14px;
	}

	.glass-card {
		border-radius: 24px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.07);
		backdrop-filter: blur(20px);
	}

	/* ADD ROW */
	.add-row {
		display: grid;
		grid-template-columns: 2fr 1fr 1fr auto;
		gap: 8px;
		padding: 12px;
		margin-bottom: 24px;
	}

	.add-row input {
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 12px;
		padding: 12px 14px;
		color: white;
		font-size: 14px;
		outline: none;
		font-family: inherit;
	}
	.add-row input::placeholder {
		color: #64748b;
	}
	.add-row input:focus {
		border-color: rgba(74, 222, 128, 0.3);
	}

	.add-btn {
		padding: 12px 18px;
		border-radius: 12px;
		background: linear-gradient(to right, #16a34a, #065f46);
		border: none;
		color: white;
		font-weight: 700;
		font-size: 14px;
		cursor: pointer;
		font-family: inherit;
		white-space: nowrap;
	}
	.add-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* CATEGORY BLOCK */
	.category-block {
		padding: 20px 24px;
		margin-bottom: 16px;
	}

	.category-title {
		margin: 0 0 12px;
		font-size: 14px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: #4ade80;
	}

	.category-title.done {
		color: #64748b;
	}

	.done-block {
		opacity: 0.85;
	}

	.done-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 12px;
		flex-wrap: wrap;
		gap: 8px;
	}

	.clear-checked-btn {
		padding: 8px 14px;
		border-radius: 10px;
		background: rgba(239, 68, 68, 0.08);
		border: 1px solid rgba(239, 68, 68, 0.18);
		color: #f87171;
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
	}
	.clear-checked-btn:hover:not(:disabled) {
		background: rgba(239, 68, 68, 0.16);
	}

	/* ITEMS */
	.item-list {
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.item {
		display: flex;
		align-items: center;
		gap: 14px;
		padding: 12px 4px;
		border-bottom: 1px solid rgba(255, 255, 255, 0.04);
	}
	.item:last-child {
		border-bottom: none;
	}
	.item.done .item-name,
	.item.done .item-amount {
		text-decoration: line-through;
		color: #64748b;
	}

	.checkbox-wrap {
		position: relative;
		width: 22px;
		height: 22px;
		flex-shrink: 0;
		cursor: pointer;
	}
	.checkbox-wrap input {
		position: absolute;
		opacity: 0;
		cursor: pointer;
		width: 0;
		height: 0;
	}
	.checkmark {
		position: absolute;
		inset: 0;
		border-radius: 6px;
		border: 2px solid rgba(255, 255, 255, 0.2);
		background: transparent;
		transition: all 0.15s;
	}
	.checkbox-wrap input:checked + .checkmark {
		background: #22c55e;
		border-color: #22c55e;
	}
	.checkbox-wrap input:checked + .checkmark::after {
		content: '';
		position: absolute;
		top: 2px;
		left: 6px;
		width: 5px;
		height: 10px;
		border: solid white;
		border-width: 0 2px 2px 0;
		transform: rotate(45deg);
	}

	.item-body {
		flex: 1;
		display: flex;
		align-items: center;
		min-width: 0;
	}

	.item-label {
		font-size: 15px;
		font-weight: 500;
		color: #e2e8f0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.item.done .item-label {
		text-decoration: line-through;
		color: #64748b;
	}

	.edit-btn,
	.del-btn {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: transparent;
		border: 1px solid rgba(255, 255, 255, 0.08);
		color: #94a3b8;
		cursor: pointer;
		font-size: 12px;
		font-family: inherit;
		flex-shrink: 0;
		transition: 0.15s;
	}
	.edit-btn:hover {
		background: rgba(34, 197, 94, 0.15);
		border-color: rgba(34, 197, 94, 0.3);
		color: #4ade80;
	}
	.del-btn:hover {
		background: rgba(239, 68, 68, 0.15);
		border-color: rgba(239, 68, 68, 0.3);
		color: #fca5a5;
	}

	/* INLINE EDIT ROW: Name | Menge | Einheit | ✓ | ✕ */
	.edit-row {
		flex: 1;
		display: grid;
		grid-template-columns: 1fr 80px 80px auto auto;
		gap: 6px;
		align-items: center;
	}

	/* Pfeil-Spinner bei Number-Input ausblenden */
	.no-spinner::-webkit-outer-spin-button,
	.no-spinner::-webkit-inner-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}
	.no-spinner {
		-moz-appearance: textfield;
		appearance: textfield;
	}
	.edit-row input {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(74, 222, 128, 0.25);
		border-radius: 8px;
		padding: 8px 10px;
		color: white;
		font-size: 13px;
		font-family: inherit;
		outline: none;
		min-width: 0;
	}
	.edit-row input::placeholder {
		color: #64748b;
	}
	.edit-row input:focus {
		border-color: rgba(74, 222, 128, 0.5);
	}
	.save-edit-btn,
	.cancel-edit-btn {
		width: 30px;
		height: 30px;
		border-radius: 8px;
		border: none;
		cursor: pointer;
		font-size: 14px;
		font-weight: 700;
		font-family: inherit;
		flex-shrink: 0;
	}
	.save-edit-btn {
		background: rgba(34, 197, 94, 0.2);
		color: #4ade80;
	}
	.save-edit-btn:hover:not(:disabled) {
		background: rgba(34, 197, 94, 0.35);
	}
	.cancel-edit-btn {
		background: rgba(255, 255, 255, 0.08);
		color: #94a3b8;
	}
	.cancel-edit-btn:hover {
		background: rgba(255, 255, 255, 0.15);
	}

	/* EMPTY */
	.empty {
		padding: 60px 30px;
		text-align: center;
		border-radius: 24px;
		background: rgba(255, 255, 255, 0.03);
		border: 1px solid rgba(255, 255, 255, 0.06);
	}
	.empty-icon {
		font-size: 60px;
		margin-bottom: 12px;
	}
	.empty h2 {
		margin: 0 0 8px;
		font-size: 22px;
		font-weight: 700;
	}
	.empty p {
		color: #64748b;
		font-size: 14px;
		margin: 0 0 18px;
	}
	.empty-btn {
		display: inline-block;
		padding: 12px 22px;
		border-radius: 12px;
		background: rgba(34, 197, 94, 0.1);
		border: 1px solid rgba(34, 197, 94, 0.25);
		color: #4ade80;
		text-decoration: none;
		font-weight: 700;
		font-size: 13px;
	}

	.bottom-actions {
		margin-top: 24px;
		display: flex;
		justify-content: center;
	}

	.clear-all-btn {
		padding: 14px 28px;
		border-radius: 14px;
		background: rgba(239, 68, 68, 0.08);
		border: 1px solid rgba(239, 68, 68, 0.2);
		color: #fca5a5;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
	}
	.clear-all-btn:hover:not(:disabled) {
		background: rgba(239, 68, 68, 0.16);
	}

	/* STATUS */
	.status-card {
		padding: 60px 40px;
		text-align: center;
		border-radius: 24px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.07);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
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

	@media (max-width: 700px) {
		.add-row {
			grid-template-columns: 1fr 1fr;
		}
		.add-name {
			grid-column: 1 / -1;
		}
		.add-btn {
			grid-column: 1 / -1;
		}
		.page-header h1 {
			font-size: 36px;
		}
		.edit-row {
			grid-template-columns: 1fr 60px 60px auto auto;
			gap: 4px;
		}
		.edit-row input {
			padding: 6px 8px;
			font-size: 12px;
		}
	}
</style>

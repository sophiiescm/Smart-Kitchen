<script lang="ts">
	import { onMount } from 'svelte';
	import { Flame, Search, Star, Clock3, ChefHat, Plus } from 'lucide-svelte';

	let recipes = $state<any[]>([]);
	let loading = $state(true);
	let errorMessage = $state('');
	let search = $state('');
	let selectedCategory = $state('');

	const categories = ['Pasta', 'Dessert', 'Vegan', 'Vegetarisch', 'Fleisch'];

	onMount(async () => {
		try {
			const res = await fetch('http://localhost:8000/recipes');
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

	let filteredRecipes = $derived(
		recipes.filter((recipe) => {
			const matchesSearch =
				recipe.title?.toLowerCase().includes(search.toLowerCase()) ||
				recipe.description?.toLowerCase().includes(search.toLowerCase());
			const matchesCategory =
				selectedCategory === '' || recipe.category === selectedCategory;
			return matchesSearch && matchesCategory;
		})
	);
</script>

<section class="mx-auto max-w-7xl px-6 py-10">

	<!-- HEADER -->
	<div class="mb-10 flex items-end justify-between gap-6">
		<div class="max-w-2xl">
			<div class="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm text-gray-300">
				<Flame class="h-4 w-4 text-orange-400" />
				Community Recipes
			</div>

			<h1 class="text-4xl font-bold tracking-tight text-white">
				Rezepte entdecken
			</h1>

			<p class="mt-3 text-base leading-relaxed text-gray-400">
				Durchstöbere beliebte Community-Rezepte und finde neue Inspiration.
			</p>
		</div>

		<a
			href="/recipes/new"
			class="flex items-center gap-2 rounded-xl bg-green-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-green-500 active:scale-95"
		>
			<Plus class="h-4 w-4" />
			Rezept erstellen
		</a>
	</div>

	<!-- SEARCH -->
	<div class="mb-6 flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3 transition focus-within:border-white/20">
		<Search class="h-5 w-5 shrink-0 text-gray-500" />
		<input
			bind:value={search}
			type="text"
			placeholder="Rezepte suchen..."
			class="w-full bg-transparent text-white outline-none placeholder:text-gray-500"
		/>
	</div>

	<!-- CATEGORIES -->
	<div class="mb-10 flex flex-wrap gap-3">
		<button
			onclick={() => (selectedCategory = '')}
			class="rounded-lg border px-4 py-2 text-sm transition {selectedCategory === ''
				? 'border-green-500 bg-green-600/20 text-green-400'
				: 'border-white/10 bg-white/5 text-gray-300 hover:border-white/20 hover:bg-white/10'}"
		>
			Alle
		</button>

		{#each categories as category}
			<button
				onclick={() => (selectedCategory = category)}
				class="rounded-lg border px-4 py-2 text-sm transition {selectedCategory === category
					? 'border-green-500 bg-green-600/20 text-green-400'
					: 'border-white/10 bg-white/5 text-gray-300 hover:border-white/20 hover:bg-white/10'}"
			>
				{category}
			</button>
		{/each}
	</div>

	<!-- ERROR -->
	{#if errorMessage}
		<div class="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
			{errorMessage}
		</div>
	{/if}

	<!-- LOADING -->
	{#if loading}
		<div class="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
			{#each Array(6) as _}
				<div class="overflow-hidden rounded-2xl border border-white/10 bg-white/5 animate-pulse">
					<div class="aspect-[4/3] bg-white/5"></div>
					<div class="p-5 space-y-3">
						<div class="h-3 w-1/3 rounded bg-white/10"></div>
						<div class="h-5 w-2/3 rounded bg-white/10"></div>
						<div class="h-3 w-full rounded bg-white/10"></div>
						<div class="h-3 w-4/5 rounded bg-white/10"></div>
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- EMPTY -->
	{#if !loading && filteredRecipes.length === 0}
		<div class="flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/5 py-24 text-center">
			<ChefHat class="mb-4 h-10 w-10 text-gray-600" />
			<p class="text-gray-400">Keine Rezepte gefunden.</p>
			{#if search || selectedCategory}
				<button
					onclick={() => { search = ''; selectedCategory = ''; }}
					class="mt-4 text-sm text-green-400 hover:text-green-300 transition"
				>
					Filter zurücksetzen
				</button>
			{/if}
		</div>
	{/if}

	<!-- GRID -->
	{#if !loading && filteredRecipes.length > 0}
		<div class="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
			{#each filteredRecipes as recipe}
				<a
					href={`/recipes/${recipe.id}`}
					class="group overflow-hidden rounded-2xl border border-white/10 bg-white/5 transition hover:border-white/20 hover:bg-white/[0.07]"
				>
					<!-- IMAGE -->
					<div class="aspect-[4/3] overflow-hidden">
						<img
							src={recipe.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=1200'}
							alt={recipe.title}
							class="h-full w-full object-cover transition duration-500 group-hover:scale-[1.04]"
						/>
					</div>

					<!-- CONTENT -->
					<div class="p-5">
						<div class="mb-3 flex items-center justify-between">
							<span class="rounded-md bg-white/5 px-2 py-1 text-xs text-gray-400">
								{recipe.category}
							</span>
							<div class="flex items-center gap-1 text-sm text-yellow-400">
								<Star class="h-4 w-4 fill-current" />
								{recipe.average_rating?.toFixed(1) ?? '0.0'}
							</div>
						</div>

						<h2 class="mb-2 text-lg font-semibold text-white">
							{recipe.title}
						</h2>

						<p class="line-clamp-2 text-sm leading-relaxed text-gray-400">
							{recipe.description}
						</p>

						<div class="mt-5 flex items-center justify-between border-t border-white/5 pt-4 text-sm text-gray-500">
							<div class="flex items-center gap-2">
								<Clock3 class="h-4 w-4" />
								{recipe.timeMinutes} Min.
							</div>
							<span class="text-green-400 transition group-hover:translate-x-0.5">
								Details →
							</span>
						</div>
					</div>
				</a>
			{/each}
		</div>
	{/if}

</section>
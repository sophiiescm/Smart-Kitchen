<script lang="ts">
	import { Clock3, Star, Search, Flame } from 'lucide-svelte';

	type Recipe = {
		id: number;
		title: string;
		description: string;
		category: string;
		timeMinutes: number;
		rating: number;
		image: string;
	};

	// später ersetzen durch:
	// import { getRecipes } from '$lib/api';

	const recipes: Recipe[] = [
		{
			id: 1,
			title: 'Spaghetti Carbonara',
			description: 'Cremige Pasta mit knusprigem Speck.',
			category: 'Pasta',
			timeMinutes: 25,
			rating: 4.8,
			image:
				'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?q=80&w=1200'
		},
		{
			id: 2,
			title: 'Shakshuka',
			description: 'Tomatensauce mit pochierten Eiern.',
			category: 'Frühstück',
			timeMinutes: 30,
			rating: 4.6,
			image:
				'https://images.unsplash.com/photo-1510693206972-df098062cb71?q=80&w=1200'
		},
		{
			id: 3,
			title: 'Ramen Bowl',
			description: 'Japanische Nudelsuppe mit intensiver Brühe.',
			category: 'Suppe',
			timeMinutes: 50,
			rating: 4.9,
			image:
				'https://images.unsplash.com/photo-1617093727343-374698b1b08d?q=80&w=1200'
		}
	];

	let search = '';

	$: filteredRecipes = recipes.filter(
		(recipe) =>
			recipe.title.toLowerCase().includes(search.toLowerCase()) ||
			recipe.category.toLowerCase().includes(search.toLowerCase())
	);
</script>

<section class="px-6 py-10 lg:px-10">
	<!-- Header -->
	<div class="mb-10 flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
		<div>
			<div
				class="mb-4 inline-flex items-center gap-2 rounded-full bg-green-500/10 px-4 py-2 text-sm font-semibold text-green-400"
			>
				<Flame class="h-4 w-4" />
				Community Recipes
			</div>

			<h1 class="text-5xl font-black text-white xl:text-6xl">
				Rezepte entdecken
			</h1>

			<p class="mt-4 max-w-2xl text-lg text-gray-400">
				Durchstöbere moderne Gerichte, beliebte Community-Favoriten und neue
				Inspirationen.
			</p>
		</div>

		<a
			href="/recipes/new"
			class="inline-flex items-center justify-center rounded-2xl bg-gradient-to-r from-green-600 to-emerald-800 px-6 py-4 font-semibold text-white shadow-2xl shadow-green-900/40 transition hover:scale-[1.02]"
		>
			+ Rezept erstellen
		</a>
	</div>

	<!-- Search -->
	<div
		class="mb-12 flex items-center gap-4 rounded-[32px] border border-white/10 bg-[#0B1118]/80 px-6 py-5 shadow-2xl backdrop-blur-2xl"
	>
		<Search class="h-5 w-5 text-gray-500" />

		<input
			bind:value={search}
			type="text"
			placeholder="Rezepte suchen..."
			class="w-full bg-transparent text-lg text-white outline-none placeholder:text-gray-500"
		/>
	</div>

	<!-- Categories -->
	<div class="mb-12 flex flex-wrap gap-4">
		{#each ['Pasta', 'Dessert', 'Suppe', 'Vegetarisch', 'BBQ'] as category}
			<button
				class="rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm text-gray-300 backdrop-blur-xl transition hover:border-green-500/30 hover:bg-green-500/10 hover:text-green-400"
			>
				{category}
			</button>
		{/each}
	</div>

	<!-- Grid -->
	<div class="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
		{#each filteredRecipes as recipe}
			<a
				href="/recipes/{recipe.id}"
				class="group overflow-hidden rounded-[32px] border border-white/10 bg-[#0B1118]/70 backdrop-blur-xl transition duration-300 hover:-translate-y-2 hover:border-green-500/20"
			>
				<div class="relative h-64 overflow-hidden">
					<img
						src={recipe.image}
						alt={recipe.title}
						class="h-full w-full object-cover transition duration-700 group-hover:scale-110"
					/>

					<div
						class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent"
					></div>

					<div
						class="absolute left-4 top-4 rounded-full bg-black/40 px-3 py-1 text-xs text-white backdrop-blur-xl"
					>
						{recipe.category}
					</div>

					<div
						class="absolute bottom-4 left-4 flex items-center gap-2 rounded-full bg-black/40 px-3 py-1 text-sm text-yellow-400 backdrop-blur-xl"
					>
						<Star class="h-4 w-4 fill-current" />
						{recipe.rating}
					</div>
				</div>

				<div class="p-6">
					<h2 class="mb-3 text-2xl font-bold text-white">
						{recipe.title}
					</h2>

					<p class="mb-6 leading-relaxed text-gray-400">
						{recipe.description}
					</p>

					<div
						class="flex items-center justify-between border-t border-white/5 pt-4 text-sm text-gray-500"
					>
						<div class="flex items-center gap-2">
							<Clock3 class="h-4 w-4" />
							{recipe.timeMinutes} Minuten
						</div>

						<span class="text-green-400">
							Details →
						</span>
					</div>
				</div>
			</a>
		{/each}
	</div>
</section>
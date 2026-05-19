
<script lang="ts">
    
    let { children } = $props();
</script>

<div class="app-layout">
    {@render children()} 
</div>

<style>
    /* Globales Reset, damit alles sauber aussieht */
    :global(html), :global(body) {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
    }
</style>
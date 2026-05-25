<script lang="ts">
    // 
    import '../app.css'; 

    let { children } = $props();
</script>

<div class="app-layout min-h-screen bg-[#04070a]">
    {@render children()} 
</div>

<style>
    /* Globales Reset, damit alles sauber aussieht */
    :global(html), :global(body) {
        margin: 0;
        padding: 0;
        width: 100%;
        min-height: 100vh;
        background-color: #04070a; /* Verhindert ein weißes Aufblitzen beim Laden */
        box-sizing: border-box;
    }
</style>
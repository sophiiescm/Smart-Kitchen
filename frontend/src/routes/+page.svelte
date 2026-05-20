
<script lang="ts">
    import { onMount } from 'svelte';

    const username = $state('Küchenchef'); // Standard-Name, falls Server lädt
    const errorMessage = $state('');

    onMount(async () => {
        // 1. Hol das Token, das wir beim Login im Browser gespeichert haben
        const token = localStorage.getItem('token');
        
        // Wenn kein Token da ist, schick den User zurück zum Login
        if (!token) {
            window.location.href = '/auth/login';
            return;
        }

        try {
            // 2. Nutze den Code von Copilot, um das Profil vom Backend zu laden
            // (Passe hier ggf. den Port an, z.B. 8000 oder 8080)
            const response = await fetch('http://localhost:8000/my-profile', {
                headers: { 
                    'Authorization': `Bearer ${token}` // Das zeigt dem Server, wer du bist!
                }
            });

            if (!response.ok) {
                throw new Error('Sitzung abgelaufen');
            }

            const data = await response.json();
            
            // 3. Setze den echten Namen aus dem Backend ein!
            username = data.username; 

        } catch (error) {
            // Falls das Token ungültig war -> ab zum Login
            localStorage.removeItem('token');
            window.location.href = '/auth/login';
        }
    });

    function handleLogout() {
        localStorage.removeItem('token');
        window.location.href = '/auth/login';
    }
</script>

<div class="dashboard-container">
    <nav class="glass-nav">
        <div class="logo">
            Smart<span>Kitchen</span>
        </div>
        <button class="logout-btn" onclick={handleLogout}>
            Abmelden
        </button>
    </nav>

    <main class="content">
        <header class="welcome-section">
            <h1>Hallo, <span>{username}!</span></h1>
            <p>Willkommen zurück. Was kochen wir heute?</p>
        </header>

        <div class="grid">
            <div class="glass-card">
                <div class="icon">🥗</div>
                <h3>Rezepte</h3>
                <p>Entdecke neue Gerichte basierend auf deinem Vorrat.</p>
            </div>

            <div class="glass-card">
                <div class="icon">🍎</div>
                <h3>Vorrat</h3>
                <p>Du hast 12 Artikel, die bald ablaufen.</p>
            </div>

            <div class="glass-card">
                <div class="icon">🛒</div>
                <h3>Einkaufsliste</h3>
                <p>5 Artikel müssen nachgekauft werden.</p>
            </div>
        </div>
    </main>
</div>

<style>
    :global(body) {
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: radial-gradient(circle at center, #f8fafc 0%, #f1f5f9 100%);
        color: #0f172a;
    }

    .dashboard-container {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }

    /* Moderne Glass-Navigation */
    .glass-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 40px;
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        position: sticky;
        top: 0;
        z-index: 100;
    }

    .logo {
        font-size: 20px;
        font-weight: 300;
        letter-spacing: 1px;
    }

    .logo span {
        font-weight: 700;
        color: #34d399;
    }

    .logout-btn {
        background: #0f172a;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .logout-btn:hover {
        background: #ef4444; /* Rot beim Ausloggen */
        transform: translateY(-1px);
    }

    .content {
        max-width: 1000px;
        margin: 40px auto;
        padding: 0 20px;
        width: 100%;
        box-sizing: border-box;
    }

    .welcome-section {
        margin-bottom: 40px;
    }

    .welcome-section h1 {
        font-size: 36px;
        font-weight: 300;
        margin: 0;
    }

    .welcome-section h1 span {
        font-weight: 700;
    }

    .welcome-section p {
        color: #64748b;
        margin-top: 10px;
    }

    /* Kachel-System */
    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 25px;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.5);
        border: 1px solid rgba(0, 0, 0, 0.05);
        padding: 30px;
        border-radius: 20px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03);
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .glass-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.8);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.06);
        border-color: rgba(52, 211, 153, 0.3);
    }

    .icon {
        font-size: 32px;
        margin-bottom: 20px;
    }

    .glass-card h3 {
        margin: 0 0 10px 0;
        font-size: 18px;
    }

    .glass-card p {
        margin: 0;
        font-size: 14px;
        color: #64748b;
        line-height: 1.5;
    }
</style>
// =========================================================================
    // TO-DO LISTE FÜR PHASE 2 (BACKEND-ANBINDUNG & SESSIONS)
    // =========================================================================
    // TODO 1: Authentifizierung absichern (Auth-Guard)
    // -> Sicherstellen, dass diese Seite NUR aufgerufen werden kann, wenn ein 
    //    gültiges Token im Speicher liegt. Falls nicht -> Redirect zu /auth/login.
    //
    // TODO 2: Dynamischen Nutzernamen laden
    // -> Beim Laden der Seite (onMount) einen Fetch-Befehl an das Backend abfeuern 
    //    (z.B. GET /users/me oder GET /profile), um den echten Namen des
    //    eingeloggten Nutzers abzufragen und die Variable 'username' zu füllen.
    //
    // TODO 3: API-Anbindung für die Dashboard-Kacheln
    // -> Fetch-Befehle implementieren, um die echten Daten aus der Datenbank
    //    zu laden:
    //    - Kachel 1 (Rezepte): GET /recipes (passend zu vorhandenen Zutaten)
    //    - Kachel 2 (Vorrat): GET /inventory (inkl. Ablaufdatum-Check)
    //    - Kachel 3 (Einkaufsliste): GET /shopping-list
    //
    // TODO 4: Fehlerbehandlung (Session-Expired)
    // -> Falls ein API-Aufruf den HTTP-Status 401 (Unauthorized) zurückgibt,
    //    muss der Nutzer automatisch ausgeloggt und zum Login geschickt werden.
    // =========================================================================
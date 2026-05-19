<script lang="ts">
    let username = '';
    let password = '';
    let errorMessage = '';
    let isLoading = false;

    async function handleLogin() {
        errorMessage = '';
        isLoading = true;

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch('http://localhost:8000/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Ungültige Anmeldedaten');
            }

            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            window.location.href = '/';
            
        } catch (error: any) {
            errorMessage = error.message || 'Verbindung zum Backend fehlgeschlagen.';
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="login-container">
    <div class="glass-card">
        <div class="header">
            <h1>Smart<span>Kitchen</span></h1>
            <p class="subtitle">Anmeldung</p>
        </div>

        <form on:submit|preventDefault={handleLogin} class="form-style">
            {#if errorMessage}
                <div class="error-box">
                    {errorMessage}
                </div>
            {/if}

            <div class="input-group">
                <label for="username">Nutzername</label>
                <input
                    id="username"
                    type="text"
                    bind:value={username}
                    required
                    placeholder="dein_name"
                />
            </div>

            <div class="input-group">
                <label for="password">Passwort</label>
                <input
                    id="password"
                    type="password"
                    bind:value={password}
                    required
                    placeholder="••••••••"
                />
            </div>

            <button type="submit" disabled={isLoading}>
                {isLoading ? 'Wird geladen...' : 'Einloggen'}
            </button>
        </form>
    </div>
</div>

<style>
    /* Globales Reset 
    :global(body) {
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #04070a;
    }

    /*Zentrierung*/
    .login-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle at center, #f8fafc 0%, #f1f5f9 100%);
        box-sizing: border-box;
    }

    /* Das echte Glassmorphism-Feld */
    .glass-card {
        width: 100%;
        max-width: 380px;
        padding: 40px;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.4);
        border: 1px solid rgba(0, 0, 0, 0.06);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
        box-sizing: border-box;
    }

    .header {
        text-align: center;
        margin-bottom: 30px;
    }

    .header h1 {
        color: #0f172a;
        font-size: 28px;
        font-weight: 300;
        margin: 0;
        letter-spacing: 0.5px;
    }

    .header h1 span {
        font-weight: 600;
        color: #34d399; 
    }

    .subtitle {
        color: #000000;;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 8px 0 0 0;
        opacity: 0.8;
    }

    .form-style {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .input-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .input-group label {
        color: #64748b;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }

    .input-group input {
        width: 100%;
        padding: 14px 16px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: #000000;;
        font-size: 14px;
        outline: none;
        transition: all 0.3s ease;
        box-sizing: border-box;
    }

    .input-group input:focus {
        border-color: rgba(52, 211, 153, 0.4);
        background: #ffffff;
        color: #000000;
    }

    .input-group input::placeholder {
        color: #000000;
    }

    /* Eleganter weißer Button, der beim Hover grün wird */
    button {
        width: 100%;
        padding: 14px;
        background: #ffffff;
        border: none;
        border-radius: 12px;
        color: #0f172a;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 10px;
    }

    button:hover {
        background: #34d399;
        box-shadow: 0 0 20px rgba(52, 211, 153, 0.3);
    }

    button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .error-box {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: #f87171;
        padding: 12px;
        border-radius: 12px;
        font-size: 12px;
        text-align: center;
    }
</style>

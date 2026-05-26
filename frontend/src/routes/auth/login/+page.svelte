<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { login } from '$lib/api';

    // In runes mode müssen reaktive Werte mit $state() deklariert werden.
    let username = $state('');
    let password = $state('');
    let errorMessage = $state('');
    let isLoading = $state(false);

    async function handleLogin() {
        errorMessage = '';
        isLoading = true;

        try {
            await login(username, password);
            localStorage.setItem('username', username);

            // Wenn der Hook uns mit ?redirect=... hierher geschickt hat,
            // springen wir nach erfolgreichem Login dorthin zurück.
            const redirectTo = $page.url.searchParams.get('redirect') || '/';
            await goto(redirectTo);
        } catch (error: unknown) {
            if (error instanceof Error) {
                errorMessage = error.message;
            } else {
                errorMessage = 'Login fehlgeschlagen.';
            }
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="auth-container">
	<!-- Background Blobs -->
	<div class="background-blur blur-1"></div>
	<div class="background-blur blur-2"></div>

	<!-- Card -->
	<div class="auth-card">

		<!-- Logo -->
		<div class="logo-block">
			<div class="logo">Smart<span>Kitchen</span></div>
			<div class="badge">🍳 Willkommen zurück</div>
		</div>

		<h1>Anmelden</h1>
		<p class="subtitle">Melde dich an, um deine Rezepte zu verwalten.</p>

		<form onsubmit={(e) => { e.preventDefault(); handleLogin(); }}>

			{#if errorMessage}
				<div class="error-box" role="alert" aria-live="assertive">
					⚠ {errorMessage}
				</div>
			{/if}

			<div class="field">
				<label for="username">Nutzername</label>
				<input
					id="username"
					type="text"
					bind:value={username}
					required
					placeholder="dein_name"
				/>
			</div>

			<div class="field">
				<label for="password">Passwort</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					required
					placeholder="••••••••"
				/>
			</div>

			<button type="submit" class="submit-btn" disabled={isLoading}>
				{isLoading ? 'Wird geladen...' : 'Einloggen →'}
			</button>
		</form>

		<p class="switch-link">
			Noch kein Account?
			<a href="/auth/register">Registrieren</a>
		</p>
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
		background: #04070a;
		color: white;
	}

	.auth-container {
		position: fixed;
		inset: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #04070a;
		overflow: hidden;
	}

	.background-blur {
		position: absolute;
		border-radius: 9999px;
		filter: blur(120px);
		pointer-events: none;
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

	/* CARD */

	.auth-card {
		position: relative;
		z-index: 1;
		width: 100%;
		max-width: 420px;
		padding: 44px 40px;
		border-radius: 32px;
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid rgba(255, 255, 255, 0.07);
		backdrop-filter: blur(24px);
		box-sizing: border-box;
		margin: 16px;
	}

	.logo-block {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 32px;
	}

	.logo {
		font-size: 22px;
		font-weight: 900;
		letter-spacing: -0.5px;
		color: white;
	}

	.logo span {
		color: #22c55e;
	}

	.badge {
		display: inline-flex;
		align-items: center;
		padding: 7px 14px;
		border-radius: 999px;
		background: rgba(34, 197, 94, 0.1);
		color: #4ade80;
		font-size: 12px;
		font-weight: 600;
	}

	h1 {
		font-size: 40px;
		font-weight: 900;
		letter-spacing: -2px;
		margin: 0 0 10px;
		background: linear-gradient(to right, #ffffff, #94a3b8);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
	}

	.subtitle {
		margin: 0 0 32px;
		color: #64748b;
		font-size: 15px;
		line-height: 1.6;
	}

	form {
		display: flex;
		flex-direction: column;
		gap: 18px;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 9px;
	}

	label {
		font-size: 11px;
		font-weight: 700;
		color: #94a3b8;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	input {
		background: rgba(255, 255, 255, 0.05);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 16px;
		padding: 14px 18px;
		color: white;
		font-size: 15px;
		font-family: inherit;
		outline: none;
		transition: border-color 0.2s, background 0.2s;
		box-sizing: border-box;
		width: 100%;
	}

	input::placeholder {
		color: #3f4d5c;
	}

	input:focus {
		border-color: rgba(74, 222, 128, 0.3);
		background: rgba(255, 255, 255, 0.07);
	}

	.error-box {
		background: rgba(239, 68, 68, 0.08);
		border: 1px solid rgba(239, 68, 68, 0.18);
		color: #f87171;
		padding: 13px 16px;
		border-radius: 14px;
		font-size: 13px;
	}

	.submit-btn {
		margin-top: 8px;
		padding: 16px;
		border-radius: 18px;
		background: linear-gradient(to right, #16a34a, #065f46);
		border: none;
		color: white;
		font-size: 16px;
		font-weight: 700;
		font-family: inherit;
		cursor: pointer;
		transition: 0.3s;
		box-shadow: 0 10px 30px rgba(22, 163, 74, 0.3);
		width: 100%;
	}

	.submit-btn:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 16px 40px rgba(22, 163, 74, 0.4);
	}

	.submit-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.switch-link {
		margin-top: 24px;
		text-align: center;
		font-size: 14px;
		color: #64748b;
	}

	.switch-link a {
		color: #4ade80;
		font-weight: 600;
		text-decoration: none;
	}

	.switch-link a:hover {
		text-decoration: underline;
	}
</style>
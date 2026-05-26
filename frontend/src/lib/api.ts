/** Basis-URL des FastAPI-Backends */
const API_BASE = 'http://localhost:8000';

/** Hilfsfunktion: gibt den gespeicherten JWT zurück (oder null) */
function getToken(): string | null {
	const stored = localStorage.getItem('token');
	if (stored) {
		return stored;
	}

	const cookieMatch = document.cookie.match(/(?:^|; )token=([^;]+)/);
	return cookieMatch ? decodeURIComponent(cookieMatch[1]) : null;
}

/** Hilfsfunktion: speichert den JWT im localStorage */
function saveToken(token: string): void {
	localStorage.setItem('token', token);
	document.cookie = `token=${encodeURIComponent(token)}; path=/`;
}

/** Hilfsfunktion: löscht den JWT (Logout) */
export function logout(): void {
	localStorage.removeItem('token');
	document.cookie = 'token=; Max-Age=0; path=/';
}

/** Gibt true zurück, wenn ein Token gespeichert ist */
export function isLoggedIn(): boolean {
	return getToken() !== null;
}

/**
 * Login via OAuth2 Password Flow.
 * Sendet username + password als Formular-Daten (nicht JSON!) an POST /token.
 * Speichert den erhaltenen access_token im localStorage.
 */
export async function login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
	const body = new URLSearchParams();
	body.set('username', username);
	body.set('password', password);
	body.set('grant_type', 'password');

	const response = await fetch(`${API_BASE}/token`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded'
		},
		body: body.toString()
	});

	if (!response.ok) {
		const errorText = await response.text();
		if (response.status === 401) {
			throw new Error('Ungültige Zugangsdaten. Bitte überprüfe Nutzername und Passwort.');
		}
		throw new Error(`Login fehlgeschlagen: ${response.status} ${response.statusText}${errorText ? ` - ${errorText}` : ''}`);
	}

	const data = await response.json();
	if (!data?.access_token || typeof data.access_token !== 'string') {
		throw new Error('Login fehlgeschlagen: Ungültige Antwort vom Server');
	}

	saveToken(data.access_token);
	return data;
}

/**
 * Führt einen authentifizierten Request aus.
 * Hängt den Bearer-Token aus dem localStorage als Authorization-Header an.
 */
export async function fetchProtected<T>(path: string, options?: RequestInit): Promise<T> {
	const token = getToken();
	if (!token) {
		window.location.href = '/auth/login';
		throw new Error('Kein Token gefunden. Weiterleitung zur Anmeldung.');
	}

	const headers = new Headers(options?.headers ?? {});
	headers.set('Authorization', `Bearer ${token}`);

	const response = await fetch(`${API_BASE}${path}`, {
		...options,
		headers
	});

	if (response.status === 401) {
		logout();
		window.location.href = '/auth/login';
		throw new Error('Unauthorized: Token ungültig oder abgelaufen. Weiterleitung zur Anmeldung.');
	}

	if (!response.ok) {
		throw new Error(`Fehler beim Laden geschützter Daten: ${response.status} ${response.statusText}`);
	}

	return await response.json() as T;
}

/**
 * Führt einen nicht authentifizierten GET-Request aus.
 */
export async function fetchPublic<T>(path: string): Promise<T> {
	const response = await fetch(`${API_BASE}${path}`);
	if (!response.ok) {
		throw new Error(`Fehler beim Laden der öffentlichen Ressource: ${response.status} ${response.statusText}`);
	}
	return await response.json() as T;
}

/**
 * Führt einen GET-Request aus und hängt das JWT als Authorization-Header an,
 * FALLS eines vorhanden ist. So funktioniert die Anfrage für anonyme Nutzer
 * weiterhin, aber bei eingeloggten Nutzern erkennt das Backend den Besitzer
 * privater Rezepte.
 */
export async function fetchOptionalAuth<T>(path: string): Promise<T> {
	const token = getToken();
	const headers: Record<string, string> = {};
	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}
	const response = await fetch(`${API_BASE}${path}`, { headers });
	if (!response.ok) {
		throw new Error(`Fehler beim Laden der Ressource: ${response.status} ${response.statusText}`);
	}
	return await response.json() as T;
}

export async function register(username: string, email: string, password: string): Promise<void> {
	const response = await fetch(`${API_BASE}/auth/register`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ username, email, password })
	});

	if (!response.ok) {
		// Versuche FastAPI-typische JSON-Fehlerantwort zu parsen
		let detail = '';
		try {
			const body = await response.json();
			if (typeof body?.detail === 'string') {
				detail = body.detail;
			} else if (Array.isArray(body?.detail)) {
				// Pydantic-Validation-Fehler
				detail = body.detail
					.map((err: any) => err?.msg ?? JSON.stringify(err))
					.join(', ');
			}
		} catch {
			// kein JSON, ignorieren
		}

		if (response.status === 409) {
			throw new Error(detail || 'Nutzername oder E-Mail bereits vergeben.');
		}
		if (response.status === 400 || response.status === 422) {
			throw new Error(detail || 'Bitte überprüfe deine Eingaben.');
		}
		throw new Error(detail || `Registrierung fehlgeschlagen (${response.status}).`);
	}
}

export async function getCurrentUser(): Promise<{ id: number; username: string; email: string }> {
	return await fetchProtected('/my-profile');
}

export async function getPublicRecipes(query?: {
	q?: string;
	category?: string;
	tag?: string;
	difficulty?: string;
	max_time?: number;
}): Promise<any[]> {
	const params = new URLSearchParams();
	if (query) {
		if (query.q) params.set('q', query.q);
		if (query.category) params.set('category', query.category);
		if (query.tag) params.set('tag', query.tag);
		if (query.difficulty) params.set('difficulty', query.difficulty);
		if (query.max_time !== undefined) params.set('max_time', String(query.max_time));
	}
	return await fetchPublic<any[]>(`/recipes?${params.toString()}`);
}

export async function getMyRecipes(): Promise<any[]> {
	return await fetchProtected('/recipes/mine');
}

export async function getRecipe(recipeId: number): Promise<any> {
	// Token mitschicken falls eingeloggt — sonst sieht der Backend-Endpoint
	// uns nicht als Besitzer und liefert 403 für eigene private Rezepte.
	return await fetchOptionalAuth<any>(`/recipes/${recipeId}`);
}

export async function createRecipe(data: {
	title: string;
	description: string;
	category?: string;
	prep_time_minutes?: number;
	servings?: number;
	difficulty?: string;
	is_public: boolean;
	ingredients: { name: string; amount?: number; unit?: string }[];
	steps: { step_number: number; instruction: string }[];
	tags: string[];
}): Promise<any> {
	return await fetchProtected<any>('/recipes', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
}

export async function rateRecipe(recipeId: number, rating: number): Promise<any> {
	// Backend RatingCreate Schema verlangt recipe_id im Body (zusätzlich
	// zum Pfad-Parameter). Beides mitschicken sonst kommt 422.
	return await fetchProtected<any>(`/recipes/${recipeId}/ratings`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ recipe_id: recipeId, rating })
	});
}

export async function updateRecipe(recipeId: number, data: any): Promise<any> {
	return await fetchProtected<any>(`/recipes/${recipeId}`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
}

export async function deleteRecipe(recipeId: number): Promise<void> {
	await fetchProtected<any>(`/recipes/${recipeId}`, {
		method: 'DELETE'
	});
}

/** ❤ Rezept zu Favoriten hinzufügen */
export async function favoriteRecipe(recipeId: number): Promise<void> {
	await fetchProtected<any>(`/recipes/${recipeId}/favorite`, { method: 'POST' });
}

/** 💔 Rezept aus Favoriten entfernen */
export async function unfavoriteRecipe(recipeId: number): Promise<void> {
	await fetchProtected<any>(`/recipes/${recipeId}/favorite`, { method: 'DELETE' });
}

/** Liste der eigenen Favoriten */
export async function getMyFavorites(): Promise<any[]> {
	return await fetchProtected<any[]>('/recipes/favorites');
}

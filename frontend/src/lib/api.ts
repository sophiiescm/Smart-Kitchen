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
export async function login(username: string, password: string): Promise<void> {
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

export async function register(username: string, email: string, password: string): Promise<void> {
	const response = await fetch(`${API_BASE}/auth/register`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ username, email, password })
	});

	if (!response.ok) {
		const errorText = await response.text();
		throw new Error(`Registrierung fehlgeschlagen: ${response.status} ${response.statusText}${errorText ? ` - ${errorText}` : ''}`);
	}
}

export async function getCurrentUser(): Promise<{ username: string; email: string }> {
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
	return await fetchPublic<any>(`/recipes/${recipeId}`);
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
	return await fetchProtected<any>(`/recipes/${recipeId}/ratings`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ rating })
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

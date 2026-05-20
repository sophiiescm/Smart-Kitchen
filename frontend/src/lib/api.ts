/** Basis-URL des FastAPI-Backends */
const API_BASE = 'http://localhost:8000';

/** Hilfsfunktion: gibt den gespeicherten JWT zurück (oder null) */
function getToken(): string | null {
	return localStorage.getItem('token');
}

/** Hilfsfunktion: speichert den JWT im localStorage */
function saveToken(token: string): void {
	localStorage.setItem('token', token);
}

/** Hilfsfunktion: löscht den JWT (Logout) */
export function logout(): void {
	localStorage.removeItem('token');
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

// TODO: Ergänzt hier eigene API-Funktionen, z. B.:
// export async function getItems() {
//   return fetchPublic<Item[]>('/items');
// }
//
// export async function createItem(data: { name: string; price: number }) {
//   const token = getToken();
//   const res = await fetch(`${API_BASE}/items`, {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       'Authorization': `Bearer ${token}`
//     },
//     body: JSON.stringify(data)
//   });
//   if (!res.ok) throw new Error('Erstellen fehlgeschlagen');
//   return res.json();
// }

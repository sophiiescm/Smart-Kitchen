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
	// TODO: Implementiert diese Funktion
	// Hinweis: URLSearchParams für Form-Daten verwenden
	//          Content-Type: 'application/x-www-form-urlencoded'
	//          Bei Erfolg: saveToken(data.access_token) aufrufen
	throw new Error('TODO: login() implementieren');
}

/**
 * Führt einen authentifizierten GET-Request aus.
 * Hängt den Bearer-Token aus dem localStorage als Authorization-Header an.
 */
export async function fetchProtected<T>(path: string): Promise<T> {
	// TODO: Implementiert diese Funktion
	// Hinweis: getToken() für den Token, Authorization: `Bearer ${token}` als Header
	//          Bei 401: logout() aufrufen und Fehler werfen
	throw new Error('TODO: fetchProtected() implementieren');
}

/**
 * Führt einen nicht authentifizierten GET-Request aus.
 */
export async function fetchPublic<T>(path: string): Promise<T> {
	// TODO: Implementiert diese Funktion
	throw new Error('TODO: fetchPublic() implementieren');
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

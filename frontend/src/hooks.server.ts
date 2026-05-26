import { redirect } from '@sveltejs/kit';
import type { Handle } from '@sveltejs/kit';

/**
 * Server-Hook für Auth-Routing.
 *
 * Konzept:
 *   - Die meisten Seiten sind OFFEN: Dashboard, Rezeptliste, einzelnes Rezept
 *     sollen auch ohne Login einsehbar sein (Public-Rezepte).
 *   - Nur Aktionen die einen Account brauchen — z.B. Rezept erstellen — sind
 *     hinter einem Login-Guard.
 *   - Wer schon eingeloggt ist und manuell auf /auth/login geht, wird zur
 *     Startseite zurückgeschickt (kein doppelter Login).
 */

// Pfade, die einen Login zwingend voraussetzen. Wer hier ohne Token landet,
// wird zur Login-Seite geschickt und nach erfolgreichem Login dort wieder
// hingeleitet (siehe `redirect` Query-Param).
const PROTECTED_PATHS = ['/recipes/new'];

function isProtected(pathname: string): boolean {
    return PROTECTED_PATHS.some((p) => pathname === p || pathname.startsWith(p + '/'));
}

export const handle: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get('token');
    const path = event.url.pathname;

    // Eingeloggte User vom Login-/Register-Screen wegholen — die brauchen
    // sich nicht nochmal einzuloggen.
    if (token && (path === '/auth/login' || path === '/auth/register')) {
        throw redirect(303, '/');
    }

    // Geschützte Routen brauchen einen Token. Anonyme Nutzer landen auf der
    // Login-Seite, alles andere darf frei besucht werden.
    if (!token && isProtected(path)) {
        throw redirect(303, `/auth/login?redirect=${encodeURIComponent(path)}`);
    }

    return await resolve(event);
};

import { redirect } from '@sveltejs/kit';
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
    // 1. Hol dir das Token (wird in Phase 2 meistens in den Cookies gespeichert)
    const token = event.cookies.get('token');
    
    // 2. Wohin will der Nutzer gerade?
    const isTryingToLogin = event.url.pathname.startsWith('/auth/login');

    // 3. Wenn kein Token da ist und der Nutzer NICHT auf der Login-Seite ist -> Abfangjäger!
    if (!token && !isTryingToLogin) {
        throw redirect(303, '/auth/login');
    }

    // 4. Wenn er eingeloggt ist und trotzdem zum Login will -> Schick ihn auf die Startseite
    if (token && isTryingToLogin) {
        throw redirect(303, '/');
    }

    return await resolve(event);
};
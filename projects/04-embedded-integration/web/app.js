import { ROUTES, buildEmbedUrl, trustedEmbedMessage } from './routes.js';

const iframe = document.getElementById('workato-frame');
const message = document.getElementById('message');
const status = document.getElementById('status');
const empty = document.getElementById('empty');
const nav = document.getElementById('navigation');

for (const [title, path] of Object.entries(ROUTES)) {
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'nav-item'; button.textContent = title;
  button.addEventListener('click', () => openRoute(title, path));
  nav.append(button);
}

document.getElementById('launch').addEventListener('click', () => openRoute('Projects', ROUTES.Projects));

async function openRoute(title, path) {
  message.textContent = '';
  status.textContent = 'Authenticating…';
  try {
    // Protected same-origin route: host session + CSRF and Gateway authorizer enforcement are deployment requirements.
    const response = await fetch('/api/embed/session', {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
      body: '{}', cache: 'no-store',
    });
    if (!response.ok) throw new Error('Unable to establish an authorized session');
    const data = await response.json();
    if (typeof data.token !== 'string' || !data.token) throw new Error('Invalid session response');
    iframe.src = buildEmbedUrl(path, data.token);
    iframe.hidden = false; empty.hidden = true;
    document.getElementById('page-title').textContent = title;
    status.textContent = 'Session requested';
    for (const item of nav.children) item.classList.toggle('active', item.textContent === title);
  } catch (error) {
    iframe.hidden = true; iframe.removeAttribute('src'); empty.hidden = false;
    status.textContent = 'Not connected'; message.textContent = error.message;
  }
}

window.addEventListener('message', (event) => {
  if (!trustedEmbedMessage(event, iframe.contentWindow)) return;
  // Only an explicit, non-sensitive display-only message type is supported.
  if (event.data?.type === 'heightChange' && Number.isFinite(event.data?.payload?.height)) {
    iframe.style.height = `${Math.min(1200, Math.max(400, event.data.payload.height))}px`;
  }
});

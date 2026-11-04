export const ROUTES = Object.freeze({
  Projects: '/projects',
  Recipes: '/browse/recipes',
  Connections: '/connections',
  'Connector SDK': '/custom_adapters',
  'Lookup Tables': '/lookup_tables',
  'Operations Hub': '/dashboard/main',
});
export const WORKATO_ORIGIN = 'https://app.workato.com';
export function buildEmbedUrl(path, token) {
  if (!Object.values(ROUTES).includes(path)) throw new Error('Disallowed navigation route');
  if (typeof token !== 'string' || token.length < 10) throw new Error('Missing embed token');
  const url = new URL('/direct_link', WORKATO_ORIGIN);
  url.searchParams.set('workato_dl_path', path);
  url.searchParams.set('workato_dl_token', token);
  return url.toString();
}
export function trustedEmbedMessage(event, expectedSource) {
  return event?.origin === WORKATO_ORIGIN && event?.source === expectedSource && event?.data !== null && typeof event?.data === 'object';
}

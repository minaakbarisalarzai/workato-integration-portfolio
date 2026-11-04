import { createSession, RequestError } from './core.mjs';

function configFromEnv() {
  return {
    apiBaseUrl: process.env.WORKATO_API_BASE_URL,
    apiToken: process.env.WORKATO_API_TOKEN,
    vendorId: process.env.WORKATO_EMBED_VENDOR_ID,
    origin: process.env.WORKATO_EMBED_ORIGIN,
    privateKey: process.env.WORKATO_EMBED_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    ttlSeconds: Number(process.env.WORKATO_EMBED_TTL_SECONDS || '300'),
  };
}
const response = (statusCode, data) => ({
  statusCode,
  headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', 'Pragma': 'no-cache', 'X-Content-Type-Options': 'nosniff' },
  body: JSON.stringify(data),
});

export async function handler(event) {
  try {
    const session = await createSession(event, { config: configFromEnv() });
    return response(200, session);
  } catch (error) {
    if (error instanceof RequestError) return response(error.statusCode, { error: error.code });
    // Do not log secrets, JWT, body, or upstream response texts.
    console.error('embed_session_failed', { category: error?.name || 'Error' });
    return response(500, { error: 'internal_server_error' });
  }
}

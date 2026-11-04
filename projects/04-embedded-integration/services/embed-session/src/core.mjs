import { createSign, randomUUID } from 'node:crypto';

const VALID_TENANT_ID = /^E?[A-Za-z0-9_-]{1,64}$/;
const B64 = (value) => Buffer.from(typeof value === 'string' ? value : JSON.stringify(value)).toString('base64url');

export class RequestError extends Error {
  constructor(statusCode, code) { super(code); this.statusCode = statusCode; this.code = code; }
}

export function validatedIdentity(event) {
  // These fields MUST come from a trusted gateway authorizer, never query/body/headers.
  const authorizer = event?.requestContext?.authorizer;
  const claims = authorizer?.lambda ?? authorizer;
  const principalId = claims?.principalId;
  const tenantId = claims?.tenantId;
  if (typeof principalId !== 'string' || !principalId.trim()) throw new RequestError(401, 'unauthenticated');
  if (typeof tenantId !== 'string' || !VALID_TENANT_ID.test(tenantId)) throw new RequestError(403, 'tenant_not_authorized');
  return { principalId, tenantId };
}

export function signEmbedJwt({ vendorId, teamId, origin, privateKey, now = Date.now(), ttlSeconds = 300, id = randomUUID() }) {
  if (!vendorId || !teamId || !/^https:\/\/[^/]+$/.test(origin || '')) throw new Error('invalid_embed_configuration');
  if (!privateKey?.includes('PRIVATE KEY')) throw new Error('invalid_signing_key');
  if (!Number.isInteger(ttlSeconds) || ttlSeconds < 60 || ttlSeconds > 900) throw new Error('invalid_embed_ttl');
  const iat = Math.floor(now / 1000);
  const header = B64({ alg: 'RS256', typ: 'JWT' });
  const payload = B64({ sub: `${vendorId}:${teamId}`, iat, exp: iat + ttlSeconds, jti: id, origin });
  const input = `${header}.${payload}`;
  const signer = createSign('RSA-SHA256');
  signer.update(input); signer.end();
  return `${input}.${signer.sign(privateKey).toString('base64url')}`;
}

export async function getManagedUserTeamId({ tenantId, apiBaseUrl, apiToken, fetchImpl = fetch }) {
  if (!apiToken || !apiBaseUrl?.startsWith('https://')) throw new Error('missing_workato_configuration');
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const url = `${apiBaseUrl.replace(/\/$/, '')}/managed_users/${encodeURIComponent(tenantId)}`;
    const response = await fetchImpl(url, {
      headers: { Authorization: `Bearer ${apiToken}`, Accept: 'application/json' },
      signal: controller.signal,
    });
    if (response.status === 404) throw new RequestError(404, 'tenant_not_found');
    if (!response.ok) throw new RequestError(502, 'workato_lookup_failed');
    const data = await response.json();
    if (!data || (typeof data.id !== 'number' && typeof data.id !== 'string')) throw new RequestError(502, 'invalid_workato_response');
    return String(data.id);
  } finally { clearTimeout(timeout); }
}

export async function createSession(event, { config, fetchImpl = fetch, now = Date.now, id = randomUUID } = {}) {
  if (event?.requestContext?.http?.method && event.requestContext.http.method !== 'POST') throw new RequestError(405, 'method_not_allowed');
  const { tenantId } = validatedIdentity(event);
  const teamId = await getManagedUserTeamId({ tenantId, apiBaseUrl: config.apiBaseUrl, apiToken: config.apiToken, fetchImpl });
  return {
    token: signEmbedJwt({ vendorId: config.vendorId, teamId, origin: config.origin, privateKey: config.privateKey, ttlSeconds: config.ttlSeconds, now: now(), id: id() }),
    expiresIn: config.ttlSeconds,
  };
}

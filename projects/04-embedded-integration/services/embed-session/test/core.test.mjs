import test from 'node:test';
import assert from 'node:assert/strict';
import { generateKeyPairSync, createVerify } from 'node:crypto';
import { createSession, validatedIdentity, RequestError, signEmbedJwt } from '../src/core.mjs';

const { privateKey, publicKey } = generateKeyPairSync('rsa', { modulusLength: 2048, publicKeyEncoding: { type: 'spki', format: 'pem' }, privateKeyEncoding: { type: 'pkcs8', format: 'pem' } });
const config = { apiBaseUrl: 'https://api.example.test/api', apiToken: 'fixture-token', vendorId: 'fixture-vendor', origin: 'https://host.example.test', privateKey, ttlSeconds: 300 };
const event = { requestContext: { http: { method: 'POST' }, authorizer: { lambda: { principalId: 'fixture-user', tenantId: 'Etest123' } } } };
const okFetch = async (url, opts) => {
  assert.match(url, /managed_users\/Etest123$/);
  assert.equal(opts.headers.Authorization, 'Bearer fixture-token');
  return { ok: true, status: 200, json: async () => ({ id: 42 }) };
};

test('rejects unauthenticated caller', () => assert.throws(() => validatedIdentity({}), { statusCode: 401 }));
test('rejects untrusted query tenant without authorizer', () => assert.throws(() => validatedIdentity({ queryStringParameters: { customerId: 'Etest123' } }), { statusCode: 401 }));
test('rejects malformed tenant', () => assert.throws(() => validatedIdentity({ requestContext: { authorizer: { principalId: 'u', tenantId: '../bad' } } }), { statusCode: 403 }));
test('requires POST', async () => await assert.rejects(() => createSession({ ...event, requestContext: { ...event.requestContext, http: { method: 'GET' } } }, { config, fetchImpl: okFetch }), { statusCode: 405 }));
test('creates signed short-lived token using server-derived team', async () => {
  const session = await createSession(event, { config, fetchImpl: okFetch, now: () => 1700000000000, id: () => 'fixture-jti' });
  const [header, payload, signature] = session.token.split('.');
  assert.equal(JSON.parse(Buffer.from(header, 'base64url')).alg, 'RS256');
  const claims = JSON.parse(Buffer.from(payload, 'base64url'));
  assert.equal(claims.sub, 'fixture-vendor:42');
  assert.equal(claims.exp - claims.iat, 300);
  assert.equal(claims.origin, 'https://host.example.test');
  assert.equal(claims.jti, 'fixture-jti');
  const verifier = createVerify('RSA-SHA256'); verifier.update(`${header}.${payload}`); verifier.end();
  assert.equal(verifier.verify(publicKey, Buffer.from(signature, 'base64url')), true);
});
test('propagates 404 tenant lookup as safe error', async () => await assert.rejects(() => createSession(event, { config, fetchImpl: async () => ({ status: 404, ok: false }) }), { statusCode: 404 }));
test('rejects excessive TTL', () => assert.throws(() => signEmbedJwt({ ...config, teamId: 't', ttlSeconds: 3600 }), /invalid_embed_ttl/));

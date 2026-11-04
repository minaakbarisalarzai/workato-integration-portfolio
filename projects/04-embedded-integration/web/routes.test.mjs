import test from 'node:test';
import assert from 'node:assert/strict';
import { ROUTES, buildEmbedUrl, trustedEmbedMessage } from './routes.js';

test('allows configured route', () => assert.equal(new URL(buildEmbedUrl(ROUTES.Projects, 'fixture-token-123')).searchParams.get('workato_dl_path'), '/projects'));
test('blocks arbitrary external route', () => assert.throws(() => buildEmbedUrl('https://other.example', 'fixture-token-123'), /Disallowed/));
test('rejects substring attack on iframe message', () => assert.equal(trustedEmbedMessage({ origin: 'https://app.workato.com.evil.test', source: {}, data: {} }, {}), false));
test('requires exact origin and frame identity', () => { const source = {}; assert.equal(trustedEmbedMessage({ origin: 'https://app.workato.com', source, data: { type: 'heightChange' } }, source), true); });

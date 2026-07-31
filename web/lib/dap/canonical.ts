import type { DapOperationEnvelope, DapRuleset } from "./types";

const encoder = new TextEncoder();
const base58Alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

function compareUtf8(left: string, right: string) {
  const a = encoder.encode(left);
  const b = encoder.encode(right);
  const length = Math.min(a.length, b.length);
  for (let index = 0; index < length; index += 1) {
    if (a[index] !== b[index]) return a[index] - b[index];
  }
  return a.length - b.length;
}

function encode(value: unknown, stack: Set<object>): string {
  if (value === null || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "string") return JSON.stringify(value.normalize("NFC"));
  if (typeof value === "number") {
    if (!Number.isSafeInteger(value) || Object.is(value, -0)) {
      throw new TypeError("DAP canonical JSON permits safe integers only");
    }
    return String(value);
  }
  if (typeof value !== "object" || value === undefined) {
    throw new TypeError(`Unsupported DAP canonical JSON value: ${typeof value}`);
  }
  const prototype = Object.getPrototypeOf(value);
  if (!Array.isArray(value) && prototype !== Object.prototype && prototype !== null) {
    throw new TypeError("DAP canonical JSON objects must be plain records");
  }
  if (stack.has(value)) throw new TypeError("Cyclic input is not canonical JSON");
  stack.add(value);
  try {
    if (Array.isArray(value)) {
      return `[${value.map((item) => encode(item, stack)).join(",")}]`;
    }
    const normalized = Object.entries(value).map(([key, item]) => [key.normalize("NFC"), item] as const);
    if (new Set(normalized.map(([key]) => key)).size !== normalized.length) {
      throw new TypeError("Object keys collide after NFC normalization");
    }
    normalized.sort(([left], [right]) => compareUtf8(left, right));
    return `{${normalized.map(([key, item]) => `${JSON.stringify(key)}:${encode(item, stack)}`).join(",")}}`;
  } finally {
    stack.delete(value);
  }
}

export function canonicalEncode(value: unknown) {
  return encode(value, new Set());
}

export function canonicalBytes(value: unknown) {
  return encoder.encode(canonicalEncode(value));
}

function bytesToHex(bytes: Uint8Array) {
  return [...bytes].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function base64urlToBytes(value: string) {
  const normalized = value.replaceAll("-", "+").replaceAll("_", "/");
  const padded = `${normalized}${"=".repeat((4 - (normalized.length % 4)) % 4)}`;
  const binary = atob(padded);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

export function bytesToBase64url(bytes: Uint8Array) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replaceAll("=", "");
}

export function base58btc(bytes: Uint8Array) {
  let leadingZeroes = 0;
  while (leadingZeroes < bytes.length && bytes[leadingZeroes] === 0) leadingZeroes += 1;
  let number = BigInt(0);
  for (const byte of bytes) number = number * BigInt(256) + BigInt(byte);
  let encoded = "";
  while (number > BigInt(0)) {
    encoded = `${base58Alphabet[Number(number % BigInt(58))]}${encoded}`;
    number /= BigInt(58);
  }
  return `z${"1".repeat(leadingZeroes)}${encoded}`;
}

export function assertSortedStringSet(values: unknown, label: string) {
  if (!Array.isArray(values) || values.some((value) => typeof value !== "string")) {
    throw new TypeError(`${label} must be a string set`);
  }
  const sorted = [...values].sort(compareUtf8);
  if (new Set(values).size !== values.length || values.some((value, index) => value !== sorted[index])) {
    throw new TypeError(`${label} must be unique and UTF-8 sorted`);
  }
}

export async function domainDigest(domain: string, value: unknown) {
  const prefix = encoder.encode(domain);
  const body = canonicalBytes(value);
  const input = new Uint8Array(prefix.length + 1 + body.length);
  input.set(prefix, 0);
  input[prefix.length] = 0;
  input.set(body, prefix.length + 1);
  return new Uint8Array(await crypto.subtle.digest("SHA-256", input));
}

export function operationBody(operation: DapOperationEnvelope | Record<string, unknown>) {
  const body = { ...operation } as Record<string, unknown>;
  delete body.operation_id;
  delete body.content_hash;
  delete body.signature;
  return body;
}

export async function operationIdentifiers(operation: DapOperationEnvelope | Record<string, unknown>) {
  const candidate = operation as Partial<DapOperationEnvelope>;
  assertSortedStringSet(candidate.evidence_ids, "evidence_ids");
  assertSortedStringSet(candidate.parent_ids, "parent_ids");
  assertSortedStringSet(candidate.dependencies, "dependencies");
  assertSortedStringSet(candidate.authorization?.authority_ids, "authorization.authority_ids");
  const digest = await domainDigest("DAP-OPERATION-0.2", operationBody(operation));
  return {
    digest,
    operationId: `op:${base58btc(digest)}`,
    contentHash: `sha256:${bytesToHex(digest)}`,
  };
}

export function rulesetBody(ruleset: DapRuleset | Record<string, unknown>) {
  const body = { ...ruleset } as Record<string, unknown>;
  delete body.ruleset_id;
  return body;
}

export async function rulesetIdentifier(ruleset: DapRuleset | Record<string, unknown>) {
  const digest = await domainDigest("DAP-RULESET-0.2", rulesetBody(ruleset));
  return `ruleset:${base58btc(digest)}`;
}

export async function stateRoot(state: unknown) {
  const digest = await domainDigest("DAP-STATE-0.2", state);
  return `state:${base58btc(digest)}`;
}

export async function historyRoot(operationIds: string[]) {
  const digest = await domainDigest("DAP-HISTORY-0.2", operationIds);
  return `history:${base58btc(digest)}`;
}

export async function verifyEd25519(publicKeyBase64url: string, signatureBase64url: string, digest: Uint8Array) {
  try {
    const publicKey = base64urlToBytes(publicKeyBase64url);
    const signature = base64urlToBytes(signatureBase64url);
    if (publicKey.length !== 32 || signature.length !== 64) return false;
    const key = await crypto.subtle.importKey("raw", publicKey, { name: "Ed25519" }, false, ["verify"]);
    return crypto.subtle.verify(
      { name: "Ed25519" },
      key,
      signature.slice().buffer as ArrayBuffer,
      digest.slice().buffer as ArrayBuffer,
    );
  } catch {
    return false;
  }
}

export async function signEd25519Pkcs8(privateKeyPkcs8Base64url: string, digest: Uint8Array) {
  const privateKey = base64urlToBytes(privateKeyPkcs8Base64url);
  const key = await crypto.subtle.importKey("pkcs8", privateKey, { name: "Ed25519" }, false, ["sign"]);
  const signature = await crypto.subtle.sign(
    { name: "Ed25519" },
    key,
    digest.slice().buffer as ArrayBuffer,
  );
  return bytesToBase64url(new Uint8Array(signature));
}

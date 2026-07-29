import { createHash } from "node:crypto";

export const UNKNOWN = Symbol("DAP_UNKNOWN");

const encoder = new TextEncoder();
const timestampPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
const base58Alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

function compareUtf8(left, right) {
  const a = encoder.encode(left);
  const b = encoder.encode(right);
  const length = Math.min(a.length, b.length);
  for (let index = 0; index < length; index += 1) {
    if (a[index] !== b[index]) return a[index] - b[index];
  }
  return a.length - b.length;
}

function encode(value, stack) {
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
    const normalizedEntries = Object.entries(value).map(([key, item]) => [key.normalize("NFC"), item]);
    const normalizedKeys = new Set(normalizedEntries.map(([key]) => key));
    if (normalizedKeys.size !== normalizedEntries.length) {
      throw new TypeError("Object keys collide after NFC normalization");
    }
    normalizedEntries.sort(([left], [right]) => compareUtf8(left, right));
    return `{${normalizedEntries
      .map(([key, item]) => `${JSON.stringify(key)}:${encode(item, stack)}`)
      .join(",")}}`;
  } finally {
    stack.delete(value);
  }
}

export function canonicalEncode(value) {
  return encode(value, new Set());
}

export function canonicalBytes(value) {
  return encoder.encode(canonicalEncode(value));
}

export function domainDigest(domain, value) {
  return createHash("sha256")
    .update(encoder.encode(domain))
    .update(Buffer.from([0]))
    .update(canonicalBytes(value))
    .digest();
}

export function base58btc(bytes) {
  const source = Buffer.from(bytes);
  let leadingZeroes = 0;
  while (leadingZeroes < source.length && source[leadingZeroes] === 0) leadingZeroes += 1;
  let number = source.length ? BigInt(`0x${source.toString("hex") || "0"}`) : 0n;
  let encoded = "";
  while (number > 0n) {
    const remainder = Number(number % 58n);
    encoded = `${base58Alphabet[remainder]}${encoded}`;
    number /= 58n;
  }
  return `z${"1".repeat(leadingZeroes)}${encoded}`;
}

export function operationBody(operation) {
  const body = { ...operation };
  delete body.operation_id;
  delete body.content_hash;
  delete body.signature;
  return body;
}

export function operationDigest(operation) {
  const setFields = [
    [operation.evidence_ids, "evidence_ids"],
    [operation.parent_ids, "parent_ids"],
    [operation.dependencies, "dependencies"],
    [operation.authorization?.authority_ids, "authorization.authority_ids"],
  ];
  for (const [values, label] of setFields) {
    if (!Array.isArray(values) || values.some((value) => typeof value !== "string")) {
      throw new TypeError(`${label} must be a string set`);
    }
    const sorted = [...values].sort(compareUtf8);
    if (new Set(values).size !== values.length || values.some((value, index) => value !== sorted[index])) {
      throw new TypeError(`${label} must be unique and UTF-8 sorted`);
    }
  }
  return domainDigest("DAP-OPERATION-0.2", operationBody(operation));
}

export function operationIdentifiers(operation) {
  const digest = operationDigest(operation);
  return {
    digest,
    operationId: `op:${base58btc(digest)}`,
    contentHash: `sha256:${digest.toString("hex")}`,
  };
}

export function rulesetBody(ruleset) {
  const body = { ...ruleset };
  delete body.ruleset_id;
  return body;
}

export function rulesetIdentifier(ruleset) {
  return `ruleset:${base58btc(domainDigest("DAP-RULESET-0.2", rulesetBody(ruleset)))}`;
}

function decodePointerToken(token) {
  return token.replaceAll("~1", "/").replaceAll("~0", "~");
}

export function resolvePath(context, pointer) {
  if (typeof pointer !== "string" || !pointer.startsWith("/")) return UNKNOWN;
  let current = context;
  for (const rawToken of pointer.slice(1).split("/")) {
    const token = decodePointerToken(rawToken);
    if (current === null || typeof current !== "object" || !(token in current)) return UNKNOWN;
    current = current[token];
  }
  return current;
}

function sameScalarType(left, right) {
  if (left === null || right === null) return left === null && right === null;
  return typeof left === typeof right && ["boolean", "number", "string"].includes(typeof left);
}

function compareOrdered(left, right) {
  if (Number.isSafeInteger(left) && Number.isSafeInteger(right)) return Math.sign(left - right);
  if (typeof left === "string" && typeof right === "string" && timestampPattern.test(left) && timestampPattern.test(right)) {
    return left === right ? 0 : left < right ? -1 : 1;
  }
  return UNKNOWN;
}

function valueKey(value) {
  if (!sameScalarType(value, value)) return UNKNOWN;
  return canonicalEncode(value);
}

function safeIntegerBinary(left, right, operator) {
  if (!Number.isSafeInteger(left) || !Number.isSafeInteger(right)) return UNKNOWN;
  const value = operator(left, right);
  return Number.isSafeInteger(value) && !Object.is(value, -0) ? value : UNKNOWN;
}

export function scopeContains(grantScope, targetScope, wildcardEnabled = false) {
  if (!Array.isArray(grantScope) || !Array.isArray(targetScope)) return UNKNOWN;
  for (let index = 0; index < grantScope.length; index += 1) {
    const segment = grantScope[index];
    if (typeof segment !== "string") return UNKNOWN;
    if (segment === "**") return wildcardEnabled && index === grantScope.length - 1;
    if (index >= targetScope.length) return false;
    if (segment === "*") {
      if (!wildcardEnabled) return false;
    } else if (segment !== targetScope[index]) {
      return false;
    }
  }
  return grantScope.length <= targetScope.length;
}

export function evaluateExpression(expression, context) {
  if (expression === null || ["boolean", "string", "number"].includes(typeof expression)) return expression;
  if (Array.isArray(expression)) return expression.map((item) => evaluateExpression(item, context));
  if (!expression || typeof expression !== "object") return UNKNOWN;
  const keys = Object.keys(expression);
  if (keys.length !== 1) return UNKNOWN;
  const operator = keys[0];
  const argument = expression[operator];
  if (operator === "path") return resolvePath(context, argument);
  if (operator === "exists") return evaluateExpression(argument, context) !== UNKNOWN;
  if (operator === "not") {
    const value = evaluateExpression(argument, context);
    return value === UNKNOWN || typeof value !== "boolean" ? UNKNOWN : !value;
  }
  if (operator === "all" || operator === "any") {
    if (!Array.isArray(argument)) return UNKNOWN;
    const values = argument.map((item) => evaluateExpression(item, context));
    if (values.some((value) => value !== UNKNOWN && typeof value !== "boolean")) return UNKNOWN;
    if (operator === "all") {
      if (values.includes(false)) return false;
      return values.includes(UNKNOWN) ? UNKNOWN : true;
    }
    if (values.includes(true)) return true;
    return values.includes(UNKNOWN) ? UNKNOWN : false;
  }
  if (operator === "count") {
    const value = evaluateExpression(argument, context);
    return Array.isArray(value) ? value.length : UNKNOWN;
  }
  if (operator === "distinct_count") {
    if (!Array.isArray(argument) || argument.length !== 2) return UNKNOWN;
    const collection = evaluateExpression(argument[0], context);
    const field = argument[1];
    if (!Array.isArray(collection) || typeof field !== "string") return UNKNOWN;
    const values = collection.map((item) => (item && typeof item === "object" && field in item ? valueKey(item[field]) : UNKNOWN));
    if (values.includes(UNKNOWN)) return UNKNOWN;
    return new Set(values).size;
  }
  if (!Array.isArray(argument) || argument.length !== 2) return UNKNOWN;
  const left = evaluateExpression(argument[0], context);
  const right = evaluateExpression(argument[1], context);
  if (left === UNKNOWN || right === UNKNOWN) return UNKNOWN;
  if (operator === "eq" || operator === "neq") {
    if (!sameScalarType(left, right)) return UNKNOWN;
    return operator === "eq" ? left === right : left !== right;
  }
  if (["lt", "lte", "gt", "gte"].includes(operator)) {
    const comparison = compareOrdered(left, right);
    if (comparison === UNKNOWN) return UNKNOWN;
    if (operator === "lt") return comparison < 0;
    if (operator === "lte") return comparison <= 0;
    if (operator === "gt") return comparison > 0;
    return comparison >= 0;
  }
  if (operator === "in") {
    if (!Array.isArray(right) || !sameScalarType(left, left)) return UNKNOWN;
    const needle = valueKey(left);
    const values = right.map(valueKey);
    return values.includes(UNKNOWN) ? UNKNOWN : values.includes(needle);
  }
  if (["contains_all", "subset"].includes(operator)) {
    if (!Array.isArray(left) || !Array.isArray(right)) return UNKNOWN;
    const leftKeys = left.map(valueKey);
    const rightKeys = right.map(valueKey);
    if (leftKeys.includes(UNKNOWN) || rightKeys.includes(UNKNOWN)) return UNKNOWN;
    const candidate = operator === "contains_all" ? rightKeys : leftKeys;
    const container = new Set(operator === "contains_all" ? leftKeys : rightKeys);
    return candidate.every((item) => container.has(item));
  }
  if (operator === "scope_contains") return scopeContains(left, right, context?.candidate?.wildcard_scope === true);
  if (operator === "add") return safeIntegerBinary(left, right, (a, b) => a + b);
  if (operator === "sub") return safeIntegerBinary(left, right, (a, b) => a - b);
  if (operator === "mul") return safeIntegerBinary(left, right, (a, b) => a * b);
  if (operator === "min") return safeIntegerBinary(left, right, Math.min);
  if (operator === "max") return safeIntegerBinary(left, right, Math.max);
  return UNKNOWN;
}

export function ratioSatisfied(actualWeight, baseWeight, ratio) {
  if (![actualWeight, baseWeight, ratio?.numerator, ratio?.denominator].every(Number.isSafeInteger)) return UNKNOWN;
  if (actualWeight < 0 || baseWeight < 0 || ratio.numerator < 0 || ratio.denominator <= 0) return UNKNOWN;
  if (baseWeight === 0) return false;
  return BigInt(actualWeight) * BigInt(ratio.denominator) >= BigInt(baseWeight) * BigInt(ratio.numerator);
}

export function aggregateAuthority(paths, mode, numericScale, minimumWeight = 0) {
  if (!Array.isArray(paths) || !Number.isSafeInteger(numericScale) || numericScale < 1) return UNKNOWN;
  const roots = new Map();
  for (const path of paths) {
    if (!path || typeof path.rootIssuer !== "string" || !Number.isSafeInteger(path.weight) || path.weight < 0) return UNKNOWN;
    roots.set(path.rootIssuer, Math.max(roots.get(path.rootIssuer) ?? 0, path.weight));
  }
  const weights = [...roots.values()];
  const maximum = weights.length ? Math.max(...weights) : 0;
  if (mode === "maximum" || mode === "non_aggregating") {
    return { weight: maximum, rootIssuers: roots.size, qualifyingRootIssuers: weights.filter((weight) => weight >= minimumWeight).length };
  }
  if (mode === "sum_capped" || mode === "issuer_diversity") {
    const sum = weights.reduce((total, weight) => total + weight, 0);
    return { weight: Math.min(sum, numericScale), rootIssuers: roots.size, qualifyingRootIssuers: weights.filter((weight) => weight >= minimumWeight).length };
  }
  if (mode === "independent_threshold") {
    const qualifying = weights.filter((weight) => weight >= minimumWeight);
    return { weight: qualifying.length ? Math.min(...qualifying) : 0, rootIssuers: roots.size, qualifyingRootIssuers: qualifying.length };
  }
  return UNKNOWN;
}

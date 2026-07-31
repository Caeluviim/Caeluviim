import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = process.cwd();

async function source(path) {
  return readFile(resolve(root, path), "utf8");
}

const protectedRoutes = [
  "app/mcp/route.ts",
  "app/api/respond/route.ts",
  "app/api/events/route.ts",
  "app/api/language/acts/route.ts",
  "app/api/language/effects/route.ts",
];

for (const path of protectedRoutes) {
  const text = await source(path);
  assert.match(
    text,
    /requireWriteAuthorization/,
    `${path} must retain the unsigned-write authorization gate.`,
  );
}

const helper = await source("lib/write-auth.ts");
assert.match(helper, /CAELUVIIM_WRITE_BEARER_TOKEN/);
assert.match(helper, /CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES/);
assert.match(helper, /status:\s*503/);
assert.match(helper, /status:\s*401/);
assert.match(helper, /www-authenticate/);

for (const path of ["app/api/districts/route.ts", "app/api/districts/operations/route.ts"]) {
  const text = await source(path);
  assert.doesNotMatch(
    text,
    /requireWriteAuthorization/,
    `${path} must preserve signed-envelope authorization rather than substitute the bearer gate.`,
  );
  assert.match(text, /submitDapOperation/);
}

const localLauncher = await source("scripts/start-local.mjs");
const testLauncher = await source("scripts/run-tests.mjs");
assert.match(localLauncher, /CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES/);
assert.match(testLauncher, /CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES/);

process.stdout.write("Unsigned write-authorization wiring verified.\n");

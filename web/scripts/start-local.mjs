import { createHash, createPublicKey, generateKeyPairSync } from "node:crypto";
import { readFile, rename, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const keyPath = resolve(projectRoot, ".caeluviim-local-validator.json");

function createValidator() {
  const pair = generateKeyPairSync("ed25519");
  const privateKey = pair.privateKey
    .export({ format: "der", type: "pkcs8" })
    .toString("base64url");
  const publicKey = createPublicKey(pair.privateKey)
    .export({ format: "der", type: "spki" })
    .subarray(-32)
    .toString("base64url");
  const fingerprint = createHash("sha256")
    .update(Buffer.from(publicKey, "base64url"))
    .digest("hex")
    .slice(0, 24);
  return {
    validatorId: "validator:caeluviim-local",
    signingKeyId: `key:caeluviim-local:${fingerprint}`,
    publicKey,
    privateKey,
    algorithm: "Ed25519",
    createdAt: new Date().toISOString(),
  };
}

function validValidator(value) {
  return (
    value &&
    typeof value === "object" &&
    typeof value.validatorId === "string" &&
    typeof value.signingKeyId === "string" &&
    typeof value.publicKey === "string" &&
    typeof value.privateKey === "string" &&
    value.algorithm === "Ed25519"
  );
}

async function loadOrCreateValidator() {
  try {
    const existing = JSON.parse(await readFile(keyPath, "utf8"));
    if (validValidator(existing)) return existing;
  } catch {
    // The local validator identity has not been created yet.
  }
  const validator = createValidator();
  const temporaryPath = `${keyPath}.tmp`;
  await writeFile(temporaryPath, `${JSON.stringify(validator, null, 2)}\n`, {
    encoding: "utf8",
    mode: 0o600,
  });
  await rename(temporaryPath, keyPath);
  return validator;
}

const validator = await loadOrCreateValidator();
const currentNodeMajor = Number(process.versions.node.split(".")[0]);
const command = currentNodeMajor >= 22
  ? (process.platform === "win32" ? "npm.cmd" : "npm")
  : (process.platform === "win32" ? "npx.cmd" : "npx");
const args = currentNodeMajor >= 22
  ? ["run", "dev:local:runtime"]
  : ["-y", "-p", "node@22", "-p", "npm@11", "npm", "run", "dev:local:runtime"];

const child = spawn(command, args, {
  cwd: projectRoot,
  env: {
    ...process.env,
    DAP_VALIDATOR_ID: validator.validatorId,
    DAP_VALIDATOR_KEY_ID: validator.signingKeyId,
    DAP_VALIDATOR_PUBLIC_KEY: validator.publicKey,
    DAP_VALIDATOR_PRIVATE_KEY_PKCS8: validator.privateKey,
    CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES:
      process.env.CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES ?? "true",
  },
  stdio: "inherit",
});

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => child.kill(signal));
}

child.on("error", (error) => {
  process.stderr.write(`Unable to start the local Caeluviim service: ${error.message}\n`);
  process.exitCode = 1;
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exitCode = code ?? 1;
});

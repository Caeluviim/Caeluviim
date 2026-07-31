import { spawn } from "node:child_process";
import { readFile, rm, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const sourceUrl = new URL("../tests/rendered-html.test.mjs", import.meta.url);
const runtimeUrl = new URL("../tests/.rendered-html.runtime.test.mjs", import.meta.url);
const configuredBaseUrl = process.env.CAELUVIIM_TEST_BASE_URL?.trim();

let source = await readFile(sourceUrl, "utf8");
if (configuredBaseUrl) {
  const original = 'const baseUrl = "http://127.0.0.1:3210";';
  if (!source.includes(original)) {
    throw new Error("Rendered test base URL declaration was not found.");
  }
  source = source.replace(original, `const baseUrl = ${JSON.stringify(configuredBaseUrl)};`);
}

await writeFile(runtimeUrl, source, "utf8");

const child = spawn(process.execPath, ["--test", fileURLToPath(runtimeUrl)], {
  cwd: fileURLToPath(new URL("../", import.meta.url)),
  env: process.env,
  stdio: "inherit",
});

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => child.kill(signal));
}

child.on("error", async (error) => {
  await rm(runtimeUrl, { force: true });
  process.stderr.write(`Unable to run rendered integration tests: ${error.message}\n`);
  process.exitCode = 1;
});

child.on("exit", async (code, signal) => {
  await rm(runtimeUrl, { force: true });
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exitCode = code ?? 1;
});

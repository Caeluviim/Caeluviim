import { spawn } from "node:child_process";

const currentNodeMajor = Number(process.versions.node.split(".")[0]);
const command = currentNodeMajor >= 22
  ? (process.platform === "win32" ? "npm.cmd" : "npm")
  : (process.platform === "win32" ? "npx.cmd" : "npx");
const args = currentNodeMajor >= 22
  ? ["run", "test:runtime"]
  : ["-y", "-p", "node@22", "-p", "npm@11", "npm", "run", "test:runtime"];

const child = spawn(command, args, {
  cwd: process.cwd(),
  env: process.env,
  stdio: "inherit",
});

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => child.kill(signal));
}

child.on("error", (error) => {
  process.stderr.write(`Unable to run the Caeluviim test suite: ${error.message}\n`);
  process.exitCode = 1;
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exitCode = code ?? 1;
});

import vinext from "vinext";
import { defineConfig } from "vite";
import hostingConfig from "./.openai/hosting.json";
import { sites } from "./build/sites-vite-plugin";

const SITE_CREATOR_PLACEHOLDER_DATABASE_ID =
  "00000000-0000-4000-8000-000000000000";

const { d1, r2 } = hostingConfig;

// macOS Seatbelt blocks FSEvents, so Codex previews need polling for HMR.
const isCodexSeatbeltSandbox = process.env.CODEX_SANDBOX === "seatbelt";
const isCi = process.env.CI === "true";
const persistencePath = process.env.CAELUVIIM_PERSIST_PATH?.trim();

const localBindingConfig = {
  main: "./worker/index.ts",
  compatibility_flags: ["nodejs_compat"],
  d1_databases: d1
    ? [
        {
          binding: d1,
          database_name: "site-creator-d1",
          database_id: SITE_CREATOR_PLACEHOLDER_DATABASE_ID,
        },
      ]
    : [],
  r2_buckets: r2
    ? [
        {
          binding: r2,
          bucket_name: "site-creator-r2",
        },
      ]
    : [],
  vars: {
    DAP_VALIDATOR_ID: process.env.DAP_VALIDATOR_ID ?? "",
    DAP_VALIDATOR_KEY_ID: process.env.DAP_VALIDATOR_KEY_ID ?? "",
    DAP_VALIDATOR_PUBLIC_KEY: process.env.DAP_VALIDATOR_PUBLIC_KEY ?? "",
    DAP_VALIDATOR_PRIVATE_KEY_PKCS8: process.env.DAP_VALIDATOR_PRIVATE_KEY_PKCS8 ?? "",
    CAELUVIIM_WRITE_BEARER_TOKEN: process.env.CAELUVIIM_WRITE_BEARER_TOKEN ?? "",
    CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES:
      process.env.CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES ?? "",
  },
};

export default defineConfig(async () => {
  // Keep Wrangler and Miniflare state project-local. These are non-secret tool
  // settings; application environment belongs in ignored `.env*` files.
  process.env.WRANGLER_WRITE_LOGS ??= "false";
  process.env.WRANGLER_LOG_PATH ??= ".wrangler/logs";
  process.env.MINIFLARE_REGISTRY_PATH ??= ".wrangler/registry";

  // Wrangler snapshots its log path while the Cloudflare plugin is imported.
  const { cloudflare } = await import("@cloudflare/vite-plugin");

  return {
    server: {
      ...(isCi ? { host: "0.0.0.0", strictPort: true } : {}),
      ...(isCodexSeatbeltSandbox
        ? { watch: { useFsEvents: false, usePolling: true } }
        : {}),
    },
    plugins: [
      vinext(),
      sites(),
      cloudflare({
        viteEnvironment: { name: "rsc", childEnvironments: ["ssr"] },
        config: localBindingConfig,
        persistState: persistencePath ? { path: persistencePath } : true,
      }),
    ],
  };
});

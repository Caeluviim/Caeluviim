import { env } from "cloudflare:workers";

const WRITE_TOKEN_BINDING = "CAELUVIIM_WRITE_BEARER_TOKEN";
const INSECURE_LOCAL_BINDING = "CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES";

type WriteAuthEnvironment = {
  CAELUVIIM_WRITE_BEARER_TOKEN?: string;
  CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES?: string;
};

function runtimeEnvironment(): WriteAuthEnvironment {
  try {
    return env as unknown as WriteAuthEnvironment;
  } catch {
    return {};
  }
}

function configuredWriteToken(): string | null {
  const workerToken = runtimeEnvironment()[WRITE_TOKEN_BINDING]?.trim();
  if (workerToken) return workerToken;

  const processToken = process.env.CAELUVIIM_WRITE_BEARER_TOKEN?.trim();
  return processToken || null;
}

function insecureLocalWritesAllowed(request: Request): boolean {
  const workerValue = runtimeEnvironment()[INSECURE_LOCAL_BINDING]?.trim();
  const processValue = process.env.CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES?.trim();
  const enabled = (workerValue || processValue || "").toLocaleLowerCase() === "true";
  if (!enabled) return false;

  const hostname = new URL(request.url).hostname.toLocaleLowerCase();
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1" || hostname === "[::1]";
}

function responseHeaders(headers: HeadersInit): Headers {
  const result = new Headers(headers);
  result.set("cache-control", "no-store");
  return result;
}

/**
 * Authorize an unsigned persistent-write surface.
 *
 * Writes fail closed unless a bearer secret is configured or the explicit
 * loopback-only development override is enabled. Signed DAP submissions retain
 * their separate cryptographic authorization path and do not use this helper.
 */
export function requireWriteAuthorization(
  request: Request,
  headers: HeadersInit = {},
): Response | null {
  const token = configuredWriteToken();

  if (!token) {
    if (insecureLocalWritesAllowed(request)) return null;
    return Response.json(
      {
        error:
          "Unsigned writes are disabled because CAELUVIIM_WRITE_BEARER_TOKEN is not configured.",
      },
      { status: 503, headers: responseHeaders(headers) },
    );
  }

  if (request.headers.get("authorization") !== `Bearer ${token}`) {
    const deniedHeaders = responseHeaders(headers);
    deniedHeaders.set("www-authenticate", 'Bearer realm="Caeluviim write API"');
    return Response.json(
      { error: "A valid Bearer credential is required for this write operation." },
      { status: 401, headers: deniedHeaders },
    );
  }

  return null;
}

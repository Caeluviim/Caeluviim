import { env } from "cloudflare:workers";

const WRITE_TOKEN_BINDING = "CAELUVIIM_WRITE_BEARER_TOKEN";

type WriteAuthEnvironment = {
  CAELUVIIM_WRITE_BEARER_TOKEN?: string;
};

function configuredWriteToken(): string | null {
  try {
    const workerToken = (env as unknown as WriteAuthEnvironment)[WRITE_TOKEN_BINDING]?.trim();
    if (workerToken) return workerToken;
  } catch {
    // The Cloudflare binding is unavailable outside the worker runtime.
  }

  const processToken = process.env.CAELUVIIM_WRITE_BEARER_TOKEN?.trim();
  return processToken || null;
}

function responseHeaders(headers: HeadersInit): Headers {
  const result = new Headers(headers);
  result.set("cache-control", "no-store");
  return result;
}

/**
 * Authorize an unsigned persistent-write surface.
 *
 * Local development remains usable when no token is configured. Production
 * fails closed: a missing secret disables unsigned writes, and a configured
 * secret requires an exact Bearer credential. Signed DAP submissions retain
 * their separate cryptographic authorization path and do not use this helper.
 */
export function requireWriteAuthorization(
  request: Request,
  headers: HeadersInit = {},
): Response | null {
  const token = configuredWriteToken();
  const production = process.env.NODE_ENV === "production";

  if (!token) {
    if (!production) return null;
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

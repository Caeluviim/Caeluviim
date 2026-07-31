interface D1Result<T = Record<string, unknown>> {
  results: T[];
  success?: boolean;
}

interface D1PreparedStatement {
  bind(...values: unknown[]): D1PreparedStatement;
  all<T = Record<string, unknown>>(): Promise<D1Result<T>>;
  run<T = Record<string, unknown>>(): Promise<D1Result<T>>;
}

interface D1Database {
  prepare(query: string): D1PreparedStatement;
  batch<T = Record<string, unknown>>(statements: D1PreparedStatement[]): Promise<D1Result<T>[]>;
}

interface Fetcher {
  fetch(input: Request | string, init?: RequestInit): Promise<Response>;
}

declare module "cloudflare:workers" {
  export const env: {
    DB?: D1Database;
    ASSETS?: Fetcher;
    DAP_VALIDATOR_ID?: string;
    DAP_VALIDATOR_KEY_ID?: string;
    DAP_VALIDATOR_PUBLIC_KEY?: string;
    DAP_VALIDATOR_PRIVATE_KEY_PKCS8?: string;
  };
}

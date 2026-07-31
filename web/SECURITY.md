# Web runtime security boundary

## Required deployment secret

Every non-local deployment must define `CAELUVIIM_WRITE_BEARER_TOKEN` as a secret runtime binding. Generate a high-entropy value, for example:

```sh
openssl rand -hex 32
```

Do not commit the value, expose it in browser JavaScript, place it in a public build variable, or include it in logs.

Unsigned persistent writes fail closed when the secret is absent. Requests then return `503`; requests with a missing or incorrect credential return `401`.

Authorized server-to-server requests use:

```http
Authorization: Bearer <CAELUVIIM_WRITE_BEARER_TOKEN>
```

## Protected unsigned write surfaces

The bearer boundary applies to:

- all `/mcp` requests because the MCP surface includes persistent write tools;
- `POST /api/respond`;
- `POST /api/events`;
- `POST /api/language/acts`;
- `POST /api/language/effects`.

Read-only HTTP endpoints remain public unless a deployment adds a stricter access layer.

## Signed DAP submissions

`POST /api/districts` and `POST /api/districts/operations` retain their separate signed-envelope authorization path. Their acceptance depends on protocol, identifier, signature, replay, membership, authority, scope, ruleset, transition, and conflict validation. The bearer credential must not be treated as a substitute for those checks.

## Local development and tests

The local launcher and automated integration suite explicitly set:

```sh
CAELUVIIM_ALLOW_INSECURE_LOCAL_WRITES=true
```

The runtime accepts that override only when the request hostname is `localhost`, `127.0.0.1`, or the IPv6 loopback address. LAN, preview, staging, and public hostnames still fail closed without the bearer secret even if the override variable is mistakenly set.

Direct `npm run dev` sessions must either configure the bearer token or explicitly set the local override. Never set the override in a shared, preview, staging, or production deployment.

Set `CAELUVIIM_WRITE_BEARER_TOKEN` locally instead when testing the production authorization boundary.

## Rotation

Rotate the bearer secret immediately after suspected disclosure. Because the credential authorizes persistent graph and event writes, production operators should also review recent records and deployment logs after rotation.

# Web runtime security boundary

## Required production secret

Every production deployment must define `CAELUVIIM_WRITE_BEARER_TOKEN` as a secret runtime binding. Generate a high-entropy value, for example:

```sh
openssl rand -hex 32
```

Do not commit the value, expose it in browser JavaScript, place it in a public build variable, or include it in logs.

Production fails closed when the secret is absent. Unsigned persistent writes return `503`; requests with a missing or incorrect credential return `401`.

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

## Local development

When `NODE_ENV` is not `production` and no bearer secret is configured, unsigned writes remain enabled for localhost development and the integration suite. Set `CAELUVIIM_WRITE_BEARER_TOKEN` locally to exercise the production authorization boundary.

## Rotation

Rotate the bearer secret immediately after suspected disclosure. Because the credential authorizes persistent graph and event writes, production operators should also review recent records and deployment logs after rotation.

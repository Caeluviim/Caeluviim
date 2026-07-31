# Caeluviim source-bound knowledge graph

Caeluviim is a phone-ready web service that gives AI platforms a shared, provenance-explicit knowledge repository and a graph/table response protocol. The knowledge graph is primary. The response-event ledger is an audit trail of mapped outputs.

## Operational contract

Every knowledge record:

1. is content-addressed with SHA-256;
2. has one or more domain and topic classifications;
3. includes a source title, URL, exact locator, excerpt, and independent source hash;
4. states the construction rule used to turn source material into the record;
5. preserves conflict groups and jurisdiction/language context when supplied.

Every knowledge edge:

1. links existing subject and object records with a typed predicate;
2. cites one or more existing evidence records;
3. is rejected when any referenced record is missing.

Every grounded response:

1. maps every answer statement to one or more existing knowledge record IDs;
2. contains all eleven response category families;
3. moves populated columns forward and leaves non-applicable categories visible;
4. includes exact record/source provenance in-row;
5. is available as structured JSON and CSV;
6. is rejected when a proposed citation is absent from the graph.

“All knowledge” is a coverage target, not a label the service asserts. Topic exploration returns required domain/facet matrices and explicitly reports every unfilled area as a gap.

## AI-platform MCP surface

The remote MCP endpoint is `/mcp`. It exposes:

| Tool | Purpose |
|---|---|
| `get_protocol_schema` | Read the response and grounding contract |
| `ingest_knowledge_record` | Store a provenance-complete source, message, process, substance, claim, authority, or other typed record |
| `link_knowledge_records` | Add an evidence-bound typed graph edge |
| `search_knowledge` | Retrieve records with source locators, excerpts, hashes, and construction rules |
| `fetch_knowledge_record` | Resolve one immutable record ID |
| `get_knowledge_neighborhood` | Traverse connected records and edges up to three hops |
| `explore_topic_coverage` | Report covered and missing topic domains/facets |
| `record_language_act` | Record expression, content, interpretation, speaker, force, authority status, scope, and evidence as separate linked resources |
| `record_operative_effect` | Record claimed or actual communicative, causal, institutional, normative, procedural, evidentiary, computational, interpretive, or symbolic effects |
| `query_language_force` | Query the joined expression/content/force/authority/effect graph |
| `map_grounded_response` | Reject uncited statements or return the complete graph/table response |
| `list_dap_districts` | List signed district histories and committed roots |
| `reconstruct_dap_district` | Replay accepted history and independently verify both roots |
| `get_dap_history` | Read deterministic accepted-operation history |
| `get_dap_operation_disposition` | Inspect a submission, validation reasons, and acceptance status |
| `submit_signed_dap_operation` | Submit an already-signed envelope through the staged validator |

The endpoint uses stateless Streamable HTTP and is compatible with web-standard/edge runtimes.

## Browser HTTP surface

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Runtime, persistence, and invariant status |
| `GET` | `/api/protocol` | Machine-readable category and endpoint contract |
| `GET` | `/api/dap` | DAP v0.2 envelope/ruleset schemas and signed examples |
| `GET` / `POST` | `/api/districts` | List districts or submit signed genesis |
| `GET` / `POST` | `/api/districts/operations` | Read history/dispositions or submit signed operations |
| `GET` | `/api/districts/state?district_id=...` | Read the committed derived-state projection |
| `GET` | `/api/districts/state?district_id=...&reconstruct=true` | Rebuild state and verify both roots |
| `POST` | `/mcp` | Remote AI-platform graph tools |
| `GET` | `/api/knowledge/search?q=...` | Search provenance-complete knowledge records |
| `GET` | `/api/knowledge/coverage?topic=...` | Topic coverage and explicit gap map |
| `GET` | `/api/language` | Read the language-force and operative-effect contract |
| `GET` / `POST` | `/api/language/acts` | Query or record source-bound language acts |
| `GET` / `POST` | `/api/language/effects` | Query or record evidence-bound operative effects |
| `GET` | `/api/language/graph` | Query/export the joined language graph as JSON, JSON-LD, or N-Quads |
| `POST` | `/api/respond` | Reference graph/table formatter |
| `POST` | `/api/events` | Mapped-response audit event ingestion |
| `GET` | `/api/events` | Append-only response audit ledger |
| `GET` | `/api/responses` | Recent mapped table responses |
| `GET` | `/api/graph` | Response projection nodes and typed edges |

Formal response-event schema: `/caeluviim-response-event.schema.json`.

## Language, force, and operative effect

The `caeluviim-language-force/1.0` layer does not equate wording with meaning or
meaning with legal/social effect. It stores these as separate graph resources:

- the exact expression and medium;
- one or more propositions and source-bound interpretations;
- speaker, addressees, context, language, script, time, jurisdiction, and scope;
- act type, illocutionary force, polarity, deontic operator, status, and claimed
  authority;
- effects with their targets, bearers, beneficiaries, conditions, temporal
  bounds, authority basis, evidence, and optional accepted DAP operation.

Assertive, directive, commissive, expressive, declarative, interrogative,
constitutive, procedural, evidentiary, interpretive, metalinguistic, and
symbolic acts are first-class. Effects remain separately typed as
communicative, interpretive, causal, institutional, normative, procedural,
evidentiary, computational, or symbolic.

The store preserves `proposed`, `claimed`, `pending`, `effective`, `contested`,
`superseded`, `void`, `expired`, `reversed`, and `no_effect` states. It rejects
an `effective` institutional, normative, or procedural effect unless the record
cites authority or an accepted signed DAP operation. Every referenced language,
content, actor, target, basis, authority, and evidence identifier must resolve
to an existing provenance-complete knowledge record.

## Districted Authority Protocol v0.2

The normative DAP working draft is in [`spec/dap/0.2`](spec/dap/0.2). It
separates structural validity, cryptographic validity, admissibility,
acceptance, and derived-state effect. The draft includes:

- a closed operation envelope with deterministic SHA-256 identifiers and
  Ed25519 signatures;
- checkpoint-derived district time and explicit ruleset binding;
- a non-Turing-complete ruleset expression language;
- authority, membership, scope, threshold, transition, conflict, and veto
  policies;
- JSON Schemas, a signed fixture, and executable conformance checks.

`GET /api/dap` returns both schemas and the content-addressed example artifacts.

### Operational district kernel

The service now executes the envelope rather than only describing it. A
district is created exclusively by a signed `DISTRICT_CREATE` genesis
operation containing its initial Ed25519 key, active ruleset, membership, and
bounded authority grants. Later submissions pass protocol, schema, identifier,
signature, replay, district, causal, membership, authority, scope, ruleset,
transition, conflict, and classification stages.

D1 retains submissions, accepted operations, validation dispositions,
rulesets, checkpoints, and derived projections in separate tables. The
`reconstruct=true` state endpoint discards the stored projection, reduces the
accepted operation envelopes again, recalculates history and state roots, and
reports whether both match storage.

The reducer currently executes signed identity/key delegation and revocation,
membership nomination/activation/suspension, scoped authority delegation and
revocation, proposal review/ballot/accept/reject/activate/archive lifecycles,
evidence registration, safety veto attachment/resolution, checkpoint
finalization, ruleset rotation, and non-destructive compensating reversals.
Reversals remain in history, record their compensation in derived state, reject
targets with live semantic dependents, and allow replacement operations without
reviving the reversed projection.

Validation dispositions are independently signed over canonical JSON with the
`DAP-DISPOSITION-0.2` domain separator. The response and stored disposition
carry the validator identity, key ID, public key, algorithm, and signature. The
PKCS#8 validator private key is supplied only as the secret runtime binding
`DAP_VALIDATOR_PRIVATE_KEY_PKCS8`; it is not committed to source.

The browser authority console and MCP surface use the same district functions.
The console can replay a district, compare the stored and reconstructed roots,
show derived membership/authority/proposal state, and submit a pasted signed
envelope. The natural-language formatter may bind a selected district and emits
its actual history root, state root, ruleset, counts, pending operations, and
conflict status in the visible provenance/verification categories.

## Local verification

The project requires Node.js 22 or newer.

```sh
npm ci
npm test
```

For the live laptop service, run:

```sh
npm run dev:local
```

This opens `http://localhost:8080`, reuses a locally generated Ed25519 validator
identity, and keeps its private key in the ignored
`.caeluviim-local-validator.json` file. On machines whose system Node is older
than Node 22, the launcher uses a temporary Node 22 runtime automatically.

When the native Neo4j service is running, project the authoritative D1
language/effect graph into the local visual graph with:

```sh
npm run project:language:neo4j
```

The projection uses the existing local Neo4j credential file, writes only
`CaeluviimResource` nodes and `CAELUVIIM_RELATION` relationships in the
`language-force/1.0` partition, and prints source-versus-Neo4j counts. D1 remains
authoritative; rerunning the command merges the same content-addressed nodes and
edges.

The automated suite builds the deployable worker, server-renders the mobile web UI, initializes MCP, verifies the complete tool list, ingests and retrieves a hashed knowledge fixture, detects deliberate coverage gaps, accepts a grounded statement, rejects a missing citation, and verifies response-event deduplication/graph projection. Its district proof creates fresh Ed25519 actors and executes 29 accepted operations while also proving rejection of bad signatures, author-chain gaps, stale rulesets, duplicate ballots, excessive delegation, unsafe reversal, contradicted ballot outcomes, revoked authority, and revoked keys before comparing reconstructed and stored roots.

## Agentic expansion

Compatible AI agents can iteratively import source records, classify them by topic/domain, add only evidence-bound relationships, traverse the resulting neighborhood, and run coverage checks. Conversation exports can be represented as `Conversation`, `Message`, and `AgentRun` records without treating model statements as authority. Conflicting statements remain separate records connected by explicit conflict or mischaracterization edges.

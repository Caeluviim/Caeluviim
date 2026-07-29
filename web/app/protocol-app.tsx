"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  PROTOCOL_DESCRIPTOR,
  type ProtocolResponse,
  type ProtocolSource,
} from "../lib/protocol";
import { KNOWLEDGE_DOMAINS } from "../lib/knowledge";

type Descriptor = typeof PROTOCOL_DESCRIPTOR;
type ServiceStatus = "connecting" | "ready" | "unavailable";
type KnowledgeRecordSummary = {
  id: string;
  recordType: string;
  label: string;
  content: string;
  domains: string[];
  sourceTitle: string;
  sourceUrl: string;
  sourceLocator: string;
};
type TopicCoverage = {
  topic: string;
  counts: Record<string, number>;
  coveredDomains: string[];
  missingDomains: string[];
  facetCounts: Record<string, number>;
  coveredFacets: string[];
  missingFacets: string[];
  recordCount: number;
  complete: boolean;
  records: KnowledgeRecordSummary[];
};
type LanguageForceResult = {
  protocolVersion: string;
  actCount: number;
  effectCount: number;
  recordCount: number;
  acts: Array<{
    id: string;
    label: string;
    actType: string;
    force: string;
    status: string;
    authorityStatus: string;
    deonticOperator: string;
  }>;
  effects: Array<{
    id: string;
    label: string;
    effectKind: string;
    operator: string;
    status: string;
    description: string;
  }>;
  records: KnowledgeRecordSummary[];
};
type DistrictSummary = {
  district_id: string;
  name: string;
  status: string;
  active_ruleset_id: string;
  accepted_count: number;
  history_root: string;
  state_root: string;
  updated_at: string;
};
type DistrictProof = {
  district_id: string;
  accepted_operation_count: number;
  stored_history_root: string;
  reconstructed_history_root: string;
  history_root_matches: boolean;
  stored_state_root: string;
  reconstructed_state_root: string;
  state_root_matches: boolean;
  state: {
    district: { name: string; status: string; active_ruleset_id: string; district_time: string; current_checkpoint_id: string | null };
    memberships: Record<string, { status: string }>;
    authorities: Record<string, { status: string }>;
    proposals: Record<string, { title: string; state: string }>;
    unresolved_conflicts: Record<string, unknown>;
  };
};
type DistrictSubmissionResult = {
  ok: boolean;
  result?: { operation_id: string; disposition: string; reason_codes: string[]; pending_conditions: string[] };
  errors?: Array<{ path: string; message: string }>;
};

const examples = [
  {
    label: "Legal proof",
    value:
      "Map this legal claim to its source, standing elements, procedural rule, risk, and verification status.",
  },
  {
    label: "Language",
    value:
      "Compare this term's competing definitions without flattening semantic conflict or losing source provenance.",
  },
  {
    label: "Commons",
    value:
      "Show how public access, collective stewardship, social obligation, and the global commons interact here.",
  },
];

function download(name: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  URL.revokeObjectURL(url);
}

function normalizeSource(title: string, url: string): ProtocolSource[] {
  const cleanTitle = title.trim();
  const cleanUrl = url.trim();
  if (!cleanTitle && !cleanUrl) return [];
  return [{ title: cleanTitle || cleanUrl, url: cleanUrl || undefined, kind: "user-supplied" }];
}

export function ProtocolApp({ descriptor }: { descriptor: Descriptor }) {
  const [prompt, setPrompt] = useState("");
  const [sourceTitle, setSourceTitle] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [response, setResponse] = useState<ProtocolResponse | null>(null);
  const [recent, setRecent] = useState<ProtocolResponse[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [copyLabel, setCopyLabel] = useState("Copy CSV");
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus>("connecting");
  const [topic, setTopic] = useState("");
  const [facets, setFacets] = useState("");
  const [coverage, setCoverage] = useState<TopicCoverage | null>(null);
  const [coverageBusy, setCoverageBusy] = useState(false);
  const [coverageError, setCoverageError] = useState("");
  const [languageQuery, setLanguageQuery] = useState("");
  const [languageJurisdiction, setLanguageJurisdiction] = useState("");
  const [languageResult, setLanguageResult] = useState<LanguageForceResult | null>(null);
  const [languageBusy, setLanguageBusy] = useState(false);
  const [languageError, setLanguageError] = useState("");
  const [districts, setDistricts] = useState<DistrictSummary[]>([]);
  const [selectedDistrictId, setSelectedDistrictId] = useState("");
  const [districtProof, setDistrictProof] = useState<DistrictProof | null>(null);
  const [districtBusy, setDistrictBusy] = useState(false);
  const [districtError, setDistrictError] = useState("");
  const [signedEnvelope, setSignedEnvelope] = useState("");
  const [submissionResult, setSubmissionResult] = useState<DistrictSubmissionResult | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/health").then((result) => {
        if (!result.ok) throw new Error("health");
        return result.json();
      }),
      fetch("/api/responses?limit=8").then((result) => {
        if (!result.ok) throw new Error("responses");
        return result.json();
      }),
      fetch("/api/districts?limit=12").then((result) => {
        if (!result.ok) throw new Error("districts");
        return result.json();
      }),
    ])
      .then(([health, history, districtList]) => {
        setServiceStatus(health.ok && health.storage === "d1" ? "ready" : "unavailable");
        setRecent(Array.isArray(history.responses) ? history.responses : []);
        const available = Array.isArray(districtList.districts) ? districtList.districts as DistrictSummary[] : [];
        setDistricts(available);
        setSelectedDistrictId(available[0]?.district_id ?? "");
      })
      .catch(() => setServiceStatus("unavailable"));
  }, []);

  const filledCount = useMemo(() => {
    if (!response) return 0;
    return response.columns.filter((column) => response.row[column.key]).length;
  }, [response]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!prompt.trim()) {
      setError("Enter a natural-language request.");
      return;
    }

    const sources = normalizeSource(sourceTitle, sourceUrl);
    setBusy(true);
    try {
      const httpResponse = await fetch("/api/respond", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ prompt, sources, district_id: selectedDistrictId || undefined }),
      });
      if (!httpResponse.ok) {
        throw new Error(`HTTP ${httpResponse.status}`);
      }
      const payload = (await httpResponse.json()) as ProtocolResponse;
      setResponse(payload);
      setRecent((current) => [payload, ...current.filter((item) => item.id !== payload.id)].slice(0, 8));
      setServiceStatus("ready");
    } catch {
      setError("The web service could not persist this response to the collective graph. Try again when it is available.");
      setServiceStatus("unavailable");
    } finally {
      setBusy(false);
    }
  }

  async function exploreTopic(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanTopic = topic.trim();
    if (!cleanTopic) {
      setCoverageError("Enter a topic to map.");
      return;
    }
    setCoverageBusy(true);
    setCoverageError("");
    const params = new URLSearchParams({
      topic: cleanTopic,
      domains: KNOWLEDGE_DOMAINS.join(","),
    });
    const cleanFacets = facets
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);
    if (cleanFacets.length) params.set("facets", cleanFacets.join(","));
    try {
      const result = await fetch(`/api/knowledge/coverage?${params}`);
      if (!result.ok) throw new Error(`HTTP ${result.status}`);
      setCoverage((await result.json()) as TopicCoverage);
    } catch {
      setCoverageError("The topic map could not be read from the knowledge service.");
    } finally {
      setCoverageBusy(false);
    }
  }

  async function exploreLanguageForce(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanQuery = languageQuery.trim();
    if (!cleanQuery) {
      setLanguageError("Enter language, a force, an effect, or a linked record to trace.");
      return;
    }
    setLanguageBusy(true);
    setLanguageError("");
    const params = new URLSearchParams({ q: cleanQuery, limit: "50" });
    if (languageJurisdiction.trim()) params.set("jurisdiction", languageJurisdiction.trim());
    try {
      const result = await fetch(`/api/language/graph?${params}`);
      if (!result.ok) throw new Error(`HTTP ${result.status}`);
      setLanguageResult((await result.json()) as LanguageForceResult);
    } catch {
      setLanguageError("The language-force graph could not be read.");
    } finally {
      setLanguageBusy(false);
    }
  }

  async function copyCsv() {
    if (!response) return;
    await navigator.clipboard.writeText(response.csv);
    setCopyLabel("Copied");
    window.setTimeout(() => setCopyLabel("Copy CSV"), 1400);
  }

  async function refreshDistricts(preferredDistrictId?: string) {
    const result = await fetch("/api/districts?limit=12");
    if (!result.ok) throw new Error(`HTTP ${result.status}`);
    const payload = await result.json() as { districts?: DistrictSummary[] };
    const available = Array.isArray(payload.districts) ? payload.districts : [];
    setDistricts(available);
    setSelectedDistrictId(preferredDistrictId ?? selectedDistrictId ?? available[0]?.district_id ?? "");
  }

  async function reconstructDistrict(districtId = selectedDistrictId) {
    if (!districtId) {
      setDistrictError("Select a district first.");
      return;
    }
    setDistrictBusy(true);
    setDistrictError("");
    try {
      const result = await fetch(`/api/districts/state?district_id=${encodeURIComponent(districtId)}&reconstruct=true`);
      if (!result.ok) throw new Error(`HTTP ${result.status}`);
      setDistrictProof(await result.json() as DistrictProof);
    } catch {
      setDistrictError("The accepted history could not be reconstructed from D1.");
      setDistrictProof(null);
    } finally {
      setDistrictBusy(false);
    }
  }

  async function submitSignedEnvelope(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setDistrictError("");
    setSubmissionResult(null);
    let operation: Record<string, unknown>;
    try {
      operation = JSON.parse(signedEnvelope) as Record<string, unknown>;
    } catch {
      setDistrictError("The signed operation envelope must be valid JSON.");
      return;
    }
    setDistrictBusy(true);
    try {
      const path = operation.operation_type === "DISTRICT_CREATE" ? "/api/districts" : "/api/districts/operations";
      const result = await fetch(path, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(operation),
      });
      const payload = await result.json() as DistrictSubmissionResult;
      setSubmissionResult(payload);
      const districtId = typeof operation.district_id === "string" ? operation.district_id : selectedDistrictId;
      await refreshDistricts(districtId);
      if (payload.ok && districtId) await reconstructDistrict(districtId);
    } catch {
      setDistrictError("The signed operation could not be submitted to the district validator.");
    } finally {
      setDistrictBusy(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">C</span>
          Caeluviim / Protocol 01
        </div>
        <div className="live-status" role="status">
          <span className="status-dot" aria-hidden="true" />
          <span>{serviceStatus === "ready" ? "knowledge graph ready" : serviceStatus}</span>
        </div>
      </header>

      <section className="hero" aria-labelledby="page-title">
        <div>
          <p className="eyebrow">Source-bound knowledge service</p>
          <h1 id="page-title">Query knowledge. <span>Ground every claim.</span></h1>
        </div>
        <div>
          <p className="hero-copy">
            AI platforms retrieve <strong>topic maps, connected records, and exact source provenance</strong> through Caeluviim, then return a full graph/table response in which every statement maps back to stored evidence.
          </p>
          <div className="capability-row" aria-label="Capabilities">
            <span className="capability">phone-ready</span>
            <span className="capability">remote MCP</span>
            <span className="capability">source-bound graph</span>
            <span className="capability">operative language</span>
            <span className="capability">visible coverage gaps</span>
          </div>
        </div>
      </section>

      <form className="explorer-panel" onSubmit={exploreTopic}>
        <div className="explorer-heading">
          <div>
            <p className="eyebrow">Knowledge graph explorer</p>
            <h2>Map a topic across every required domain.</h2>
          </div>
          <span>{KNOWLEDGE_DOMAINS.length} domains checked</span>
        </div>
        <div className="explorer-inputs">
          <label>
            <span>Topic</span>
            <input
              value={topic}
              onChange={(event) => setTopic(event.target.value)}
              placeholder="plasmapheresis"
            />
          </label>
          <label>
            <span>Required facets, comma-separated</span>
            <input
              value={facets}
              onChange={(event) => setFacets(event.target.value)}
              placeholder="plasma constituents, biological processes, dialysis analog, history"
            />
          </label>
          <button className="primary-button" disabled={coverageBusy} type="submit">
            {coverageBusy ? "Mapping…" : "Map topic →"}
          </button>
        </div>
        <button
          className="example-button explorer-example"
          type="button"
          onClick={() => {
            setTopic("plasmapheresis");
            setFacets(
              "plasma constituents, biological processes, biologics, medical procedure, dialysis analog, history, economics, law, regulation, international practice, academic literature",
            );
          }}
        >
          Load plasmapheresis coverage requirements
        </button>
        {coverageError ? <p className="error" role="alert">{coverageError}</p> : null}
        {coverage ? (
          <div className="coverage-output" aria-live="polite">
            <div className="coverage-summary">
              <strong>{coverage.recordCount}</strong>
              <span>connected records</span>
              <strong>{coverage.coveredDomains.length}/{KNOWLEDGE_DOMAINS.length}</strong>
              <span>domains covered</span>
              <b data-complete={coverage.complete}>{coverage.complete ? "coverage target met" : "gaps remain"}</b>
            </div>
            <div className="table-scroll" tabIndex={0}>
              <table className="coverage-table">
                <thead><tr><th>Domain</th><th>Records</th><th>Status</th></tr></thead>
                <tbody>
                  {KNOWLEDGE_DOMAINS.map((domain) => (
                    <tr key={domain}>
                      <td>{domain}</td>
                      <td>{coverage.counts[domain] ?? 0}</td>
                      <td data-covered={(coverage.counts[domain] ?? 0) > 0}>
                        {(coverage.counts[domain] ?? 0) > 0 ? "covered" : "gap"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {Object.keys(coverage.facetCounts).length ? (
              <div className="facet-list">
                {Object.entries(coverage.facetCounts).map(([facet, count]) => (
                  <span key={facet} data-covered={count > 0}>{facet}: {count || "gap"}</span>
                ))}
              </div>
            ) : null}
            <div className="knowledge-records">
              {coverage.records.slice(0, 20).map((record) => (
                <article key={record.id}>
                  <small>{record.recordType} · {record.domains.join(" / ")}</small>
                  <h3>{record.label}</h3>
                  <p>{record.content}</p>
                  <a href={record.sourceUrl} target="_blank" rel="noreferrer">
                    {record.sourceTitle} · {record.sourceLocator}
                  </a>
                </article>
              ))}
            </div>
          </div>
        ) : null}
      </form>

      <form className="explorer-panel" onSubmit={exploreLanguageForce}>
        <div className="explorer-heading">
          <div>
            <p className="eyebrow">Language / force / effect graph</p>
            <h2>Trace what words mean, claim, authorize, and actually change.</h2>
          </div>
          <span>expression ≠ content ≠ effect</span>
        </div>
        <div className="explorer-inputs">
          <label>
            <span>Language, force, effect, actor, or target</span>
            <input
              value={languageQuery}
              onChange={(event) => setLanguageQuery(event.target.value)}
              placeholder="revocation, obligation, disputed definition, permit"
            />
          </label>
          <label>
            <span>Jurisdiction, optional</span>
            <input
              value={languageJurisdiction}
              onChange={(event) => setLanguageJurisdiction(event.target.value)}
              placeholder="Minnesota, federal, treaty, protocol district"
            />
          </label>
          <button className="primary-button" disabled={languageBusy} type="submit">
            {languageBusy ? "Tracing…" : "Trace force →"}
          </button>
        </div>
        <button
          className="example-button explorer-example"
          type="button"
          onClick={() => {
            setLanguageQuery("definition obligation revocation permission authority");
            setLanguageJurisdiction("");
          }}
        >
          Load operative-language trace
        </button>
        {languageError ? <p className="error" role="alert">{languageError}</p> : null}
        {languageResult ? (
          <div className="coverage-output" aria-live="polite">
            <div className="coverage-summary">
              <strong>{languageResult.actCount}</strong><span>language acts</span>
              <strong>{languageResult.effectCount}</strong><span>operative effects</span>
              <strong>{languageResult.recordCount}</strong><span>source-bound records</span>
              <b data-complete={languageResult.effectCount > 0}>
                {languageResult.effectCount > 0 ? "effects traced" : "no effect asserted"}
              </b>
            </div>
            <div className="table-scroll" tabIndex={0}>
              <table className="coverage-table">
                <thead>
                  <tr><th>Language act</th><th>Type / force</th><th>Modality</th><th>Authority / status</th></tr>
                </thead>
                <tbody>
                  {languageResult.acts.map((act) => (
                    <tr key={act.id}>
                      <td>{act.label}</td>
                      <td>{act.actType} / {act.force}</td>
                      <td>{act.deonticOperator}</td>
                      <td data-covered={act.authorityStatus === "verified"}>
                        {act.authorityStatus} / {act.status}
                      </td>
                    </tr>
                  ))}
                  {!languageResult.acts.length ? (
                    <tr><td colSpan={4}>No recorded language act matched this trace.</td></tr>
                  ) : null}
                </tbody>
              </table>
            </div>
            {languageResult.effects.length ? (
              <div className="knowledge-records">
                {languageResult.effects.map((effect) => (
                  <article key={effect.id}>
                    <small>{effect.effectKind} · {effect.operator} · {effect.status}</small>
                    <h3>{effect.label}</h3>
                    <p>{effect.description}</p>
                  </article>
                ))}
              </div>
            ) : null}
            <div className="facet-list">
              <a
                className="example-button"
                href={`/api/language/graph?q=${encodeURIComponent(languageQuery)}&jurisdiction=${encodeURIComponent(languageJurisdiction)}&format=jsonld`}
              >
                JSON-LD
              </a>
              <a
                className="example-button"
                href={`/api/language/graph?q=${encodeURIComponent(languageQuery)}&jurisdiction=${encodeURIComponent(languageJurisdiction)}&format=nquads`}
              >
                N-Quads
              </a>
            </div>
          </div>
        ) : null}
      </form>

      <section className="district-panel" aria-labelledby="district-title">
        <div className="district-heading">
          <div>
            <p className="eyebrow">Districted Authority Protocol / v0.2</p>
            <h2 id="district-title">Verify authority from signed history.</h2>
          </div>
          <span>{districts.length} district{districts.length === 1 ? "" : "s"} visible</span>
        </div>

        <div className="district-controls">
          <label>
            <span>District</span>
            <select
              value={selectedDistrictId}
              onChange={(event) => {
                setSelectedDistrictId(event.target.value);
                setDistrictProof(null);
                setSubmissionResult(null);
              }}
            >
              {!districts.length ? <option value="">No signed district yet</option> : null}
              {districts.map((district) => (
                <option value={district.district_id} key={district.district_id}>
                  {district.name} · {district.accepted_count} operations
                </option>
              ))}
            </select>
          </label>
          <button className="primary-button" type="button" disabled={districtBusy || !selectedDistrictId} onClick={() => reconstructDistrict()}>
            {districtBusy ? "Checking…" : "Reconstruct + verify →"}
          </button>
        </div>

        {districtProof ? (
          <div className="district-proof" aria-live="polite">
            <div className="root-proof">
              <span data-match={districtProof.history_root_matches}>history root {districtProof.history_root_matches ? "matches" : "mismatch"}</span>
              <code>{districtProof.reconstructed_history_root}</code>
            </div>
            <div className="root-proof">
              <span data-match={districtProof.state_root_matches}>state root {districtProof.state_root_matches ? "matches" : "mismatch"}</span>
              <code>{districtProof.reconstructed_state_root}</code>
            </div>
            <div className="district-stats">
              <div><strong>{districtProof.accepted_operation_count}</strong><span>accepted operations</span></div>
              <div><strong>{Object.values(districtProof.state.memberships).filter((member) => member.status === "active").length}</strong><span>active members</span></div>
              <div><strong>{Object.values(districtProof.state.authorities).filter((authority) => authority.status === "active").length}</strong><span>active authorities</span></div>
              <div><strong>{Object.keys(districtProof.state.unresolved_conflicts).length}</strong><span>unresolved conflicts</span></div>
            </div>
            <div className="proposal-state-list">
              {Object.entries(districtProof.state.proposals).map(([proposalId, proposal]) => (
                <div key={proposalId}>
                  <span>{proposal.title || proposalId}</span>
                  <b data-state={proposal.state}>{proposal.state}</b>
                </div>
              ))}
              {!Object.keys(districtProof.state.proposals).length ? <p>No proposal state has been derived.</p> : null}
            </div>
            <p className="district-meta">
              Ruleset <code>{districtProof.state.district.active_ruleset_id}</code> · district time {districtProof.state.district.district_time} · checkpoint {districtProof.state.district.current_checkpoint_id ?? "genesis"}
            </p>
          </div>
        ) : (
          <p className="district-empty">
            Select a district and replay its accepted operations. The stored projection is accepted only when both recomputed roots match.
          </p>
        )}

        <form className="signed-operation-form" onSubmit={submitSignedEnvelope}>
          <div>
            <h3>Submit a signed operation</h3>
            <p>The server validates the author signature, key chain, causal chain, membership, scoped authority, active ruleset, transition, and conflicts. It never signs for the actor.</p>
          </div>
          <label htmlFor="signed-envelope" className="sr-only">Signed DAP operation envelope JSON</label>
          <textarea
            id="signed-envelope"
            value={signedEnvelope}
            onChange={(event) => setSignedEnvelope(event.target.value)}
            placeholder={'{"protocol_version":"dap/0.2","operation_id":"op:z…","signature":{"algorithm":"Ed25519","value":"…"}}'}
            maxLength={1_000_000}
          />
          <div className="signed-operation-actions">
            <button className="secondary-button" type="submit" disabled={districtBusy || !signedEnvelope.trim()}>
              Validate + submit
            </button>
            <a href="/api/dap" target="_blank" rel="noreferrer">operation schema + signed vectors ↗</a>
          </div>
          {submissionResult?.result ? (
            <div className="submission-result" data-ok={submissionResult.ok}>
              <strong>{submissionResult.result.disposition}</strong>
              <code>{submissionResult.result.operation_id}</code>
              {submissionResult.result.reason_codes.length ? <span>{submissionResult.result.reason_codes.join(" · ")}</span> : null}
              {submissionResult.result.pending_conditions.length ? <span>{submissionResult.result.pending_conditions.join(" · ")}</span> : null}
            </div>
          ) : null}
          {submissionResult?.errors?.length ? (
            <p className="error">{submissionResult.errors.map((item) => `${item.path}: ${item.message}`).join(" · ")}</p>
          ) : null}
          {districtError ? <p className="error" role="alert">{districtError}</p> : null}
        </form>
      </section>

      <form className="composer" onSubmit={submit}>
        <div className="section-label">
          <span>Reference response formatter</span>
          <b>{descriptor.categories.length} categories always</b>
        </div>
        <label htmlFor="prompt" className="sr-only">Natural-language request</label>
        <textarea
          id="prompt"
          className="prompt"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="Tell the protocol what you are working through…"
          maxLength={10_000}
        />

        <div className="source-area" aria-label="Optional provenance source">
          <label className="sr-only" htmlFor="source-title">Source title</label>
          <input
            id="source-title"
            className="source-input"
            value={sourceTitle}
            onChange={(event) => setSourceTitle(event.target.value)}
            placeholder="Optional source title"
          />
          <label className="sr-only" htmlFor="source-url">Source URL</label>
          <input
            id="source-url"
            className="source-input"
            value={sourceUrl}
            onChange={(event) => setSourceUrl(event.target.value)}
            placeholder="https://source.example/document"
            inputMode="url"
          />
        </div>

        <div className="composer-actions">
          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "Publishing…" : "Publish response →"}
          </button>
          <div className="examples" aria-label="Example requests">
            {examples.map((example) => (
              <button
                className="example-button"
                type="button"
                key={example.label}
                onClick={() => setPrompt(example.value)}
              >
                {example.label}
              </button>
            ))}
          </div>
        </div>
        {error ? <p className="error" role="alert">{error}</p> : null}
        <p className="public-note">This reference formatter demonstrates the table/event representation. Provenance-complete knowledge enters through the stricter MCP ingestion tool, which requires an exact source locator, excerpt, hashes, and construction rule.</p>
      </form>

      {response ? (
        <section className="output-panel" aria-labelledby="output-title">
          <div className="output-header">
            <div>
              <p className="eyebrow">High-dimensional response</p>
              <h2 id="output-title">All categories. Ordered by relevance.</h2>
              <p className="output-meta">
                {response.event?.eventId ?? response.id} · schema {response.schemaVersion} · {filledCount}/{response.columns.length} populated
              </p>
            </div>
            <span className="persist-badge">
              {response.event?.ingestionStatus === "projected" ? "event + graph projected" : "projection pending"}
            </span>
          </div>

          <div className="table-scroll" tabIndex={0} aria-label="Scrollable response table">
            <table className="protocol-table">
              <thead>
                <tr>
                  {response.columns.map((column) => (
                    <th key={column.key} scope="col" data-filled={Boolean(response.row[column.key])}>
                      {column.label}
                      <span className="category-group">{column.group}</span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr>
                  {response.columns.map((column) => (
                    <td key={column.key}>
                      {response.row[column.key] || <span className="empty-cell" aria-label="Empty category">□</span>}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>

          <div className="result-actions">
            <button className="secondary-button" type="button" onClick={copyCsv}>{copyLabel}</button>
            <button
              className="secondary-button"
              type="button"
              onClick={() => download("caeluviim-response.csv", response.csv, "text/csv;charset=utf-8")}
            >
              Download CSV
            </button>
            <button
              className="secondary-button"
              type="button"
              onClick={() => download("caeluviim-response-event.json", JSON.stringify(response, null, 2), "application/json")}
            >
              Download graph event
            </button>
          </div>

          <div className="graph-strip" aria-label="Graph output summary">
            <div className="graph-stat"><strong>{response.graph.nodes.length}</strong><span>graph nodes</span></div>
            <div className="graph-stat"><strong>{response.graph.edges.length}</strong><span>typed edges</span></div>
            <div className="graph-stat"><strong>{response.event?.partitionKey ?? "pending"}</strong><span>event partition</span></div>
          </div>
        </section>
      ) : null}

      <section className="collective-panel" aria-labelledby="collective-title">
        <div className="collective-heading">
          <div>
            <p className="eyebrow">Response audit ledger</p>
            <h2 id="collective-title">Mapped outputs preserved as events.</h2>
          </div>
          <span>{recent.length} recent</span>
        </div>
        {recent.length ? (
          <div className="ledger-list">
            {recent.map((item) => (
              <button className="ledger-item" key={item.id} type="button" onClick={() => setResponse(item)}>
                <span>{item.prompt}</span>
                <small>{new Date(item.createdAt).toLocaleString()} · {item.graph.nodes.length} nodes</small>
              </button>
            ))}
          </div>
        ) : (
          <p className="ledger-empty">The first mapped response will begin the audit ledger.</p>
        )}
      </section>

      <section className="architecture-panel" aria-labelledby="architecture-title">
        <div>
          <p className="eyebrow">Open HTTP surface</p>
          <h2 id="architecture-title">One protocol. Any phone or model.</h2>
          <p className="architecture-copy">
            The <strong>source-bound graph is the shared knowledge container</strong>. Any compatible AI platform connects to <code>/mcp</code>, searches and traverses the graph, checks topic coverage, and submits proposed statements to the grounding mapper. The response-event ledger is an audit trail, not the knowledge repository itself.
          </p>
        </div>
        <div className="route-list" aria-label="HTTP endpoints">
          {descriptor.endpoints.map((endpoint) => (
            <div className="route" key={`${endpoint.method}:${endpoint.path}`}>
              <b>{endpoint.method}</b>
              <span>{endpoint.path} — {endpoint.purpose}</span>
            </div>
          ))}
        </div>
      </section>

      <footer className="footer">
        <span>{descriptor.name} · v{descriptor.version}</span>
        <span>Source-bound records · evidence-bound edges · every answer statement mapped</span>
      </footer>
    </main>
  );
}

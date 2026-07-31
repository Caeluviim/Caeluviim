# Project Content Inclusion and Consolidation Rule

**Rule ID:** CAELUVIIM-OPS-CONTENT-INCLUSION-001  
**Version:** 1.0.0  
**Status:** Effective by architect directive  
**Scope:** GitHub repository, graph-ingestion corpus, issues, pull requests, architecture records, legal records, governance records, operations records, and consolidation submissions.

## 1. Governing rule

Content may enter the formal Caeluviim project record only when it has a durable and identifiable relationship to the project’s architecture, implementation, legal or research corpus, governance, validation, evidence, operations, or accountable work.

Transient conversation context, personal scheduling information, temporary tooling limits, generic commentary, and other material that does not create or modify durable project state must not be formalized in GitHub or the graph.

When relevance, destination, scope, canonical status, or intended treatment is uncertain, no repository or graph write may occur until the architect is asked a targeted question and supplies direction.

## 2. Mandatory inclusion test

Content is relevant for formal inclusion only when at least one of the following conditions is satisfied and the proposed destination can be identified:

1. **Architecture:** It defines, changes, constrains, extends, or conflicts with a project primitive, ontology, schema, relation, invariant, protocol, system boundary, or design rule.
2. **Implementation:** It adds or changes executable code, configuration, migrations, tests, deployment procedures, security controls, backup procedures, or runtime behavior.
3. **Governance:** It records an authorized decision, ratification state, veto, validation requirement, role, authority, appeal process, or change-control rule.
4. **Legal or research corpus:** It contributes a sourced legal theory, authority, claim model, evidence structure, research finding, or analytical framework intended for later retrieval, comparison, litigation support, or protocol development.
5. **Evidence or provenance:** It preserves source material, an evidentiary event, provenance, hashes, chain of custody, validation results, or a revision affecting an existing claim.
6. **Operations:** It defines a durable and repeatable process necessary to operate, secure, validate, recover, ingest, monitor, or maintain the system.
7. **Accountable work:** It identifies a concrete defect, deliverable, acceptance criterion, dependency, decision required, or task whose completion changes project state.
8. **Pending consolidation:** It contains materially significant project content that has not yet been encoded, provided that it is explicitly labeled as proposed, unvalidated, or pending consolidation.

Passing one condition is necessary but not sufficient. The content must also satisfy all requirements in Section 3.

## 3. Required conditions for formal inclusion

Before formal inclusion, the content must have:

- a defined project relationship;
- an appropriate repository or graph destination;
- a stable identifier or file path;
- provenance identifying where the material came from;
- a status such as proposed, validated, ratified, contested, superseded, or rejected;
- enough specificity to be retrieved and acted upon;
- no unresolved ambiguity about whether the architect intended formal inclusion;
- no duplication of an existing canonical record unless the new record explicitly revises, supersedes, or conflicts with it.

Content that lacks any required condition must remain outside the formal project record until corrected or directed by the architect.

## 4. Explicit exclusions

The following content is not relevant for formal inclusion unless the architect expressly directs otherwise or it is transformed into a durable project requirement:

- personal reminders, appointments, availability, or scheduling notes;
- temporary usage limits, rate limits, reset times, subscription constraints, or transient tool outages;
- conversational acknowledgments, apologies, interpersonal commentary, or response-style preferences that do not define a project protocol;
- generic brainstorming with no identified claim, task, decision, source, or destination;
- repeated copies of existing content without a revision relation;
- unsupported factual assertions presented as established fact;
- speculation that is not labeled as a proposal, hypothesis, prediction, or contested claim;
- operational narration that merely reports what an assistant is doing;
- incidental biographical information with no defined evidentiary or project function;
- material whose only relevance is that it occurred during a project conversation;
- reminders to use a tool later, unless the reminder is converted into an approved recurring operational control;
- private or sensitive information that is unnecessary for the project purpose.

The fact that information may affect when work can occur does not by itself make that information project content.

## 5. Destination rule

Relevant content must be placed in the destination corresponding to its function:

| Content function | Formal destination |
|---|---|
| Normative architecture or protocol | `docs/architecture/` plus ingestion manifest when graph-relevant |
| Legal theory, authority, or litigation model | `docs/legal/` plus ingestion manifest |
| Repeatable operational procedure | `docs/operations/` |
| Production graph content | `ingest/manifests/` |
| Schema or validation contract | `schemas/`, `ontology/`, or `shapes/` |
| Executable implementation | source-code directory with tests |
| Concrete defect or bounded work item | GitHub issue |
| Proposed code or document change requiring review | branch and pull request |
| Temporary reminder or personal scheduling note | outside GitHub and outside the graph |
| Unresolved but potentially material content | pending-consolidation queue only after architect approval |

A GitHub issue must not be used as a general memory store.

## 6. Ambiguity and architect-confirmation rule

Ambiguity exists when there is reasonable uncertainty about any of the following:

- whether the content is materially connected to Caeluviim;
- whether the content is transient context or durable project state;
- whether it should be canonical, proposed, evidentiary, operational, or excluded;
- which repository path, graph label, relation, or workflow object is appropriate;
- whether the content duplicates or revises an existing record;
- whether the architect intended a statement to become a formal project directive;
- whether sensitive or personal information is necessary for the project purpose.

When ambiguity exists:

1. stop before writing to GitHub, the graph, Notion, or another formal project system;
2. state the proposed classification and intended destination;
3. identify the precise ambiguity;
4. ask the architect one focused question that can resolve it;
5. perform no formal inclusion until the architect answers;
6. record the architect’s answer as the authority for the subsequent classification.

The required question format is:

> **Proposed classification:** [classification]  
> **Proposed destination:** [destination or exclusion]  
> **Ambiguity:** [single precise uncertainty]  
> **Decision required:** Should this material be formally included as proposed, included elsewhere, or excluded?

Silence, urgency, assistant preference, or convenience must not be treated as approval.

## 7. Material-content submission rule

When the assistant produces content of material significance to Caeluviim and its relevance is unambiguous, the assistant must concurrently:

1. preserve the source content;
2. assign a stable identifier;
3. record provenance and status;
4. submit it to the proper repository location;
5. create or update an ingestion manifest when graph consolidation is required;
6. validate the resulting structure to the extent available;
7. report the destination, commit, validation status, and any unresolved defect.

When relevance is ambiguous, the assistant must ask the architect before submission rather than creating a speculative repository record.

## 8. Prohibited inference rules

The following inferences are prohibited:

- conversation occurrence does not imply project relevance;
- project relevance does not imply GitHub-issue relevance;
- a future date does not imply a task;
- a tool limitation does not imply a project dependency;
- a useful idea does not imply canonical status;
- a legal argument does not imply controlling authority;
- a repository write does not imply graph ingestion;
- graph ingestion does not imply validation or ratification;
- architect discussion does not imply architect approval unless the instruction is express or confirmed.

## 9. Correction procedure

If irrelevant or ambiguously classified content is formally included:

1. stop any downstream consolidation;
2. mark the record non-canonical;
3. close, revert, supersede, or remove it using the repository’s audit-preserving procedure;
4. document the classification error and applied correction;
5. verify that no active manifest, graph projection, work plan, or dependency still treats it as project state;
6. report the correction and validation result.

A failure report is incomplete unless it identifies either the correction applied or the precise action required to complete correction.

## 10. Decision matrix

| Question | Yes | No or uncertain |
|---|---|---|
| Does the material change or evidence durable project state? | Continue | Exclude or ask |
| Does it fit an inclusion category in Section 2? | Continue | Exclude |
| Is a formal destination identifiable? | Continue | Ask |
| Is provenance available? | Continue | Hold |
| Is status explicitly labeled? | Continue | Label before inclusion |
| Is the architect’s intent to formalize clear? | Continue | Ask |
| Is it non-duplicative or explicitly revisionary? | Include | Revise, link, or exclude |
| Can validation be performed? | Validate and report | Mark validation pending |

## 11. Canonical determination

**Formal inclusion is reserved for durable, attributable, status-labeled content that changes, constrains, evidences, validates, or operationalizes Caeluviim. Transient context remains outside the project record. Any reasonable uncertainty requires architect confirmation before formal inclusion.**

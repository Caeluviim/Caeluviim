# Caeluviim Relational Definition Standard

**Status:** Proposed v0.1.0  
**Function:** Establish the minimum completeness criterion for any canonical definition admitted to Caeluviim.

## 1. Governing principle

A definition is not a compressed synonym, isolated genus-and-differentia formula, or bare text property. A definition is a provenance-bearing relational field that identifies how a term emerged, what distinctions it performs, which relations constitute its meaning, where it applies, what it excludes, how it changes under context, and how competing formulations remain visible.

No canonical term is definition-complete merely because it has a label and one explanatory sentence.

## 2. Definition-completeness criterion

A canonical definition MUST contain or explicitly mark the absence of every field below.

| Field | Required content |
|---|---|
| Stable identity | Canonical URI, preferred label, version, language tag, and governance status. |
| Lexical forms | Preferred form, inflections, transliterations, abbreviations, historical spellings, aliases, and deprecated forms. |
| Etymology | Earliest recoverable forms; source language and script; component morphemes; literal senses; transmission path; semantic shifts; earliest attested use where supportable; etymological uncertainty and competing accounts. |
| Source definition occurrences | Immutable quotations or exact source spans for every supplied, historical, disciplinary, corrected, and synthesized definition occurrence. |
| Intensional nucleus | The minimal positive constraints without which an instance is not an instance of the concept. |
| Extensional field | Paradigm instances, marginal instances, counterexamples, and presently unresolved cases. |
| Relational constitution | Relations necessary to instantiate the concept; participants, objects, processes, condition fields, temporal dependencies, and consequence structure. |
| Semantic neighborhood | Near-synonyms, analogues, superordinate and subordinate concepts, co-hyponyms, collocations, associated frames, and multilingual anchors. |
| Contrast field | Antonyms, privative oppositions, contrary and contradictory concepts, category mistakes, false friends, and misleading substitutions. |
| Boundary conditions | Inclusion criteria, exclusion criteria, threshold conditions, failure conditions, and purpose-indexed boundary variations. |
| Context and indexicality | Domain, jurisdiction, community, speaker position, temporal state, medium, and other context variables that materially alter application. |
| Diachronic development | Historical sequence of materially different senses, continuities, ruptures, appropriations, and disciplinary redefinitions. |
| Framework mappings | How the concept is represented in relevant philosophical, scientific, linguistic, legal, cultural, technical, and Caeluviim-specific frameworks. |
| Formal realization | Logical formula, graph pattern, typed signature, domain/range, cardinality, constraints, inference classification, and computability limits where applicable. |
| Operationalization | Observable indicators, tests, measurements, procedures, decision rules, and known proxy failures. |
| Phenomenological profile | How the concept may be lived, perceived, felt, enacted, or encountered where materially applicable. |
| Normative and institutional effects | Rights, duties, authority, recognition, benefit, burden, sanctions, classifications, and power effects produced by applying the definition. |
| Provenance and contribution | Originating persons, dialogic contributors, cultural inheritance, infrastructural contribution, source authorities, transformations, and validation history. |
| Contestation field | Competing definitions, irreconcilable accounts, paradoxes, open questions, objections, and alternative classifications. |
| Revision history | Prior versions, correction events, supersession relations, reasons, evidence changes, and preserved historical effect. |
| Examples | Positive, negative, boundary, adversarial, cross-cultural, and cross-scale examples. |
| Epistemic status | Supplied, synthesized, inferred, verified, contested, unresolved, deprecated, or ratified, with confidence and assessment basis where appropriate. |

## 3. Relational field requirement

For concept `x`, a canonical definition is represented as a structured field rather than a string:

```text
D(x, Γ_t, p) = ⟨
  lexical-history,
  source-occurrences,
  intensional-constraints,
  extension,
  constitutive-relations,
  semantic-neighborhood,
  contrasts,
  boundaries,
  framework-mappings,
  formalization,
  operationalization,
  effects,
  provenance,
  contestations,
  revisions
⟩
```

`Γ_t` is the versioned condition field under which the definition is evaluated. `p` is the purpose or use-context that makes particular boundaries operative. Neither variable permits silent redefinition: materially different configurations produce separate definition states linked by revision, contrast, specialization, or contextualization relations.

## 4. Definition modes

| Mode | Meaning |
|---|---|
| Lexical | Records established language use and attested sense distributions. |
| Stipulative | Introduces a declared use for a bounded purpose without claiming historical or universal usage. |
| Precising | Narrows an indeterminate term for an operational domain. |
| Theoretical | Locates a concept inside an explanatory framework. |
| Operational | Specifies tests, observations, or procedures used to classify instances. |
| Legal or institutional | Specifies an authority-bound classification with consequences. |
| First-person or phenomenological | Preserves an avowed or lived meaning without converting it into an unrestricted external fact. |
| Cross-linguistic | Maps partially overlapping semantic fields without presuming exact equivalence. |
| Caeluviim canonical | Reconciles prior modes into a versioned relational field while preserving their differences and provenance. |

Every definition occurrence MUST identify its mode. A Caeluviim canonical definition MUST NOT erase differences among modes.

## 5. Etymology requirements

Etymology is evidence, not destiny. Historical origin does not by itself determine present meaning.

A conforming etymology record MUST:

1. separate attested forms from reconstructions;
2. identify scripts and language stages;
3. preserve morpheme boundaries where supportable;
4. distinguish literal historical sense from later technical senses;
5. identify borrowing and translation paths;
6. expose disputed or folk-etymological accounts;
7. cite the source used for each historical assertion;
8. avoid asserting exact semantic equivalence across languages merely because terms share a gloss;
9. connect each semantic shift to a dated or ordered definition occurrence where evidence permits;
10. mark missing evidence as unresolved rather than filling the gap generatively.

## 6. Relation inventory for definitions

Minimum relations include:

- `HAS_DEFINITION_OCCURRENCE`
- `HAS_ETYMOLOGICAL_FORM`
- `DERIVED_LEXICALLY_FROM`
- `BORROWED_THROUGH`
- `UNDERWENT_SEMANTIC_SHIFT`
- `HAS_INTENSIONAL_CONSTRAINT`
- `HAS_PARADIGM_INSTANCE`
- `HAS_BOUNDARY_INSTANCE`
- `EXCLUDES_INSTANCE`
- `REQUIRES_RELATION`
- `HAS_SUPERORDINATE`
- `HAS_SUBORDINATE`
- `NEAR_SYNONYM_OF`
- `CONTRASTS_WITH`
- `CONTRADICTS`
- `ANALOG_OF`
- `TRANSLATES_PARTIALLY_TO`
- `EVOKES_FRAME`
- `SPECIALIZED_IN_DOMAIN`
- `OPERATIVE_UNDER_PURPOSE`
- `FORMALIZED_BY`
- `OPERATIONALIZED_BY`
- `PRODUCES_NORMATIVE_EFFECT`
- `CONTESTED_BY`
- `REVISED_BY`
- `SUPERSEDES`
- `HAS_PROVENANCE`

Where the current graph vocabulary lacks one of these relations, the relation remains a declared vocabulary requirement and MUST NOT be flattened into an ambiguous generic edge.

## 7. Completion states

| State | Criterion |
|---|---|
| `lexical_stub` | Label and stable identity only. Not a definition. |
| `source_bound` | At least one immutable source definition occurrence and provenance. |
| `relational_partial` | Intensional nucleus, key relations, boundaries, contrasts, and status present; one or more required fields explicitly pending. |
| `relational_complete_candidate` | Every required field populated or explicitly resolved as inapplicable, unknown, or contested. |
| `validated_definition` | Candidate checked against sources, formal constraints, examples, and contestations. |
| `ratified_definition` | Exact version accepted through applicable Caeluviim governance. |

The prior CE submission is classified `relational_partial`, not definition-complete.

## 8. Non-erasure and competing definitions

Conflicting definitions remain separate definition states. Reconciliation may produce a higher-order mapping, but it cannot overwrite:

- historical source wording;
- disciplinary differences;
- community-specific meanings;
- first-person self-definition;
- legal definitions and their jurisdictional scope;
- unresolved contradictions;
- prior Caeluviim versions.

A canonical definition is therefore a navigable topology of definition states, not a winner-take-all sentence.

## 9. Application to consolidation

Every consolidation that introduces or materially revises a concept MUST either:

1. supply a relational-definition record meeting this standard; or
2. mark the concept as `definition_pending` and create an explicit completion task.

A graph-ingestion manifest containing a one-sentence `text` field may preserve a Claim, but it does not satisfy the canonical-definition criterion.

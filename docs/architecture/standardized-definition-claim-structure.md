# Standardized Definition Claim Structure

**Status:** Consolidated architectural correction v0.3.0  
**Parent standards:**
- `docs/architecture/relational-definition-standard.md`
- `docs/architecture/universal-claim-card-node-standard.md`
- `docs/architecture/definition-claim-nesting-and-composition.md`
- `docs/architecture/definition-claim-linguistic-etymological-multilingual-glyph-structure.md`
- `docs/architecture/host-language-lexical-decentering-and-multilingual-incorporation.md`

## 1. Governing rule

Every protocol-relevant conception MUST be represented by one standardized, recursively compositional Definition Claim field.

A Definition Claim is not a summary sentence with optional metadata. It is the canonical Claim structure through which a conception is identified, synthesized, bounded, linguistically manifested, historically developed, translated, symbolized, sourced, contested, operationalized, governed, and revised.

```text
CompleteDefinitionField(c)
:= RootDefinitionClaim(c)
 + NestedConceptualClaimGraph(c)
 + LinguisticEtymologicalGraph(c)
 + MultilingualGraph(c)
 + GlyphEmojiRiderGraph(c)
 + FormalOperationalEvidentiaryGraphs(c)
 + HistoricalConflictConsequenceGraphs(c)
 + ProvenanceGovernanceAndRevision(c)
```

All Definition Claims use one standard structural grammar. They do not all contain equal quantities of local content.

```text
DefinitionStructure(c)
⊆ StandardDefinitionGrammar
⊆ UniversalClaimStructure
```

The Caeluviim rider is one invariant protocol lexicon used across every host language. The host language supplies grammar, explanation, local accessibility, and search glosses; it does not replace the rider's canonical protocol lexemes.

## 2. Conception and manifestation distinctions

The architecture MUST preserve:

```text
canonical conception
≠ root definition sentence
≠ canonical rider lexeme
≠ host-language gloss
≠ source-language lexical Claim
≠ multilingual composite
≠ additional multilingual anchor
≠ glyph or emoji-rider manifestation
≠ scoped Claim occurrence
```

The canonical conception is the stable Claim identity. Words, translations, composites, signs, and glyphs are sourced manifestations and relations through which the conception becomes available.

A lexical etymology belongs to a particular lexical manifestation, language, script, community, and history. It must not be attributed directly to an abstract language-independent conception without that distinction.

## 3. Mandatory definition kernel

Every registered Definition Claim MUST possess the following kernel.

| Field | Requirement |
|---|---|
| `claim_id` | Stable, globally unique root Claim identifier. |
| `version` | Non-erasing version identifier. |
| `canonical_conception` | Language-independent conception reference. |
| `canonical_rider_lexeme` | Invariant ratified protocol word used across every host language. |
| `rider_lexeme_class` | `attested`, `revived`, `reconstructed`, `protocol_coinage`, or `multilingual_composite`. |
| `host_language_glosses` | Searchable and explanatory local-language labels that do not replace the rider lexeme. |
| `preferred_label` | Current display manifestation with language, script, provenance, and status. |
| `exact_definition_claim` | Concise root Claim compressing the current synthesis. |
| `nested_claim_graph` | Full material recursive Claim composition required to reconstruct and use the definition. |
| `linguistic_etymological_graph` | Lexical identities, morphology, etymologies, semantic histories, usage, nomenclature, and source Claims. |
| `multilingual_graph` | Language anchors, translation relations, partial equivalence, non-equivalence, community provenance, and unresolved expansion. |
| `glyph_emoji_rider_graph` | Glyph identities, Unicode or custom forms, component semantics, legacy meanings, collisions, accessibility, governance, and current assignment state. |
| `declared_scope` | Domain, purpose, jurisdiction, scale, time, and participant field. |
| `relational_configuration` | What the conception distinguishes and how it relates included loci and Claims. |
| `inclusions` | Material membership Claims. |
| `exclusions` | Material nonmembership Claims. |
| `boundary_conditions` | Thresholds, edge cases, qualifications, exceptions, and application tests. |
| `principal_relations` | Typed external relations not already represented as nested composition. |
| `provenance` | Claiming loci, sources, citations, contribution history, and transformations. |
| `epistemic_status` | Proposed, source-bound, contested, consolidated, ratified, superseded, or another declared state. |
| `governance_state` | Authority, permissions, ratification scope, and review process. |
| `completeness_claim` | Represented closure, imported dependencies, unresolved Claims, and material omissions. |

Unknown, unassigned, or unavailable content MUST be represented by explicit unresolved Claims. Silent omission does not satisfy the kernel.

A card may exist before rider ratification as `root_captured`, `nested_structure_drafted`, `lexeme_candidates_identified`, `lexeme_selected`, `lexeme_source_bound`, or `multilingual_implementation_pending`, but it is not formally incorporated.

## 4. Formal incorporation gate

```text
FormallyIncorporated(d)
:= RootAndNestedStructureImplemented(d)
 ∧ CanonicalRiderLexemeSelectedOrComposed(d)
 ∧ LexicalSourceAndConstructionClaimsBound(d)
 ∧ HostLanguageGlossesDeclared(d)
 ∧ LinguisticEtymologicalGraphImplemented(d)
 ∧ MultilingualRelationsImplemented(d)
 ∧ GlyphStateExplicit(d)
 ∧ MapParserDisplayIntegrationComplete(d)
 ∧ ProvenanceAndGovernanceExplicit(d)
```

For the most central protocol conceptions, the canonical rider lexeme MUST preferentially come from a lost, dormant, sleeping, extinct, endangered, severely displaced, or historically suppressed language under the source, authority, and semantic-limit rules of the rider standard.

For less-central and derivative conceptions, the canonical rider term MAY be a governed compound or derivation composed from the existing multilingual rider lexicon, operators, and glyph relations.

The invariant rider lexeme remains the same across English, Ojibwe, French, Arabic, and every other host language. Host-language words remain glosses and search aliases.

## 5. Root and recursive Claim composition

The `exact_definition_claim` is the root of the Definition Claim field, not a substitute for it.

```text
DefinitionRoot(c)
= compressed current synthesis

DefinitionField(c)
= every material Claim required to reconstruct, distinguish,
  apply, source, translate, symbolize, contest, validate, and revise c
```

Every nested occurrence MUST preserve:

- stable occurrence ID;
- child Claim ID and exact version;
- parent occurrence;
- typed compositional role;
- nesting path;
- incorporation scope and state;
- necessity or contribution status;
- provenance;
- qualifications, exceptions, and activation conditions;
- propagation and review policy.

```text
ClaimIdentity(c)
≠ NestedOccurrence(c, parent, role, path, scope)
```

A relation is not automatically composition.

```text
RelatedTo(a,b)
≠ ConstitutiveOf(b,a)
```

## 6. Mandatory linguistic-etymological graph

Every Definition Claim MUST represent, as nested Claims or explicit unresolved Claims:

- each material lexical form;
- language, dialect, script, orthography, pronunciation, and grammatical category;
- morphology, derivation, inflection, and compositional analysis;
- attested predecessor forms and source languages;
- borrowing, calquing, compounding, metaphorization, clipping, acronym formation, reclamation, reconstruction, or protocol coinage;
- sourced etymology and disputed or folk etymology as separate epistemic states;
- semantic broadening, narrowing, drift, inversion, pejoration, amelioration, reclamation, and domain specialization;
- historical, legal, institutional, technical, cultural, community, and user-authored senses;
- active meanings, inactive legacy meanings, invocation conditions, and prohibited automatic inferences;
- representative sourced usages, examples, counterexamples, collocations, and pragmatic behavior;
- protocol nomenclature and naming governance;
- explicit distinction among inherited, revived, reconstructed, protocol-coined, and multilingual-composite forms.

## 7. Mandatory multilingual graph

Every Definition Claim MUST declare its multilingual state, including unresolved expansion where applicable.

Each source lexeme, anchor, or component Claim MUST preserve:

- exact lexical form and script;
- language, dialect, community, region, and historical period;
- pronunciation and morphology where available;
- local source definition and context;
- contributor and community provenance;
- source manifestation and citation location;
- relation to the canonical conception and canonical rider lexeme;
- equivalence type, scope, and limitations;
- non-equivalent semantic dimensions;
- cultural, ceremonial, institutional, or restricted-use conditions;
- governance and permission state;
- uncertainty, conflict, and unresolved Claims.

Translation relations MUST distinguish exact-within-scope, partial, analogous, broader, narrower, conflicting, borrowed, calqued, protocol-anchor, and no-established-equivalent states.

A multilingual composite MUST preserve every component's Claim identity, source, semantic contribution, ordering, morphology, and construction event. It MUST NOT be represented as an inherited word of any contributing language.

## 8. Mandatory glyph and emoji-rider graph

Every Definition Claim MUST declare its glyph state.

If no glyph is active, the card MUST contain an explicit `glyph_unassigned`, `glyph_resolution_pending`, or equivalent Claim.

Every candidate or active glyph MUST represent:

- stable glyph-manifestation Claim ID;
- literal glyph or sequence;
- Unicode characters, code points, Unicode names, and version where applicable;
- custom-glyph or platform-rendering status;
- textual fallback and accessibility description;
- visual elements, sequence order, and component semantics;
- synthesized protocol meaning;
- relation to root and nested Claims;
- identification, operator, state, warning, role, process, or compound function;
- common public, platform, historical, institutional, and community meanings;
- inactive legacy connotations and conditions of invocation;
- collision, ambiguity, accessibility, and misinterpretation risks;
- proposer, contributor, design provenance, governance, ratification, deprecation, and supersession state.

A glyph is a semantic manifestation and navigational compression. It is not the canonical conception and cannot replace the Definition Claim field.

## 9. Conditional material branches

The following branches are mandatory when materially generated by the conception and scope. Their absence must be justified in the completeness Claim.

### 9.1 Formal

- logical and mathematical expressions;
- graph signatures;
- ontology mappings;
- JSON Schema, RDF/OWL, SHACL, and runtime projections;
- invariants, arity, cardinality, precedence, and validation.

### 9.2 Operational

- recognition and application procedures;
- inputs, outputs, triggers, transitions, responsible loci;
- permissions, prohibitions, failures, recovery, and verification.

### 9.3 Evidentiary

- supporting and contrary evidence;
- source quality, uncertainty, observation conditions;
- prediction, resolution, custody, and transformation.

### 9.4 Historical-comparative

- originating formulations and traditions;
- prior and superseded definitions;
- competing, supporting, extending, conflicting, analogous, and paradoxical Claims;
- institutional and cultural histories;
- known semantic and conceptual drift.

### 9.5 Consequence and power

- legal and governance effects;
- institutional enforcement;
- economic, social, ecological, and cultural consequences;
- authority asymmetries, coercive imposition, affected loci, repair, and revision.

### 9.6 Activation and manifestation

- condition fields that activate the conception;
- perceptual, linguistic, computational, institutional, and behavioral manifestations;
- disposition and probability effects;
- dormant, active, competing, and inhibited configurations;
- dialogic execution.

### 9.7 Semantic dimension

- distinctions made available;
- salience and valuation effects;
- interpretive continuations;
- neighboring, overlapping, competing, and conflicting dimensions;
- predictable conflations;
- effects of inactivation and revision.

## 10. Canonical machine template

```yaml
claim_id: C:<stable-root-id>
version: <non-erasing-version>
canonical_conception: <language-independent conception reference>
canonical_rider_lexeme:
  lexical_claim_id: L:<stable-id>
  form: <invariant rider form>
  script: <ISO 15924>
  class: <attested|revived|reconstructed|protocol_coinage|multilingual_composite>
  source_languages: []
  ratification_state: <state>
host_language_glosses:
  - form: <gloss>
    language: <BCP-47>
    script: <ISO 15924>
preferred_label: <display policy>
exact_definition_claim: <root synthesis>
nested_claim_graph: {}
linguistic_etymological_graph: {}
multilingual_graph: {}
glyph_emoji_rider_graph: {}
declared_scope: {}
relational_configuration: {}
inclusions: []
exclusions: []
boundary_conditions: []
principal_relations: []
provenance: {}
epistemic_status: <state>
governance_state: {}
completeness_claim: {}
material_branches:
  formal: {}
  operational: {}
  evidentiary: {}
  historical_comparative: {}
  consequence_power: {}
  activation_manifestation: {}
  semantic_dimension: {}
```

## 11. Definition lifecycle

| State | Meaning |
|---|---|
| `identified` | A materially significant conception has a stable Claim ID. |
| `root_captured` | The originating and current root manifestations are preserved. |
| `nested_structure_drafted` | The recursive conceptual Claim structure is explicit. |
| `lexeme_candidates_identified` | Source-bound rider candidates or possible composites are recorded. |
| `lexeme_selected` | A rider selection or construction Claim exists. |
| `lexeme_source_bound` | Form, morphology, etymology, local meaning, provenance, and restrictions are verified. |
| `multilingual_implemented` | Rider, source lexemes, glosses, relations, maps, parser, model access, and display are implemented. |
| `glyph_state_implemented` | Active, candidate, or unassigned glyph state is fully represented. |
| `formally_incorporated` | All kernel, nesting, lexical, multilingual, glyph, provenance, governance, access, and validation requirements are satisfied. |
| `expanded_multilingual` | Additional anchors or components are incorporated non-erasingly. |
| `superseded_non_erasing` | A later version is operative while this version remains recoverable. |

## 12. Completeness and validation

A Definition Claim is complete at condition field `Γt` only when:

```text
DefinitionComplete(c, Γt)
:= KernelComplete(c)
 ∧ NestedClaimClosureExplicit(c, Γt)
 ∧ RootReconstructibleFromNesting(c)
 ∧ RiderLexemeImplemented(c)
 ∧ LinguisticAndEtymologicalClosureExplicit(c)
 ∧ MultilingualStateExplicit(c)
 ∧ GlyphStateExplicit(c)
 ∧ ScopeExplicit(c)
 ∧ BoundariesTestable(c)
 ∧ ExternalRelationsTyped(c)
 ∧ ProvenancePreserved(c)
 ∧ NoMaterialBranchOmitted(c, Γt)
 ∧ UnresolvedClaimsVisible(c)
```

Validation MUST reject:

- a root synthesis that cannot be reconstructed from nested Claims;
- formal-incorporation status without an invariant canonical rider lexeme;
- different canonical rider terms for the same conception across host languages;
- a core conception that ignores the lost-language source priority without a declared governance exception;
- an English or other host-language label treated as canonical nomenclature after rider ratification;
- a multilingual composite presented as a naturally inherited word;
- unsourced lexical form, morphology, etymology, local meaning, or usage Claims;
- multilingual anchors represented only through host-language glosses;
- translation equivalence without scope and non-equivalence Claims;
- glyph structure lacking identity, provenance, component semantics, accessibility, or governance state;
- public and legacy glyph meanings silently erased;
- materially constitutive Claims represented only as untyped external links;
- shared Claims duplicated rather than reused through scoped occurrences;
- hidden exceptions, conflicts, unresolved dependencies, scope changes, or propagation effects;
- definition changes that erase prior versions or acquired consequences.

## 13. Initial build order

The first build wave MUST establish:

1. Claim identity and occurrence;
2. Definition Claim nesting and composition;
3. conception and definition;
4. lexical Claim and lexical manifestation;
5. etymology event and semantic-change event;
6. source-language status and community authority;
7. canonical rider lexeme and host-language gloss;
8. multilingual relation and non-equivalence;
9. attested, revived, reconstructed, protocol-coinage, and multilingual-composite states;
10. glyph and emoji-rider manifestation;
11. transliteration, pronunciation, and accessibility;
12. selection, ratification, withdrawal, replacement, and supersession;
13. compositional rider grammar;
14. model-access, parser, map, display, search, and validation implementation.

Only after these foundations exist should the central conception lexicon be classified as formally incorporated.

## 14. Constitutional formulation

> Caeluviim defines each conception through one recursively nested, source-bound, multilingual Definition Claim field. The same invariant rider lexeme names a conception across every host language, while host-language words remain glosses and access paths. The most central rider lexemes are preferentially sourced from lost, dormant, endangered, displaced, and historically suppressed languages; less-central terms may be governed compounds or derivations from the accumulated multilingual rider field. Etymology, semantic history, multilingual relations, glyph structure, provenance, authority, and unresolved limits are constitutive Claim branches. No card is formally incorporated until these structures are chosen, implemented, mapped, transmitted, displayed, and validated.

# Definition Claim Linguistic, Etymological, Multilingual, and Glyph Structure

**Status:** Binding architectural correction v0.1.0  
**Extends:**
- `docs/architecture/standardized-definition-claim-structure.md`
- `docs/architecture/definition-claim-nesting-and-composition.md`
- `docs/architecture/universal-claim-card-node-standard.md`

## 1. Governing correction

A Definition Claim-card is not complete when it contains only a root synthesis, abstract nested Claims, and external relations.

Every registered Definition Claim MUST also represent the full materially available linguistic, etymological, multilingual, and glyph/emoji-rider structure through which the conception has been manifested, transmitted, altered, contested, and made available for protocol use.

These structures are not decorative metadata and are not detached supplements. They are Claims and Claim relations inside the complete Definition Claim field.

```text
CompleteDefinitionField(d)
:= RootDefinitionClaim(d)
 + NestedConceptualClaimGraph(d)
 + LexicalAndEtymologicalClaimGraph(d)
 + MultilingualClaimGraph(d)
 + GlyphAndEmojiRiderClaimGraph(d)
 + HistoricalSourceClaimGraph(d)
 + FormalOperationalEvidentiaryGraph(d)
 + ConflictProvenanceAndRevision(d)
```

## 2. Conception, lexeme, and glyph are distinct

The architecture MUST distinguish:

```text
canonical conception
≠ lexical manifestation
≠ translation or language anchor
≠ glyph or emoji-rider manifestation
```

- The **canonical conception** is the language-independent Claim identity presently being defined.
- A **lexical manifestation** is a word, phrase, morpheme, sign, or nomenclatural form through which the conception is manifested in a declared language, script, community, period, and usage field.
- A **translation or language anchor** is a sourced relation between lexical manifestations or conceptions; it may be exact, partial, analogous, context-bound, contested, or non-equivalent.
- A **glyph or emoji-rider manifestation** is a visual-symbolic Claim construction assigned to identify, compress, combine, or operationalize part of the conception.

A conception does not possess one universal word-history. Each lexical manifestation has its own etymology, morphology, usage history, semantic changes, and provenance. The Definition Claim-card integrates those histories without collapsing them into the conception itself.

## 3. Mandatory linguistic and etymological nesting

Every Definition Claim-card MUST contain a `linguistic_etymological_graph` branch. Where information is unknown, disputed, absent, or not yet sourced, the branch remains present through explicit unresolved Claims.

The branch MUST represent, where materially available:

### 3.1 Lexical identities

- stable lexical-form Claim ID;
- written form;
- spoken or signed form where available;
- language and dialect;
- script and orthography;
- pronunciation or phonological representation;
- grammatical category;
- morphological composition;
- inflectional and derivational forms;
- register, community, domain, and jurisdiction;
- current preferred, deprecated, contested, or prohibited status.

### 3.2 Etymology

- earliest materially relevant attested forms;
- source language and predecessor forms;
- borrowing, calque, derivation, compounding, clipping, acronym, metaphorization, or other formation process;
- morpheme-level contribution Claims;
- date or period Claims;
- source manifestations and citation locations;
- disputed or folk-etymology Claims preserved separately;
- uncertainty and evidentiary limitations.

### 3.3 Semantic history

- prior senses;
- present senses;
- specialized technical, legal, institutional, scientific, religious, cultural, or community senses;
- broadening, narrowing, metaphorical extension, pejoration, amelioration, reclamation, inversion, or semantic displacement;
- source-specific and speaker-specific meanings;
- active user-authored definitions;
- inactive legacy meanings;
- conditions under which a prior meaning becomes active again;
- known conflations and imposed meanings;
- historical consequences of semantic use.

### 3.4 Usage and manifestation

- representative sourced occurrences;
- grammatical and pragmatic behavior;
- collocations and construction patterns;
- discourse and institutional contexts;
- examples and counterexamples;
- literal, figurative, technical, performative, indexical, and metalinguistic uses;
- observed changes across time, communities, and media.

No asserted etymology, usage history, or semantic development may enter the canonical card without provenance and epistemic status.

## 4. Mandatory multilingual structure

Every Definition Claim-card MUST contain a `multilingual_graph` branch, even when only unresolved language-expansion Claims presently exist.

For each language manifestation or anchor, the card MUST preserve:

- stable lexical Claim identity;
- exact form and script;
- language, dialect, community, and region;
- pronunciation where available;
- morphology and literal compositional analysis;
- local definition and source context;
- contributor and community provenance;
- source manifestation and citation location;
- relation to the canonical conception;
- translation relation type;
- scope and conditions of equivalence;
- non-equivalent dimensions;
- cultural, institutional, ceremonial, or restricted-use conditions;
- governance and permission state;
- confidence, dispute, and unresolved Claims.

Translation relations MUST distinguish at least:

- `TRANSLATES_EXACTLY_WITHIN_SCOPE`;
- `PARTIALLY_EQUIVALENT_TO`;
- `ANALOGOUS_TO`;
- `EXTENDS_BEYOND`;
- `NARROWS`;
- `CONFLICTS_WITH`;
- `HAS_NO_ESTABLISHED_EQUIVALENT`;
- `BORROWED_AS`;
- `CALQUED_AS`;
- `PROTOCOL_ANCHOR_FOR`;
- `NON_EQUIVALENT_BUT_RELATIONALLY_USEFUL`.

A multilingual anchor MUST NOT be treated as interchangeable merely because an English gloss is available.

## 5. Mandatory glyph and emoji-rider structure

Every Definition Claim-card MUST contain a `glyph_emoji_rider_graph` branch.

If no canonical glyph has been assigned, the branch MUST contain an explicit `glyph_unassigned` or `glyph_resolution_pending` Claim. Absence may not be represented by silent omission.

For every candidate, active, contested, deprecated, or superseded glyph, emoji, emoji sequence, icon, or composite rider, the card MUST represent:

### 5.1 Glyph identity

- stable glyph-manifestation Claim ID;
- literal glyph or sequence;
- Unicode characters and code points where applicable;
- Unicode names and version where applicable;
- text, emoji, monochrome, color, or custom-rendering status;
- canonical textual fallback;
- accessibility description;
- rendering and platform-variation Claims.

### 5.2 Visual and compositional semantics

- visual elements;
- sequence order;
- spatial or compositional relations;
- contribution of each component;
- synthesized protocol meaning;
- relation to the root conception;
- relation to nested Claims or operators;
- intended salience, valence, action, or navigation function;
- whether the glyph identifies a conception, primitive, operator, state, warning, process, role, or compound Claim.

### 5.3 Existing and legacy meanings

- common public meanings;
- platform-specific meanings;
- historical and community meanings;
- institutional or commercial uses;
- inactive legacy connotations;
- collision, ambiguity, or misinterpretation risks;
- conditions under which a legacy meaning is materially invoked;
- prohibited automatic inferences.

### 5.4 Governance

- proposer and contributing loci;
- source and design provenance;
- candidate, active, contested, ratified, deprecated, or superseded state;
- scope of authorization;
- multilingual compatibility;
- cultural-appropriation, restricted-symbol, or community-authority Claims where material;
- collision review;
- accessibility review;
- revision and replacement rules.

The glyph is a semantic manifestation and navigational compression of Claim structure. It is never the canonical conception itself and cannot silently replace the full Definition Claim-card.

## 6. Constitutive nesting requirement

Linguistic, etymological, multilingual, and glyph Claims MUST be nested within the Definition Claim field according to their actual roles.

Illustrative structure:

```text
C:<conception>
├── /conceptual-synthesis
├── /linguistic
│   ├── /lexemes/<language>/<form>
│   │   ├── /morphology
│   │   ├── /etymology
│   │   ├── /semantic-history
│   │   ├── /usage
│   │   └── /sources
│   └── /nomenclature
├── /multilingual
│   ├── /anchors/<language>/<form>
│   ├── /translation-relations
│   ├── /non-equivalences
│   └── /community-provenance
├── /glyph-emoji-rider
│   ├── /candidate-glyphs
│   ├── /active-glyph
│   ├── /component-semantics
│   ├── /legacy-and-collisions
│   ├── /accessibility
│   └── /governance
├── /formal
├── /operational
├── /evidentiary
├── /historical-comparative
├── /consequence-power
├── /conflicts
└── /unresolved
```

The path labels are illustrative. Every actual branch must use stable Claim and occurrence identities.

## 7. Card completeness

A Definition Claim-card cannot claim `maximally_represented_at_condition` unless:

```text
LinguisticClosureExplicit(d)
∧ EtymologicalClaimsSourceBound(d)
∧ SemanticHistoryPreserved(d)
∧ MultilingualStateExplicit(d)
∧ GlyphStateExplicit(d)
∧ LegacyAndCollisionClaimsVisible(d)
∧ AccessibilityFallbackPresent(d)
∧ GovernanceStateExplicit(d)
```

This does not require invented etymologies, translations, or glyphs. It requires explicit representation of what is known, sourced, contested, absent, deferred, or unresolved.

## 8. Validation failures

Validation MUST reject:

- a definition presented as complete while its etymological or lexical history is silently omitted;
- a lexical etymology attributed directly to the language-independent conception without identifying the lexeme;
- unsourced etymology or folk etymology presented as established;
- an English word treated as the canonical conception identity;
- multilingual anchors represented only by English glosses;
- translation equivalence asserted without scope and non-equivalence Claims;
- glyph or emoji fields lacking Claim identity, provenance, component semantics, or governance state;
- public or legacy glyph meanings silently erased;
- a glyph treated as the complete conception;
- an inaccessible glyph without textual fallback and accessibility description;
- silent absence of a glyph or multilingual state;
- flattening these branches into unaddressable prose or ornamental metadata.

## 9. Model-access requirement

When a task concerns naming, meaning, interpretation, historical usage, translation, cultural relation, glyph navigation, protocol nomenclature, or semantic conflict, the model-access packet MUST load the relevant branches of:

- lexical identity;
- etymology;
- morphology;
- semantic history;
- multilingual anchors and non-equivalence;
- glyph/emoji-rider meaning and governance;
- legacy meanings and collision constraints;
- source and provenance Claims.

A root definition sentence or conceptual nesting closure alone is insufficient for those tasks.

## 10. Mandatory implementation derivatives

The architecture requires:

- lexical-form and glyph-manifestation Claim schemas;
- etymology-event and semantic-change event schemas;
- multilingual-anchor and translation-relation schemas;
- Unicode and custom-glyph representation;
- textual fallback and accessibility fields;
- glyph composition and component-semantic relations;
- legacy-meaning, collision, ambiguity, and invocation-condition Claims;
- language, script, dialect, community, and source provenance validation;
- exact, partial, analogous, conflicting, and non-equivalent translation relations;
- glyph candidate, ratification, deprecation, and supersession processes;
- source-bound etymology and usage-history ingestion;
- model-access branch retrieval for linguistic and glyph tasks;
- migration of every existing Definition Claim into explicit linguistic, multilingual, and glyph states.

## 11. Constitutional formulation

> A complete Definition Claim is one synthesized, recursively nested Claim field containing not only its conceptual construction but also the lexical manifestations, etymologies, morphology, semantic histories, multilingual anchors, translation limits, glyph and emoji-rider manifestations, legacy meanings, accessibility, sources, governance, conflicts, and unresolved Claims through which the conception is made available. These are constitutive Claim branches, not decorative metadata or optional appendices. Unknown or unassigned structure remains explicit as unresolved state rather than disappearing through omission.

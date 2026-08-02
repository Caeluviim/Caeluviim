# Rider Lexical Density and Proto-Semantic Field

**Status:** Binding architectural extension v0.1.0  
**Extends:**
- `docs/architecture/host-language-lexical-decentering-and-multilingual-incorporation.md`
- `docs/architecture/standardized-definition-claim-structure.md`
- `docs/architecture/definition-claim-nesting-and-composition.md`

## 1. Governing correction

The rider MUST NOT select canonical terms merely because they are ancient, minimally attested, associated with an early society, or glossed by a basic concept.

The rider optimizes for **relational semantic density**: the quantity, centrality, generativity, and recoverability of material Claim structure compressed into a usable lexical manifestation.

```text
CanonicalRiderSelection(c)
≠ oldest available word for c
≠ shortest available word for c
≠ most exotic available word for c
≠ dictionary synonym for c

CanonicalRiderSelection(c)
= source-valid lexeme or governed construction
  with maximal useful relational density
  under provenance, authority, accessibility,
  distinguishability, and implementation constraints
```

Lost-language priority determines where core candidates should preferentially be sought. Density analysis determines whether a candidate is sufficiently expressive and structurally useful for the conception.

## 2. Relational semantic density

```text
RelationalSemanticDensity(l,c,Γt)
:= materially recoverable Claim structure contributed by lexical form l
   to conception c under condition field Γt
   relative to the cognitive, phonological, visual, and operational cost
   of learning, distinguishing, transmitting, and applying l
```

Density is not mere polysemy. A word with many unrelated senses may be ambiguous rather than dense.

A high-density rider lexeme compresses a coherent relational neighborhood whose distinctions can be expanded from the Definition Claim-card.

## 3. Density dimensions

Every core rider candidate MUST be assessed across at least these dimensions:

### 3.1 Constitutive coverage

How many necessary branches of the conception does the candidate materially express or organize?

### 3.2 Relational centrality

How strongly does the candidate connect to other core conceptions and operations?

### 3.3 Generativity

Can the candidate support governed compounds, derivations, operators, states, and process terms without semantic collapse?

### 3.4 Coherence

Are the compressed senses mutually intelligible as one relational structure, or merely accidental homonyms and unrelated polysemy?

### 3.5 Distinctiveness

Can the form be reliably distinguished in speech, text, sign, search, parsing, and interface use?

### 3.6 Recoverability

Can the compressed structure be expanded through mapped Claim relations, sources, morphology, and etymology?

### 3.7 Cross-domain transfer

Does the term retain useful structure across interpersonal, legal, scientific, governance, technical, ecological, and other material scopes?

### 3.8 Stability under host languages

Can the invariant rider form remain recognizable while riding over different grammars, scripts, phonologies, and interfaces?

### 3.9 Accessibility and learnability

Can persons learn, pronounce or otherwise manifest, remember, search, and distinguish the term with reasonable support?

### 3.10 Provenance and authority integrity

Can the term be used without erasing source meaning, community authority, use restrictions, uncertainty, or contribution history?

### 3.11 Collision cost

How much confusion arises from existing public meanings, homophony, script collision, platform rendering, institutional usage, or conflicting protocol terms?

### 3.12 Compression benefit

How much repeated explanatory structure does use of the term eliminate while preserving access to the full Definition Claim graph?

## 4. Density is scope-bound

A term is not universally dense in the abstract.

```text
Density(l,c,Γ₁) may differ from Density(l,c,Γ₂)
```

A candidate can be highly useful for interpersonal care yet too narrow for a general protocol conception of care. Another may be broad enough but insufficiently discriminating.

Every density Claim MUST identify scope, evidence, source structure, and comparison set.

## 5. Selection is multi-objective

Canonical rider selection MUST NOT reduce to one scalar score without preserving component Claims.

An implementation MAY compute an advisory vector:

```text
V(l,c) = ⟨
  constitutive_coverage,
  relational_centrality,
  generativity,
  coherence,
  distinctiveness,
  recoverability,
  cross_domain_transfer,
  host_stability,
  accessibility,
  provenance_integrity,
  collision_cost,
  compression_benefit
⟩
```

A weighted selection function MAY support comparison:

```text
AdvisoryDensityScore(l,c)
:= Σ wi·Vi − penalties
```

but the vector, weights, objections, authority conditions, and unresolved conflicts MUST remain visible. A high score cannot override cultural restriction, unreliable attestation, or lack of authority.

## 6. Proto-semantic field rather than singular first word

Caeluviim MUST NOT assume that language began through one isolated first word.

The more coherent architectural model is a gradually differentiating **proto-semantic field** of recurrent shared distinctions, orientations, and interactional operations.

Illustrative early field dimensions include:

- attention and salience;
- presence and absence;
- self, other, and group;
- approach and avoidance;
- danger and safety;
- favorable and unfavorable;
- obtain, retain, give, and lose;
- agent, object, action, and result;
- here, there, now, later, and recurrence;
- invitation, warning, refusal, demand, recognition, and coordination;
- food, water, shelter, offspring, predator, tool, path, and place;
- shared affect, joint attention, imitation, and displaced reference.

These are not asserted as a historically recovered first vocabulary. They are a model of mutually dependent communicative functions from which word-like distinctions could differentiate.

```text
recurrent shared conditions
→ repeated multimodal manifestations
→ differentiated signal–condition relations
→ mutually constraining proto-lexical field
→ increasingly stable lexical Claims
→ compositional language
```

## 7. Concurrent materialization

The emergence model permits several lexical distinctions to stabilize concurrently because each helps define the others.

```text
attention
↔ danger
↔ approach/avoidance
↔ good/bad orientation
↔ agent/object/action
↔ here/there
```

For example, a danger signal depends on attention, an affected locus, an adverse orientation, a source or location, and a possible response. The semantic identity of one emerging signal is constrained by the field around it.

Therefore:

```text
first lexical field
is architecturally more plausible than
single self-sufficient first word
```

This is a conceptual model, not a claim that the exact prehistoric field can now be recovered.

## 8. Implication for rider architecture

The rider should not imitate a hypothetical primitive cave vocabulary.

Its task is inverse and synthetic:

```text
complete contemporary Claim field
→ identify highest-centrality conceptions
→ recover lost-language lexical structures
→ compare their relational density
→ select or construct invariant rider lexemes
→ preserve full expansion through Definition Claim cards
```

The core rider vocabulary should therefore be small enough to learn but dense enough to organize the wider protocol.

## 9. Core versus derivative density

### 9.1 Core rider terms

Core terms SHOULD maximize:

- relational centrality;
- cross-domain transfer;
- generativity;
- coherent compression;
- source-language contribution;
- distinction from neighboring core terms.

### 9.2 Derivative terms

Derivative terms SHOULD maximize reconstructibility from the established core lexicon.

```text
DerivativeTerm
= core rider lexemes
+ governed operators or affixes
+ explicit composition relations
```

A derivative term does not need a separate ancient source word when a transparent high-density composition better preserves meaning.

## 10. Candidate comparison record

Every rider-candidate comparison MUST preserve:

- candidate lexical Claim identity;
- source state and attestation;
- Definition Claim branches covered;
- branches omitted or contradicted;
- semantic-density vector;
- morphology and derivational potential;
- competing candidates;
- host-language and cross-script behavior;
- collision and accessibility Claims;
- source-community authority and restrictions;
- selection, objection, and ratification history.

## 11. Validation failures

Validation MUST reject:

- selection justified only by antiquity;
- a basic or purportedly primordial gloss treated as inherently high-density;
- unrelated polysemy counted as coherent semantic density;
- a dense-looking term whose structure cannot be recovered from sources and Claim relations;
- a term selected for central use despite weak distinctiveness or severe collision;
- a scalar score that erases component tradeoffs or authority restrictions;
- fabricated Claims about the historically first human word;
- presentation of the illustrative proto-semantic field as recovered prehistoric fact;
- derivative coinages that cannot be reconstructed from component Claims;
- density optimization used to override provenance, authority, non-equivalence, or accessibility.

## 12. Mandatory implementation derivatives

The architecture requires:

- semantic-density vector schema;
- candidate-comparison records;
- relation-centrality and generativity measures;
- coherent-polysemy versus accidental-ambiguity Claims;
- collision, learnability, pronunciation, rendering, and search tests;
- core-conception centrality map;
- source-authority veto and restriction handling;
- multi-objective selection interface;
- transparent derivative-term grammar;
- model-access packets carrying density rationale and unresolved tradeoffs;
- non-erasing selection and replacement events.

## 13. Constitutional formulation

> Caeluviim selects rider lexemes for relational semantic density rather than antiquity, novelty, or superficial brevity. A high-density word coherently compresses a central, generative, source-recoverable Claim structure while remaining distinguishable, learnable, governable, and usable across host languages. Language origin is not modeled as one recoverable first word but as a concurrently differentiating proto-semantic field of attention, orientation, agents, actions, values, dangers, locations, and coordination. The rider does not reproduce that primitive field; it uses the complete contemporary Claim graph to construct a compact, high-density, translingual lexicon whose meanings remain fully expandable.

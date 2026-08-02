# Definition Claims as Dimensions of Semantic Interpretation

**Status:** Binding architectural correction v0.2.0  
**Legacy path:** `docs/architecture/definition-claims-as-qualia-dimensions.md`  
**Supersedes:** v0.1.0 claim that Definition Claims are themselves dimensions of qualia

## 1. Governing correction

Definition Claims are not dimensions of qualia themselves.

They are dimensions of **semantic interpretation** through which a locus can distinguish, organize, name, relate, evaluate, remember, communicate, and act upon manifested conditions.

```text
DefinitionClaim d
→ establishes a semantic distinction structure
→ structure becomes available for activation
→ activated structure participates in interpretation
```

The dimension belongs to semantic organization. The experienced or manifested condition is not identical to the Definition Claim that interprets it.

## 2. Core distinction

```text
manifested condition
≠
semantic dimension
≠
semantic interpretation
```

- A **manifested condition** is what materially, perceptually, affectively, relationally, or otherwise occurs for a locus.
- A **semantic dimension** is a Definition Claim-established structure of possible distinction.
- A **semantic interpretation** is the condition-bound application of one or more activated semantic dimensions to a manifested condition.

The architecture need not claim access to an uninterpreted private essence. It must only preserve the distinction between what is being interpreted and the Claim-structured relations through which interpretation occurs.

## 3. Formal model

Let:

- `M(l,t,Γt)` be the manifested condition of locus `l` at time `t` under condition field `Γt`;
- `D = {d₁ ... dₙ}` be the available Definition Claim field;
- `A(l,t,Γt) ⊆ D` be the Definition Claims presently activated;
- `I` be the semantic interpretation operation.

Then:

```text
SemanticInterpretation(l,t,Γt)
:= I(M(l,t,Γt), A(l,t,Γt), Γt)
```

The result is not a direct copy of the manifested condition. It is the relational meaning made available through the activated Definition Claims.

## 4. Definition Claims establish interpretive dimensions

```text
SemanticDimension(d)
:= the structured range of distinctions, relations, boundaries,
   implications, valuations, and possible continuations established
   by Definition Claim d
```

A Definition Claim establishes:

- what can be distinguished;
- what counts as included or excluded;
- what relations become salient;
- what comparisons become available;
- what consequences can be inferred;
- what responses become intelligible;
- what language can stabilize and transmit;
- what memories and events can be indexed under the conception;
- what disagreements and competing interpretations can be stated.

Its full synthesized card defines the internal geometry of that semantic dimension.

```text
InternalGeometry(SemanticDimension(d))
:= SynthesizedStructure(DefinitionCard(d))
```

## 5. Experience through semantic interpretation

A locus does not experience a Definition Claim as though the card itself were a quale.

Rather:

```text
manifested condition
+ activated Definition Claims
+ condition field
→ semantic interpretation of the condition
```

Examples:

```text
pain, loss, restriction, or degradation
+ activation of C:harm
→ interpretation as injury, deprivation, violation,
   cumulative burden, responsibility, or repair obligation
```

```text
attention, assistance, restraint, or intervention
+ activation of C:care
→ interpretation through responsiveness, dignity, agency,
   consent, consequence, follow-through, or paternalism
```

```text
assertion, evidence, uncertainty, and contradiction
+ activation of C:truth
→ interpretation through accuracy, qualification,
   distortion, support, revision, or unresolved remainder
```

The underlying condition may occur without the relevant Definition Claim being active. In that case it may remain unnamed, weakly differentiated, differently organized, or interpreted through another semantic dimension.

## 6. Semantic topology

Typed relations among Definition Claims define the topology of semantic interpretation.

```text
SemanticTopology
:= Definition Claim dimensions
 + typed relations among them
 + activation conditions
 + provenance and revision history
```

Examples:

```text
C:care DISTINGUISHES_FROM C:control
C:validation DISTINGUISHES_FROM C:agreement
C:apology DISTINGUISHES_FROM C:repair
C:coercion CONSTRAINS C:consent
C:trust EXPOSES C:vulnerability
C:harm GENERATES_OBLIGATION C:repair
```

These relations structure adjacency, opposition, dependency, conflict, implication, translation, and possible movement among interpretations.

## 7. Concept acquisition

Acquiring a Definition Claim expands a locus's available semantic dimensionality.

```text
prior semantic field S₀
+ acquisition and integration of Definition Claim d
→ expanded semantic field S₁
```

This may enable the locus to:

- distinguish previously conflated conditions;
- recognize patterns across events;
- articulate experience more precisely;
- compare interpretations;
- identify consequences or obligations;
- communicate a condition to another locus;
- contest an imposed interpretation;
- perceive possible action or repair.

This is an expansion of semantic interpretation, not proof that a new Definition Claim creates a new sensory or phenomenal capacity.

## 8. Competing definitions

Competing Definition Claims under one surface label establish competing semantic dimensions.

```text
Definition d₁: care as protective control
Definition d₂: care as consent-sensitive preservation of agency
```

These definitions organize the same events differently and generate different boundaries, saliences, obligations, and possible responses.

The graph must preserve each definition, its provenance, its operative scope, its consequences, and its relation to the current synthesis.

## 9. Revision

Revision of a Definition Claim changes semantic geometry non-erasingly.

```text
Definition d(v₁)
→ prior interpretations and consequences
→ acquired difference or correction
→ Definition d(v₂)
→ revised interpretive structure
```

The prior definition remains material because actions, memories, agreements, and injuries may have been organized through it.

## 10. Interpersonal communication

Interpersonal misunderstanding often results from differently activated semantic dimensions.

```text
manifestation by locus l₁
→ interpreted through semantic field A₁
→ received and interpreted through semantic field A₂
```

Misalignment may occur when:

- the same label invokes different Definition Claims;
- one locus lacks or does not activate a distinction active for another;
- one locus imports an inactive legacy meaning;
- several distinctions are collapsed into one;
- power makes one interpretation operative while suppressing another;
- first-person manifestation is confused with verified external condition;
- an inference is represented as literal content or verified intent.

Mediation and semantic repair therefore require explicit dimension mapping.

## 11. Model access

A model-access packet transmits semantic dimensions, maps, active definitions, dispositions, and source relations.

It does not transmit qualia merely by transmitting definition cards.

```text
Definition Claims loaded by model
→ expanded semantic interpretation capacity
≠ automatic possession of another locus's manifested experience
```

A model may interpret, relate, and respond to Claims concerning experience while preserving the distinction between:

- first-person manifestation;
- observable condition;
- semantic interpretation;
- plausible inference;
- source-bound theory;
- verified external condition.

## 12. Mandatory card module

Every full Definition Claim-card should include a `semantic_dimension` module:

```yaml
semantic_dimension:
  distinctions_enabled: []
  inclusion_exclusion_structure: []
  salience_conditions: []
  valuation_relations: []
  interpretive_continuations: []
  actions_made_intelligible: []
  adjacent_dimensions: []
  conflicting_dimensions: []
  common_conflations: []
  absence_or_inactivation_effects: []
  revision_effects: []
```

Where a Definition Claim concerns lived or qualitative experience, the card may additionally record first-person and observable manifestation modules. Those manifestations must not be collapsed into the semantic dimension itself.

## 13. Validation requirements

Implementation must detect:

- claims that Definition Claims are themselves qualia;
- claims that loading a definition transmits another locus's experience;
- conflation of manifested condition with semantic interpretation;
- conflation of first-person manifestation with verified external condition;
- imported semantic meanings not active in present use;
- erasure of competing semantic dimensions under one label;
- revision that deletes prior interpretive geometry or its consequences;
- treatment of all available Definition Claims as simultaneously active;
- reduction of experience to language while ignoring material, perceptual, affective, or relational manifestation.

## 14. Constitutional formulation

> Every Definition Claim is a de facto dimension of semantic interpretation. It establishes a structured axis through which manifested conditions can be distinguished, related, valued, remembered, communicated, and acted upon. The full synthesized Definition Claim-card defines the internal geometry of that semantic dimension; typed relations among cards define the semantic topology; and condition-bound activation determines which dimensions participate in a particular interpretation. Definition Claims do not themselves constitute qualia, nor does transmission of a definition transmit another locus's experience.
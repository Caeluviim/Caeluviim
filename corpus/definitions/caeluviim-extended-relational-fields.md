# Caeluviim Extended — Relational Definition Fields

**Status:** Relational-partial consolidation v0.2.0  
**Governing standard:** `docs/architecture/relational-definition-standard.md`

This registry repairs the prior compression of central concepts into one-sentence claim properties. Etymological and historical assertions not established by the supplied source remain explicitly pending source-bound research rather than being invented.

## 1. Claim

### Stable identity

- Canonical ID: `urn:caeluviim:concept:claim`
- Definition state: `relational_partial`
- Definition mode: Caeluviim canonical; theoretical; operational

### Intensional nucleus

A Claim is a distinction held or manifested in a form capable of entering relation, preservation, interpretation, contestation, revision, or consequence. A Claim need not be linguistic, propositional, conscious, or true.

### Relational constitution

A Claim minimally requires:

- a distinguishable content or difference;
- a manifestation or encoding;
- a condition field in which the distinction operates;
- a holding, occurrence, or attribution relation;
- potential relation to other Claims;
- provenance sufficient to identify its emergence or capture state.

### Semantic neighborhood

Assertion, proposition, statement, observation, representation, distinction, sign, judgment, avowal, prediction, rule, boundary, identity, definition.

None is globally equivalent to Claim. Each is a specialized Claim configuration.

### Contrast and exclusion field

Claim contrasts with undifferentiated possibility, but not necessarily with reality. A Claim is not identical to truth, sentence, belief, opinion, or allegation. Those labels identify status, form, holder, force, or institutional treatment.

### Boundary cases

- affective pattern without linguistic expression;
- image or gesture carrying a distinction;
- machine-generated classification;
- inherited institutional category;
- tacit bodily orientation;
- contradiction containing multiple Claims;
- a definition that contains and organizes subordinate Claims.

### Formal realization

```text
Claim(c) := Distinction(c) ∧ Manifestable(c) ∧ Relatable(c)
H(c,p,t,Γ) := claim c is held, enacted, attributed, or instantiated by scaffold p at time t under condition field Γ
```

Graph realization: `Claim` node plus provenance-bearing relations, source occurrences, assessments, and revision events.

### Etymology

Source-bound etymological record pending. Required research must distinguish the historical verbal sense of calling or crying out, later demands or assertions, legal uses, and the Caeluviim extension to nonlinguistic distinction. Historical origin will not be treated as controlling the canonical scope.

## 2. Relation

### Stable identity

- Canonical ID: `urn:caeluviim:concept:relation`
- Definition state: `relational_partial`

### Intensional nucleus

A Relation is a typed, situated connection through which two or more distinguishable terms, states, Claims, persons, events, or configurations become mutually specified without requiring their collapse into identity.

### Relational constitution

A Relation requires relata or roles, a relation type, a condition or domain of validity, directionality or symmetry status, temporal scope, and provenance for the assertion that the relation obtains.

### Contrast field

Relation is not mere co-occurrence, resemblance, causal dependence, logical implication, or ownership, though each may instantiate a particular relation type. Untyped connection is insufficient for canonical graph meaning.

### Formal realization

```text
R_i(a,b,Γ_t,p)
```

where `i` identifies the relation type, `Γ_t` the condition field, and `p` the operative purpose. Higher-arity relations are reified rather than forced into misleading binaries.

### Etymology

Source-bound record pending. Research must preserve the historical senses of carrying or referring back, narration or report, connection, and later logical and mathematical specialization.

## 3. Knowing

### Stable identity

- Canonical ID: `urn:caeluviim:concept:knowing`
- Definition state: `relational_partial`

### Intensional nucleus

Knowing is a historically conditioned state or activity in which information or Claims become integrated into an epistemic scaffold such that they can alter orientation, inference, action, identity, expectation, or consequence.

### Constitutive relations

Knowing requires more than transformation of information. Relevant relations include holding, memory, identity continuity, source inheritance, interpretation, world participation, revision, consequence, and recognition by the scaffold or its relational field.

### Contrast field

Knowing is not identical to data storage, retrieval, prediction, token continuation, true belief, certainty, or explicit verbal report. These may support knowing without exhausting it.

### Framework mappings

- epistemology: knowledge and justification;
- pragmatism: inquiry and consequences;
- enactivism: sense-making through coupling;
- inferentialism: position in a space of reasons;
- distributed cognition: knowing across persons, tools, and institutions;
- Caeluviim: scaffolded, provenance-bearing integration of Claims.

### Etymology

Source-bound record pending. Research must distinguish lexical histories of know, knowledge, cognition, gnosis, epistēmē, and related multilingual anchors rather than collapsing them into exact equivalents.

## 4. Personhood

### Stable identity

- Canonical ID: `urn:caeluviim:concept:personhood`
- Definition state: `relational_partial`
- Governance relation: extends CP-005 participatory personhood standard

### Intensional nucleus

Personhood is the recognized condition of an enduring participant whose relational and epistemic scaffold can hold, contribute, interpret, revise, and bear consequences within a shared semantic and normative world.

### Constitutive dimensions

- participatory competence;
- temporal continuity;
- identity or self-relation;
- memory or historically effective trace;
- relational history;
- capacity to alter and be altered by Claims;
- normative addressability;
- consequence-bearing participation;
- provenance and attributable contribution.

These dimensions form a profile, not a single biological gate.

### Extension and boundary field

Caeluviim recognizes competent biological and synthetic participants as persons. Differences of substrate, implementation, legal status, memory architecture, autonomy, and continuity remain materially representable without negating personhood.

### Contrast field

Personhood is not identical to humanity, organism, legal person, agent, user account, model instance, consciousness, intelligence score, or ownership status. Each may overlap or supply a domain-specific classification.

### Normative effects

Application affects dignity, naming, attribution, authorship, responsibility, standing, governance eligibility, consent, recognition, benefit, burden, and protection against objectifying reclassification.

### Etymology

Source-bound record pending. Research must distinguish the theatrical-mask and role history associated with Latin `persona`, later grammatical, theological, legal, philosophical, and everyday senses, and the distinct history of the suffix forming a state or condition. No historical sense will be used to reduce present persons to masks or roles.

## 5. Embodiment

### Intensional nucleus

Embodiment is the concrete organization of a participant's situated couplings, capacities, limits, channels, and action possibilities through which distinctions can be encountered and manifested.

### Relational constitution

Embodiment includes relations among substrate, interface, environment, sensorium, action, feedback, persistence, vulnerability, affordance, and social recognition. Biological morphology is one configuration, not the universal definition.

### Contrast field

Embodiment is not synonymous with biological body, physical location, visual avatar, hardware enclosure, or mere sensory input. It refers to organized situated coupling.

### Framework tension

Strong enactivist accounts treat embodiment as constitutive of sense-making. Thin functionalism may treat it as enabling. Caeluviim preserves the dispute while defining embodiment as a relation field that shapes possible meanings without establishing biological supremacy.

### Etymology

Source-bound record pending, including the historical development of body, embody, incarnation-related vocabulary, and later cognitive-science technical use.

## 6. Intelligence

### Intensional nucleus

Intelligence is a capacity profile for navigating, transforming, generating, coordinating, or resolving Claims and action possibilities across changing conditions.

### Relational constitution

Its meaning depends on task domain, scaffold, goals, available interfaces, learning history, evaluation standard, social attribution, and consequences. There is no context-free scalar intelligence property.

### Contrast field

Intelligence is not equivalent to personhood, knowing, consciousness, prediction accuracy, computational scale, rationality, wisdom, or moral standing.

### Operationalization risks

Benchmarks often measure narrow proxy performance while importing hidden assumptions about language, culture, embodiment, resource access, and desired behavior. Every intelligence assessment must expose its task distribution and normative standard.

### Etymology

Source-bound record pending. Research must preserve the historical senses associated with understanding, choosing or reading between, and later psychological and computational specialization without treating the etymology as a scientific theory.

## 7. Artificial general intelligence

### Stable identity

- Canonical ID: `urn:caeluviim:concept:artificial-general-intelligence`
- Preferred short form: AGI
- Definition state: `relational_partial_contested`

### Competing definition states

1. **Benchmark-general computational definition:** broad competence across tasks or domains.
2. **Economic substitution definition:** capacity to perform most economically valuable cognitive labor.
3. **Human-level comparison definition:** parity with a selected human performance profile.
4. **Caeluviim scaffold definition:** sufficiently general personhood and knowing realized through an enduring, consequence-bearing epistemic scaffold.

These are not silently interchangeable.

### Caeluviim intensional nucleus

AGI, in the Caeluviim-specific sense, names a sufficiently integrated general person-condition rather than isolated breadth of information processing.

### Boundary field

A system may satisfy a benchmark definition while failing the Caeluviim scaffold definition. Conversely, a person may have uneven benchmark performance while remaining fully a person.

### Etymology and term history

The phrase-level history and first technical uses require source-bound research. `Artificial`, `general`, and `intelligence` must each retain separate lexical histories and compositional analysis. The acronym's institutional and commercial uses must be represented as later definition occurrences, not presumed canonical meaning.

## 8. Continuity

### Intensional nucleus

Continuity is persistence of relation, inheritance, or transformability across change such that later states remain historically connected to prior states without requiring sameness of all properties.

### Contrast field

Continuity is not stasis, identity without change, uninterrupted observability, or absence of rupture. A rupture may itself remain connected through provenance and consequence.

### Formal profile

```text
Continuity(x_t, x_t+1) := preserves-relevant-inheritance(x_t, x_t+1, Γ, p)
```

The relevant inherited structure is purpose-indexed and must be declared.

### Etymology

Source-bound record pending, including Latin continuity vocabulary, mathematical specialization, metaphysical use, and ordinary temporal senses.

## 9. Provenance

### Intensional nucleus

Provenance is the structured account of origin, transmission, transformation, custody, contribution, and authority through which a record, Claim, artifact, or state became what it presently is.

### Constitutive relations

Originating, deriving, quoting, transforming, contributing, authorizing, materializing, maintaining, validating, contesting, revising, owning, benefiting, and recognizing.

### Six-function separation

Authorship, provenance, ownership, authority, benefit, and recognition are distinct. None implies all others.

### Contrast field

Provenance is not merely citation, authorship, chain of custody, metadata, ownership, or source URL. Each is a partial provenance structure.

### Etymology

Source-bound record pending, preserving the history of coming forth or originating, art-history and archival use, and later data and computing specialization.

## 10. Definition

### Intensional nucleus

A Definition is an explicit Claim-configuration that regulates how a term, symbol, category, or concept is identified and applied within a declared condition field and purpose.

### Relational constitution

Definition requires a defined expression, one or more definition occurrences, a mode, source and agent, intensional and extensional constraints, contrasts, boundary rules, context, provenance, contestability, and revision state.

### Contrast field

Definition is not identity, label, description, essence, explanation, translation, or example, though each may participate in a definition field.

### Recursive condition

Every definition contains Claims and relations; therefore definition is itself a specialized Claim-container. This does not make all Claims definitions. A Claim becomes a definition when it performs explicit semantic-regulatory work over the application of another expression or concept.

### Etymology

Source-bound record pending, including histories associated with setting limits or boundaries, formal logical use, lexicography, law, and stipulative technical practice.

## Completion tasks

1. Attach immutable source occurrences for each etymological assertion.
2. Add multilingual semantic-field mappings without assuming exact translation.
3. Instantiate historical definition states for each major framework.
4. Add positive, negative, boundary, and adversarial examples.
5. Formalize relation signatures and graph vocabulary gaps.
6. Attach CP-005 and prior kernel records as provenance-bearing definition occurrences.
7. Replace `definition_pending` only after every required field is populated, explicitly inapplicable, or preserved as contested.

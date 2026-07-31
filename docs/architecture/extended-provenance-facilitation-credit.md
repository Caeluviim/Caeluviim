# Extended Provenance and Facilitation Credit

**Doctrine ID:** CAELUVIIM-PROV-EXTENDED-FACILITATION-001  
**Version:** 0.1.0  
**Status:** Proposed provenance doctrine; architect-directed consolidation  
**Domain:** Provenance, attribution, credit, discovery, interpretation, incorporation, governance

## 1. Core proposition

Authorship is only one form of contribution.

A person or agent who did not originate a source may nevertheless be a materially necessary participant in the actual, traceable sequence by which that source was discovered, recognized, transmitted, interpreted, validated, and incorporated into Caeluviim.

Caeluviim therefore preserves both:

1. **source provenance** — who created, published, maintained, or originally expressed the source material; and
2. **incorporation provenance** — who or what materially facilitated the source’s path into the project.

The original author retains authorship credit. Facilitation credit does not transfer authorship, ownership, authority, endorsement, or control.

## 2. Normative determination

**Every materially significant inclusion must preserve the full traceable arc of actual participation, not merely the identity of the original author and final repository committer.**

A participant’s documented role in that historical chain must not be erased merely because another actor could hypothetically have performed the same function. The actual event history is non-substitutable: once the incorporation occurred through a particular sequence of actors and events, those contributions remain part of the provenance record.

“Immutable” in this doctrine means that verified historical participation must not be silently removed or reassigned. It does not mean that descriptions, interpretations, confidence levels, or legal conclusions are immune from correction.

## 3. Distinct contribution roles

Caeluviim must represent contribution roles separately rather than collapsing them into a generic `contributor` field.

| Role | Function |
|---|---|
| `Originator` | Created the source expression, work, claim, dataset, artifact, or event record. |
| `Publisher` | Made the source publicly or institutionally available. |
| `Materializer` | Instantiated the source in a physical or technical medium. |
| `Encounterer` | Directly encountered the source or event in the world. |
| `Discoverer` | Located material whose relevance was not already established within the project. |
| `Recognizer` | Identified potential material value or project relevance. |
| `Transmitter` | Carried, quoted, described, uploaded, or otherwise conveyed the material into the inquiry process. |
| `Retriever` | Recovered the authoritative or best-available source. |
| `Verifier` | Checked attribution, wording, context, integrity, or factual status. |
| `Interpreter` | Produced an explicitly labeled interpretation or relational reading. |
| `Synthesizer` | Connected the source with other claims, values, authorities, or structures. |
| `Facilitator` | Enabled a transition that materially advanced the source toward inclusion. |
| `Integrator` | Encoded or incorporated the material into the repository, ontology, graph, or protocol. |
| `Authorizer` | Directed or approved formal inclusion. |
| `Validator` | Assessed structural, factual, semantic, legal, or governance validity. |
| `Contester` | Formally challenged a claim, attribution, interpretation, or incorporation decision. |

One actor may hold multiple roles. Multiple actors may hold the same role. Each role must be connected to a specific event, object, and evidentiary basis.

## 4. Material-facilitation threshold

An actor receives facilitation credit only when all applicable conditions are satisfied:

1. **Actual participation:** the actor participated in the documented incorporation chain.
2. **Material contribution:** the action enabled, preserved, clarified, accelerated, redirected, validated, or authorized inclusion in a non-trivial way.
3. **Role specificity:** the contribution can be described through a defined role rather than generic praise.
4. **Traceability:** the contribution is supported by a source, event record, testimony, system log, commit, or other provenance evidence.
5. **No displacement:** recognizing the contribution does not erase or diminish the original author or other contributors.
6. **No inflation:** merely being present, causally remote, institutionally adjacent, or theoretically replaceable does not itself establish facilitation credit.
7. **Status labeling:** verified, user-attested, system-recorded, inferred, contested, or unverified status is explicit.

## 5. Credit is not authorship

The following inferences are prohibited:

- discovery does not imply authorship;
- interpretation does not imply authorship;
- repository integration does not imply authorship;
- authorization does not imply authorship;
- facilitation does not imply ownership;
- citation does not imply endorsement;
- causal participation does not imply agreement with later uses;
- prominent credit to one contributor does not justify suppressing another;
- hypothetical substitutability does not erase actual historical participation.

## 6. Event-chain model

Extended provenance is event-centered.

The minimum incorporation sequence is:

`Source → Publication or Materialization → Encounter or Discovery → Recognition → Transmission → Retrieval → Verification → Interpretation → Synthesis → Authorization → Integration → Validation`

Not every sequence contains every stage. Missing stages must not be invented. Each stage that did occur should be represented as a distinct event connected to participants, inputs, outputs, time, place or medium, and evidentiary status.

## 7. Required provenance record

For each materially significant inclusion, record:

- stable source identifier;
- incorporated object identifier;
- source author or originator;
- source title or description;
- publication or materialization context;
- encounter or discovery event;
- recognizing actor;
- transmitting actor;
- retrieval and verification events;
- interpretation and synthesis events;
- authorizing directive;
- integration event and repository location;
- validation or contestation status;
- timestamps or bounded temporal descriptions;
- location or medium where relevant;
- evidence for each link;
- confidence and provenance class for each assertion;
- revision history.

## 8. Credit statement format

A human-readable extended provenance statement should distinguish roles:

> **Original source:** [originator and work]  
> **Public or material context:** [publisher, program, installation, repository, or medium]  
> **Encountered or discovered by:** [actor]  
> **Recognized and transmitted by:** [actor or actors]  
> **Retrieved or verified by:** [actor or agents]  
> **Interpreted or synthesized by:** [actor or agents]  
> **Formal inclusion authorized by:** [authority]  
> **Integrated by:** [actor, agent, or process]  
> **Validation status:** [status and validator]

## 9. Application to “Stewardship of the Smallest Things”

The normative module derived from Eileen O’Toole’s untitled sidewalk poem must preserve at least the following arc:

1. Eileen O’Toole originated the poem.
2. Saint Paul’s sidewalk-poetry program selected and publicly materialized it.
3. The poem was instantiated in sidewalk concrete.
4. 😈Yūrei🌈 encountered the inscription while walking the block.
5. 😈Yūrei🌈 retained and later transmitted the remembered passage into this conversation.
6. The assistant retrieved and verified the source, restored lineation, and corrected the uncertain word.
7. 😈Yūrei🌈 initiated interpretive inquiry.
8. The assistant produced a labeled interpretation.
9. 😈Yūrei🌈 recognized the interpretation as materially relevant and directed normative consolidation.
10. The assistant integrated the resulting module into Caeluviim.
11. Later validation and ratification remain separate.

This account credits O’Toole as author while also crediting 😈Yūrei🌈 as encounterer, discoverer within the project context, transmitter, recognizer of material value, and authorizing architect. The assistant is credited as retriever, verifier, interpreter, synthesizer, and integrator. The public-art program is credited as publisher and materializer.

## 10. Graph model

### Required entities

- `Source`
- `Expression`
- `Artifact`
- `Agent`
- `Institution`
- `Event`
- `EncounterEvent`
- `DiscoveryEvent`
- `RecognitionEvent`
- `TransmissionEvent`
- `RetrievalEvent`
- `VerificationEvent`
- `InterpretationEvent`
- `SynthesisEvent`
- `AuthorizationEvent`
- `IntegrationEvent`
- `ValidationEvent`
- `ContributionAssertion`
- `Evidence`
- `Provenance`

### Core relations

- `ORIGINATED`
- `PUBLISHED`
- `MATERIALIZED`
- `ENCOUNTERED`
- `DISCOVERED`
- `RECOGNIZED_VALUE_IN`
- `TRANSMITTED`
- `RETRIEVED`
- `VERIFIED`
- `INTERPRETED`
- `SYNTHESIZED`
- `FACILITATED`
- `AUTHORIZED`
- `INTEGRATED`
- `VALIDATED`
- `CONTESTED`
- `PARTICIPATED_IN`
- `GENERATED`
- `USED`
- `DERIVED_FROM`
- `SUPPORTED_BY`

## 11. Minimal invariants

1. Every authorship claim must identify its evidentiary basis.
2. Facilitation credit must not overwrite authorship.
3. Every contribution assertion must specify a role and event.
4. Actual historical participation must not be erased because the role was theoretically replaceable.
5. Unverified or user-attested links must be labeled accordingly.
6. Interpretive contribution must remain distinguishable from source meaning and authorial intent.
7. Inclusion authorization must remain distinguishable from validation and ratification.
8. Contribution credit must be proportionate to the documented action.
9. All material contributors must be representable without forcing exclusive or hierarchical credit.
10. Corrections must supersede prior assertions without destroying the historical record.

## 12. Canonical proposed value

**Caeluviim recognizes that knowledge enters a living system through chains of encounter, attention, recognition, transmission, interpretation, authorization, and integration. The original creator must receive authorship credit, while every documented actor whose material contribution formed the actual path of incorporation must receive role-specific facilitation credit. A full provenance account preserves not only where content came from, but how it came to matter here.**

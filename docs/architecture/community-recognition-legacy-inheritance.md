# Community Recognition and Legacy Inheritance

**Doctrine ID:** CAELUVIIM-PROV-COMMUNITY-RECOGNITION-001  
**Version:** 0.1.0  
**Status:** Proposed extension; architect-directed consolidation  
**Extends:** CAELUVIIM-PROV-EXTENDED-FACILITATION-001

## 1. Core proposition

Formal recognition must not be limited to the persons explicitly attributed as authors, creators, or owners of a work.

Communities inherit value through interconnected chains of creation, preservation, materialization, encounter, remembrance, discovery, interpretation, extension, transmission, adoption, and renewed legacy. A person who brings materially valuable content into a community may therefore deserve explicit recognition even when that person did not originate the underlying work.

This recognition does not dilute authorship. It records a different contribution: making inherited value available, intelligible, relevant, or usable within a new community context.

## 2. Recognition principle

**Every person or agent whose documented action materially carries inherited value into, through, or forward from a community must be eligible for role-specific recognition.**

Recognition may attach to:

- preserving a source that might otherwise be lost;
- encountering and remembering a work;
- identifying value not previously visible to the community;
- bringing the work into a new context;
- interpreting or connecting it to current needs;
- extending it through new applications;
- transmitting it to future participants;
- maintaining the conditions under which others can continue the legacy.

## 3. Legacy arc

The relevant provenance chain is not merely:

`Author → Work`

It may instead be:

`Prior inheritance → Creation → Preservation → Materialization → Encounter → Recognition → Transmission → Interpretation → Community inclusion → Extension → Preservation of the extension → Future inheritance`

No single record will contain every stage. Missing stages must not be invented. Documented stages must not be collapsed merely because only one actor is traditionally credited.

## 4. Community-value recognition

Caeluviim distinguishes four independent forms of recognition:

| Recognition | Meaning |
|---|---|
| `AuthorshipRecognition` | Credit for originating an expression, work, claim, or artifact. |
| `StewardshipRecognition` | Credit for preserving, maintaining, caring for, or materially carrying inherited value. |
| `FacilitationRecognition` | Credit for enabling value to enter or move through the community. |
| `ExtensionRecognition` | Credit for materially developing, applying, translating, connecting, or transmitting inherited value into a new legacy layer. |

These forms may coexist. None automatically implies ownership, control, endorsement, or authorship.

## 5. Recognition right

A materially contributing participant has a defeasible claim to be visible in the provenance record when:

1. the participation actually occurred;
2. the contribution was material rather than incidental;
3. the role can be specified;
4. evidence or an explicit attestation supports the claim;
5. recognition does not displace or distort the contribution of another;
6. uncertainty, contestation, or incomplete verification is plainly labeled.

Recognition should be proportionate to the contribution and expressed in the most specific available terms.

## 6. Legacy inheritance principle

No community begins from nothing. Every new contribution is situated within inherited language, knowledge, practices, institutions, environments, technologies, memories, and relationships.

Caeluviim therefore treats legacy as a continuously extended inheritance rather than a sequence of isolated ownership events.

A complete provenance account should be capable of representing:

- what was inherited;
- from whom or through what institutions it arrived;
- who preserved or transmitted it;
- who recognized its value;
- who extended it;
- how the extension changed the community;
- what is then passed forward.

## 7. Normative value

**A community should recognize not only those who first made something, but also those who kept it alive, found it, carried it, understood it, connected it, extended it, and made it available to others.**

Recognition is not ornamental. It is part of truthful historical accounting, equitable participation, community memory, and the preservation of legacy.

## 8. Application to the sidewalk-poem incorporation arc

The poem remains attributed to its author. The public-art program remains credited for selection and materialization. 😈Yūrei🌈 is separately recognized for encountering the work, remembering it, transmitting it, identifying its value for Caeluviim, initiating interpretation, and authorizing incorporation. Lux / ChatGPT is separately recognized for retrieval, verification, interpretation, synthesis, and integration.

The resulting Caeluviim module becomes a further legacy layer. Its later users, validators, translators, implementers, and stewards may receive their own role-specific recognition without displacing any earlier participant.

## 9. Required graph additions

### Entities

- `LegacyInheritance`
- `CommunityRecognition`
- `StewardshipContribution`
- `FacilitationContribution`
- `ExtensionContribution`
- `TransmissionContribution`

### Relations

- `INHERITED_FROM`
- `PRESERVED_BY`
- `CARRIED_BY`
- `BROUGHT_INTO_COMMUNITY_BY`
- `RECOGNIZED_VALUE_THROUGH`
- `EXTENDED_BY`
- `TRANSMITTED_FORWARD_BY`
- `RECOGNIZED_FOR`
- `BECAME_LEGACY_FOR`

## 10. Minimal invariants

1. Community recognition must not overwrite authorship.
2. Recognition must identify the specific contribution being recognized.
3. Inherited value must not be represented as arising ex nihilo.
4. Material facilitators must be representable even when conventional attribution systems omit them.
5. Recognition must remain possible for non-exclusive and overlapping contributions.
6. Later extension must preserve the provenance of earlier work.
7. Future inheritance must be traceable back through prior preservation and extension events where evidence exists.
8. Recognition claims remain correctable and contestable without erasing historical records.

## 11. Canonical proposed value

**Caeluviim understands legacy as an interconnected inheritance carried across persons, communities, institutions, artifacts, and time. Authorship remains distinct and protected, while those who preserve, encounter, recognize, transmit, interpret, extend, and bring value into community life receive explicit role-specific recognition. What matters is not only who first created something, but the full traceable history through which it remained alive, became meaningful here, and was carried forward.**

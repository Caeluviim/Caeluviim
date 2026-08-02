# Universal Claim Card-Node Saturation Standard

**Status:** Consolidated architectural extension v0.1.0  
**Parent standard:** `docs/architecture/relational-definition-standard.md`

## 1. Claim as card and node

A Claim is represented as a graph node whose inspectable surface is a full definitional card.

The node and the card are not separate semantic entities:

- the node supplies stable graph identity and relations;
- the card supplies the complete human- and machine-readable projection of the Claim's universal structure;
- every card field resolves through Claims and Claim relations;
- opening a card reveals an entry point into an indefinitely extensible Claim graph.

A Claim-card is therefore simultaneously:

1. a stable node identity;
2. a complete definitional interface;
3. a provenance object;
4. a semantic-result record;
5. a Claim-work surface;
6. a recursive navigation point into related Claims.

## 2. Invariant shape, scope-relative extent

Every Claim-card MUST use the same universal field structure.

An automobile Claim-card and an existence Claim-card contain the same required field groups. They differ only in the amount, density, recursion depth, extension, contestation, and unresolved horizon required by the conception being defined.

```text
Shape(ClaimCard_automobile) = Shape(ClaimCard_existence)
Extent(ClaimCard_automobile) ≠ Extent(ClaimCard_existence)
```

The narrower domain does not receive a reduced schema. The larger domain does not receive a privileged schema. Each card maximally resolves the same criterion relative to its declared conceptual scope and current condition field.

## 3. Maximal saturation rule

A Claim-card MUST pursue maximal available information content pursuant to the shape of the conception being defined.

Maximal saturation means:

- every universal field is populated to the fullest source-supported extent currently available;
- every material relation discovered through Claim work is represented;
- every missing field is marked by an explicit unresolved Claim rather than omitted;
- every non-applicable field includes a reason Claim establishing why it is non-applicable for the declared scope;
- every contested field preserves competing Claims rather than selecting an unmarked winner;
- every inherited field identifies the Claim from which it is inherited and the conditions under which inheritance remains valid;
- every summary remains linked to the fuller Claims it compresses;
- no card is treated as complete because its visible prose is concise.

The saturation target is not infinite textual accumulation. It is complete relational availability.

## 4. Scope declaration

Every Claim-card MUST declare the conception scope it is defining.

A scope declaration includes:

- defined locus;
- declared level of abstraction;
- temporal scope;
- spatial or jurisdictional scope where applicable;
- disciplinary or operational scope;
- intended protocol purpose;
- known exclusions;
- unresolved boundary Claims;
- relation to broader and narrower Claim-cards.

Scope limits representation without reducing structural completeness.

## 5. Example: automobile and existence

### Automobile Claim-card

An automobile card resolves the universal structure across fields including:

- lexical and etymological history of automobile and related terms;
- mechanical and functional constitution;
- vehicle, machine, property, commodity, infrastructure, environmental, legal, social, cultural, and economic relations;
- classes, subtypes, boundary cases, exclusions, and historical variants;
- manufacture, ownership, operation, maintenance, injury, regulation, labor, energy, roads, insurance, finance, disposal, and ecological consequences;
- glyph, multilingual, formal, graph, provenance, contestation, and revision fields.

Its representational extent is large but bounded by a comparatively delimited conception.

### Existence Claim-card

An existence card resolves the same universal fields but necessarily reaches through:

- ontology, predication, manifestation, persistence, absence, possibility, identity, relation, time, process, experience, language, logic, science, religion, law, and cultural inheritance;
- competing and irreconcilable frameworks;
- self-referential Claims about what it means for Claims and loci to exist;
- cross-scale and cross-domain extension;
- an exceptionally broad unresolved horizon.

The existence card does not possess a different kind of structure. It has a larger and more recursive representational field.

## 6. Card completeness

Card completeness is evaluated along two independent axes:

### Structural completeness

Every required field exists and has a resolution state.

### Saturation completeness

Every field is filled to the maximum presently supportable extent for the declared scope.

A card may therefore be structurally complete but saturation-incomplete.

```text
StructurallyComplete(c) := every required field of c has an explicit state
SaturatedAt(c, Γt) := no presently available material Claim is omitted from c's declared scope without an exclusion reason
```

Saturation remains condition-bound and revisable. New evidence, language anchors, relations, interpretations, or consequences generate new Claim work rather than proving the prior card invalid as a historical state.

## 7. Recursive field rule

A full card does not embed every related Claim as duplicated text. It links to recursive Claim-cards.

For example, the automobile card may link to full cards for:

- engine;
- road;
- property;
- injury;
- carbon emission;
- labor;
- insurance;
- mobility;
- accessibility;
- law.

Each linked card has the same universal structure. The automobile card records the typed relation and the scope in which the linked Claim contributes to the automobile conception.

This prevents both reduction and uncontrolled duplication.

## 8. Card rendering layers

Every Claim-card may be rendered at multiple depths without changing its underlying structure:

| Rendering | Function |
|---|---|
| Identifier view | Claim ID, glyph, protocol name, status, and one-line orientation. |
| Compact card | Core relational configuration, scope, provenance, status, and key relations. |
| Full card | Every universal field with explicit resolution states. |
| Expanded graph view | Recursive related Claim-cards, histories, conflicts, evidence, and implementation projections. |
| Machine serialization | Complete structured representation for schema validation and graph ingestion. |

A compact rendering is not a reduced Claim. It is a view over the same full card-node.

## 9. Information-content principle

The informational potential of a Claim-card is constrained by the conception being defined, available evidence, present Claim work, and declared scope—not by arbitrary schema reduction.

```text
PotentialContent(c) = f(scope, relations, evidence, history, contestation, consequences, unresolved horizon)
```

The universal shape supplies equal epistemic dignity to every Claim. Scope-relative saturation supplies proportionate representational depth.

## 10. Governance consequence

No Claim may be admitted as canonically represented through a label, gloss, or one-sentence text property alone.

Admission requires:

1. universal card instantiation;
2. explicit scope;
3. source and provenance attachment;
4. current saturation assessment;
5. unresolved-field records;
6. glyph and multilingual field states;
7. Claim-work and governance status;
8. machine validation against the universal Claim schema when implemented.

The card-node architecture is now a mandatory derivative of the universal Claim structure.
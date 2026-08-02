# Invariant Rider Lexicon and Multilingual Incorporation

**Status:** Binding architectural correction v0.2.0  
**Applies to:** every formal Definition Claim incorporated into canonical Caeluviim state  
**Extends:**
- `docs/architecture/standardized-definition-claim-structure.md`
- `docs/architecture/definition-claim-linguistic-etymological-multilingual-glyph-structure.md`
- `docs/architecture/definition-claim-nesting-and-composition.md`

## 1. Governing principle

The Caeluviim rider is one invariant protocol lexicon that remains the same regardless of the language beneath it.

It does not select a different extra-lingual term relative to each host language. It replaces the same central host-language words in every language with the same canonical rider lexemes.

```text
InvariantRiderLexicon R
+ HostLanguage H
→ RiderRealization(R over H)
```

For every host language `H`, the rider lexeme for a conception remains the same.

```text
CanonicalRiderLexeme(c, H₁)
= CanonicalRiderLexeme(c, H₂)
= CanonicalRiderLexeme(c)
```

The host language supplies grammar, syntax, inflectional accommodation, explanatory prose, and local accessibility. It does not supply the canonical protocol name for a conception already assigned within the rider.

## 2. Replacement rather than translation attachment

The rider is not a translation layer attached beside ordinary host-language vocabulary.

For a rider-governed conception:

```text
host-language word
→ remains available as gloss, alias, search key, and explanation
→ is replaced in canonical protocol use by the invariant rider lexeme
```

Thus the same rider lexeme appears inside English, Ojibwe, French, Arabic, or any other host-language expression.

```text
English grammar + rider lexeme
Ojibwe grammar + same rider lexeme
French grammar + same rider lexeme
Arabic grammar + same rider lexeme
```

The protocol therefore forms one translingual nomenclature rather than separate translated protocol vocabularies.

## 3. Lexical strata

The rider lexicon has at least two lexical strata.

### 3.1 Core lexical stratum

The most structurally central conceptions MUST preferentially receive canonical rider lexemes from lost, dormant, sleeping, extinct, endangered, severely displaced, or otherwise historically suppressed languages.

The purpose is to make those languages constitutive of the protocol's central operations rather than ornamental references at its margins.

Core conceptions include at least:

- Claim;
- conception;
- definition;
- relation;
- truth;
- meaning;
- knowledge;
- care;
- harm;
- dignity;
- consent;
- agency;
- responsibility;
- trust;
- justice;
- repair;
- memory;
- identity;
- continuity;
- governance;
- authority;
- provenance;
- evidence;
- dialogue;
- personhood;
- possibility;
- probability;
- manifestation;
- difference;
- dislocation;
- reconnection;
- union.

A term from a living but endangered or revitalizing language may enter this stratum only with source, community, use-condition, and governance Claims sufficient to avoid treating the language as an extractive word supply.

A term from an extinct or historically documented language requires reliable attestation, morphological analysis where possible, source provenance, uncertainty, and explicit distinction between attested meaning and protocol extension.

### 3.2 Compositional lexical stratum

Less-central and derivative protocol terms MAY be constructed through consolidation across the existing multilingual lexicon.

```text
SecondaryRiderTerm(s)
:= governed composition of existing rider lexemes,
   sourced language elements, operators, and glyph relations
```

A secondary term may be:

- a compound of existing canonical rider lexemes;
- a derivation from one rider lexeme using a governed protocol affix or operator;
- a composite drawing sourced elements from more than one language;
- a glyph–lexeme compound;
- a shortened operational form derived from a fully represented Definition Claim.

The composition MUST preserve the source identity and semantic contribution of every component. It may not fabricate the appearance of a natural historical word in any source language.

## 4. Conception and lexical roles

The architecture distinguishes:

```text
canonical conception identity
≠ canonical rider lexeme
≠ host-language gloss
≠ source-language lexical Claim
≠ compositional rider term
≠ additional multilingual anchor
≠ glyph or emoji-rider manifestation
```

- **Canonical conception identity:** stable language-independent Claim ID.
- **Canonical rider lexeme:** invariant ratified protocol word used across all host languages.
- **Host-language gloss:** local explanatory, searchable, and accessibility rendering.
- **Source-language lexical Claim:** the attested lexical form and its own historical semantic structure.
- **Compositional rider term:** a governed protocol construction assembled from represented lexical components.
- **Additional multilingual anchor:** a source-bound relation that supports, contrasts, extends, or qualifies the conception.
- **Glyph or emoji-rider manifestation:** the invariant visual-symbolic companion or compression of the conception.

The rider lexeme is canonical nomenclature, not the conception's ontological identity. The Claim ID and full Definition Claim field remain primary for machine identity and semantic reconstruction.

## 5. Core-source priority

Core lexeme selection MUST prioritize languages according to a declared restoration-oriented source policy.

The policy SHOULD prioritize:

1. extinct or no-longer-natively-spoken languages with sufficiently reliable documentation;
2. dormant or sleeping languages undergoing reclamation or revitalization;
3. critically endangered languages;
4. severely displaced Indigenous and minoritized languages;
5. languages whose conceptual contributions have been historically appropriated, erased, or subordinated;
6. additional languages needed to distribute the lexicon across families, regions, and scripts.

Priority does not create automatic permission. Selection MUST preserve:

- community authority where a living or revitalizing community exists;
- restrictions on sacred, ceremonial, private, or role-limited language;
- contributor and source provenance;
- uncertainty and disagreement;
- distinction between attested meaning and Caeluviim's ratified protocol use;
- non-erasing replacement or withdrawal procedures.

## 6. No false naturalization

Caeluviim MUST distinguish an inherited source-language word from a newly created protocol construction.

```text
AttestedLexeme
≠ RevivedLexeme
≠ ReconstructedLexeme
≠ CaeluviimProtocolCoinage
≠ MultilingualComposite
```

Every rider term MUST declare which of these states applies.

A multilingual composite MUST NOT be presented as if it were an authentic inherited word of any contributing language. Its morphology, component boundaries, construction event, and protocol-only status must remain explicit.

## 7. Formal incorporation gate

A formal Definition Claim is not incorporated merely because a root definition or host-language rendering has been committed to GitHub.

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

For core conceptions, the rider lexeme MUST satisfy the lost-language core-source policy unless an explicit contested governance exception is recorded.

For less-central conceptions, a governed composite from the existing multilingual rider field may satisfy the lexical requirement.

## 8. Required lexical record

Every canonical rider lexeme MUST have a provenance-bearing lexical record containing:

- conception Claim ID and version;
- canonical rider lexical Claim ID;
- exact form and script;
- classification as attested, revived, reconstructed, protocol coinage, or multilingual composite;
- source language or contributing languages;
- dialect, community, region, and period where known;
- pronunciation and phonological form where available;
- morphology and component segmentation;
- etymology and semantic history;
- attested local meanings and source contexts;
- exact source manifestations and citation locations;
- contributing, proposing, selecting, and ratifying loci;
- reason for selection or construction;
- relation to the canonical conception;
- distinction between source meaning and protocol meaning;
- equivalence, partial-equivalence, extension, narrowing, conflict, and non-equivalence Claims;
- cultural, ceremonial, institutional, or restricted-use conditions;
- host-language glosses;
- governance and ratification state;
- unresolved objections, variants, and alternatives.

## 9. Compositional term grammar

A less-central rider term MAY be synthesized only through a declared compositional grammar.

The grammar MUST specify:

- permissible lexical components;
- operator and affix inventory;
- ordering and attachment rules;
- phonological or orthographic adaptation rules;
- script strategy;
- semantic composition rules;
- conflict and ambiguity checks;
- accessibility and pronunciation;
- versioning and deprecation;
- source attribution for every component;
- prohibition on false representation as a natural source-language form.

```text
CompositeTerm
→ component Claim identities
→ typed composition relations
→ synthesized protocol definition
→ source and construction provenance
```

A composite is accepted only when the resulting meaning can be reconstructed from its components and Definition Claim nesting.

## 10. Invariant rendering across host languages

The canonical rider lexicon remains stable across interfaces.

```text
Rider(c) over English
= same canonical rider lexeme

Rider(c) over Ojibwe
= same canonical rider lexeme

Rider(c) over French
= same canonical rider lexeme
```

Host-language integration MAY alter:

- grammatical particles;
- case marking;
- agreement;
- article use;
- word order;
- explanatory gloss placement;
- transliteration display;
- pronunciation assistance.

It MUST NOT silently replace the canonical rider lexeme with a host-language synonym.

## 11. Search, display, and learning behavior

Every interface SHOULD display:

```text
canonical rider lexeme
(host-language gloss)
[glyph where ratified]
```

The system MUST support lookup by:

- rider lexeme;
- host-language gloss;
- source-language form;
- Claim ID;
- glyph;
- conceptual relation;
- component lexemes for composites.

At first exposure, the host-language gloss and concise Definition Claim may be shown prominently. As familiarity increases, the rider lexeme becomes the default nomenclature while the gloss remains available on demand.

## 12. Existing-card correction

Every existing Definition Claim represented primarily through English nomenclature MUST be reclassified according to its actual rider implementation state.

For the current interpersonal corpus:

```text
42 English-labeled Definition Claim roots
→ root and partial-card content captured
→ nested Claim migration pending
→ lexical and etymological source binding pending
→ core or compositional rider lexeme assignment pending
→ multilingual and glyph implementation pending
→ not yet formally incorporated
```

English terms remain working glosses and search aliases. They are not final canonical protocol nomenclature.

## 13. Validation failures

Validation MUST reject:

- host-relative lexical substitution that assigns different canonical rider terms to the same conception in different host languages;
- formal-incorporation status without an invariant canonical rider lexeme;
- a core conception whose canonical term ignores the lost-language source priority without a declared governance exception;
- a multilingual composite presented as a natural inherited word;
- source components without stable lexical Claim identities and provenance;
- unsourced etymology, morphology, local meaning, or usage Claims;
- dictionary-gloss equivalence treated as complete semantic identity;
- a rider lexeme present in prose but absent from machine serialization, maps, parser, model access, or display;
- inaccessible scripts or glyphs without transliteration, textual fallback, and accessibility description;
- culturally restricted language incorporated without authority;
- decorative multilingualism that contributes no semantic structure;
- silent reversion to host-language vocabulary in canonical protocol operations.

## 14. Constitutional formulation

> Caeluviim uses one invariant rider lexicon across every host language. The host language supplies grammatical and explanatory scaffolding, while the rider replaces the same central vocabulary regardless of the language beneath it. The most central rider lexemes are preferentially sourced from lost, dormant, endangered, displaced, and historically suppressed languages with full provenance, authority, and semantic limits. Less-central terms may be governed compounds or derivations synthesized from the accumulated multilingual rider field. Every term preserves its source identity, construction history, Definition Claim structure, and distinction between inherited language and protocol coinage.

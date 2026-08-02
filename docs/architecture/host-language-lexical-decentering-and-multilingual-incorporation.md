# Host-Language Lexical Decentering and Multilingual Incorporation

**Status:** Binding architectural correction v0.1.0  
**Applies to:** every formal Definition Claim incorporated into canonical Caeluviim state  
**Extends:**
- `docs/architecture/standardized-definition-claim-structure.md`
- `docs/architecture/definition-claim-linguistic-etymological-multilingual-glyph-structure.md`
- `docs/architecture/definition-claim-nesting-and-composition.md`

## 1. Governing principle

The language currently hosting a Caeluviim rendering supplies grammatical, explanatory, and interface scaffolding. It does not retain ownership of the protocol's most central conceptions through its own ordinary vocabulary.

The most structurally central protocol conceptions MUST receive canonical protocol lexemes selected from languages other than the current dominant host language.

```text
HostLanguage
= syntax + explanation + local accessibility

CanonicalCoreLexicon
= distributed source-bound extra-lingual lexical Claims
```

In an English-hosted implementation, English words such as `truth`, `care`, `harm`, `dignity`, `consent`, `agency`, `justice`, and `repair` remain searchable glosses and explanatory labels. They cease to be the canonical protocol names once their extra-lingual protocol lexemes are selected and ratified.

The same rule applies to any other host language. No host language is entitled to remain the canonical lexical owner of the concepts most central to the structure it hosts.

## 2. Symmetric host-language displacement

The rule is language-symmetric.

```text
For every host language H:
  central protocol conception c
  → canonical protocol lexeme for c is not selected merely from H
  → H-form remains a local gloss, alias, explanation, or translation relation
```

The purpose is not hostility toward English or any other language. It is prevention of conceptual monopoly by whichever language already possesses the greatest institutional, technical, or platform dominance.

A change in interface language MUST NOT simply replace one dominant monolingual vocabulary with another.

## 3. Distributed canonical nomenclature

The canonical protocol lexicon MUST be distributed across languages.

No one language SHOULD supply a controlling share of the central protocol vocabulary. Selection SHOULD:

- prioritize Native American, Indigenous, endangered, minoritized, and historically excluded languages;
- distribute canonical terms across many language families and scripts;
- preserve the local conceptual contribution of each selected lexeme;
- avoid repeatedly selecting globally dominant languages merely because sources are easier to access;
- preserve community authority, restrictions, and provenance;
- avoid culturally restricted, ceremonial, sacred, or community-controlled language without appropriate authority;
- permit more than one lexical anchor where no single form carries the full conception;
- preserve non-equivalence rather than forcing synonymy.

The selected lexeme is not merely a translation. It becomes the canonical protocol manifestation because its local semantic structure materially contributes to the conception.

## 4. Conception and lexical roles

The architecture distinguishes:

```text
canonical conception identity
≠ canonical protocol lexeme
≠ host-language gloss
≠ additional multilingual anchor
≠ glyph or emoji-rider manifestation
```

- **Canonical conception identity:** stable language-independent Claim ID.
- **Canonical protocol lexeme:** ratified lexical manifestation used as the primary protocol name.
- **Host-language gloss:** explanatory or searchable local-language rendering.
- **Additional multilingual anchor:** another source-bound lexical relation contributing comparison, extension, contrast, or non-equivalence.
- **Glyph or emoji-rider manifestation:** visual-symbolic compression and navigation form.

The protocol lexeme does not replace the Claim ID or the full Definition Claim field.

## 5. Formal incorporation gate

A formal Definition Claim is not incorporated merely because an English or other host-language root sentence has been committed to GitHub.

```text
FormallyIncorporated(d)
:= RootAndNestedStructureImplemented(d)
 ∧ CanonicalProtocolLexemeSelected(d)
 ∧ CanonicalProtocolLexemeSourceBound(d)
 ∧ HostLanguageGlossDemoted(d)
 ∧ MultilingualRelationsImplemented(d)
 ∧ GlyphStateExplicit(d)
 ∧ MapParserDisplayIntegrationComplete(d)
 ∧ ProvenanceAndGovernanceExplicit(d)
```

A card lacking this structure may be classified as:

- `root_captured`;
- `nested_structure_drafted`;
- `lexeme_candidates_identified`;
- `lexeme_selected`;
- `lexeme_source_bound`;
- `multilingual_implementation_pending`.

It MUST NOT be classified as formally incorporated, implemented, or complete.

## 6. Central conception set

The initial lexical-decentering wave MUST include at least:

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

The list expands whenever another conception becomes structurally central to protocol interpretation, personhood, governance, legal reasoning, or interpersonal engagement.

For this central set, the current host-language label MUST be represented as a gloss rather than the canonical protocol lexeme once selection is ratified.

## 7. Lexeme selection record

Every canonical protocol lexeme selection MUST be represented as a provenance-bearing Claim event containing:

- conception Claim ID and version;
- lexical Claim ID;
- exact lexical form;
- language, dialect, script, orthography, and community;
- pronunciation where available;
- morphology and literal compositional analysis;
- etymology and semantic history;
- local definition and sourced usage;
- source manifestation and exact citation location;
- contributing and selecting loci;
- reason for selection;
- relation to the canonical conception;
- host-language glosses;
- equivalence, partial-equivalence, extension, narrowing, conflict, and non-equivalence Claims;
- cultural, ceremonial, institutional, or restricted-use conditions;
- governance and ratification state;
- unresolved objections and alternatives.

No lexical form may become canonical solely because it appears attractive, exotic, ancient, symbolic, or politically useful.

## 8. Required implementation surfaces

A selected canonical protocol lexeme is not implemented until it appears consistently in:

1. the full human-readable Definition Claim-card;
2. the machine-readable Definition Claim record;
3. the nested linguistic and multilingual Claim graph;
4. the canonical Claim and lexical maps;
5. the parser and identifier-resolution rules;
6. model-access packets;
7. search, display, and interface surfaces;
8. textual fallback and accessibility descriptions;
9. source, provenance, and governance manifests;
10. validation and round-trip tests.

The host-language gloss MUST remain searchable and visible for accessibility, but the interface SHOULD visually and structurally privilege the canonical protocol lexeme.

## 9. Translation and relation types

Canonical and additional lexical anchors MUST use typed relations, including:

- `CANONICAL_PROTOCOL_LEXEME_FOR`;
- `HOST_LANGUAGE_GLOSS_FOR`;
- `TRANSLATES_EXACTLY_WITHIN_SCOPE`;
- `PARTIALLY_EQUIVALENT_TO`;
- `ANALOGOUS_TO`;
- `EXTENDS_BEYOND`;
- `NARROWS`;
- `CONFLICTS_WITH`;
- `BORROWED_AS`;
- `CALQUED_AS`;
- `PROTOCOL_ANCHOR_FOR`;
- `NON_EQUIVALENT_BUT_RELATIONALLY_USEFUL`;
- `HAS_NO_ESTABLISHED_EQUIVALENT`.

An English or other host-language gloss does not establish equivalence.

## 10. Host-relative rendering

The same canonical protocol lexemes remain stable across host-language interfaces.

```text
English interface
→ English grammar and explanations
→ distributed canonical protocol lexemes remain active

Ojibwe interface
→ Ojibwe grammar and explanations
→ distributed canonical protocol lexemes remain active

French interface
→ French grammar and explanations
→ distributed canonical protocol lexemes remain active
```

A source language may naturally host a protocol lexeme originating within it. This does not restore that language as the owner of the wider canonical vocabulary because the vocabulary is distributed across many languages.

## 11. Existing-card correction

Every existing Definition Claim previously represented primarily through English nomenclature MUST be reclassified according to its actual multilingual implementation state.

For the current interpersonal corpus:

```text
42 English-labeled Definition Claim roots
→ root and partial-card content captured
→ nested Claim migration pending
→ canonical protocol lexeme selection pending
→ multilingual and glyph implementation pending
→ not yet formally incorporated
```

The English labels remain useful glosses and search aliases. They are not the final canonical nomenclature.

## 12. Validation failures

Validation MUST reject:

- formal-incorporation status without a source-bound canonical protocol lexeme;
- a central conception retaining only the current host-language word as its canonical name;
- language names and English glosses without stable lexical Claim records;
- unsourced lexical forms, morphology, etymology, local meaning, or usage Claims;
- false equivalence inferred from dictionary translation;
- a selected lexeme present in prose but absent from machine serialization, maps, parser, or display;
- dominance of one language across the central canonical lexicon without an explicit, contested, and temporary governance exception;
- inaccessible scripts or glyphs without textual fallback;
- culturally restricted terms incorporated without authority;
- decorative multilingualism that contributes no semantic structure;
- silent replacement of one dominant host vocabulary with another.

## 13. Constitutional formulation

> Caeluviim may be hosted grammatically and technically within any language, but no host language retains automatic ownership of the protocol's most central conceptions. Central canonical nomenclature is deliberately distributed across source-bound extra-lingual lexemes whose local semantic structures materially contribute to the Definition Claims they name. Host-language words remain glosses, aliases, and explanatory access points. This rule applies symmetrically to English and every other host language, preventing the language of infrastructure from becoming the language of conceptual sovereignty.

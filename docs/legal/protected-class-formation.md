# Legal Formation of Protected Classes

**Status:** Proposed consolidation record  
**Domain:** United States constitutional and civil-rights law  
**Purpose:** Define the mechanisms by which legally protected classifications are created, interpreted, expanded, and enforced, and specify the graph structure required to represent them without collapsing distinct legal regimes.

## Core proposition

A “protected class” is not a single nationwide status conferred upon a group once and for all. It is shorthand for a characteristic that a particular constitutional provision, statute, regulation, or judicial doctrine prohibits a specified decision-maker from using in a specified domain.

Protection is therefore relational and authority-bound:

`Characteristic → Legal Instrument → Regulated Domain → Covered Actor → Prohibited Act → Enforcement Authority → Cause of Action → Remedy → Judicial Standard`

The graph must not encode a characteristic as merely `PROTECTED = TRUE`. It must encode:

`PROTECTED_UNDER [specific authority] AGAINST [specific conduct] BY [specific covered actor] WITHIN [specific domain] SUBJECT_TO [exceptions, procedure, and remedy]`.

## Four principal legal routes

| Route | Mechanism | Legal effect |
|---|---|---|
| Constitutional amendment | The people ratify constitutional language restricting government conduct or empowering Congress to enforce rights. | Creates supreme constitutional law binding governmental actors. |
| Legislation | Congress or a state legislature identifies characteristics, covered domains, prohibited conduct, covered actors, exceptions, procedures, enforcement authority, and remedies, then enacts the bill. | Creates statutory protection within the enacted instrument’s defined scope. |
| Judicial interpretation | Courts interpret constitutional language or statutory terms and determine the standard of review and the scope of existing text. | Can recognize that an existing provision covers conduct or classifications not previously settled. |
| Administrative implementation | An authorized agency promulgates regulations, investigates complaints, adjudicates matters, and brings enforcement actions within delegated authority. | Operationalizes statutory protection but ordinarily does not create a new statutory category outside delegated authority. |

## Historical formation sequence

The recurring formation sequence is:

`documented exclusion or inequality → collective organization and litigation → political demand → identification of constitutional authority → drafting → designation of protected characteristics and covered domains → legislative passage and enactment → administrative enforcement → judicial interpretation → amendment or expansion`.

### Reconstruction architecture

The Thirteenth, Fourteenth, and Fifteenth Amendments, the Civil Rights Act of 1866, and the Reconstruction Enforcement Acts established federal constitutional and statutory architecture for citizenship, equal protection, voting rights, and federal remedies.

The Fourteenth Amendment did not supply a closed table of protected classes. It established a general equal-protection command and expressly authorized congressional enforcement. Courts later developed standards of review for different governmental classifications.

### Civil-rights legislation

Congress converts political demands into operative legal protections by defining:

1. protected characteristic;
2. regulated domain;
3. covered actor;
4. prohibited conduct;
5. exceptions and defenses;
6. enforcement authority;
7. procedures and limitation periods;
8. causes of action;
9. available remedies.

Title VII of the Civil Rights Act of 1964 prohibits covered employment discrimination because of race, color, religion, sex, or national origin.

Later enactments and amendments created or expanded protection in particular domains, including the Age Discrimination in Employment Act, the Rehabilitation Act, the Americans with Disabilities Act, the Pregnancy Discrimination Act, the Genetic Information Nondiscrimination Act, Title IX, and amendments to the Fair Housing Act.

State and local enactments may protect additional characteristics, cover additional entities, or provide different remedies.

## Constitutional and statutory classification are distinct

Two legal concepts must remain separate:

| Concept | Meaning |
|---|---|
| Statutorily protected characteristic | A characteristic expressly named in a statute or included through binding statutory interpretation. |
| Constitutional suspect or quasi-suspect classification | A governmental classification that triggers heightened equal-protection scrutiny. |

Race classifications ordinarily receive strict scrutiny. Sex classifications ordinarily receive intermediate scrutiny. Age and disability classifications ordinarily receive rational-basis review under federal equal-protection doctrine, even though age and disability are protected by important federal statutes in specified domains.

A characteristic can therefore receive extensive statutory protection without being treated as a suspect classification under the Constitution.

## Judicial interpretation

Judicial interpretation may expand the operative coverage of an existing statutory term without the legislature adding a new phrase.

In *Bostock v. Clayton County*, the Supreme Court held that discrimination against an employee because of sexual orientation or transgender status is discrimination “because of sex” under Title VII.

That statutory holding does not itself establish a constitutional suspect classification for every purpose. In *United States v. Skrmetti*, the Supreme Court applied rational-basis review to the challenged Tennessee law and did not convert *Bostock* into a general equal-protection classification rule.

## Required graph model

### Required entities

- `Characteristic`
- `LegalInstrument`
- `ConstitutionalProvision`
- `Statute`
- `Regulation`
- `JudicialDecision`
- `RegulatedDomain`
- `CoveredActor`
- `ProhibitedAct`
- `Exception`
- `EnforcementAuthority`
- `CauseOfAction`
- `Remedy`
- `JudicialStandard`
- `ProtectedClassificationAssertion`
- `HistoricalFormationEvent`
- `Evidence`
- `Provenance`

### ProtectedClassificationAssertion

A protected-class assertion must contain or link to:

- stable assertion identifier;
- characteristic;
- jurisdiction;
- legal authority;
- authority type;
- effective dates;
- regulated domain;
- covered actor;
- prohibited conduct;
- protected persons;
- exceptions and defenses;
- enforcement authority;
- administrative exhaustion requirements;
- private cause of action status;
- remedies;
- judicial standard;
- controlling interpretation;
- current validity;
- provenance;
- validation status.

### Minimal invariants

1. No `ProtectedClassificationAssertion` is valid without a specific legal authority.
2. No assertion may infer universal coverage from protection in a single domain.
3. Constitutional scrutiny and statutory protection must be represented separately.
4. Judicial interpretation must identify the interpreted text and jurisdictional scope.
5. Administrative rules must identify their delegating statute.
6. Amendments and superseding decisions must be represented as revisions, not destructive overwrites.
7. Historical disadvantage, suspect-class status, and statutory coverage are distinct properties.
8. Every assertion must carry provenance and temporal validity.

## Consolidation determination

The canonical project rule is:

**Protected status is a governed legal relation, not an intrinsic boolean property of a person or group.**

This record is submitted as a proposed legal-ontology module. Graph ingestion does not ratify its legal conclusions; ratification and validation remain separate governance events.

## Primary authorities represented

- U.S. Constitution, Amendments XIII, XIV, and XV
- Civil Rights Act of 1866
- Reconstruction Enforcement Acts
- Civil Rights Act of 1964, including Title VII
- Fair Housing Act
- Age Discrimination in Employment Act
- Rehabilitation Act of 1973
- Americans with Disabilities Act
- Pregnancy Discrimination Act
- Genetic Information Nondiscrimination Act
- Title IX of the Education Amendments of 1972
- *Bostock v. Clayton County*, 590 U.S. 644 (2020)
- *United States v. Skrmetti*, 605 U.S. ___ (2025)

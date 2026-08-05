# Plasma Draft Completion Report

Date: 2026-08-05
Matter: MAT-PLASMA-2026-08-04-001
Branch: `lux/plasma-filing-packet-2026-08-05`
Base commit: `5417cf79e5accb0c1157843ddc8c914b21897417`

## Objective

Move the compensated-plasma matter from a corrected theory memorandum to an operative complaint-development packet while preserving evidentiary discipline and preventing unsupported filing claims.

## Repository audit

The audit located:

- `sources/matters/plasma/mat-plasma-2026-08-04-001.md`, the canonical source record;
- `docs/legal/compensated-plasma-extraction-case-repair.md`, the defect register and filing gate;
- no complaint-form working pleading;
- no row-level evidence and pleading ledger;
- no completion report tying new artifacts to the existing source and repair records.

## Actions completed

### 1. Created complaint-form working draft

Created `docs/legal/plasma/complaint-working-draft.md`.

The draft now contains:

- Minnesota district-court caption structure;
- nature-of-action allegations;
- parties, jurisdiction, and venue sections;
- plaintiff-specific factual allegations preserved from the canonical source;
- explicit machine-display ambiguity controls;
- standardized-practice and public-benefit allegations;
- five claim modules;
- declaratory and injunctive relief controls;
- a lawful prayer for relief; and
- nine explicit filing gates.

The draft does not invent defendant names, transaction dates, exact advertisements, medical diagnoses, or damages figures.

### 2. Created evidence and pleading ledger

Created `docs/legal/plasma/evidence-and-pleading-ledger.csv`.

The ledger provides row-level fields for:

- defendant and facility attribution;
- transaction date and period;
- speaker, source, medium, and exact statement;
- omission and observed practice;
- governing authority and effective date;
- falsity or breach basis;
- reliance and injury;
- evidence location and authentication;
- public-benefit basis;
- claim mapping;
- verification status; and
- permitted filing use.

Seed rows are marked `unverified` and `exclude_until_verified` to prevent unsupported allegations from entering a filed pleading.

### 3. Preserved legal and epistemic safeguards

The packet preserves the following controls already established in the source record and repair memorandum:

- terminology is not treated as dispositive liability proof;
- federal Source Plasma regulations are not pleaded as an implied private cause of action;
- Minn. Stat. § 8.31, subd. 3a is not described as automatically creating relator status;
- machine values are not treated as net plasma volume without device records;
- professional-negligence and informed-consent counts remain gated by expert and affidavit requirements;
- downstream plasma-product value is not used as an automatic damages measure; and
- statewide or aggregate relief is not asserted without a lawful procedural and evidentiary mechanism.

## Verification result

Repository-write verification succeeded for all three artifacts.

| Artifact | Commit |
|---|---|
| Complaint working draft | `9251c542e8b79b7ef4c1b7b182a04399f5b94729` |
| Evidence and pleading ledger | `9ff2ec7de75d6ba1637bea0308d24276d2fd272b` |
| Completion report | recorded by the commit creating this file |

## Current state

The repository now contains a coherent plasma complaint-development packet. It remains pre-filing because the canonical source record identifies unresolved event-level facts. The remaining work is evidentiary completion, not structural drafting.

## Exact remaining gates

1. Verify operating-company names and legal relationships for each facility.
2. Enter dated visits and facility addresses into the ledger.
3. Preserve exact advertisements, compensation schedules, consent versions, and staff statements.
4. Obtain participant records, laboratory records, deferral records, and payment history.
5. Identify machine model, software version, approved nomogram, target, actual collection, anticoagulant volume, and audit logs.
6. Map each alleged departure to the regulation effective on the event date.
7. Determine professional-negligence affidavit and expert requirements before activating Counts III or IV.
8. Calculate plaintiff-specific damages and restitution from admissible records.
9. Build and authenticate the exhibit index.

## Classification

Repository change only. No live graph ingestion or runtime state change is claimed. No runtime-generated ingestion receipt was created by these documentation commits.

# Plasma Case Repair Report

Date: 2026-08-04
Repository: Caeluviim/Caeluviim

## Actions completed

| Action | Path | Commit |
|---|---|---|
| Created corrected matter source record | `sources/matters/plasma/mat-plasma-2026-08-04-001.md` | `4601645d87f47000518b1e19ada7dc2eaa135c7a` |
| Created pleading, evidence, and filing-gate architecture | `docs/legal/compensated-plasma-extraction-case-repair.md` | `0f4ac45308b9659fa09726b9099313d2b2d6903e` |
| Created this action report | `reports/plasma-case-repair-2026-08-04.md` | recorded by the commit containing this file |

## Corrections applied

- Reframed the dispute around conduct, transactions, disclosures, procedures, reliance, injury, and remedies rather than a dispositive semantic classification.
- Preserved “commercial plasmapheresis medical practice,” “commercial blood-plasma procurement,” and “compensated plasma extraction” as canonical project terminology.
- Marked “statutory enforcement relator” as a project theory rather than an established caption status.
- Limited Minn. Stat. § 8.31, subd. 3a to an injured private plaintiff framework and added the public-benefit pleading requirement.
- Prevented federal Source Plasma regulations from being pleaded as an implied private cause of action.
- Converted machine-display observations into device and record questions requiring nomogram and log evidence.
- Separated periodic donor testing, per-collection screening, product testing, and center-specific protocols.
- Removed CPT codes as independent proof of unlawful classification or billing.
- Replaced speculative industry-value damages with plaintiff-specific damages categories and a separately labeled aggregate-remedy hypothesis.
- Added claim-by-claim filing gates, medical-malpractice screening, informed-consent causation requirements, and evidence-preservation targets.

## Consolidation status

The plasma matter is now represented in the repository as a source matter and legal architecture. It is not yet represented by a validated graph ingestion manifest because the repository’s current ingest schema requires fields and identifiers that must be generated consistently with the graph pipeline. Creating an ad hoc manifest would falsely report successful graph consolidation.

## Pending graph work

- assign canonical node identifiers for matter, claims, observations, evidence requests, legal authorities, defects, corrections, and remedies;
- generate an ingest manifest conforming to `schemas/ingest-manifest.schema.json`;
- validate the manifest;
- run the graph-ingestion workflow;
- record the runtime ingestion receipt and graph-index identifiers.

## Remaining evidentiary work

- exact dates and locations of plaintiff visits;
- exact advertisements and compensation representations;
- actual consent and educational materials by version;
- test names, dates, frequencies, and results;
- machine manufacturer, model, software, displayed field meaning, approved nomogram, target volume, actual plasma volume, and anticoagulant volume;
- facility entities and license holders;
- documented injury and causation evidence;
- current controlling Minnesota appellate authority for each selected state-law claim and remedy.
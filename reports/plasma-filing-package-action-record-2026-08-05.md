# Plasma Filing Package — Action Record

Date: 2026-08-05
Branch: `plasma/filing-package-2026-08-05`
Matter: `MAT-PLASMA-2026-08-04-001`

## Actions completed

1. Inspected the repository’s canonical plasma matter record, corrected draft architecture, predicate module, graph manifest, and repository write controls.
2. Verified current authoritative source anchors for Minn. Stat. §§ 8.31 and 325F.69 and 21 C.F.R. parts 630 and 640.
3. Created a dedicated branch from `main` rather than writing directly to the protected integration branch.
4. Added `corpus/legal/minnesota/plasma/pleading/working-complaint-v1.md`.
5. Consolidated the statutory-enforcement-relator theory, representative-group allegations, public-benefit allegations, regulated medical and commercial transaction model, six counts, prayer for relief, jury demand, and filing-control schedules into one pleading artifact.
6. Preserved the proposed Minnesota Structural Relief Pool of not less than $3.6 billion while expressly conditioning it on legal authority, admissible proof, proportionality, causation, and administrability.
7. Added an explicit Minn. Stat. § 145.682 expert-review compliance checkpoint for any medical-malpractice claim subject to that statute.
8. Prevented unsupported conversion of allegations into adjudicated facts by labeling record-specific fields and requiring exact entity, date, quotation, injury, and exhibit support before filing.
9. Re-audited pull request #58, confirmed it remains open and mergeable, and verified its changed-file set before making additional edits.
10. Added `corpus/legal/minnesota/plasma/pleading/filing-readiness-matrix.md` with 22 controlled filing components, standardized statuses, evidentiary dependencies, required next actions, and filing consequences.
11. Added stable evidence-ID conventions for events, entities, representations, omissions, medical records, payment records, expenses, regulations, exhibits, and authorities.
12. Defined a minimum filing gate and placed unsupported medical-negligence, informed-consent, structural-relief, and Rule 11 certification matters on explicit hold rather than inferring completion.
13. Updated this action record in the same branch so the repository contains an auditable account of the additional work.
14. Re-audited PR #58 at head `ad5ff1dfc939f3ebce5c9705f6d1bf14a26ac94e`, confirmed it was open and mergeable, and verified the three existing changed files before further writes.
15. Added `corpus/legal/minnesota/plasma/pleading/evidence-and-event-ledger.md` in commit `7dbccb398e487a167cb2ef396878879deb6dd162`.
16. The evidence ledger now supplies controlled tables for event chronology, entity and facility identity, representations and omissions, medical and laboratory records, procedure and device data, payments, expenses, exhibits, authentication, contradictions, and complaint-paragraph mapping.
17. Added `corpus/legal/minnesota/plasma/pleading/authority-and-elements-matrix.md` in commit `03281de8409d49d7dc099fdc1957fa8b612419fd`.
18. The authority matrix now separates authority registration, event-date version control, claim elements, factual support, likely defenses, remedy authority, and explicit limits on using federal regulations as standards rather than implied private causes of action.
19. Added `corpus/legal/minnesota/plasma/pleading/preservation-and-discovery-targets.md` in commit `29fe53e6e5b1f8d4d013f9d5b5d67a38b96db7d0`.
20. The preservation plan now identifies participant, laboratory, device, payment, communication, policy, personnel, quality, corporate-control, retention, metadata, chain-of-custody, and discovery-sequencing controls without asserting that any unverified record exists.
21. Added `corpus/legal/minnesota/plasma/pleading/filing-packet-and-rule11-checklist.md` in commit `887fc9a2621e45dee865d6e0e3fd3397a5c91670`.
22. The filing checklist now controls caption, party identity, venue, pleading support, limitations, injury, public benefit, expert review, structural relief, summons, cover sheets, fees or waiver, exhibits, service, e-filing, redaction, deadline calendaring, and final certification.
23. Preserved the rule that no blocked or held field may be completed by inference, and that unsupported claims or remedies must be withheld or removed from a filing candidate.
24. Updated this action record after all four repository additions to preserve commit-level traceability.

## Filing-critical facts still requiring completion

The repository does not presently contain enough verified information to truthfully complete these fields:

- Plaintiff’s legal filing name and service contact information.
- Exact defendant legal entities, registered agents, facility operators, and facility addresses.
- Event dates or bounded participation periods for each facility.
- Exact advertisement, application, consent-form, signage, and staff language.
- Complete donor file, laboratory history, deferral notices, payment records, machine logs, and adverse-event records.
- A medical expert’s review and the procedural determination required by Minn. Stat. § 145.682.
- A defensible damages computation and evidentiary model for the proposed structural-relief amount.
- Final venue facts, summons forms, filing fee or fee-waiver documents, and service plan.

## Legal-control determinations

- Federal plasma regulations are used as standards, notice, duty, materiality, and falsity evidence, not as an implied federal private cause of action.
- The representative group supplies public-benefit and remedial scope; the draft does not purport to prosecute unnamed persons’ individual damages claims.
- The structural pool is not pleaded as Plaintiff’s personal compensatory damages.
- Medical negligence and informed-consent theories remain subject to expert, causation, and procedural review.
- Bracketed or scheduled facts must not be removed by guessing. They must be completed from records, declarations, or verified sources.
- The readiness matrix is the operative filing-control index; any component marked `BLOCKED` or `HOLD` prevents characterization of the package as file-ready.
- Operational templates are not evidence. A blank or partially populated schedule does not satisfy a filing gate until each material field is sourced, verified, and linked.

## Next executable repository actions

1. Populate the entity and facility register from verified Minnesota corporate, registered-agent, facility, and federal establishment records.
2. Populate the event chronology from participant-controlled records and a reviewed declaration.
3. Transcribe exact advertisement, application, consent, signage, and staff language into the representation-and-omission schedule.
4. Index and authenticate the donor file, laboratory history, procedure records, payment records, expenses, communications, and preserved source materials.
5. Complete the event-date authority register, claim-element matrix, adverse-authority review, limitations audit, and remedy-control matrix.
6. Complete the § 145.682 and informed-consent review before retaining medical claims in a filed pleading.
7. Prepare a separate damages and structural-remedy methodology supported by admissible data and legal authority.
8. Resolve caption, venue, forms, fee or waiver, service, e-filing, redaction, and deadline-calendar requirements.
9. Run final contradiction, attribution, jurisdiction, limitations, venue, service, remedy, privacy, and certification audits against the exact filing copy.

## Result

The repository now contains a consolidated working complaint, a 22-component filing-readiness control matrix, an operational evidence and event ledger, an authority and claim-element matrix, a preservation and discovery target plan, a filing-packet and certification checklist, stable evidence-ID conventions, and a commit-traceable action record. The package is materially advanced but is not truthfully file-ready until the blocked factual and procedural fields are completed and every hold is resolved.
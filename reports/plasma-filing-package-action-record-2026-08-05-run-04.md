# Plasma Filing Package — Action Record — Run 04

Date: 2026-08-05
Branch: `plasma/filing-package-2026-08-05`
Matter: `MAT-PLASMA-2026-08-04-001`
Pull request: `#58`

## Repository audit performed

1. Fetched pull request #58 and verified that it remained open, non-draft, and mergeable before writing.
2. Verified the branch head before this run as `458203faf63ff30fa3c280d37fb60117646af72a`.
3. Enumerated the seven changed files already present in the pull request.
4. Reviewed the existing action record and confirmed that limitations analysis and Rule 11 certification were identified as incomplete filing gates.
5. Determined that the existing checklist referenced those gates but did not provide dedicated event-level and sentence-level operational control tables.

## Files added

### `corpus/legal/minnesota/plasma/pleading/limitations-and-accrual-audit.md`

Commit: `88e30a4362c4be71f83706945e3f04d893be57d1`

Added controls for:

- separate event-level limitations analysis;
- earliest adverse accrual and expiration calculations;
- alternative accrual theories;
- statutes of repose;
- tolling and suspension facts;
- event-date authority mapping;
- claim-level timeliness status;
- deadline calendaring and safety-margin dates;
- a prohibition on calculating deadlines from estimated or inferred event dates.

### `corpus/legal/minnesota/plasma/pleading/allegation-source-and-rule11-map.md`

Commit: `d1a30462733187654555617668d338527288be4b`

Added controls for:

- sentence-level mapping of the exact filing candidate;
- classification of facts, information-and-belief allegations, legal contentions, inferences, and remedy requests;
- evidence, authentication, authority, contradiction, and further-investigation links;
- information-and-belief particularity;
- natural-person, employer, facility, parent, and affiliate attribution;
- agency and control support;
- independent remedy support;
- final Rule 11 certification questions;
- mandatory withholding or narrowing of unsupported allegations.

### `reports/plasma-filing-package-action-record-2026-08-05-run-04.md`

This file records the audit, all writes, commit identifiers, controls introduced, and remaining blockers for this run.

## Legal and evidentiary control determinations

- A generic limitations checklist is insufficient because different events, defendants, claims, accrual theories, tolling facts, and repose rules may produce different deadlines.
- The earliest plausible adverse deadline must be preserved and calendared; a favorable accrual theory may not replace the adverse calculation.
- A paragraph-level evidence index is insufficient for final certification when a paragraph contains multiple factual or legal propositions. The exact filing candidate must be mapped at sentence level.
- Information-and-belief allegations require a recorded known basis and specifically identified further investigation; they may not function as placeholders for unsupported accusations.
- Branding, trade names, location signage, or corporate affiliation alone do not establish agency, employment, operational control, or parent liability.
- Each remedy requires authority, injury, causation, scope, methodology, and administrability support independent of the merits allegations.
- The proposed medical-monitoring and structural-relief remedies remain on hold.

## Remaining external dependencies

The following cannot be truthfully completed from the repository record alone:

- verified dates and bounded periods for each plasma event;
- exact defendant entities, facility operators, agents, and attribution facts;
- source records for each proposed factual sentence;
- exact representations, omissions, consent language, advertisements, and staff statements;
- medical, laboratory, procedure, machine, payment, expense, and communication records;
- event-date limitations and accrual authority;
- tolling facts and adverse deadline calculations;
- expert and procedural review under Minn. Stat. § 145.682 where applicable;
- admissible damages and structural-remedy methodology;
- final caption, venue, summons, fee or waiver, service, privacy, and filing-system data;
- final review of the exact paginated filing copy.

## Result

The branch now contains dedicated operational controls for the two filing gates that remained structurally under-specified: limitations/accrual and allegation-level Rule 11 support. These additions materially improve auditability and reduce the risk that estimated dates, unsupported attributions, paragraph-level overbreadth, or remedy assumptions are converted into certified filing assertions. The package remains a controlled working draft, not a file-ready pleading.
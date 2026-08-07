# Minnesota Commercial Plasmapheresis Action Ledger

Date: 2026-08-04
Controlling pull request: #37
Branch: `legal/minnesota-plasma-filing-20260803`
Base reviewed: `df76e837140b73d891d818cf14a93b1187e96878`

## Scope controls applied

- Litigation files contain no personal allocation or compensation arrangement.
- Litigation files contain no nonparty project or organization name.
- The requested structural relief amount is treated only as a proposed conservative minimum floor of USD 3.7 billion, not as a ceiling, present asset, adjudicated award, or personal allocation.
- A separate USD 1.2 billion figure is not part of the structural pool and is not included in the case package.
- Pure omissions are separated from affirmative statements. No standalone affirmative representation is imposed as an element where the pleaded mechanism is a pure omission supported by a recognized disclosure duty.
- Regulatory provisions lacking a private cause of action are treated as factual and legal predicates mapped to actionable counts rather than mislabeled as standalone damages counts.

## Actions completed in this run

1. Audited all open repository pull requests and identified PR #37 as the controlling Minnesota plasma branch.
2. Confirmed PR #37 remains open and mergeable and that its own merge boundary states the existing complaint is not final.
3. Reviewed the PR #37 changed-file inventory.
4. Reviewed the narrower complaint form on PR #36 to identify the competing pleading architecture and unresolved consolidation boundary.
5. Re-tested direct repository cloning. The execution environment again returned `Could not resolve host: github.com`; no false claim of a complete clone is made.
6. Generated and validated a complete pleading-sufficiency matrix outside the repository containing:
   - 198 data records plus headers;
   - 70 atomic fact rows;
   - 42 authorities;
   - 12 count or theory records;
   - 13 regulatory or non-actionable predicate records;
   - element, particularity, duty, materiality, knowledge, causation, injury, public-benefit, liability, relief, status, gap, and corrective-action fields.
7. Generated two spreadsheet renderings and a canonical CSV representation.
8. Recorded cryptographic hashes for later binary or text upload verification.
9. Added this action ledger to PR #37 so the repository itself records the work, limitations, corrections, and next gates.

## Generated artifact identities

| Artifact | SHA-256 |
|---|---|
| `Minnesota_Commercial_Plasmapheresis_Pleading_Sufficiency_Matrix.csv` | `3c88854eb999abf0c7fee99e7b22480c69964add0f453e65afe05c334278db9b` |
| `Minnesota_Commercial_Plasmapheresis_Pleading_Sufficiency_Matrix.xlsx` | `3a964115b113a0f9376e2b8b4e729151b2fed76d92d0ccea8ef14f2d610a3f` |
| `Minnesota_Commercial_Plasmapheresis_Pleading_Sufficiency_Matrix_Single_Sheet.xlsx` | `20e232bdf91da4016f9c3b74d940dafc8738b91ea2460de38f0fbb4bec39c190` |
| `Complaint_Commercial_Plasmapheresis_v22_Public_Repository_Clean.docx` | `39dfc7578e721548f1845e4c57b908aa471033ad56278a0fa295e507b99bbbc7` |
| `Complaint_Yurei_v_CSL_v21_Misclassification_Omission_Theory_Corrected.docx` | `8b948683385a0c7a539347c071208903cd14797d464b6904c2194d88d1396839` |

## Corrections applied

- Corrected the package status boundary: the filing package is not final while the standing insertion, complaint text, cross-references, and controlling remedy architecture remain split across branches or external artifacts.
- Preserved the distinction between the USD 3.7 billion structural-relief request and all excluded personal disposition material.
- Preserved omission pleading as omission pleading and removed any requirement that every omission depend on a separate affirmative representation.
- Preserved the distinction between plaintiff's own statutory claim, public-benefit allegations, prospective public-facing relief, and any mechanism that would be required for absent-person monetary claims.
- Preserved contrary scientific evidence and procedural barriers in the sufficiency matrix rather than presenting only supporting propositions.

## Current blockers

1. The complaint text, required standing insertion, filing directions, and pleading-sufficiency matrix are not yet consolidated into one authoritative branch-visible filing package.
2. The connected GitHub text-content action cannot transmit local XLSX or DOCX binary files.
3. The execution container cannot resolve `github.com`, preventing a complete clone and ordinary Git binary upload.
4. Exact transaction dates, complete consent versions, advertisements, payment histories, laboratory records, machine logs, corporate identities, and current registered-agent records remain required for fact-specific Rule 9.02 and service verification.
5. The USD 3.7 billion requested structural minimum does not yet have a complete Minnesota-specific quantum model traceable to admissible source data, authorized remedies, offsets, and nonduplication rules.
6. Group monetary relief remains procedurally distinct from individual statutory standing and public-facing equitable relief.

## Merge decision

Do not merge PR #37 or describe the complaint as filing-ready until all of the following are true:

- one authoritative complaint text is present on PR #37;
- the standing section is integrated into that complaint rather than existing only as an insertion memorandum;
- paragraph numbering and cross-references are regenerated and verified;
- the atomic-fact matrix and authority index are repository-visible or their exact hash-identified artifacts are uploaded through a binary-capable path;
- all factual and service gates are marked satisfied or deliberately excluded;
- generated DOCX and PDF versions are rendered and inspected after the final text change;
- hosted checks pass on the exact final head.

## Next actions

1. Consolidate PR #36 complaint content and PR #37 standing architecture onto PR #37 only.
2. Add the hash-identified canonical CSV through the GitHub contents API or a binary-capable Git path.
3. Upload the two XLSX files and final DOCX/PDF artifacts through a binary-capable path and verify their hashes.
4. Close superseded complaint PRs only after consolidation and changed-file verification.
5. Run hosted validation on the exact consolidated head.

## Highest-priority action

Create one authoritative complaint on PR #37 with the standing section integrated into the pleading text, then regenerate and inspect every derivative filing artifact from that exact source.
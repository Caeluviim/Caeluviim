# Minnesota Plasma Filing — Readiness Matrix

Matter: `MAT-PLASMA-2026-08-04-001`
Status date: 2026-08-05
Controlling draft: `working-complaint-v1.md`

## Status vocabulary

- `COMPLETE`: repository contains a usable, identified artifact.
- `PARTIAL`: structure exists, but record-specific completion remains.
- `BLOCKED`: cannot be completed truthfully from repository evidence presently available.
- `HOLD`: do not include in a filed pleading until the stated control is satisfied.

## Filing package controls

| ID | Component | Status | Existing repository artifact | Missing proof or decision | Required next action | Filing consequence |
|---|---|---:|---|---|---|---|
| FR-001 | Consolidated complaint architecture | COMPLETE | `working-complaint-v1.md` | None for architecture | Maintain controlled edits | Usable as working pleading |
| FR-002 | Plaintiff caption and contact block | BLOCKED | Bracketed fields in complaint | Legal filing name, mailing/service address, email, telephone or alternate contact | Populate only from verified filing information | Complaint cannot be filed with placeholders |
| FR-003 | Defendant identities | BLOCKED | Generic defendant pleading rule | Exact legal entities, assumed names, facility operators, parent/affiliate roles, registered agents | Create defendant identity schedule from verified corporate and regulatory records | Caption, service, venue, and attribution remain defective |
| FR-004 | Facility and venue facts | PARTIAL | Hennepin County venue theory | Exact facilities, transactions, operators, and county nexus | Map each event to facility, operator, address, and county | Venue allegation remains conditional |
| FR-005 | Event chronology | BLOCKED | General participation allegations | Dates or bounded periods, center, procedure, statement, payment, test, deferral, injury, source | Create one row per event from records and declaration | Particularity, limitations, causation, and attribution cannot be audited |
| FR-006 | Representation-and-omission schedule | BLOCKED | Categories pleaded in Counts I–II | Exact language, medium, date, speaker/publisher, responsible entity, exposure, materiality, injury | Transcribe exact statements and identify omissions with source IDs | Consumer-fraud and advertising counts remain vulnerable |
| FR-007 | Medical and laboratory record set | BLOCKED | Low-protein deferral allegation | Donor files, test results, deferral notices, adverse-event records, machine logs, collection records | Obtain, index, authenticate, and map records to allegations | Injury and causation allegations remain unverified |
| FR-008 | Payment and expense proof | BLOCKED | General compensation and transportation allegations | Payment history, incentive terms, receipts, transit costs, time records | Build economic-loss schedule with source IDs | Economic injury cannot be quantified reliably |
| FR-009 | Federal-regulatory mapping | PARTIAL | 21 C.F.R. parts 606, 630, 640 anchors | Event-date-specific subsection, effective text, guidance/device instruction, factual predicate | Build authority-to-event matrix | Regulations may be cited only as supported standards, not a private cause of action |
| FR-010 | Minnesota statutory mapping | PARTIAL | Minn. Stat. §§ 8.31, 325F.67, 325F.68–.70 | Event-date effective text, claim elements, particularity, causation, public-benefit support | Build element-by-element authority table | Statutory counts remain structurally pleaded but not fact-complete |
| FR-011 | Public-benefit proof | PARTIAL | Representative-group and standardized-practice allegations | Common materials, continuing conduct, statewide reach, prospective effect | Link standardized practices to common documents and facilities | Section 8.31 private-AG theory remains contestable |
| FR-012 | Medical-negligence claim | HOLD | Count III and § 145.682 checkpoint | Expert-review determination, applicable affidavit analysis, breach, causation, damages | Complete privileged expert/procedural review before filing | Remove or withhold claim unless statutory requirements are satisfied |
| FR-013 | Informed-consent claim | HOLD | Count IV | Applicable duty, material risks, disclosure record, causation, expert needs | Complete legal and expert review; map disclosures and alternatives | Do not file as fact-complete without support |
| FR-014 | Unjust-enrichment theory | PARTIAL | Alternative Count V | Benefit conferred, inequity, remedy compatibility, adequate-remedy analysis | Map transactions and evaluate duplication/preemption limits | Must remain expressly alternative and legally controlled |
| FR-015 | Injunctive and declaratory relief | PARTIAL | Count VI and prayer | Ongoing conduct, standing for prospective relief, redressability, requested terms | Draft remedy-by-violation matrix | Overbroad or unsupported injunction risk |
| FR-016 | Structural Relief Pool methodology | HOLD | Conditional $3.6 billion request | Minnesota transaction volume, participant count, duration, downstream value, remedial cost, legal authority, proportionality, administrability | Prepare separate methodology memorandum with admissible sources and calculations | Do not present amount as proven damages or fixed entitlement |
| FR-017 | Exhibit index and authentication map | BLOCKED | Required-schedules list | Actual exhibits, custodians, source, date, authentication method, allegation links | Create exhibit register and assign stable IDs | Factual allegations lack record traceability |
| FR-018 | Preservation package | PARTIAL | Discovery targets identified conceptually | Named recipients, entities, facilities, date ranges, systems, categories | Draft controlled preservation letter and target schedule | Spoliation-preservation step remains incomplete |
| FR-019 | Limitations and accrual audit | BLOCKED | No event dates | Dates, discovery, continuing conduct, tolling facts, claim-specific periods | Run claim-by-claim limitations table after chronology exists | Filing deadline cannot be responsibly determined |
| FR-020 | Summons, civil cover sheet, fee/waiver, service plan | BLOCKED | Checklist reference only | Final parties, addresses, registered agents, filing status, fee information | Prepare court forms after caption and venue are fixed | Filing packet remains procedurally incomplete |
| FR-021 | Contradiction and attribution audit | PARTIAL | Filing-control notice | Completed schedules and evidence links | Run final paragraph-level audit against sources | Draft cannot be certified as internally verified |
| FR-022 | Rule 11 / certification review | HOLD | Explicit anti-guessing controls | Final evidence-supported pleading, legal basis, inquiry record | Complete immediately before filing | No filing should occur before certification review |

## Evidence-ID convention

Every factual row added to a schedule should use a stable identifier:

- `EVT-####` — participation or communication event
- `ENT-####` — legal entity or facility
- `REP-####` — representation or advertisement
- `OMI-####` — alleged omission
- `MED-####` — medical or laboratory record
- `PAY-####` — payment or incentive record
- `EXP-####` — expense or time-loss record
- `REG-####` — regulation, guidance, standard, or device instruction
- `EXH-####` — filed or proposed exhibit
- `AUTH-####` — legal authority

Each complaint allegation should ultimately map to at least one evidence ID or be expressly labeled as information-and-belief with the factual basis identified.

## Current filing gate

The package is not file-ready. The minimum gate to advance from working draft to filing candidate is completion of FR-002 through FR-010, FR-017, FR-019, and FR-020, plus resolution of each `HOLD` item. No placeholder should be replaced by inference or assumption.
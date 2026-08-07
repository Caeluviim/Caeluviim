# Party Identity, Capacity, Venue, and Service Audit

Status: operational filing control; not evidence and not a certification of filing readiness.

## Purpose

This audit prevents a complaint from being commenced against an imprecisely named entity, served through an unverified channel, or placed in a county unsupported by defendant-specific facts. It also separates four questions that must not be collapsed:

1. Who is the legally cognizable defendant?
2. What conduct is attributable to that defendant?
3. Why is the selected county a proper place of trial?
4. How will the action be commenced against each defendant under Minnesota law?

No trade name, facility sign, website label, payment-card descriptor, or colloquial provider name is sufficient by itself.

## Controlling procedural propositions

- Under Minn. R. Civ. P. 3.01, commencement is defendant-specific. An action is commenced against a defendant by service, signed waiver, or qualifying delivery to the sheriff followed by actual service within 60 days.
- Minn. R. Civ. P. 4.01 requires the summons to identify the court and parties, be subscribed, provide a United States service address for the subscriber, state the answer period, and warn of default.
- Minn. R. Civ. P. 4.03 controls personal service and must be matched to the defendant's legal form.
- Minn. R. Civ. P. 5.04 separately controls filing after commencement; commencement and filing are not interchangeable events.
- Minnesota Statutes chapter 542 governs venue. A county must be supported by the operative venue provision and defendant-specific or event-specific facts, not merely convenience or preference.
- Minnesota Judicial Branch eFiling guidance requires separate filing codes and appropriate public, confidential, or sealed designations. Sensitive exhibits must not be bundled into a public complaint without a document-level security determination.

Primary sources checked for this control:

- https://www.revisor.mn.gov/court_rules/rule/cp-3/
- https://www.revisor.mn.gov/court_rules/cp/id/4/
- https://www.revisor.mn.gov/statutes/cite/542
- https://www.mncourts.gov/eFile
- https://www.mncourts.gov/GetForms.aspx?c=7&p=137

## A. Defendant identity register

Create one row for every proposed defendant. Do not combine parent, subsidiary, assumed name, facility, operator, landlord, staffing company, laboratory, payment vendor, or medical director unless the evidence establishes the relationship.

| Field | Required entry | Gate |
|---|---|---|
| PARTY-ID | Stable identifier, e.g. DEF-001 | Required |
| Exact legal name | Name from authoritative record | Required |
| Entity type | Corporation, LLC, partnership, individual, other | Required |
| Jurisdiction of formation | State or country | Required |
| Minnesota file number | Secretary of State record identifier, if applicable | Required when registered |
| Active status and date checked | Exact status and verification date | Required |
| Registered office | Exact address from current record | Required if applicable |
| Registered agent | Exact current agent name | Required if applicable |
| Principal office | Verified address | Required |
| Facility or assumed name | Trade name connected to legal entity | Required if used in pleading |
| Ownership source | Filing, license, contract, website terms, or other record | Required |
| Operator source | Evidence identifying actual facility operator | Required |
| Conduct attributed | Specific acts, omissions, representations, policies | Required |
| Actor linkage | Employee, agent, contractor, policy, record, or ratification basis | Required |
| Service method | Rule-specific proposed method | Required |
| Service address/person | Verified recipient and location | Required |
| Venue nexus | County-specific fact and source | Required |
| Limitations sensitivity | Earliest possible deadline affected by naming/service | Required |
| Verification source IDs | Evidence ledger references | Required |
| Status | VERIFIED, PARTIAL, CONFLICT, HOLD | Required |

### Identity evidence hierarchy

Use the strongest available source and preserve the lookup result:

1. Minnesota Secretary of State entity record and assumed-name record.
2. Foreign-state formation record where the entity is not formed in Minnesota.
3. FDA establishment registration, inspection, license, or enforcement record tied to the facility address.
4. Facility license, accreditation, laboratory record, property record, or lease-related public record.
5. Terms of use, privacy policy, consent document, payment record, tax form, or participant agreement naming the counterparty.
6. Corporate website statements only when archived with URL, access date, and page capture.
7. Secondary reporting only as a lead, not final identity proof.

### Mandatory conflict rule

If two sources identify different operators or legal entities for the same facility, mark `CONFLICT`. Do not choose one by inference. The complaint may plead an uncertainty only when there is a good-faith factual basis and the allegation is drafted to disclose the uncertainty rather than conceal it.

## B. Capacity and attribution matrix

For each count, map each defendant to the legal and factual basis for liability.

| CLAIM-ID | PARTY-ID | Direct conduct | Policy/control | Agency basis | Knowledge basis | Benefit received | Causation link | Source IDs | Status |
|---|---|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | HOLD |

### Attribution rules

- A parent company is not interchangeable with a subsidiary.
- A brand owner is not automatically the facility operator.
- A laboratory is not automatically responsible for collection-center representations.
- A medical director's signature does not by itself establish involvement in every operational decision.
- Collective references such as “Defendants” may be used only after defendant-specific conduct is pleaded or when the allegation expressly concerns a jointly adopted policy supported by evidence.
- Respondeat superior, agency, apparent authority, ratification, concerted action, and direct corporate liability must remain analytically distinct.
- The receipt of economic benefit does not alone establish authorship, knowledge, control, or causation.

## C. Venue audit

### County-level venue register

| VENUE-ID | Proposed county | Statutory/rule basis | Defendant residence/presence fact | Cause-arose fact | Facility/event address | Source IDs | Anticipated challenge | Status |
|---|---|---|---|---|---|---|---|---|
| VEN-001 | Hennepin County or other verified county | Minn. Stat. ch. 542 provision to be fixed after party/event verification | TBD | TBD | TBD | TBD | Improper venue/change of venue | HOLD |

### Venue gate

The caption must not identify a county until all of the following are complete:

- At least one operative venue provision is identified by exact citation.
- The selected provision is applicable to the pleaded causes of action and defendant types.
- At least one admissible or reasonably discoverable fact supports the selected county.
- The event address and county are independently verified.
- Every material contrary venue fact is logged.
- The possibility of a demand or motion to change venue is assessed.
- The venue allegation is defendant-specific where the statute requires it.

### Prohibited venue shortcuts

Do not plead venue solely because:

- the plaintiff is currently located in the county;
- the county contains a district court;
- a parent company conducts business statewide;
- an internet advertisement was viewable there;
- statewide public benefit is alleged;
- another related matter is associated with the county.

## D. Service and commencement plan

Create a separate service packet and commencement clock for each defendant.

| SERVICE-ID | PARTY-ID | Method | Rule subsection | Recipient | Address | Server | Delivery date | Actual service/waiver date | 60-day sheriff deadline | Proof filed | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SRV-001 | DEF-001 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | HOLD |

### Service packet components

- Civil summons conforming to Rule 4.01.
- Complaint with identical caption and party names.
- Any required civil cover sheet or filing document.
- Waiver materials if Rule 4.05 is used.
- Instructions to the process server or sheriff that identify the exact legal entity and authorized recipient.
- Current entity record supporting the selected recipient and address.
- Affidavit or return of service preserving date, time, place, manner, documents served, recipient identity, and server identity.
- Defendant-specific commencement date entered in the limitations calendar.

### Commencement controls

1. Calculate limitations against actual commencement rules, not the later court-filing date.
2. If using sheriff delivery, record the delivery method and preserve proof of delivery.
3. Calendar the 60-day actual-service deadline immediately.
4. Do not assume service on one affiliated entity commences the case against another.
5. Reconcile the caption, summons, complaint, process-server instructions, affidavit, and entity record before service.
6. Treat a refused, redirected, or ambiguous delivery as unresolved until legally sufficient service is established.
7. Record the one-year Rule 5.04 filing deadline from the earliest commencement event and separately track each later-added defendant.

## E. Misnomer, amendment, and relation-back risk

A naming error can become dispositive when corrected after a limitations deadline. Before commencement:

- compare the exact legal name across Secretary of State records, contracts, consent forms, payment records, FDA records, and facility materials;
- distinguish a correct entity named inaccurately from the wrong entity entirely;
- identify whether the proposed defendant had notice and whether an amendment would change the party;
- do not rely prospectively on relation back as a substitute for pre-service verification;
- preserve every source showing common branding, shared address, shared agent, notice, control, or identity confusion without treating those facts as conclusive.

Any post-deadline amendment requires a dedicated Rule 15 and limitations memorandum before filing.

## F. Privacy and public-access control

Before eFiling or paper filing, classify every document independently:

| DOC-ID | Document | Public/non-public basis | Redaction required | Separate filing code | Coversheet required | Status |
|---|---|---|---|---|---|---|
| TBD | Complaint | Presumptively public; review line by line | TBD | Complaint code | TBD | HOLD |
| TBD | Medical records | Non-public treatment required unless authority supports otherwise | Yes | Separate code | Likely | HOLD |
| TBD | Laboratory records | Review as medical/non-public material | Yes | Separate code | Likely | HOLD |
| TBD | Payment records | Redact account and identifying data | Yes | Separate code | TBD | HOLD |

Do not place full birth dates, financial account numbers, medical identifiers, participant numbers, precise shelter locations, or other protected information into a public complaint when a narrower allegation is sufficient.

## G. Filing-release gate

Party, venue, and service architecture is `RELEASED` only when:

- every named defendant has a verified legal identity;
- every trade name is connected to a legal entity by source;
- every count has defendant-specific attribution;
- the selected county has an exact legal and factual basis;
- summons and complaint captions match exactly;
- a Rule 4 service method and verified recipient exist for every defendant;
- commencement and filing deadlines are calculated;
- privacy classification is complete for every filing component;
- a paragraph-level Rule 11 source map contains no unresolved defendant identity or attribution conflicts.

Until then, the correct status is `HOLD — PARTY/VENUE/SERVICE VERIFICATION INCOMPLETE`.

## Immediate evidence queue

1. Obtain current Minnesota Secretary of State records for every candidate defendant and assumed name.
2. Obtain formation-state records for each foreign entity.
3. Match every facility address to its actual operator using FDA and corporate records.
4. Preserve participant agreements, consent forms, privacy notices, payment records, and correspondence identifying the contracting entity.
5. Verify the county of each material event and facility.
6. Identify a legally sufficient service recipient and address for each entity.
7. Add all results to the evidence ledger using stable source IDs.
8. Re-run limitations analysis using defendant-specific commencement dates.
9. Replace collective pleading language with defendant-specific allegations before release.
10. Prepare separate public/non-public filing classifications and redacted copies.

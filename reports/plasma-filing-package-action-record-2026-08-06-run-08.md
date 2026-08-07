# Plasma Filing Package Action Record — Run 08

Date: 2026-08-06
Repository: `Caeluviim/Caeluviim`
Branch: `plasma/filing-package-2026-08-05`
Pull request: #58

## Objective

Advance the Minnesota compensated-plasma filing package by eliminating unresolved ambiguity in defendant identity, legal capacity, venue, service, commencement, and filing privacy. Record every repository action and every substantive control decision.

## Repository actions

1. Read PR #58 metadata and confirmed it was open and mergeable before this run.
2. Read the complete changed-file index to avoid duplicating existing audits.
3. Reviewed current official Minnesota procedural sources governing commencement, summons, service, venue, civil filing forms, eFiling, and document security classification.
4. Created `corpus/legal/minnesota/plasma/pleading/party-identity-capacity-venue-and-service-audit.md`.
5. Recorded the resulting commit: `61e69cff21f08957fedd7e6dc8b22050f1f82f28`.
6. Created this action record.
7. Updated the PR description to index the new control architecture and preserve the filing-readiness disclaimer.
8. Re-read PR metadata after the writes to verify branch head, mergeability, commit count, changed-file count, and additions.

## Official sources reviewed

- Minnesota Rules of Civil Procedure, Rule 3: https://www.revisor.mn.gov/court_rules/rule/cp-3/
- Minnesota Rules of Civil Procedure, Rule 4: https://www.revisor.mn.gov/court_rules/cp/id/4/
- Minnesota Statutes chapter 542: https://www.revisor.mn.gov/statutes/cite/542
- Minnesota Judicial Branch eFile and eServe guidance: https://www.mncourts.gov/eFile
- Minnesota Judicial Branch civil starting forms: https://www.mncourts.gov/GetForms.aspx?c=7&p=137

## Substantive determinations

### 1. Defendant identity is a release gate

A trade name, facility sign, website brand, or payment descriptor cannot substitute for a verified legal entity. Every proposed defendant now requires an authoritative identity record, entity type, formation jurisdiction, status, registered agent or equivalent recipient, principal office, facility/operator linkage, and evidence references.

### 2. Affiliated entities cannot be pleaded collectively by default

Parent, subsidiary, brand owner, facility operator, laboratory, staffing company, payment vendor, landlord, and medical director must be kept separate unless evidence supports a specific relationship. The audit prohibits collective “Defendants” allegations from concealing missing attribution.

### 3. Capacity and attribution must be claim-specific

Each count must identify each defendant's direct conduct, control or policy role, agency basis, knowledge basis, benefit, causation link, and source. Economic benefit alone does not prove control, knowledge, authorship, agency, or causation.

### 4. Venue cannot rest on preference or statewide framing

The selected county must be supported by an exact venue provision and verified defendant- or event-specific facts. Plaintiff location, statewide business, internet availability, public-benefit allegations, or connection to another matter are not sufficient shortcuts.

### 5. Commencement is defendant-specific

The action's commencement date must be recorded separately for each defendant under Minn. R. Civ. P. 3.01. Service on one affiliate does not commence an action against another. Sheriff-delivery commencement requires proof of delivery and actual service within 60 days.

### 6. Summons, complaint, service instructions, and proof must reconcile

The exact legal name must match across the caption, summons, complaint, process-server instructions, entity record, and affidavit or return of service. Any mismatch is a hold requiring correction before service.

### 7. Relation back is not a substitute for pre-service identity verification

The package now distinguishes a misnamed correct entity from substitution of an entirely different entity. It prohibits planned reliance on amendment or relation back to cure avoidable pre-service uncertainty.

### 8. Public and non-public materials require document-level control

Medical, laboratory, payment, and identifying records must be separately classified, redacted, and filed using appropriate security designations. They must not be bundled into a public complaint without legal and filing-code review.

## New operational controls

The new audit adds:

- a defendant identity register;
- an identity-source hierarchy;
- a mandatory conflict rule;
- a capacity and attribution matrix;
- a county-level venue register;
- a venue release gate;
- a defendant-specific service and commencement register;
- a service-packet checklist;
- commencement and 60-day sheriff-delivery controls;
- misnomer, amendment, and relation-back controls;
- public-access and privacy classification controls;
- a ten-item immediate evidence queue;
- a consolidated filing-release gate.

## Filing status after this run

The pleading package remains `HOLD — PARTY/VENUE/SERVICE VERIFICATION INCOMPLETE`.

The following non-fabricable inputs remain unresolved:

- exact legal names and formation records for each intended defendant;
- current status and registered-agent records;
- verified facility ownership and operator identity;
- defendant-specific conduct and actor attribution;
- exact county and address for each material event;
- exact statutory basis for the selected venue;
- verified recipient and service address for every defendant;
- limitations calculations keyed to actual defendant-specific commencement dates;
- public/non-public classification and redacted copies for each filing component;
- final paragraph-level Rule 11 certification.

No unresolved field was completed by inference. No trade name was converted into a legal defendant without evidence. No venue, service recipient, commencement date, or privacy designation was fabricated.

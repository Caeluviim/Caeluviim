# Structural Insolvency and Collective Resolution Plane

**Module identifier:** `urn:caeluviim:module:sicrp`  
**Version:** `0.1.0`  
**Status:** Proposed — implemented, not ratified  
**Scope:** Formal architecture and validation contracts. Implementation does
not establish that any real institution is insolvent, that any asserted right
is legally effective, or that any recorded condition has been resolved.

## 1. Purpose

The Structural Insolvency and Collective Resolution Plane (SICRP) represents
how a system can repeatedly fail to discharge binding obligations to affected
constituencies because its operative mechanisms constrain, redirect, extract,
delay, or withhold resource flows.

The plane also represents a materially stronger resolution path:

```text
StructuralInsolvencyCondition
  -> ProducingMechanism
  -> AffectedConstituency
  -> MaterialDeficit
  -> InstitutionalObligation or InterventionRight
  -> Intervention
  -> ResolutionEvidence
```

SICRP does not equate expenditure, announced reform, completed activity, or
aggregate improvement with resolution. A resolution claim must be supported
by constituency-level measurements against declared obligations and must pass
mechanism-neutralization, rights, coverage, and non-regression checks.

## 2. Relationship to EMGN

SICRP is a domain-specific realization of the Error-Mediated Generative
Non-Closure (EMGN) architecture.

| EMGN primitive | SICRP realization |
| --- | --- |
| `DiscrepancyEvent` | An observed institutional failure, measured material deficit, or conflict between an operative rule and a declared obligation |
| `ErrorResidue` | A retained structural error residue: condition, debt, exclusion, institutional constraint, or contested rule |
| `RemediationEvent` | A rights-grounded collective intervention |
| `TransitionRegime` | The allocation regime and producing-mechanism configuration before or after intervention |
| `ReachabilitySnapshot` | A resolution observation describing reachable material conditions |
| `NovelFutureWitness` | Independently assessed evidence of new reachable material conditions, when a separate EMGN novelty claim is made |

Every SICRP record contains an `emgn_trace` linking the domain record to
addressable EMGN discrepancies, residue, and before/after transition regimes.
That trace does not automatically validate an EMGN novelty claim. Conversely,
an EMGN novelty witness does not establish that deprivation was resolved.

## 3. Critical distinctions

### 3.1 Hardship is not yet a mechanism finding

A hardship observation describes a condition. A mechanism finding identifies
an operative rule, process, gate, transfer, delay, or control relation and
traces its effect through resource flows to an affected constituency.

### 3.2 Scarcity is not automatically structural insolvency

Structural insolvency is not merely a low aggregate resource total. A
supported claim requires:

1. a declared obligation or threshold;
2. an affected constituency;
3. a measured shortfall;
4. one or more operative mechanisms;
5. one or more traced resource flows; and
6. capacity evidence showing the relevant system configuration or resource
   holder could materially affect discharge of the obligation.

The capacity evidence may still show a genuine aggregate constraint. The
module records that evidence; it does not predetermine the conclusion.

### 3.3 Aggregate sufficiency is not distributional discharge

An aggregate balance can coexist with constituency-level deprivation. Every
obligation result and resolution measurement is therefore scoped to an
identified affected constituency.

### 3.4 A right is not its exercise

An intervention right records a holder, duty bearers, authority basis,
targeted mechanisms, exercisable actions, and a contest path. A remediation
activity must separately identify which rights were exercised.

### 3.5 Resource input is not resolution

Funding or resource delivery may be relevant evidence, but a validated
resolution requires all of:

- obligation thresholds satisfied;
- targeted mechanisms neutralized or transformed;
- intervention rights remaining exercisable;
- complete affected-constituency coverage;
- non-regression checks passed; and
- independent measurement completed.

### 3.6 Activity completion is not outcome validation

A remediation may be marked completed without being marked verified. A
resolution state is separately produced by an independent assessor.

### 3.7 Implementation is not ratification

This module is implemented as a proposal. Neither the repository author, the
record proposer, nor the implementation itself may validate or ratify its own
claim. Ratification requires two distinct validators who are not the proposer.

## 4. Primitive entities

| Entity | Formal role |
| --- | --- |
| `StructuralInsolvencyCondition` | A governed condition record linking mechanisms, constituencies, deficits, obligations, flows, exclusions, and capacity evidence |
| `ProducingMechanism` | An operative process that constrains, extracts, redirects, delays, excludes, captures, or withholds |
| `AffectedConstituency` | A defined group whose members bear the measured shortfall and whose representation method is recorded |
| `MaterialDeficit` | A measured constituency-specific shortfall in a typed resource, service, access condition, or right |
| `InstitutionalObligation` | A threshold-bearing duty or entitlement with an authority basis and duty bearer |
| `ResourceFlow` | A time-bounded transfer, withholding, extraction, allocation, or delivery of a typed resource |
| `ExclusionEvent` | A reified denial, delay, gate, displacement, or exclusion linking a mechanism to a constituency and deficit |
| `CapacityEvidence` | Evidence about resources or operational capacity relevant to discharging an obligation |
| `InterventionRight` | A holder-specific, authority-grounded power to inspect, participate, contest, redirect, recover, suspend, or compel |
| `Intervention` | A rights-grounded activity directed at mechanisms, exclusions, obligations, or resource flows |
| `CollectiveResolutionPlan` | A constituency-scoped plan linking interventions, responsible actors, target mechanisms, metrics, and decision rules |
| `ResolutionMetric` | A typed threshold or distributional measure used to evaluate collective resolution |
| `ResolutionObservation` | A time-bounded observation of a resolution metric for a defined population scope |
| `ResidualInsolvency` | Disclosed unmet obligations, active mechanisms, uncovered subpopulations, or unresolved deficits after intervention |
| `DistributionalEffect` | A measured effect across the affected population, including initiating and non-initiating members or subgroups |
| `ValidatorAssessment` | An independent assessment of condition or resolution evidence |
| `CollectiveResolutionClaim` | A governed comparison asserting population-generalized resolution rather than individual improvement |
| `GovernanceRecord` | Proposal, validation, ratification, rejection, and validator-independence data |
| `ModuleStatusRecord` | Machine-readable status and artifact manifest for this module version |

All addressable relations that require evidence, governance, or revision are
represented as first-class resources.

## 5. Formal core

Let:

- `C` be the set of affected constituencies;
- `O` be the set of institutional obligations;
- `M` be the set of operative mechanisms;
- `F_t` be the resource-flow configuration during interval `t`;
- `q(o,c,t)` be the measured quantity delivered for obligation `o` and
  constituency `c`; and
- `theta(o,c,t)` be the required threshold in the same declared unit.

The shortfall is:

\[
d(o,c,t) = \max(0,\theta(o,c,t)-q(o,c,t)).
\]

A `StructuralInsolvencyCondition` is evidentially supported only when:

\[
\exists o\in O,\ c\in C,\ m\in M:
d(o,c,t)>0
\]

and the record supplies a trace:

\[
m \leadsto F_t \leadsto d(o,c,t)
\]

together with authority, capacity, and source evidence. This is a record
criterion, not an automatic causal theorem: validators remain responsible for
the adequacy of the supplied evidence.

Let `I` be a set of intervention rights and `R` a
`CollectiveResolutionPlan`. An intervention is rights-grounded only if:

\[
\forall r\in \operatorname{Interventions}(R),\ \exists i\in I:
\operatorname{exercises}(r,i).
\]

Let `Z_0` and `Z_1` be independently assessed sets of
`ResolutionObservation` values. Individual improvement is explicitly
insufficient:

\[
\operatorname{Improved}(\text{initiating claimant})
\not\Rightarrow
\operatorname{CollectivelyResolved}(c).
\]

A validated collective resolution requires:

\[
\forall (o,c)\text{ in scope},\
q_{Z_1}(o,c)\geq\theta_{Z_1}(o,c)
\]

plus:

\[
\operatorname{MechanismAltered}(Z_1)
\land
\operatorname{AffectedPopulationDefined}(c)
\land
\operatorname{ResourceOrRightRestored}(Z_1)
\land
\operatorname{DistributionalEffectMeasured}(Z_1)
\land
\operatorname{ResidualInsolvencyDisclosed}(Z_1)
\land
\operatorname{PopulationGeneralizationDemonstrated}(Z_1)
\land
\operatorname{RightsExercisable}(Z_1)
\land
\operatorname{CoverageComplete}(Z_1)
\land
\operatorname{NonRegression}(Z_0,Z_1)
\land
\operatorname{IndependentValidationRecorded}(Z_1).
\]

No single conjunct is a substitute for the conjunction.

## 6. Record lifecycle

1. Define affected constituencies and record their representation methods.
2. Declare obligations, thresholds, units, duty bearers, and authority bases.
3. Record time-bounded resource flows.
4. Identify alleged or evidenced producing mechanisms and link them to flows.
5. Measure constituency-specific material deficits.
6. Reify exclusion events that connect mechanisms to deficits.
7. Record capacity evidence relevant to discharge of each obligation.
8. Submit a structural-insolvency condition with the complete evidence trace.
9. Record intervention rights and their contest paths.
10. Adopt a collective resolution plan.
11. Record which rights are exercised by each intervention.
12. Define resolution metrics before evaluating outcomes.
13. Produce before and after resolution observations.
14. Record distributional effects across the affected constituency.
15. Disclose all residual insolvency.
16. Attach independent validator assessments.
17. Evaluate every collective-resolution criterion.
18. Ratify only after two distinct validators, neither the proposer.

## 7. Required validation invariants

A conforming SICRP record must satisfy:

- every producing mechanism has evidence, responsible actors, affected flows,
  affected deficits, and
  affected constituencies;
- every affected constituency has a definition, scope, representation method,
  representative, and evidence;
- every institutional obligation names a beneficiary constituency, duty bearer, authority
  basis, typed threshold, unit, and evaluation period;
- every resource flow is time-bounded, measured, sourced, and linked to an
  authority basis;
- every material deficit links an obligation and constituency to at least
  one mechanism and flow;
- `shortfall = max(0, required - observed)` in the declared unit;
- every exclusion event links a producing mechanism, affected constituency,
  material deficit, time, and evidence;
- every structural-insolvency condition links mechanisms, constituencies,
  obligations, deficits, flows, exclusions, and capacity evidence;
- every intervention right names a holder, duty bearers, authority basis,
  targeted mechanisms, exercisable actions, and contest path;
- every intervention exercises at least one recorded right;
- every collective resolution plan identifies target mechanisms, affected
  constituencies, interventions, metrics, responsible actors, and decision
  rules;
- every resolution observation is time-bounded and linked to a declared
  metric and population scope;
- every distributional effect includes initiating and non-initiating scopes;
- all residual insolvency is disclosed rather than erased from the record;
- individual improvement cannot satisfy a collective-resolution claim;
- validated collective resolution requires mechanism alteration, population
  definition, restoration, distributional measurement, residual disclosure,
  population generalization, rights exercisability, coverage,
  non-regression, and independent validation;
- validated collective resolution requires all referenced interventions to be
  verified;
- validated resolution and ratification require two distinct validators;
- the proposer is never a validator;
- a validator is neither the proposer nor an implementer of the intervention
  being assessed;
- provenance includes a content hash, timestamp, and source references; and
- the module status record cannot claim ratification without the required
  independent validators.

Reference-integrity, arithmetic, complete-coverage, independence, and
cross-record rules are checked by executable tests in addition to the JSON
Schema and SHACL contracts.

## 8. Resolution measurement

Every measurement layer contains:

- `ResolutionMetric` definitions with unit, threshold, comparison direction,
  population scope, and evidence;
- `ResolutionObservation` values with a closed window and observed population;
- `DistributionalEffect` records covering initiating and non-initiating
  scopes;
- `ResidualInsolvency` records for every remaining deficit, mechanism,
  exclusion, obligation, or uncovered subgroup; and
- `ValidatorAssessment` records with independent assessor identity,
  assessment scope, decision, evidence, and time.

These records are evidence for governance. They do not govern themselves.

## 9. Governance and status

Record governance states are:

- `proposed`
- `under_validation`
- `ratified`
- `rejected`

Claim states are:

- `proposed`
- `supported`
- `validated`
- `rejected`

`implemented` is an implementation status, not a governance status.

The normative module-status record is:

```text
governance/sicrp-v0.1.0.status.json
```

It records `implementation_status = implemented`,
`governance_status = proposed`, `ratification_claimed = false`, zero
validators, the required independent-validator count, and hashes of the
implemented artifacts.

## 10. Non-claims

This module does not establish that:

- every unmet need is caused by a structural mechanism;
- every aggregate shortage is artificial;
- every recorded authority basis is legally valid or enforceable;
- constituency representatives have authority beyond the recorded basis;
- exercise of a right guarantees successful remediation;
- resource expenditure establishes resolution;
- a completed remediation establishes a resolved state;
- improvement for one constituency establishes complete coverage;
- a single metric establishes non-regression;
- EMGN novelty and SICRP resolution are interchangeable; or
- implementation ratifies this module or any claim represented through it.

## 11. Machine artifacts

- JSON record schema: `schemas/sicrp-record.schema.json`
- Module-status schema: `schemas/sicrp-module-status.schema.json`
- RDF/OWL vocabulary: `ontology/sicrp.ttl`
- SHACL constraints: `shapes/sicrp.shacl.ttl`
- Conforming JSON record: `examples/sicrp-record.valid.json`
- Conforming RDF record: `examples/sicrp-record.valid.ttl`
- Module governance/status record:
  `governance/sicrp-v0.1.0.status.json`
- Executable tests: `tests/test_sicrp.py`
- Validation workflow: `.github/workflows/validate-sicrp.yml`

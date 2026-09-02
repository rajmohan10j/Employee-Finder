# Employee Finder — Dependable Analytics and Reporting Delivery Proposal

**Scope:** Analytics plus the supporting data model, recruiter workflow, privacy/security, CI/CA, automated testing, rollout, and governance controls  
**Business use case:** Insurance Advisory sourcing and conversion intelligence  
**Status:** Revised full proposal

## 1. Outcome

Deliver analytics that can be trusted for operational decisions, not just charts that render. The system must identify the preferred audience, measure outreach and progression, preserve candidate and event history, prevent PII leakage, and make every release reproducible and reversible.

The default targeting policy is:

- **P1:** age above 50, represented as 51+, and retired government employee;
- **P2:** a configurable expansion across a wider minimum age, employment sector, job background, experience, and location;
- P1 and P2 remain separate so the team can measure whether expansion improves the advisory pipeline.

This proposal treats “CI/CA” as **Continuous Integration plus Continuous Assurance**. If the project uses a different internal meaning for CA, the label can change without removing the controls defined here.

## 2. Current-state findings

The UAT code already includes:

- an Excel-backed Flask service with `RLock` protection;
- conversion fields for call response, meeting agreement, and advisory interest;
- an `/api/analytics` endpoint;
- a Chart.js analytics interface;
- staging/review flows and GFS-style backups;
- Playwright desktop/mobile test suites.

The main dependability gaps are structural:

1. The reviewed tracker headers do not include age, employment sector, retirement status, or a normalized job-background field, so the P1/P2 policy cannot be calculated reliably.
2. One candidate row cannot represent multiple outreach attempts, changing outcomes, or a reliable first-contact cohort.
3. A blank `Call Response` can be inferred from `HR Called`; this is useful for migration but must be labeled as inferred rather than treated as a confirmed fact.
4. Current funnel counts are snapshot aggregates and may not represent the same candidate cohort at each stage.
5. Current reports lack consistent denominator, unknown-value, sample-size, provenance, and as-of handling.
6. The HTML loads Chart.js from a CDN even though the application is intended for local/LAN use.
7. The reviewed Flask code permits `Access-Control-Allow-Origin: *`; this needs to be constrained before exposing candidate data beyond a trusted local environment.

## 3. Target data model

### 3.1 Candidate master fields

Add controlled, validated fields to the master record or a compatible staging layer:

| Field | Purpose | Rule |
|---|---|---|
| `Age` or approved age band | P1/P2 targeting | Integer or controlled band; age 50 is not P1, age 51 is eligible |
| `Employment Sector` | Government/Public/Private segmentation | Controlled vocabulary plus Unknown |
| `Employment Status` | Active/Retired/Other | Controlled vocabulary |
| `Retirement Status` | Explicit retired/not-retired/unknown state | Do not infer retirement from age alone |
| `Job Background` | Normalized role family or career background | Preserve original role separately |
| `Experience Years` | Numeric reporting and bands | Store parsed value plus parse status |
| `Target Priority` | P1/P2/Unclassified | Derived from versioned rules, not manually trusted as the only source |
| `Target Rule Version` | Auditability | Records which policy classified the candidate |
| `Data Quality Status` | Complete/Partial/Invalid | Supports visible unknowns and remediation queues |
| `Contact Permission/Basis` | Outreach governance | Use the organization’s approved policy vocabulary; do not invent legal consent claims |

Do not require date of birth unless there is a documented business and privacy justification. An age-at-sourcing value or approved age band is usually more data-minimizing. If age is supplied from a resume, retain a source/confidence indicator.

### 3.2 Outreach event history

Add a separate `Contact Attempts` worksheet or storage abstraction. One row per attempt should contain:

- candidate key;
- attempt timestamp and timezone;
- channel, such as phone or WhatsApp;
- staff member;
- outcome: connected, no response, busy, wrong number, declined, or other approved value;
- structured response classification;
- next action and follow-up date;
- meeting status if discussed;
- advisory-interest status if discussed;
- minimal operational note;
- created/updated audit metadata.

The master candidate row may retain the current summary fields for convenience, but analytics should prefer the event history when available. This supports multiple attempts, accurate cohorts, and reconciliation.

### 3.3 Controlled vocabularies and validation

Centralize allowed values for sectors, retirement statuses, response outcomes, meeting modes, advisory stages, source portals, and job-background families. Reject invalid values at the API boundary and flag legacy values during import. Do not silently map a value to P1/P2 when the mapping is uncertain.

## 4. P1/P2 classification and expansion workflow

Classification should be a versioned, explainable rule:

```text
P1 = age > 50 AND sector = Government AND retirement_status = Retired
P2 = configured expansion criteria satisfied AND not P1
Unclassified = required fields missing or invalid
```

The configuration must support:

- minimum age;
- eligible sectors;
- retirement-status rules;
- job-background families;
- experience minimum/maximum;
- optional location and source constraints.

Each classified record should expose an eligibility reason, such as `P1: age=62; sector=Government; retired=Yes`, without exposing unnecessary PII in aggregate logs.

## 5. Recruiter workflow

The dependable workflow is:

1. **Import/source:** ingest candidates and retain source metadata.
2. **Normalize:** validate age, sector, retirement status, role, and experience; route incomplete records to data-quality review.
3. **Classify:** calculate P1/P2/Unclassified using the active rule version.
4. **Prioritize:** present P1 first, then P2 ordered by configured job-background and experience criteria.
5. **Outreach:** record every attempt as an event; do not overwrite history.
6. **Follow-up:** schedule next action with owner and due date.
7. **Meeting:** record mode, date, and outcome explicitly.
8. **Advisory progression:** distinguish interested, information requested, declined, and formally agreed.
9. **Review/staging:** route sensitive or shared changes through the existing review queue where required.
10. **Close:** record closure reason without deleting historical events.
11. **Report:** show the selected cohort, data-quality state, as-of time, and denominator definitions.
12. **Improve:** use conversion evidence to adjust P2 configuration, never by silently changing P1.

The UI should make the next action obvious and prevent a recruiter from marking a candidate as accepted when only interest or meeting agreement was recorded.

## 6. Analytics and API contract

Use the existing `/api/analytics` endpoint as the compatibility point. Extend it with:

- report and definitions versions;
- P1/P2 criteria;
- selected filters and cohort dates;
- as-of timestamp;
- counts, numerators, denominators, and rates;
- unknown, invalid, and inferred counts;
- sample-size warnings;
- data-reconciliation status;
- authorized drill-down references rather than raw PII in aggregate payloads.

The four report groups are:

1. Target Audience Coverage;
2. Outreach Response Performance;
3. Meeting/Interview Agreement;
4. Advisory Interest and Formal Acceptance.

Every report must show P1, P2, and Unclassified separately. Every rate must display its denominator. Zero-denominator values are `N/A`; unknown data is not converted to negative outcomes.

## 7. Privacy and security requirements

### Data minimization and access

- Keep real candidate files and contact details outside Git and test fixtures.
- Do not place phone numbers, emails, resumes, or raw call notes in analytics logs, screenshots, or CI artifacts.
- Return aggregates by default; require an authorized drill-down for candidate names.
- Add authentication/authorization before LAN or non-local access is treated as production use.
- Restrict CORS from `*` to approved origins, or remove cross-origin access when it is not needed.
- Define role permissions for recruiter, reviewer, administrator, and report-only users.

### Retention, backups, and audit

- Keep the existing backup-before-write behavior and verify that new sheets/fields are included.
- Test restore into a disposable copy before a production restore.
- Record who changed classification rules, candidate outcomes, and report configuration.
- Define retention for event history, exports, audit logs, and backups.
- Watermark exports with report version, filter criteria, and generated timestamp.

### External assets and services

Self-host Chart.js or provide an offline-safe fallback. Do not send candidate data to a CDN, analytics service, or LLM. If an external service is ever added, require a separate privacy review and explicit approval.

## 8. CI — Continuous Integration

Every change to UAT should run:

- Python syntax/import checks;
- unit tests for classifiers, parsers, status mappings, and rate calculations;
- API contract tests for valid, invalid, empty, and legacy data;
- aggregate reconciliation tests against a fixed anonymized fixture;
- tests for age boundaries, sector/retirement combinations, missing values, duplicate records, and zero denominators;
- Excel round-trip tests that preserve existing columns and new fields;
- staging/review and backup tests;
- Playwright desktop tests;
- Playwright mobile viewport tests;
- JavaScript syntax and analytics rendering tests;
- PII and secret scans for repository changes;
- dependency and license checks where supported.

The CI gate should fail if a report changes without an updated definitions version or fixture expectation.

## 9. CA — Continuous Assurance

After deployment or during scheduled checks, measure:

- report API availability and latency;
- count reconciliation between Excel rows, API totals, and UI totals;
- percentage of candidates with complete P1/P2 fields;
- percentage of outcomes inferred from legacy fields;
- unknown/invalid value counts by field;
- event-to-master summary reconciliation;
- backup success and restore-test age;
- failed imports, failed writes, and review-queue errors;
- unusual conversion-rate changes caused by denominator or schema changes;
- stale follow-ups and records without an owner.

Alert on failed backups, broken report contracts, large unknown-value increases, non-reconciling totals, or a sudden change in inferred-versus-explicit outcomes. Preserve the evidence used to investigate each alert.

## 10. Automated test matrix

### Unit and contract tests

- age 50 excluded and age 51 included;
- P1 requires all three conditions;
- unknown sector or retirement status produces Unclassified;
- P2 configuration changes classification without changing historical rule versions;
- role/background normalization is deterministic;
- experience parsing handles numeric, range, blank, and invalid values;
- response mapping distinguishes explicit from inferred outcomes;
- meeting interest is not advisory acceptance;
- rates handle zero denominators and small samples;
- all report totals reconcile to the selected fixture population.

### Integration tests

- import a legacy workbook and preserve unknown fields for review;
- write/read new master fields through OpenPyXL;
- append multiple contact attempts without overwriting prior events;
- update a summary from event history;
- submit, approve, reject, and audit a staged change;
- create and restore a backup containing both candidate and event data;
- verify API output matches the stored fixture.

### Browser tests

- P1/P2 filters update all reports;
- count/percentage toggle preserves totals;
- unknown/inferred badges appear;
- charts render from a local asset or display a useful fallback;
- empty and API-error states are understandable;
- drill-down is not available to unauthorized roles;
- desktop and mobile layouts have no horizontal overflow;
- analytics changes do not break candidate editing, review, QR/mobile, or quick-close workflows.

### Manual UAT evidence

For each release candidate, retain:

- anonymized fixture input;
- expected metric table calculated independently;
- API response sample;
- desktop and mobile screenshots;
- test run identifiers;
- reviewer sign-off and known limitations.

## 11. Rollout plan

### Phase 0 — Baseline

- Snapshot the UAT workbook and verify restore.
- Record current dashboard/API totals.
- Freeze the metric definitions and P1/P2 rule version.
- Confirm the real-data location and PII exclusion rules.

### Phase 1 — Data and event foundation

- Add normalized targeting fields and controlled values.
- Add the contact-attempt structure.
- Import legacy values as explicit, inferred, or unknown.
- Run data-quality reconciliation before enabling decision reports.

### Phase 2 — Analytics hardening

- Extend `/api/analytics` with versions, filters, denominators, unknowns, and as-of data.
- Add P1/P2 report views, failure states, and privacy-safe drill-down.
- Self-host the chart asset or implement the fallback.

### Phase 3 — Pilot

- Use a small controlled recruiter group.
- Compare report totals with hand-calculated fixture results and selected real records.
- Review whether P2 produces useful incremental meetings/advisory interest without diluting P1 focus.

### Phase 4 — Release

- Require CI green, CA baseline established, UAT sign-off, backup verification, and rollback rehearsal.
- Promote only the verified UAT build to the production copy.
- Keep the previous version and pre-release workbook snapshot available.

## 12. Rollback and recovery

Rollback must be defined separately for code, configuration, and data:

- **Code:** restore the previous verified application version.
- **Rules:** restore the previous P1/P2 configuration and retain rule-version history.
- **Schema:** preserve unknown columns/values; do not destructively delete new fields during rollback.
- **Data:** create a safety backup before restore, restore into a controlled copy, reconcile counts, then switch only after approval.
- **Reports:** mark affected exports as superseded if a definitions or denominator defect is discovered.

## 13. Delivery gates

The feature is ready for production only when:

- P1/P2 classification is explainable and boundary-tested;
- event history and master summaries reconcile;
- rates show denominators and retain unknowns;
- explicit and inferred outcomes are distinguished;
- aggregate responses protect PII;
- CORS and access controls match the deployment boundary;
- CI checks and browser suites pass;
- CA checks have a baseline and owner;
- backup restore has been exercised;
- UAT and rollback sign-offs are recorded.

## 14. Decisions still required

1. Which age field is permitted: age-at-sourcing, age band, or another approved representation?
2. What exact employment-sector vocabulary should be used for Government, Public Sector, and Private Sector?
3. Which evidence qualifies as formal advisory acceptance?
4. Which users may view candidate-level drill-down and exports?
5. What minimum sample size should trigger a warning or suppression?
6. What is the approved retention period for contact events, exports, and backups?
7. Does “CI/CA” have an internal definition different from Continuous Integration/Continuous Assurance?

Until these decisions are recorded, the system may display operational counts, but it should not present P1/P2 conversion results as final business evidence.

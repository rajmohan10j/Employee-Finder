# Employee Finder — Analytics and Report Changes Proposal

**Scope:** Analytics/report changes only  
**Audience:** Recruiters, sourcing leads, reviewers, and decision-makers for Insurance Advisory outreach  
**Status:** Revised proposal based on the current README, UAT proposal, and UAT implementation review

## 1. Objective

Improve the analytics area so the team can answer four operational questions:

1. Are we sourcing the preferred audience for Insurance Advisory?
2. Which audience profiles respond to outreach?
3. Which profiles agree to an interview or meeting?
4. Which profiles become genuinely interested in, or formally accept, an advisory role?

The default priority is **P1: age above 50 (51+) and retired government employees**. The system must also support a configurable **P2 expansion** using a wider minimum age, job background, employment sector, and experience range. P2 is an evidence-based expansion, not an automatic replacement of P1.

## 2. Current state and required correction to the earlier proposal

The earlier `Analytics_Proposal.md` describes several items as future work that are already present in the UAT branch:

| Capability | Current UAT state | Proposal implication |
|---|---|---|
| `Call Response` | Present in `TRACKER_HEADERS`, form, API logic, and analytics | Harden definitions and provenance; do not add it again |
| `Interview / Meeting Agreed` | Present in the tracker, form, API aggregation, and charts | Improve denominator rules and segment analysis |
| `Advisory Role Interest` | Present in the tracker, form, API aggregation, and charts | Separate interest from formal acceptance |
| `/api/analytics` | Already implemented in `candidate_app/app.py` | Extend the contract rather than create a duplicate endpoint |
| Analytics UI | Existing Chart.js report area in `templates/index.html` and `static/js/app.js` | Add filters, quality states, drill-down, and reliable loading |
| Age, employment sector, retirement status | Not present in the reviewed `TRACKER_HEADERS` | P1/P2 reports cannot be reliable until these values are supplied by the data model; see the full proposal |

This proposal therefore focuses on the report layer. The supporting data and workflow changes required to make P1/P2 dependable are intentionally specified in the companion full-delivery proposal.

## 3. Audience segmentation

### P1 — preferred segment

P1 is true only when all required conditions are known and satisfied:

- Age is greater than 50, represented as 51+.
- Employment sector is Government.
- Employment status or retirement status is Retired.

Unknown age, sector, or retirement status must not be silently treated as P1.

### P2 — controlled expansion

P2 is a configurable expansion query. Its parameters must be visible in the report header and included in the API response:

- minimum age;
- accepted employment sectors, such as Government, Public Sector, and Private Sector;
- retirement/employment-status rules;
- job-background or role families;
- experience range;
- location and source filters, where required.

The report must show P1 and P2 side by side. It must never merge them into one “target” count without labeling the priority.

## 4. Report set

### Report 1 — Target Audience Coverage

**Question:** Are we sourcing enough P1 candidates, and what is the composition of the P2 expansion pool?

Required views:

- P1, P2, and unclassified/unknown counts;
- age-band distribution;
- employment sector and retirement-status distribution;
- job-background and current-role distribution;
- experience bands;
- location and portal/source distribution;
- data completeness rate for fields required by P1/P2.

Every chart must support the same global filters and expose count plus percentage. Unknown values must be visible rather than discarded.

### Report 2 — Outreach Response Performance

**Question:** Which target profiles respond to outreach?

Required views:

- contacted/attempted count;
- reached or connected count, where available;
- positive, neutral, negative, no-response, and pending outcomes;
- response and positive-response rates by P1/P2, sector, retirement status, job background, experience band, location, and source;
- absolute counts beside every rate;
- cohort filter based on sourcing date or first outreach date.

The existing fallback from `HR Called` to `Call Response` should be labeled as an inferred/proxy value. It must not be displayed as equivalent to a manually recorded outcome.

### Report 3 — Meeting and Interview Agreement

**Question:** Which profiles agree to continue to an interview or meeting?

Required views:

- meeting-agreement count and rate;
- in-person versus virtual split;
- agreement rate by P1/P2, sector, retirement status, job background, experience, location, and source;
- pending and not-discussed counts;
- selected-segment candidate drill-down for authorized users.

The default denominator is candidates with a known outreach outcome in the selected population. The report must also show the denominator definition in plain language.

### Report 4 — Advisory Interest and Acceptance

**Question:** Which profiles progress toward the Insurance Advisory role?

Required views:

- sourced → outreach attempted → positive response → meeting agreed → advisory interest → formal acceptance;
- separate counts for `Interested - More Info Needed`, `Agreed`, `Declined`, `Not Discussed`, and `Unknown`;
- conversion by P1/P2, sector, retirement status, job background, experience, location, and source;
- named list of candidates only after an authorized drill-down action;
- cohort and as-of date displayed with the result.

“Interested” must not be reported as “accepted.” Formal acceptance requires an explicit recorded status and, if the business requires it, a separate acceptance date or confirmation reference.

The proposed parametric simulator is deferred until there is sufficient clean historical data. It should not project advisor counts from small or mixed-denominator samples.

## 5. Metric contract

The API and UI must use one shared definition table:

| Metric | Definition |
|---|---|
| Sourced | Eligible, non-duplicate candidate records in the selected population and period |
| Attempted | Candidate with at least one recorded outreach attempt; current `HR Called` is a temporary proxy |
| Positive response | Explicit `Call Response = Positive`; inferred values must be flagged |
| Meeting agreed | `Interview / Meeting Agreed` begins with `Yes` |
| Advisory interested | `Interested - More Info Needed` |
| Advisory accepted | `Advisory Role Interest = Agreed`, not merely positive or interested |
| Rate | Numerator divided by the explicitly stated stage denominator; denominator zero returns `N/A`, not 0% |
| Unknown | Missing, invalid, or unclassifiable value; retained in quality totals |
| As of | Timestamp and filter configuration used to produce the report |

Funnel stages must be cohort-aware. A snapshot of current candidate fields may produce non-monotonic counts; if that happens, the UI must show a data-quality warning rather than implying a valid sequential funnel.

## 6. Analytics UI changes

Add the following to the existing Analytics tab:

- global date and source filters;
- P1/P2 selector with visible criteria;
- minimum-age, sector, retirement-status, job-background, experience, and location filters;
- count/percentage toggle;
- “known,” “unknown,” and “inferred” data-quality indicators;
- sample-size display on every rate;
- reset filters and export-current-view actions;
- click-through from a chart segment to the authorized candidate list;
- loading, empty, partial-data, and API-error states;
- visible “as of” timestamp and report definition link.

Charts must not expose candidate names in tooltips by default. Drill-down should be deliberate, permission-controlled, and auditable.

The current HTML loads Chart.js from a CDN. Because the application is intended to work on a local/LAN address, analytics should either self-host the chart library or show a clear degraded state when the asset is unavailable.

## 7. API changes within this proposal

Extend the existing `/api/analytics` response rather than introduce another analytics endpoint. The response should include:

- `report_version`;
- `as_of` timestamp;
- applied filter configuration;
- P1/P2 criteria and counts;
- counts, rates, and denominators for each report;
- `unknown_counts` and `inferred_counts`;
- sample-size and suppression/warning metadata;
- a stable `definitions_version` so saved exports can be interpreted later.

The endpoint should accept validated filters and reject unsupported values with a useful client error. It should not return raw phone numbers, emails, or free-text remarks in aggregate responses.

## 8. Minimum acceptance criteria

- Age 50 is excluded from P1; age 51 is eligible when sector and retirement status also match.
- A candidate with unknown retirement status is not counted as P1.
- P1 and P2 counts are mutually labeled and reconcile to the selected population, including unknowns.
- Every rate displays its numerator and denominator.
- Zero-denominator rates display `N/A`.
- Inferred call outcomes are visibly distinguished from explicit call outcomes.
- “Interested” and “Agreed” appear as separate advisory stages.
- Changing any global filter updates every report consistently.
- A small segment displays a sample-size warning and does not produce misleading projections.
- API responses include an as-of timestamp and applied filters.
- Aggregate responses contain no candidate contact details.
- The UI remains usable when the analytics API or chart asset is unavailable.
- Existing dashboard, candidate editing, review, backup, and mobile workflows continue to work.

## 9. Out of scope

- Adding or redesigning the candidate data model;
- recording multiple outreach attempts per candidate;
- authentication and authorization redesign;
- retention, backup, or privacy policy changes;
- CI/CA pipeline construction;
- production rollout and rollback execution.

Those requirements are covered in `Analytics_Report_Dependable_Delivery_Proposal.md`.

## 10. Recommended implementation order

1. Freeze metric definitions and P1/P2 filter semantics.
2. Add a report contract version and data-quality metadata to `/api/analytics`.
3. Implement global filters and cohort/as-of handling.
4. Add P1/P2 views and unknown/inferred states.
5. Add drill-down and export with privacy-safe behavior.
6. Replace or locally package the CDN dependency.
7. Run API, aggregate-reconciliation, desktop, mobile, and failure-state tests.

The analytics-only release is complete only when the report definitions, displayed numbers, and API values agree on the same fixture dataset.

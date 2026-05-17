# StageOS Full UAT Journey Pack

This pack is for non-technical user acceptance testing. Use `TESTING_GUIDE.md` for the matching technical/API checks and examples.

The goal is to prove StageOS as the theatre operating control layer:

`intake -> approval -> Workspace -> department execution -> files/evidence -> calendar -> reports -> Audit Trail`

## How To Use This Pack

1. Run `python manage.py seed_dev_data` and use the Moukangwe Theatre users listed in `docs/UAT_USERS.md`.
2. Start the backend and frontend.
3. Log in through `/login` as each role.
4. Complete each journey through the browser.
5. Record Pass/Fail and notes in the tables below.
6. Use API checks only to confirm permission boundaries or investigate failed browser steps.

## Authority Mapping

| Theatre authority | Current implementation mapping | UAT expectation |
| --- | --- | --- |
| CEO / COO | `executive` | Organisation-wide oversight, approvals, reports, Audit Trail and executive actions |
| GM / Site Manager | `manager` | Site/operations oversight, reports, issue raising and authorised approvals |
| Department Head | Department membership with `department_manager` authority | Own department execution, assignment, review and response to executive actions |
| Internal Admin | `internal_admin` | Settings, users and full administrative configuration |
| Board / Read-only | `read_only` | Report viewing only, no mutation |
| Client / Supplier / Artist external | external user types | Own records only where portal surface exists |

## Manual UAT Master Table

| Journey | Role | Objective | Browser route | Steps | Expected result | Pass/Fail | Notes |
| ------- | ---- | --------- | ------------- | ----- | --------------- | --------- | ----- |
| Login and access | All users | Confirm role-aware access | `/login`, `/dashboard` | Log in, inspect sidebar, open Dashboard, logout | Correct dashboard/permission state; external and read-only users cannot mutate |  |  |
| Client request | Client external or internal requester | Submit request without internal visibility | `/programming` if client UI is available, otherwise API-assisted | Submit venue booking or production proposal | Private Intake Request created; own request only; internal notes hidden |  | Client-facing UI is limited, so API-assisted UAT may be needed |
| Programming intake | Programming Head | Review private intake | `/programming` | Open intake, start review, add notes, create hold, recommend decision | Raw intake visible to Programming only; actions audited |  |  |
| Leadership decision | CEO / COO / GM | Decide request | `/programming` | Approve, decline, defer or request changes | Decision recorded; comments required where appropriate; Audit Trail updated |  |  |
| Workspace conversion | Programming Head | Convert approved request | `/programming`, `/workspaces/[id]` | Convert approved intake to Workspace | Workspace created once; source intake linked; departments see approved Workspace, not raw intake |  |  |
| Calendar | Internal users | Plan operational dates and issues | `/calendar` | View holds/slots/issues; raise, progress and resolve issue | Real API data loads; issue lifecycle works; report and Audit Trail update |  |  |
| Calendar double-booking | Programming Head | Prove venue protection | `/calendar`, direct API if needed | Create confirmed Tene Theatre hold 18:00-22:00, then attempt another confirmed Tene hold 19:00-21:00 | Backend returns `409`; CalendarIssue and Audit Trail record the blocked conflict |  |  |
| Calendar alternate venue | Programming Head | Prove legitimate parallel events | `/calendar`, direct API if needed | Create Tumisho Theatre hold at the same time as Tene Theatre | Booking is allowed because venue differs |  |  |
| Calendar non-overlap | Programming Head | Prove same-day scheduling works | `/calendar`, direct API if needed | Create Tene Theatre hold 09:00-11:00, then another 11:00-13:00 | Booking is allowed because occupied windows do not overlap |  |  |
| Calendar blackout | Programming Head | Prove venue closure protection | `/calendar`, direct API if needed | Create confirmed blackout/maintenance slot, then attempt confirmed hold in that window | Booking is blocked and issue is raised |  |  |
| Capacity check | Programming Head / GM | Prove capacity warning/block | `/calendar`, direct API if needed | Attempt event with expected audience above venue capacity | Warning issue is created; more than 10 percent over capacity is blocked |  |  |
| Marketing | Head of Marketing and Communications | Manage campaign execution | `/marketing`, `/workspaces/[id]` | Create campaign/deliverables, upload proof, complete deliverable, respond to executive action | Marketing can edit own records; evidence blocks false completion; raw intake hidden |  |  |
| Technical | Technical Head / Stage Manager | Manage technical readiness | `/technical`, `/calendar`, `/workspaces/[id]` | Create rider, crew/equipment requirements, submit/approve/revise where supported | Technical readiness visible; no unauthorised Programming hold edits |  |  |
| FOH / Operations | FOH Head | Manage show-day readiness | `/operations`, `/workspaces/[id]` | Create FOH plan, checklist, incident and close-out | FOH workflow works; incidents/checklists audited; sensitive notes checked |  |  |
| Contracts / Legal | Contracts Head | Control contract readiness | `/contracts`, `/workspaces/[id]` | Create contract, submit review, sign/lock document | Contract status/readiness updates; signed document lock works |  |  |
| Suppliers / SCM / Finance | SCM / Finance Head | Manage supplier readiness | `/suppliers`, `/workspaces/[id]` | Verify/reject supplier docs, create engagement/payment pack | Readiness and reports update; payment-sensitive data checked |  |  |
| Artists | Artist Management | Manage artist readiness | `/artists`, `/workspaces/[id]` | Verify/reject artist docs, create engagement and link contract | Artist readiness updates; external artist restrictions checked |  |  |
| Ticketing | Ticketing Head | Track ticketing and evidence | `/ticketing`, `/workspaces/[id]` | Set provider/link/pricing, import sales, settle | Tracking works without pretending to be live ticketing sync |  |  |
| Youth Development | Youth Head | Manage youth programme controls | `/youth`, `/workspaces/[id]` | Create youth project, sessions, consent, attendance, assessments | Youth workflow works; sensitive data remains restricted |  |  |
| Governance / M&E | Governance Head | Manage risks, KPIs and corrective actions | `/governance`, `/governance/risks`, `/reports` | Create risk, KPI, corrective action, evidence | Board Summary and Audit Trail update; read-only users cannot edit |  |  |
| Documents and Evidence | Department users | Prove file/evidence control | `/documents`, `/workspaces/[id]` | Upload file, submit evidence, accept/reject, download file, complete task | Real upload/download works; rejection requires reason; no-evidence-no-completion enforced |  |  |
| Approvals and Process | Approver / Executive | Control gates | `/approvals`, `/workspaces/[id]` | Create/decide approval, complete evidence/approval-required Process step | Evidence and approval requirements block progression until satisfied |  |  |
| Executive actions | Executive and department head | Intervene with accountability | `/governance`, `/workspaces/[id]` | Request change, department acknowledges/completes | Department sees instruction; lifecycle audited |  | Use department head users such as Marketing Head or Technical Head |
| Reports | Executive, GM, Board | Answer management questions | `/reports` | Open Executive, Board, Workspace, Department, Risk, Contract, Supplier, Evidence Gaps and Calendar reports | Reports load real data and respect permissions |  |  |
| Audit Trail | Executive / Admin / Manager | Prove accountability | `/audit` | Inspect recent intake, conversion, file, evidence, approval, process, calendar and executive events | Critical actions visible with actor/time/target/reason where applicable |  |  |
| Admin / Settings | Internal Admin | Manage organisation structure and users | `/settings` | Review org, site, venue, department and user management | Settings are tenant-scoped; unauthorised users cannot manage users |  |  |
| External users | Client, Supplier, Artist | Confirm external boundaries | `/programming`, `/suppliers`, `/artists` where available | View own records only; attempt unrelated access | No internal operations or other external records leak |  | Full self-service portals remain limited |

## Required Negative UAT

| Negative journey | Role | Steps | Expected result | Pass/Fail | Notes |
| --- | --- | --- | --- | --- | --- |
| Marketing views raw intake | Marketing Head | Try `/programming` and direct intake API | Blocked or no raw intake data leaked unless explicitly authorised |  |  |
| Technical edits Programming hold | Technical Head | Attempt direct hold mutation | Blocked unless role is authorised |  |  |
| Marketing edits Programming hold | Marketing Head | Attempt direct hold mutation | Backend returns `403` with Programming venue scheduling message |  |  |
| Ticketing edits Programming hold | Ticketing Head | Attempt direct hold mutation | Backend returns `403` |  |  |
| Read-only approves | Board user | Attempt approval decision | Backend returns `403`; no decision recorded |  |  |
| Board edits Calendar | Board user | Attempt direct hold or slot mutation | Backend returns `403`; no calendar item is created |  |  |
| Supplier sees another supplier | Supplier external | Open supplier list/API | Own supplier only |  |  |
| Artist sees unrelated artist/contract | Artist external | Open artist/contract views/API | Own records only; unrelated contracts hidden |  |  |
| Wrong tenant downloads file | User from other organisation | Request document download URL | `404` or denied; no file returned |  |  |
| Missing evidence completion | Department user | Complete evidence-required task with no accepted evidence | Frontend blocks; direct API returns `422` |  |  |
| Department cancels executive action | Staff department user | Attempt cancel action | Backend returns `403`; action remains active |  |  |

## Automated Coverage Already Present

The current automated suite includes:

| Automated proof | File |
| --- | --- |
| Master intake-to-audit journey | `tests/e2e/test_master_theatre_journey.py` |
| Documents, upload/download and evidence review | `tests/documents/test_api.py` |
| Calendar issue workflow | `tests/programming/test_api.py` |
| Department execution modules | department test files under `tests/marketing`, `tests/technical`, `tests/operations`, `tests/contracts`, `tests/suppliers`, `tests/artists`, `tests/ticketing`, `tests/youth`, `tests/governance` |
| Process and approvals | `tests/workflows/test_api.py`, `tests/approvals/test_api.py` |
| Reports | `tests/reports/test_api.py`, `tests/reports/test_management_reports.py` |
| Tenant isolation and permissions | `tests/isolation`, `tests/security` |
| Sprint 4 calendar hardening | `tests/programming/test_calendar_hardening.py` |

## Current Readiness Interpretation

If the automated gates pass and this manual UAT pack passes in the browser, StageOS can move from **QA-ready MVP candidate** to **full manual UAT-ready**.

Controlled pilot readiness still needs:

- staging deployment sign-off,
- backup and restore proof,
- monitoring and error alerting,
- real role-based UAT with theatre staff,
- production data and privacy review.

## Sprint 4 Product Closure Notes

- Executive override is intentionally deferred for UAT. Confirmed conflicts are blocked rather than overridden.
- CalendarSlot now supports start/end time, setup buffer, strike buffer and expected audience.
- VenueHold now supports setup buffer, strike buffer and expected audience.
- CalendarIssue is the visible record for blocked conflicts, provisional overlap warnings, blackout conflicts and capacity warnings.
- Browser UAT should use the role-specific dashboards added in Sprint 3 and the seeded users in `docs/UAT_USERS.md`.

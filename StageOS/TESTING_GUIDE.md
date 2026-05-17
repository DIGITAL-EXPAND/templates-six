# StageOS Testing Guide

This guide is aligned with the current StageOS implementation after the intake, calendar, files/evidence, department execution, executive action, reports and master UAT proof work.

Use it in two layers:

1. **Technical/API tests** prove backend rules, permissions, tenant isolation and audit behaviour.
2. **Manual browser UAT** proves that real users can complete the journeys through the frontend.

## Current Frontend Routes

| Area | Route | Notes |
| --- | --- | --- |
| Login | `/login` | Public login screen |
| Dashboard | `/dashboard` | Role-aware operational dashboard |
| Calendar | `/calendar` | Venue holds, calendar slots and calendar issues |
| Workspaces | `/workspaces`, `/workspaces/create`, `/workspaces/[id]` | Workspace list, create and detail tabs |
| Programming | `/programming` | Private intake, reviews, holds and producer handoff |
| Tasks | `/tasks` | Task list, creation, evidence-required completion |
| Documents | `/documents` | Real file upload/download and evidence review |
| Approvals | `/approvals` | Approval decisions and evidence review |
| Contracts | `/contracts` | Contract records, review/sign/lock actions |
| Suppliers / SCM | `/suppliers` | Supplier profiles, documents, engagements, payment packs |
| Artists | `/artists` | Artist profiles, documents and engagements |
| Marketing | `/marketing` | Campaigns, deliverables and evidence |
| Technical | `/technical` | Riders, crew/equipment and technical readiness |
| FOH / Operations | `/operations` | FOH plans, checklists and incidents |
| Ticketing | `/ticketing` | Provider setup, sales import and settlement tracking |
| Youth Development | `/youth` | Youth projects, sessions, consent, attendance and assessments |
| Governance | `/governance`, `/governance/risks` | Risks, KPIs, corrective and executive actions |
| Reports | `/reports` | Executive, board, readiness, risk, supplier, evidence and calendar reports |
| Audit Trail | `/audit` | Audit export view |
| Settings | `/settings` | Organisation, structure and users |

## Verified API Endpoint Families

| Area | API |
| --- | --- |
| Auth | `/api/token/`, `/api/token/refresh/`, `/api/v1/me/`, `/api/health/` |
| Workspaces | `/api/v1/contexts/` |
| Structure | `/api/v1/sites/`, `/api/v1/venues/`, `/api/v1/spaces/`, `/api/v1/departments/`, `/api/v1/users/` |
| Programming | `/api/v1/programming/intake-requests/`, `/api/v1/programming/intake-reviews/`, `/api/v1/programming/producer-assignments/`, `/api/v1/programming/venue-holds/`, `/api/v1/programming/calendar-slots/`, `/api/v1/programming/calendar-issues/` |
| Tasks | `/api/v1/tasks/`, `/api/v1/tasks/{id}/complete/` |
| Documents & Evidence | `/api/v1/documents/`, `/api/v1/documents/upload/`, `/api/v1/documents/{id}/download/`, `/api/v1/evidence/`, `/api/v1/evidence/{id}/accept/`, `/api/v1/evidence/{id}/reject/` |
| Approvals | `/api/v1/approvals/routes/`, `/api/v1/approvals/steps/`, `/api/v1/approvals/requests/`, decision actions on `/api/v1/approvals/requests/{id}/.../` |
| Process | `/api/v1/workflows/templates/`, `/api/v1/workflows/step-templates/`, `/api/v1/workflows/instances/`, `/api/v1/workflows/steps/{id}/advance/` |
| Executive Actions | `/api/v1/governance/executive-actions/`, `/acknowledge/`, `/complete/`, `/cancel/` |
| Governance | `/api/v1/governance/kpis/`, `/api/v1/governance/kpi-evidence/`, `/api/v1/governance/risks/`, `/api/v1/governance/corrective-actions/` |
| Contracts | `/api/v1/contracts/templates/`, `/api/v1/contracts/records/`, `/api/v1/contracts/signatures/` |
| Suppliers | `/api/v1/suppliers/`, `/api/v1/suppliers/documents/`, `/api/v1/suppliers/engagements/`, `/api/v1/suppliers/payment-packs/` |
| Artists | `/api/v1/artists/`, `/api/v1/artists/documents/`, `/api/v1/artists/engagements/` |
| Marketing | `/api/v1/marketing/campaigns/`, `/api/v1/marketing/deliverables/` |
| Technical | `/api/v1/technical/riders/`, `/api/v1/technical/crew/`, `/api/v1/technical/equipment/` |
| FOH / Operations | `/api/v1/operations/foh-plans/`, `/api/v1/operations/checklists/`, `/api/v1/operations/incidents/` |
| Ticketing | `/api/v1/ticketing/setups/`, `/api/v1/ticketing/sales-imports/` |
| Youth | `/api/v1/youth/projects/`, `/api/v1/youth/activities/`, `/api/v1/youth/sessions/`, `/api/v1/youth/learner-groups/`, `/api/v1/youth/facilitators/`, `/api/v1/youth/consent/`, `/api/v1/youth/attendance/`, `/api/v1/youth/assessments/`, `/api/v1/youth/showcases/` |
| Reports | `/api/v1/reports/executive-summary/`, `/board-summary/`, `/context-readiness/{id}/`, `/department-readiness/{id}/`, `/risk-register/`, `/contract-status/`, `/supplier-readiness/`, `/evidence-gaps/`, `/calendar-issues/`, `/audit-export/` |
| Audit Trail | `/api/v1/audit/` |

## Department-Specific Seed Users

Run the current seed command before manual UAT. It creates the Moukangwe Theatre UAT structure, venues, departments, users and demo records. Full credentials and role expectations are maintained in [docs/UAT_USERS.md](docs/UAT_USERS.md).

| User | Email | User type | UAT authority |
| --- | --- | --- | --- |
| Internal Admin | `admin@moukangwetheatre.test` | `internal_admin` | Settings, users, all operational areas |
| CEO | `ceo@moukangwetheatre.test` | `executive` | Organisation-wide oversight, approvals and interventions |
| COO | `coo@moukangwetheatre.test` | `executive` | Organisation-wide operational oversight and interventions |
| GM / Site Manager | `gm@moukangwetheatre.test` | `manager` | Site-level management, reports, approvals and interventions |
| Programming Head | `programming.manager@moukangwetheatre.test` | `manager` | Private intake, holds and programming handoff |
| Head of Marketing and Communications | `marketing.manager@moukangwetheatre.test` | `manager` | Marketing campaigns and deliverables |
| Technical Head / Stage Manager | `technical.manager@moukangwetheatre.test` | `manager` | Riders, crew, equipment and technical readiness |
| FOH / Operations Head | `foh.manager@moukangwetheatre.test` | `manager` | FOH plan, checklist and incidents |
| Contracts / Legal Head | `contracts.manager@moukangwetheatre.test` | `manager` | Contract records and signatures |
| SCM / Finance Head | `scm.manager@moukangwetheatre.test` | `manager` | Suppliers, payment packs and finance readiness |
| Ticketing Head | `ticketing.manager@moukangwetheatre.test` | `manager` | Ticketing setup, sales import and settlement |
| Youth Development Head | `youth.manager@moukangwetheatre.test` | `manager` | Youth projects, consent, attendance and assessments |
| Governance / M&E Head | `governance.manager@moukangwetheatre.test` | `manager` | Risks, KPIs and corrective actions |
| Hospitality / Restaurant Operations Head | `hospitality.manager@moukangwetheatre.test` | `manager` | Hospitality support and FOH-linked restaurant readiness |
| Board / Read-only | `board@moukangwetheatre.test` | `read_only` | Reports only, no mutation |
| Read-only | `readonly@moukangwetheatre.test` | `read_only` | Reports only, no mutation |
| Client External | `client@moukangwetheatre.test` | `client_external` | Own intake request only |
| Supplier External | `supplier@moukangwetheatre.test` | `supplier_external` | Own supplier records only where supported |
| Artist External | `artist@moukangwetheatre.test` | `artist_external` | Own artist records only where supported |

Password for every UAT user:

```text
MoukangweTest123!
```

Recommended seed command:

```powershell
.\.venv\Scripts\python.exe manage.py seed_dev_data
```

The current user model stores `user_type` and organisation, but not a direct user-to-department relationship. Department authority is represented through user naming, manager/staff role type, and seeded department-owned records such as tasks, approval steps, executive actions and module records.

## Technical Test Gates

Run these before manual UAT:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
npm run typecheck
npm run lint
npm run build
```

Expected current result:

| Gate | Expected |
| --- | --- |
| Migration check | Pass, no model changes detected |
| Django system check | Pass |
| Pytest | Pass, including `tests/e2e/test_master_theatre_journey.py` |
| Frontend typecheck | Pass |
| Frontend lint | Pass |
| Frontend build | Pass |

## API Test Examples

Replace `$TOKEN`, `$WORKSPACE_ID`, `$TASK_ID`, `$DOCUMENT_ID`, `$EVIDENCE_ID` and other IDs with values created in your environment.

### Login

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/token/" `
  -ContentType "application/json" `
  -Body '{"email":"admin@stageos.test","password":"Admin123!"}'
```

### Real Multipart File Upload

```powershell
$headers = @{ Authorization = "Bearer $TOKEN" }
$form = @{
  operating_context = $WORKSPACE_ID
  title = "Approved artwork proof"
  document_type = "marketing_asset"
  version = "1"
  file = Get-Item ".\test-files\artwork-proof.pdf"
}
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/documents/upload/" `
  -Headers $headers `
  -Form $form
```

Expected:

| Check | Expected |
| --- | --- |
| Valid file | `201` Document record |
| Disallowed MIME type | `400` with file validation error |
| Oversized file | `400` with file validation error |
| Read-only user upload | `403` |
| Unauthenticated upload | `401` |
| Audit Trail | `document.file_uploaded` |

### Secure Download

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/v1/documents/$DOCUMENT_ID/download/" `
  -Headers $headers `
  -OutFile ".\downloaded-proof.pdf"
```

Expected:

| Check | Expected |
| --- | --- |
| Authorised tenant user | `200` file response |
| Wrong tenant | `404` |
| Unauthenticated | `401` |
| Metadata-only document | `404` no stored file |
| Audit Trail | `document.downloaded` |

### Evidence Review and No-Evidence-No-Completion

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/evidence/" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body "{`"operating_context`":`"$WORKSPACE_ID`",`"task`":`"$TASK_ID`",`"document`":`"$DOCUMENT_ID`",`"submission_note`":`"UAT proof uploaded.`"}"

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/evidence/$EVIDENCE_ID/accept/" `
  -Headers $headers
```

Expected:

| Check | Expected |
| --- | --- |
| Evidence submission | `201`, `evidence.submitted` audit event |
| Evidence accept | `200`, task `evidence_provided=true` when linked to evidence-required task |
| Evidence reject without reason | `400` |
| Evidence reject with reason | `200`, `evidence.rejected` audit event |
| Complete evidence-required task before accepted evidence | `422` |
| Complete after accepted evidence | `200` |

### Calendar Issue Workflow

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/programming/calendar-issues/" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body "{`"title`":`"Load-in clash`",`"operating_context`":`"$WORKSPACE_ID`",`"severity`":`"high`"}"
```

Then call:

| Action | Endpoint |
| --- | --- |
| Progress | `POST /api/v1/programming/calendar-issues/{id}/progress/` |
| Resolve | `POST /api/v1/programming/calendar-issues/{id}/resolve/` with `note` |
| Cancel | `POST /api/v1/programming/calendar-issues/{id}/cancel/` |

Expected audit events include `calendar.issue_raised`, `calendar.issue_in_progress` and `calendar.issue_resolved`.

### Master API Journey

The automated master proof is:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_master_theatre_journey.py -q
```

It proves: intake, review, approval, Workspace conversion, venue hold, upload, evidence acceptance, task completion, approval, Process step, calendar issue, executive action, reports and Audit Trail.

## Manual Browser UAT

Use `http://localhost:3000/login`, then complete each row. Fill in Pass/Fail and Notes during testing.

| Journey | User | Frontend route | Steps | Expected result | Pass/Fail | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Login | All users | `/login` | Log in and log out | Correct Dashboard or permission state; session clears on logout |  |  |
| Executive dashboard | CEO / COO | `/dashboard` | Review Workspaces, approvals, risks, blockers, evidence gaps | Organisation-wide operational picture loads from API |  |  |
| GM dashboard | GM / Site Manager | `/dashboard`, `/calendar`, `/reports` | Review site work, calendar issues and readiness | GM can monitor and intervene where authorised |  |  |
| Private intake | Programming Head | `/programming` | Create/open intake, start review, approve/defer/decline/request changes as authorised | Intake records visible to Programming; raw intake hidden from departments |  |  |
| Workspace conversion | Programming Head | `/programming`, `/workspaces/[id]` | Convert approved request into Workspace | Workspace opens with tabs and linked operational data |  |  |
| Calendar | Internal users | `/calendar` | View holds/slots/issues; create and resolve issue | Calendar uses real backend data; issue lifecycle works |  |  |
| Calendar double-booking | Programming Head | `/calendar`, API-assisted if needed | Attempt overlapping confirmed Tene Theatre booking | `409` conflict, CalendarIssue and Audit Trail entry |  |  |
| Calendar different venue | Programming Head | `/calendar`, API-assisted if needed | Attempt Tumisho Theatre booking at same time as Tene Theatre | Allowed because venue differs |  |  |
| Calendar non-overlap | Programming Head | `/calendar`, API-assisted if needed | Attempt Tene Theatre 11:00 start after 09:00-11:00 booking | Allowed unless setup/strike buffer overlaps |  |  |
| Calendar blackout/capacity | Programming Head / GM | `/calendar`, API-assisted if needed | Attempt confirmed event during blackout or over capacity | Blackout blocks; capacity warning/block is recorded |  |  |
| Marketing | Head of Marketing and Communications | `/marketing`, `/workspaces/[id]` | Manage campaign/deliverables, upload evidence, respond to executive action | Marketing can edit own records; raw intake not visible |  |  |
| Technical | Technical Head | `/technical`, `/calendar`, `/workspaces/[id]` | Manage rider, crew/equipment and technical blockers | Technical readiness is visible; Programming holds are not editable by default |  |  |
| FOH / Operations | FOH Head | `/operations`, `/calendar`, `/workspaces/[id]` | Manage FOH plan, checklist and incidents | FOH close-out and incidents are tracked and audited |  |  |
| Contracts | Contracts / Legal Head | `/contracts`, `/workspaces/[id]` | Create contract, review, sign, lock final document | Contract status/readiness updates |  |  |
| Suppliers / SCM | SCM / Finance Head | `/suppliers`, `/workspaces/[id]` | Verify docs, create engagement/payment pack | Supplier readiness and payment blockers update |  |  |
| Artists | Artist Management | `/artists`, `/workspaces/[id]` | Verify artist docs, link engagement and contract | Artist readiness updates; fee sensitivity checked manually |  |  |
| Ticketing | Ticketing Head | `/ticketing`, `/workspaces/[id]` | Set provider, booking link, sales import and settlement | Ticketing tracks evidence, not live ticketing sync |  |  |
| Youth | Youth Development Head | `/youth`, `/workspaces/[id]` | Manage project, sessions, consent, attendance, assessment | Youth summary updates and sensitive data remains controlled |  |  |
| Governance / M&E | Governance Head | `/governance`, `/governance/risks`, `/reports` | Create risk, KPI, corrective action and evidence | Governance reporting and Board Summary update |  |  |
| Documents & Evidence | Department users | `/documents`, `/workspaces/[id]` | Upload, download, submit evidence, accept/reject | Real files work; rejection requires reason; missing evidence blocks completion |  |  |
| Approvals and Process | Approver / Executive | `/approvals`, `/workspaces/[id]` | Decide approvals and complete Process steps | Evidence and approval-required steps block until satisfied |  |  |
| Executive actions | Executive and assigned department head | `/governance`, `/workspaces/[id]` | Request change, department acknowledges and completes | Department sees instruction; lifecycle is audited |  |  |
| Reports | Executive, GM, Board | `/reports` | Open all report cards and selected Workspace/Department/Youth reports | Reports load real data and respect permissions |  |  |
| Audit Trail | Executive / Admin / Manager | `/audit` | Review recent critical actions | Audit Trail shows actor/action/target/time |  |  |
| Read-only / Board | Board user | `/dashboard`, `/reports` | View summaries, attempt mutation | Summary visible; backend blocks mutation |  |  |
| Client external | Client user | `/programming` if available to client, or API | Submit intake and view own request status only | Client cannot see internal operations |  | Client UI may be limited |
| Supplier external | Supplier user | `/suppliers` if available | View own supplier data only | Other suppliers and internal operations are hidden |  | Upload portal remains limited unless enabled |
| Artist external | Artist user | `/artists` if available | View own artist data only | Other artists and unrelated contracts are hidden |  | Upload portal remains limited unless enabled |

## Negative Permission Tests

| Test | User | Route/API | Expected |
| --- | --- | --- | --- |
| Marketing tries raw intake | Marketing Head | `/api/v1/programming/intake-requests/` | Backend must not leak private intake unless authorised |
| Technical edits Programming hold | Technical Head | `/api/v1/programming/venue-holds/{id}/` | Mutation blocked unless authorised |
| Marketing edits Programming hold | Marketing Head | `/api/v1/programming/venue-holds/` | `403`, Programming owns venue scheduling |
| Board edits Calendar | Board user | `/api/v1/programming/venue-holds/` or `/calendar-slots/` | `403` |
| Read-only approves | Board user | `/api/v1/approvals/requests/{id}/approve/` | `403` |
| Supplier sees another supplier | Supplier external | `/api/v1/suppliers/` | Own records only |
| Artist sees another artist | Artist external | `/api/v1/artists/` | Own records only |
| Wrong tenant downloads file | Any user from other tenant | `/api/v1/documents/{id}/download/` | `404` |
| Missing evidence completion | Department user | `/api/v1/tasks/{id}/complete/` | `422` for evidence-required task without accepted evidence |
| Department cancels executive action | Staff user | `/api/v1/governance/executive-actions/{id}/cancel/` | `403` |

## Known UAT Boundaries

These are not failures of the current MVP unless your pilot requires them:

- No live Microsoft 365, SharePoint, WordPress, ticketing provider, SAP/ERP, CSD, e-signature, Power BI or billing integration.
- External client/supplier/artist portals are limited. Backend external restrictions exist, but full portal self-service should be treated as later scope.
- Browser UAT must still confirm role-specific sidebar visibility and non-technical usability.
- Production deployment, backups, monitoring, restore testing and staging sign-off remain separate pilot-readiness gates.

## Sprint 4 Test Layers

### Technical/API tests

Run:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py seed_dev_data
.\.venv\Scripts\python.exe manage.py seed_dev_data
.\.venv\Scripts\python.exe -m pytest -q
```

Calendar hardening is covered by `tests/programming/test_calendar_hardening.py`.

### Browser/manual UAT

Run the backend and frontend locally, then log in through `http://localhost:3000/login`.

Required role smoke checks:

- `marketing.manager@moukangwetheatre.test`: Marketing dashboard, Marketing navigation, assigned-team work, cannot approve Technical, cannot edit Programming holds.
- `designer@moukangwetheatre.test`: assigned artwork work, no approval authority.
- `technical.manager@moukangwetheatre.test`: Technical dashboard, Technical approval authority only.
- `foh.manager@moukangwetheatre.test`: FOH / Operations dashboard and no Technical rider ownership.
- `board@moukangwetheatre.test`: reports/read-only dashboard, no create/edit/approve/upload buttons.
- `client@moukangwetheatre.test`: client dashboard/request area only, no internal dashboard.
- `supplier@moukangwetheatre.test`: supplier area only, no internal reports or audit.
- `artist@moukangwetheatre.test`: artist area only, no unrelated contracts or internal reports.

### Security/negative tests

Use direct API calls to prove backend enforcement for cross-department approvals, calendar mutation, read-only mutation, external access and wrong-tenant access. Frontend hiding is not sufficient evidence.

### Known limitations

- Executive calendar override is deferred. Confirmed conflicts are blocked without override.
- Full browser E2E automation is not yet installed as an npm script.
- Production readiness still requires deployment, monitoring, backups, cloud storage, security review, production email/notification handling, rate limiting and support processes.

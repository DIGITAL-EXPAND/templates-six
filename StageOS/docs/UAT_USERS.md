# Moukangwe Theatre UAT Users

Run this seed before manual testing:

```powershell
.\.venv\Scripts\python.exe manage.py seed_dev_data
```

The command is idempotent and seeds one realistic theatre organisation for UAT.

## Theatre Structure

| Level | Name |
| --- | --- |
| Organisation / theatre group | Moukangwe Theatre |
| Primary site | Moukangwe Theatre Complex |

## Venues And Spaces

| Venue / space | Type represented in current model | Capacity | UAT purpose |
| --- | --- | --- | --- |
| Tene Theatre | Performance | 600 | Main performance venue and main stage UAT scenario |
| Tumisho Theatre | Performance | 350 | Secondary venue booking scenario |
| Koketso Theatre | Performance / studio space | 150 | Workshop and smaller venue scenario |
| Dikeledi Restaurant | Other venue / restaurant space | 120 | Hospitality and visitor experience support |
| Moukangwe Foyer | Multipurpose / foyer space | 200 | Stakeholder reception and foyer events |
| Rehearsal Room | Rehearsal / workshop space | 80 | Youth sessions, workshops and training |

The current data model has `Venue` and `Space` records. The seed creates a venue and a matching primary space for each row above. There is no dedicated `main venue` flag in the current model, so Tene Theatre is identified as the main venue by name, description and seeded use.

## Departments

| Department | Current department type |
| --- | --- |
| Executive Office | executive |
| Programming | programming |
| Marketing and Communications | marketing |
| Technical and Stage Management | technical |
| FOH / Operations | operations |
| Contracts / Legal | contracts |
| SCM / Finance | finance |
| Ticketing / Audience Coordination | ticketing |
| Youth Development | youth |
| Governance / M&E | governance |
| Hospitality / Restaurant Operations | operations |

The current operating model stores organisation, department, position and authority through `UserDepartmentMembership`. Department assignment is no longer inferred from email alone. Use `/api/v1/me/operating-profile/` to confirm a user's primary department, position, authority level, manageable departments, approvable departments and enabled modules.

## Password

All UAT users use:

```text
MoukangweTest123!
```

## Users And Role Mapping

| Journey | Email | user_type | Department | Position | Authority | Expected dashboard | Allowed actions | Blocked actions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Admin | admin@moukangwetheatre.test | internal_admin | Executive Office | System Administrator | executive/admin | Admin | Manage settings, users, structure and operational records | Cross-tenant access |
| CEO | ceo@moukangwetheatre.test | executive | Executive Office | Chief Executive Officer | executive | Executive | Organisation oversight, reports, audit, executive action and authorised approvals | Silent unaudited overwrite; cross-tenant access |
| COO | coo@moukangwetheatre.test | executive | Executive Office | Chief Operating Officer | executive | Executive | Operational oversight, reports, audit, intervention and authorised approvals | Silent unaudited overwrite; cross-tenant access |
| GM | gm@moukangwetheatre.test | manager | Executive Office | General Manager | gm | GM | Site readiness, calendar issues, reports and authorised intervention | Cross-tenant access; admin-only configuration where restricted |
| Board | board@moukangwetheatre.test | read_only | Executive Office | Board Member / Read-only Oversight | read_only | Board | View board summary, reports and authorised read-only summaries | Create, edit, approve, upload, delete or assign |
| Read-only | readonly@moukangwetheatre.test | read_only | Executive Office | Read-only User | read_only | Board | View authorised summaries and reports | Create, edit, approve, upload, delete or assign |
| Client external | client@moukangwetheatre.test | client_external | External | Client | external | Client | Submit/view own request where surface exists | Internal dashboards, private review notes and other client records |
| Supplier external | supplier@moukangwetheatre.test | supplier_external | External | Supplier | external | Supplier | View own supplier area where surface exists | Other suppliers, internal SCM notes and internal operations |
| Artist external | artist@moukangwetheatre.test | artist_external | External | Artist | external | Artist | View own artist area where surface exists | Other artists, unrelated contracts and internal reports |

## Department Test Users

| Department | Manager/head | Standard user | Expected allowed work | Expected blocked work |
| --- | --- | --- | --- | --- |
| Programming | programming.manager@moukangwetheatre.test | programming.user@moukangwetheatre.test | Private intake, venue holds, programming handoff and Workspace conversion where authorised | Editing department-owned records outside authority |
| Marketing and Communications | marketing.manager@moukangwetheatre.test | marketing.user@moukangwetheatre.test | Campaigns, deliverables, artwork evidence and executive action response | Raw intake by default; Technical or FOH edits |
| Technical and Stage Management | technical.manager@moukangwetheatre.test | technical.user@moukangwetheatre.test | Riders, crew, equipment, load-in, strike and incidents | Raw intake by default; Programming hold edits |
| FOH / Operations | foh.manager@moukangwetheatre.test | foh.user@moukangwetheatre.test | FOH plans, checklist, show-day readiness and incidents | Raw intake by default; Technical rider edits |
| Contracts / Legal | contracts.manager@moukangwetheatre.test | contracts.user@moukangwetheatre.test | Contracts, signature status, signed document checks | Unauthorised finance/admin actions |
| SCM / Finance | scm.manager@moukangwetheatre.test | scm.user@moukangwetheatre.test | Suppliers, CSD readiness, payment packs and ERP references | Unauthorised artist/contract edits |
| Ticketing / Audience Coordination | ticketing.manager@moukangwetheatre.test | ticketing.user@moukangwetheatre.test | Ticketing setup, booking link, comps, sales imports and settlement evidence | Raw intake by default; Programming hold edits |
| Youth Development | youth.manager@moukangwetheatre.test | youth.user@moukangwetheatre.test | Youth projects, sessions, consent, attendance, assessments and showcases | Sensitive youth access by unauthorised users |
| Governance / M&E | governance.manager@moukangwetheatre.test | governance.user@moukangwetheatre.test | Risks, KPIs, corrective actions and evidence | Department edits outside authority |
| Hospitality / Restaurant Operations | hospitality.manager@moukangwetheatre.test | hospitality.user@moukangwetheatre.test | Dikeledi Restaurant hospitality support through FOH/governance-linked records | Private intake and unrelated department records |

## Manual Login Order

1. `admin@moukangwetheatre.test`
2. `ceo@moukangwetheatre.test`
3. `coo@moukangwetheatre.test`
4. `gm@moukangwetheatre.test`
5. Department manager users, one by one
6. `client@moukangwetheatre.test`
7. `supplier@moukangwetheatre.test`
8. `artist@moukangwetheatre.test`
9. `board@moukangwetheatre.test`
10. `readonly@moukangwetheatre.test`

## Demo Records Seeded

| Area | Seeded record |
| --- | --- |
| Intake | Venue Booking Request: Moukangwe Community Concert at Tene Theatre |
| Production Workspace | The Main Stage Production at Tene Theatre |
| Secondary booking Workspace | Tumisho Theatre Comedy Night |
| Workshop Workspace | Koketso Theatre Workshop Series |
| Youth Workspace | Moukangwe Youth Development Programme in Rehearsal Room |
| Hospitality / FOH | FOH hospitality notes linked to Dikeledi Restaurant support |
| Foyer / stakeholder event | Stakeholder Reception at Moukangwe Foyer |
| Calendar | Venue holds and confirmed slots for Tene, Tumisho and Koketso; one Tene Theatre calendar issue |
| Marketing | Campaign and poster artwork deliverable |
| Technical | Technical rider, crew requirement and equipment requirement |
| FOH / Operations | FOH plan, checklist item and incident |
| Contracts | Signed artist performance contract with locked signed document metadata |
| Suppliers / SCM | Supplier, CSD document, engagement and payment pack |
| Artists | Artist profile, verified artist document and engagement |
| Ticketing | Webtickets-style setup and sales import evidence |
| Youth | Activity, session, facilitator, learner group, consent, attendance, assessment and showcase |
| Governance | KPI, KPI evidence, risk, corrective action and executive action |

## UAT Notes

Use the seed to prove realistic theatre journeys, not production deployment. External supplier and artist access is limited by the current product surface and should be tested as restricted access unless a specific portal workflow exists. Department-specific permission checks should focus on backend blocking, frontend route visibility, executive action visibility and department-owned seeded records.

## Sprint 4 Calendar UAT Records

The seed also supports final UAT calendar checks:

| Venue | Seeded purpose | Expected test |
| --- | --- | --- |
| Tene Theatre | Confirmed main production with setup and strike buffers | Overlapping confirmed booking is blocked |
| Tumisho Theatre | Confirmed secondary performance | Same-time booking in a different venue is allowed |
| Koketso Theatre | Provisional workshop | Provisional overlap creates a warning issue |
| Dikeledi Restaurant | Hospitality support event | Hospitality calendar support appears in UAT data |
| Moukangwe Foyer | Stakeholder reception | Foyer event appears in calendar/report UAT |
| Rehearsal Room | Youth class/session | Youth/rehearsal activity appears in calendar UAT |

Calendar conflict rules for manual UAT:

- Same venue, overlapping confirmed occupation windows are blocked.
- Same venue, non-overlapping times are allowed.
- Different venues at the same time are allowed.
- Setup and strike buffers expand the occupied window.
- Maintenance, blackout, venue unavailable and dark-day slots block confirmed events.
- Capacity above venue capacity creates a warning; more than 10 percent over capacity is blocked.
- Executive override is intentionally deferred. Confirmed conflicts are blocked without override.

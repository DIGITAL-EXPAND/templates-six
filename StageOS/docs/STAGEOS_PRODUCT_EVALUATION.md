# StageOS Product Evaluation

StageOS is positioned well as a theatre operating system: it already models the core journey from private intake to approval, Workspace conversion, department execution, evidence, calendar, reports and audit. The strongest product direction is to make StageOS feel like a daily control room for each department, not a generic admin dashboard with theatre labels.

## Departmental Operating Model

| Department | Primary accountability | StageOS surface | Key handoffs |
| --- | --- | --- | --- |
| Executive / CEO / COO | Strategic decisions, escalations, audit confidence and board readiness | Dashboard, Approvals, Governance, Reports, Audit Trail | Programming decisions, executive actions, risk acceptance, board packs |
| General Manager / Site Manager | Site readiness, cross-department blockers and show-week execution | Dashboard, Calendar, Workspaces, Reports, My Work | Venue readiness, department blockers, incident escalation |
| Programming | Private intake, artistic fit, venue holds, approval recommendations and Workspace conversion | Programming, Calendar, Workspaces | Intake to leadership, approved work to departments, calendar conflicts to GM |
| Marketing and Communications | Campaign planning, public assets, PR, social media, evidence and launch readiness | Marketing, Workspaces, Documents, My Work | Approved Workspace from Programming, artwork and copy approvals, evidence to Governance |
| Technical / Stage Management | Riders, equipment, crew, load-in, strike, technical risks and technical sign-off | Technical, Calendar, Workspaces, Documents | Workspace readiness from Programming, risk/issues to GM, evidence to Documents |
| FOH / Operations | Audience flow, ushers, accessibility, safety, incidents and show-day close-out | Operations, Calendar, Workspaces, Documents | Event schedule from Calendar, incidents to Governance, close-out to Reports |
| Contracts / Legal | Contract drafting, review gates, signatures, locks and expiry monitoring | Contracts, Approvals, Documents | Artist/supplier records, executive approvals, signed documents to evidence |
| SCM / Finance / Suppliers | Supplier verification, CSD checks, payment packs and procurement readiness | Suppliers, Contracts, Documents, Reports | Supplier docs from portal, finance blockers to GM, payment pack evidence |
| Artist Management | Artist records, documents, engagements, contract readiness and communication | Artists, Contracts, Documents | Contract requests to Legal, document gaps to artist portal, readiness to Workspace |
| Ticketing | Ticket setup, provider links, comps, sales imports, settlements and ticketing evidence | Ticketing, Reports, Documents | Calendar/Workspace event details, settlement evidence to Finance and Reports |
| Youth Development | Youth programmes, consent, attendance, assessments, safeguarding and showcases | Youth, Documents, Governance | Consent evidence, safeguarding escalations, outcomes to M&E |
| Governance / M&E | Risk register, KPIs, corrective actions, evidence quality and board reporting | Governance, Reports, Audit Trail | Department evidence, executive actions, KPI packs and board summaries |
| Internal Admin | Tenant, site, venue, department, user and permission configuration | Settings, Audit Trail | User setup, department mapping, venue/site governance |
| External clients, suppliers and artists | Submit and maintain only their own records | Limited portal views | Requests, supplier documents, artist documents and notifications |

## Recommended Workflow Architecture

1. Intake and privacy gate

   Client or internal requester submits a request. Programming is the only department that should see raw intake details by default. StageOS should show Programming a clean queue: new, in review, changes requested, recommended, approved, declined and converted.

2. Leadership decision gate

   Executive, COO or GM decides whether the proposal proceeds. Decisions should require structured outcomes and comments for decline, defer or changes requested. The decision creates an audit event and unlocks Workspace conversion.

3. Workspace conversion

   Approved intake becomes a Workspace exactly once. The Workspace is the operating container for all departments. It should show dates, venue, risk, readiness, evidence, approvals, blockers and department ownership in one place.

4. Department execution

   Each department works from its own queue, but every task links back to the Workspace. The product should make ownership obvious: assigned to me, assigned to my department, blocked, overdue, waiting for approval and ready for sign-off.

5. Evidence and approval controls

   StageOS should keep the rule: no evidence, no completion where evidence is required. Approvals should be visible as gates, not hidden API states. Users need to see what is blocking progress and who can unblock it.

6. Calendar and venue protection

   Calendar is a control surface, not just a date list. It should clearly distinguish confirmed holds, provisional holds, blackout windows, capacity warnings, blocked conflicts and issue status.

7. Reporting and audit

   Reports should answer management questions: what is opening soon, what is blocked, what lacks evidence, what is risky, what needs approval, what is board-ready and what changed recently. Audit Trail should remain the trust layer.

## Priority User Journeys

| Journey | Primary user | Current readiness | Recommended frontend improvement |
| --- | --- | --- | --- |
| Sign in and land on the right dashboard | All users | Present | Make the dashboard clearly role-specific with a stronger top-level action area |
| Review private intake and create a Workspace | Programming Head | Core path documented | Add a visual pipeline and conversion checklist |
| Resolve department blockers before opening night | GM / Department Heads | Metrics exist | Add a cross-department blocker board by Workspace and due date |
| Complete evidence-backed department work | Department staff | Backend rules exist | Show evidence requirements inline on tasks and completion buttons |
| Approve or reject a gate | Executive / approver | Present | Add an approvals inbox with impact, requester, due date and linked evidence |
| Manage venue conflicts | Programming / GM | Backend checks exist | Show conflicts as calendar issue cards with clear next action |
| Prepare board pack | Executive / Governance | Reports exist | Add a Board Readiness view: risks, KPIs, evidence gaps, unresolved actions |
| Supplier or artist completes own documents | External users | Limited | Add narrow portal dashboards with only their records, status and missing documents |
| Close out show day | FOH / Operations | Supported by incidents/checklists | Add a close-out checklist and incident summary panel on Workspace |

## Frontend Rework Direction

The frontend should feel like an operations cockpit: restrained, dense, fast to scan and action-led. Recommended changes:

- Keep the left navigation role-aware, but make the active module and group labels stronger.
- Make the topbar sticky, with user identity, role, search and notifications visible without taking space from the work area.
- Replace generic white panels with a consistent surface system: flat white, subtle borders, compact radius, strong focus states.
- Make dashboard sections answer action questions: what needs my decision, what is blocked, what is due, what changed, what is at risk.
- Keep mobile navigation simple: menu button, compact title, notifications and sign out.
- Avoid marketing-style hero composition inside the application. The app should prioritize scanning, comparison and repeated action.

## Suggested Next Product Build

1. Workspace Command View: one page with readiness by department, blockers, evidence gaps, approvals and recent audit.
2. My Work Queue: unified task, approval, evidence and notification queue filtered by role.
3. Department Boards: marketing, technical, FOH, contracts, suppliers, artists, ticketing, youth and governance each receive queue + readiness + evidence.
4. Calendar Conflict Center: blocked conflicts, provisional overlaps, blackouts and capacity warnings with owner and next action.
5. External Portal MVP: client request status, supplier document status and artist engagement/document status.

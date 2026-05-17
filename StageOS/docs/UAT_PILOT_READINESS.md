# StageOS UAT / Pilot Readiness Checklist

Use this checklist to prove StageOS as a controlled MVP pilot before production use.

## Quality Gates

- Backend migrations check passes.
- Backend system check passes.
- Full backend test suite passes.
- Frontend typecheck passes.
- Frontend lint passes.
- Frontend production build passes.

## Core Journey

- Intake request is submitted and remains private to authorised users.
- Programming reviews the request and records a recommendation.
- Leadership approves, declines, requests changes or asks for more information.
- Approved request converts to a Workspace.
- Calendar hold or confirmed calendar item is visible to authorised users.
- Department tasks are created and linked to the Workspace.
- Department users complete owned work without editing another department's records.
- Required evidence blocks completion until uploaded or linked.
- Approvals block dependent completion until decided.
- Executive intervention creates visible actions and Audit Trail events.
- Workspace readiness shows blockers, risks, approvals, calendar issues and evidence gaps.
- Close-out evidence and statuses are recorded.

## Reports To Validate

- Executive Summary.
- Board Summary.
- Workspace Readiness.
- Department Readiness.
- Youth Summary.
- Risk Register.
- Contract Status.
- Supplier Readiness.
- Evidence Gaps.
- Calendar Issues.
- Audit Trail export.

## Pilot Exit Criteria

- A non-technical internal user can complete the core journey using the frontend.
- Backend permissions block unauthorised direct API access.
- Tenant isolation is proven for reports and operating records.
- Audit Trail can prove who acted, when, on what record and why where reasons are required.
- Reports answer: what is happening, what is blocked, who owns it, what evidence exists and what is ready.

## Known Non-MVP Scope

- Live WordPress publishing.
- Live ticketing provider sync.
- Microsoft 365 or SharePoint sync.
- SAP/ERP sync.
- CSD direct integration.
- E-signature provider integration.
- Billing and subscriptions.

// Theatre-friendly labels for all backend concepts

export const PRODUCTION_LABELS = {
  singular: 'Production',
  plural: 'Productions',
  new: 'New Production',
  types: {
    production: 'Theatre Production',
    venue_rental: 'Venue Hire',
    co_production: 'Co-Production',
    youth_project: 'Youth Programme',
    festival: 'Festival',
    conference: 'Conference',
    private_event: 'Private Event',
    other: 'Other',
  },
  statuses: {
    draft: 'Draft',
    active: 'In Progress',
    hold: 'On Hold',
    cancelled: 'Cancelled',
    completed: 'Completed',
  },
} as const;

export const TASK_LABELS = {
  singular: 'Action',
  plural: 'Actions',
  new: 'Add Action',
  statuses: {
    open: 'To Do',
    in_progress: 'In Progress',
    blocked: 'Stuck — Needs Help',
    done: 'Done',
    cancelled: 'Cancelled',
  },
  statusShort: {
    open: 'To Do',
    in_progress: 'In Progress',
    blocked: 'Stuck',
    done: 'Done',
    cancelled: 'Cancelled',
  },
  priorities: {
    critical: 'Urgent',
    high: 'High',
    medium: 'Normal',
    low: 'Low',
  },
  workTypes: {
    general: 'General',
    readiness: 'Show Readiness',
    evidence: 'File Required',
    approval_prep: 'For Sign-Off',
    issue_response: 'Issue Response',
    follow_up: 'Follow-Up',
  },
  actions: {
    start: 'Start Working',
    block: "I'm Stuck",
    complete: 'Mark as Done',
    cancel: 'Cancel',
    reopen: 'Reopen',
    assign: 'Assign To',
    comment: 'Add Note',
    upload: 'Upload File',
  },
  evidenceRequired: 'A file must be uploaded before this can be marked done',
  noTasks: 'No actions here yet',
  myTasksEmpty: "You're all caught up — no actions assigned to you",
};

export const APPROVAL_LABELS = {
  singular: 'Sign-Off',
  plural: 'Sign-Offs',
  new: 'Request Sign-Off',
  decisions: {
    pending: 'Awaiting Decision',
    approved: 'Approved',
    rejected: 'Not Approved',
    changes_requested: 'Changes Needed',
    escalated: 'Escalated',
    exception_approved: 'Exception Approved',
    cancelled: 'Cancelled',
  },
  actions: {
    approve: 'Approve',
    reject: 'Decline',
    request_changes: 'Request Changes',
    escalate: 'Escalate',
    exception_approve: 'Exception Approve',
  },
};

export const EVIDENCE_LABELS = {
  singular: 'Supporting File',
  plural: 'Supporting Files',
  upload: 'Upload File',
  accepted: 'Accepted',
  rejected: 'Returned — See Reason',
  pending: 'Awaiting Review',
  actions: {
    accept: 'Accept File',
    reject: 'Return with Reason',
  },
  uploadHint: 'Drag & drop a file or click to browse',
  rejectionReasonLabel: 'Reason for returning this file',
};

export const CONTRACT_LABELS = {
  singular: 'Agreement',
  plural: 'Agreements',
  new: 'New Agreement',
  statuses: {
    draft: 'Draft',
    legal_review: 'Legal Review',
    finance_review: 'Finance Review',
    scm_review: 'SCM Review',
    issued: 'Issued',
    counter_signed: 'Counter-Signed',
    signed: 'Fully Signed',
    expired: 'Expired',
    cancelled: 'Cancelled',
  },
};

export const SUPPLIER_LABELS = {
  singular: 'Supplier',
  plural: 'Suppliers',
  statuses: {
    documents_incomplete: 'Documents Incomplete',
    pending_verification: 'Pending Verification',
    ready: 'Ready to Engage',
    suspended: 'Suspended',
    blacklisted: 'Blacklisted',
  },
};

export const ARTIST_LABELS = {
  singular: 'Performer',
  plural: 'Performers',
  statuses: {
    documents_incomplete: 'Documents Incomplete',
    contract_ready: 'Contract Ready',
    contracted: 'Contracted',
    payment_ready: 'Payment Ready',
  },
  engagementStatuses: {
    proposed: 'Proposed',
    confirmed: 'Confirmed',
    contracted: 'Contracted',
    performed: 'Performed',
    cancelled: 'Cancelled',
  },
};

export const CALENDAR_LABELS = {
  venueHold: 'Venue Booking',
  venueHolds: 'Venue Bookings',
  calendarSlot: 'Performance Date',
  calendarSlots: 'Performance Dates',
  issue: 'Schedule Problem',
  issues: 'Schedule Problems',
  holdTypes: {
    provisional: 'Provisional Hold',
    confirmed: 'Confirmed',
    blocked: 'Blocked Out',
  },
  issueSeverity: {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    critical: 'Critical',
  },
};

export const WORKFLOW_LABELS = {
  instance: 'Progress Checklist',
  step: 'Checklist Step',
  statuses: {
    pending: 'Not Started',
    in_progress: 'In Progress',
    completed: 'Complete',
    skipped: 'Skipped',
    blocked: 'Stuck',
  },
};

export const NOTIFICATION_LABELS = {
  types: {
    task_assigned: 'New action assigned to you',
    task_updated: 'Action updated',
    task_blocked: 'Action is stuck',
    task_completed: 'Action completed',
    department_issue: 'Department issue raised',
    evidence_rejected: 'Your file was returned',
    approval_decided: 'Sign-off decision made',
  },
};

export const DEPARTMENT_LABELS: Record<string, string> = {
  PROGRAMMING: 'Programming',
  MARKETING: 'Marketing',
  TECHNICAL: 'Technical',
  OPERATIONS: 'Front of House',
  FINANCE: 'Finance',
  CONTRACTS: 'Contracts',
  TICKETING: 'Box Office',
  YOUTH: 'Youth & Education',
  GOVERNANCE: 'Governance',
  EXECUTIVE: 'Executive',
  ICT: 'ICT',
};

export const ROLE_LABELS: Record<string, string> = {
  internal_admin: 'System Administrator',
  executive: 'Executive',
  manager: 'Manager',
  staff: 'Team Member',
  read_only: 'View Only',
  supplier_external: 'Supplier',
  artist_external: 'Performer',
  client_external: 'Client',
  youth_external: 'Youth Programme Participant',
  integration_service: 'Integration Service',
};

export const AUTHORITY_LABELS: Record<string, string> = {
  executive: 'Executive',
  gm: 'General Manager',
  department_manager: 'Department Manager',
  department_user: 'Team Member',
  specialist: 'Specialist',
  read_only: 'View Only',
  external: 'External',
};

export const DASHBOARD_LABELS: Record<string, { heading: string; subheading: string }> = {
  admin: { heading: 'System Overview', subheading: 'Full system access' },
  executive: { heading: 'Executive Overview', subheading: 'Organisation-wide performance' },
  gm: { heading: 'Operations', subheading: 'Site operations overview' },
  programming: { heading: 'Programming', subheading: 'Show pipeline & scheduling' },
  marketing: { heading: 'Marketing', subheading: 'Campaigns & publicity' },
  technical: { heading: 'Technical', subheading: 'Production technical requirements' },
  foh: { heading: 'Front of House', subheading: 'Show-day operations' },
  contracts: { heading: 'Contracts', subheading: 'Agreements & signatures' },
  scm: { heading: 'Supply Chain', subheading: 'Suppliers & procurement' },
  ticketing: { heading: 'Box Office', subheading: 'Ticket sales & settlement' },
  youth: { heading: 'Youth & Education', subheading: 'Programmes & participants' },
  governance: { heading: 'Governance', subheading: 'Performance & oversight' },
  hospitality: { heading: 'Hospitality', subheading: 'VIP & hospitality plans' },
  board: { heading: 'Board View', subheading: 'Organisational summary' },
  client: { heading: 'My Productions', subheading: 'Your show proposals & updates' },
  supplier: { heading: 'My Engagements', subheading: 'Your supplier profile & work' },
  artist: { heading: 'My Engagements', subheading: 'Your performer profile & contracts' },
  generic: { heading: 'My Work', subheading: 'Your actions & files' },
};

export const INTAKE_LABELS = {
  singular: 'Show Proposal',
  plural: 'Show Proposals',
  new: 'Submit a Proposal',
  statuses: {
    submitted: 'Submitted',
    under_review: 'Under Review',
    changes_requested: 'Changes Requested',
    deferred: 'Deferred',
    approved: 'Approved',
    declined: 'Declined',
    converted: 'Converted to Production',
    archived: 'Archived',
  },
};

export const GOVERNANCE_LABELS = {
  kpi: 'Performance Goal',
  kpis: 'Performance Goals',
  risk: 'Risk Item',
  risks: 'Risk Register',
  correctiveAction: 'Corrective Action',
  executiveAction: 'Leadership Note',
  riskLevels: {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    critical: 'Critical',
  },
};

export const YOUTH_LABELS = {
  project: 'Youth Programme',
  activity: 'Activity',
  session: 'Session',
  learnerGroup: 'Learner Group',
  facilitator: 'Facilitator',
  consent: 'Consent Record',
  attendance: 'Attendance',
  assessment: 'Assessment',
  showcase: 'Showcase',
};

export const MARKETING_LABELS = {
  campaign: 'Publicity Campaign',
  deliverable: 'Campaign Task',
  deliverableStatuses: {
    pending: 'Not Started',
    planning: 'Planning',
    in_progress: 'In Progress',
    review: 'Under Review',
    complete: 'Complete',
    cancelled: 'Cancelled',
  },
};

export const TECHNICAL_LABELS = {
  rider: 'Technical Requirements',
  crew: 'Crew Requirement',
  equipment: 'Equipment Requirement',
  riderStatuses: {
    draft: 'Draft',
    submitted: 'Submitted',
    under_review: 'Under Review',
    approved: 'Approved',
    rejected: 'Returned',
  },
};

export const OPERATIONS_LABELS = {
  fohPlan: 'Front of House Plan',
  checklist: 'Show Day Checklist',
  incident: 'Incident Report',
  fohStatuses: {
    planning: 'Planning',
    confirmed: 'Confirmed',
    active: 'Show Day Active',
    closed: 'Closed',
  },
};

export const TICKETING_LABELS = {
  setup: 'Box Office Setup',
  salesImport: 'Sales Import',
  setupStatuses: {
    awaiting_setup: 'Setting Up',
    in_progress: 'In Progress',
    live: 'Live',
    closed: 'Closed',
  },
  settlementStatuses: {
    pending: 'Pending',
    in_progress: 'In Progress',
    settled: 'Settled',
    not_applicable: 'N/A',
  },
};

export const NAV_LABELS = {
  home: 'Home',
  productions: 'Shows & Events',
  myWork: 'My Actions',
  teamWork: "My Team's Actions",
  calendar: 'Schedule',
  proposals: 'Show Proposals',
  plans: 'Plans',
  performers: 'Performers',
  suppliers: 'Suppliers',
  agreements: 'Agreements',
  boxOffice: 'Box Office',
  youthProgrammes: 'Youth Development',
  frontOfHouse: 'Front of House',
  marketing: 'Marketing & Publicity',
  technical: 'Technical Production',
  governance: 'Performance & Oversight',
  reports: 'Reports',
  activityLog: 'Audit Trail',
  settings: 'Settings',
  signOff: 'Sign-Offs',
  files: 'Files & Evidence',
  hospitality: 'VIP & Hospitality',
};

export type UserRole =
  | 'internal_admin'
  | 'executive'
  | 'manager'
  | 'staff'
  | 'read_only'
  | 'supplier_external'
  | 'artist_external'
  | 'client_external'
  | 'youth_external'
  | 'integration_service';

export type AuthTokens = {
  access: string;
  refresh: string;
};

export type CurrentUser = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  user_type: UserRole;
  is_active: boolean;
  date_joined: string;
};

export type UserListItem = CurrentUser;

export type OperatingProfileDepartment = {
  id: string;
  name: string;
  code?: string;
};

export type OperatingProfilePosition = {
  id: string;
  title: string;
  authority_level: string;
};

export type OperatingProfile = {
  user: {
    id: string;
    email: string;
    user_type: UserRole;
  };
  organisation: {
    id: string;
    name: string;
  } | null;
  primary_site: {
    id: string;
    name: string;
  } | null;
  primary_department: OperatingProfileDepartment | null;
  primary_position: OperatingProfilePosition | null;
  memberships: {
    id: string;
    site: { id: string; name: string } | null;
    department: OperatingProfileDepartment;
    position: OperatingProfilePosition;
    authority_level: string;
    is_primary: boolean;
    can_manage_department: boolean;
    can_assign_work: boolean;
    can_approve_work: boolean;
    can_view_department_summary: boolean;
    can_raise_department_issue: boolean;
  }[];
  can_manage_departments: OperatingProfileDepartment[];
  can_approve_departments: OperatingProfileDepartment[];
  active_modules: string[];
};

export type OrganisationItem = {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type ApiErrorPayload = {
  detail?: string;
  non_field_errors?: string[];
  [key: string]: unknown;
};

export type ExecutiveKpi = {
  id: string;
  name: string;
  target: string;
  actual: string;
  unit: string;
  percentage: number;
};

export type UpcomingOpening = {
  id: string;
  title: string;
  opening_date: string;
  days_until: number;
};

export type ExecutiveSummary = {
  total_contexts: number;
  contexts_by_status: Record<string, number>;
  contexts_by_type: Record<string, number>;
  total_budget: string;
  total_spend: string;
  average_readiness: number;
  open_risks: number;
  high_risks: number;
  pending_approvals: number;
  open_tasks: number;
  kpi_summary: ExecutiveKpi[];
  upcoming_openings: UpcomingOpening[];
};

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type SiteListItem = {
  id: string;
  name: string;
  code: string;
  address: string;
  city: string;
  province: string;
  country: string;
  is_active: boolean;
};

export type DepartmentListItem = {
  id: string;
  name: string;
  code: string;
  site: string | null;
  site_name: string | null;
  department_type: string;
  is_active: boolean;
};

export type PositionItem = {
  id: string;
  title: string;
  code: string;
  description: string;
  department: string;
  department_name: string;
  site: string | null;
  site_name: string | null;
  level: string;
  authority_level: string;
  is_active: boolean;
  is_manager_position: boolean;
  is_specialist_position: boolean;
  is_external_position: boolean;
};

export type OperatingModelItem = {
  id: string;
  name: string;
  model_type: string;
  description: string;
  is_active: boolean;
  is_default: boolean;
  configuration: Record<string, unknown>;
};

export type UserDepartmentMembershipItem = {
  id: string;
  user: string;
  user_email: string;
  department: string;
  department_name: string;
  position: string;
  position_title: string;
  authority_level: string;
  is_primary: boolean;
  can_manage_department: boolean;
  can_assign_work: boolean;
  can_approve_work: boolean;
};

export type ModuleActivationItem = {
  id: string;
  module_key: string;
  label: string;
  is_enabled: boolean;
};

export type OperatingContextListItem = {
  id: string;
  title: string;
  context_type: string;
  status: string;
  priority?: string;
  risk_level?: string;
  synopsis?: string;
  site?: string;
  site_detail?: {
    id: string;
    name: string;
    city: string;
  } | null;
  venue_detail?: {
    id: string;
    name: string;
    venue_type: string;
  } | null;
  owner_detail?: {
    id: string;
    email: string;
    full_name: string;
  } | null;
  budget?: string;
  actual_spend?: string;
  readiness_score?: number;
  start_date?: string | null;
  end_date?: string | null;
  opening_date?: string | null;
  closing_date?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type CreateWorkspacePayload = {
  title: string;
  context_type: string;
  site: string;
  owner: string;
  priority?: string;
  risk_level?: string;
  synopsis?: string;
  start_date?: string;
  end_date?: string;
  opening_date?: string;
  closing_date?: string;
  budget?: string;
};

export type IntakeRequestStatus =
  | 'submitted'
  | 'under_review'
  | 'changes_requested'
  | 'deferred'
  | 'approved'
  | 'declined'
  | 'converted'
  | 'archived';

export type IntakeRequestItem = {
  id: string;
  request_type: string;
  status: IntakeRequestStatus;
  event_title: string;
  client_name: string;
  client_organisation: string;
  contact_email: string;
  contact_phone: string;
  requested_start_date: string | null;
  requested_end_date: string | null;
  preferred_venue: string | null;
  expected_audience: number | null;
  ticketing_required: boolean;
  technical_summary: string;
  foh_notes: string;
  accessibility_requirements: string;
  attachments_note: string;
  notes: string;
  submitted_by: string | null;
  reviewed_by: string | null;
  decided_by: string | null;
  decision_comment: string;
  decision_at: string | null;
  converted_context: string | null;
  created_at: string;
  updated_at: string;
};

export type CreateIntakeRequestPayload = {
  request_type: string;
  event_title: string;
  client_name: string;
  client_organisation?: string;
  contact_email?: string;
  contact_phone?: string;
  requested_start_date?: string | null;
  requested_end_date?: string | null;
  preferred_venue?: string | null;
  expected_audience?: number | null;
  ticketing_required?: boolean;
  technical_summary?: string;
  foh_notes?: string;
  accessibility_requirements?: string;
  attachments_note?: string;
  notes?: string;
};

export type VenueHoldItem = {
  id: string;
  operating_context: string;
  venue: string;
  space: string | null;
  hold_date: string;
  hold_type: 'provisional' | 'confirmed' | 'blocked';
    start_time: string | null;
    end_time: string | null;
    setup_buffer_minutes: number;
    strike_buffer_minutes: number;
    expected_audience: number | null;
    purpose: string;
  notes: string;
  held_by: string;
  created_at: string;
  updated_at: string;
};

export type CalendarSlotItem = {
  id: string;
  operating_context: string;
  venue: string;
  date: string;
    slot_type: string;
    is_confirmed: boolean;
    start_time: string | null;
    end_time: string | null;
    setup_buffer_minutes: number;
    strike_buffer_minutes: number;
    expected_audience: number | null;
    created_at: string;
  updated_at: string;
};

export type CalendarIssueStatus = 'open' | 'in_progress' | 'resolved' | 'cancelled';

export type CalendarIssueItem = {
  id: string;
  title: string;
  description: string;
  operating_context: string | null;
  venue_hold: string | null;
  calendar_slot: string | null;
  department: string | null;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: CalendarIssueStatus;
  due_date: string | null;
  raised_by: string;
  resolved_by: string | null;
  resolved_at: string | null;
  resolution_note: string;
  created_at: string;
  updated_at: string;
};

export type CreateCalendarIssuePayload = {
  title: string;
  description?: string;
  operating_context?: string | null;
  venue_hold?: string | null;
  calendar_slot?: string | null;
  department?: string | null;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  due_date?: string | null;
};

export type ExecutiveActionType =
  | 'comment'
  | 'request_change'
  | 'flag_issue'
  | 'flag_risk'
  | 'assign_corrective_action'
  | 'approve'
  | 'decline'
  | 'request_more_information'
  | 'override'
  | 'escalate';

export type ExecutiveActionStatus = 'open' | 'acknowledged' | 'completed' | 'cancelled';

export type ExecutiveActionItem = {
  id: string;
  action_type: ExecutiveActionType;
  status: ExecutiveActionStatus;
  title: string;
  reason: string;
  instruction: string;
  operating_context: string | null;
  target_type: string;
  target_id: string;
  department: string | null;
  assigned_to: string | null;
  due_date: string | null;
  created_by: string;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  completed_by: string | null;
  completed_at: string | null;
  linked_task: string | null;
  linked_risk: string | null;
  linked_corrective_action: string | null;
  created_at: string;
  updated_at: string;
};

export type CreateExecutiveActionPayload = {
  action_type: ExecutiveActionType;
  title: string;
  reason?: string;
  instruction?: string;
  operating_context?: string | null;
  target_type?: string;
  target_id?: string;
  department?: string | null;
  assigned_to?: string | null;
  due_date?: string | null;
};

export type TaskStatus = 'open' | 'in_progress' | 'blocked' | 'done' | 'cancelled';
export type Priority = 'low' | 'medium' | 'high' | 'critical';

export type TaskItem = {
  id: string;
  operating_context: string;
  title: string;
  description: string;
  department: string | null;
  assigned_to: string | null;
  assigned_by: string | null;
  work_type: 'general' | 'readiness' | 'evidence' | 'approval_prep' | 'issue_response' | 'follow_up';
  due_date: string | null;
  priority: Priority;
  status: TaskStatus;
  started_at: string | null;
  blocked_reason: string;
  completed_at: string | null;
  completed_by: string | null;
  evidence_required: boolean;
  evidence_provided: boolean;
  created_at: string;
  updated_at: string;
};

export type CreateTaskPayload = {
  operating_context: string;
  title: string;
  description?: string;
  department?: string | null;
  assigned_to?: string | null;
  work_type?: TaskItem['work_type'];
  due_date?: string | null;
  priority?: Priority;
  evidence_required?: boolean;
};

export type NotificationItem = {
  id: string;
  recipient: string;
  recipient_email: string;
  actor: string | null;
  actor_email: string | null;
  notification_type: 'task_assigned' | 'task_updated' | 'task_blocked' | 'task_completed' | 'department_issue' | 'evidence_rejected' | 'approval_decided';
  title: string;
  message: string;
  task: string | null;
  department: string | null;
  department_name: string | null;
  read_at: string | null;
  created_at: string;
};

export type DocumentItem = {
  id: string;
  operating_context: string;
  title: string;
  document_type: string;
  file_name: string;
  file_size: string;
  mime_type: string;
  storage_ref: string;
  file: string;
  version: number;
  uploaded_by: string;
  is_locked: boolean;
  created_at: string;
  updated_at: string;
};

export type CreateDocumentPayload = {
  operating_context: string;
  title: string;
  document_type: string;
  file_name: string;
  version?: number;
};

export type EvidenceSubmissionItem = {
  id: string;
  operating_context: string;
  task: string | null;
  document: string;
  submitted_by: string;
  submission_note: string;
  accepted: boolean;
  accepted_by: string | null;
  accepted_at: string | null;
  rejected: boolean;
  rejected_by: string | null;
  rejected_at: string | null;
  rejection_reason: string;
  created_at: string;
  updated_at: string;
};

export type CreateEvidencePayload = {
  operating_context: string;
  task?: string | null;
  document: string;
  submission_note?: string;
};

export type ContractStatus =
  | 'draft'
  | 'legal_review'
  | 'finance_review'
  | 'scm_review'
  | 'issued'
  | 'counter_signed'
  | 'signed'
  | 'expired'
  | 'cancelled';

export type ContractTemplateItem = {
  id: string;
  name: string;
  contract_type: string;
  description: string;
  is_active: boolean;
  version: number;
  template_fields: unknown[];
  created_at: string;
  updated_at: string;
};

export type ContractRecordItem = {
  id: string;
  operating_context: string;
  template: string | null;
  contract_type: string;
  counterparty_name: string;
  counterparty_type: string;
  value: string;
  currency: string;
  status: ContractStatus;
  issued_date: string | null;
  effective_date: string | null;
  expiry_date: string | null;
  signatures_required: number;
  signatures_received: number;
  signed_document: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type SignatureRecordItem = {
  id: string;
  contract: string;
  signatory_name: string;
  signatory_role: string;
  signature_type: string;
  signed_at: string | null;
  is_signed: boolean;
  signature_order: number;
  created_at: string;
  updated_at: string;
};

export type SupplierStatus = 'documents_incomplete' | 'pending_verification' | 'ready' | 'suspended' | 'blacklisted';
export type SupplierDocumentStatus = 'missing' | 'uploaded' | 'verified' | 'rejected';
export type SupplierEngagementStatus = 'proposed' | 'confirmed' | 'active' | 'completed' | 'cancelled';
export type PaymentPackStatus = 'awaiting_csd' | 'ready_for_erp' | 'sent_to_erp' | 'paid' | 'rejected';

export type SupplierItem = {
  id: string;
  name: string;
  category: string;
  panel: string;
  csd_number: string;
  csd_verified: boolean;
  csd_verified_by: string | null;
  csd_verified_at: string | null;
  bee_level: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  status: SupplierStatus;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type SupplierDocumentItem = {
  id: string;
  supplier: string;
  document_type: string;
  document: string | null;
  file_name: string;
  status: SupplierDocumentStatus;
  verified_by: string | null;
  verified_at: string | null;
  created_at: string;
  updated_at: string;
};

export type SupplierEngagementItem = {
  id: string;
  supplier: string;
  operating_context: string;
  role: string;
  value: string;
  status: SupplierEngagementStatus;
  created_at: string;
  updated_at: string;
};

export type PaymentPackItem = {
  id: string;
  supplier_engagement: string;
  operating_context: string;
  amount: string;
  status: PaymentPackStatus;
  erp_reference: string;
  submitted_date: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type ArtistStatus = 'documents_incomplete' | 'contract_ready' | 'contracted' | 'payment_ready';
export type ArtistDocumentStatus = 'missing' | 'uploaded' | 'verified' | 'rejected';
export type ArtistEngagementStatus = 'proposed' | 'confirmed' | 'contracted' | 'performed' | 'cancelled';

export type ArtistItem = {
  id: string;
  legal_name: string;
  professional_name: string;
  discipline: string;
  contact_email: string;
  contact_phone: string;
  standard_fee: string;
  status: ArtistStatus;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type ArtistDocumentItem = {
  id: string;
  artist: string;
  document_type: string;
  document: string | null;
  file_name: string;
  status: ArtistDocumentStatus;
  verified_by: string | null;
  verified_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ArtistEngagementItem = {
  id: string;
  artist: string;
  operating_context: string;
  role: string;
  fee: string;
  contract: string | null;
  status: ArtistEngagementStatus;
  created_at: string;
  updated_at: string;
};

export type CampaignStatus = 'planning' | 'active' | 'paused' | 'closed' | 'cancelled';
export type DeliverableStatus = 'pending' | 'planning' | 'in_progress' | 'review' | 'complete' | 'cancelled';

export type CampaignItem = {
  id: string;
  operating_context: string;
  campaign_level: string;
  budget: string;
  status: CampaignStatus;
  owner: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type CampaignDeliverableItem = {
  id: string;
  campaign: string;
  deliverable_type: string;
  title: string;
  owner_name: string;
  due_date: string | null;
  status: DeliverableStatus;
  completed_at: string | null;
  evidence_document: string | null;
  created_at: string;
  updated_at: string;
};

export type RiderStatus = 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected';

export type TechnicalRiderItem = {
  id: string;
  operating_context: string;
  lighting: string;
  sound: string;
  av: string;
  crew_size: number;
  load_in_date: string | null;
  strike_date: string | null;
  status: RiderStatus;
  approved_by: string | null;
  approved_at: string | null;
  special_requirements: string;
  created_at: string;
  updated_at: string;
};

export type CrewRequirementItem = {
  id: string;
  rider: string;
  role: string;
  quantity: number;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type EquipmentRequirementItem = {
  id: string;
  rider: string;
  item: string;
  quantity: number;
  source: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type FohStatus = 'planning' | 'confirmed' | 'active' | 'closed';

export type FohPlanItem = {
  id: string;
  operating_context: string;
  ushers: number;
  security: number;
  cleaning: number;
  vip_count: number;
  accessibility_provisions: string;
  hospitality_notes: string;
  status: FohStatus;
  created_at: string;
  updated_at: string;
};

export type ChecklistItem = {
  id: string;
  foh_plan: string;
  item: string;
  is_checked: boolean;
  checked_by: string | null;
  checked_at: string | null;
  created_at: string;
  updated_at: string;
};

export type IncidentItem = {
  id: string;
  operating_context: string;
  foh_plan: string | null;
  incident_type: string;
  occurred_at: string;
  description: string;
  response: string;
  reported_by: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  created_at: string;
  updated_at: string;
};

export type TicketingSetupItem = {
  id: string;
  operating_context: string;
  provider: string;
  booking_link: string;
  pricing_description: string;
  comps_allocated: number;
  comps_used: number;
  setup_status: 'awaiting_setup' | 'in_progress' | 'live' | 'closed';
  sales_imported: boolean;
  tickets_sold: number;
  tickets_available: number;
  settlement_status: 'pending' | 'in_progress' | 'settled' | 'not_applicable';
  settlement_amount: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type SalesImportItem = {
  id: string;
  ticketing_setup: string;
  import_date: string;
  tickets_sold: number;
  revenue: string;
  imported_by: string;
  source_file: string | null;
  notes: string;
};

export type DepartmentReadinessReport = {
  department: {
    id: string;
    name: string;
    department_type: string;
  };
  contexts_count: number;
  open_tasks: number;
  overdue_tasks: number;
  completed_tasks: number;
  pending_approvals: number;
  open_risks: number;
};

export type RiskRegisterReport = {
  total: number;
  open: number;
  high_or_critical: number;
  by_level: Record<string, number>;
  by_status: Record<string, number>;
  results: {
    id: string;
    title: string;
    level: string;
    status: string;
    workspace: string | null;
    owner: string | null;
    raised_date: string | null;
    mitigation: string;
  }[];
};

export type ContractStatusReport = {
  total: number;
  total_value: string;
  pending_signature: number;
  signed: number;
  by_status: Record<string, number>;
  results: {
    id: string;
    workspace: string;
    counterparty: string;
    type: string;
    status: string;
    value: string;
    currency: string;
    signatures: string;
    signed_document: string | null;
  }[];
};

export type SupplierReadinessReport = {
  total: number;
  verified: number;
  pending_verification: number;
  document_gaps: number;
  engagements: number;
  results: {
    id: string;
    name: string;
    status: string;
    category: string;
    csd_verified: boolean;
    documents_total: number;
    documents_missing_or_unverified: number;
    workspaces: string[];
  }[];
};

export type EvidenceGapsReport = {
  total: number;
  task_gaps: number;
  process_step_gaps: number;
  results: {
    type: 'task' | 'process_step';
    id: string;
    title: string;
    workspace: string;
    owner: string | null;
    due_date: string | null;
  }[];
};

export type CalendarIssuesReport = {
  total: number;
  open: number;
  critical_or_high: number;
  results: {
    id: string;
    title: string;
    severity: string;
    status: string;
    workspace: string | null;
    department: string | null;
    due_date: string | null;
    raised_by: string | null;
  }[];
};

export type BoardSummaryReport = {
  workspaces: number;
  average_readiness: number;
  high_risks: number;
  pending_approvals: number;
  evidence_gaps: number;
  calendar_issues: number;
  board_ready: boolean;
};

export type YouthSummaryReport = {
  project: { id: string; title: string; status: string };
  total_learners: number;
  target_learners: number;
  schools: string;
  consent_total: number;
  consent_received: number;
  consent_rate: number;
  sessions_total: number;
  sessions_completed: number;
  attendance_rate: number;
  facilitators: number;
  facilitators_vetted: number;
  activities: { id: string; name: string; type: string; sessions_total: number; sessions_completed: number }[];
  showcases: { id: string; title: string; type: string; date: string | null; has_production_context: boolean }[];
  assessments_count: number;
};

export type AuditEventItem = {
  id: string;
  event_type: string;
  actor_email?: string | null;
  actor?: string | null;
  target_type?: string;
  target_id?: string;
  reason?: string;
  payload?: Record<string, unknown>;
  created_at: string;
};

export type YouthProjectItem = {
  id: string;
  operating_context: string;
  target_learners: number;
  target_schools: number;
  age_range_min: number | null;
  age_range_max: number | null;
  safeguarding_notes: string;
  status: 'planning' | 'recruiting' | 'active' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
};

export type YouthActivityItem = {
  id: string;
  youth_project: string;
  name: string;
  activity_type: string;
  venue: string | null;
  space: string | null;
  recurrence: string;
  start_date: string | null;
  end_date: string | null;
  day_of_week: string;
  start_time: string | null;
  end_time: string | null;
  facilitator_count: number;
  max_learners: number;
  description: string;
  created_at: string;
  updated_at: string;
};

export type YouthSessionItem = {
  id: string;
  activity: string;
  session_date: string;
  start_time: string | null;
  end_time: string | null;
  venue: string | null;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  facilitator_notes: string;
  attendance_captured: boolean;
  created_at: string;
  updated_at: string;
};

export type LearnerGroupItem = {
  id: string;
  youth_project: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
};

export type FacilitatorAssignmentItem = {
  id: string;
  youth_project: string;
  activity: string | null;
  facilitator: string;
  role: string;
  start_date: string | null;
  end_date: string | null;
  is_vetted: boolean;
  vetting_date: string | null;
  vetting_notes: string;
  created_at: string;
  updated_at: string;
};

export type ConsentRecordItem = {
  id: string;
  youth_project: string;
  learner_identifier: string;
  learner_group: string | null;
  guardian_consent_received: boolean;
  consent_date: string | null;
  consent_document: string | null;
  photo_consent: boolean;
  data_processing_consent: boolean;
  withdrawal_date: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type AttendanceRecordItem = {
  id: string;
  session: string;
  learner_identifier: string;
  learner_group: string | null;
  present: boolean;
  arrival_time: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type YouthAssessmentItem = {
  id: string;
  youth_project: string;
  activity: string | null;
  learner_identifier: string;
  assessment_type: string;
  score: string;
  assessor: string;
  assessment_date: string;
  notes: string;
  evidence_document: string | null;
  created_at: string;
  updated_at: string;
};

export type ShowcaseOutputItem = {
  id: string;
  youth_project: string;
  output_context: string | null;
  title: string;
  output_type: string;
  date: string | null;
  description: string;
  evidence_document: string | null;
  created_at: string;
  updated_at: string;
};

export type YouthProjectStats = {
  total_learners?: number;
  target_learners?: number;
  consent_total?: number;
  consent_received?: number;
  consent_rate?: number;
  sessions_total?: number;
  sessions_completed?: number;
  attendance_rate?: number;
  facilitators?: number;
  facilitators_vetted?: number;
  showcases?: number;
  assessments_count?: number;
  [key: string]: unknown;
};

export type ApprovalDecision =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'changes_requested'
  | 'escalated'
  | 'exception_approved'
  | 'cancelled';

export type ApprovalStepItem = {
  id: string;
  route: string;
  step_number: number;
  name: string;
  approver_department: string | null;
  approver_role_description: string;
  can_delegate: boolean;
};

export type ApprovalRequestItem = {
  id: string;
  operating_context: string;
  approval_step: string;
  requested_by: string;
  requested_at: string;
  decision: ApprovalDecision;
  decided_by: string | null;
  decided_at: string | null;
  decision_comment: string;
  evidence_reviewed: string | null;
};

export type WorkflowTemplateItem = {
  id: string;
  name: string;
  context_type: string;
  description: string;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
};

export type WorkflowStepTemplateItem = {
  id: string;
  template: string;
  step_number: number;
  name: string;
  owner_department: string | null;
  owner_role_description: string;
  requires_approval: boolean;
  requires_evidence: boolean;
  sla_days: number | null;
  description: string;
};

export type WorkflowInstanceItem = {
  id: string;
  template: string;
  operating_context: string;
  status: 'active' | 'completed' | 'cancelled';
  started_at: string;
  completed_at: string | null;
};

export type WorkflowStepStatus = 'pending' | 'in_progress' | 'completed' | 'skipped' | 'blocked';

export type WorkflowStepItem = {
  id: string;
  workflow_instance: string;
  step_template: string;
  step_number: number;
  status: WorkflowStepStatus;
  assigned_to: string | null;
  started_at: string | null;
  completed_at: string | null;
  completed_by: string | null;
  evidence_document: string | null;
  approval_request: string | null;
  notes: string;
  owner_department: string | null;
  owner_role_description: string;
  requires_approval: boolean;
  requires_evidence: boolean;
  sla_days: number | null;
  due_date: string | null;
  blockers: string[];
};

export type ContextReadiness = {
  context: {
    id: string;
    title: string;
    context_type: string;
    status: string;
    readiness_score: number;
    opening_date: string | null;
  };
  approvals: {
    step_name: string;
    decision: string;
    decided_by: string | null;
    decided_at: string | null;
  }[];
  tasks: {
    total: number;
    open: number;
    done: number;
    blocked: number;
  };
  documents_count: number;
  contracts: {
    id: string;
    type: string;
    counterparty: string;
    status: string;
    signed: boolean;
  }[];
  suppliers: {
    id: string;
    name: string;
    status: string;
    csd_verified: boolean;
  }[];
  artists: {
    id: string;
    name: string;
    status: string;
  }[];
  campaign: {
    level: string;
    status: string;
    deliverables_total: number;
    deliverables_complete: number;
  } | null;
  rider: {
    status: string;
    crew_size: number;
  } | null;
  foh_plan: {
    status: string;
    incidents: number;
  } | null;
  ticketing: {
    provider: string;
    setup_status: string;
    tickets_sold: number;
    settlement_status: string;
  } | null;
  youth_project: {
    status: string;
    learners: number;
    target: number;
    consent_rate: number;
    sessions_completed: number;
  } | null;
  risks: {
    id: string;
    title: string;
    level: string;
    status: string;
  }[];
  blockers?: {
    type: string;
    severity: string;
    label: string;
    detail: string;
    owner: string | null;
    due_date: string | null;
  }[];
};

export type TaskCommentItem = {
  id: string;
  task: string;
  author: string | null;
  author_email: string | null;
  author_name: string | null;
  body: string;
  created_at: string;
  updated_at: string;
};

export type CreateTaskCommentPayload = {
  task: string;
  body: string;
};

export type ScorecardTasks = {
  my_open: number;
  my_in_progress: number;
  my_overdue: number;
  dept_open: number;
  dept_in_progress: number;
  dept_overdue: number;
};

export type ScorecardDepartment = {
  id: string;
  name: string;
  is_manager: boolean;
};

export type ScorecardShow = {
  id: string;
  title: string;
  status: string;
  operating_context: string;
};

export type Scorecard = {
  tasks: ScorecardTasks;
  pending_approvals: number;
  contracts_expiring_30d: number;
  active_contexts: number;
  upcoming_shows: ScorecardShow[];
  unread_notifications: number;
  departments: ScorecardDepartment[];
};

export type PriceCategoryItem = {
  id: string;
  ticketing_setup: string;
  name: string;
  price: string;
  is_comp: boolean;
  sort_order: number;
};

export type CreatePriceCategoryPayload = {
  ticketing_setup: string;
  name: string;
  price: string;
  is_comp?: boolean;
  sort_order?: number;
};

export type BookingItem = {
  id: string;
  ticketing_setup: string;
  performance: string | null;
  booking_reference: string;
  patron_name: string;
  patron_email: string;
  patron_phone: string;
  channel: string;
  total_amount: string;
  is_group_booking: boolean;
  group_name: string;
  notes: string;
  booked_at: string;
  updated_at: string;
  tickets: TicketItem[];
};

export type TicketItem = {
  id: string;
  booking: string;
  price_category: string | null;
  seat_reference: string;
  status: string;
  amount: string;
  checked_in: boolean;
  checked_in_at: string | null;
  created_at: string;
};

export type CreateBookingPayload = {
  ticketing_setup: string;
  patron_name: string;
  patron_email?: string;
  patron_phone?: string;
  channel: string;
  total_amount: string;
  booking_reference: string;
  notes?: string;
};

export type TillReconciliationItem = {
  id: string;
  ticketing_setup: string;
  performance: string | null;
  recon_date: string;
  cash_counted: string;
  card_total: string;
  system_total: string;
  variance: string;
  variance_explained: string;
  signed_off_by: string;
  created_at: string;
  updated_at: string;
};

export type CreateTillReconciliationPayload = {
  ticketing_setup: string;
  recon_date: string;
  cash_counted: string;
  card_total: string;
  system_total: string;
  variance: string;
  variance_explained?: string;
  signed_off_by: string;
};

export type BudgetLineItem = {
  id: string;
  budget: string;
  category: string;
  description: string;
  quantity: string;
  unit_cost: string;
  amount: string;
  actual_amount: string;
  variance: string;
  notes: string;
  sort_order: number;
};

export type CreateBudgetLinePayload = {
  budget: string;
  category: string;
  description: string;
  quantity: string;
  unit_cost: string;
  actual_amount?: string;
  notes?: string;
};

export type BudgetItem = {
  id: string;
  operating_context: string;
  name: string;
  financial_year: string;
  status: string;
  total_income: string;
  total_expenditure: string;
  net_position: string;
  approved_by: string | null;
  approved_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type BoardMeetingItem = {
  id: string;
  meeting_type: string;
  title: string;
  meeting_date: string;
  venue: string;
  status: string;
  quorum_required: number;
  quorum_achieved: boolean;
  members_present: number;
  chaired_by: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type CreateBoardMeetingPayload = {
  meeting_type: string;
  title: string;
  meeting_date: string;
  venue?: string;
  quorum_required?: number;
  chaired_by?: string;
  notes?: string;
};

export type BoardResolutionItem = {
  id: string;
  meeting: string;
  resolution_number: string;
  title: string;
  description: string;
  status: string;
  proposed_by: string;
  votes_for: number;
  votes_against: number;
  votes_abstained: number;
  action_required: string;
  action_completed: boolean;
  action_due_date: string | null;
};

export type PurchaseRequisitionItem = {
  id: string;
  operating_context: string;
  requisition_number: string;
  title: string;
  description: string;
  department: string | null;
  estimated_value: string;
  currency: string;
  required_by_date: string | null;
  status: string;
  requested_by: string;
  approved_by: string | null;
  approved_at: string | null;
  rejection_reason: string;
  notes: string;
  created_at: string;
};

export type CreatePurchaseRequisitionPayload = {
  operating_context: string;
  title: string;
  description?: string;
  estimated_value: string;
  required_by_date?: string;
  notes?: string;
};

export type PurchaseOrderItem = {
  id: string;
  po_number: string;
  supplier: string;
  operating_context: string;
  description: string;
  value: string;
  currency: string;
  status: string;
  issued_date: string | null;
  delivery_date: string | null;
  actual_delivery_date: string | null;
  invoice_number: string;
  invoice_amount: string;
  three_quotes_obtained: boolean;
  csd_verified: boolean;
  notes: string;
  created_at: string;
};

export type KPIItem = {
  id: string;
  name: string;
  owner_department: string | null;
  owner_description: string;
  target_value: string;
  actual_value: string;
  unit: string;
  evidence_description: string;
  reporting_period: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type RiskItem = {
  id: string;
  operating_context: string | null;
  title: string;
  description: string;
  risk_level: string;
  owner: string;
  status: string;
  mitigation_plan: string;
  raised_date: string;
  closed_date: string | null;
  updated_at: string;
};

export type CorrectiveActionItem = {
  id: string;
  risk: string;
  action: string;
  owner: string;
  due_date: string | null;
  status: string;
  completed_date: string | null;
  updated_at: string;
};

export type PatronSegment = 'general' | 'subscriber' | 'vip' | 'youth' | 'educator' | 'corporate' | 'media' | 'donor';

export type PatronItem = {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  segment: PatronSegment;
  source: string;
  postal_code: string;
  city: string;
  province: string;
  marketing_opt_in: boolean;
  popia_consent_given: boolean;
  popia_consent_date: string | null;
  is_active: boolean;
  total_bookings: number;
  total_spend: string;
  first_visit_date: string | null;
  last_visit_date: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type PatronSummary = {
  total: number;
  opted_in: number;
  total_revenue: string | null;
  avg_spend: string | null;
  by_segment: { segment: string; count: number }[];
};

export type SocialPostItem = {
  id: string;
  campaign: string;
  platform: string;
  content: string;
  status: string;
  scheduled_at: string | null;
  published_at: string | null;
  reach: number;
  impressions: number;
  engagements: number;
  clicks: number;
  created_at: string;
};

export type AudienceReportItem = {
  id: string;
  operating_context: string;
  total_attendance: number;
  capacity_total: number;
  comps_issued: number;
  school_groups: number;
  average_ticket_price: string;
  gross_revenue: string;
  occupancy_rate: number;
  demographics_notes: string;
  feedback_summary: string;
  average_rating: string;
  is_finalised: boolean;
  created_at: string;
};

export type ShowCallItem = {
  id: string;
  operating_context: string;
  performance: string | null;
  show_date: string;
  call_time: string;
  house_open_time: string | null;
  show_start_time: string | null;
  expected_audience: number | null;
  technical_notes: string;
  foh_notes: string;
  cast_notes: string;
  production_manager_notes: string;
  status: string;
  distributed_at: string | null;
  created_at: string;
};

export type PostShowReportItem = {
  id: string;
  operating_context: string;
  performance: string | null;
  show_date: string;
  actual_start_time: string | null;
  actual_end_time: string | null;
  actual_audience: number;
  walk_ins: number;
  comps_used: number;
  incidents_count: number;
  technical_issues: string;
  foh_summary: string;
  audience_feedback: string;
  overall_rating: number | null;
  cash_collected: string;
  card_collected: string;
  created_at: string;
};

// Phase 4 types
export type PaymentMilestone = 'deposit' | 'balance' | 'final' | 'full';
export type PaymentStatus = 'pending' | 'invoice_received' | 'approved' | 'paid' | 'disputed';

export type ArtistPaymentItem = {
  id: string;
  engagement: string;
  milestone: PaymentMilestone;
  amount: string;
  status: PaymentStatus;
  due_date: string | null;
  invoice_number: string;
  paid_date: string | null;
  approved_by: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type StaffCallStatus = 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
export type StaffCallRole =
  | 'stage_manager' | 'deputy_sm' | 'lighting_op' | 'sound_op' | 'follow_spot'
  | 'fly_op' | 'head_of_wardrobe' | 'wardrobe_assistant' | 'head_usher' | 'usher'
  | 'box_office' | 'security' | 'foh_manager' | 'production_manager' | 'other';

export type StaffCallItem = {
  id: string;
  show_call: string;
  staff_member: string;
  staff_member_name: string;
  role: StaffCallRole;
  call_time: string;
  finish_time: string | null;
  status: StaffCallStatus;
  confirmed_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type SeasonSummary = {
  season_id: string;
  season_name: string;
  year: number;
  show_count: number;
  performance_count: number;
  total_bookings: number;
  tickets_sold: number;
  gross_revenue: string;
};

export type ShowFinancials = {
  show_id: string;
  show_title: string;
  budget_approved: string;
  revenue_target: string;
  ticket_revenue: string;
  artist_costs_paid: string;
  net_position: string;
};

// Phase 5 types
export type ShowLifecycle = {
  show_id: string;
  title: string;
  status: string;
  budget_approved: string;
  revenue_target: string;
  performances: {
    id: string;
    date: string;
    start_time: string;
    end_time: string | null;
    expected_audience: number;
  }[];
  engagements: {
    id: string;
    artist_name: string;
    role: string;
    fee: string;
    status: string;
  }[];
  payments: {
    id: string;
    milestone: string;
    amount: string;
    status: string;
    paid_date: string | null;
  }[];
  contracts: {
    id: string;
    contract_type: string;
    status: string;
    expiry_date: string | null;
  }[];
  technical_rider: { status: string; crew_size: number; load_in_date: string | null } | null;
  show_calls_count: number;
  post_show_reports_count: number;
  financial_summary: { ticket_revenue: string; artist_costs_paid: string; net_position: string };
};

export type BoardPackData = {
  meeting: {
    id: string;
    title: string;
    meeting_date: string;
    meeting_type: string;
    status: string;
    quorum_achieved: boolean;
    members_present: number;
  };
  kpi_summary: { name: string; target: string; actual: string; unit: string; period: string }[];
  open_risks: { title: string; likelihood: number; impact: number }[];
  resolutions: {
    id: string;
    number: string;
    title: string;
    status: string;
    proposed_by: string;
    action_due_date: string | null;
    action_completed: boolean;
  }[];
  budget_summary: {
    id: string;
    title: string;
    total_income: string;
    total_expenditure: string;
    net_position: string;
  } | null;
  generated_at: string;
};

export type VenueCapacityConfigItem = {
  id: string;
  space: string;
  configuration: string;
  capacity: number;
  notes: string;
  is_default: boolean;
  created_at: string;
};

export type ShowItem = {
  id: string;
  operating_context: string | null;
  budget_approved: string;
  revenue_target: string;
  season: string | null;
  created_at: string;
};

// Phase 7 types
export interface TenantEntityConfig {
  id: string;
  entity_type: 'pfma_schedule_3a' | 'mfma_municipal' | 'section_21_npo' | 'private_company';
  executive_authority: string;
  accounting_authority: string;
  auditor_general_client: boolean;
  pfma_applicable: boolean;
  mfma_applicable: boolean;
  grap_reporting: boolean;
  treasury_reporting_required: boolean;
  shareholder_compact_required: boolean;
  delegation_framework_required: boolean;
  financial_year_end: string;
}

export interface DelegationRule {
  id: string;
  category: string;
  action_description: string;
  delegated_to: string;
  threshold_amount: string | null;
  requires_countersign: boolean;
  countersign_level: string;
  requires_board_approval: boolean;
  notes: string;
}

export interface DelegationMatrix {
  id: string;
  name: string;
  version: number;
  effective_date: string;
  is_active: boolean;
  rules?: DelegationRule[];
}

export interface CompactActual {
  id: string;
  quarter: number;
  actual_value: string;
  variance_notes: string;
  reported_at: string;
  evidence_reference: string;
}

export interface CompactTarget {
  id: string;
  category: string;
  indicator_name: string;
  baseline_value: string;
  target_value: string;
  unit: string;
  weight_percent: string;
  q1_target: string;
  q2_target: string;
  q3_target: string;
  q4_target: string;
  actuals?: CompactActual[];
}

export interface FundingTranche {
  id: string;
  tranche_number: number;
  description: string;
  amount: string;
  due_date: string;
  received_date: string | null;
  is_received: boolean;
  notes: string;
}

export interface ShareholderCompact {
  id: string;
  financial_year: string;
  status: string;
  executive_authority: string;
  signed_date: string | null;
  review_date: string | null;
  total_grant_allocation: string;
  targets?: CompactTarget[];
  tranches?: FundingTranche[];
}

export interface IUFWIncident {
  id: string;
  reference_number: string;
  iufw_type: 'irregular' | 'unauthorised' | 'fruitless' | 'wasteful';
  status: string;
  financial_year: string;
  description: string;
  amount: string;
  discovered_date: string;
  responsible_description: string;
  root_cause: string;
  reported_to_board: boolean;
  reported_to_ag: boolean;
  agsa_reference: string;
}

// Phase 8 types
export interface AGAuditEvidence {
  id: string;
  category: string;
  description: string;
  document_reference: string;
  is_provided: boolean;
  ag_query_ref: string;
  notes: string;
  provided_date: string | null;
}

export interface AGAuditRequest {
  id: string;
  financial_year: string;
  audit_type: string;
  status: string;
  notice_date: string | null;
  fieldwork_start: string | null;
  fieldwork_end: string | null;
  draft_report_date: string | null;
  final_report_date: string | null;
  audit_outcome: string;
  management_response: string;
  evidence_items?: AGAuditEvidence[];
}

export interface ProductionLicence {
  id: string;
  operating_context: string;
  licensing_body: string;
  status: string;
  licence_number: string;
  application_date: string | null;
  approval_date: string | null;
  expiry_date: string | null;
  fee_amount: string | null;
  fee_paid_date: string | null;
  notes: string;
}

export interface VenueRentalEnquiry {
  id: string;
  reference_number: string;
  client_name: string;
  client_email: string;
  client_phone: string;
  client_organisation: string;
  event_type: string;
  event_name: string;
  event_date: string;
  event_end_date: string | null;
  expected_attendance: number;
  status: string;
  special_requirements: string;
  venue: string;
  space: string | null;
}

export interface VenueRentalQuote {
  id: string;
  enquiry: string;
  quote_number: string;
  venue_hire_fee: string;
  technical_fee: string;
  catering_fee: string;
  security_fee: string;
  other_fee: string;
  vat_rate: string;
  deposit_percentage: string;
  subtotal: number;
  vat_amount: number;
  total_inc_vat: number;
  deposit_amount: number;
  valid_until: string | null;
  is_accepted: boolean;
}

export interface SupplierCSDVerification {
  id: string;
  supplier: string;
  csd_supplier_number: string;
  verification_status: string;
  verification_date: string | null;
  tax_compliance_status: string;
  tax_clearance_expiry: string | null;
  bee_level: number | null;
  bee_certificate_expiry: string | null;
  is_blacklisted: boolean;
  blacklist_reason: string;
}

// Phase 9 types
export interface ConflictOfInterest {
  id: string;
  declarant: string;
  declarant_name?: string;
  declaration_date: string;
  financial_year: string;
  status: 'declared_none' | 'declared_conflict' | 'recused' | 'pending' | 'overdue';
  category: string;
  description: string;
  entity_name: string;
  matter_reference: string;
  recusal_details: string;
  is_annual_declaration: boolean;
}

export interface SupplierQuote {
  id: string;
  supplier_name: string;
  quote_amount: string;
  quote_date: string;
  quote_reference: string;
  is_preferred: boolean;
  disqualified: boolean;
}

export interface ThreeQuoteRequirement {
  id: string;
  reference_number: string;
  description: string;
  estimated_value: string;
  status: string;
  required_by_date: string | null;
  budget_line: string;
  awarded_amount: string | null;
  award_motivation: string;
  quotes_count: number;
  quotes?: SupplierQuote[];
}

export interface PerformanceReport {
  id: string;
  compact: string;
  quarter: number;
  status: string;
  reporting_period_start: string;
  reporting_period_end: string;
  executive_summary: string;
  key_achievements: string;
  challenges: string;
  corrective_actions: string;
  submitted_date: string | null;
  approved_date: string | null;
}

// Phase 10 types
export interface ProductionJournalEntry {
  id: string;
  operating_context: string;
  entry_date: string;
  entry_type: string;
  title: string;
  body: string;
  author: string | null;
  is_confidential: boolean;
  requires_follow_up: boolean;
  follow_up_by: string | null;
  follow_up_completed: boolean;
}

export interface LeaveRequest {
  id: string;
  employee: string;
  employee_name?: string;
  leave_type: string;
  status: string;
  start_date: string;
  end_date: string;
  days_requested: string;
  reason: string;
  approved_by: string | null;
  declined_reason: string;
}

export interface LiquorLicence {
  id: string;
  venue: string;
  venue_name?: string;
  licence_number: string;
  licence_holder: string;
  status: string;
  issue_date: string | null;
  expiry_date: string | null;
  annual_fee: string | null;
  issuing_authority: string;
}

export interface SafetyComplianceRecord {
  id: string;
  compliance_type: string;
  venue: string | null;
  operating_context: string | null;
  is_compliant: boolean;
  certificate_number: string;
  issue_date: string | null;
  expiry_date: string | null;
  issuing_body: string;
}

export interface Donor {
  id: string;
  name: string;
  category: string;
  contact_person: string;
  email: string;
  phone: string;
  is_section_18a: boolean;
  tax_exempt_number: string;
}

export interface Donation {
  id: string;
  donor: string;
  donor_name?: string;
  financial_year: string;
  status: string;
  amount_pledged: string;
  amount_received: string;
  pledge_date: string;
  received_date: string | null;
  section_18a_issued: boolean;
  purpose: string;
}

export interface BoardMemberProfile {
  id: string;
  full_name: string;
  role_title: string;
  status: string;
  appointment_date: string;
  term_end_date: string | null;
  term_number: number;
  appointing_authority: string;
  expertise_areas: string;
  committee_memberships: string;
  is_independent: boolean;
  annual_declaration_submitted: boolean;
  annual_declaration_date: string | null;
}

// Phase 5 full types
export interface GLAccount {
  id: string;
  account_code: string;
  name: string;
  category: string;
  is_active: boolean;
  grap_standard: string;
  description: string;
}

export interface GLJournalLine {
  id: string;
  account: string;
  account_code: string;
  account_name: string;
  debit: string;
  credit: string;
  description: string;
}

export interface GLJournalEntry {
  id: string;
  reference: string;
  description: string;
  entry_date: string;
  financial_year: string;
  period: number;
  is_posted: boolean;
  source: string;
  lines: GLJournalLine[];
  total_debits: number;
  total_credits: number;
  is_balanced: boolean;
}

export interface DeferredIncome {
  id: string;
  grant_name: string;
  grantor: string;
  financial_year: string;
  recognition_type: string;
  total_grant_amount: string;
  amount_recognised: string;
  amount_deferred: string;
  conditions_description: string;
  is_fully_recognised: boolean;
  recognition_date: string | null;
}

export interface Section32ProgrammeLine {
  id: string;
  programme_name: string;
  budget_allocation: string;
  expenditure_ytd: string;
  expenditure_this_month: string;
  variance: string;
  variance_explanation: string;
}

export interface Section32Report {
  id: string;
  financial_year: string;
  month: number;
  reporting_period_end: string;
  status: string;
  total_revenue_budget: string;
  total_revenue_actual: string;
  total_expenditure_budget: string;
  total_expenditure_actual: string;
  grant_receipts_ytd: string;
  fruitless_wasteful_ytd: string;
  irregular_ytd: string;
  submitted_date: string | null;
  treasury_reference: string;
  programme_lines: Section32ProgrammeLine[];
}

export interface AnnualReportSection {
  id: string;
  section_type: string;
  title: string;
  content: string;
  status: string;
  due_date: string | null;
  word_count: number;
  reviewer_notes: string;
  order: number;
}

export interface AnnualReport {
  id: string;
  financial_year: string;
  status: string;
  theme: string;
  overall_audit_outcome: string;
  tabling_date: string | null;
  publication_date: string | null;
  approved_by_board_date: string | null;
  sections: AnnualReportSection[];
  sections_complete_count: number;
  sections_total_count: number;
}

export interface IUFWDisciplinaryReferral {
  id: string;
  incident: string;
  referral_date: string;
  employee_name: string;
  charge_description: string;
  hearing_date: string | null;
  outcome: string;
  sanction_details: string;
  appeal_lodged: boolean;
}

export interface AGAuditPackage {
  audit_id: string;
  financial_year: string;
  audit_type: string;
  status: string;
  completeness_pct: number;
  total_evidence_items: number;
  provided: number;
  outstanding_count: number;
  by_category: Record<string, { total: number; provided: number; items: { id: string; description: string; ag_query_ref: string }[] }>;
  generated_at: string;
}

// Phase 6 full types
export interface SetlistWork {
  id: string;
  performance: string;
  title: string;
  composer: string;
  arranger: string;
  publisher: string;
  isrc_code: string;
  iswc_code: string;
  duration_minutes: string;
  is_original_work: boolean;
  is_public_domain: boolean;
  licensing_body: string;
  order: number;
}

export interface CoProducer {
  id: string;
  operating_context: string;
  partner_name: string;
  role: string;
  contact_person: string;
  email: string;
  cost_share_percent: string;
  revenue_share_percent: string;
  upfront_contribution: string;
}

export interface CoProductionSettlementLine {
  id: string;
  co_producer: string;
  amount_due: string;
  amount_paid: string;
  is_paid: boolean;
  payment_date: string | null;
}

export interface CoProductionSettlement {
  id: string;
  operating_context: string;
  settlement_date: string;
  total_revenue: string;
  total_costs: string;
  net_position: string;
  status: string;
  lines: CoProductionSettlementLine[];
}

export interface RentalBooking {
  id: string;
  enquiry: string;
  booking_number: string;
  confirmed_date: string;
  status: string;
  contract_signed: boolean;
  contract_signed_date: string | null;
}

export interface RentalInvoice {
  id: string;
  booking: string;
  invoice_number: string;
  invoice_type: string;
  invoice_date: string;
  due_date: string;
  subtotal: string;
  vat_amount: string;
  total: string;
  is_paid: boolean;
  paid_date: string | null;
  paid_amount: string;
}

export interface Festival {
  id: string;
  name: string;
  edition: string;
  status: string;
  start_date: string;
  end_date: string;
  expected_attendance: number;
  max_accreditation: number;
}

export interface FestivalPass {
  id: string;
  festival: string;
  pass_type: string;
  holder_name: string;
  holder_email: string;
  organisation_name: string;
  pass_number: string;
  valid_days: string;
  venue_access: string;
  is_active: boolean;
  issued_date: string | null;
}

export interface FestivalVenueSlot {
  id: string;
  festival: string;
  festival_venue: string;
  operating_context: string | null;
  slot_date: string;
  start_time: string;
  end_time: string;
  slot_label: string;
  is_confirmed: boolean;
}

export interface ResidentCompany {
  id: string;
  name: string;
  company_type: string;
  status: string;
  venue: string;
  artistic_director: string;
  contact_email: string;
  residency_start_date: string;
  residency_end_date: string | null;
  performance_slots_per_year: number;
  annual_subsidy: string;
  rental_rate_discount_pct: string;
}

export interface UnionAgreement {
  id: string;
  union: string;
  agreement_name: string;
  effective_date: string;
  expiry_date: string | null;
  is_active: boolean;
  minimum_call_hours: string;
  overtime_threshold_hours: string;
  overtime_multiplier: string;
  turnaround_hours: string;
}

export interface UnionCallRate {
  id: string;
  agreement: string;
  role_category: string;
  rate_type: string;
  minimum_rate: string;
  effective_date: string;
}

// Phase 6 types
export type SeasonCloseOut = {
  season_id: string;
  season_name: string;
  year: number;
  shows: {
    show_id: string;
    title: string;
    status: string;
    performances: number;
    ticket_revenue: string;
    artist_costs: string;
    net: string;
  }[];
  totals: {
    total_revenue: string;
    total_costs: string;
    net_position: string;
  };
};

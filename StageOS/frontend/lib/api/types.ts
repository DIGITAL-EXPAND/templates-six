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

import { ApiError, apiRequest, apiUrl } from './client';
import type {
  AuthTokens,
  GLAccount,
  GLJournalEntry,
  DeferredIncome,
  Section32Report,
  AnnualReport,
  AGAuditPackage,
  ConflictOfInterest,
  PerformanceReport,
  SupplierQuote,
  ThreeQuoteRequirement,
  TenantEntityConfig,
  DelegationMatrix,
  DelegationRule,
  ShareholderCompact,
  CompactTarget,
  IUFWIncident,
  AGAuditRequest,
  AGAuditEvidence,
  ProductionLicence,
  VenueRentalEnquiry,
  SupplierCSDVerification,
  ArtistDocumentItem,
  TaskCommentItem,
  CreateTaskCommentPayload,
  ArtistEngagementItem,
  ArtistItem,
  CalendarIssueItem,
  CalendarIssuesReport,
  ApprovalRequestItem,
  ApprovalStepItem,
  BoardSummaryReport,
  CampaignDeliverableItem,
  CampaignItem,
  ChecklistItem,
  ContextReadiness,
  ContractStatusReport,
  ContractRecordItem,
  ContractTemplateItem,
  CreateCalendarIssuePayload,
  CreateDocumentPayload,
  CreateEvidencePayload,
  CreateExecutiveActionPayload,
  CreateIntakeRequestPayload,
  CreateTaskPayload,
  CreateWorkspacePayload,
  CurrentUser,
  DepartmentListItem,
  DepartmentReadinessReport,
  DocumentItem,
  EvidenceGapsReport,
  EquipmentRequirementItem,
  EvidenceSubmissionItem,
  ExecutiveSummary,
  ExecutiveActionItem,
  FohPlanItem,
  IncidentItem,
  IntakeRequestItem,
  OperatingContextListItem,
  OrganisationItem,
  OperatingProfile,
  OperatingModelItem,
  PaginatedResponse,
  PaymentPackItem,
  RiskRegisterReport,
  SiteListItem,
  ModuleActivationItem,
  NotificationItem,
  PositionItem,
  Scorecard,
  SignatureRecordItem,
  SupplierDocumentItem,
  SupplierEngagementItem,
  SupplierItem,
  SupplierReadinessReport,
  TaskItem,
  CrewRequirementItem,
  TechnicalRiderItem,
  CalendarSlotItem,
  TicketingSetupItem,
  SalesImportItem,
  YouthSummaryReport,
  AuditEventItem,
  AttendanceRecordItem,
  ConsentRecordItem,
  FacilitatorAssignmentItem,
  LearnerGroupItem,
  ShowcaseOutputItem,
  UserListItem,
  UserDepartmentMembershipItem,
  VenueHoldItem,
  WorkflowInstanceItem,
  WorkflowStepItem,
  WorkflowStepTemplateItem,
  WorkflowTemplateItem,
  YouthActivityItem,
  YouthAssessmentItem,
  YouthProjectItem,
  YouthProjectStats,
  YouthSessionItem,
  BookingItem,
  CreateBookingPayload,
  PriceCategoryItem,
  CreatePriceCategoryPayload,
  TillReconciliationItem,
  CreateTillReconciliationPayload,
  BudgetItem,
  BudgetLineItem,
  CreateBudgetLinePayload,
  BoardMeetingItem,
  CreateBoardMeetingPayload,
  BoardResolutionItem,
  PurchaseRequisitionItem,
  CreatePurchaseRequisitionPayload,
  PurchaseOrderItem,
  KPIItem,
  RiskItem,
  CorrectiveActionItem,
  PatronItem,
  PatronSummary,
  SocialPostItem,
  AudienceReportItem,
  ShowCallItem,
  PostShowReportItem,
  ArtistPaymentItem,
  StaffCallItem,
  SeasonSummary,
  ShowFinancials,
  ShowLifecycle,
  BoardPackData,
  VenueCapacityConfigItem,
  ShowItem,
  SeasonCloseOut,
  ProductionJournalEntry,
  LeaveRequest,
  LiquorLicence,
  SafetyComplianceRecord,
  Donor,
  Donation,
  BoardMemberProfile,
  SetlistWork,
  CoProducer,
  CoProductionSettlement,
  RentalBooking,
  RentalInvoice,
  Festival,
  FestivalPass,
  ResidentCompany,
  UnionAgreement,
  UnionCallRate,
  MaintenanceTicket,
  MaintenanceSchedule,
  InspectionRecord,
  VenueDowntime,
  CueSheet,
  CueLine,
  PropsItem,
  WardrobeItem,
  AudienceComplaint,
  AccessibilityRequirement,
  MediaContact,
  NewsletterCampaign,
  CIComplianceCheck,
  TouringProduction,
  TouringVenueDate,
  RecurringProduction,
  ExpiryAlert,
} from './types';

function queryString(params?: Record<string, string | boolean | null | undefined>) {
  if (!params) {
    return '';
  }
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '' && value !== false) {
      search.set(key, String(value));
    }
  });
  const value = search.toString();
  return value ? `?${value}` : '';
}

export function loginRequest(email: string, password: string) {
  return apiRequest<AuthTokens>('/api/token/', {
    method: 'POST',
    body: { email, password },
  });
}

export function fetchCurrentUser(token: string) {
  return apiRequest<CurrentUser>('/api/v1/me/', {
    method: 'GET',
    token,
  });
}

export function fetchOperatingProfile(token: string) {
  return apiRequest<OperatingProfile>('/api/v1/me/operating-profile/', {
    method: 'GET',
    token,
  });
}

export function refreshToken(refresh: string) {
  return apiRequest<Pick<AuthTokens, 'access'>>('/api/token/refresh/', {
    method: 'POST',
    body: { refresh },
  });
}

export function fetchExecutiveSummary(token: string) {
  return apiRequest<ExecutiveSummary>('/api/v1/reports/executive-summary/', {
    method: 'GET',
    token,
  });
}

export function fetchOperatingContexts(token: string) {
  return apiRequest<PaginatedResponse<OperatingContextListItem>>('/api/v1/contexts/', {
    method: 'GET',
    token,
  });
}

export function fetchOperatingContext(token: string, id: string) {
  return apiRequest<OperatingContextListItem>(`/api/v1/contexts/${id}/`, {
    method: 'GET',
    token,
  });
}

export function createWorkspace(token: string, payload: CreateWorkspacePayload) {
  return apiRequest<OperatingContextListItem>('/api/v1/contexts/', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function fetchContextReadiness(token: string, id: string) {
  return apiRequest<ContextReadiness>(`/api/v1/reports/context-readiness/${id}/`, {
    method: 'GET',
    token,
  });
}

export function fetchSites(token: string) {
  return apiRequest<PaginatedResponse<SiteListItem>>('/api/v1/sites/', {
    method: 'GET',
    token,
  });
}

export function fetchDepartments(token: string) {
  return apiRequest<PaginatedResponse<DepartmentListItem>>('/api/v1/departments/', {
    method: 'GET',
    token,
  });
}

export function fetchPositions(token: string) {
  return apiRequest<PaginatedResponse<PositionItem>>('/api/v1/positions/', {
    method: 'GET',
    token,
  });
}

export function fetchOperatingModels(token: string) {
  return apiRequest<PaginatedResponse<OperatingModelItem>>('/api/v1/operating-models/', {
    method: 'GET',
    token,
  });
}

export function fetchUserDepartmentMemberships(token: string) {
  return apiRequest<PaginatedResponse<UserDepartmentMembershipItem>>('/api/v1/user-department-memberships/', {
    method: 'GET',
    token,
  });
}

export function fetchModuleActivations(token: string) {
  return apiRequest<PaginatedResponse<ModuleActivationItem>>('/api/v1/module-activations/', {
    method: 'GET',
    token,
  });
}

export function fetchUsers(token: string) {
  return apiRequest<PaginatedResponse<UserListItem>>('/api/v1/users/', {
    method: 'GET',
    token,
  });
}

export function fetchOrganisations(token: string) {
  return apiRequest<PaginatedResponse<OrganisationItem>>('/api/v1/organisations/', {
    method: 'GET',
    token,
  });
}

export function fetchContextAuditTrail(token: string, id: string) {
  return apiRequest<PaginatedResponse<AuditEventItem>>(`/api/v1/reports/context-audit/${id}/`, {
    method: 'GET',
    token,
  });
}

export function fetchIntakeRequests(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<IntakeRequestItem>>(
    `/api/v1/programming/intake-requests/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function createIntakeRequest(token: string, payload: CreateIntakeRequestPayload) {
  return apiRequest<IntakeRequestItem>('/api/v1/programming/intake-requests/', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function setIntakeRequestAction(
  token: string,
  requestId: string,
  action: 'start-review' | 'approve' | 'decline' | 'defer' | 'request-changes',
  comment: string,
) {
  return apiRequest<IntakeRequestItem>(`/api/v1/programming/intake-requests/${requestId}/${action}/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function convertIntakeRequestToWorkspace(
  token: string,
  requestId: string,
  payload: { site?: string; venue?: string | null; owner: string; department?: string | null; priority?: string; risk_level?: string; budget?: string },
) {
  return apiRequest<{ workspace_id: string }>(
    `/api/v1/programming/intake-requests/${requestId}/convert-to-workspace/`,
    {
      method: 'POST',
      token,
      body: payload,
    },
  );
}

export function fetchVenueHolds(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<VenueHoldItem>>(
    `/api/v1/programming/venue-holds/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function fetchCalendarSlots(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<CalendarSlotItem>>(
    `/api/v1/programming/calendar-slots/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function fetchCalendarIssues(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<CalendarIssueItem>>(
    `/api/v1/programming/calendar-issues/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function createCalendarIssue(token: string, payload: CreateCalendarIssuePayload) {
  return apiRequest<CalendarIssueItem>('/api/v1/programming/calendar-issues/', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function setCalendarIssueAction(
  token: string,
  issueId: string,
  action: 'progress' | 'resolve' | 'cancel',
  note: string,
) {
  return apiRequest<CalendarIssueItem>(`/api/v1/programming/calendar-issues/${issueId}/${action}/`, {
    method: 'POST',
    token,
    body: { note },
  });
}

export function fetchExecutiveActions(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<ExecutiveActionItem>>(
    `/api/v1/governance/executive-actions/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function createExecutiveAction(token: string, payload: CreateExecutiveActionPayload) {
  return apiRequest<ExecutiveActionItem>('/api/v1/governance/executive-actions/', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function setExecutiveActionStatus(
  token: string,
  actionId: string,
  action: 'acknowledge' | 'complete' | 'cancel',
  comment: string,
) {
  return apiRequest<ExecutiveActionItem>(`/api/v1/governance/executive-actions/${actionId}/${action}/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchTasks(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<TaskItem>>(`/api/v1/tasks/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function createTask(token: string, payload: CreateTaskPayload) {
  return apiRequest<TaskItem>('/api/v1/tasks/', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function completeTask(token: string, taskId: string, hasEvidence: boolean) {
  return apiRequest<TaskItem>(`/api/v1/tasks/${taskId}/complete/`, {
    method: 'POST',
    token,
    body: { has_evidence: hasEvidence },
  });
}

export function fetchDocuments(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<DocumentItem>>(`/api/v1/documents/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function createDocument(token: string, payload: CreateDocumentPayload) {
  return apiRequest<DocumentItem>('/api/v1/documents/', {
    method: 'POST',
    token,
    body: {
      ...payload,
      file_size: '0',
      mime_type: '',
    },
  });
}

export function fetchEvidence(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<EvidenceSubmissionItem>>(
    `/api/v1/evidence/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function submitEvidence(token: string, payload: CreateEvidencePayload) {
  return apiRequest<EvidenceSubmissionItem>('/api/v1/evidence/', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function acceptEvidence(token: string, evidenceId: string) {
  return apiRequest<EvidenceSubmissionItem>(`/api/v1/evidence/${evidenceId}/accept/`, {
    method: 'POST',
    token,
  });
}

export function startTask(token: string, taskId: string, comment = '') {
  return apiRequest<TaskItem>(`/api/v1/tasks/${taskId}/start/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function blockTask(token: string, taskId: string, comment: string) {
  return apiRequest<TaskItem>(`/api/v1/tasks/${taskId}/block/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchScorecard(token: string) {
  return apiRequest<Scorecard>('/api/v1/me/scorecard/', {
    method: 'GET',
    token,
  });
}

export function fetchNotifications(token: string) {
  return apiRequest<PaginatedResponse<NotificationItem>>('/api/v1/notifications/', {
    method: 'GET',
    token,
  });
}

export function markNotificationRead(token: string, notificationId: string) {
  return apiRequest<NotificationItem>(`/api/v1/notifications/${notificationId}/read/`, {
    method: 'POST',
    token,
  });
}

export function rejectEvidence(token: string, evidenceId: string, reason: string) {
  return apiRequest<EvidenceSubmissionItem>(`/api/v1/evidence/${evidenceId}/reject/`, {
    method: 'POST',
    token,
    body: { reason },
  });
}

export async function downloadDocument(token: string, documentId: string) {
  const response = await fetch(apiUrl(`/api/v1/documents/${documentId}/download/`), {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error(`Download failed with status ${response.status}`);
  }
  return response.blob();
}

export function fetchContractTemplates(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<ContractTemplateItem>>(
    `/api/v1/contracts/templates/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function fetchContracts(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<ContractRecordItem>>(
    `/api/v1/contracts/records/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function fetchSignatures(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<SignatureRecordItem>>(
    `/api/v1/contracts/signatures/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function issueContract(token: string, contractId: string) {
  return apiRequest<ContractRecordItem>(`/api/v1/contracts/records/${contractId}/issue/`, {
    method: 'POST',
    token,
  });
}

export function submitContractForReview(token: string, contractId: string, reviewType: string) {
  return apiRequest<ContractRecordItem>(
    `/api/v1/contracts/records/${contractId}/submit-for-review/`,
    {
      method: 'POST',
      token,
      body: { review_type: reviewType },
    },
  );
}

export function cancelContract(token: string, contractId: string, comment: string) {
  return apiRequest<ContractRecordItem>(`/api/v1/contracts/records/${contractId}/cancel/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function lockFinalContract(token: string, contractId: string, comment: string) {
  return apiRequest<ContractRecordItem>(`/api/v1/contracts/records/${contractId}/lock/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function signContractSignature(token: string, signatureId: string) {
  return apiRequest<SignatureRecordItem>(`/api/v1/contracts/signatures/${signatureId}/sign/`, {
    method: 'POST',
    token,
  });
}

export function fetchSuppliers(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<SupplierItem>>(`/api/v1/suppliers/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function verifySupplier(token: string, supplierId: string) {
  return apiRequest<SupplierItem>(`/api/v1/suppliers/${supplierId}/verify/`, {
    method: 'POST',
    token,
  });
}

export function suspendSupplier(token: string, supplierId: string, comment: string) {
  return apiRequest<SupplierItem>(`/api/v1/suppliers/${supplierId}/suspend/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchSupplierDocuments(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<SupplierDocumentItem>>(
    `/api/v1/suppliers/documents/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function decideSupplierDocument(
  token: string,
  documentId: string,
  action: 'verify' | 'reject',
  comment: string,
) {
  return apiRequest<SupplierDocumentItem>(`/api/v1/suppliers/documents/${documentId}/${action}/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchSupplierEngagements(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<SupplierEngagementItem>>(
    `/api/v1/suppliers/engagements/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function fetchPaymentPacks(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<PaymentPackItem>>(
    `/api/v1/suppliers/payment-packs/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function sendPaymentPackToErp(token: string, packId: string) {
  return apiRequest<PaymentPackItem>(`/api/v1/suppliers/payment-packs/${packId}/send-to-erp/`, {
    method: 'POST',
    token,
  });
}

export function fetchArtists(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<ArtistItem>>(`/api/v1/artists/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchArtistDocuments(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<ArtistDocumentItem>>(
    `/api/v1/artists/documents/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function decideArtistDocument(
  token: string,
  documentId: string,
  action: 'verify' | 'reject',
  comment: string,
) {
  return apiRequest<ArtistDocumentItem>(`/api/v1/artists/documents/${documentId}/${action}/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchArtistEngagements(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<ArtistEngagementItem>>(
    `/api/v1/artists/engagements/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function confirmArtistEngagement(token: string, engagementId: string) {
  return apiRequest<ArtistEngagementItem>(`/api/v1/artists/engagements/${engagementId}/confirm/`, {
    method: 'POST',
    token,
  });
}

export function fetchCampaigns(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<CampaignItem>>(`/api/v1/marketing/campaigns/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function setCampaignAction(
  token: string,
  campaignId: string,
  action: 'launch' | 'pause' | 'close',
  comment: string,
) {
  return apiRequest<CampaignItem>(`/api/v1/marketing/campaigns/${campaignId}/${action}/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchCampaignDeliverables(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<CampaignDeliverableItem>>(
    `/api/v1/marketing/deliverables/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function completeCampaignDeliverable(
  token: string,
  deliverableId: string,
  payload: { evidence_document?: string | null; comment?: string },
) {
  return apiRequest<CampaignDeliverableItem>(`/api/v1/marketing/deliverables/${deliverableId}/complete/`, {
    method: 'POST',
    token,
    body: payload,
  });
}

export function fetchTechnicalRiders(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<TechnicalRiderItem>>(`/api/v1/technical/riders/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function setRiderAction(
  token: string,
  riderId: string,
  action: 'submit' | 'approve' | 'reject' | 'request-revision',
  comment: string,
) {
  return apiRequest<TechnicalRiderItem>(`/api/v1/technical/riders/${riderId}/${action}/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchCrewRequirements(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<CrewRequirementItem>>(`/api/v1/technical/crew/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchEquipmentRequirements(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<EquipmentRequirementItem>>(
    `/api/v1/technical/equipment/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function fetchFohPlans(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<FohPlanItem>>(`/api/v1/operations/foh-plans/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function setFohPlanAction(token: string, planId: string, action: 'confirm' | 'close', comment: string) {
  return apiRequest<FohPlanItem>(`/api/v1/operations/foh-plans/${planId}/${action}/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchChecklists(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<ChecklistItem>>(`/api/v1/operations/checklists/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function checkChecklistItem(token: string, itemId: string, comment: string) {
  return apiRequest<ChecklistItem>(`/api/v1/operations/checklists/${itemId}/check/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchIncidents(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<IncidentItem>>(`/api/v1/operations/incidents/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function createIncident(
  token: string,
  payload: {
    operating_context: string;
    foh_plan?: string | null;
    incident_type: string;
    occurred_at: string;
    description: string;
    response?: string;
    severity: string;
  },
) {
  return apiRequest<IncidentItem>('/api/v1/operations/incidents/', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function fetchTicketingSetups(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<TicketingSetupItem>>(`/api/v1/ticketing/setups/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function setTicketingLive(token: string, setupId: string) {
  return apiRequest<TicketingSetupItem>(`/api/v1/ticketing/setups/${setupId}/go-live/`, {
    method: 'POST',
    token,
  });
}

export function importTicketSales(
  token: string,
  setupId: string,
  payload: { tickets_sold: number; revenue: string; notes?: string; source_file?: string | null },
) {
  return apiRequest<SalesImportItem>(`/api/v1/ticketing/setups/${setupId}/import-sales/`, {
    method: 'POST',
    token,
    body: payload,
  });
}

export function settleTicketing(token: string, setupId: string, amount: string) {
  return apiRequest<TicketingSetupItem>(`/api/v1/ticketing/setups/${setupId}/settle/`, {
    method: 'POST',
    token,
    body: { amount },
  });
}

export function fetchSalesImports(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<SalesImportItem>>(`/api/v1/ticketing/sales-imports/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchDepartmentReadiness(token: string, departmentId: string) {
  return apiRequest<DepartmentReadinessReport>(`/api/v1/reports/department-readiness/${departmentId}/`, {
    method: 'GET',
    token,
  });
}

export function fetchRiskRegister(token: string) {
  return apiRequest<RiskRegisterReport>('/api/v1/reports/risk-register/', {
    method: 'GET',
    token,
  });
}

export function fetchContractStatusReport(token: string) {
  return apiRequest<ContractStatusReport>('/api/v1/reports/contract-status/', {
    method: 'GET',
    token,
  });
}

export function fetchSupplierReadinessReport(token: string) {
  return apiRequest<SupplierReadinessReport>('/api/v1/reports/supplier-readiness/', {
    method: 'GET',
    token,
  });
}

export function fetchEvidenceGapsReport(token: string) {
  return apiRequest<EvidenceGapsReport>('/api/v1/reports/evidence-gaps/', {
    method: 'GET',
    token,
  });
}

export function fetchCalendarIssuesReport(token: string) {
  return apiRequest<CalendarIssuesReport>('/api/v1/reports/calendar-issues/', {
    method: 'GET',
    token,
  });
}

export function fetchBoardSummaryReport(token: string) {
  return apiRequest<BoardSummaryReport>('/api/v1/reports/board-summary/', {
    method: 'GET',
    token,
  });
}

export function fetchYouthSummary(token: string, projectId: string) {
  return apiRequest<YouthSummaryReport>(`/api/v1/reports/youth-summary/${projectId}/`, {
    method: 'GET',
    token,
  });
}

export function fetchAuditExport(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<AuditEventItem>>(`/api/v1/reports/audit-export/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchAuditEvents(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<AuditEventItem>>(`/api/v1/audit/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchKPIs(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<KPIItem>>(`/api/v1/governance/kpis/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchRisks(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<RiskItem>>(`/api/v1/governance/risks/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchCorrectiveActions(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<CorrectiveActionItem>>(`/api/v1/governance/corrective-actions/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function uploadDocumentFile(
  token: string,
  payload: {
    operating_context: string;
    title: string;
    document_type: string;
    file: File;
    version?: number;
  },
) {
  const form = new FormData();
  form.set('operating_context', payload.operating_context);
  form.set('title', payload.title);
  form.set('document_type', payload.document_type);
  form.set('file', payload.file);
  form.set('version', String(payload.version ?? 1));
  return apiRequest<DocumentItem>('/api/v1/documents/upload/', {
    method: 'POST',
    token,
    body: form,
  });
}

export function fetchYouthProjects(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<YouthProjectItem>>(`/api/v1/youth/projects/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchYouthProjectStats(token: string, projectId: string) {
  return apiRequest<YouthProjectStats>(`/api/v1/youth/projects/${projectId}/stats/`, {
    method: 'GET',
    token,
  });
}

export function setYouthProjectAction(token: string, projectId: string, action: 'activate' | 'complete', comment: string) {
  return apiRequest<YouthProjectItem>(`/api/v1/youth/projects/${projectId}/${action}/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchYouthActivities(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<YouthActivityItem>>(`/api/v1/youth/activities/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchYouthSessions(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<YouthSessionItem>>(`/api/v1/youth/sessions/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function completeYouthSession(token: string, sessionId: string, comment: string) {
  return apiRequest<YouthSessionItem>(`/api/v1/youth/sessions/${sessionId}/complete/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function captureYouthAttendance(
  token: string,
  sessionId: string,
  attendance: { learner_identifier: string; present: boolean; arrival_time?: string | null; notes?: string }[],
) {
  return apiRequest<{ session_id: string; records_captured: number; attendance_captured: boolean }>(
    `/api/v1/youth/sessions/${sessionId}/capture-attendance/`,
    {
      method: 'POST',
      token,
      body: { attendance },
    },
  );
}

export function fetchLearnerGroups(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<LearnerGroupItem>>(`/api/v1/youth/learner-groups/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchFacilitators(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<FacilitatorAssignmentItem>>(`/api/v1/youth/facilitators/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function vetFacilitator(token: string, facilitatorId: string, comment: string) {
  return apiRequest<FacilitatorAssignmentItem>(`/api/v1/youth/facilitators/${facilitatorId}/vet/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchConsentRecords(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<ConsentRecordItem>>(`/api/v1/youth/consent/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function setConsentAction(token: string, consentId: string, action: 'receive-consent' | 'withdraw-consent', comment: string) {
  return apiRequest<ConsentRecordItem>(`/api/v1/youth/consent/${consentId}/${action}/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

export function fetchAttendanceRecords(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<AttendanceRecordItem>>(`/api/v1/youth/attendance/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchYouthAssessments(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<YouthAssessmentItem>>(`/api/v1/youth/assessments/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchShowcaseOutputs(token: string, params?: Record<string, string | boolean | null | undefined>) {
  return apiRequest<PaginatedResponse<ShowcaseOutputItem>>(`/api/v1/youth/showcases/${queryString(params)}`, {
    method: 'GET',
    token,
  });
}

export function fetchApprovalSteps(token: string) {
  return apiRequest<PaginatedResponse<ApprovalStepItem>>('/api/v1/approvals/steps/', {
    method: 'GET',
    token,
  });
}

export function fetchApprovalRequests(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<ApprovalRequestItem>>(
    `/api/v1/approvals/requests/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function decideApproval(
  token: string,
  approvalId: string,
  action: 'approve' | 'reject' | 'request-changes' | 'request-more-information' | 'escalate' | 'exception-approve',
  payload: { comment?: string; evidence?: string | null },
) {
  return apiRequest<ApprovalRequestItem>(`/api/v1/approvals/requests/${approvalId}/${action}/`, {
    method: 'POST',
    token,
    body: payload,
  });
}

export function fetchWorkflowTemplates(token: string) {
  return apiRequest<PaginatedResponse<WorkflowTemplateItem>>('/api/v1/workflows/templates/', {
    method: 'GET',
    token,
  });
}

export function fetchWorkflowStepTemplates(token: string) {
  return apiRequest<PaginatedResponse<WorkflowStepTemplateItem>>(
    '/api/v1/workflows/step-templates/',
    {
      method: 'GET',
      token,
    },
  );
}

export function fetchWorkflowInstances(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<WorkflowInstanceItem>>(
    `/api/v1/workflows/instances/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function fetchWorkflowSteps(
  token: string,
  params?: Record<string, string | boolean | null | undefined>,
) {
  return apiRequest<PaginatedResponse<WorkflowStepItem>>(
    `/api/v1/workflows/steps/${queryString(params)}`,
    {
      method: 'GET',
      token,
    },
  );
}

export function advanceWorkflowStep(
  token: string,
  stepId: string,
  payload: { notes?: string; evidence_document?: string | null; approval_request?: string | null },
) {
  return apiRequest<WorkflowStepItem>(`/api/v1/workflows/steps/${stepId}/advance/`, {
    method: 'POST',
    token,
    body: payload,
  });
}

export function fetchTaskComments(token: string, taskId: string) {
  return apiRequest<PaginatedResponse<TaskCommentItem>>(`/api/v1/tasks/comments/?task=${taskId}`, {
    method: 'GET',
    token,
  });
}

export function createTaskComment(token: string, payload: CreateTaskCommentPayload) {
  return apiRequest<TaskCommentItem>('/api/v1/tasks/comments/', {
    method: 'POST',
    token,
    body: payload,
  });
}

export function deleteTaskComment(token: string, commentId: string) {
  return apiRequest<void>(`/api/v1/tasks/comments/${commentId}/`, {
    method: 'DELETE',
    token,
  });
}

export function assignTask(token: string, taskId: string, payload: { assigned_to: string | null; due_date?: string | null; comment?: string }) {
  return apiRequest<TaskItem>(`/api/v1/tasks/${taskId}/assign/`, {
    method: 'POST',
    token,
    body: payload,
  });
}

export function reopenTask(token: string, taskId: string, comment = '') {
  return apiRequest<TaskItem>(`/api/v1/tasks/${taskId}/reopen/`, {
    method: 'POST',
    token,
    body: { comment },
  });
}

// Bookings
export function fetchBookings(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<BookingItem>>(`/api/v1/ticketing/bookings/${queryString(params)}`, { token });
}

export function createBooking(token: string, data: CreateBookingPayload) {
  return apiRequest<BookingItem>('/api/v1/ticketing/bookings/', { method: 'POST', token, body: data });
}

// Price categories
export function fetchPriceCategories(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<PriceCategoryItem>>(`/api/v1/ticketing/price-categories/${queryString(params)}`, { token });
}

export function createPriceCategory(token: string, data: CreatePriceCategoryPayload) {
  return apiRequest<PriceCategoryItem>('/api/v1/ticketing/price-categories/', { method: 'POST', token, body: data });
}

// Till reconciliations
export function fetchTillReconciliations(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<TillReconciliationItem>>(`/api/v1/ticketing/till-reconciliations/${queryString(params)}`, { token });
}

export function createTillReconciliation(token: string, data: CreateTillReconciliationPayload) {
  return apiRequest<TillReconciliationItem>('/api/v1/ticketing/till-reconciliations/', { method: 'POST', token, body: data });
}

// Budget
export function fetchBudgets(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<BudgetItem>>(`/api/v1/governance/budgets/${queryString(params)}`, { token });
}

export function fetchBudgetLines(token: string, budgetId: string) {
  return apiRequest<PaginatedResponse<BudgetLineItem>>(`/api/v1/governance/budget-lines/?budget=${budgetId}`, { token });
}

export function createBudgetLine(token: string, data: CreateBudgetLinePayload) {
  return apiRequest<BudgetLineItem>('/api/v1/governance/budget-lines/', { method: 'POST', token, body: data });
}

export function approveBudget(token: string, budgetId: string) {
  return apiRequest<BudgetItem>(`/api/v1/governance/budgets/${budgetId}/approve/`, { method: 'POST', token });
}

// Board meetings
export function fetchBoardMeetings(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<BoardMeetingItem>>(`/api/v1/governance/board-meetings/${queryString(params)}`, { token });
}

export function createBoardMeeting(token: string, data: CreateBoardMeetingPayload) {
  return apiRequest<BoardMeetingItem>('/api/v1/governance/board-meetings/', { method: 'POST', token, body: data });
}

export function fetchBoardResolutions(token: string, meetingId: string) {
  return apiRequest<PaginatedResponse<BoardResolutionItem>>(`/api/v1/governance/board-resolutions/?board_meeting=${meetingId}`, { token });
}

// Procurement
export function fetchPurchaseRequisitions(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<PurchaseRequisitionItem>>(`/api/v1/suppliers/purchase-orders/${queryString(params)}`, { token });
}

export function createPurchaseRequisition(token: string, data: CreatePurchaseRequisitionPayload) {
  return apiRequest<PurchaseRequisitionItem>('/api/v1/suppliers/purchase-orders/', { method: 'POST', token, body: data });
}

export function approvePurchaseRequisition(token: string, id: string) {
  return apiRequest<PurchaseRequisitionItem>(`/api/v1/suppliers/purchase-orders/${id}/approve/`, { method: 'POST', token });
}

export function rejectPurchaseRequisition(token: string, id: string, reason: string) {
  return apiRequest<PurchaseRequisitionItem>(`/api/v1/suppliers/purchase-orders/${id}/reject/`, { method: 'POST', token, body: { reason } });
}

export function fetchPurchaseOrders(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<PurchaseOrderItem>>(`/api/v1/suppliers/purchase-orders/${queryString(params)}`, { token });
}

// Patrons
export function fetchPatrons(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<PatronItem>>(`/api/v1/patrons/${queryString(params)}`, { token });
}

export function fetchPatronSummary(token: string) {
  return apiRequest<PatronSummary>('/api/v1/patrons/summary/', { token });
}

export function createPatron(token: string, data: Partial<PatronItem>) {
  return apiRequest<PatronItem>('/api/v1/patrons/', { method: 'POST', token, body: data });
}

// Social posts
export function fetchSocialPosts(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<SocialPostItem>>(`/api/v1/marketing/social-posts/${queryString(params)}`, { token });
}

// Audience reports
export function fetchAudienceReports(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<AudienceReportItem>>(`/api/v1/marketing/audience-reports/${queryString(params)}`, { token });
}

// Show calls
export function fetchShowCalls(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<ShowCallItem>>(`/api/v1/operations/show-calls/${queryString(params)}`, { token });
}

// Post-show reports
export function fetchPostShowReports(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<PostShowReportItem>>(`/api/v1/operations/post-show-reports/${queryString(params)}`, { token });
}

// Phase 4 endpoints
export async function fetchArtistPayments(token: string, engagementId?: string): Promise<ArtistPaymentItem[]> {
  const url = engagementId
    ? `/api/v1/artists/payments/?engagement=${engagementId}`
    : '/api/v1/artists/payments/';
  const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load artist payments' });
  const data = await r.json();
  return Array.isArray(data) ? data : (data.results ?? []);
}

export async function approveArtistPayment(token: string, id: string): Promise<ArtistPaymentItem> {
  const r = await fetch(`/api/v1/artists/payments/${id}/approve/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to approve payment' });
  return r.json();
}

export async function markArtistPaymentPaid(token: string, id: string): Promise<ArtistPaymentItem> {
  const r = await fetch(`/api/v1/artists/payments/${id}/mark_paid/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to mark payment paid' });
  return r.json();
}

export async function fetchStaffCalls(token: string, showCallId?: string): Promise<StaffCallItem[]> {
  const url = showCallId
    ? `/api/v1/operations/staff-calls/?show_call=${showCallId}`
    : '/api/v1/operations/staff-calls/';
  const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load staff calls' });
  const data = await r.json();
  return Array.isArray(data) ? data : (data.results ?? []);
}

export async function fetchSeasonSummary(token: string, seasonId: string): Promise<SeasonSummary> {
  const r = await fetch(`/api/v1/programming/seasons/${seasonId}/summary/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load season summary' });
  return r.json();
}

export async function fetchShowFinancials(token: string, showId: string): Promise<ShowFinancials> {
  const r = await fetch(`/api/v1/programming/shows/${showId}/financials/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load show financials' });
  return r.json();
}

// Phase 5 endpoints
export async function fetchShowLifecycle(token: string, showId: string): Promise<ShowLifecycle> {
  const r = await fetch(`/api/v1/programming/shows/${showId}/lifecycle/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load show lifecycle' });
  return r.json();
}

export async function fetchShows(token: string): Promise<ShowItem[]> {
  const r = await fetch('/api/v1/programming/shows/', {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load shows' });
  const data = await r.json();
  return Array.isArray(data) ? data : (data.results ?? []);
}

export async function fetchBoardPack(token: string, meetingId: string): Promise<BoardPackData> {
  const r = await fetch(`/api/v1/governance/board-meetings/${meetingId}/pack/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load board pack' });
  return r.json();
}

export async function fetchVenueCapacityConfigs(token: string, spaceId?: string): Promise<VenueCapacityConfigItem[]> {
  const url = spaceId
    ? `/api/v1/venue-capacity-configs/?space=${spaceId}`
    : '/api/v1/venue-capacity-configs/';
  const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load capacity configs' });
  const data = await r.json();
  return Array.isArray(data) ? data : (data.results ?? []);
}

export async function fetchVenues(token: string): Promise<{ id: string; name: string; venue_type: string; site: string; site_name: string; capacity: number; is_active: boolean }[]> {
  const r = await fetch('/api/v1/venues/', { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load venues' });
  const data = await r.json();
  return Array.isArray(data) ? data : (data.results ?? []);
}

export async function fetchSpacesForVenue(token: string): Promise<{ id: string; name: string; space_type: string; venue: string; venue_name: string; capacity: number; is_bookable: boolean }[]> {
  const r = await fetch('/api/v1/spaces/', { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load spaces' });
  const data = await r.json();
  return Array.isArray(data) ? data : (data.results ?? []);
}

// Phase 6 endpoints
export async function launchWorkflow(token: string, templateId: string, contextId: string): Promise<WorkflowInstanceItem> {
  const r = await fetch('/api/v1/workflows/instances/launch/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ template: templateId, operating_context: contextId }),
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to launch workflow' });
  return r.json();
}

export async function fetchSeasonCloseOut(token: string, seasonId: string): Promise<SeasonCloseOut> {
  const r = await fetch(`/api/v1/programming/seasons/${seasonId}/close_out_summary/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to load season close-out' });
  return r.json();
}

export async function closeOutShow(token: string, showId: string): Promise<{ show_id: string; title: string; status: string; ticket_revenue: string; artist_costs_paid: string; net_position: string; message: string }> {
  const r = await fetch(`/api/v1/programming/shows/${showId}/close_out/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to close out show' });
  return r.json();
}

// Phase 7 endpoints
export async function fetchDelegationMatrices(token: string) {
  const res = await fetch('/api/v1/governance/delegation-matrices/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: DelegationMatrix[] }>;
}

export async function fetchDelegationMatrixRules(token: string, matrixId: string) {
  const res = await fetch(`/api/v1/governance/delegation-rules/?delegation_matrix=${matrixId}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: DelegationRule[] }>;
}

export async function fetchShareholderCompacts(token: string) {
  const res = await fetch('/api/v1/governance/shareholder-compacts/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: ShareholderCompact[] }>;
}

export async function fetchCompactProgress(token: string, compactId: string) {
  const res = await fetch(`/api/v1/governance/shareholder-compacts/${compactId}/progress/`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ targets: (CompactTarget & { achievement_pct: number })[] }>;
}

export async function fetchIUFWIncidents(token: string) {
  const res = await fetch('/api/v1/governance/iufw-incidents/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: IUFWIncident[] }>;
}

export async function fetchIUFWRegister(token: string) {
  const res = await fetch('/api/v1/governance/iufw-incidents/register/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json();
}

export async function createIUFWIncident(token: string, payload: Partial<IUFWIncident>) {
  const res = await fetch('/api/v1/governance/iufw-incidents/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<IUFWIncident>;
}

export async function fetchEntityConfig(token: string) {
  const res = await fetch('/api/v1/entity-config/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: TenantEntityConfig[] }>;
}

export async function createHospitalityRequest(token: string, payload: {
  request_type: string;
  event_date: string;
  guest_count: number;
  contact_name: string;
  contact_phone?: string;
  special_requirements?: string;
  dietary_restrictions?: string;
  operating_context?: string | null;
}): Promise<{ id: string; status: string; contact_name: string; event_date: string; request_type: string }> {
  const r = await fetch('/api/v1/hospitality/requests/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new ApiError(r.status, { detail: 'Failed to create hospitality request' });
  return r.json();
}

// Phase 8 endpoints
export async function fetchAGAuditRequests(token: string) {
  const res = await fetch('/api/v1/governance/ag-audit-requests/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: AGAuditRequest[] }>;
}

export async function fetchAGAuditEvidence(token: string, auditId: string) {
  const res = await fetch(`/api/v1/governance/ag-audit-requests/${auditId}/evidence/`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<AGAuditEvidence[]>;
}

export async function fetchProductionLicences(token: string, contextId?: string) {
  const qs = contextId ? `?operating_context=${contextId}` : '';
  const res = await fetch(`/api/v1/programming/licence-agreements/${qs}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: ProductionLicence[] }>;
}

export async function fetchRentalEnquiries(token: string) {
  const res = await fetch('/api/v1/rental-enquiries/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: VenueRentalEnquiry[] }>;
}

export async function createRentalEnquiry(token: string, payload: Partial<VenueRentalEnquiry>) {
  const res = await fetch('/api/v1/rental-enquiries/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<VenueRentalEnquiry>;
}

export async function fetchCSDVerifications(token: string) {
  const res = await fetch('/api/v1/suppliers/csd/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: SupplierCSDVerification[] }>;
}

// Phase 9 endpoints
export async function fetchConflictDeclarations(token: string) {
  const res = await fetch('/api/v1/governance/conflict-of-interest/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: ConflictOfInterest[] }>;
}

export async function createConflictDeclaration(token: string, payload: Partial<ConflictOfInterest>) {
  const res = await fetch('/api/v1/governance/conflict-of-interest/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<ConflictOfInterest>;
}

export async function fetchRFQList(token: string) {
  const res = await fetch('/api/v1/suppliers/rfq/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: ThreeQuoteRequirement[] }>;
}

export async function createRFQ(token: string, payload: Partial<ThreeQuoteRequirement>) {
  const res = await fetch('/api/v1/suppliers/rfq/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<ThreeQuoteRequirement>;
}

export async function addQuoteToRFQ(token: string, rfqId: string, payload: Partial<SupplierQuote>) {
  const res = await fetch(`/api/v1/suppliers/rfq/${rfqId}/add_quote/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json();
}

export async function fetchPerformanceReports(token: string) {
  const res = await fetch('/api/v1/governance/performance-reports/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: PerformanceReport[] }>;
}

export async function submitPerformanceReport(token: string, reportId: string) {
  const res = await fetch(`/api/v1/governance/performance-reports/${reportId}/submit/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('submit failed');
  return res.json() as Promise<PerformanceReport>;
}

// Phase 10 endpoints
export async function fetchJournalEntries(token: string, contextId?: string) {
  const qs = contextId ? `?operating_context=${contextId}` : '';
  const res = await fetch(`/api/v1/programming/production-journals/${qs}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: ProductionJournalEntry[] }>;
}

export async function createJournalEntry(token: string, payload: Partial<ProductionJournalEntry>) {
  const res = await fetch('/api/v1/programming/production-journals/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<ProductionJournalEntry>;
}

export async function fetchLeaveRequests(token: string) {
  const res = await fetch('/api/v1/accounts/leave-requests/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: LeaveRequest[] }>;
}

export async function createLeaveRequest(token: string, payload: Partial<LeaveRequest>) {
  const res = await fetch('/api/v1/accounts/leave-requests/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<LeaveRequest>;
}

export async function approveLeaveRequest(token: string, id: string) {
  const res = await fetch(`/api/v1/accounts/leave-requests/${id}/approve/`, {
    method: 'POST', headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('approve failed');
  return res.json() as Promise<LeaveRequest>;
}

export async function fetchLiquorLicences(token: string) {
  const res = await fetch('/api/v1/operations/liquor-licences/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: LiquorLicence[] }>;
}

export async function fetchSafetyRecords(token: string) {
  const res = await fetch('/api/v1/operations/safety-compliance/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: SafetyComplianceRecord[] }>;
}

export async function fetchDonors(token: string) {
  const res = await fetch('/api/v1/patrons/donors/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: Donor[] }>;
}

export async function fetchDonations(token: string) {
  const res = await fetch('/api/v1/patrons/donations/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: Donation[] }>;
}

export async function createDonor(token: string, payload: Partial<Donor>) {
  const res = await fetch('/api/v1/patrons/donors/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<Donor>;
}

export async function fetchBoardMembers(token: string) {
  const res = await fetch('/api/v1/governance/board-members/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: BoardMemberProfile[] }>;
}

// Phase 5 full endpoints
export async function fetchGLAccounts(token: string) {
  const res = await fetch('/api/v1/finance/accounts/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: GLAccount[] }>;
}

export async function fetchTrialBalance(token: string, financialYear: string) {
  const res = await fetch(`/api/v1/finance/accounts/trial_balance/?financial_year=${financialYear}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ account_code: string; account_name: string; category: string; total_debit: number; total_credit: number; net: number }[]>;
}

export async function fetchGLJournals(token: string, financialYear?: string) {
  const qs = financialYear ? `?financial_year=${financialYear}` : '';
  const res = await fetch(`/api/v1/finance/journals/${qs}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: GLJournalEntry[] }>;
}

export async function postGLJournal(token: string, journalId: string) {
  const res = await fetch(`/api/v1/finance/journals/${journalId}/post_entry/`, {
    method: 'POST', headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('post failed');
  return res.json() as Promise<GLJournalEntry>;
}

export async function fetchDeferredIncome(token: string) {
  const res = await fetch('/api/v1/finance/deferred-income/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: DeferredIncome[] }>;
}

export async function recogniseDeferredIncome(token: string, id: string, amount: number) {
  const res = await fetch(`/api/v1/finance/deferred-income/${id}/recognise/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount }),
  });
  if (!res.ok) throw new Error('recognise failed');
  return res.json() as Promise<DeferredIncome>;
}

export async function fetchSection32Reports(token: string) {
  const res = await fetch('/api/v1/governance/section32/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: Section32Report[] }>;
}

export async function submitSection32Report(token: string, id: string) {
  const res = await fetch(`/api/v1/governance/section32/${id}/submit/`, {
    method: 'POST', headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('submit failed');
  return res.json() as Promise<Section32Report>;
}

export async function fetchAnnualReports(token: string) {
  const res = await fetch('/api/v1/governance/annual-reports/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: AnnualReport[] }>;
}

export async function approveAnnualReport(token: string, id: string) {
  const res = await fetch(`/api/v1/governance/annual-reports/${id}/approve/`, {
    method: 'POST', headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('approve failed');
  return res.json() as Promise<AnnualReport>;
}

export async function fetchAGAuditPackage(token: string, auditId: string) {
  const res = await fetch(`/api/v1/governance/ag-audit-requests/${auditId}/generate_package/`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<AGAuditPackage>;
}

// Phase 6 full endpoints
export async function fetchSetlistWorks(token: string, performanceId?: string) {
  const qs = performanceId ? `?performance=${performanceId}` : '';
  const res = await fetch(`/api/v1/programming/setlist-works/${qs}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: SetlistWork[] }>;
}

export async function createSetlistWork(token: string, payload: Partial<SetlistWork>) {
  const res = await fetch('/api/v1/programming/setlist-works/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<SetlistWork>;
}

export async function fetchSAMROReport(token: string, dateFrom: string, dateTo: string) {
  const res = await fetch(`/api/v1/programming/setlist-works/samro_report/?date_from=${dateFrom}&date_to=${dateTo}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ works: Record<string, string>[]; total_works: number }>;
}

export async function fetchCoProducers(token: string) {
  const res = await fetch('/api/v1/programming/co-producers/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: CoProducer[] }>;
}

export async function fetchCoProductionSettlements(token: string) {
  const res = await fetch('/api/v1/programming/co-production-settlements/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: CoProductionSettlement[] }>;
}

export async function agreeCoProductionSettlement(token: string, id: string) {
  const res = await fetch(`/api/v1/programming/co-production-settlements/${id}/agree/`, {
    method: 'POST', headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('agree failed');
  return res.json() as Promise<CoProductionSettlement>;
}

export async function fetchRentalBookings(token: string) {
  const res = await fetch('/api/v1/rental-bookings/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: RentalBooking[] }>;
}

export async function fetchRentalInvoices(token: string) {
  const res = await fetch('/api/v1/rental-invoices/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: RentalInvoice[] }>;
}

export async function createRentalInvoice(token: string, bookingId: string, invoiceType: string) {
  const res = await fetch(`/api/v1/rental-bookings/${bookingId}/invoice/`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ invoice_type: invoiceType }),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<RentalInvoice>;
}

export async function fetchFestivals(token: string) {
  const res = await fetch('/api/v1/festivals/festivals/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: Festival[] }>;
}

export async function fetchFestivalPasses(token: string, festivalId?: string) {
  const qs = festivalId ? `?festival=${festivalId}` : '';
  const res = await fetch(`/api/v1/festivals/passes/${qs}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: FestivalPass[] }>;
}

export async function createFestivalPass(token: string, payload: Partial<FestivalPass>) {
  const res = await fetch('/api/v1/festivals/passes/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<FestivalPass>;
}

export async function fetchResidentCompanies(token: string) {
  const res = await fetch('/api/v1/resident-companies/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: ResidentCompany[] }>;
}

export async function fetchUnionAgreements(token: string) {
  const res = await fetch('/api/v1/operations/union-agreements/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: UnionAgreement[] }>;
}

export async function fetchUnionRates(token: string) {
  const res = await fetch('/api/v1/operations/union-rates/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: UnionCallRate[] }>;
}

// Gap-fill endpoints A
export async function fetchMaintenanceTickets(token: string) {
  const res = await fetch('/api/v1/operations/maintenance-tickets/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: MaintenanceTicket[] }>;
}
export async function createMaintenanceTicket(token: string, payload: Partial<MaintenanceTicket>) {
  const res = await fetch('/api/v1/operations/maintenance-tickets/', { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<MaintenanceTicket>;
}
export async function resolveMaintenanceTicket(token: string, id: string, notes: string) {
  const res = await fetch(`/api/v1/operations/maintenance-tickets/${id}/resolve/`, { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ resolution_notes: notes }) });
  if (!res.ok) throw new Error('resolve failed');
  return res.json() as Promise<MaintenanceTicket>;
}
export async function fetchMaintenanceSchedules(token: string) {
  const res = await fetch('/api/v1/operations/maintenance-schedules/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: MaintenanceSchedule[] }>;
}
export async function fetchInspections(token: string) {
  const res = await fetch('/api/v1/operations/inspections/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: InspectionRecord[] }>;
}
export async function fetchVenueDowntime(token: string) {
  const res = await fetch('/api/v1/operations/venue-downtime/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: VenueDowntime[] }>;
}
export async function fetchCueSheets(token: string, contextId?: string) {
  const qs = contextId ? `?operating_context=${contextId}` : '';
  const res = await fetch(`/api/v1/technical/cue-sheets/${qs}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: CueSheet[] }>;
}
export async function fetchCueLines(token: string, cueSheetId: string) {
  const res = await fetch(`/api/v1/technical/cue-lines/?cue_sheet=${cueSheetId}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: CueLine[] }>;
}
export async function fetchProps(token: string) {
  const res = await fetch('/api/v1/technical/props/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: PropsItem[] }>;
}
export async function fetchWardrobe(token: string) {
  const res = await fetch('/api/v1/technical/wardrobe/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: WardrobeItem[] }>;
}
export async function fetchComplaints(token: string) {
  const res = await fetch('/api/v1/operations/complaints/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: AudienceComplaint[] }>;
}
export async function createComplaint(token: string, payload: Partial<AudienceComplaint>) {
  const res = await fetch('/api/v1/operations/complaints/', { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<AudienceComplaint>;
}
export async function fetchAccessibilityRequirements(token: string) {
  const res = await fetch('/api/v1/operations/accessibility/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: AccessibilityRequirement[] }>;
}

// Gap-fill endpoints B
export async function fetchMediaContacts(token: string) {
  const res = await fetch('/api/v1/marketing/media-contacts/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: MediaContact[] }>;
}
export async function createMediaContact(token: string, payload: Partial<MediaContact>) {
  const res = await fetch('/api/v1/marketing/media-contacts/', { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<MediaContact>;
}
export async function fetchNewsletters(token: string) {
  const res = await fetch('/api/v1/marketing/newsletters/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: NewsletterCampaign[] }>;
}
export async function createNewsletter(token: string, payload: Partial<NewsletterCampaign>) {
  const res = await fetch('/api/v1/marketing/newsletters/', { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<NewsletterCampaign>;
}
export async function fetchCIChecks(token: string) {
  const res = await fetch('/api/v1/marketing/ci-compliance/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: CIComplianceCheck[] }>;
}
export async function createCICheck(token: string, payload: Partial<CIComplianceCheck>) {
  const res = await fetch('/api/v1/marketing/ci-compliance/', { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<CIComplianceCheck>;
}
export async function approveCICheck(token: string, id: string) {
  const res = await fetch(`/api/v1/marketing/ci-compliance/${id}/approve/`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('approve failed');
  return res.json() as Promise<CIComplianceCheck>;
}
export async function fetchTouringProductions(token: string) {
  const res = await fetch('/api/v1/programming/touring-productions/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: TouringProduction[] }>;
}
export async function fetchTouringVenueDates(token: string, touringProductionId: string) {
  const res = await fetch(`/api/v1/programming/touring-venue-dates/?touring_production=${touringProductionId}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: TouringVenueDate[] }>;
}
export async function fetchRecurringProductions(token: string) {
  const res = await fetch('/api/v1/programming/recurring-productions/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ results: RecurringProduction[] }>;
}
export async function createRecurringProduction(token: string, payload: Partial<RecurringProduction>) {
  const res = await fetch('/api/v1/programming/recurring-productions/', { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error('create failed');
  return res.json() as Promise<RecurringProduction>;
}
export async function fetchExpiryAlerts(token: string) {
  const res = await fetch('/api/v1/governance/expiry-alerts/upcoming/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<ExpiryAlert[]>;
}
export async function acknowledgeExpiryAlert(token: string, id: string) {
  const res = await fetch(`/api/v1/governance/expiry-alerts/${id}/acknowledge/`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('acknowledge failed');
  return res.json() as Promise<ExpiryAlert>;
}
export async function fetchOverdueTasks(token: string) {
  const res = await fetch('/api/v1/tasks/overdue_summary/', { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('fetch failed');
  return res.json() as Promise<{ overdue_tasks: { id: string; title: string; due_date: string; days_overdue: number; status: string }[]; total: number }>;
}

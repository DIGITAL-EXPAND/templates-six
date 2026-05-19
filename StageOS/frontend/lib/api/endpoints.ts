import { apiRequest, apiUrl } from './client';
import type {
  AuthTokens,
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
  return apiRequest<PaginatedResponse<BudgetItem>>(`/api/v1/budgets/${queryString(params)}`, { token });
}

export function fetchBudgetLines(token: string, budgetId: string) {
  return apiRequest<PaginatedResponse<BudgetLineItem>>(`/api/v1/budget-lines/?budget=${budgetId}`, { token });
}

export function createBudgetLine(token: string, data: CreateBudgetLinePayload) {
  return apiRequest<BudgetLineItem>('/api/v1/budget-lines/', { method: 'POST', token, body: data });
}

export function approveBudget(token: string, budgetId: string) {
  return apiRequest<BudgetItem>(`/api/v1/budgets/${budgetId}/approve/`, { method: 'POST', token });
}

// Board meetings
export function fetchBoardMeetings(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<BoardMeetingItem>>(`/api/v1/board-meetings/${queryString(params)}`, { token });
}

export function createBoardMeeting(token: string, data: CreateBoardMeetingPayload) {
  return apiRequest<BoardMeetingItem>('/api/v1/board-meetings/', { method: 'POST', token, body: data });
}

export function fetchBoardResolutions(token: string, meetingId: string) {
  return apiRequest<PaginatedResponse<BoardResolutionItem>>(`/api/v1/board-resolutions/?meeting=${meetingId}`, { token });
}

// Procurement
export function fetchPurchaseRequisitions(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<PurchaseRequisitionItem>>(`/api/v1/requisitions/${queryString(params)}`, { token });
}

export function createPurchaseRequisition(token: string, data: CreatePurchaseRequisitionPayload) {
  return apiRequest<PurchaseRequisitionItem>('/api/v1/requisitions/', { method: 'POST', token, body: data });
}

export function approvePurchaseRequisition(token: string, id: string) {
  return apiRequest<PurchaseRequisitionItem>(`/api/v1/requisitions/${id}/approve/`, { method: 'POST', token });
}

export function rejectPurchaseRequisition(token: string, id: string, reason: string) {
  return apiRequest<PurchaseRequisitionItem>(`/api/v1/requisitions/${id}/reject/`, { method: 'POST', token, body: { reason } });
}

export function fetchPurchaseOrders(token: string, params?: Record<string, string>) {
  return apiRequest<PaginatedResponse<PurchaseOrderItem>>(`/api/v1/purchase-orders/${queryString(params)}`, { token });
}

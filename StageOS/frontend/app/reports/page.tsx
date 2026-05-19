'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import {
  AuditTrailReport,
  BoardSummaryReportView,
  CalendarIssuesReportView,
  ContractStatusReportView,
  DepartmentReadinessReportView,
  EvidenceGapsReportView,
  ExecutiveSummaryReport,
  ReportCard,
  RiskRegisterReportView,
  SupplierReadinessReportView,
  WorkspaceReadinessReport,
  YouthSummaryReportView,
} from '@/components/reports/report-components';
import { PageHeader } from '@/components/ui/page-header';
import { ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  fetchAuditExport,
  fetchBoardSummaryReport,
  fetchCalendarIssuesReport,
  fetchContextReadiness,
  fetchContractStatusReport,
  fetchDepartmentReadiness,
  fetchDepartments,
  fetchEvidenceGapsReport,
  fetchExecutiveSummary,
  fetchOperatingContexts,
  fetchOperatingProfile,
  fetchRiskRegister,
  fetchSupplierReadinessReport,
  fetchYouthProjects,
  fetchYouthSummary,
} from '@/lib/api/endpoints';
import type {
  AuditEventItem,
  BoardSummaryReport,
  CalendarIssuesReport,
  ContextReadiness,
  ContractStatusReport,
  DepartmentListItem,
  DepartmentReadinessReport,
  EvidenceGapsReport,
  ExecutiveSummary,
  OperatingContextListItem,
  OperatingProfile,
  RiskRegisterReport,
  SupplierReadinessReport,
  YouthProjectItem,
  YouthSummaryReport,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';
import { dashboardKind } from '@/lib/role-experience';

type ActiveReport =
  | 'executive'
  | 'board'
  | 'workspace'
  | 'department'
  | 'risk'
  | 'contracts'
  | 'suppliers'
  | 'evidence'
  | 'calendar'
  | 'youth'
  | 'audit';

export default function ReportsPage() {
  const { tokens } = useAuth();
  const [profile, setProfile] = useState<OperatingProfile | null>(null);
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null);
  const [boardSummary, setBoardSummary] = useState<BoardSummaryReport | null>(null);
  const [riskReport, setRiskReport] = useState<RiskRegisterReport | null>(null);
  const [contractReport, setContractReport] = useState<ContractStatusReport | null>(null);
  const [supplierReport, setSupplierReport] = useState<SupplierReadinessReport | null>(null);
  const [evidenceReport, setEvidenceReport] = useState<EvidenceGapsReport | null>(null);
  const [calendarReport, setCalendarReport] = useState<CalendarIssuesReport | null>(null);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [youthProjects, setYouthProjects] = useState<YouthProjectItem[]>([]);
  const [workspaceReport, setWorkspaceReport] = useState<ContextReadiness | null>(null);
  const [departmentReport, setDepartmentReport] = useState<DepartmentReadinessReport | null>(null);
  const [youthReport, setYouthReport] = useState<YouthSummaryReport | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEventItem[]>([]);
  const [active, setActive] = useState<ActiveReport>('executive');
  const [selectedWorkspace, setSelectedWorkspace] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [selectedYouthProject, setSelectedYouthProject] = useState('');
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([
      fetchExecutiveSummary(tokens.access),
      fetchBoardSummaryReport(tokens.access),
      fetchRiskRegister(tokens.access),
      fetchContractStatusReport(tokens.access),
      fetchSupplierReadinessReport(tokens.access),
      fetchEvidenceGapsReport(tokens.access),
      fetchCalendarIssuesReport(tokens.access),
      fetchOperatingContexts(tokens.access),
      fetchDepartments(tokens.access),
      fetchYouthProjects(tokens.access),
      fetchAuditExport(tokens.access),
      fetchOperatingProfile(tokens.access),
    ])
      .then(([
        summaryResult,
        boardResult,
        riskResult,
        contractResult,
        supplierResult,
        evidenceResult,
        calendarResult,
        workspaceResult,
        departmentResult,
        youthProjectResult,
        auditResult,
        profileResult,
      ]) => {
        if (!mounted) return;
        if (summaryResult.status === 'fulfilled') setSummary(summaryResult.value);
        else if (summaryResult.reason instanceof ApiError && summaryResult.reason.status === 403) setPermissionDenied(true);
        if (boardResult.status === 'fulfilled') setBoardSummary(boardResult.value);
        if (riskResult.status === 'fulfilled') setRiskReport(riskResult.value);
        if (contractResult.status === 'fulfilled') setContractReport(contractResult.value);
        if (supplierResult.status === 'fulfilled') setSupplierReport(supplierResult.value);
        if (evidenceResult.status === 'fulfilled') setEvidenceReport(evidenceResult.value);
        if (calendarResult.status === 'fulfilled') setCalendarReport(calendarResult.value);
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
        if (youthProjectResult.status === 'fulfilled') setYouthProjects(youthProjectResult.value.results);
        if (auditResult.status === 'fulfilled') setAuditEvents(auditResult.value.results);
        if (profileResult.status === 'fulfilled') setProfile(profileResult.value);

        // Filter departments to user's own memberships unless admin/executive
        if (departmentResult.status === 'fulfilled') {
          const allDepts = departmentResult.value.results;
          const resolvedProfile = profileResult.status === 'fulfilled' ? profileResult.value : null;
          const role = dashboardKind(resolvedProfile);
          const isAdminLevel = role === 'admin' || role === 'executive';
          if (isAdminLevel || !resolvedProfile?.memberships?.length) {
            setDepartments(allDepts);
          } else {
            const memberDeptIds = new Set(resolvedProfile.memberships.map((m) => m.department.id));
            setDepartments(allDepts.filter((d) => memberDeptIds.has(d.id)));
          }
        }
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  async function loadWorkspaceReport(id: string) {
    if (!tokens?.access || !id) return;
    setSelectedWorkspace(id);
    setError('');
    try {
      setWorkspaceReport(await fetchContextReadiness(tokens.access, id));
      setActive('workspace');
    } catch (err) {
      handleError(err);
    }
  }

  async function loadDepartmentReport(id: string) {
    if (!tokens?.access || !id) return;
    setSelectedDepartment(id);
    setError('');
    try {
      setDepartmentReport(await fetchDepartmentReadiness(tokens.access, id));
      setActive('department');
    } catch (err) {
      handleError(err);
    }
  }

  async function loadYouthReport(id: string) {
    if (!tokens?.access || !id) return;
    setSelectedYouthProject(id);
    setError('');
    try {
      setYouthReport(await fetchYouthSummary(tokens.access, id));
      setActive('youth');
    } catch (err) {
      handleError(err);
    }
  }

  function handleError(err: unknown) {
    if (err instanceof ApiError) {
      if (err.status === 403) setPermissionDenied(true);
      setError(JSON.stringify(err.payload ?? { detail: err.message }));
    } else {
      setError('Unexpected error loading report.');
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="Executive, board, Workspace, department, youth, evidence, calendar and Audit Trail reporting in one place."
          eyebrow="Reports"
          title="Reports"
        />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading reports" /> : (
          <>
            {/* Organisation Health summary strip */}
            {summary && (
              <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <HealthCard
                  label="Active Productions"
                  value={summary.total_contexts}
                  colour="blue"
                />
                <HealthCard
                  label="Open Risks"
                  value={summary.open_risks}
                  colour={summary.open_risks > 0 ? 'red' : 'green'}
                />
                <HealthCard
                  label="Tasks Overdue"
                  value={summary.open_tasks}
                  colour={summary.open_tasks > 0 ? 'amber' : 'green'}
                />
                <HealthCard
                  label="Pending Approvals"
                  value={summary.pending_approvals}
                  colour={summary.pending_approvals > 0 ? 'amber' : 'green'}
                />
              </section>
            )}

            {/* Show Report — productions list */}
            {workspaces.length > 0 && (
              <section className="rounded-lg border border-slate-200 bg-white p-4">
                <h2 className="mb-3 text-base font-bold text-slate-950">Show Report</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-100">
                        <th className="pb-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Production</th>
                        <th className="pb-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
                        <th className="pb-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Readiness</th>
                        <th className="pb-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Opening</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {workspaces.map(ws => (
                        <tr key={ws.id} className="py-1">
                          <td className="py-2 font-medium text-slate-900">{ws.title}</td>
                          <td className="py-2">
                            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs capitalize">
                              {ws.status.replace(/_/g, ' ')}
                            </span>
                          </td>
                          <td className="py-2">
                            {ws.readiness_score !== undefined ? (
                              <div className="flex items-center gap-2">
                                <div className="h-1.5 w-24 overflow-hidden rounded-full bg-slate-100">
                                  <div
                                    className={`h-1.5 rounded-full ${ws.readiness_score >= 90 ? 'bg-green-500' : ws.readiness_score >= 60 ? 'bg-amber-400' : 'bg-red-500'}`}
                                    style={{ width: `${ws.readiness_score}%` }}
                                  />
                                </div>
                                <span className="text-xs text-slate-500">{ws.readiness_score}%</span>
                              </div>
                            ) : <span className="text-xs text-slate-400">—</span>}
                          </td>
                          <td className="py-2 text-xs text-slate-500">
                            {ws.opening_date ? new Date(ws.opening_date).toLocaleDateString('en-ZA') : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <ReportCard access={summary ? 'ready' : 'restricted'} description="Leadership totals, risks, tasks, approvals, budgets, KPIs and openings." onOpen={() => setActive('executive')} title="Organisation Overview" />
              <ReportCard access={boardSummary ? (boardSummary.board_ready ? 'ready' : 'attention_required') : 'restricted'} description="Board-ready pilot signal across readiness, risks, approvals, evidence and calendar issues." onOpen={() => setActive('board')} title="Board Summary" />
              <ReportCard access={workspaces.length ? 'ready' : 'empty'} description="Detailed readiness for a selected Workspace." onOpen={() => setActive('workspace')} title="Workspace Readiness" />
              <ReportCard access={departments.length ? 'ready' : 'empty'} description="Department task, approval and risk readiness." onOpen={() => setActive('department')} title="Department Status Report" />
              <ReportCard access={riskReport ? 'ready' : 'restricted'} description="Tenant-scoped risk register with status, owner and mitigation." onOpen={() => setActive('risk')} title="Risk Register" />
              <ReportCard access={contractReport ? 'ready' : 'restricted'} description="Contract value, status and signature readiness." onOpen={() => setActive('contracts')} title="Contract Status" />
              <ReportCard access={supplierReport ? 'ready' : 'restricted'} description="Supplier CSD, document and engagement readiness." onOpen={() => setActive('suppliers')} title="Supplier Readiness" />
              <ReportCard access={evidenceReport ? (evidenceReport.total ? 'gaps_found' : 'ready') : 'restricted'} description="Missing required evidence on tasks and Process steps." onOpen={() => setActive('evidence')} title="Evidence Gaps" />
              <ReportCard access={calendarReport ? (calendarReport.open ? 'issues_open' : 'ready') : 'restricted'} description="Open calendar issues, severity and department ownership." onOpen={() => setActive('calendar')} title="Calendar Issues" />
              <ReportCard access={youthProjects.length ? 'ready' : 'empty'} description="Youth project consent, attendance, facilitator and assessment summary." onOpen={() => setActive('youth')} title="Youth Summary" />
              <ReportCard access={auditEvents.length ? 'ready' : 'empty'} description="Audit Trail export and recent events." onOpen={() => setActive('audit')} title="Audit Trail" />
            </section>

            <section className="grid gap-3 md:grid-cols-3">
              <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => loadWorkspaceReport(event.target.value)} value={selectedWorkspace}>
                <option value="">Select Workspace Readiness</option>
                {workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.title}</option>)}
              </select>
              <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => loadDepartmentReport(event.target.value)} value={selectedDepartment}>
                <option value="">Select Department Readiness</option>
                {departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}
              </select>
              <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => loadYouthReport(event.target.value)} value={selectedYouthProject}>
                <option value="">Select Youth Summary</option>
                {youthProjects.map((project) => <option key={project.id} value={project.id}>{project.operating_context}</option>)}
              </select>
            </section>

            {active === 'executive' ? <ExecutiveSummaryReport summary={summary} /> : null}
            {active === 'board' ? <BoardSummaryReportView report={boardSummary} /> : null}
            {active === 'workspace' ? <WorkspaceReadinessReport readiness={workspaceReport} /> : null}
            {active === 'department' ? <DepartmentReadinessReportView report={departmentReport} /> : null}
            {active === 'risk' ? <RiskRegisterReportView report={riskReport} /> : null}
            {active === 'contracts' ? <ContractStatusReportView report={contractReport} /> : null}
            {active === 'suppliers' ? <SupplierReadinessReportView report={supplierReport} /> : null}
            {active === 'evidence' ? <EvidenceGapsReportView report={evidenceReport} /> : null}
            {active === 'calendar' ? <CalendarIssuesReportView report={calendarReport} /> : null}
            {active === 'youth' ? <YouthSummaryReportView report={youthReport} /> : null}
            {active === 'audit' ? <AuditTrailReport events={auditEvents} /> : null}
          </>
        )}
      </div>
    </AppShell>
  );
}

type HealthColour = 'blue' | 'green' | 'amber' | 'red';

const HEALTH_COLOURS: Record<HealthColour, { card: string; value: string }> = {
  blue:  { card: 'border-blue-100 bg-blue-50',   value: 'text-blue-800' },
  green: { card: 'border-green-100 bg-green-50', value: 'text-green-800' },
  amber: { card: 'border-amber-100 bg-amber-50', value: 'text-amber-800' },
  red:   { card: 'border-red-100 bg-red-50',     value: 'text-red-800' },
};

function HealthCard({ label, value, colour }: { label: string; value: number; colour: HealthColour }) {
  const c = HEALTH_COLOURS[colour];
  return (
    <article className={`rounded-lg border p-4 text-center ${c.card}`}>
      <div className={`text-3xl font-bold ${c.value}`}>{value}</div>
      <div className="mt-1 text-sm font-semibold text-slate-600">{label}</div>
    </article>
  );
}

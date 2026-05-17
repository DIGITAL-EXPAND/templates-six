import { MetricCard } from '@/components/dashboard/metric-card';
import { ReadinessBadge, labelFromValue, money } from '@/components/readiness/shared';
import { EmptyState, PermissionDeniedState } from '@/components/ui/states';
import { BarChart3, ClipboardList, FileText, ShieldCheck } from 'lucide-react';
import type {
  AuditEventItem,
  BoardSummaryReport,
  CalendarIssuesReport,
  ContextReadiness,
  ContractStatusReport,
  DepartmentReadinessReport,
  EvidenceGapsReport,
  ExecutiveSummary,
  RiskRegisterReport,
  SupplierReadinessReport,
  YouthSummaryReport,
} from '@/lib/api/types';

export function ReportCard({
  title,
  description,
  access,
  onOpen,
}: {
  title: string;
  description: string;
  access: string;
  onOpen: () => void;
}) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-950">{title}</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
          <p className="mt-2 text-xs font-semibold text-slate-500">Last viewed/exported: not available</p>
        </div>
        <ReadinessBadge value={access} />
      </div>
      <button className="mt-4 h-9 rounded-md bg-blue-600 px-3 text-sm font-bold text-white" onClick={onOpen} type="button">
        Open report
      </button>
    </article>
  );
}

export function ExecutiveSummaryReport({ summary }: { summary: ExecutiveSummary | null }) {
  if (!summary) return <PermissionDeniedState />;
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <MetricCard detail="Visible active Workspaces" icon={BarChart3} label="Total Workspaces" value={summary.total_contexts} />
      <MetricCard detail="Average readiness" icon={ShieldCheck} label="Readiness" value={`${summary.average_readiness}%`} />
      <MetricCard detail="Open risks" icon={ClipboardList} label="Risks" value={summary.open_risks} />
      <MetricCard detail="High or critical" icon={ClipboardList} label="High risks" value={summary.high_risks} />
      <MetricCard detail="Pending approval requests" icon={FileText} label="Approvals" value={summary.pending_approvals} />
      <MetricCard detail="Open tasks" icon={FileText} label="Tasks" value={summary.open_tasks} />
      <MetricCard detail="Total budget" icon={BarChart3} label="Budget" value={money(summary.total_budget)} />
      <MetricCard detail="Total spend" icon={BarChart3} label="Spend" value={money(summary.total_spend)} />
    </section>
  );
}

export function WorkspaceReadinessReport({ readiness }: { readiness: ContextReadiness | null }) {
  if (!readiness) return <EmptyState title="Select a Workspace" description="Workspace Readiness will appear when a Workspace is selected." />;
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4">
      <h2 className="text-base font-bold text-slate-950">{readiness.context.title}</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <MetricCard detail="Workspace readiness" icon={ShieldCheck} label="Readiness" value={`${readiness.context.readiness_score}%`} />
        <MetricCard detail="Open task count" icon={FileText} label="Open tasks" value={readiness.tasks.open} />
        <MetricCard detail="Documents" icon={FileText} label="Documents" value={readiness.documents_count} />
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <ReadinessBadge value={readiness.campaign?.status ?? 'marketing_unavailable'} />
        <ReadinessBadge value={readiness.rider?.status ?? 'technical_unavailable'} />
        <ReadinessBadge value={readiness.foh_plan?.status ?? 'foh_unavailable'} />
        <ReadinessBadge value={readiness.ticketing?.setup_status ?? 'ticketing_unavailable'} />
      </div>
    </section>
  );
}

export function DepartmentReadinessReportView({ report }: { report: DepartmentReadinessReport | null }) {
  if (!report) return <EmptyState title="Select a department" description="Department Readiness will appear when a department is selected." />;
  return (
    <section className="grid gap-4 md:grid-cols-3">
      <MetricCard detail={report.department.name} icon={BarChart3} label="Linked Workspaces" value={report.contexts_count} />
      <MetricCard detail="Department open tasks" icon={FileText} label="Open tasks" value={report.open_tasks} />
      <MetricCard detail="Past due tasks" icon={FileText} label="Overdue tasks" value={report.overdue_tasks} />
      <MetricCard detail="Done tasks" icon={ShieldCheck} label="Completed tasks" value={report.completed_tasks} />
      <MetricCard detail="Awaiting decisions" icon={ShieldCheck} label="Approvals" value={report.pending_approvals} />
      <MetricCard detail="Open department risks" icon={ClipboardList} label="Risks" value={report.open_risks} />
    </section>
  );
}

export function YouthSummaryReportView({ report }: { report: YouthSummaryReport | null }) {
  if (!report) return <EmptyState title="Select a youth project" description="Youth Summary will appear when a youth project is selected." />;
  return (
    <section className="grid gap-4 md:grid-cols-3">
      <MetricCard detail={report.project.title} icon={BarChart3} label="Learners" value={`${report.total_learners}/${report.target_learners}`} />
      <MetricCard detail={`${report.schools} schools`} icon={ShieldCheck} label="Consent" value={`${report.consent_rate}%`} />
      <MetricCard detail="Completed sessions" icon={FileText} label="Sessions" value={`${report.sessions_completed}/${report.sessions_total}`} />
      <MetricCard detail="Average attendance" icon={FileText} label="Attendance" value={`${report.attendance_rate}%`} />
      <MetricCard detail="Vetted facilitators" icon={ShieldCheck} label="Facilitators" value={`${report.facilitators_vetted}/${report.facilitators}`} />
      <MetricCard detail="Assessment count" icon={ClipboardList} label="Assessments" value={report.assessments_count} />
    </section>
  );
}

export function BoardSummaryReportView({ report }: { report: BoardSummaryReport | null }) {
  if (!report) return <PermissionDeniedState />;
  return (
    <section className="grid gap-4 md:grid-cols-3">
      <MetricCard detail="Visible active Workspaces" icon={BarChart3} label="Workspaces" value={report.workspaces} />
      <MetricCard detail="Average readiness" icon={ShieldCheck} label="Readiness" value={`${report.average_readiness}%`} />
      <MetricCard detail="High or critical open risks" icon={ClipboardList} label="High risks" value={report.high_risks} />
      <MetricCard detail="Awaiting decisions" icon={FileText} label="Approvals" value={report.pending_approvals} />
      <MetricCard detail="Missing required evidence" icon={FileText} label="Evidence gaps" value={report.evidence_gaps} />
      <MetricCard detail="Open calendar issues" icon={ClipboardList} label="Calendar issues" value={report.calendar_issues} />
      <MetricCard detail="Pilot readiness signal" icon={ShieldCheck} label="Board ready" value={report.board_ready ? 'Yes' : 'No'} />
    </section>
  );
}

export function RiskRegisterReportView({ report }: { report: RiskRegisterReport | null }) {
  if (!report) return <PermissionDeniedState />;
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-3">
        <MetricCard detail="All tenant-scoped risks" icon={ClipboardList} label="Risks" value={report.total} />
        <MetricCard detail="Not closed" icon={ClipboardList} label="Open" value={report.open} />
        <MetricCard detail="High or critical" icon={ShieldCheck} label="High/Critical" value={report.high_or_critical} />
      </div>
      <ReportRows rows={report.results.map((risk) => ({
        id: risk.id,
        title: risk.title,
        detail: `${risk.workspace ?? 'No Workspace'} - ${risk.owner ?? 'No owner'}`,
        badges: [risk.level, risk.status],
        note: risk.mitigation || 'No mitigation recorded',
      }))} />
    </section>
  );
}

export function ContractStatusReportView({ report }: { report: ContractStatusReport | null }) {
  if (!report) return <PermissionDeniedState />;
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-4">
        <MetricCard detail="All contracts" icon={FileText} label="Contracts" value={report.total} />
        <MetricCard detail="Contract value" icon={BarChart3} label="Value" value={money(report.total_value)} />
        <MetricCard detail="Awaiting signatures" icon={FileText} label="Pending" value={report.pending_signature} />
        <MetricCard detail="Signed contracts" icon={ShieldCheck} label="Signed" value={report.signed} />
      </div>
      <ReportRows rows={report.results.map((contract) => ({
        id: contract.id,
        title: contract.counterparty,
        detail: `${contract.workspace} - ${labelFromValue(contract.type)}`,
        badges: [contract.status],
        note: `${money(contract.value)} - signatures ${contract.signatures}`,
      }))} />
    </section>
  );
}

export function SupplierReadinessReportView({ report }: { report: SupplierReadinessReport | null }) {
  if (!report) return <PermissionDeniedState />;
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-4">
        <MetricCard detail="Supplier profiles" icon={BarChart3} label="Suppliers" value={report.total} />
        <MetricCard detail="CSD verified" icon={ShieldCheck} label="Verified" value={report.verified} />
        <MetricCard detail="Unverified suppliers" icon={ClipboardList} label="Pending" value={report.pending_verification} />
        <MetricCard detail="Missing or unverified documents" icon={FileText} label="Doc gaps" value={report.document_gaps} />
      </div>
      <ReportRows rows={report.results.map((supplier) => ({
        id: supplier.id,
        title: supplier.name,
        detail: supplier.category,
        badges: [supplier.status, supplier.csd_verified ? 'csd_verified' : 'csd_pending'],
        note: `${supplier.documents_missing_or_unverified} document gaps - ${supplier.workspaces.join(', ') || 'No Workspace'}`,
      }))} />
    </section>
  );
}

export function EvidenceGapsReportView({ report }: { report: EvidenceGapsReport | null }) {
  if (!report) return <PermissionDeniedState />;
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-3">
        <MetricCard detail="Total missing evidence" icon={FileText} label="Gaps" value={report.total} />
        <MetricCard detail="Evidence-required tasks" icon={ClipboardList} label="Task gaps" value={report.task_gaps} />
        <MetricCard detail="Evidence-required Process steps" icon={ShieldCheck} label="Process gaps" value={report.process_step_gaps} />
      </div>
      <ReportRows rows={report.results.map((gap) => ({
        id: `${gap.type}-${gap.id}`,
        title: gap.title,
        detail: gap.workspace,
        badges: [gap.type],
        note: `${gap.owner ?? 'No owner'}${gap.due_date ? ` - due ${gap.due_date}` : ''}`,
      }))} />
    </section>
  );
}

export function CalendarIssuesReportView({ report }: { report: CalendarIssuesReport | null }) {
  if (!report) return <PermissionDeniedState />;
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="grid gap-3 border-b border-slate-200 p-4 md:grid-cols-3">
        <MetricCard detail="All calendar issues" icon={ClipboardList} label="Issues" value={report.total} />
        <MetricCard detail="Not resolved" icon={FileText} label="Open" value={report.open} />
        <MetricCard detail="Open high or critical" icon={ShieldCheck} label="High/Critical" value={report.critical_or_high} />
      </div>
      <ReportRows rows={report.results.map((issue) => ({
        id: issue.id,
        title: issue.title,
        detail: `${issue.workspace ?? 'No Workspace'} - ${issue.department ?? 'No department'}`,
        badges: [issue.severity, issue.status],
        note: `${issue.raised_by ?? 'Unknown'}${issue.due_date ? ` - due ${issue.due_date}` : ''}`,
      }))} />
    </section>
  );
}

export function AuditTrailReport({ events }: { events: AuditEventItem[] }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-base font-bold text-slate-950">Audit Trail</h2>
      </div>
      <div className="divide-y divide-slate-100">
        {events.length ? events.slice(0, 20).map((event) => (
          <div className="px-4 py-3" key={event.id}>
            <div className="text-sm font-bold text-slate-900">{labelFromValue(event.event_type)}</div>
            <div className="mt-1 text-xs text-slate-500">
              {event.actor_email ?? event.actor ?? 'System'} - {event.target_type ?? 'Target'} - {new Date(event.created_at).toLocaleString()}
            </div>
          </div>
        )) : <div className="px-4 py-8 text-sm text-slate-500">No audit events returned or access is restricted.</div>}
      </div>
    </section>
  );
}

function ReportRows({
  rows,
}: {
  rows: { id: string; title: string; detail: string; badges: string[]; note: string }[];
}) {
  return (
    <div className="divide-y divide-slate-100">
      {rows.length ? rows.slice(0, 20).map((row) => (
        <div className="grid gap-2 px-4 py-3 md:grid-cols-[1.3fr_0.8fr_1fr]" key={row.id}>
          <div>
            <div className="text-sm font-bold text-slate-950">{row.title}</div>
            <div className="text-xs text-slate-500">{row.detail}</div>
          </div>
          <div className="flex flex-wrap gap-2">{row.badges.map((badge) => <ReadinessBadge key={badge} value={badge} />)}</div>
          <div className="text-sm text-slate-600">{row.note}</div>
        </div>
      )) : <div className="px-4 py-8 text-sm text-slate-500">No records returned.</div>}
    </div>
  );
}

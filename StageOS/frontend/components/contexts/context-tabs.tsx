'use client';

import { useEffect, useMemo, useState } from 'react';
import clsx from 'clsx';
import { isTaskOverdue } from '@/components/tasks/helpers';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchContextAuditTrail, fetchDocuments, fetchEvidence, fetchTasks } from '@/lib/api/endpoints';
import type {
  AuditEventItem,
  ContextReadiness,
  DocumentItem,
  EvidenceSubmissionItem,
  OperatingContextListItem,
  TaskItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';
import { WorkspaceApprovalsTab } from './workspace-approvals-tab';
import { WorkspaceArtistsTab } from './workspace-artists-tab';
import { WorkspaceContractsTab } from './workspace-contracts-tab';
import { WorkspaceDocumentsTab } from './workspace-documents-tab';
import { WorkspaceExecutiveActionsTab } from './workspace-executive-actions-tab';
import { WorkspaceMarketingTab } from './workspace-marketing-tab';
import { WorkspaceOperationsTab } from './workspace-operations-tab';
import { WorkspaceTasksTab } from './workspace-tasks-tab';
import { WorkspaceSuppliersTab } from './workspace-suppliers-tab';
import { WorkspaceTechnicalTab } from './workspace-technical-tab';
import { WorkspaceTicketingTab } from './workspace-ticketing-tab';
import { WorkspaceReportsTab } from './workspace-reports-tab';
import { WorkspaceWorkflowTab } from './workspace-workflow-tab';
import { WorkspaceYouthTab } from './workspace-youth-tab';

const tabs = [
  'overview',
  'tasks',
  'documents',
  'approvals',
  'workflow',
  'executive',
  'contracts',
  'marketing',
  'technical',
  'foh',
  'suppliers',
  'artists',
  'ticketing',
  'youth',
  'risks',
  'reports',
  'audit',
] as const;

type TabKey = (typeof tabs)[number];

const tabLabels: Record<TabKey, string> = {
  overview: 'Overview',
  tasks: 'Tasks',
  documents: 'Documents / Evidence',
  approvals: 'Approvals',
  workflow: 'Process',
  executive: 'Executive Actions',
  contracts: 'Contracts',
  marketing: 'Marketing',
  technical: 'Technical',
  foh: 'FOH / Operations',
  suppliers: 'Suppliers',
  artists: 'Artists',
  ticketing: 'Ticketing',
  youth: 'Youth Development',
  risks: 'Risks',
  reports: 'Reports',
  audit: 'Audit Trail',
};

export function ContextTabs({
  context,
  readiness,
}: {
  context: OperatingContextListItem;
  readiness: ContextReadiness | null;
}) {
  const [active, setActive] = useState<TabKey>('overview');
  const { tokens } = useAuth();
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [evidence, setEvidence] = useState<EvidenceSubmissionItem[]>([]);

  useEffect(() => {
    if (!tokens?.access) {
      return;
    }

    let mounted = true;
    Promise.all([
      fetchTasks(tokens.access, { operating_context: context.id }),
      fetchDocuments(tokens.access, { operating_context: context.id }),
      fetchEvidence(tokens.access, { operating_context: context.id }),
    ])
      .then(([taskResponse, documentResponse, evidenceResponse]) => {
        if (!mounted) {
          return;
        }
        setTasks(taskResponse.results);
        setDocuments(documentResponse.results);
        setEvidence(evidenceResponse.results);
      })
      .catch(() => {
        // Overview metrics are supplementary; tab-level components show detailed errors.
      });

    return () => {
      mounted = false;
    };
  }, [context.id, tokens?.access]);

  const metrics = useMemo(() => {
    const evidenceRequired = tasks.filter((task) => task.evidence_required).length;
    const evidenceGaps = tasks.filter((task) => task.evidence_required && !task.evidence_provided).length;
    return {
      totalTasks: tasks.length || readiness?.tasks.total || 0,
      overdueTasks: tasks.filter(isTaskOverdue).length,
      evidenceRequired,
      documentsCount: documents.length || readiness?.documents_count || 0,
      evidenceGaps,
      evidenceSubmissions: evidence.length,
    };
  }, [documents.length, evidence.length, readiness?.documents_count, readiness?.tasks.total, tasks]);

  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="overflow-x-auto border-b border-slate-200">
        <div className="flex min-w-max gap-1 px-3 py-2" role="tablist" aria-label="Project workspace tabs">
          {tabs.map((tab) => (
            <button
              className={clsx(
                'h-9 rounded-md px-3 text-sm font-bold',
                active === tab ? 'bg-slate-950 text-white' : 'text-slate-600 hover:bg-slate-100',
              )}
              key={tab}
              onClick={() => setActive(tab)}
              role="tab"
              type="button"
            >
              {tabLabels[tab]}
            </button>
          ))}
        </div>
        <div className="mt-4 rounded-md border border-slate-200 bg-white p-3">
          <div className="font-bold text-slate-900">Readiness blockers</div>
          <div className="mt-3 grid gap-2">
            {readiness?.blockers?.length ? readiness.blockers.slice(0, 8).map((blocker, index) => (
              <div className="flex items-start justify-between gap-3 rounded-md bg-slate-50 p-3" key={`${blocker.type}-${blocker.label}-${index}`}>
                <div>
                  <div className="text-sm font-bold text-slate-900">{blocker.label}</div>
                  <div className="mt-1 text-xs text-slate-500">{blocker.detail}</div>
                </div>
                <StatusBadge tone={blocker.severity === 'critical' || blocker.severity === 'high' ? 'danger' : 'warning'}>
                  {blocker.type.replaceAll('_', ' ')}
                </StatusBadge>
              </div>
            )) : <div className="text-sm text-slate-500">No readiness blockers returned.</div>}
          </div>
        </div>
      </div>
      <div className="p-4">
        {active === 'overview' ? <OverviewPanel context={context} metrics={metrics} readiness={readiness} /> : null}
        {active === 'tasks' ? <WorkspaceTasksTab workspaceId={context.id} /> : null}
        {active === 'documents' ? <WorkspaceDocumentsTab workspaceId={context.id} /> : null}
        {active === 'approvals' ? <WorkspaceApprovalsTab workspaceId={context.id} /> : null}
        {active === 'workflow' ? <WorkspaceWorkflowTab workspaceId={context.id} /> : null}
        {active === 'executive' ? <WorkspaceExecutiveActionsTab workspaceId={context.id} /> : null}
        {active === 'contracts' ? <WorkspaceContractsTab workspaceId={context.id} /> : null}
        {active === 'marketing' ? <WorkspaceMarketingTab workspaceId={context.id} /> : null}
        {active === 'technical' ? <WorkspaceTechnicalTab workspaceId={context.id} /> : null}
        {active === 'foh' ? <WorkspaceOperationsTab workspaceId={context.id} /> : null}
        {active === 'suppliers' ? <WorkspaceSuppliersTab workspaceId={context.id} /> : null}
        {active === 'artists' ? <WorkspaceArtistsTab workspaceId={context.id} /> : null}
        {active === 'ticketing' ? <WorkspaceTicketingTab workspaceId={context.id} /> : null}
        {active === 'youth' ? <WorkspaceYouthTab workspaceId={context.id} /> : null}
        {active === 'risks' ? <RisksPanel readiness={readiness} /> : null}
        {active === 'reports' ? <WorkspaceReportsTab workspaceId={context.id} /> : null}
        {active === 'audit' ? <AuditPanel workspaceId={context.id} /> : null}
      </div>
    </section>
  );
}

function EmptyState({ label }: { label: string }) {
  return <div className="rounded-md bg-slate-50 p-4 text-sm text-slate-500">{label}</div>;
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border border-slate-200 p-3">
      <div className="text-xs font-bold uppercase tracking-normal text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-bold text-slate-950">{value}</div>
    </div>
  );
}

function OverviewPanel({
  context,
  metrics,
  readiness,
}: {
  context: OperatingContextListItem;
  metrics: {
    totalTasks: number;
    overdueTasks: number;
    evidenceRequired: number;
    documentsCount: number;
    evidenceGaps: number;
    evidenceSubmissions: number;
  };
  readiness: ContextReadiness | null;
}) {
  const departmentBlockers = [
    readiness?.campaign && readiness.campaign.status !== 'closed' && readiness.campaign.deliverables_complete < readiness.campaign.deliverables_total
      ? 'Marketing deliverables need attention'
      : '',
    readiness?.rider && readiness.rider.status !== 'approved' ? 'Technical rider is not approved' : '',
    readiness?.foh_plan && readiness.foh_plan.status !== 'closed' && readiness.foh_plan.incidents > 0 ? 'FOH incidents need review' : '',
  ].filter(Boolean);

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_520px]">
      <div>
        <h2 className="text-lg font-bold text-slate-950">Workspace overview</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {context.synopsis || 'No summary has been captured for this Workspace yet.'}
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          <Stat label="Marketing readiness" value={readiness?.campaign?.status ?? 'Unavailable'} />
          <Stat label="Technical readiness" value={readiness?.rider?.status ?? 'Unavailable'} />
          <Stat label="FOH / Operations" value={readiness?.foh_plan?.status ?? 'Unavailable'} />
          <Stat label="Ticketing setup" value={readiness?.ticketing?.setup_status ?? 'Unavailable'} />
          <Stat label="Sales imported" value={readiness?.ticketing ? 'See Ticketing' : 'Unavailable'} />
          <Stat label="Report readiness" value={readiness ? 'Available' : 'Unavailable'} />
        </div>
        <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
          <div className="font-bold text-slate-900">Next department action</div>
          <div className="mt-1">
            {departmentBlockers.length ? departmentBlockers.join(' · ') : 'No department blockers returned in readiness data.'}
          </div>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <Stat label="Readiness" value={`${context.readiness_score ?? 0}%`} />
        <Stat label="Total tasks" value={metrics.totalTasks} />
        <Stat label="Overdue tasks" value={metrics.overdueTasks} />
        <Stat label="Evidence required" value={metrics.evidenceRequired} />
        <Stat label="Documents" value={metrics.documentsCount} />
        <Stat label="Evidence gaps" value={metrics.evidenceGaps} />
      </div>
    </div>
  );
}

function RisksPanel({ readiness }: { readiness: ContextReadiness | null }) {
  if (!readiness?.risks.length) {
    return <EmptyState label="No risks returned for this Workspace." />;
  }
  return (
    <div className="grid gap-3">
      {readiness.risks.map((risk) => (
        <div className="flex items-center justify-between gap-3 rounded-md border border-slate-200 p-3" key={risk.id}>
          <div>
            <div className="text-sm font-bold text-slate-900">{risk.title}</div>
            <div className="text-xs text-slate-500">{risk.status}</div>
          </div>
          <StatusBadge tone={risk.level === 'critical' || risk.level === 'high' ? 'danger' : 'warning'}>
            {risk.level}
          </StatusBadge>
        </div>
      ))}
    </div>
  );
}

function AuditPanel({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [events, setEvents] = useState<AuditEventItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    fetchContextAuditTrail(tokens.access, workspaceId)
      .then((response) => {
        if (mounted) setEvents(response.results);
      })
      .catch(() => {
        if (mounted) setEvents([]);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [tokens?.access, workspaceId]);

  if (loading) {
    return <EmptyState label="Loading Workspace Audit Trail" />;
  }

  return (
    <div className="grid gap-3">
      {events.length ? events.map((event) => (
        <div className="rounded-md border border-slate-200 p-3" key={event.id}>
          <div className="text-sm font-bold text-slate-900">{event.event_type.replaceAll('_', ' ')}</div>
          <div className="mt-1 text-xs text-slate-500">
            {event.actor_email ?? event.actor ?? 'System'} · {new Date(event.created_at).toLocaleString()}
          </div>
          {event.reason ? <div className="mt-2 text-sm text-slate-600">{event.reason}</div> : null}
        </div>
      )) : <EmptyState label="No Workspace Audit Trail events returned." />}
    </div>
  );
}

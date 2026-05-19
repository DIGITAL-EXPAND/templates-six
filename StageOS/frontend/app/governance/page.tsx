'use client';

import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { AlertTriangle, CheckCircle2, Gavel, ShieldAlert } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import {
  ExecutiveActionList,
  executiveActionTypes,
} from '@/components/governance/executive-actions';
import { PageHeader } from '@/components/ui/page-header';
import { ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  createExecutiveAction,
  fetchCorrectiveActions,
  fetchDepartments,
  fetchExecutiveActions,
  fetchKPIs,
  fetchOperatingContexts,
  fetchRisks,
  fetchUsers,
  setExecutiveActionStatus,
} from '@/lib/api/endpoints';
import type {
  CorrectiveActionItem,
  DepartmentListItem,
  ExecutiveActionItem,
  ExecutiveActionType,
  KPIItem,
  OperatingContextListItem,
  RiskItem,
  UserListItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

// ── KPI helpers ──────────────────────────────────────────────────────────────

function kpiPct(kpi: KPIItem): number {
  const target = parseFloat(kpi.target_value);
  const actual = parseFloat(kpi.actual_value);
  if (target <= 0) return 0;
  return Math.min(100, (actual / target) * 100);
}

type Rag = 'green' | 'amber' | 'red';

function ragStatus(pct: number): Rag {
  if (pct >= 90) return 'green';
  if (pct >= 60) return 'amber';
  return 'red';
}

const RAG_COLOURS: Record<Rag, string> = {
  green: 'bg-green-500',
  amber: 'bg-amber-400',
  red:   'bg-red-500',
};

const RAG_BADGE: Record<Rag, string> = {
  green: 'bg-green-100 text-green-800',
  amber: 'bg-amber-100 text-amber-800',
  red:   'bg-red-100 text-red-700',
};

const RAG_LABEL: Record<Rag, string> = {
  green: 'On Track',
  amber: 'At Risk',
  red:   'Off Track',
};

function KpiCard({ kpi }: { kpi: KPIItem }) {
  const pct = kpiPct(kpi);
  const rag = ragStatus(pct);
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-3">
      <div className="flex items-start justify-between gap-2">
        <span className="text-sm font-medium text-slate-800 leading-snug">{kpi.name}</span>
        <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${RAG_BADGE[rag]}`}>
          {RAG_LABEL[rag]}
        </span>
      </div>
      <div className="mt-2 flex items-baseline gap-1 text-xs text-slate-500">
        <span className="text-lg font-bold text-slate-900">{parseFloat(kpi.actual_value).toLocaleString()}</span>
        <span>/</span>
        <span>{parseFloat(kpi.target_value).toLocaleString()} {kpi.unit}</span>
      </div>
      {/* Progress bar */}
      <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-2 rounded-full transition-all ${RAG_COLOURS[rag]}`}
          style={{ width: `${pct.toFixed(1)}%` }}
        />
      </div>
      <div className="mt-1 text-right text-xs text-slate-400">{pct.toFixed(0)}%</div>
      {kpi.reporting_period && (
        <div className="mt-1 text-xs text-slate-400 capitalize">{kpi.reporting_period}</div>
      )}
    </article>
  );
}

// ── Risk summary helpers ──────────────────────────────────────────────────────

const RISK_LEVEL_ORDER = ['critical', 'high', 'medium', 'low'];

const RISK_LEVEL_COLOURS: Record<string, string> = {
  critical: 'bg-red-100 text-red-800',
  high:     'bg-orange-100 text-orange-700',
  medium:   'bg-amber-100 text-amber-700',
  low:      'bg-green-100 text-green-700',
};

// ── Main page ─────────────────────────────────────────────────────────────────

export default function GovernancePage() {
  const { tokens } = useAuth();
  const [actions, setActions] = useState<ExecutiveActionItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [kpis, setKpis] = useState<KPIItem[]>([]);
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [correctiveActions, setCorrectiveActions] = useState<CorrectiveActionItem[]>([]);
  const [actionType, setActionType] = useState<ExecutiveActionType>('request_change');
  const [title, setTitle] = useState('');
  const [reason, setReason] = useState('');
  const [instruction, setInstruction] = useState('');
  const [workspaceId, setWorkspaceId] = useState('');
  const [departmentId, setDepartmentId] = useState('');
  const [assignedTo, setAssignedTo] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([
      fetchExecutiveActions(tokens.access),
      fetchOperatingContexts(tokens.access),
      fetchDepartments(tokens.access),
      fetchUsers(tokens.access),
      fetchKPIs(tokens.access),
      fetchRisks(tokens.access),
      fetchCorrectiveActions(tokens.access),
    ])
      .then(([actionResult, workspaceResult, departmentResult, userResult, kpiResult, riskResult, caResult]) => {
        if (!mounted) return;
        if (actionResult.status === 'fulfilled') setActions(actionResult.value.results);
        else if (actionResult.reason instanceof ApiError && actionResult.reason.status === 403) setPermissionDenied(true);
        else setError('Executive actions could not be loaded.');
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
        if (departmentResult.status === 'fulfilled') setDepartments(departmentResult.value.results);
        if (userResult.status === 'fulfilled') setUsers(userResult.value.results);
        if (kpiResult.status === 'fulfilled') setKpis(kpiResult.value.results);
        if (riskResult.status === 'fulfilled') setRisks(riskResult.value.results);
        if (caResult.status === 'fulfilled') setCorrectiveActions(caResult.value.results);
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access]);

  const metrics = useMemo(() => ({
    open: actions.filter((action) => action.status === 'open').length,
    acknowledged: actions.filter((action) => action.status === 'acknowledged').length,
    highAuthority: actions.filter((action) => ['override', 'decline', 'escalate'].includes(action.action_type)).length,
    linkedWork: actions.filter((action) => action.linked_task || action.linked_risk || action.linked_corrective_action).length,
  }), [actions]);

  // Group KPIs by department name (use owner_description as fallback)
  const kpisByDept = useMemo(() => {
    const map = new Map<string, KPIItem[]>();
    for (const kpi of kpis.filter((k) => k.is_active)) {
      const dept = departments.find((d) => d.id === kpi.owner_department);
      const label = dept?.name ?? kpi.owner_description ?? 'General';
      const existing = map.get(label) ?? [];
      existing.push(kpi);
      map.set(label, existing);
    }
    return map;
  }, [kpis, departments]);

  // Risk summary grouped by level and status
  const riskSummary = useMemo(() => {
    const byLevel: Record<string, { open: number; in_progress: number; mitigated: number }> = {};
    for (const risk of risks) {
      if (!byLevel[risk.risk_level]) {
        byLevel[risk.risk_level] = { open: 0, in_progress: 0, mitigated: 0 };
      }
      if (risk.status === 'open') byLevel[risk.risk_level].open++;
      else if (risk.status === 'in_progress') byLevel[risk.risk_level].in_progress++;
      else if (risk.status === 'mitigated') byLevel[risk.risk_level].mitigated++;
    }
    return byLevel;
  }, [risks]);

  const overdueCount = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    return correctiveActions.filter(
      (ca) => ca.status !== 'completed' && ca.due_date && ca.due_date < today,
    ).length;
  }, [correctiveActions]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setError('');
    try {
      const created = await createExecutiveAction(tokens.access, {
        action_type: actionType,
        title,
        reason,
        instruction,
        operating_context: workspaceId || null,
        department: departmentId || null,
        assigned_to: assignedTo || null,
        due_date: dueDate || null,
      });
      setActions((current) => [created, ...current]);
      setTitle('');
      setReason('');
      setInstruction('');
      setDueDate('');
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Executive action could not be created.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAction(item: ExecutiveActionItem, statusAction: 'acknowledge' | 'complete' | 'cancel') {
    if (!tokens?.access) return;
    setSubmitting(true);
    setError('');
    try {
      const updated = await setExecutiveActionStatus(tokens.access, item.id, statusAction, comment);
      setActions((current) => current.map((action) => (action.id === updated.id ? updated : action)));
      setComment('');
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Executive action update failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="Create controlled executive interventions that are visible, actionable and recorded in the Audit Trail."
          eyebrow="Governance"
          title="Executive Actions"
        />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading executive actions" /> : (
          <>
            {/* Executive action metrics */}
            <section className="grid gap-4 md:grid-cols-4">
              <Metric icon={ShieldAlert} label="Open" value={metrics.open} />
              <Metric icon={CheckCircle2} label="Acknowledged" value={metrics.acknowledged} />
              <Metric icon={Gavel} label="High authority" value={metrics.highAuthority} />
              <Metric icon={AlertTriangle} label="Linked work" value={metrics.linkedWork} />
            </section>

            {/* KPI Dashboard */}
            {kpis.length > 0 && (
              <section>
                <h2 className="mb-3 text-base font-bold text-slate-950">KPI Dashboard</h2>
                {Array.from(kpisByDept.entries()).map(([deptName, deptKpis]) => (
                  <div key={deptName} className="mb-4">
                    <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">{deptName}</h3>
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                      {deptKpis.map((kpi) => <KpiCard key={kpi.id} kpi={kpi} />)}
                    </div>
                  </div>
                ))}
              </section>
            )}

            {/* Risk Register Summary + Corrective Actions */}
            {(risks.length > 0 || correctiveActions.length > 0) && (
              <section className="grid gap-4 md:grid-cols-2">
                {/* Risk register */}
                {risks.length > 0 && (
                  <div className="rounded-lg border border-slate-200 bg-white p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h2 className="text-base font-bold text-slate-950">Risk Register</h2>
                      <span className="text-xs text-slate-500">{risks.length} total</span>
                    </div>
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-slate-100">
                          <th className="pb-2 text-left font-semibold text-slate-500 uppercase tracking-wide">Level</th>
                          <th className="pb-2 text-center font-semibold text-slate-500 uppercase tracking-wide">Open</th>
                          <th className="pb-2 text-center font-semibold text-slate-500 uppercase tracking-wide">In Progress</th>
                          <th className="pb-2 text-center font-semibold text-slate-500 uppercase tracking-wide">Mitigated</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                        {RISK_LEVEL_ORDER.filter((level) => riskSummary[level]).map((level) => (
                          <tr key={level} className="py-1">
                            <td className="py-2">
                              <span className={`rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${RISK_LEVEL_COLOURS[level] ?? 'bg-slate-100 text-slate-700'}`}>
                                {level}
                              </span>
                            </td>
                            <td className="py-2 text-center font-medium text-red-600">{riskSummary[level].open}</td>
                            <td className="py-2 text-center font-medium text-amber-600">{riskSummary[level].in_progress}</td>
                            <td className="py-2 text-center font-medium text-green-600">{riskSummary[level].mitigated}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Corrective actions overdue */}
                {correctiveActions.length > 0 && (
                  <div className="rounded-lg border border-slate-200 bg-white p-4 flex flex-col gap-3">
                    <h2 className="text-base font-bold text-slate-950">Corrective Actions</h2>
                    <div className="grid grid-cols-3 gap-3">
                      <div className="rounded-lg bg-red-50 border border-red-100 p-3 text-center">
                        <div className="text-2xl font-bold text-red-700">{overdueCount}</div>
                        <div className="text-xs text-red-500 mt-1">Overdue</div>
                      </div>
                      <div className="rounded-lg bg-amber-50 border border-amber-100 p-3 text-center">
                        <div className="text-2xl font-bold text-amber-700">
                          {correctiveActions.filter((ca) => ca.status === 'in_progress').length}
                        </div>
                        <div className="text-xs text-amber-500 mt-1">In Progress</div>
                      </div>
                      <div className="rounded-lg bg-green-50 border border-green-100 p-3 text-center">
                        <div className="text-2xl font-bold text-green-700">
                          {correctiveActions.filter((ca) => ca.status === 'completed').length}
                        </div>
                        <div className="text-xs text-green-500 mt-1">Completed</div>
                      </div>
                    </div>
                  </div>
                )}
              </section>
            )}

            <section className="grid gap-5 xl:grid-cols-[0.85fr_1.4fr]">
              <form className="space-y-3 rounded-lg border border-slate-200 bg-white p-4" onSubmit={handleCreate}>
                <h2 className="text-base font-bold text-slate-950">New Executive Action</h2>
                <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setActionType(event.target.value as ExecutiveActionType)} value={actionType}>
                  {executiveActionTypes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
                <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setTitle(event.target.value)} placeholder="Title" required value={title} />
                <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setWorkspaceId(event.target.value)} value={workspaceId}>
                  <option value="">No linked Workspace</option>
                  {workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.title}</option>)}
                </select>
                <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setDepartmentId(event.target.value)} value={departmentId}>
                  <option value="">No department</option>
                  {departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}
                </select>
                <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setAssignedTo(event.target.value)} value={assignedTo}>
                  <option value="">Unassigned</option>
                  {users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}
                </select>
                <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setDueDate(event.target.value)} type="date" value={dueDate} />
                <textarea className="min-h-24 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" onChange={(event) => setReason(event.target.value)} placeholder="Reason" value={reason} />
                <textarea className="min-h-24 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" onChange={(event) => setInstruction(event.target.value)} placeholder="Instruction" value={instruction} />
                <button className="inline-flex h-10 items-center justify-center rounded-md bg-blue-700 px-4 text-sm font-bold text-white disabled:opacity-50" disabled={submitting} type="submit">
                  Create Action
                </button>
              </form>

              <section className="space-y-3">
                <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setComment(event.target.value)} placeholder="Status action comment" value={comment} />
                <ExecutiveActionList
                  actions={actions}
                  departments={departments}
                  onAction={handleAction}
                  submitting={submitting}
                  users={users}
                  workspaces={workspaces}
                />
              </section>
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}

function Metric({ icon: Icon, label, value }: { icon: typeof ShieldAlert; label: string; value: number }) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <Icon className="h-5 w-5 text-blue-700" />
      <div className="mt-3 text-2xl font-bold text-slate-950">{value}</div>
      <div className="text-sm font-semibold text-slate-500">{label}</div>
    </article>
  );
}

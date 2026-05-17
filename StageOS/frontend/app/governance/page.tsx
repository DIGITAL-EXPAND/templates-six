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
  fetchDepartments,
  fetchExecutiveActions,
  fetchOperatingContexts,
  fetchUsers,
  setExecutiveActionStatus,
} from '@/lib/api/endpoints';
import type {
  DepartmentListItem,
  ExecutiveActionItem,
  ExecutiveActionType,
  OperatingContextListItem,
  UserListItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export default function GovernancePage() {
  const { tokens } = useAuth();
  const [actions, setActions] = useState<ExecutiveActionItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
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
    ])
      .then(([actionResult, workspaceResult, departmentResult, userResult]) => {
        if (!mounted) return;
        if (actionResult.status === 'fulfilled') setActions(actionResult.value.results);
        else if (actionResult.reason instanceof ApiError && actionResult.reason.status === 403) setPermissionDenied(true);
        else setError('Executive actions could not be loaded.');
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
        if (departmentResult.status === 'fulfilled') setDepartments(departmentResult.value.results);
        if (userResult.status === 'fulfilled') setUsers(userResult.value.results);
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
            <section className="grid gap-4 md:grid-cols-4">
              <Metric icon={ShieldAlert} label="Open" value={metrics.open} />
              <Metric icon={CheckCircle2} label="Acknowledged" value={metrics.acknowledged} />
              <Metric icon={Gavel} label="High authority" value={metrics.highAuthority} />
              <Metric icon={AlertTriangle} label="Linked work" value={metrics.linkedWork} />
            </section>

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

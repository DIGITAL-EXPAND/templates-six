'use client';

import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { AlertTriangle, CalendarDays, CheckCircle2, Clock3, XCircle } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { ApiError } from '@/lib/api/client';
import {
  createCalendarIssue,
  fetchCalendarIssues,
  fetchCalendarSlots,
  fetchDepartments,
  fetchOperatingContexts,
  fetchOperatingProfile,
  fetchVenueHolds,
  setCalendarIssueAction,
} from '@/lib/api/endpoints';
import type {
  CalendarIssueItem,
  CalendarSlotItem,
  DepartmentListItem,
  OperatingContextListItem,
  VenueHoldItem,
  OperatingProfile,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';
import { dashboardKind } from '@/lib/role-experience';

const severityTone: Record<string, 'neutral' | 'info' | 'good' | 'warning' | 'danger'> = {
  low: 'neutral',
  medium: 'info',
  high: 'warning',
  critical: 'danger',
};

const statusTone: Record<string, 'neutral' | 'info' | 'good' | 'warning' | 'danger'> = {
  open: 'warning',
  in_progress: 'info',
  resolved: 'good',
  cancelled: 'neutral',
};

function label(value: string) {
  return value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function workspaceName(workspaces: OperatingContextListItem[], id?: string | null) {
  return workspaces.find((workspace) => workspace.id === id)?.title ?? 'No Workspace';
}

function departmentName(departments: DepartmentListItem[], id?: string | null) {
  return departments.find((department) => department.id === id)?.name ?? 'Unassigned';
}

function venueLabel(holds: VenueHoldItem[], slots: CalendarSlotItem[], issue: CalendarIssueItem) {
  const hold = holds.find((item) => item.id === issue.venue_hold);
  if (hold) return `${label(hold.hold_type)} hold on ${hold.hold_date}`;
  const slot = slots.find((item) => item.id === issue.calendar_slot);
  if (slot) return `${label(slot.slot_type)} slot on ${slot.date}`;
  return 'No linked calendar item';
}

export default function CalendarPage() {
  const { tokens } = useAuth();
  const [holds, setHolds] = useState<VenueHoldItem[]>([]);
  const [slots, setSlots] = useState<CalendarSlotItem[]>([]);
  const [issues, setIssues] = useState<CalendarIssueItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [profile, setProfile] = useState<OperatingProfile | null>(null);
  const [selectedWorkspace, setSelectedWorkspace] = useState('');
  const [selectedHold, setSelectedHold] = useState('');
  const [selectedSlot, setSelectedSlot] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState<'low' | 'medium' | 'high' | 'critical'>('medium');
  const [dueDate, setDueDate] = useState('');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([
      fetchVenueHolds(tokens.access),
      fetchCalendarSlots(tokens.access),
      fetchCalendarIssues(tokens.access),
      fetchOperatingContexts(tokens.access),
      fetchDepartments(tokens.access),
      fetchOperatingProfile(tokens.access),
    ])
      .then(([holdResult, slotResult, issueResult, workspaceResult, departmentResult, profileResult]) => {
        if (!mounted) return;
        if (holdResult.status === 'fulfilled') setHolds(holdResult.value.results);
        else if (holdResult.reason instanceof ApiError && holdResult.reason.status === 403) setPermissionDenied(true);
        if (slotResult.status === 'fulfilled') setSlots(slotResult.value.results);
        if (issueResult.status === 'fulfilled') setIssues(issueResult.value.results);
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
        if (departmentResult.status === 'fulfilled') setDepartments(departmentResult.value.results);
        if (profileResult.status === 'fulfilled') setProfile(profileResult.value);
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access]);

  const filteredHolds = useMemo(
    () => (selectedWorkspace ? holds.filter((hold) => hold.operating_context === selectedWorkspace) : holds),
    [holds, selectedWorkspace],
  );

  const filteredSlots = useMemo(
    () => (selectedWorkspace ? slots.filter((slot) => slot.operating_context === selectedWorkspace) : slots),
    [selectedWorkspace, slots],
  );

  const calendarRows = useMemo(() => {
    const holdRows = holds.map((hold) => ({
      id: `hold-${hold.id}`,
      date: hold.hold_date,
      type: `${label(hold.hold_type)} hold`,
      detail: label(hold.purpose),
      workspace: workspaceName(workspaces, hold.operating_context),
      status: hold.hold_type,
    }));
    const slotRows = slots.map((slot) => ({
      id: `slot-${slot.id}`,
      date: slot.date,
      type: label(slot.slot_type),
      detail: slot.is_confirmed ? 'Confirmed' : 'Provisional',
      workspace: workspaceName(workspaces, slot.operating_context),
      status: slot.is_confirmed ? 'confirmed' : 'provisional',
    }));
    return [...holdRows, ...slotRows].sort((a, b) => a.date.localeCompare(b.date)).slice(0, 40);
  }, [holds, slots, workspaces]);

  const openIssues = issues.filter((issue) => issue.status !== 'resolved' && issue.status !== 'cancelled');
  const criticalIssues = issues.filter((issue) => issue.severity === 'critical' && issue.status !== 'resolved').length;
  const role = dashboardKind(profile);
  const canRaiseIssue = !['board', 'client', 'supplier', 'artist'].includes(role);
  const canManageIssue = ['admin', 'executive', 'gm', 'programming'].includes(role);

  async function handleCreateIssue(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!tokens?.access || !canRaiseIssue) return;
    setSubmitting(true);
    setError('');
    try {
      const created = await createCalendarIssue(tokens.access, {
        title,
        description,
        operating_context: selectedWorkspace || null,
        venue_hold: selectedHold || null,
        calendar_slot: selectedSlot || null,
        department: selectedDepartment || null,
        severity,
        due_date: dueDate || null,
      });
      setIssues((current) => [created, ...current]);
      setTitle('');
      setDescription('');
      setSelectedHold('');
      setSelectedSlot('');
      setDueDate('');
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Calendar issue could not be raised.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleIssueAction(issue: CalendarIssueItem, action: 'progress' | 'resolve' | 'cancel') {
    if (!tokens?.access || !canManageIssue) return;
    setSubmitting(true);
    setError('');
    try {
      const updated = await setCalendarIssueAction(tokens.access, issue.id, action, note);
      setIssues((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setNote('');
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Calendar issue action failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="Review confirmed and provisional venue dates, then raise or resolve scheduling issues."
          eyebrow="Planning"
          title="Calendar"
        />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading calendar" /> : (
          <>
            <section className="grid gap-4 md:grid-cols-4">
              <Metric icon={CalendarDays} label="Venue holds" value={holds.length} />
              <Metric icon={Clock3} label="Calendar slots" value={slots.length} />
              <Metric icon={AlertTriangle} label="Open issues" value={openIssues.length} />
              <Metric icon={XCircle} label="Critical issues" value={criticalIssues} />
            </section>

            <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
              <article className="rounded-lg border border-slate-200 bg-white">
                <div className="border-b border-slate-200 px-4 py-3">
                  <h2 className="text-base font-bold text-slate-950">Shared Calendar</h2>
                </div>
                <div className="divide-y divide-slate-100">
                  {calendarRows.length ? calendarRows.map((row) => (
                    <div className="grid gap-2 px-4 py-3 md:grid-cols-[110px_1fr_auto]" key={row.id}>
                      <div className="text-sm font-bold text-slate-950">{row.date}</div>
                      <div>
                        <div className="text-sm font-bold text-slate-900">{row.type}</div>
                        <div className="mt-1 text-xs text-slate-500">{row.workspace} · {row.detail}</div>
                      </div>
                      <StatusBadge tone={row.status === 'confirmed' ? 'good' : row.status === 'blocked' ? 'danger' : 'info'}>
                        {label(row.status)}
                      </StatusBadge>
                    </div>
                  )) : (
                    <div className="px-4 py-8 text-sm text-slate-500">No venue holds or calendar slots returned.</div>
                  )}
                </div>
              </article>

              <form className="space-y-3 rounded-lg border border-slate-200 bg-white p-4" onSubmit={handleCreateIssue}>
                <h2 className="text-base font-bold text-slate-950">Raise Calendar Issue</h2>
                {!canRaiseIssue ? <p className="text-sm font-semibold text-amber-700">Calendar editing is restricted for your role.</p> : null}
                <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setTitle(event.target.value)} placeholder="Issue title" required value={title} />
                <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setSelectedWorkspace(event.target.value)} value={selectedWorkspace}>
                  <option value="">No linked Workspace</option>
                  {workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.title}</option>)}
                </select>
                <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => { setSelectedHold(event.target.value); if (event.target.value) setSelectedSlot(''); }} value={selectedHold}>
                  <option value="">No linked venue hold</option>
                  {filteredHolds.map((hold) => <option key={hold.id} value={hold.id}>{hold.hold_date} · {label(hold.hold_type)} · {label(hold.purpose)}</option>)}
                </select>
                <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => { setSelectedSlot(event.target.value); if (event.target.value) setSelectedHold(''); }} value={selectedSlot}>
                  <option value="">No linked calendar slot</option>
                  {filteredSlots.map((slot) => <option key={slot.id} value={slot.id}>{slot.date} · {label(slot.slot_type)}</option>)}
                </select>
                <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setSelectedDepartment(event.target.value)} value={selectedDepartment}>
                  <option value="">Unassigned department</option>
                  {departments.map((department) => <option key={department.id} value={department.id}>{department.name}</option>)}
                </select>
                <div className="grid gap-3 md:grid-cols-2">
                  <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setSeverity(event.target.value as typeof severity)} value={severity}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                  <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setDueDate(event.target.value)} type="date" value={dueDate} />
                </div>
                <textarea className="min-h-24 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" onChange={(event) => setDescription(event.target.value)} placeholder="Describe the scheduling issue" value={description} />
                <button className="inline-flex h-10 items-center justify-center rounded-md bg-blue-700 px-4 text-sm font-bold text-white disabled:opacity-50" disabled={submitting || !canRaiseIssue} type="submit">
                  Raise Issue
                </button>
              </form>
            </section>

            <section className="space-y-3">
              <div className="grid gap-3 md:grid-cols-[1fr_260px]">
                <h2 className="text-base font-bold text-slate-950">Calendar Issues</h2>
                <input className="h-10 rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setNote(event.target.value)} placeholder="Action note" value={note} />
              </div>
              {issues.length ? issues.map((issue) => (
                <article className="rounded-lg border border-slate-200 bg-white p-4" key={issue.id}>
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-base font-bold text-slate-950">{issue.title}</h3>
                        <StatusBadge tone={statusTone[issue.status]}>{label(issue.status)}</StatusBadge>
                        <StatusBadge tone={severityTone[issue.severity]}>{label(issue.severity)}</StatusBadge>
                      </div>
                      <div className="mt-1 text-xs text-slate-500">
                        {workspaceName(workspaces, issue.operating_context)} · {departmentName(departments, issue.department)} · {venueLabel(holds, slots, issue)}
                      </div>
                      <p className="mt-2 text-sm leading-6 text-slate-600">{issue.description || 'No description captured.'}</p>
                      {issue.resolution_note ? <p className="mt-2 text-xs font-semibold text-emerald-700">Resolved: {issue.resolution_note}</p> : null}
                    </div>
                    <div className="flex flex-wrap gap-2 md:justify-end">
                      <ActionButton disabled={submitting || !canManageIssue || issue.status !== 'open'} icon={Clock3} label="Progress" onClick={() => handleIssueAction(issue, 'progress')} />
                      <ActionButton disabled={submitting || !canManageIssue || issue.status === 'resolved' || issue.status === 'cancelled'} icon={CheckCircle2} label="Resolve" onClick={() => handleIssueAction(issue, 'resolve')} />
                      <ActionButton disabled={submitting || !canManageIssue || issue.status === 'resolved' || issue.status === 'cancelled'} icon={XCircle} label="Cancel" onClick={() => handleIssueAction(issue, 'cancel')} />
                    </div>
                  </div>
                </article>
              )) : (
                <div className="rounded-lg border border-dashed border-slate-300 bg-white px-4 py-10 text-center text-sm text-slate-500">
                  No calendar issues returned.
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}

function Metric({ icon: Icon, label, value }: { icon: typeof CalendarDays; label: string; value: number }) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <Icon className="h-5 w-5 text-blue-700" />
      <div className="mt-3 text-2xl font-bold text-slate-950">{value}</div>
      <div className="text-sm font-semibold text-slate-500">{label}</div>
    </article>
  );
}

function ActionButton({
  disabled,
  icon: Icon,
  label: buttonLabel,
  onClick,
}: {
  disabled: boolean;
  icon: typeof CalendarDays;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      className="inline-flex h-9 items-center gap-1 rounded-md border border-slate-200 bg-white px-3 text-xs font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-40"
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      <Icon className="h-3.5 w-3.5" />
      {buttonLabel}
    </button>
  );
}

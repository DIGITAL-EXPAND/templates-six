'use client';

import { useEffect, useState } from 'react';
import {
  AlertTriangle,
  BadgeCheck,
  BellRing,
  CalendarDays,
  CheckCircle2,
  CircleDot,
  ClipboardList,
  FileSignature,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DashboardSkeleton } from '@/components/dashboard/dashboard-skeleton';
import { MetricCard } from '@/components/dashboard/metric-card';
import { TaskPanel } from '@/components/tasks/TaskPanel';
import {
  fetchApprovalRequests,
  fetchExecutiveSummary,
  fetchNotifications,
  fetchOperatingProfile,
  fetchTasks,
} from '@/lib/api/endpoints';
import type {
  ApprovalRequestItem,
  ExecutiveSummary,
  NotificationItem,
  OperatingContextListItem,
  OperatingProfile,
  TaskItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';
import {
  APPROVAL_LABELS,
  AUTHORITY_LABELS,
  DASHBOARD_LABELS,
  NOTIFICATION_LABELS,
  ROLE_LABELS,
  TASK_LABELS,
} from '@/lib/labels';
import { dashboardKind } from '@/lib/role-experience';

// ── Small helpers ─────────────────────────────────────────────────────────────

function greeting(firstName: string) {
  const hour = new Date().getHours();
  const salutation =
    hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
  return firstName ? `${salutation}, ${firstName}` : salutation;
}

function formatDate(d: string | null | undefined) {
  if (!d) return 'No due date';
  return new Date(d).toLocaleDateString('en-ZA', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

function isOverdue(task: TaskItem) {
  if (!task.due_date || task.status === 'done' || task.status === 'cancelled') return false;
  return task.due_date < new Date().toISOString().slice(0, 10);
}

// ── Shared Card wrapper ───────────────────────────────────────────────────────

function Card({
  children,
  className = '',
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-xl border border-gray-200 bg-white shadow-sm ${className}`}>
      {children}
    </div>
  );
}

function CardHeader({ title, count }: { title: string; count?: number }) {
  return (
    <div className="flex items-center justify-between border-b border-gray-100 px-5 py-3.5">
      <h2 className="text-sm font-semibold text-gray-900">{title}</h2>
      {count !== undefined ? (
        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-semibold text-gray-600">
          {count}
        </span>
      ) : null}
    </div>
  );
}

// ── Status / Priority mini-badges ─────────────────────────────────────────────

type TaskStatus = TaskItem['status'];
type Priority = TaskItem['priority'];

const STATUS_CLASSES: Record<TaskStatus, string> = {
  open:        'bg-gray-100 text-gray-700',
  in_progress: 'bg-blue-100 text-blue-700',
  blocked:     'bg-red-100 text-red-700',
  done:        'bg-green-100 text-green-700',
  cancelled:   'bg-gray-100 text-gray-400',
};

const PRIORITY_CLASSES: Record<Priority, string> = {
  critical: 'bg-red-100 text-red-700',
  high:     'bg-orange-100 text-orange-700',
  medium:   'bg-blue-100 text-blue-700',
  low:      'bg-gray-100 text-gray-600',
};

function TaskStatusBadge({ status }: { status: TaskStatus }) {
  return (
    <span className={`inline-flex shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_CLASSES[status]}`}>
      {TASK_LABELS.statusShort[status]}
    </span>
  );
}

function TaskPriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span className={`inline-flex shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold ${PRIORITY_CLASSES[priority]}`}>
      {TASK_LABELS.priorities[priority]}
    </span>
  );
}

// ── Task row (used in manager + staff views) ──────────────────────────────────

function TaskRow({
  task,
  showAssignee = false,
  onClick,
}: {
  task: TaskItem;
  showAssignee?: boolean;
  onClick: (id: string) => void;
}) {
  const overdue = isOverdue(task);

  return (
    <button
      className="flex w-full items-center gap-3 px-5 py-3 text-left hover:bg-gray-50 focus:outline-none focus-visible:bg-gray-50"
      onClick={() => onClick(task.id)}
      type="button"
    >
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-gray-900">{task.title}</p>
        <div className="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-gray-400">
          {showAssignee && task.assigned_to ? (
            <span className="truncate">{task.assigned_to}</span>
          ) : null}
          <span className={overdue ? 'font-semibold text-red-500' : ''}>
            {formatDate(task.due_date)}
          </span>
        </div>
      </div>
      <div className="flex shrink-0 flex-wrap gap-1.5">
        <TaskPriorityBadge priority={task.priority} />
        <TaskStatusBadge status={task.status} />
      </div>
    </button>
  );
}

// ── Role badge ────────────────────────────────────────────────────────────────

function RoleBadge({ profile }: { profile: OperatingProfile }) {
  const dept = profile.primary_department?.name;
  const authority = profile.primary_position?.authority_level;
  const label = dept
    ? `${dept}${authority ? ' · ' + (AUTHORITY_LABELS[authority] ?? authority) : ''}`
    : ROLE_LABELS[profile.user.user_type] ?? profile.user.user_type;
  return (
    <span className="inline-flex items-center rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-700 ring-1 ring-teal-200">
      {label}
    </span>
  );
}

// ── Greeting header ───────────────────────────────────────────────────────────

function GreetingHeader({
  firstName,
  profile,
}: {
  firstName: string;
  profile: OperatingProfile | null;
}) {
  const kind = dashboardKind(profile);
  const labels = DASHBOARD_LABELS[kind] ?? DASHBOARD_LABELS.generic;

  return (
    <section className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{greeting(firstName)}</h1>
        <p className="mt-1 text-sm text-gray-500">{labels.subheading}</p>
      </div>
      {profile ? <RoleBadge profile={profile} /> : null}
    </section>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// EXECUTIVE DASHBOARD
// ─────────────────────────────────────────────────────────────────────────────

function ExecutiveSummaryDashboard({
  summary,
  approvals,
  onTaskClick,
}: {
  summary: ExecutiveSummary;
  approvals: ApprovalRequestItem[];
  onTaskClick: (id: string) => void;
}) {
  const pendingApprovals = approvals.filter((a) => a.decision === 'pending').length;
  const readinessPct = Math.round(summary.average_readiness);

  // Build production status list from contexts_by_status
  const statusEntries = Object.entries(summary.contexts_by_status).sort(
    ([, a], [, b]) => b - a,
  );

  return (
    <div className="space-y-5">
      {/* 4 stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          color="teal"
          detail="Across all active productions"
          icon={CalendarDays}
          label="Productions"
          value={summary.total_contexts}
        />
        <MetricCard
          color={readinessPct >= 80 ? 'green' : readinessPct >= 50 ? 'orange' : 'red'}
          detail="Average across all productions"
          label="Readiness"
          value={`${readinessPct}%`}
        />
        <MetricCard
          color={summary.high_risks > 0 ? 'red' : 'green'}
          detail={`${summary.high_risks} high or critical`}
          icon={AlertTriangle}
          label="Open Risks"
          value={summary.open_risks}
        />
        <MetricCard
          color={pendingApprovals > 0 ? 'orange' : 'green'}
          detail="Awaiting sign-off decision"
          icon={BadgeCheck}
          label="Pending Sign-Offs"
          value={pendingApprovals}
        />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Productions this season */}
        <Card>
          <CardHeader title="Productions This Season" count={summary.total_contexts} />
          <div className="divide-y divide-gray-50 px-5 py-2">
            {statusEntries.length ? (
              statusEntries.map(([status, count]) => (
                <div className="flex items-center justify-between py-2.5" key={status}>
                  <span className="text-sm capitalize text-gray-700">
                    {status.replace(/_/g, ' ')}
                  </span>
                  <span className="text-sm font-semibold text-gray-900">{count}</span>
                </div>
              ))
            ) : (
              <p className="py-5 text-sm text-gray-400">No productions data available.</p>
            )}
          </div>
        </Card>

        {/* Needs your attention */}
        <Card>
          <CardHeader title="Needs Your Attention" />
          <div className="divide-y divide-gray-50 px-5 py-2">
            <div className="flex items-center justify-between py-2.5">
              <div className="flex items-center gap-2.5 text-sm text-gray-700">
                <ClipboardList className="h-4 w-4 text-gray-400" />
                Open actions
              </div>
              <span
                className={`text-sm font-semibold ${summary.open_tasks > 0 ? 'text-red-600' : 'text-gray-900'}`}
              >
                {summary.open_tasks}
              </span>
            </div>
            <div className="flex items-center justify-between py-2.5">
              <div className="flex items-center gap-2.5 text-sm text-gray-700">
                <BadgeCheck className="h-4 w-4 text-gray-400" />
                Pending sign-offs
              </div>
              <span
                className={`text-sm font-semibold ${pendingApprovals > 0 ? 'text-orange-600' : 'text-gray-900'}`}
              >
                {pendingApprovals}
              </span>
            </div>
            {summary.upcoming_openings.slice(0, 4).map((opening) => (
              <div className="flex items-center justify-between py-2.5" key={opening.id}>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-gray-800">{opening.title}</p>
                  <p className="text-xs text-gray-400">Opening in {opening.days_until} days</p>
                </div>
                <span
                  className={`ml-3 shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                    opening.days_until <= 7
                      ? 'bg-red-100 text-red-700'
                      : opening.days_until <= 30
                      ? 'bg-orange-100 text-orange-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {opening.days_until}d
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// MANAGER DASHBOARD
// ─────────────────────────────────────────────────────────────────────────────

function ManagerDashboard({
  tasks,
  approvals,
  profile,
  onTaskClick,
}: {
  tasks: TaskItem[];
  approvals: ApprovalRequestItem[];
  profile: OperatingProfile;
  onTaskClick: (id: string) => void;
}) {
  const pendingApprovals = approvals.filter((a) => a.decision === 'pending');

  const openTasks = tasks.filter((t) => t.status === 'open');
  const stuckTasks = tasks.filter((t) => t.status === 'blocked');
  const doneTasks = tasks.filter((t) => t.status === 'done');
  const activeTasks = tasks.filter((t) => t.status === 'in_progress');

  return (
    <div className="space-y-5">
      {/* Mini stat strip */}
      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard
          color="default"
          icon={CircleDot}
          label="Open"
          value={openTasks.length}
          detail="To do"
        />
        <MetricCard
          color={stuckTasks.length > 0 ? 'red' : 'default'}
          icon={AlertTriangle}
          label="Stuck"
          value={stuckTasks.length}
          detail="Needs help"
        />
        <MetricCard
          color="green"
          icon={CheckCircle2}
          label="Done"
          value={doneTasks.length}
          detail="Completed"
        />
      </div>

      {/* Team actions */}
      <Card>
        <CardHeader title="My Team's Actions" count={tasks.filter((t) => t.status !== 'done' && t.status !== 'cancelled').length} />
        {tasks.length ? (
          <div className="divide-y divide-gray-50">
            {stuckTasks.length > 0 ? (
              <div>
                <p className="bg-red-50 px-5 py-1.5 text-xs font-semibold uppercase tracking-wider text-red-600">
                  Stuck
                </p>
                {stuckTasks.map((task) => (
                  <TaskRow key={task.id} onClick={onTaskClick} showAssignee task={task} />
                ))}
              </div>
            ) : null}
            {activeTasks.length > 0 ? (
              <div>
                <p className="bg-blue-50 px-5 py-1.5 text-xs font-semibold uppercase tracking-wider text-blue-600">
                  In Progress
                </p>
                {activeTasks.map((task) => (
                  <TaskRow key={task.id} onClick={onTaskClick} showAssignee task={task} />
                ))}
              </div>
            ) : null}
            {openTasks.length > 0 ? (
              <div>
                <p className="bg-gray-50 px-5 py-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500">
                  To Do
                </p>
                {openTasks.map((task) => (
                  <TaskRow key={task.id} onClick={onTaskClick} showAssignee task={task} />
                ))}
              </div>
            ) : null}
          </div>
        ) : (
          <p className="px-5 py-8 text-sm text-gray-400">{TASK_LABELS.noTasks}</p>
        )}
      </Card>

      {/* Needs sign-off */}
      {pendingApprovals.length > 0 ? (
        <Card>
          <CardHeader title="Needs Sign-Off" count={pendingApprovals.length} />
          <div className="divide-y divide-gray-50">
            {pendingApprovals.slice(0, 5).map((approval) => (
              <div className="flex items-center justify-between px-5 py-3" key={approval.id}>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {APPROVAL_LABELS.singular} #{approval.id.slice(-6)}
                  </p>
                  <p className="text-xs text-gray-400">
                    Requested {new Date(approval.requested_at).toLocaleDateString('en-ZA')}
                  </p>
                </div>
                <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-700">
                  {APPROVAL_LABELS.decisions.pending}
                </span>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// STAFF DASHBOARD
// ─────────────────────────────────────────────────────────────────────────────

function StaffDashboard({
  tasks,
  notifications,
  onTaskClick,
}: {
  tasks: TaskItem[];
  notifications: NotificationItem[];
  onTaskClick: (id: string) => void;
}) {
  const todo = tasks.filter((t) => t.status === 'open');
  const inProgress = tasks.filter((t) => t.status === 'in_progress');
  const stuck = tasks.filter((t) => t.status === 'blocked');
  const unreadNotifications = notifications.filter((n) => !n.read_at).slice(0, 5);

  const activeSections: { label: string; items: TaskItem[]; accent: string }[] = [
    { label: 'Stuck — Needs Help', items: stuck, accent: 'text-red-600 bg-red-50' },
    { label: 'In Progress', items: inProgress, accent: 'text-blue-600 bg-blue-50' },
    { label: 'To Do', items: todo, accent: 'text-gray-600 bg-gray-50' },
  ].filter((s) => s.items.length > 0);

  return (
    <div className="space-y-5">
      {/* My Actions */}
      <Card>
        <CardHeader
          title="My Actions"
          count={tasks.filter((t) => t.status !== 'done' && t.status !== 'cancelled').length}
        />
        {activeSections.length > 0 ? (
          <div className="divide-y divide-gray-50">
            {activeSections.map(({ label, items, accent }) => (
              <div key={label}>
                <p className={`px-5 py-1.5 text-xs font-semibold uppercase tracking-wider ${accent}`}>
                  {label}
                </p>
                {items.map((task) => (
                  <TaskRow key={task.id} onClick={onTaskClick} task={task} />
                ))}
              </div>
            ))}
          </div>
        ) : (
          <p className="px-5 py-8 text-sm text-gray-400">{TASK_LABELS.myTasksEmpty}</p>
        )}
      </Card>

      {/* Notifications */}
      {notifications.length > 0 ? (
        <Card>
          <CardHeader
            title="Recent Notifications"
            count={unreadNotifications.length > 0 ? unreadNotifications.length : undefined}
          />
          <div className="divide-y divide-gray-50">
            {notifications.slice(0, 5).map((n) => (
              <div className={`px-5 py-3 ${!n.read_at ? 'bg-teal-50/40' : ''}`} key={n.id}>
                <div className="flex items-start gap-3">
                  <BellRing className={`mt-0.5 h-4 w-4 shrink-0 ${!n.read_at ? 'text-teal-600' : 'text-gray-400'}`} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-gray-900">{n.title}</p>
                    {n.message ? (
                      <p className="mt-0.5 text-xs text-gray-500">{n.message}</p>
                    ) : null}
                    <p className="mt-0.5 text-xs text-gray-400">
                      {NOTIFICATION_LABELS.types[n.notification_type] ?? n.notification_type}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// EXTERNAL DASHBOARD
// ─────────────────────────────────────────────────────────────────────────────

function ExternalDashboard({ notifications }: { notifications: NotificationItem[] }) {
  return (
    <div className="space-y-5">
      <Card>
        <CardHeader title="My Engagements" count={notifications.length} />
        {notifications.length ? (
          <div className="divide-y divide-gray-50">
            {notifications.slice(0, 8).map((n) => (
              <div className="flex items-start gap-3 px-5 py-3" key={n.id}>
                <BellRing className={`mt-0.5 h-4 w-4 shrink-0 ${!n.read_at ? 'text-teal-600' : 'text-gray-400'}`} />
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-gray-900">{n.title}</p>
                  {n.message ? (
                    <p className="mt-0.5 text-xs text-gray-500">{n.message}</p>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="px-5 py-8 text-sm text-gray-400">No notifications yet.</p>
        )}
      </Card>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// PAGE
// ─────────────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { tokens, user } = useAuth();
  const token = tokens?.access ?? '';

  const [profile, setProfile] = useState<OperatingProfile | null>(null);
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRequestItem[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [blocked, setBlocked] = useState(false);

  // Task panel state
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  // ── Fetch operating profile first, then role-specific data ────────────────

  useEffect(() => {
    if (!token) return;
    let mounted = true;

    setLoading(true);
    setError('');

    fetchOperatingProfile(token)
      .then(async (p) => {
        if (!mounted) return;
        setProfile(p);

        const kind = dashboardKind(p);
        const isExecutiveLevel =
          kind === 'executive' || kind === 'admin' || kind === 'gm' || kind === 'board';
        const isManager =
          p.primary_position?.authority_level === 'department_manager' || kind === 'admin';
        const isExternal =
          kind === 'client' || kind === 'supplier' || kind === 'artist';

        const fetches: Promise<unknown>[] = [
          fetchNotifications(token).then((r) => { if (mounted) setNotifications(r.results); }).catch(() => {}),
          fetchApprovalRequests(token).then((r) => { if (mounted) setApprovals(r.results); }).catch(() => {}),
        ];

        if (isExecutiveLevel) {
          fetches.push(
            fetchExecutiveSummary(token)
              .then((s) => { if (mounted) setSummary(s); })
              .catch((err: unknown) => {
                if (mounted) {
                  const status = (err as { status?: number })?.status;
                  if (status === 403) setBlocked(true);
                  else setError('Dashboard data could not be loaded.');
                }
              }),
          );
        }

        if (!isExternal) {
          const userId = p.user.id;
          const deptId = p.can_manage_departments[0]?.id ?? undefined;
          const taskParams = isManager && deptId
            ? { department: deptId, page_size: '50' }
            : { assigned_to: userId, page_size: '50' };

          fetches.push(
            fetchTasks(token, taskParams)
              .then((r) => { if (mounted) setTasks(r.results); })
              .catch(() => {}),
          );
        }

        await Promise.allSettled(fetches);
        if (mounted) setLoading(false);
      })
      .catch(() => {
        if (!mounted) return;
        // Still show staff/generic dashboard with empty data
        setLoading(false);
      });

    return () => { mounted = false; };
  }, [token]);

  // ── Task panel update callback ────────────────────────────────────────────

  function handleTaskUpdate(updated: TaskItem) {
    setTasks((prev) =>
      prev.map((t) => (t.id === updated.id ? updated : t)),
    );
  }

  // ── Render ────────────────────────────────────────────────────────────────

  const firstName = user?.first_name ?? '';
  const kind = dashboardKind(profile);
  const isExecutiveLevel =
    kind === 'executive' || kind === 'admin' || kind === 'gm' || kind === 'board';
  const isManager =
    profile?.primary_position?.authority_level === 'department_manager' || kind === 'admin';
  const isExternal =
    kind === 'client' || kind === 'supplier' || kind === 'artist';

  return (
    <AppShell>
      {loading ? (
        <DashboardSkeleton />
      ) : blocked ? (
        <section className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-amber-900">
          <h1 className="text-xl font-bold">Dashboard access is restricted</h1>
          <p className="mt-2 text-sm">
            Your account is signed in, but the system did not grant access to this dashboard.
            Please contact your administrator.
          </p>
        </section>
      ) : (
        <div className="space-y-6">
          {/* Greeting */}
          <GreetingHeader firstName={firstName} profile={profile} />

          {/* Error banner */}
          {error ? (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
              {error}
            </div>
          ) : null}

          {/* Role-based content */}
          {isExecutiveLevel && summary ? (
            <ExecutiveSummaryDashboard
              approvals={approvals}
              onTaskClick={setSelectedTaskId}
              summary={summary}
            />
          ) : isExternal ? (
            <ExternalDashboard notifications={notifications} />
          ) : isManager ? (
            profile ? (
              <ManagerDashboard
                approvals={approvals}
                onTaskClick={setSelectedTaskId}
                profile={profile}
                tasks={tasks}
              />
            ) : null
          ) : (
            <StaffDashboard
              notifications={notifications}
              onTaskClick={setSelectedTaskId}
              tasks={tasks}
            />
          )}
        </div>
      )}

      {/* Task side panel */}
      <TaskPanel
        onClose={() => setSelectedTaskId(null)}
        onTaskUpdate={handleTaskUpdate}
        taskId={selectedTaskId}
      />
    </AppShell>
  );
}

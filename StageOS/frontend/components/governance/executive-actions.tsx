import { CheckCircle2, Clock3, XCircle } from 'lucide-react';
import { StatusBadge } from '@/components/ui/status-badge';
import type {
  DepartmentListItem,
  ExecutiveActionItem,
  OperatingContextListItem,
  UserListItem,
} from '@/lib/api/types';

export const executiveActionTypes = [
  ['comment', 'Comment'],
  ['request_change', 'Request Change'],
  ['flag_issue', 'Flag Issue'],
  ['flag_risk', 'Flag Risk'],
  ['assign_corrective_action', 'Assign Corrective Action'],
  ['approve', 'Approve'],
  ['decline', 'Decline'],
  ['request_more_information', 'Request More Information'],
  ['override', 'Override With Reason'],
  ['escalate', 'Escalate'],
] as const;

export const actionStatusTone: Record<string, 'neutral' | 'info' | 'good' | 'warning' | 'danger'> = {
  open: 'warning',
  acknowledged: 'info',
  completed: 'good',
  cancelled: 'neutral',
};

export function labelFromValue(value: string) {
  return value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function workspaceName(workspaces: OperatingContextListItem[], id?: string | null) {
  return workspaces.find((workspace) => workspace.id === id)?.title ?? 'No Workspace';
}

export function departmentName(departments: DepartmentListItem[], id?: string | null) {
  return departments.find((department) => department.id === id)?.name ?? 'No Department';
}

export function userName(users: UserListItem[], id?: string | null) {
  return users.find((user) => user.id === id)?.full_name ?? 'Unassigned';
}

export function ExecutiveActionList({
  actions,
  departments,
  onAction,
  submitting,
  users,
  workspaces,
}: {
  actions: ExecutiveActionItem[];
  departments: DepartmentListItem[];
  onAction: (action: ExecutiveActionItem, statusAction: 'acknowledge' | 'complete' | 'cancel') => void;
  submitting: boolean;
  users: UserListItem[];
  workspaces: OperatingContextListItem[];
}) {
  if (!actions.length) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white px-4 py-10 text-center text-sm text-slate-500">
        No executive actions returned.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {actions.map((item) => (
        <article className="rounded-lg border border-slate-200 bg-white p-4" key={item.id}>
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-base font-bold text-slate-950">{item.title}</h3>
                <StatusBadge tone={actionStatusTone[item.status]}>{labelFromValue(item.status)}</StatusBadge>
                <StatusBadge tone={item.action_type === 'override' || item.action_type === 'decline' ? 'danger' : 'info'}>
                  {labelFromValue(item.action_type)}
                </StatusBadge>
              </div>
              <div className="mt-1 text-xs text-slate-500">
                {workspaceName(workspaces, item.operating_context)} · {departmentName(departments, item.department)} · {userName(users, item.assigned_to)}
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.reason || 'No reason captured.'}</p>
              {item.instruction ? <p className="mt-2 text-sm leading-6 text-slate-700">{item.instruction}</p> : null}
              <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
                {item.linked_task ? <span>Task linked</span> : null}
                {item.linked_risk ? <span>Risk linked</span> : null}
                {item.linked_corrective_action ? <span>Corrective action linked</span> : null}
                {item.due_date ? <span>Due {item.due_date}</span> : null}
              </div>
            </div>
            <div className="flex flex-wrap gap-2 md:justify-end">
              <ActionButton disabled={submitting || item.status !== 'open'} icon={Clock3} label="Acknowledge" onClick={() => onAction(item, 'acknowledge')} />
              <ActionButton disabled={submitting || item.status === 'completed' || item.status === 'cancelled'} icon={CheckCircle2} label="Complete" onClick={() => onAction(item, 'complete')} />
              <ActionButton disabled={submitting || item.status === 'completed' || item.status === 'cancelled'} icon={XCircle} label="Cancel" onClick={() => onAction(item, 'cancel')} />
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

function ActionButton({
  disabled,
  icon: Icon,
  label,
  onClick,
}: {
  disabled: boolean;
  icon: typeof Clock3;
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
      {label}
    </button>
  );
}

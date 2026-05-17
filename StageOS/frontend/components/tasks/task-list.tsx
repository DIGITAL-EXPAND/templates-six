import { CalendarDays } from 'lucide-react';
import { EvidenceBadge } from '@/components/ui/evidence-badge';
import { PriorityBadge } from '@/components/ui/priority-badge';
import { StatusBadge } from '@/components/ui/status-badge';
import type {
  DepartmentListItem,
  OperatingContextListItem,
  TaskItem,
  UserListItem,
} from '@/lib/api/types';
import { departmentName, isTaskOverdue, userName, workspaceName } from './helpers';

export function TaskList({
  tasks,
  workspaces,
  departments,
  users,
  onSelect,
}: {
  tasks: TaskItem[];
  workspaces: OperatingContextListItem[];
  departments: DepartmentListItem[];
  users: UserListItem[];
  onSelect: (task: TaskItem) => void;
}) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div className="divide-y divide-slate-100">
        {tasks.map((task) => (
          <button
            className="grid w-full gap-3 px-4 py-4 text-left hover:bg-slate-50 lg:grid-cols-[1.3fr_1fr_0.8fr_0.9fr]"
            key={task.id}
            onClick={() => onSelect(task)}
            type="button"
          >
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="truncate text-sm font-bold text-slate-950">{task.title}</h2>
                {isTaskOverdue(task) ? <StatusBadge tone="danger">Overdue</StatusBadge> : null}
              </div>
              <p className="mt-1 truncate text-xs text-slate-500">
                {workspaceName(workspaces, task.operating_context)}
              </p>
            </div>
            <div className="text-sm text-slate-600">
              <div className="font-semibold">{departmentName(departments, task.department)}</div>
              <div className="mt-1 text-xs text-slate-500">{userName(users, task.assigned_to)}</div>
              <div className="mt-1 text-xs text-slate-500 capitalize">{task.work_type.replace('_', ' ')}</div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <PriorityBadge priority={task.priority} />
              <StatusBadge tone={task.status === 'blocked' ? 'warning' : task.status === 'done' ? 'good' : 'neutral'}>
                {task.status.replace('_', ' ')}
              </StatusBadge>
            </div>
            <div className="flex flex-col gap-2 text-sm text-slate-600">
              <div className="flex items-center gap-2">
                <CalendarDays className="h-4 w-4 text-slate-400" />
                {task.due_date ?? 'No due date'}
              </div>
              <EvidenceBadge required={task.evidence_required} provided={task.evidence_provided} />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

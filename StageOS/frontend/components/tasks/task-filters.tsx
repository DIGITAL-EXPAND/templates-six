import type { DepartmentListItem, Priority, TaskStatus } from '@/lib/api/types';

export type TaskFiltersValue = {
  status: 'all' | TaskStatus;
  priority: 'all' | Priority;
  department: 'all' | string;
  overdueOnly: boolean;
};

export function TaskFilters({
  value,
  departments,
  onChange,
}: {
  value: TaskFiltersValue;
  departments: DepartmentListItem[];
  onChange: (next: TaskFiltersValue) => void;
}) {
  return (
    <div className="grid gap-2 md:grid-cols-4">
      <select
        aria-label="Filter tasks by status"
        className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
        onChange={(event) => onChange({ ...value, status: event.target.value as TaskFiltersValue['status'] })}
        value={value.status}
      >
        <option value="all">All statuses</option>
        <option value="open">Open</option>
        <option value="in_progress">In progress</option>
        <option value="blocked">Blocked</option>
        <option value="done">Done</option>
        <option value="cancelled">Cancelled</option>
      </select>
      <select
        aria-label="Filter tasks by priority"
        className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
        onChange={(event) => onChange({ ...value, priority: event.target.value as TaskFiltersValue['priority'] })}
        value={value.priority}
      >
        <option value="all">All priorities</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="critical">Critical</option>
      </select>
      <select
        aria-label="Filter tasks by department"
        className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
        onChange={(event) => onChange({ ...value, department: event.target.value })}
        value={value.department}
      >
        <option value="all">All departments</option>
        {departments.map((department) => (
          <option key={department.id} value={department.id}>
            {department.name}
          </option>
        ))}
      </select>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700">
        <input
          checked={value.overdueOnly}
          onChange={(event) => onChange({ ...value, overdueOnly: event.target.checked })}
          type="checkbox"
        />
        Overdue only
      </label>
    </div>
  );
}

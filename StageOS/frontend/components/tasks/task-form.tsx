'use client';

import { FormEvent, useMemo, useState } from 'react';
import type {
  DepartmentListItem,
  OperatingContextListItem,
  OperatingProfile,
  Priority,
  UserListItem,
} from '@/lib/api/types';

function isAdminOrExecutive(profile: OperatingProfile | null | undefined): boolean {
  const userType = profile?.user.user_type;
  return userType === 'internal_admin' || userType === 'executive';
}

export type TaskFormValues = {
  operating_context: string;
  title: string;
  description: string;
  department: string;
  assigned_to: string;
  work_type: 'general' | 'readiness' | 'evidence' | 'approval_prep' | 'issue_response' | 'follow_up';
  due_date: string;
  priority: Priority;
  evidence_required: boolean;
};

export function TaskForm({
  workspaces,
  departments,
  users,
  profile,
  defaultWorkspaceId = '',
  onSubmit,
}: {
  workspaces: OperatingContextListItem[];
  departments: DepartmentListItem[];
  users: UserListItem[];
  profile?: OperatingProfile | null;
  defaultWorkspaceId?: string;
  onSubmit: (values: TaskFormValues) => Promise<void>;
}) {
  const [values, setValues] = useState<TaskFormValues>({
    operating_context: defaultWorkspaceId || workspaces[0]?.id || '',
    title: '',
    description: '',
    department: '',
    assigned_to: '',
    work_type: 'general',
    due_date: '',
    priority: 'medium',
    evidence_required: false,
  });
  const [submitting, setSubmitting] = useState(false);

  // Filter departments to those the user can assign work in (admins/executives see all)
  const deptOptions = useMemo(() => {
    if (isAdminOrExecutive(profile)) return departments;
    if (!profile?.memberships) return departments;
    const assignableDeptIds = new Set(
      profile.memberships.filter((m) => m.can_assign_work).map((m) => m.department.id),
    );
    return departments.filter((d) => assignableDeptIds.has(d.id));
  }, [departments, profile]);

  // Filter assignees to members of the selected department
  const assigneeOptions = useMemo(() => {
    if (!values.department) return users;
    // UserListItem doesn't carry membership data; show all users when dept is set
    // (server-side filtering via API would be needed for strict isolation)
    return users;
  }, [users, values.department]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(values);
      setValues((current) => ({
        ...current,
        title: '',
        description: '',
        due_date: '',
        evidence_required: false,
      }));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="grid gap-4 rounded-lg border border-slate-200 bg-white p-4" onSubmit={handleSubmit}>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="task-title">
            Task title
          </label>
          <input
            className="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950"
            id="task-title"
            onChange={(event) => setValues({ ...values, title: event.target.value })}
            required
            value={values.title}
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="task-workspace">
            Workspace
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            disabled={Boolean(defaultWorkspaceId)}
            id="task-workspace"
            onChange={(event) => setValues({ ...values, operating_context: event.target.value })}
            required
            value={values.operating_context}
          >
            {workspaces.map((workspace) => (
              <option key={workspace.id} value={workspace.id}>
                {workspace.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="task-description">
          Notes
        </label>
        <textarea
          className="min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950"
          id="task-description"
          onChange={(event) => setValues({ ...values, description: event.target.value })}
          value={values.description}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-5">
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="task-work-type">
            Work type
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            id="task-work-type"
            onChange={(event) => setValues({ ...values, work_type: event.target.value as TaskFormValues['work_type'] })}
            value={values.work_type}
          >
            <option value="general">General</option>
            <option value="readiness">Readiness</option>
            <option value="evidence">Evidence</option>
            <option value="approval_prep">Approval preparation</option>
            <option value="issue_response">Issue response</option>
            <option value="follow_up">Follow up</option>
          </select>
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="task-department">
            Department
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            id="task-department"
            onChange={(event) => setValues({ ...values, department: event.target.value })}
            value={values.department}
          >
            <option value="">No department</option>
            {deptOptions.map((department) => (
              <option key={department.id} value={department.id}>
                {department.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="task-assignee">
            Assignee
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            id="task-assignee"
            onChange={(event) => setValues({ ...values, assigned_to: event.target.value })}
            value={values.assigned_to}
          >
            <option value="">Unassigned</option>
            {assigneeOptions.map((user) => (
              <option key={user.id} value={user.id}>
                {user.full_name || user.email}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="task-date">
            Due date
          </label>
          <input
            className="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950"
            id="task-date"
            onChange={(event) => setValues({ ...values, due_date: event.target.value })}
            type="date"
            value={values.due_date}
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="task-priority">
            Priority
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            id="task-priority"
            onChange={(event) => setValues({ ...values, priority: event.target.value as Priority })}
            value={values.priority}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm font-semibold text-slate-700">
        <input
          checked={values.evidence_required}
          onChange={(event) => setValues({ ...values, evidence_required: event.target.checked })}
          type="checkbox"
        />
        Evidence is required before completion
      </label>

      <button
        className="inline-flex h-10 w-fit items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        disabled={submitting || !values.operating_context}
        type="submit"
      >
        {submitting ? 'Creating' : 'Create Task'}
      </button>
    </form>
  );
}

import type {
  DepartmentListItem,
  OperatingContextListItem,
  TaskItem,
  UserListItem,
} from '@/lib/api/types';
import { workspaceTypeLabel } from '@/lib/workspaces/labels';

export function isTaskOverdue(task: TaskItem) {
  if (!task.due_date || task.status === 'done' || task.status === 'cancelled') {
    return false;
  }
  return task.due_date < new Date().toISOString().slice(0, 10);
}

export function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  const workspace = workspaces.find((item) => item.id === id);
  if (!workspace) {
    return 'Workspace unavailable';
  }
  return `${workspace.title} (${workspaceTypeLabel(workspace.context_type)})`;
}

export function departmentName(departments: DepartmentListItem[], id: string | null) {
  if (!id) {
    return 'Unassigned department';
  }
  return departments.find((item) => item.id === id)?.name ?? 'Department unavailable';
}

export function userName(users: UserListItem[], id: string | null) {
  if (!id) {
    return 'Unassigned';
  }
  const user = users.find((item) => item.id === id);
  return user?.full_name || user?.email || 'User unavailable';
}

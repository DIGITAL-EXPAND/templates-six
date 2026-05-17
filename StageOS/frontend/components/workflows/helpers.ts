import type {
  DepartmentListItem,
  DocumentItem,
  UserListItem,
  WorkflowInstanceItem,
  WorkflowStepItem,
  WorkflowStepTemplateItem,
  WorkflowTemplateItem,
} from '@/lib/api/types';

export function workflowName(instances: WorkflowInstanceItem[], templates: WorkflowTemplateItem[], step: WorkflowStepItem) {
  const instance = instances.find((item) => item.id === step.workflow_instance);
  const template = templates.find((item) => item.id === instance?.template);
  return template?.name ?? 'Process unavailable';
}

export function stepTemplate(templates: WorkflowStepTemplateItem[], step: WorkflowStepItem) {
  return templates.find((item) => item.id === step.step_template);
}

export function departmentName(departments: DepartmentListItem[], id: string | null | undefined) {
  if (!id) {
    return 'No owner department';
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

export function documentTitle(documents: DocumentItem[], id: string | null) {
  if (!id) {
    return 'No evidence document';
  }
  return documents.find((item) => item.id === id)?.title ?? 'Evidence unavailable';
}

export function dueLabel(date: string | null) {
  if (!date) {
    return 'No SLA date';
  }
  return new Date(date).toLocaleDateString();
}

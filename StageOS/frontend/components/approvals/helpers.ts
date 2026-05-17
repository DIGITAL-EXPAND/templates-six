import type {
  ApprovalRequestItem,
  ApprovalStepItem,
  DocumentItem,
  OperatingContextListItem,
  UserListItem,
} from '@/lib/api/types';

export function approvalStepName(steps: ApprovalStepItem[], id: string) {
  const step = steps.find((item) => item.id === id);
  return step ? `Step ${step.step_number}: ${step.name}` : 'Approval step unavailable';
}

export function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  return workspaces.find((item) => item.id === id)?.title ?? 'Workspace unavailable';
}

export function userName(users: UserListItem[], id: string | null) {
  if (!id) {
    return 'Not decided';
  }
  const user = users.find((item) => item.id === id);
  return user?.full_name || user?.email || 'User unavailable';
}

export function documentTitle(documents: DocumentItem[], id: string | null) {
  if (!id) {
    return 'No evidence reviewed';
  }
  return documents.find((item) => item.id === id)?.title ?? 'Evidence unavailable';
}

export function isPendingApproval(item: ApprovalRequestItem) {
  return item.decision === 'pending';
}

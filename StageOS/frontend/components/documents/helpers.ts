import type {
  DocumentItem,
  EvidenceSubmissionItem,
  OperatingContextListItem,
  TaskItem,
  UserListItem,
} from '@/lib/api/types';
import { workspaceTypeLabel } from '@/lib/workspaces/labels';

export function documentTypeLabel(value: string) {
  return value
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

export function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  const workspace = workspaces.find((item) => item.id === id);
  if (!workspace) {
    return 'Workspace unavailable';
  }
  return `${workspace.title} (${workspaceTypeLabel(workspace.context_type)})`;
}

export function userName(users: UserListItem[], id: string | null) {
  if (!id) {
    return 'Unknown user';
  }
  const user = users.find((item) => item.id === id);
  return user?.full_name || user?.email || 'User unavailable';
}

export function taskName(tasks: TaskItem[], id: string | null) {
  if (!id) {
    return 'No task linked';
  }
  return tasks.find((task) => task.id === id)?.title ?? 'Task unavailable';
}

export function evidenceStatus(evidence: EvidenceSubmissionItem) {
  if (evidence.rejected) {
    return 'rejected';
  }
  return evidence.accepted ? 'accepted' : 'pending';
}

export function hasEvidenceForDocument(document: DocumentItem, evidence: EvidenceSubmissionItem[]) {
  return evidence.some((item) => item.document === document.id);
}

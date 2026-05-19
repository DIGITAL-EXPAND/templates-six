'use client';

// Backwards-compatible wrapper: tasks/page.tsx and workspace-tasks-tab.tsx
// pass a full TaskItem object plus action callbacks. TaskPanel only needs
// taskId + onClose + onTaskUpdate, so we extract those here.

import type { TaskItem } from '@/lib/api/types';
import { TaskPanel } from './TaskPanel';
import type { TaskPanelProps } from './TaskPanel';

export type TaskDetailDrawerProps = Omit<TaskPanelProps, 'taskId'> & {
  task?: TaskItem | null;
  // Legacy props — accepted but ignored (TaskPanel handles its own actions)
  completing?: boolean;
  departments?: unknown[];
  onComplete?: (task: TaskItem) => void | Promise<void>;
  onStart?: (task: TaskItem) => void | Promise<void>;
  onBlock?: (task: TaskItem, comment: string) => void | Promise<void>;
  users?: unknown[];
  workspaces?: unknown[];
};

export function TaskDetailDrawer({
  task,
  onClose,
  onTaskUpdate,
  // legacy props intentionally unused
  completing: _completing,
  departments: _departments,
  onComplete: _onComplete,
  onStart: _onStart,
  onBlock: _onBlock,
  users: _users,
  workspaces: _workspaces,
}: TaskDetailDrawerProps) {
  return (
    <TaskPanel
      taskId={task?.id ?? null}
      onClose={onClose}
      onTaskUpdate={onTaskUpdate}
    />
  );
}

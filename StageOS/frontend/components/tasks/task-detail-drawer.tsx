'use client';

// TaskPanel.tsx is the new authoritative task panel component.
// This file re-exports it as TaskDetailDrawer for backwards compatibility
// with any existing page that imports from this path.
//
// New code should import TaskPanel directly from './TaskPanel'.

export { TaskPanel as TaskDetailDrawer } from './TaskPanel';
export type { TaskPanelProps as TaskDetailDrawerProps } from './TaskPanel';

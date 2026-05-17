'use client';

import { useEffect, useMemo, useState } from 'react';
import { TaskDetailDrawer } from '@/components/tasks/task-detail-drawer';
import { TaskForm, type TaskFormValues } from '@/components/tasks/task-form';
import { isTaskOverdue } from '@/components/tasks/helpers';
import { TaskList } from '@/components/tasks/task-list';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  completeTask,
  blockTask,
  createTask,
  fetchDepartments,
  fetchOperatingContexts,
  fetchTasks,
  fetchUsers,
  startTask,
} from '@/lib/api/endpoints';
import type {
  DepartmentListItem,
  OperatingContextListItem,
  TaskItem,
  UserListItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceTasksTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [selectedTask, setSelectedTask] = useState<TaskItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [completing, setCompleting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) {
      return;
    }

    let mounted = true;
    Promise.all([
      fetchTasks(tokens.access, { operating_context: workspaceId }),
      fetchOperatingContexts(tokens.access),
      fetchDepartments(tokens.access),
      fetchUsers(tokens.access),
    ])
      .then(([taskResponse, workspaceResponse, departmentResponse, userResponse]) => {
        if (!mounted) {
          return;
        }
        setTasks(taskResponse.results);
        setWorkspaces(workspaceResponse.results);
        setDepartments(departmentResponse.results);
        setUsers(userResponse.results);
      })
      .catch((err) => {
        if (!mounted) {
          return;
        }
        if (err instanceof ApiError && err.status === 403) {
          setPermissionDenied(true);
        } else {
          setError('Tasks could not be loaded for this Workspace.');
        }
      })
      .finally(() => {
        if (mounted) {
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [tokens?.access, workspaceId]);

  const visibleTasks = useMemo(
    () => [...tasks].sort((a, b) => Number(isTaskOverdue(b)) - Number(isTaskOverdue(a))),
    [tasks],
  );

  async function handleCreateTask(values: TaskFormValues) {
    if (!tokens?.access) {
      return;
    }
    setError('');
    try {
      const task = await createTask(tokens.access, {
        operating_context: workspaceId,
        title: values.title,
        description: values.description,
        department: values.department || null,
        assigned_to: values.assigned_to || null,
        work_type: values.work_type,
        due_date: values.due_date || null,
        priority: values.priority,
        evidence_required: values.evidence_required,
      });
      setTasks((current) => [task, ...current]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setPermissionDenied(true);
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Task could not be created.');
      }
    }
  }

  async function handleCompleteTask(task: TaskItem) {
    if (!tokens?.access) {
      return;
    }
    setCompleting(true);
    setError('');
    try {
      const updated = await completeTask(tokens.access, task.id, task.evidence_provided);
      setTasks((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setSelectedTask(updated);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setPermissionDenied(true);
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Task could not be completed.');
      }
    } finally {
      setCompleting(false);
    }
  }

  async function handleStartTask(task: TaskItem) {
    if (!tokens?.access) return;
    setError('');
    try {
      const updated = await startTask(tokens.access, task.id);
      setTasks((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setSelectedTask(updated);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Task could not be started.');
    }
  }

  async function handleBlockTask(task: TaskItem, comment: string) {
    if (!tokens?.access) return;
    setError('');
    try {
      const updated = await blockTask(tokens.access, task.id, comment);
      setTasks((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setSelectedTask(updated);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Task could not be blocked.');
    }
  }

  if (loading) {
    return <LoadingState label="Loading Workspace tasks" />;
  }

  return (
    <div className="space-y-4">
      {permissionDenied ? <PermissionDeniedState /> : null}
      {error ? <ErrorState message={error} /> : null}
      <TaskForm
        defaultWorkspaceId={workspaceId}
        departments={departments}
        onSubmit={handleCreateTask}
        users={users}
        workspaces={workspaces}
      />
      {visibleTasks.length ? (
        <TaskList
          departments={departments}
          onSelect={setSelectedTask}
          tasks={visibleTasks}
          users={users}
          workspaces={workspaces}
        />
      ) : (
        <EmptyState description="Create the first task for this Workspace." title="No tasks yet" />
      )}
      <TaskDetailDrawer
        completing={completing}
        departments={departments}
        onClose={() => setSelectedTask(null)}
        onBlock={handleBlockTask}
        onComplete={handleCompleteTask}
        onStart={handleStartTask}
        task={selectedTask}
        users={users}
        workspaces={workspaces}
      />
    </div>
  );
}

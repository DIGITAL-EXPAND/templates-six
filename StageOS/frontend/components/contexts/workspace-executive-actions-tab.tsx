'use client';

import { useEffect, useState } from 'react';
import { ExecutiveActionList } from '@/components/governance/executive-actions';
import { ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  fetchDepartments,
  fetchExecutiveActions,
  fetchOperatingContexts,
  fetchUsers,
  setExecutiveActionStatus,
} from '@/lib/api/endpoints';
import type {
  DepartmentListItem,
  ExecutiveActionItem,
  OperatingContextListItem,
  UserListItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceExecutiveActionsTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [actions, setActions] = useState<ExecutiveActionItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([
      fetchExecutiveActions(tokens.access, { operating_context: workspaceId }),
      fetchOperatingContexts(tokens.access),
      fetchDepartments(tokens.access),
      fetchUsers(tokens.access),
    ])
      .then(([actionResult, workspaceResult, departmentResult, userResult]) => {
        if (!mounted) return;
        if (actionResult.status === 'fulfilled') setActions(actionResult.value.results);
        else if (actionResult.reason instanceof ApiError && actionResult.reason.status === 403) setPermissionDenied(true);
        else setError('Executive actions could not be loaded for this Workspace.');
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
        if (departmentResult.status === 'fulfilled') setDepartments(departmentResult.value.results);
        if (userResult.status === 'fulfilled') setUsers(userResult.value.results);
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access, workspaceId]);

  async function handleAction(item: ExecutiveActionItem, statusAction: 'acknowledge' | 'complete' | 'cancel') {
    if (!tokens?.access) return;
    setSubmitting(true);
    setError('');
    try {
      const updated = await setExecutiveActionStatus(tokens.access, item.id, statusAction, comment);
      setActions((current) => current.map((action) => (action.id === updated.id ? updated : action)));
      setComment('');
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Executive action update failed.');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingState label="Loading executive actions" />;

  return (
    <div className="space-y-3">
      {permissionDenied ? <PermissionDeniedState /> : null}
      {error ? <ErrorState message={error} /> : null}
      <input
        className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
        onChange={(event) => setComment(event.target.value)}
        placeholder="Status action comment"
        value={comment}
      />
      <ExecutiveActionList
        actions={actions}
        departments={departments}
        onAction={handleAction}
        submitting={submitting}
        users={users}
        workspaces={workspaces}
      />
    </div>
  );
}

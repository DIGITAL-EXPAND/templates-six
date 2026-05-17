'use client';

import { useEffect, useMemo, useState } from 'react';
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

type StatusAction = 'acknowledge' | 'complete' | 'cancel';

export function DepartmentExecutiveActionsPanel({
  departmentTypes,
  targetTypes = [],
  title = 'Executive actions',
}: {
  departmentTypes: string[];
  targetTypes?: string[];
  title?: string;
}) {
  const { tokens } = useAuth();
  const [actions, setActions] = useState<ExecutiveActionItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.all([
      fetchExecutiveActions(tokens.access),
      fetchDepartments(tokens.access),
      fetchOperatingContexts(tokens.access),
      fetchUsers(tokens.access),
    ])
      .then(([actionResponse, departmentResponse, workspaceResponse, userResponse]) => {
        if (!mounted) return;
        setActions(actionResponse.results);
        setDepartments(departmentResponse.results);
        setWorkspaces(workspaceResponse.results);
        setUsers(userResponse.results);
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('Executive actions could not be loaded for this department.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  const departmentIds = useMemo(
    () => new Set(departments.filter((department) => departmentTypes.includes(department.department_type)).map((department) => department.id)),
    [departments, departmentTypes],
  );
  const filteredActions = useMemo(
    () => actions.filter((action) => {
      if (action.department && departmentIds.has(action.department)) return true;
      if (action.target_type && targetTypes.includes(action.target_type)) return true;
      return false;
    }),
    [actions, departmentIds, targetTypes],
  );

  async function handleStatusAction(item: ExecutiveActionItem, statusAction: StatusAction) {
    if (!tokens?.access) return;
    setSubmitting(true);
    setError('');
    try {
      const comment = window.prompt(`${statusAction.replace('-', ' ')} comment`) ?? '';
      const updated = await setExecutiveActionStatus(tokens.access, item.id, statusAction, comment);
      setActions((current) => current.map((action) => (action.id === updated.id ? updated : action)));
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to update this executive action.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Executive action could not be updated.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-950">{title}</h2>
          <p className="mt-1 text-sm text-slate-500">Acknowledge or complete executive instructions assigned to this department.</p>
        </div>
        <span className="rounded-md border border-slate-200 px-2 py-1 text-xs font-bold text-slate-600">{filteredActions.length}</span>
      </div>
      {permissionDenied ? <PermissionDeniedState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {loading ? (
        <LoadingState label="Loading executive actions" />
      ) : (
        <ExecutiveActionList
          actions={filteredActions}
          departments={departments}
          onAction={handleStatusAction}
          submitting={submitting}
          users={users}
          workspaces={workspaces}
        />
      )}
    </section>
  );
}

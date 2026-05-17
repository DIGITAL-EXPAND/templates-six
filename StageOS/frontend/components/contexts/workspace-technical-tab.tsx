'use client';

import { useEffect, useState } from 'react';
import { TechnicalActionDialog, TechnicalRiderList, type TechnicalAction } from '@/components/technical/technical-components';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { fetchCrewRequirements, fetchEquipmentRequirements, fetchOperatingContexts, fetchTechnicalRiders, fetchUsers, setRiderAction } from '@/lib/api/endpoints';
import type { CrewRequirementItem, EquipmentRequirementItem, OperatingContextListItem, TechnicalRiderItem, UserListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceTechnicalTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [riders, setRiders] = useState<TechnicalRiderItem[]>([]);
  const [crew, setCrew] = useState<CrewRequirementItem[]>([]);
  const [equipment, setEquipment] = useState<EquipmentRequirementItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [action, setAction] = useState<TechnicalAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.all([fetchTechnicalRiders(tokens.access), fetchCrewRequirements(tokens.access), fetchEquipmentRequirements(tokens.access), fetchOperatingContexts(tokens.access), fetchUsers(tokens.access)])
      .then(([riderResponse, crewResponse, equipmentResponse, workspaceResponse, userResponse]) => {
        if (!mounted) return;
        const scoped = riderResponse.results.filter((rider) => rider.operating_context === workspaceId);
        const riderIds = new Set(scoped.map((rider) => rider.id));
        setRiders(scoped);
        setCrew(crewResponse.results.filter((item) => riderIds.has(item.rider)));
        setEquipment(equipmentResponse.results.filter((item) => riderIds.has(item.rider)));
        setWorkspaces(workspaceResponse.results);
        setUsers(userResponse.results);
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('Technical readiness could not be loaded for this Workspace.');
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access, workspaceId]);

  async function handleAction(comment: string) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    try {
      const updated = await setRiderAction(tokens.access, action.rider.id, action.kind, comment);
      setRiders((current) => current.map((rider) => rider.id === updated.id ? updated : rider));
      setAction(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to perform this technical action.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Technical action could not be completed.');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingState label="Loading Workspace technical readiness" />;
  return <div className="space-y-4">{permissionDenied ? <PermissionDeniedState /> : null}{error ? <ErrorState message={error} /> : null}{riders.length ? <TechnicalRiderList crew={crew} equipment={equipment} onAction={setAction} riders={riders} users={users} workspaces={workspaces} /> : <EmptyState description="Technical riders linked to this Workspace will appear here." title="No technical rider yet" />}<TechnicalActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} /></div>;
}


'use client';

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DepartmentExecutiveActionsPanel } from '@/components/governance/department-executive-actions-panel';
import {
  TechnicalActionDialog,
  TechnicalFilters,
  TechnicalRiderList,
  riderCrew,
  riderEquipment,
  technicalBlockers,
  type TechnicalAction,
} from '@/components/technical/technical-components';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  fetchCrewRequirements,
  fetchEquipmentRequirements,
  fetchOperatingContexts,
  fetchTechnicalRiders,
  fetchUsers,
  setRiderAction,
} from '@/lib/api/endpoints';
import type { CrewRequirementItem, EquipmentRequirementItem, OperatingContextListItem, TechnicalRiderItem, UserListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export default function TechnicalPage() {
  const { tokens } = useAuth();
  const [riders, setRiders] = useState<TechnicalRiderItem[]>([]);
  const [crew, setCrew] = useState<CrewRequirementItem[]>([]);
  const [equipment, setEquipment] = useState<EquipmentRequirementItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [filters, setFilters] = useState({ status: 'all', workspace: 'all', source: 'all', pending: false, missing: false });
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
        setRiders(riderResponse.results);
        setCrew(crewResponse.results);
        setEquipment(equipmentResponse.results);
        setWorkspaces(workspaceResponse.results);
        setUsers(userResponse.results);
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('Technical riders could not be loaded.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  const sources = useMemo(() => Array.from(new Set(equipment.map((item) => item.source))).sort(), [equipment]);
  const filteredRiders = useMemo(() => riders.filter((rider) => {
    const riderCrewItems = riderCrew(crew, rider.id);
    const riderEquipmentItems = riderEquipment(equipment, rider.id);
    if (filters.status !== 'all' && rider.status !== filters.status) return false;
    if (filters.workspace !== 'all' && rider.operating_context !== filters.workspace) return false;
    if (filters.source !== 'all' && !riderEquipmentItems.some((item) => item.source === filters.source)) return false;
    if (filters.pending && !['submitted', 'under_review'].includes(rider.status)) return false;
    if (filters.missing && !technicalBlockers(rider, riderCrewItems, riderEquipmentItems).length) return false;
    return true;
  }), [crew, equipment, filters, riders]);

  async function handleAction(comment: string) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    setError('');
    try {
      const updated = await setRiderAction(tokens.access, action.rider.id, action.kind, comment);
      setRiders((current) => current.map((rider) => (rider.id === updated.id ? updated : rider)));
      setAction(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to perform this technical action.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Technical action could not be completed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader description="Track rider status, crew needs, equipment requirements and approval readiness." eyebrow="Technical" title="Technical" />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading technical riders" /> : (
          <>
            <TechnicalFilters onChange={setFilters} sources={sources} value={filters} workspaces={workspaces} />
            <DepartmentExecutiveActionsPanel departmentTypes={['technical']} targetTypes={['TechnicalRider', 'CrewRequirement', 'EquipmentRequirement']} />
            {filteredRiders.length ? <TechnicalRiderList crew={crew} equipment={equipment} onAction={setAction} riders={filteredRiders} users={users} workspaces={workspaces} /> : <EmptyState description="Technical riders will appear here when records are available or filters are cleared." title="No technical riders found" />}
          </>
        )}
      </div>
      <TechnicalActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </AppShell>
  );
}

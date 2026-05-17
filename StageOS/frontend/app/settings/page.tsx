'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import {
  AccessAndRolesCard,
  AdminControlsPanel,
  OrganisationSettingsCard,
  OperatingModelAdminCard,
  PreferencesPlaceholderCard,
  ProfileSettingsCard,
  SecuritySettingsCard,
} from '@/components/settings/settings-components';
import { PageHeader } from '@/components/ui/page-header';
import { ErrorState, LoadingState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { apiRequest } from '@/lib/api/client';
import {
  fetchDepartments,
  fetchModuleActivations,
  fetchOperatingModels,
  fetchOrganisations,
  fetchPositions,
  fetchSites,
  fetchUserDepartmentMemberships,
  fetchUsers,
} from '@/lib/api/endpoints';
import type {
  DepartmentListItem,
  ModuleActivationItem,
  OperatingModelItem,
  OrganisationItem,
  PositionItem,
  SiteListItem,
  UserDepartmentMembershipItem,
  UserListItem,
  UserRole,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export default function SettingsPage() {
  const { tokens, user, logout } = useAuth();
  const [organisations, setOrganisations] = useState<OrganisationItem[]>([]);
  const [sites, setSites] = useState<SiteListItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [operatingModels, setOperatingModels] = useState<OperatingModelItem[]>([]);
  const [positions, setPositions] = useState<PositionItem[]>([]);
  const [memberships, setMemberships] = useState<UserDepartmentMembershipItem[]>([]);
  const [moduleActivations, setModuleActivations] = useState<ModuleActivationItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [adminBlocked, setAdminBlocked] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([
      fetchOrganisations(tokens.access),
      fetchSites(tokens.access),
      fetchDepartments(tokens.access),
      fetchUsers(tokens.access),
      fetchOperatingModels(tokens.access),
      fetchPositions(tokens.access),
      fetchUserDepartmentMemberships(tokens.access),
      fetchModuleActivations(tokens.access),
    ])
      .then(([organisationResult, siteResult, departmentResult, userResult, operatingModelResult, positionResult, membershipResult, moduleResult]) => {
        if (!mounted) return;
        if (organisationResult.status === 'fulfilled') setOrganisations(organisationResult.value.results);
        if (siteResult.status === 'fulfilled') setSites(siteResult.value.results);
        if (departmentResult.status === 'fulfilled') setDepartments(departmentResult.value.results);
        if (userResult.status === 'fulfilled') setUsers(userResult.value.results);
        else if (userResult.reason instanceof ApiError && userResult.reason.status === 403) setAdminBlocked(true);
        if (operatingModelResult.status === 'fulfilled') setOperatingModels(operatingModelResult.value.results);
        if (positionResult.status === 'fulfilled') setPositions(positionResult.value.results);
        if (membershipResult.status === 'fulfilled') setMemberships(membershipResult.value.results);
        if (moduleResult.status === 'fulfilled') setModuleActivations(moduleResult.value.results);
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access]);

  async function handleCreateUser(values: { email: string; password: string; first_name: string; last_name: string; user_type: UserRole }) {
    if (!tokens?.access) return;
    setSubmitting(true);
    setError('');
    try {
      const created = await apiRequest<UserListItem>('/api/v1/users/', {
        method: 'POST',
        token: tokens.access,
        body: values,
      });
      setUsers((current) => [created, ...current]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to manage administration settings.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('User could not be created.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader description="Review your profile, organisation settings, access and permission-controlled admin controls." eyebrow="Settings" title="Settings" />
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading settings" /> : (
          <>
            <ProfileSettingsCard user={user} />
            <OrganisationSettingsCard departments={departments} organisations={organisations} sites={sites} />
            <OperatingModelAdminCard
              memberships={memberships}
              moduleActivations={moduleActivations}
              operatingModels={operatingModels}
              positions={positions}
            />
            <AccessAndRolesCard user={user} />
            <PreferencesPlaceholderCard />
            <SecuritySettingsCard onLogout={logout} />
            <AdminControlsPanel blocked={adminBlocked} onCreate={handleCreateUser} submitting={submitting} users={users} />
          </>
        )}
      </div>
    </AppShell>
  );
}

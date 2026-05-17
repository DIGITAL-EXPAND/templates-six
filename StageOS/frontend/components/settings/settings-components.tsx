'use client';

import { FormEvent, useState } from 'react';
import { RoleBadge } from '@/components/ui/role-badge';
import { EmptyState, PermissionDeniedState } from '@/components/ui/states';
import { RestrictedField, ReadinessBadge } from '@/components/readiness/shared';
import type {
  CurrentUser,
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

export function SettingsSection({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4">
      <h2 className="text-base font-bold text-slate-950">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
      <div className="mt-4">{children}</div>
    </section>
  );
}

export function ProfileSettingsCard({ user }: { user: CurrentUser | null }) {
  return (
    <SettingsSection title="Profile" description="Your profile is managed by your organisation account. Some settings are controlled by your organisation administrator.">
      <dl className="grid gap-3 md:grid-cols-2">
        <Info label="Name" value={user?.full_name || `${user?.first_name ?? ''} ${user?.last_name ?? ''}`.trim()} />
        <Info label="Email" value={user?.email} />
        <div>
          <dt className="text-xs font-bold uppercase tracking-normal text-slate-500">Access level</dt>
          <dd className="mt-1">{user ? <RoleBadge role={user.user_type} /> : <span className="text-sm text-slate-500">Not signed in</span>}</dd>
        </div>
        <Info label="Session status" value={user?.is_active ? 'Active' : 'Unavailable'} />
      </dl>
    </SettingsSection>
  );
}

export function OrganisationSettingsCard({ organisations, sites, departments }: { organisations: OrganisationItem[]; sites: SiteListItem[]; departments: DepartmentListItem[] }) {
  const organisation = organisations[0];
  return (
    <SettingsSection title="Organisation" description="Organisation, site and department records are shown from backend data when your role permits access.">
      <dl className="grid gap-3 md:grid-cols-3">
        <Info label="Organisation" value={organisation?.name} />
        <Info label="Status" value={organisation ? (organisation.is_active ? 'Active' : 'Inactive') : ''} />
        <Info label="Sites" value={String(sites.length)} />
        <Info label="Departments" value={String(departments.length)} />
      </dl>
    </SettingsSection>
  );
}

export function AccessAndRolesCard({ user }: { user: CurrentUser | null }) {
  return (
    <SettingsSection title="Access and Roles" description="StageOS uses backend permissions as the source of truth. The frontend reflects only the records and actions the API permits.">
      <div className="grid gap-3 md:grid-cols-2">
        <div className="rounded-md border border-slate-200 p-3">
          <div className="text-xs font-bold uppercase tracking-normal text-slate-500">Current access</div>
          <div className="mt-2">{user ? <RoleBadge role={user.user_type} /> : 'Unavailable'}</div>
        </div>
        <div className="rounded-md border border-slate-200 p-3 text-sm text-slate-600">
          This action requires additional approval authority where the backend enforces it. Contact your organisation administrator if this access is incorrect.
        </div>
      </div>
    </SettingsSection>
  );
}

export function OperatingModelAdminCard({
  memberships,
  moduleActivations,
  operatingModels,
  positions,
}: {
  memberships: UserDepartmentMembershipItem[];
  moduleActivations: ModuleActivationItem[];
  operatingModels: OperatingModelItem[];
  positions: PositionItem[];
}) {
  const defaultModel = operatingModels.find((model) => model.is_default) ?? operatingModels[0];
  return (
    <SettingsSection title="Operating Model" description="Organisation structure, positions, memberships and module activation are configured by the backend.">
      <div className="grid gap-3 md:grid-cols-4">
        <Info label="Active model" value={defaultModel?.name} />
        <Info label="Model type" value={defaultModel?.model_type?.replaceAll('_', ' ')} />
        <Info label="Positions" value={String(positions.length)} />
        <Info label="Memberships" value={String(memberships.length)} />
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="rounded-md border border-slate-200 p-3">
          <h3 className="text-sm font-bold text-slate-950">Positions</h3>
          <div className="mt-3 space-y-2">
            {positions.slice(0, 8).map((position) => (
              <div className="text-sm text-slate-700" key={position.id}>
                <span className="font-semibold text-slate-900">{position.title}</span>
                <span className="text-slate-500"> · {position.department_name} · {position.authority_level.replaceAll('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-md border border-slate-200 p-3">
          <h3 className="text-sm font-bold text-slate-950">Module activations</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {moduleActivations.map((module) => (
              <span className="rounded-md border border-slate-200 px-2 py-1 text-xs font-semibold text-slate-700" key={module.id}>
                {module.label}
              </span>
            ))}
          </div>
        </div>
      </div>
    </SettingsSection>
  );
}

export function PreferencesPlaceholderCard() {
  return (
    <SettingsSection title="Preferences" description="Notification, display and default Workspace filters can be added when backend preference endpoints are available.">
      <div className="grid gap-3 md:grid-cols-3">
        <Placeholder label="Notification preferences" />
        <Placeholder label="Display preferences" />
        <Placeholder label="Default site and Workspace filters" />
      </div>
    </SettingsSection>
  );
}

export function SecuritySettingsCard({ onLogout }: { onLogout: () => void }) {
  return (
    <SettingsSection title="Security" description="Your current browser session is active. Password reset and MFA controls can be added when backend endpoints are available.">
      <button className="h-10 rounded-md bg-slate-950 px-4 text-sm font-bold text-white hover:bg-slate-800" onClick={onLogout} type="button">Sign out</button>
    </SettingsSection>
  );
}

export function AdminControlsPanel({
  users,
  blocked,
  onCreate,
  submitting,
}: {
  users: UserListItem[];
  blocked: boolean;
  onCreate: (values: { email: string; password: string; first_name: string; last_name: string; user_type: UserRole }) => void;
  submitting: boolean;
}) {
  const [showForm, setShowForm] = useState(false);

  if (blocked) {
    return (
      <SettingsSection title="Admin Controls" description="Administration settings are permission-controlled.">
        <PermissionDeniedState />
        <p className="mt-3 text-sm text-slate-500">You do not have permission to manage administration settings.</p>
      </SettingsSection>
    );
  }

  return (
    <SettingsSection title="Admin Controls" description="User access is shown only when the backend permits it. Role assignment and user creation are validated by the backend.">
      <div className="mb-4 flex justify-end">
        <button className="h-9 rounded-md bg-blue-600 px-3 text-sm font-bold text-white" onClick={() => setShowForm((value) => !value)} type="button">Invite / create user</button>
      </div>
      {showForm ? <CreateUserForm onSubmit={onCreate} submitting={submitting} /> : null}
      {users.length ? <UserAccessList users={users} /> : <EmptyState title="No users returned" description="User access records will appear here when the backend returns them." />}
    </SettingsSection>
  );
}

function CreateUserForm({ onSubmit, submitting }: { onSubmit: (values: { email: string; password: string; first_name: string; last_name: string; user_type: UserRole }) => void; submitting: boolean }) {
  const [values, setValues] = useState({ email: '', password: '', first_name: '', last_name: '', user_type: 'staff' as UserRole });
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(values);
  }
  return (
    <form className="mb-4 grid gap-3 rounded-md border border-slate-200 p-3 md:grid-cols-2" onSubmit={submit}>
      <Input label="Email" onChange={(value) => setValues({ ...values, email: value })} type="email" value={values.email} />
      <Input label="Temporary password" onChange={(value) => setValues({ ...values, password: value })} type="password" value={values.password} />
      <Input label="First name" onChange={(value) => setValues({ ...values, first_name: value })} value={values.first_name} />
      <Input label="Last name" onChange={(value) => setValues({ ...values, last_name: value })} value={values.last_name} />
      <label className="text-sm font-bold text-slate-800">
        User type
        <select className="mt-2 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950" onChange={(event) => setValues({ ...values, user_type: event.target.value as UserRole })} value={values.user_type}>
          {['executive', 'manager', 'staff', 'read_only', 'supplier_external', 'artist_external', 'client_external', 'youth_external'].map((role) => <option key={role} value={role}>{role.replace('_', ' ')}</option>)}
        </select>
      </label>
      <div className="flex items-end">
        <button className="h-10 w-full rounded-md bg-blue-600 px-4 text-sm font-bold text-white disabled:bg-slate-400" disabled={submitting} type="submit">{submitting ? 'Creating user' : 'Create user'}</button>
      </div>
    </form>
  );
}

function UserAccessList({ users }: { users: UserListItem[] }) {
  return (
    <div className="divide-y divide-slate-100 rounded-md border border-slate-200">
      {users.map((user) => (
        <div className="flex flex-col gap-3 p-3 md:flex-row md:items-center md:justify-between" key={user.id}>
          <div>
            <div className="text-sm font-bold text-slate-900"><RestrictedField value={user.full_name || user.email} /></div>
            <div className="mt-1 text-xs text-slate-500"><RestrictedField value={user.email} /></div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <RoleBadge role={user.user_type} />
            <ReadinessBadge value={user.is_active ? 'active' : 'inactive'} />
          </div>
        </div>
      ))}
    </div>
  );
}

function Info({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="rounded-md border border-slate-200 p-3">
      <dt className="text-xs font-bold uppercase tracking-normal text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-700"><RestrictedField value={value} /></dd>
    </div>
  );
}

function Placeholder({ label }: { label: string }) {
  return <div className="rounded-md border border-dashed border-slate-300 p-3 text-sm font-semibold text-slate-500">{label}</div>;
}

function Input({ label, value, type = 'text', onChange }: { label: string; value: string; type?: string; onChange: (value: string) => void }) {
  return (
    <label className="text-sm font-bold text-slate-800">
      {label}
      <input className="mt-2 h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950" onChange={(event) => onChange(event.target.value)} type={type} value={value} />
    </label>
  );
}


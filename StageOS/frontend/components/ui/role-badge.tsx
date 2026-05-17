import { StatusBadge } from './status-badge';
import type { UserRole } from '@/lib/api/types';

const roleLabels: Record<UserRole, string> = {
  internal_admin: 'Admin',
  executive: 'Executive',
  manager: 'Manager',
  staff: 'Staff',
  read_only: 'Read only',
  supplier_external: 'Supplier',
  artist_external: 'Artist',
  client_external: 'Client',
  youth_external: 'Youth',
  integration_service: 'Service',
};

export function RoleBadge({ role }: { role: UserRole }) {
  return <StatusBadge tone="info">{roleLabels[role] ?? role}</StatusBadge>;
}

'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { AuditEventDetailDrawer, AuditFilterBar, AuditTrailList, uniqueAuditValues, useFilteredAuditEvents } from '@/components/audit/audit-components';
import { PageHeader } from '@/components/ui/page-header';
import { ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { fetchAuditExport } from '@/lib/api/endpoints';
import type { AuditEventItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export default function AuditPage() {
  const { tokens } = useAuth();
  const [events, setEvents] = useState<AuditEventItem[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<AuditEventItem | null>(null);
  const [filters, setFilters] = useState({ action: 'all', targetType: 'all', from: '', to: '', actor: '' });
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    fetchAuditExport(tokens.access)
      .then((response) => {
        if (mounted) setEvents(response.results);
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
        else setError('Audit Trail could not be loaded.');
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access]);

  const filteredEvents = useFilteredAuditEvents(events, filters);

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader description="Review activity, changes and exportable audit records where your role permits access." eyebrow="Audit" title="Audit Trail" />
        {permissionDenied ? (
          <div>
            <PermissionDeniedState />
            <p className="mt-3 text-sm font-medium text-amber-900">You do not have permission to view the audit trail.</p>
          </div>
        ) : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading Audit Trail" /> : (
          <>
            <AuditFilterBar eventTypes={uniqueAuditValues(events, 'event_type')} onChange={setFilters} targetTypes={uniqueAuditValues(events, 'target_type')} value={filters} />
            <AuditTrailList events={filteredEvents} onSelect={setSelectedEvent} />
          </>
        )}
      </div>
      <AuditEventDetailDrawer event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </AppShell>
  );
}

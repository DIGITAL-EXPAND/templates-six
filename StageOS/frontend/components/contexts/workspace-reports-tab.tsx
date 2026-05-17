'use client';

import { useEffect, useState } from 'react';
import { AuditTrailReport, WorkspaceReadinessReport } from '@/components/reports/report-components';
import { ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { fetchAuditExport, fetchContextReadiness } from '@/lib/api/endpoints';
import type { AuditEventItem, ContextReadiness } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceReportsTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [readiness, setReadiness] = useState<ContextReadiness | null>(null);
  const [events, setEvents] = useState<AuditEventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([fetchContextReadiness(tokens.access, workspaceId), fetchAuditExport(tokens.access)])
      .then(([readinessResult, auditResult]) => {
        if (!mounted) return;
        if (readinessResult.status === 'fulfilled') setReadiness(readinessResult.value);
        else if (readinessResult.reason instanceof ApiError && readinessResult.reason.status === 403) setPermissionDenied(true);
        else setError('Workspace reports could not be loaded.');
        if (auditResult.status === 'fulfilled') setEvents(auditResult.value.results);
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access, workspaceId]);

  if (loading) return <LoadingState label="Loading Workspace reports" />;
  return <div className="space-y-4">{permissionDenied ? <PermissionDeniedState /> : null}{error ? <ErrorState message={error} /> : null}<WorkspaceReadinessReport readiness={readiness} /><AuditTrailReport events={events} /></div>;
}


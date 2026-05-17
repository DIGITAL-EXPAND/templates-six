'use client';

import { useEffect, useState } from 'react';
import { TicketingActionDialog, TicketingSetupList, type TicketingAction } from '@/components/ticketing/ticketing-components';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { fetchDocuments, fetchOperatingContexts, fetchSalesImports, fetchTicketingSetups, importTicketSales, setTicketingLive, settleTicketing } from '@/lib/api/endpoints';
import type { DocumentItem, OperatingContextListItem, SalesImportItem, TicketingSetupItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceTicketingTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [setups, setSetups] = useState<TicketingSetupItem[]>([]);
  const [imports, setImports] = useState<SalesImportItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [action, setAction] = useState<TicketingAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.all([fetchTicketingSetups(tokens.access, { operating_context: workspaceId }), fetchSalesImports(tokens.access), fetchDocuments(tokens.access), fetchOperatingContexts(tokens.access)])
      .then(([setupResponse, importResponse, documentResponse, workspaceResponse]) => {
        if (!mounted) return;
        const setupIds = new Set(setupResponse.results.map((setup) => setup.id));
        setSetups(setupResponse.results);
        setImports(importResponse.results.filter((item) => setupIds.has(item.ticketing_setup)));
        setDocuments(documentResponse.results.filter((item) => item.operating_context === workspaceId));
        setWorkspaces(workspaceResponse.results);
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('Ticketing could not be loaded for this Workspace.');
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access, workspaceId]);

  async function handleAction(values: { tickets: string; revenue: string; amount: string; notes: string; sourceFile: string }) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    try {
      if (action.kind === 'go-live') {
        const updated = await setTicketingLive(tokens.access, action.setup.id);
        setSetups((current) => current.map((setup) => setup.id === updated.id ? updated : setup));
      } else if (action.kind === 'import-sales') {
        const created = await importTicketSales(tokens.access, action.setup.id, { tickets_sold: Number(values.tickets || 0), revenue: values.revenue || '0', notes: values.notes, source_file: values.sourceFile || null });
        setImports((current) => [created, ...current]);
      } else {
        const updated = await settleTicketing(tokens.access, action.setup.id, values.amount || '0');
        setSetups((current) => current.map((setup) => setup.id === updated.id ? updated : setup));
      }
      setAction(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to perform this ticketing action.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Ticketing action could not be completed.');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingState label="Loading Workspace ticketing" />;
  return <div className="space-y-4">{permissionDenied ? <PermissionDeniedState /> : null}{error ? <ErrorState message={error} /> : null}{setups.length ? <TicketingSetupList imports={imports} onAction={setAction} setups={setups} workspaces={workspaces} /> : <EmptyState description="Ticketing setup linked to this Workspace will appear here." title="No ticketing setup yet" />}<TicketingActionDialog action={action} documents={documents} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} /></div>;
}


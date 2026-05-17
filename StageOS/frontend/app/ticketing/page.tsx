'use client';

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DepartmentExecutiveActionsPanel } from '@/components/governance/department-executive-actions-panel';
import { TicketingActionDialog, TicketingFilters, TicketingSetupList, type TicketingAction } from '@/components/ticketing/ticketing-components';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { fetchDocuments, fetchOperatingContexts, fetchSalesImports, fetchTicketingSetups, importTicketSales, setTicketingLive, settleTicketing } from '@/lib/api/endpoints';
import type { DocumentItem, OperatingContextListItem, SalesImportItem, TicketingSetupItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export default function TicketingPage() {
  const { tokens } = useAuth();
  const [setups, setSetups] = useState<TicketingSetupItem[]>([]);
  const [imports, setImports] = useState<SalesImportItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [filters, setFilters] = useState({ provider: 'all', setup: 'all', settlement: 'all', imported: 'all', workspace: 'all', missingLink: false, settlementPending: false });
  const [action, setAction] = useState<TicketingAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.all([fetchTicketingSetups(tokens.access), fetchSalesImports(tokens.access), fetchDocuments(tokens.access), fetchOperatingContexts(tokens.access)])
      .then(([setupResponse, importResponse, documentResponse, workspaceResponse]) => {
        if (!mounted) return;
        setSetups(setupResponse.results);
        setImports(importResponse.results);
        setDocuments(documentResponse.results);
        setWorkspaces(workspaceResponse.results);
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('Ticketing setups could not be loaded.');
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access]);

  const providers = useMemo(() => Array.from(new Set(setups.map((setup) => setup.provider))).sort(), [setups]);
  const filteredSetups = useMemo(() => setups.filter((setup) => {
    if (filters.provider !== 'all' && setup.provider !== filters.provider) return false;
    if (filters.setup !== 'all' && setup.setup_status !== filters.setup) return false;
    if (filters.settlement !== 'all' && setup.settlement_status !== filters.settlement) return false;
    if (filters.imported === 'imported' && !setup.sales_imported) return false;
    if (filters.imported === 'not_imported' && setup.sales_imported) return false;
    if (filters.workspace !== 'all' && setup.operating_context !== filters.workspace) return false;
    if (filters.missingLink && setup.booking_link) return false;
    if (filters.settlementPending && !['pending', 'in_progress'].includes(setup.settlement_status)) return false;
    return true;
  }), [filters, setups]);

  async function handleAction(values: { tickets: string; revenue: string; amount: string; notes: string; sourceFile: string }) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    setError('');
    try {
      if (action.kind === 'go-live') {
        const updated = await setTicketingLive(tokens.access, action.setup.id);
        setSetups((current) => current.map((setup) => setup.id === updated.id ? updated : setup));
      } else if (action.kind === 'import-sales') {
        const created = await importTicketSales(tokens.access, action.setup.id, { tickets_sold: Number(values.tickets || 0), revenue: values.revenue || '0', notes: values.notes, source_file: values.sourceFile || null });
        setImports((current) => [created, ...current]);
        setSetups((current) => current.map((setup) => setup.id === action.setup.id ? { ...setup, sales_imported: true, tickets_sold: setup.tickets_sold + created.tickets_sold } : setup));
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

  return <AppShell><div className="space-y-5"><PageHeader description="Track ticketing setup, sales imports, comps and settlement readiness." eyebrow="Ticketing" title="Ticketing" />{permissionDenied ? <PermissionDeniedState /> : null}{error ? <ErrorState message={error} /> : null}{loading ? <LoadingState label="Loading ticketing setups" /> : <><TicketingFilters onChange={setFilters} providers={providers} value={filters} workspaces={workspaces} /><DepartmentExecutiveActionsPanel departmentTypes={['ticketing']} targetTypes={['TicketingSetup', 'SalesImport']} />{filteredSetups.length ? <TicketingSetupList imports={imports} onAction={setAction} setups={filteredSetups} workspaces={workspaces} /> : <EmptyState description="Ticketing setups will appear here when records are available or filters are cleared." title="No ticketing setups found" />}</>}</div><TicketingActionDialog action={action} documents={documents} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} /></AppShell>;
}

'use client';

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DepartmentExecutiveActionsPanel } from '@/components/governance/department-executive-actions-panel';
import { SupplierActionDialog, type SupplierAction } from '@/components/suppliers/supplier-action-dialog';
import { SupplierDetailDrawer } from '@/components/suppliers/supplier-detail-drawer';
import { SupplierFilters, type SupplierFiltersValue } from '@/components/suppliers/supplier-filters';
import { supplierDocuments, supplierEngagements } from '@/components/suppliers/helpers';
import { SupplierList } from '@/components/suppliers/supplier-list';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  decideSupplierDocument,
  fetchOperatingContexts,
  fetchPaymentPacks,
  fetchSupplierDocuments,
  fetchSupplierEngagements,
  fetchSuppliers,
  sendPaymentPackToErp,
  suspendSupplier,
  verifySupplier,
} from '@/lib/api/endpoints';
import type { OperatingContextListItem, PaymentPackItem, SupplierDocumentItem, SupplierEngagementItem, SupplierItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export default function SuppliersPage() {
  const { tokens } = useAuth();
  const [suppliers, setSuppliers] = useState<SupplierItem[]>([]);
  const [documents, setDocuments] = useState<SupplierDocumentItem[]>([]);
  const [engagements, setEngagements] = useState<SupplierEngagementItem[]>([]);
  const [packs, setPacks] = useState<PaymentPackItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierItem | null>(null);
  const [action, setAction] = useState<SupplierAction | null>(null);
  const [filters, setFilters] = useState<SupplierFiltersValue>({ status: 'all', category: 'all', csd: 'all', documents: 'all', workspace: 'all', search: '' });
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [sendingPackId, setSendingPackId] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([fetchSuppliers(tokens.access), fetchSupplierDocuments(tokens.access), fetchSupplierEngagements(tokens.access), fetchPaymentPacks(tokens.access), fetchOperatingContexts(tokens.access)])
      .then(([supplierResult, documentResult, engagementResult, packResult, workspaceResult]) => {
        if (!mounted) return;
        if (supplierResult.status === 'fulfilled') setSuppliers(supplierResult.value.results);
        else if (supplierResult.reason instanceof ApiError && supplierResult.reason.status === 403) setPermissionDenied(true);
        else setError('Suppliers could not be loaded.');
        if (documentResult.status === 'fulfilled') setDocuments(documentResult.value.results);
        if (engagementResult.status === 'fulfilled') setEngagements(engagementResult.value.results);
        if (packResult.status === 'fulfilled') setPacks(packResult.value.results);
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  const categories = useMemo(() => Array.from(new Set(suppliers.map((supplier) => supplier.category).filter(Boolean))).sort(), [suppliers]);
  const filteredSuppliers = useMemo(() => suppliers.filter((supplier) => {
    const docs = supplierDocuments(documents, supplier.id);
    const engs = supplierEngagements(engagements, supplier.id);
    const query = filters.search.trim().toLowerCase();
    if (filters.status !== 'all' && supplier.status !== filters.status) return false;
    if (filters.category !== 'all' && supplier.category !== filters.category) return false;
    if (filters.csd === 'verified' && !supplier.csd_verified) return false;
    if (filters.csd === 'not_verified' && supplier.csd_verified) return false;
    if (filters.documents === 'ready' && docs.some((doc) => doc.status !== 'verified')) return false;
    if (filters.documents === 'not_ready' && docs.every((doc) => doc.status === 'verified')) return false;
    if (filters.workspace !== 'all' && !engs.some((engagement) => engagement.operating_context === filters.workspace)) return false;
    if (query && !`${supplier.name} ${supplier.category} ${supplier.csd_number}`.toLowerCase().includes(query)) return false;
    return true;
  }), [documents, engagements, filters, suppliers]);

  async function handleAction(comment: string) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    setError('');
    try {
      if (action.kind === 'verify_supplier') {
        const updated = await verifySupplier(tokens.access, action.supplier.id);
        setSuppliers((current) => current.map((supplier) => (supplier.id === updated.id ? updated : supplier)));
        setSelectedSupplier((current) => (current?.id === updated.id ? updated : current));
      } else if (action.kind === 'suspend_supplier') {
        const updated = await suspendSupplier(tokens.access, action.supplier.id, comment);
        setSuppliers((current) => current.map((supplier) => (supplier.id === updated.id ? updated : supplier)));
        setSelectedSupplier((current) => (current?.id === updated.id ? updated : current));
      } else {
        const updated = await decideSupplierDocument(tokens.access, action.document.id, action.kind === 'verify_document' ? 'verify' : 'reject', comment);
        setDocuments((current) => current.map((document) => (document.id === updated.id ? updated : document)));
      }
      setAction(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to perform this supplier action.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Supplier action could not be completed.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSendPack(pack: PaymentPackItem) {
    if (!tokens?.access) return;
    setSendingPackId(pack.id);
    setError('');
    try {
      const updated = await sendPaymentPackToErp(tokens.access, pack.id);
      setPacks((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to perform this supplier action.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Payment pack could not be sent to ERP.');
    } finally {
      setSendingPackId('');
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader description="Manage supplier readiness, CSD verification, documents, engagements and payment packs." eyebrow="Suppliers" title="Suppliers" />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading suppliers" /> : (
          <>
            <SupplierFilters categories={categories} onChange={setFilters} value={filters} workspaces={workspaces} />
            <DepartmentExecutiveActionsPanel departmentTypes={['finance']} targetTypes={['Supplier', 'SupplierEngagement', 'SupplierDocument', 'PaymentPack']} title="Executive actions for Suppliers / SCM" />
            {filteredSuppliers.length ? <SupplierList documents={documents} engagements={engagements} onSelect={setSelectedSupplier} packs={packs} suppliers={filteredSuppliers} workspaces={workspaces} /> : <EmptyState description="Suppliers will appear here when records are available or filters are cleared." title="No suppliers found" />}
          </>
        )}
      </div>
      <SupplierDetailDrawer documents={documents} engagements={engagements} onAction={setAction} onClose={() => setSelectedSupplier(null)} onSendPack={handleSendPack} packs={packs} sendingPackId={sendingPackId} supplier={selectedSupplier} workspaces={workspaces} />
      <SupplierActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </AppShell>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { SupplierActionDialog, type SupplierAction } from '@/components/suppliers/supplier-action-dialog';
import { SupplierDetailDrawer } from '@/components/suppliers/supplier-detail-drawer';
import { SupplierList } from '@/components/suppliers/supplier-list';
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

export function WorkspaceSuppliersTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [suppliers, setSuppliers] = useState<SupplierItem[]>([]);
  const [documents, setDocuments] = useState<SupplierDocumentItem[]>([]);
  const [engagements, setEngagements] = useState<SupplierEngagementItem[]>([]);
  const [packs, setPacks] = useState<PaymentPackItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierItem | null>(null);
  const [action, setAction] = useState<SupplierAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [sendingPackId, setSendingPackId] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([fetchSupplierEngagements(tokens.access, { operating_context: workspaceId }), fetchSuppliers(tokens.access), fetchSupplierDocuments(tokens.access), fetchPaymentPacks(tokens.access, { operating_context: workspaceId }), fetchOperatingContexts(tokens.access)])
      .then(([engagementResult, supplierResult, documentResult, packResult, workspaceResult]) => {
        if (!mounted) return;
        if (engagementResult.status === 'fulfilled') setEngagements(engagementResult.value.results);
        else if (engagementResult.reason instanceof ApiError && engagementResult.reason.status === 403) setPermissionDenied(true);
        else setError('Suppliers could not be loaded for this Workspace.');
        if (supplierResult.status === 'fulfilled' && engagementResult.status === 'fulfilled') {
          const supplierIds = new Set(engagementResult.value.results.map((engagement) => engagement.supplier));
          setSuppliers(supplierResult.value.results.filter((supplier) => supplierIds.has(supplier.id)));
        }
        if (documentResult.status === 'fulfilled') setDocuments(documentResult.value.results);
        if (packResult.status === 'fulfilled') setPacks(packResult.value.results);
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access, workspaceId]);

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
    try {
      const updated = await sendPaymentPackToErp(tokens.access, pack.id);
      setPacks((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } finally {
      setSendingPackId('');
    }
  }

  if (loading) return <LoadingState label="Loading Workspace suppliers" />;

  return (
    <div className="space-y-4">
      {permissionDenied ? <PermissionDeniedState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {suppliers.length ? <SupplierList documents={documents} engagements={engagements} onSelect={setSelectedSupplier} packs={packs} suppliers={suppliers} workspaces={workspaces} /> : <EmptyState description="Suppliers linked to this Workspace will appear here." title="No suppliers yet" />}
      <SupplierDetailDrawer documents={documents} engagements={engagements} onAction={setAction} onClose={() => setSelectedSupplier(null)} onSendPack={handleSendPack} packs={packs} sendingPackId={sendingPackId} supplier={selectedSupplier} workspaces={workspaces} />
      <SupplierActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </div>
  );
}


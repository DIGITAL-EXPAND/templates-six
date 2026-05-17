'use client';

import { X } from 'lucide-react';
import { BlockerAlert, labelFromValue, money, ReadinessBadge, RestrictedField } from '@/components/readiness/shared';
import type { OperatingContextListItem, PaymentPackItem, SupplierDocumentItem, SupplierEngagementItem, SupplierItem } from '@/lib/api/types';
import type { SupplierAction } from './supplier-action-dialog';
import { supplierBlockers, supplierDocuments, supplierEngagements, supplierPaymentPacks } from './helpers';

function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  return workspaces.find((workspace) => workspace.id === id)?.title ?? 'Workspace unavailable';
}

export function SupplierDetailDrawer({
  supplier,
  documents,
  engagements,
  packs,
  workspaces,
  sendingPackId,
  onAction,
  onClose,
  onSendPack,
}: {
  supplier: SupplierItem | null;
  documents: SupplierDocumentItem[];
  engagements: SupplierEngagementItem[];
  packs: PaymentPackItem[];
  workspaces: OperatingContextListItem[];
  sendingPackId: string;
  onAction: (action: SupplierAction) => void;
  onClose: () => void;
  onSendPack: (pack: PaymentPackItem) => void;
}) {
  if (!supplier) return null;
  const supplierDocs = supplierDocuments(documents, supplier.id);
  const supplierEngs = supplierEngagements(engagements, supplier.id);
  const supplierPacks = supplierPaymentPacks(packs, supplierEngs);

  return (
    <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-2xl overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-blue-700">Supplier detail</p>
          <h2 className="mt-1 text-xl font-bold text-slate-950">{supplier.name}</h2>
          <p className="mt-1 text-sm text-slate-500">{supplier.category || 'No category'} · {supplier.panel || 'No panel'}</p>
        </div>
        <button aria-label="Close supplier detail" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700" onClick={onClose} type="button"><X className="h-4 w-4" /></button>
      </div>
      <div className="mt-5 space-y-5">
        <div className="flex flex-wrap gap-2"><ReadinessBadge value={supplier.status} /><ReadinessBadge value={supplier.csd_verified ? 'verified' : 'pending_verification'} /></div>
        <BlockerAlert blockers={supplierBlockers(supplier, supplierDocs, supplierPacks)} />
        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Profile</h3>
          <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
            <div><dt className="font-bold text-slate-700">CSD number</dt><dd className="mt-1 text-slate-600"><RestrictedField value={supplier.csd_number} /></dd></div>
            <div><dt className="font-bold text-slate-700">B-BBEE level</dt><dd className="mt-1 text-slate-600">{supplier.bee_level ? labelFromValue(supplier.bee_level) : 'Not provided'}</dd></div>
            <div><dt className="font-bold text-slate-700">Contact person</dt><dd className="mt-1 text-slate-600"><RestrictedField value={supplier.contact_name} /></dd></div>
            <div><dt className="font-bold text-slate-700">Contact email</dt><dd className="mt-1 text-slate-600"><RestrictedField value={supplier.contact_email} /></dd></div>
          </dl>
          {supplier.notes ? <p className="mt-3 text-sm leading-6 text-slate-600">{supplier.notes}</p> : null}
          <div className="mt-4 flex flex-wrap gap-2">
            <button className="h-9 rounded-md bg-blue-600 px-3 text-sm font-bold text-white hover:bg-blue-700" onClick={() => onAction({ kind: 'verify_supplier', supplier })} type="button">Verify CSD</button>
            <button className="h-9 rounded-md border border-rose-200 px-3 text-sm font-bold text-rose-700 hover:bg-rose-50" onClick={() => onAction({ kind: 'suspend_supplier', supplier })} type="button">Suspend supplier</button>
          </div>
        </section>
        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Document checklist</h3>
          <div className="mt-3 divide-y divide-slate-100 rounded-md border border-slate-200">
            {supplierDocs.length ? supplierDocs.map((document) => (
              <div className="flex flex-col gap-3 p-3 md:flex-row md:items-center md:justify-between" key={document.id}>
                <div><div className="text-sm font-bold text-slate-900">{labelFromValue(document.document_type)}</div><div className="mt-1 text-xs text-slate-500">{document.file_name || 'No file linked'}</div></div>
                <div className="flex flex-wrap items-center gap-2"><ReadinessBadge value={document.status} /><button className="h-8 rounded-md border border-slate-200 px-2 text-xs font-bold text-slate-700" onClick={() => onAction({ kind: 'verify_document', document })} type="button">Verify</button><button className="h-8 rounded-md border border-rose-200 px-2 text-xs font-bold text-rose-700" onClick={() => onAction({ kind: 'reject_document', document })} type="button">Reject</button></div>
              </div>
            )) : <div className="p-3 text-sm text-slate-500">No supplier documents returned.</div>}
          </div>
        </section>
        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Workspace engagements</h3>
          <div className="mt-3 grid gap-3">
            {supplierEngs.length ? supplierEngs.map((engagement) => <div className="rounded-md border border-slate-200 p-3" key={engagement.id}><div className="text-sm font-bold text-slate-900">{workspaceName(workspaces, engagement.operating_context)}</div><div className="mt-1 text-xs text-slate-500">{engagement.role} · {money(engagement.value)}</div><div className="mt-2"><ReadinessBadge value={engagement.status} /></div></div>) : <div className="text-sm text-slate-500">No linked Workspace engagements returned.</div>}
          </div>
        </section>
        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Payment readiness</h3>
          <div className="mt-3 grid gap-3">
            {supplierPacks.length ? supplierPacks.map((pack) => <div className="flex flex-col gap-3 rounded-md border border-slate-200 p-3 md:flex-row md:items-center md:justify-between" key={pack.id}><div><div className="text-sm font-bold text-slate-900">{money(pack.amount)}</div><div className="mt-1 text-xs text-slate-500">{pack.erp_reference || 'No ERP reference yet'}</div></div><div className="flex flex-wrap items-center gap-2"><ReadinessBadge value={pack.status} /><button className="h-8 rounded-md border border-slate-200 px-2 text-xs font-bold text-slate-700 disabled:text-slate-400" disabled={sendingPackId === pack.id} onClick={() => onSendPack(pack)} type="button">{sendingPackId === pack.id ? 'Sending' : 'Send to ERP'}</button></div></div>) : <div className="text-sm text-slate-500">No payment packs returned or access is restricted.</div>}
          </div>
        </section>
      </div>
    </aside>
  );
}


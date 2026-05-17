import { BlockerAlert, labelFromValue, money, ReadinessBadge, RestrictedField } from '@/components/readiness/shared';
import type { OperatingContextListItem, PaymentPackItem, SupplierDocumentItem, SupplierEngagementItem, SupplierItem } from '@/lib/api/types';
import { supplierBlockers, supplierDocuments, supplierEngagements, supplierPaymentPacks } from './helpers';

function workspaceNames(engagements: SupplierEngagementItem[], workspaces: OperatingContextListItem[]) {
  return engagements.map((engagement) => workspaces.find((workspace) => workspace.id === engagement.operating_context)?.title ?? 'Workspace unavailable').join(', ') || 'No linked Workspace';
}

export function SupplierCard({
  supplier,
  documents,
  engagements,
  packs,
  workspaces,
  onSelect,
}: {
  supplier: SupplierItem;
  documents: SupplierDocumentItem[];
  engagements: SupplierEngagementItem[];
  packs: PaymentPackItem[];
  workspaces: OperatingContextListItem[];
  onSelect: (supplier: SupplierItem) => void;
}) {
  const supplierDocs = supplierDocuments(documents, supplier.id);
  const supplierEngs = supplierEngagements(engagements, supplier.id);
  const supplierPacks = supplierPaymentPacks(packs, supplierEngs);
  const blockers = supplierBlockers(supplier, supplierDocs, supplierPacks);
  const totalValue = supplierEngs.reduce((sum, engagement) => sum + Number(engagement.value || 0), 0);

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-950">{supplier.name}</h2>
          <p className="mt-1 text-sm text-slate-500">{supplier.category || 'No category'} · {supplier.panel || 'No panel'}</p>
        </div>
        <ReadinessBadge value={supplier.status} />
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-3">
        <div><dt className="font-bold text-slate-700">CSD number</dt><dd className="mt-1 text-slate-600"><RestrictedField value={supplier.csd_number} /></dd></div>
        <div><dt className="font-bold text-slate-700">CSD readiness</dt><dd className="mt-1 text-slate-600">{supplier.csd_verified ? 'Verified' : 'Not verified'}</dd></div>
        <div><dt className="font-bold text-slate-700">B-BBEE level</dt><dd className="mt-1 text-slate-600">{supplier.bee_level ? labelFromValue(supplier.bee_level) : 'Not provided'}</dd></div>
        <div><dt className="font-bold text-slate-700">Contact person</dt><dd className="mt-1 text-slate-600"><RestrictedField value={supplier.contact_name} /></dd></div>
        <div><dt className="font-bold text-slate-700">Contact email</dt><dd className="mt-1 text-slate-600"><RestrictedField value={supplier.contact_email} /></dd></div>
        <div><dt className="font-bold text-slate-700">Engagement value</dt><dd className="mt-1 text-slate-600">{money(String(totalValue))}</dd></div>
      </dl>
      <p className="mt-3 text-sm text-slate-500">{workspaceNames(supplierEngs, workspaces)}</p>
      <div className="mt-4"><BlockerAlert blockers={blockers} /></div>
      <button className="mt-4 h-10 rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700" onClick={() => onSelect(supplier)} type="button">
        View supplier
      </button>
    </article>
  );
}


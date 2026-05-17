import type { OperatingContextListItem, SupplierStatus } from '@/lib/api/types';
import { labelFromValue } from '@/components/readiness/shared';

export type SupplierFiltersValue = {
  status: 'all' | SupplierStatus;
  category: string;
  csd: 'all' | 'verified' | 'not_verified';
  documents: 'all' | 'ready' | 'not_ready';
  workspace: string;
  search: string;
};

const statuses: SupplierStatus[] = ['documents_incomplete', 'pending_verification', 'ready', 'suspended', 'blacklisted'];

export function SupplierFilters({
  categories,
  value,
  workspaces,
  onChange,
}: {
  categories: string[];
  value: SupplierFiltersValue;
  workspaces: OperatingContextListItem[];
  onChange: (value: SupplierFiltersValue) => void;
}) {
  return (
    <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 md:grid-cols-3 xl:grid-cols-6">
      <input
        aria-label="Search suppliers"
        className="h-10 rounded-md border border-slate-200 px-3 text-sm text-slate-950"
        onChange={(event) => onChange({ ...value, search: event.target.value })}
        placeholder="Search supplier, category, CSD"
        value={value.search}
      />
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, status: event.target.value as SupplierFiltersValue['status'] })} value={value.status}>
        <option value="all">All statuses</option>
        {statuses.map((status) => <option key={status} value={status}>{labelFromValue(status)}</option>)}
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, category: event.target.value })} value={value.category}>
        <option value="all">All categories</option>
        {categories.map((category) => <option key={category} value={category}>{category}</option>)}
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, csd: event.target.value as SupplierFiltersValue['csd'] })} value={value.csd}>
        <option value="all">All CSD</option>
        <option value="verified">CSD verified</option>
        <option value="not_verified">CSD not verified</option>
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, documents: event.target.value as SupplierFiltersValue['documents'] })} value={value.documents}>
        <option value="all">All documents</option>
        <option value="ready">Documents ready</option>
        <option value="not_ready">Documents not ready</option>
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, workspace: event.target.value })} value={value.workspace}>
        <option value="all">All Workspaces</option>
        {workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.title}</option>)}
      </select>
    </section>
  );
}


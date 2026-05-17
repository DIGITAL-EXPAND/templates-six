import { labelFromValue } from '@/components/readiness/shared';
import type { ArtistStatus, OperatingContextListItem } from '@/lib/api/types';

export type ArtistFiltersValue = {
  status: 'all' | ArtistStatus;
  discipline: string;
  contractReady: boolean;
  paymentReady: boolean;
  workspace: string;
  search: string;
};

const statuses: ArtistStatus[] = ['documents_incomplete', 'contract_ready', 'contracted', 'payment_ready'];

export function ArtistFilters({
  disciplines,
  value,
  workspaces,
  onChange,
}: {
  disciplines: string[];
  value: ArtistFiltersValue;
  workspaces: OperatingContextListItem[];
  onChange: (value: ArtistFiltersValue) => void;
}) {
  return (
    <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 md:grid-cols-3 xl:grid-cols-6">
      <input aria-label="Search artists" className="h-10 rounded-md border border-slate-200 px-3 text-sm text-slate-950" onChange={(event) => onChange({ ...value, search: event.target.value })} placeholder="Search name or discipline" value={value.search} />
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, status: event.target.value as ArtistFiltersValue['status'] })} value={value.status}>
        <option value="all">All statuses</option>
        {statuses.map((status) => <option key={status} value={status}>{labelFromValue(status)}</option>)}
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, discipline: event.target.value })} value={value.discipline}>
        <option value="all">All disciplines</option>
        {disciplines.map((discipline) => <option key={discipline} value={discipline}>{discipline}</option>)}
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, workspace: event.target.value })} value={value.workspace}>
        <option value="all">All Workspaces</option>
        {workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.title}</option>)}
      </select>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.contractReady} onChange={(event) => onChange({ ...value, contractReady: event.target.checked })} type="checkbox" />Contract ready</label>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.paymentReady} onChange={(event) => onChange({ ...value, paymentReady: event.target.checked })} type="checkbox" />Payment ready</label>
    </section>
  );
}


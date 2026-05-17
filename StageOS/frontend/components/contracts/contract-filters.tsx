import type { ContractStatus, OperatingContextListItem } from '@/lib/api/types';
import { friendlyContractType } from './helpers';

export type ContractFiltersValue = {
  status: 'all' | ContractStatus;
  contractType: string;
  workspace: string;
  pendingSignature: boolean;
  expiry: 'all' | 'expired' | 'expiring_soon';
  search: string;
};

const statuses: ContractStatus[] = [
  'draft',
  'legal_review',
  'finance_review',
  'scm_review',
  'issued',
  'counter_signed',
  'signed',
  'expired',
  'cancelled',
];

export function ContractFilters({
  contractTypes,
  value,
  workspaces,
  onChange,
}: {
  contractTypes: string[];
  value: ContractFiltersValue;
  workspaces: OperatingContextListItem[];
  onChange: (value: ContractFiltersValue) => void;
}) {
  return (
    <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 md:grid-cols-3 xl:grid-cols-6">
      <input
        aria-label="Search by counterparty"
        className="h-10 rounded-md border border-slate-200 px-3 text-sm text-slate-950"
        onChange={(event) => onChange({ ...value, search: event.target.value })}
        placeholder="Search counterparty"
        value={value.search}
      />
      <select
        aria-label="Filter by contract status"
        className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
        onChange={(event) => onChange({ ...value, status: event.target.value as ContractFiltersValue['status'] })}
        value={value.status}
      >
        <option value="all">All statuses</option>
        {statuses.map((status) => (
          <option key={status} value={status}>
            {friendlyContractType(status)}
          </option>
        ))}
      </select>
      <select
        aria-label="Filter by contract type"
        className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
        onChange={(event) => onChange({ ...value, contractType: event.target.value })}
        value={value.contractType}
      >
        <option value="all">All types</option>
        {contractTypes.map((contractType) => (
          <option key={contractType} value={contractType}>
            {friendlyContractType(contractType)}
          </option>
        ))}
      </select>
      <select
        aria-label="Filter by Workspace"
        className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
        onChange={(event) => onChange({ ...value, workspace: event.target.value })}
        value={value.workspace}
      >
        <option value="all">All Workspaces</option>
        {workspaces.map((workspace) => (
          <option key={workspace.id} value={workspace.id}>
            {workspace.title}
          </option>
        ))}
      </select>
      <select
        aria-label="Filter by expiry"
        className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
        onChange={(event) => onChange({ ...value, expiry: event.target.value as ContractFiltersValue['expiry'] })}
        value={value.expiry}
      >
        <option value="all">All dates</option>
        <option value="expired">Expired</option>
        <option value="expiring_soon">Expiring soon</option>
      </select>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700">
        <input
          checked={value.pendingSignature}
          onChange={(event) => onChange({ ...value, pendingSignature: event.target.checked })}
          type="checkbox"
        />
        Pending signature
      </label>
    </section>
  );
}


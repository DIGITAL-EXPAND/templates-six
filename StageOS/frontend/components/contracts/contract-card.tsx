import type {
  ContractRecordItem,
  DocumentItem,
  OperatingContextListItem,
  SignatureRecordItem,
} from '@/lib/api/types';
import { ContractBlockerAlert } from './contract-blocker-alert';
import { ContractStatusBadge } from './contract-status-badge';
import {
  contractSignatures,
  documentTitle,
  formatDate,
  friendlyContractType,
  money,
  workspaceName,
} from './helpers';
import { SignatureProgress } from './signature-progress';

export function ContractCard({
  contract,
  documents,
  now,
  signatures,
  workspaces,
  onSelect,
}: {
  contract: ContractRecordItem;
  documents: DocumentItem[];
  now: number;
  signatures: SignatureRecordItem[];
  workspaces: OperatingContextListItem[];
  onSelect: (contract: ContractRecordItem) => void;
}) {
  const contractSigners = contractSignatures(signatures, contract.id);
  const pendingSigners = contractSigners.filter((signature) => !signature.is_signed).length;

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-950">{contract.counterparty_name}</h2>
          <p className="mt-1 text-sm text-slate-500">
            {friendlyContractType(contract.contract_type)} · {workspaceName(workspaces, contract.operating_context)}
          </p>
        </div>
        <ContractStatusBadge status={contract.status} />
      </div>

      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-3">
        <div>
          <dt className="font-bold text-slate-700">Value</dt>
          <dd className="mt-1 text-slate-600">{money(contract)}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Issued</dt>
          <dd className="mt-1 text-slate-600">{formatDate(contract.issued_date)}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Expiry</dt>
          <dd className="mt-1 text-slate-600">{formatDate(contract.expiry_date)}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Signatures required</dt>
          <dd className="mt-1 text-slate-600">{contract.signatures_required}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Signatures received</dt>
          <dd className="mt-1 text-slate-600">{contract.signatures_received}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Signed document</dt>
          <dd className="mt-1 text-slate-600">{documentTitle(documents, contract.signed_document)}</dd>
        </div>
      </dl>

      <div className="mt-4">
        <SignatureProgress contract={contract} />
      </div>
      {pendingSigners ? (
        <p className="mt-2 text-xs font-semibold text-amber-700">{pendingSigners} signature action pending.</p>
      ) : null}
      <div className="mt-4">
        <ContractBlockerAlert contract={contract} now={now} />
      </div>
      <button
        className="mt-4 h-10 rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700"
        onClick={() => onSelect(contract)}
        type="button"
      >
        View contract
      </button>
    </article>
  );
}


'use client';

import { X } from 'lucide-react';
import type {
  ContractRecordItem,
  DocumentItem,
  OperatingContextListItem,
  SignatureRecordItem,
} from '@/lib/api/types';
import type { ContractAction } from './contract-action-dialog';
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
import { SignatureList } from './signature-list';
import { SignatureProgress } from './signature-progress';

export function ContractDetailDrawer({
  contract,
  documents,
  now,
  signatures,
  signingId,
  workspaces,
  onAction,
  onClose,
  onSign,
}: {
  contract: ContractRecordItem | null;
  documents: DocumentItem[];
  now: number;
  signatures: SignatureRecordItem[];
  signingId: string;
  workspaces: OperatingContextListItem[];
  onAction: (action: ContractAction, contract: ContractRecordItem) => void;
  onClose: () => void;
  onSign: (signature: SignatureRecordItem) => void;
}) {
  if (!contract) {
    return null;
  }

  const contractSigners = contractSignatures(signatures, contract.id);

  return (
    <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-2xl overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-blue-700">Contract detail</p>
          <h2 className="mt-1 text-xl font-bold text-slate-950">{contract.counterparty_name}</h2>
          <p className="mt-1 text-sm text-slate-500">
            {friendlyContractType(contract.contract_type)} · {workspaceName(workspaces, contract.operating_context)}
          </p>
        </div>
        <button
          aria-label="Close contract detail"
          className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700"
          onClick={onClose}
          type="button"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-5 space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <ContractStatusBadge status={contract.status} />
          <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-semibold text-slate-600">
            {money(contract)}
          </span>
        </div>

        <ContractBlockerAlert contract={contract} now={now} />

        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Summary</h3>
          <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
            <div>
              <dt className="font-bold text-slate-700">Counterparty</dt>
              <dd className="mt-1 text-slate-600">{contract.counterparty_name}</dd>
            </div>
            <div>
              <dt className="font-bold text-slate-700">Counterparty type</dt>
              <dd className="mt-1 text-slate-600">{friendlyContractType(contract.counterparty_type)}</dd>
            </div>
            <div>
              <dt className="font-bold text-slate-700">Issued date</dt>
              <dd className="mt-1 text-slate-600">{formatDate(contract.issued_date)}</dd>
            </div>
            <div>
              <dt className="font-bold text-slate-700">Effective date</dt>
              <dd className="mt-1 text-slate-600">{formatDate(contract.effective_date)}</dd>
            </div>
            <div>
              <dt className="font-bold text-slate-700">Expiry date</dt>
              <dd className="mt-1 text-slate-600">{formatDate(contract.expiry_date)}</dd>
            </div>
            <div>
              <dt className="font-bold text-slate-700">Signed document</dt>
              <dd className="mt-1 text-slate-600">{documentTitle(documents, contract.signed_document)}</dd>
            </div>
          </dl>
          {contract.notes ? <p className="mt-3 text-sm leading-6 text-slate-600">{contract.notes}</p> : null}
        </section>

        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Signature route</h3>
          <div className="mt-3">
            <SignatureProgress contract={contract} />
          </div>
          <div className="mt-4">
            <SignatureList onSign={onSign} signatures={contractSigners} signingId={signingId} />
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Next action</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              className="h-9 rounded-md bg-blue-600 px-3 text-sm font-bold text-white hover:bg-blue-700"
              onClick={() => onAction('issue', contract)}
              type="button"
            >
              Issue contract
            </button>
            <button
              className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700 hover:bg-slate-50"
              onClick={() => onAction('review', contract)}
              type="button"
            >
              Submit for review
            </button>
            <button
              className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700 hover:bg-slate-50"
              onClick={() => onAction('lock', contract)}
              type="button"
            >
              Lock final
            </button>
            <button
              className="h-9 rounded-md border border-rose-200 px-3 text-sm font-bold text-rose-700 hover:bg-rose-50"
              onClick={() => onAction('cancel', contract)}
              type="button"
            >
              Cancel contract
            </button>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Last activity</h3>
          <p className="mt-2 text-sm text-slate-600">Updated {formatDate(contract.updated_at)}.</p>
        </section>
      </div>
    </aside>
  );
}


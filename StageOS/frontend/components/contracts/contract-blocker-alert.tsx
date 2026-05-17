import type { ContractRecordItem } from '@/lib/api/types';
import { formatDate, isPendingSignature } from './helpers';

export function ContractBlockerAlert({ contract, now }: { contract: ContractRecordItem; now: number }) {
  const blockers: string[] = [];

  if (isPendingSignature(contract)) {
    blockers.push('Signatures are still outstanding.');
  }
  if (contract.status.endsWith('_review')) {
    blockers.push('Review is still in progress.');
  }
  if (!contract.signed_document && contract.status === 'signed') {
    blockers.push('Final signed document is not linked.');
  }
  if (contract.expiry_date && new Date(contract.expiry_date).getTime() < now) {
    blockers.push(`This contract expired on ${formatDate(contract.expiry_date)}.`);
  }

  if (!blockers.length) {
    return null;
  }

  return (
    <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">
      <div className="font-bold">Contract not ready</div>
      <ul className="mt-2 list-disc space-y-1 pl-5">
        {blockers.map((blocker) => (
          <li key={blocker}>{blocker}</li>
        ))}
      </ul>
    </div>
  );
}


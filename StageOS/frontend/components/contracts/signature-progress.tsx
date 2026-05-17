import type { ContractRecordItem } from '@/lib/api/types';

export function SignatureProgress({ contract }: { contract: ContractRecordItem }) {
  const total = Math.max(contract.signatures_required, 1);
  const received = Math.min(contract.signatures_received, total);
  const percent = Math.round((received / total) * 100);

  return (
    <div>
      <div className="flex items-center justify-between gap-3 text-xs font-bold text-slate-600">
        <span>Signature progress</span>
        <span>
          {contract.signatures_received}/{contract.signatures_required}
        </span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-slate-100">
        <div className="h-2 rounded-full bg-blue-600" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}


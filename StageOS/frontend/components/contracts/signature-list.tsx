import type { SignatureRecordItem } from '@/lib/api/types';
import { formatDate } from './helpers';

export function SignatureList({
  signatures,
  signingId,
  onSign,
}: {
  signatures: SignatureRecordItem[];
  signingId: string;
  onSign: (signature: SignatureRecordItem) => void;
}) {
  if (!signatures.length) {
    return <div className="rounded-md bg-slate-50 p-3 text-sm text-slate-500">No signature route returned.</div>;
  }

  return (
    <div className="divide-y divide-slate-100 rounded-md border border-slate-200">
      {signatures.map((signature) => (
        <div className="flex flex-col gap-3 p-3 md:flex-row md:items-center md:justify-between" key={signature.id}>
          <div>
            <div className="text-sm font-bold text-slate-900">{signature.signatory_name}</div>
            <div className="mt-1 text-xs text-slate-500">
              {signature.signatory_role} · {signature.signature_type} · {signature.is_signed ? formatDate(signature.signed_at) : 'Pending'}
            </div>
          </div>
          <button
            className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
            disabled={signature.is_signed || signingId === signature.id}
            onClick={() => onSign(signature)}
            type="button"
          >
            {signingId === signature.id ? 'Recording' : signature.is_signed ? 'Signed' : 'Record signature'}
          </button>
        </div>
      ))}
    </div>
  );
}


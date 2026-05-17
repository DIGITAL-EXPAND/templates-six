import { FileCheck2 } from 'lucide-react';

export function EvidenceReviewPanel({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-600">
      <FileCheck2 className="h-4 w-4 text-slate-400" />
      <span>{label}</span>
    </div>
  );
}

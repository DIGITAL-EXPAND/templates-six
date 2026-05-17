'use client';

import { FormEvent, useState } from 'react';
import { X } from 'lucide-react';
import type { ApprovalRequestItem, DocumentItem } from '@/lib/api/types';

export type ApprovalAction = 'approve' | 'reject' | 'request-changes' | 'request-more-information' | 'escalate' | 'exception-approve';

export function ApprovalDecisionDialog({
  approval,
  documents,
  submitting,
  onClose,
  onSubmit,
}: {
  approval: ApprovalRequestItem | null;
  documents: DocumentItem[];
  submitting: boolean;
  onClose: () => void;
  onSubmit: (action: ApprovalAction, values: { comment: string; evidence: string }) => void;
}) {
  const [comment, setComment] = useState('');
  const [evidence, setEvidence] = useState('');
  const [action, setAction] = useState<ApprovalAction>('approve');

  if (!approval) {
    return null;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(action, { comment, evidence });
  }

  return (
    <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-lg overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-blue-700">Approval decision</p>
          <h2 className="mt-1 text-xl font-bold text-slate-950">Review request</h2>
        </div>
        <button
          aria-label="Close approval decision"
          className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700"
          onClick={onClose}
          type="button"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="approval-action">
            Decision
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            id="approval-action"
            onChange={(event) => setAction(event.target.value as ApprovalAction)}
            value={action}
          >
            <option value="approve">Approve</option>
            <option value="reject">Reject</option>
            <option value="request-changes">Request changes</option>
            <option value="request-more-information">Request more information</option>
            <option value="escalate">Escalate</option>
            <option value="exception-approve">Exception / override approve</option>
          </select>
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="approval-evidence">
            Evidence reviewed
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            id="approval-evidence"
            onChange={(event) => setEvidence(event.target.value)}
            value={evidence}
          >
            <option value="">No evidence selected</option>
            {documents
              .filter((document) => document.operating_context === approval.operating_context)
              .map((document) => (
                <option key={document.id} value={document.id}>
                  {document.title}
                </option>
              ))}
          </select>
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="approval-comment">
            Decision comment
          </label>
          <textarea
            className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950"
            id="approval-comment"
            onChange={(event) => setComment(event.target.value)}
            value={comment}
          />
        </div>
        <button
          className="inline-flex h-10 w-full items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          disabled={submitting}
          type="submit"
        >
          {submitting ? 'Submitting decision' : 'Submit decision'}
        </button>
      </form>
    </aside>
  );
}

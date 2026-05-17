'use client';

import { FormEvent, useState } from 'react';
import { X } from 'lucide-react';
import type { ContractRecordItem } from '@/lib/api/types';

export type ContractAction = 'issue' | 'review' | 'lock' | 'cancel';

export function ContractActionDialog({
  action,
  contract,
  submitting,
  onClose,
  onSubmit,
}: {
  action: ContractAction | null;
  contract: ContractRecordItem | null;
  submitting: boolean;
  onClose: () => void;
  onSubmit: (values: { reviewType: string; comment: string }) => void;
}) {
  const [reviewType, setReviewType] = useState('legal');
  const [comment, setComment] = useState('');

  if (!action || !contract) {
    return null;
  }

  function title() {
    if (action === 'issue') {
      return 'Issue contract';
    }
    if (action === 'review') {
      return 'Submit for review';
    }
    if (action === 'lock') {
      return 'Lock final contract';
    }
    return 'Cancel contract';
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit({ reviewType, comment });
  }

  return (
    <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-md overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-blue-700">Contract action</p>
          <h2 className="mt-1 text-xl font-bold text-slate-950">{title()}</h2>
          <p className="mt-1 text-sm text-slate-500">{contract.counterparty_name}</p>
        </div>
        <button
          aria-label="Close contract action"
          className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700"
          onClick={onClose}
          type="button"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
        {action === 'review' ? (
          <div>
            <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="contract-review-type">
              Review type
            </label>
            <select
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
              id="contract-review-type"
              onChange={(event) => setReviewType(event.target.value)}
              value={reviewType}
            >
              <option value="legal">Legal review</option>
              <option value="finance">Finance review</option>
              <option value="scm">SCM review</option>
            </select>
          </div>
        ) : null}
        {(action === 'lock' || action === 'cancel') ? (
          <div>
            <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="contract-comment">
              Comment
            </label>
            <textarea
              className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950"
              id="contract-comment"
              onChange={(event) => setComment(event.target.value)}
              value={comment}
            />
          </div>
        ) : null}
        <button
          className="inline-flex h-10 w-full items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          disabled={submitting}
          type="submit"
        >
          {submitting ? 'Submitting' : title()}
        </button>
      </form>
    </aside>
  );
}


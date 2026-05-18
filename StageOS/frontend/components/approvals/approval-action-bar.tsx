'use client';

import { useState } from 'react';

type ApprovalAction = 'approve' | 'reject' | 'request_changes' | 'escalate' | 'exception_approve';

type ApprovalActionBarProps = {
  canApprove: boolean;
  canEscalate?: boolean;
  canExceptionApprove?: boolean;
  onAction: (action: ApprovalAction, comment?: string) => Promise<void>;
  loading?: boolean;
};

const actionConfig: Record<ApprovalAction, { label: string; requiresComment: boolean }> = {
  approve: { label: 'Approve this item?', requiresComment: false },
  reject: { label: 'Reason for rejection (required)', requiresComment: true },
  request_changes: { label: 'What changes are needed? (required)', requiresComment: true },
  escalate: { label: 'Reason for escalation', requiresComment: false },
  exception_approve: { label: 'Reason for exception approval (required)', requiresComment: true },
};

export function ApprovalActionBar({
  canApprove,
  canEscalate = false,
  canExceptionApprove = false,
  onAction,
  loading = false,
}: ApprovalActionBarProps) {
  const [activeAction, setActiveAction] = useState<ApprovalAction | null>(null);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!canApprove) return null;

  async function handleSubmit(action: ApprovalAction) {
    setSubmitting(true);
    try {
      await onAction(action, comment || undefined);
      setActiveAction(null);
      setComment('');
    } finally {
      setSubmitting(false);
    }
  }

  const config = activeAction ? actionConfig[activeAction] : null;

  return (
    <div aria-label="Approval actions" className="rounded-lg border border-gray-200 bg-gray-50 p-4" role="group">
      {activeAction && config ? (
        <div className="space-y-3">
          <p className="text-sm font-medium text-gray-700" id="action-prompt">{config.label}</p>
          {config.requiresComment && (
            <div>
              <label className="sr-only" htmlFor="approval-comment">Comment</label>
              <textarea
                aria-describedby="action-prompt"
                aria-required="true"
                className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-teal-600 focus:outline-none focus:ring-1 focus:ring-teal-600"
                id="approval-comment"
                onChange={(e) => setComment(e.target.value)}
                placeholder="Add your comment..."
                rows={3}
                value={comment}
              />
            </div>
          )}
          <div className="flex gap-2">
            <button
              className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2"
              disabled={submitting || (config.requiresComment && !comment.trim())}
              onClick={() => handleSubmit(activeAction)}
              type="button"
            >
              {submitting ? 'Submitting...' : 'Confirm'}
            </button>
            <button
              className="rounded-md border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
              onClick={() => { setActiveAction(null); setComment(''); }}
              type="button"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-wrap gap-2">
          <button
            className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2"
            disabled={loading}
            onClick={() => setActiveAction('approve')}
            type="button"
          >
            Approve
          </button>
          <button
            className="rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2"
            disabled={loading}
            onClick={() => setActiveAction('request_changes')}
            type="button"
          >
            Request Changes
          </button>
          <button
            className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            disabled={loading}
            onClick={() => setActiveAction('reject')}
            type="button"
          >
            Decline
          </button>
          {canEscalate && (
            <button
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
              disabled={loading}
              onClick={() => setActiveAction('escalate')}
              type="button"
            >
              Escalate
            </button>
          )}
          {canExceptionApprove && (
            <button
              className="rounded-md border border-amber-300 bg-amber-50 px-4 py-2 text-sm font-medium text-amber-700 hover:bg-amber-100 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2"
              disabled={loading}
              onClick={() => setActiveAction('exception_approve')}
              type="button"
            >
              Exception Approve
            </button>
          )}
        </div>
      )}
    </div>
  );
}

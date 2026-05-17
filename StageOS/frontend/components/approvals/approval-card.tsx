import { StatusBadge } from '@/components/ui/status-badge';
import type {
  ApprovalRequestItem,
  ApprovalStepItem,
  DocumentItem,
  OperatingContextListItem,
  UserListItem,
} from '@/lib/api/types';
import { approvalStepName, documentTitle, userName, workspaceName } from './helpers';
import { EvidenceReviewPanel } from './evidence-review-panel';

function decisionTone(decision: string) {
  if (decision === 'approved' || decision === 'exception_approved') {
    return 'good';
  }
  if (decision === 'rejected' || decision === 'changes_requested') {
    return 'danger';
  }
  return 'warning';
}

export function ApprovalCard({
  approval,
  steps,
  workspaces,
  users,
  documents,
  onSelect,
  canDecide,
}: {
  approval: ApprovalRequestItem;
  steps: ApprovalStepItem[];
  workspaces: OperatingContextListItem[];
  users: UserListItem[];
  documents: DocumentItem[];
  onSelect: (approval: ApprovalRequestItem) => void;
  canDecide: boolean;
}) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-950">
            {approvalStepName(steps, approval.approval_step)}
          </h2>
          <p className="mt-1 text-sm text-slate-500">{workspaceName(workspaces, approval.operating_context)}</p>
        </div>
        <StatusBadge tone={decisionTone(approval.decision)}>
          {approval.decision.replace('_', ' ')}
        </StatusBadge>
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="font-bold text-slate-700">Requested by</dt>
          <dd className="mt-1 text-slate-600">{userName(users, approval.requested_by)}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Requested date</dt>
          <dd className="mt-1 text-slate-600">{new Date(approval.requested_at).toLocaleDateString()}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Decided by</dt>
          <dd className="mt-1 text-slate-600">{userName(users, approval.decided_by)}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Decided date</dt>
          <dd className="mt-1 text-slate-600">
            {approval.decided_at ? new Date(approval.decided_at).toLocaleDateString() : 'Not decided'}
          </dd>
        </div>
      </dl>
      <div className="mt-4">
        <EvidenceReviewPanel label={documentTitle(documents, approval.evidence_reviewed)} />
      </div>
      {approval.decision === 'pending' && canDecide ? (
        <button
          className="mt-4 h-10 rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700"
          onClick={() => onSelect(approval)}
          type="button"
        >
          Review decision
        </button>
      ) : approval.decision === 'pending' ? (
        <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-800">
          This action requires additional approval authority.
        </div>
      ) : null}
    </article>
  );
}

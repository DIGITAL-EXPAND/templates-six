import type { ApprovalRequestItem, ApprovalStepItem, UserListItem } from '@/lib/api/types';
import { approvalStepName, userName } from './helpers';

export function ApprovalTimeline({
  approvals,
  steps,
  users,
}: {
  approvals: ApprovalRequestItem[];
  steps: ApprovalStepItem[];
  users: UserListItem[];
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <h2 className="text-base font-bold text-slate-950">Approval timeline</h2>
      <div className="mt-4 space-y-4">
        {approvals.map((approval) => (
          <div className="border-l-2 border-slate-200 pl-4" key={approval.id}>
            <div className="text-sm font-bold text-slate-900">
              {approvalStepName(steps, approval.approval_step)}
            </div>
            <div className="mt-1 text-xs text-slate-500">
              {approval.decision.replace('_', ' ')} · {userName(users, approval.decided_by)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

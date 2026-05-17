import type {
  ApprovalRequestItem,
  ApprovalStepItem,
  DocumentItem,
  OperatingContextListItem,
  UserListItem,
} from '@/lib/api/types';
import { ApprovalCard } from './approval-card';

export function ApprovalList({
  approvals,
  steps,
  workspaces,
  users,
  documents,
  onSelect,
  canDecide,
}: {
  approvals: ApprovalRequestItem[];
  steps: ApprovalStepItem[];
  workspaces: OperatingContextListItem[];
  users: UserListItem[];
  documents: DocumentItem[];
  onSelect: (approval: ApprovalRequestItem) => void;
  canDecide: (approval: ApprovalRequestItem) => boolean;
}) {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {approvals.map((approval) => (
        <ApprovalCard
          approval={approval}
          documents={documents}
          key={approval.id}
          canDecide={canDecide(approval)}
          onSelect={onSelect}
          steps={steps}
          users={users}
          workspaces={workspaces}
        />
      ))}
    </div>
  );
}

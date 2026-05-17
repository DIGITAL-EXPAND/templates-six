import { StatusBadge } from '@/components/ui/status-badge';
import type {
  DocumentItem,
  EvidenceSubmissionItem,
  TaskItem,
  UserListItem,
} from '@/lib/api/types';
import { documentTypeLabel, evidenceStatus, taskName, userName } from './helpers';

export function EvidenceList({
  evidence,
  documents,
  tasks,
  users,
  acceptingId,
  onAccept,
  rejectingId,
  onReject,
}: {
  evidence: EvidenceSubmissionItem[];
  documents: DocumentItem[];
  tasks: TaskItem[];
  users: UserListItem[];
  acceptingId: string;
  rejectingId: string;
  onAccept: (item: EvidenceSubmissionItem) => void;
  onReject: (item: EvidenceSubmissionItem) => void;
}) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div className="divide-y divide-slate-100">
        {evidence.map((item) => {
          const document = documents.find((doc) => doc.id === item.document);
          const status = evidenceStatus(item);
          return (
            <article className="grid gap-3 px-4 py-4 lg:grid-cols-[1.2fr_1fr_0.7fr_0.7fr]" key={item.id}>
              <div className="min-w-0">
                <h2 className="truncate text-sm font-bold text-slate-950">
                  {document?.title ?? 'Document unavailable'}
                </h2>
                <p className="mt-1 truncate text-xs text-slate-500">{taskName(tasks, item.task)}</p>
              </div>
              <div className="text-sm text-slate-600">
                <div className="font-semibold">{document ? documentTypeLabel(document.document_type) : 'Evidence'}</div>
                <div className="mt-1 text-xs text-slate-500">{userName(users, item.submitted_by)}</div>
              </div>
              <div>
                <StatusBadge tone={status === 'accepted' ? 'good' : status === 'rejected' ? 'danger' : 'warning'}>{status}</StatusBadge>
                {item.rejection_reason ? <p className="mt-2 text-xs font-medium text-rose-700">{item.rejection_reason}</p> : null}
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:text-slate-400"
                  disabled={item.accepted || acceptingId === item.id || rejectingId === item.id}
                  onClick={() => onAccept(item)}
                  type="button"
                >
                  {acceptingId === item.id ? 'Accepting' : item.accepted ? 'Accepted' : 'Accept'}
                </button>
                <button
                  className="h-9 rounded-md border border-rose-200 px-3 text-sm font-bold text-rose-700 hover:bg-rose-50 disabled:cursor-not-allowed disabled:text-rose-300"
                  disabled={item.rejected || acceptingId === item.id || rejectingId === item.id}
                  onClick={() => onReject(item)}
                  type="button"
                >
                  {rejectingId === item.id ? 'Rejecting' : item.rejected ? 'Rejected' : 'Reject'}
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}

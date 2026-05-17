import { Download, Lock, Unlock } from 'lucide-react';
import { StatusBadge } from '@/components/ui/status-badge';
import type { DocumentItem, OperatingContextListItem, UserListItem } from '@/lib/api/types';
import { documentTypeLabel, userName, workspaceName } from './helpers';

export function DocumentList({
  documents,
  workspaces,
  users,
  onDownload,
}: {
  documents: DocumentItem[];
  workspaces: OperatingContextListItem[];
  users: UserListItem[];
  onDownload?: (document: DocumentItem) => void;
}) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div className="divide-y divide-slate-100">
        {documents.map((document) => (
          <article
            className="grid gap-3 px-4 py-4 lg:grid-cols-[1.3fr_1fr_0.8fr_0.8fr]"
            key={document.id}
          >
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="truncate text-sm font-bold text-slate-950">{document.title}</h2>
                {document.is_locked ? <StatusBadge tone="warning">Read-only</StatusBadge> : null}
              </div>
              <p className="mt-1 truncate text-xs text-slate-500">
                {workspaceName(workspaces, document.operating_context)}
              </p>
            </div>
            <div className="text-sm text-slate-600">
              <div className="font-semibold">{documentTypeLabel(document.document_type)}</div>
              <div className="mt-1 text-xs text-slate-500">{document.file_name}</div>
            </div>
            <div className="text-sm text-slate-600">
              <div className="font-semibold">Version {document.version}</div>
              <div className="mt-1 text-xs text-slate-500">{userName(users, document.uploaded_by)}</div>
            </div>
            <div className="text-sm text-slate-600">
              <div className="flex items-center gap-2 font-semibold">
                {document.is_locked ? <Lock className="h-4 w-4" /> : <Unlock className="h-4 w-4" />}
                {document.is_locked ? 'Locked' : 'Editable'}
              </div>
              <div className="mt-1 flex items-center gap-2 text-xs text-slate-500">
                <span>{new Date(document.created_at).toLocaleDateString()}</span>
                {document.storage_ref && onDownload ? (
                  <button
                    className="inline-flex items-center gap-1 font-bold text-blue-700"
                    onClick={() => onDownload(document)}
                    type="button"
                  >
                    <Download className="h-3.5 w-3.5" />
                    Download
                  </button>
                ) : null}
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

'use client';

import { FormEvent, useState } from 'react';
import { X } from 'lucide-react';
import type { ArtistDocumentItem, ArtistEngagementItem } from '@/lib/api/types';

export type ArtistAction =
  | { kind: 'verify_document'; document: ArtistDocumentItem }
  | { kind: 'reject_document'; document: ArtistDocumentItem }
  | { kind: 'confirm_engagement'; engagement: ArtistEngagementItem };

export function ArtistActionDialog({
  action,
  submitting,
  onClose,
  onSubmit,
}: {
  action: ArtistAction | null;
  submitting: boolean;
  onClose: () => void;
  onSubmit: (comment: string) => void;
}) {
  const [comment, setComment] = useState('');
  if (!action) return null;
  const title = action.kind === 'confirm_engagement' ? 'Confirm engagement' : action.kind === 'verify_document' ? 'Verify artist document' : 'Reject artist document';
  const needsComment = action.kind === 'reject_document';

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(comment);
  }

  return (
    <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-md overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl">
      <div className="flex items-start justify-between gap-4">
        <div><p className="text-sm font-semibold text-blue-700">Artist action</p><h2 className="mt-1 text-xl font-bold text-slate-950">{title}</h2></div>
        <button aria-label="Close artist action" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700" onClick={onClose} type="button"><X className="h-4 w-4" /></button>
      </div>
      <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
        {needsComment ? <div><label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="artist-comment">Comment</label><textarea className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950" id="artist-comment" onChange={(event) => setComment(event.target.value)} value={comment} /></div> : null}
        <button className="inline-flex h-10 w-full items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400" disabled={submitting} type="submit">{submitting ? 'Submitting' : title}</button>
      </form>
    </aside>
  );
}


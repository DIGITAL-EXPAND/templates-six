'use client';

import { X } from 'lucide-react';
import { BlockerAlert, labelFromValue, money, ReadinessBadge, RestrictedField } from '@/components/readiness/shared';
import type { ArtistDocumentItem, ArtistEngagementItem, ArtistItem, ContractRecordItem, OperatingContextListItem } from '@/lib/api/types';
import type { ArtistAction } from './artist-action-dialog';
import { artistBlockers, artistDisplayName, artistDocuments, artistEngagements } from './helpers';

function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  return workspaces.find((workspace) => workspace.id === id)?.title ?? 'Workspace unavailable';
}

function contractName(contracts: ContractRecordItem[], id: string | null) {
  if (!id) return 'No contract linked';
  return contracts.find((contract) => contract.id === id)?.counterparty_name ?? 'Contract unavailable';
}

export function ArtistDetailDrawer({
  artist,
  documents,
  engagements,
  contracts,
  workspaces,
  onAction,
  onClose,
}: {
  artist: ArtistItem | null;
  documents: ArtistDocumentItem[];
  engagements: ArtistEngagementItem[];
  contracts: ContractRecordItem[];
  workspaces: OperatingContextListItem[];
  onAction: (action: ArtistAction) => void;
  onClose: () => void;
}) {
  if (!artist) return null;
  const artistDocs = artistDocuments(documents, artist.id);
  const artistEngs = artistEngagements(engagements, artist.id);

  return (
    <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-2xl overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl">
      <div className="flex items-start justify-between gap-4">
        <div><p className="text-sm font-semibold text-blue-700">Artist detail</p><h2 className="mt-1 text-xl font-bold text-slate-950">{artistDisplayName(artist)}</h2><p className="mt-1 text-sm text-slate-500">{artist.legal_name} · {artist.discipline}</p></div>
        <button aria-label="Close artist detail" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700" onClick={onClose} type="button"><X className="h-4 w-4" /></button>
      </div>
      <div className="mt-5 space-y-5">
        <div className="flex flex-wrap gap-2"><ReadinessBadge value={artist.status} /></div>
        <BlockerAlert blockers={artistBlockers(artist, artistDocs, artistEngs)} />
        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Profile</h3>
          <dl className="mt-3 grid gap-3 text-sm md:grid-cols-2">
            <div><dt className="font-bold text-slate-700">Contact email</dt><dd className="mt-1 text-slate-600"><RestrictedField value={artist.contact_email} /></dd></div>
            <div><dt className="font-bold text-slate-700">Contact phone</dt><dd className="mt-1 text-slate-600"><RestrictedField value={artist.contact_phone} /></dd></div>
            <div><dt className="font-bold text-slate-700">Standard fee</dt><dd className="mt-1 text-slate-600">{money(artist.standard_fee)}</dd></div>
            <div><dt className="font-bold text-slate-700">Payment readiness</dt><dd className="mt-1 text-slate-600">{artist.status === 'payment_ready' ? 'Ready' : 'Not ready'}</dd></div>
          </dl>
          {artist.notes ? <p className="mt-3 text-sm leading-6 text-slate-600">{artist.notes}</p> : null}
        </section>
        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Document checklist</h3>
          <div className="mt-3 divide-y divide-slate-100 rounded-md border border-slate-200">
            {artistDocs.length ? artistDocs.map((document) => (
              <div className="flex flex-col gap-3 p-3 md:flex-row md:items-center md:justify-between" key={document.id}>
                <div><div className="text-sm font-bold text-slate-900">{labelFromValue(document.document_type)}</div><div className="mt-1 text-xs text-slate-500">{document.file_name || 'No file linked'}</div></div>
                <div className="flex flex-wrap items-center gap-2"><ReadinessBadge value={document.status} /><button className="h-8 rounded-md border border-slate-200 px-2 text-xs font-bold text-slate-700" onClick={() => onAction({ kind: 'verify_document', document })} type="button">Verify</button><button className="h-8 rounded-md border border-rose-200 px-2 text-xs font-bold text-rose-700" onClick={() => onAction({ kind: 'reject_document', document })} type="button">Reject</button></div>
              </div>
            )) : <div className="p-3 text-sm text-slate-500">No artist documents returned.</div>}
          </div>
        </section>
        <section className="rounded-lg border border-slate-200 p-4">
          <h3 className="text-base font-bold text-slate-950">Engagement history</h3>
          <div className="mt-3 grid gap-3">
            {artistEngs.length ? artistEngs.map((engagement) => <div className="rounded-md border border-slate-200 p-3" key={engagement.id}><div className="text-sm font-bold text-slate-900">{workspaceName(workspaces, engagement.operating_context)}</div><div className="mt-1 text-xs text-slate-500">{engagement.role} · {money(engagement.fee)} · {contractName(contracts, engagement.contract)}</div><div className="mt-2 flex flex-wrap items-center gap-2"><ReadinessBadge value={engagement.status} /><button className="h-8 rounded-md border border-slate-200 px-2 text-xs font-bold text-slate-700" onClick={() => onAction({ kind: 'confirm_engagement', engagement })} type="button">Confirm engagement</button></div></div>) : <div className="text-sm text-slate-500">No linked Workspace engagements returned.</div>}
          </div>
        </section>
      </div>
    </aside>
  );
}


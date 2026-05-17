import { BlockerAlert, money, ReadinessBadge, RestrictedField } from '@/components/readiness/shared';
import type { ArtistDocumentItem, ArtistEngagementItem, ArtistItem, ContractRecordItem, OperatingContextListItem } from '@/lib/api/types';
import { artistBlockers, artistDisplayName, artistDocuments, artistEngagements } from './helpers';

function workspaceNames(engagements: ArtistEngagementItem[], workspaces: OperatingContextListItem[]) {
  return engagements.map((engagement) => workspaces.find((workspace) => workspace.id === engagement.operating_context)?.title ?? 'Workspace unavailable').join(', ') || 'No linked Workspace';
}

export function ArtistCard({
  artist,
  documents,
  engagements,
  contracts,
  workspaces,
  onSelect,
}: {
  artist: ArtistItem;
  documents: ArtistDocumentItem[];
  engagements: ArtistEngagementItem[];
  contracts: ContractRecordItem[];
  workspaces: OperatingContextListItem[];
  onSelect: (artist: ArtistItem) => void;
}) {
  const artistDocs = artistDocuments(documents, artist.id);
  const artistEngs = artistEngagements(engagements, artist.id);
  const linkedContracts = artistEngs.filter((engagement) => contracts.some((contract) => contract.id === engagement.contract)).length;

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div><h2 className="text-base font-bold text-slate-950">{artistDisplayName(artist)}</h2><p className="mt-1 text-sm text-slate-500">{artist.legal_name} · {artist.discipline}</p></div>
        <ReadinessBadge value={artist.status} />
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-3">
        <div><dt className="font-bold text-slate-700">Contact email</dt><dd className="mt-1 text-slate-600"><RestrictedField value={artist.contact_email} /></dd></div>
        <div><dt className="font-bold text-slate-700">Standard fee</dt><dd className="mt-1 text-slate-600">{money(artist.standard_fee)}</dd></div>
        <div><dt className="font-bold text-slate-700">Linked contracts</dt><dd className="mt-1 text-slate-600">{linkedContracts}</dd></div>
      </dl>
      <p className="mt-3 text-sm text-slate-500">{workspaceNames(artistEngs, workspaces)}</p>
      <div className="mt-4"><BlockerAlert blockers={artistBlockers(artist, artistDocs, artistEngs)} /></div>
      <button className="mt-4 h-10 rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700" onClick={() => onSelect(artist)} type="button">View artist</button>
    </article>
  );
}


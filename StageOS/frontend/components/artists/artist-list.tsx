import type { ArtistDocumentItem, ArtistEngagementItem, ArtistItem, ContractRecordItem, OperatingContextListItem } from '@/lib/api/types';
import { ArtistCard } from './artist-card';

export function ArtistList({
  artists,
  documents,
  engagements,
  contracts,
  workspaces,
  onSelect,
}: {
  artists: ArtistItem[];
  documents: ArtistDocumentItem[];
  engagements: ArtistEngagementItem[];
  contracts: ContractRecordItem[];
  workspaces: OperatingContextListItem[];
  onSelect: (artist: ArtistItem) => void;
}) {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {artists.map((artist) => (
        <ArtistCard artist={artist} contracts={contracts} documents={documents} engagements={engagements} key={artist.id} onSelect={onSelect} workspaces={workspaces} />
      ))}
    </div>
  );
}


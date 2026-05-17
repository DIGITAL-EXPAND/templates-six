'use client';

import { useEffect, useState } from 'react';
import { ArtistActionDialog, type ArtistAction } from '@/components/artists/artist-action-dialog';
import { ArtistDetailDrawer } from '@/components/artists/artist-detail-drawer';
import { ArtistList } from '@/components/artists/artist-list';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  confirmArtistEngagement,
  decideArtistDocument,
  fetchArtistDocuments,
  fetchArtistEngagements,
  fetchArtists,
  fetchContracts,
  fetchOperatingContexts,
} from '@/lib/api/endpoints';
import type { ArtistDocumentItem, ArtistEngagementItem, ArtistItem, ContractRecordItem, OperatingContextListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceArtistsTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [artists, setArtists] = useState<ArtistItem[]>([]);
  const [documents, setDocuments] = useState<ArtistDocumentItem[]>([]);
  const [engagements, setEngagements] = useState<ArtistEngagementItem[]>([]);
  const [contracts, setContracts] = useState<ContractRecordItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [selectedArtist, setSelectedArtist] = useState<ArtistItem | null>(null);
  const [action, setAction] = useState<ArtistAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([fetchArtistEngagements(tokens.access, { operating_context: workspaceId }), fetchArtists(tokens.access), fetchArtistDocuments(tokens.access), fetchContracts(tokens.access), fetchOperatingContexts(tokens.access)])
      .then(([engagementResult, artistResult, documentResult, contractResult, workspaceResult]) => {
        if (!mounted) return;
        if (engagementResult.status === 'fulfilled') setEngagements(engagementResult.value.results);
        else if (engagementResult.reason instanceof ApiError && engagementResult.reason.status === 403) setPermissionDenied(true);
        else setError('Artists could not be loaded for this Workspace.');
        if (artistResult.status === 'fulfilled' && engagementResult.status === 'fulfilled') {
          const artistIds = new Set(engagementResult.value.results.map((engagement) => engagement.artist));
          setArtists(artistResult.value.results.filter((artist) => artistIds.has(artist.id)));
        }
        if (documentResult.status === 'fulfilled') setDocuments(documentResult.value.results);
        if (contractResult.status === 'fulfilled') setContracts(contractResult.value.results);
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access, workspaceId]);

  async function handleAction(comment: string) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    setError('');
    try {
      if (action.kind === 'confirm_engagement') {
        const updated = await confirmArtistEngagement(tokens.access, action.engagement.id);
        setEngagements((current) => current.map((engagement) => (engagement.id === updated.id ? updated : engagement)));
      } else {
        const updated = await decideArtistDocument(tokens.access, action.document.id, action.kind === 'verify_document' ? 'verify' : 'reject', comment);
        setDocuments((current) => current.map((document) => (document.id === updated.id ? updated : document)));
      }
      setAction(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to perform this artist action.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Artist action could not be completed.');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingState label="Loading Workspace artists" />;

  return (
    <div className="space-y-4">
      {permissionDenied ? <PermissionDeniedState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {artists.length ? <ArtistList artists={artists} contracts={contracts} documents={documents} engagements={engagements} onSelect={setSelectedArtist} workspaces={workspaces} /> : <EmptyState description="Artists linked to this Workspace will appear here." title="No artists yet" />}
      <ArtistDetailDrawer artist={selectedArtist} contracts={contracts} documents={documents} engagements={engagements} onAction={setAction} onClose={() => setSelectedArtist(null)} workspaces={workspaces} />
      <ArtistActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </div>
  );
}


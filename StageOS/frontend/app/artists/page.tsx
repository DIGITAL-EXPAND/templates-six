'use client';

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DepartmentExecutiveActionsPanel } from '@/components/governance/department-executive-actions-panel';
import { ArtistActionDialog, type ArtistAction } from '@/components/artists/artist-action-dialog';
import { ArtistDetailDrawer } from '@/components/artists/artist-detail-drawer';
import { ArtistFilters, type ArtistFiltersValue } from '@/components/artists/artist-filters';
import { artistDisplayName, artistDocuments, artistEngagements } from '@/components/artists/helpers';
import { ArtistList } from '@/components/artists/artist-list';
import { PageHeader } from '@/components/ui/page-header';
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

export default function ArtistsPage() {
  const { tokens } = useAuth();
  const [artists, setArtists] = useState<ArtistItem[]>([]);
  const [documents, setDocuments] = useState<ArtistDocumentItem[]>([]);
  const [engagements, setEngagements] = useState<ArtistEngagementItem[]>([]);
  const [contracts, setContracts] = useState<ContractRecordItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [selectedArtist, setSelectedArtist] = useState<ArtistItem | null>(null);
  const [action, setAction] = useState<ArtistAction | null>(null);
  const [filters, setFilters] = useState<ArtistFiltersValue>({ status: 'all', discipline: 'all', contractReady: false, paymentReady: false, workspace: 'all', search: '' });
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([fetchArtists(tokens.access), fetchArtistDocuments(tokens.access), fetchArtistEngagements(tokens.access), fetchContracts(tokens.access), fetchOperatingContexts(tokens.access)])
      .then(([artistResult, documentResult, engagementResult, contractResult, workspaceResult]) => {
        if (!mounted) return;
        if (artistResult.status === 'fulfilled') setArtists(artistResult.value.results);
        else if (artistResult.reason instanceof ApiError && artistResult.reason.status === 403) setPermissionDenied(true);
        else setError('Artists could not be loaded.');
        if (documentResult.status === 'fulfilled') setDocuments(documentResult.value.results);
        if (engagementResult.status === 'fulfilled') setEngagements(engagementResult.value.results);
        if (contractResult.status === 'fulfilled') setContracts(contractResult.value.results);
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  const disciplines = useMemo(() => Array.from(new Set(artists.map((artist) => artist.discipline).filter(Boolean))).sort(), [artists]);
  const filteredArtists = useMemo(() => artists.filter((artist) => {
    const docs = artistDocuments(documents, artist.id);
    const engs = artistEngagements(engagements, artist.id);
    const query = filters.search.trim().toLowerCase();
    if (filters.status !== 'all' && artist.status !== filters.status) return false;
    if (filters.discipline !== 'all' && artist.discipline !== filters.discipline) return false;
    if (filters.contractReady && !['contract_ready', 'contracted', 'payment_ready'].includes(artist.status)) return false;
    if (filters.paymentReady && artist.status !== 'payment_ready') return false;
    if (filters.workspace !== 'all' && !engs.some((engagement) => engagement.operating_context === filters.workspace)) return false;
    if (query && !`${artist.legal_name} ${artist.professional_name} ${artist.discipline}`.toLowerCase().includes(query)) return false;
    if (filters.contractReady && docs.some((document) => document.status === 'missing' || document.status === 'rejected')) return false;
    return true;
  }), [artists, documents, engagements, filters]);

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

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader description="Manage artist profiles, documents, engagements, contract readiness and payment readiness." eyebrow="Artists" title="Artists" />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading artists" /> : (
          <>
            <ArtistFilters disciplines={disciplines} onChange={setFilters} value={filters} workspaces={workspaces} />
            <DepartmentExecutiveActionsPanel departmentTypes={['programming', 'contracts']} targetTypes={['Artist', 'ArtistEngagement', 'ArtistDocument']} title="Executive actions for Artists" />
            {filteredArtists.length ? <ArtistList artists={filteredArtists} contracts={contracts} documents={documents} engagements={engagements} onSelect={setSelectedArtist} workspaces={workspaces} /> : <EmptyState description="Artists will appear here when records are available or filters are cleared." title="No artists found" />}
          </>
        )}
      </div>
      <ArtistDetailDrawer artist={selectedArtist} contracts={contracts} documents={documents} engagements={engagements} onAction={setAction} onClose={() => setSelectedArtist(null)} workspaces={workspaces} />
      <ArtistActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </AppShell>
  );
}

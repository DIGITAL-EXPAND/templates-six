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
import { StatusBadge } from '@/components/ui/status-badge';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  approveArtistPayment,
  confirmArtistEngagement,
  decideArtistDocument,
  fetchArtistDocuments,
  fetchArtistEngagements,
  fetchArtistPayments,
  fetchArtists,
  fetchContracts,
  fetchOperatingContexts,
  markArtistPaymentPaid,
} from '@/lib/api/endpoints';
import type { ArtistDocumentItem, ArtistEngagementItem, ArtistItem, ArtistPaymentItem, ContractRecordItem, OperatingContextListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function formatZAR(val: string) {
  return 'R ' + parseFloat(val).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

const PAYMENT_STATUS_TONE: Record<string, 'neutral' | 'info' | 'warning' | 'good' | 'danger'> = {
  pending: 'neutral',
  invoice_received: 'info',
  approved: 'warning',
  paid: 'good',
  disputed: 'danger',
};

export default function ArtistsPage() {
  const { tokens } = useAuth();
  const [artists, setArtists] = useState<ArtistItem[]>([]);
  const [documents, setDocuments] = useState<ArtistDocumentItem[]>([]);
  const [engagements, setEngagements] = useState<ArtistEngagementItem[]>([]);
  const [contracts, setContracts] = useState<ContractRecordItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [payments, setPayments] = useState<ArtistPaymentItem[]>([]);
  const [selectedArtist, setSelectedArtist] = useState<ArtistItem | null>(null);
  const [action, setAction] = useState<ArtistAction | null>(null);
  const [filters, setFilters] = useState<ArtistFiltersValue>({ status: 'all', discipline: 'all', contractReady: false, paymentReady: false, workspace: 'all', search: '' });
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [paymentActionBusy, setPaymentActionBusy] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([fetchArtists(tokens.access), fetchArtistDocuments(tokens.access), fetchArtistEngagements(tokens.access), fetchContracts(tokens.access), fetchOperatingContexts(tokens.access), fetchArtistPayments(tokens.access)])
      .then(([artistResult, documentResult, engagementResult, contractResult, workspaceResult, paymentResult]) => {
        if (!mounted) return;
        if (artistResult.status === 'fulfilled') setArtists(artistResult.value.results);
        else if (artistResult.reason instanceof ApiError && artistResult.reason.status === 403) setPermissionDenied(true);
        else setError('Artists could not be loaded.');
        if (documentResult.status === 'fulfilled') setDocuments(documentResult.value.results);
        if (engagementResult.status === 'fulfilled') setEngagements(engagementResult.value.results);
        if (contractResult.status === 'fulfilled') setContracts(contractResult.value.results);
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
        if (paymentResult.status === 'fulfilled') setPayments(paymentResult.value);
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

  async function handlePaymentApprove(paymentId: string) {
    if (!tokens?.access) return;
    setPaymentActionBusy(paymentId);
    try {
      const updated = await approveArtistPayment(tokens.access, paymentId);
      setPayments((current) => current.map((p) => (p.id === updated.id ? updated : p)));
    } catch {
      setError('Payment approve action failed.');
    } finally {
      setPaymentActionBusy(null);
    }
  }

  async function handlePaymentMarkPaid(paymentId: string) {
    if (!tokens?.access) return;
    setPaymentActionBusy(paymentId);
    try {
      const updated = await markArtistPaymentPaid(tokens.access, paymentId);
      setPayments((current) => current.map((p) => (p.id === updated.id ? updated : p)));
    } catch {
      setError('Mark paid action failed.');
    } finally {
      setPaymentActionBusy(null);
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

        {/* Artist Payments */}
        {!loading && (
          <details className="group rounded-xl border border-gray-200 bg-white">
            <summary className="flex cursor-pointer items-center justify-between px-5 py-4 text-sm font-semibold text-gray-800 select-none list-none [&::-webkit-details-marker]:hidden">
              Artist Payments
              <span className="text-xs font-normal text-gray-500">
                {payments.length} record{payments.length !== 1 ? 's' : ''}
              </span>
            </summary>
            <div className="border-t border-gray-100">
              {payments.length === 0 ? (
                <p className="px-5 py-6 text-sm text-gray-400 text-center">No payment records found.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-100">
                      <tr>
                        {['Engagement', 'Milestone', 'Amount', 'Status', 'Due Date', 'Invoice #', 'Paid Date', 'Actions'].map((h) => (
                          <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {payments.map((payment) => {
                        const eng = engagements.find((e) => e.id === payment.engagement);
                        const artist = eng ? artists.find((a) => a.id === eng.artist) : null;
                        const artistLabel = artist
                          ? (artist.professional_name || artist.legal_name)
                          : payment.engagement.slice(0, 8);
                        const isBusy = paymentActionBusy === payment.id;
                        return (
                          <tr key={payment.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-gray-900 font-medium whitespace-nowrap">{artistLabel}</td>
                            <td className="px-4 py-3 text-gray-700 capitalize">{payment.milestone}</td>
                            <td className="px-4 py-3 text-gray-900 font-semibold whitespace-nowrap">{formatZAR(payment.amount)}</td>
                            <td className="px-4 py-3">
                              <StatusBadge tone={PAYMENT_STATUS_TONE[payment.status] ?? 'neutral'}>
                                {payment.status.replace('_', ' ')}
                              </StatusBadge>
                            </td>
                            <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                              {payment.due_date ? new Date(payment.due_date).toLocaleDateString('en-ZA') : '—'}
                            </td>
                            <td className="px-4 py-3 text-gray-500">{payment.invoice_number || '—'}</td>
                            <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                              {payment.paid_date ? new Date(payment.paid_date).toLocaleDateString('en-ZA') : '—'}
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                {payment.status === 'invoice_received' && (
                                  <button
                                    className="rounded border border-amber-300 bg-amber-50 px-2 py-1 text-xs font-medium text-amber-700 hover:bg-amber-100 disabled:opacity-50"
                                    disabled={isBusy}
                                    onClick={() => handlePaymentApprove(payment.id)}
                                  >
                                    Approve
                                  </button>
                                )}
                                {payment.status === 'approved' && (
                                  <button
                                    className="rounded border border-emerald-300 bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700 hover:bg-emerald-100 disabled:opacity-50"
                                    disabled={isBusy}
                                    onClick={() => handlePaymentMarkPaid(payment.id)}
                                  >
                                    Mark Paid
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </details>
        )}
      </div>
      <ArtistDetailDrawer artist={selectedArtist} contracts={contracts} documents={documents} engagements={engagements} onAction={setAction} onClose={() => setSelectedArtist(null)} workspaces={workspaces} />
      <ArtistActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </AppShell>
  );
}

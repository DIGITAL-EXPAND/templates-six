'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchTouringProductions, fetchTouringVenueDates } from '@/lib/api/endpoints';
import type { TouringProduction, TouringVenueDate } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function zar(val: string | null | undefined): string {
  if (!val) return '—';
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function venueDateStatusTone(status: string): StatusTone {
  switch (status) {
    case 'confirmed': return 'good';
    case 'tentative': return 'warning';
    case 'cancelled': return 'danger';
    default: return 'neutral';
  }
}

function TouringCard({ production }: { production: TouringProduction }) {
  const { tokens } = useAuth();
  const [expanded, setExpanded] = useState(false);
  const [venueDates, setVenueDates] = useState<TouringVenueDate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadVenueDates() {
    if (!tokens?.access || venueDates.length > 0) return;
    setLoading(true);
    try {
      const res = await fetchTouringVenueDates(tokens.access, production.id);
      setVenueDates(res.results);
    } catch {
      setError('Failed to load venue dates');
    } finally {
      setLoading(false);
    }
  }

  function handleExpand() {
    if (!expanded) loadVenueDates();
    setExpanded(!expanded);
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <div className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-slate-900">Production #{production.id.slice(0, 8)}</span>
              <StatusBadge tone={production.is_outgoing ? 'good' : 'info'}>
                {production.is_outgoing ? 'Outgoing' : 'Incoming'}
              </StatusBadge>
            </div>
          </div>
          <button
            onClick={handleExpand}
            className="shrink-0 text-xs font-medium text-indigo-600 hover:text-indigo-800"
          >
            {expanded ? 'Hide dates' : 'Show venue dates'}
          </button>
        </div>
        <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
          <div><span className="text-slate-500">Tour Manager:</span> <span className="text-slate-800">{production.tour_manager || '—'}</span></div>
          <div><span className="text-slate-500">Transport:</span> <span className="text-slate-800">{production.transport_provider || '—'}</span></div>
          <div><span className="text-slate-500">Per Diem:</span> <span className="text-slate-800">{zar(production.per_diem_rate)}</span></div>
          <div><span className="text-slate-500">Technical Advance:</span> <span className="text-slate-800">{formatDate(production.technical_advance_date)}</span></div>
        </div>
        {production.notes && (
          <p className="text-xs text-slate-500">{production.notes}</p>
        )}
      </div>

      {expanded && (
        <div className="border-t border-slate-100 bg-slate-50 p-4">
          {loading ? (
            <LoadingState label="Loading venue dates…" />
          ) : error ? (
            <ErrorState message={error} />
          ) : venueDates.length === 0 ? (
            <EmptyState title="No venue dates" description="No venue dates have been added to this touring production." />
          ) : (
            <div className="overflow-hidden rounded border border-slate-200 bg-white">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {['Venue', 'City', 'Performance Date', 'Load In', 'Load Out', 'Fee', 'Status'].map((h) => (
                      <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {venueDates.map((vd) => (
                    <tr key={vd.id} className="hover:bg-slate-50">
                      <td className="px-3 py-2 font-medium text-slate-900">{vd.venue_name}</td>
                      <td className="px-3 py-2 text-slate-600">{vd.city}</td>
                      <td className="px-3 py-2 text-slate-600">{formatDate(vd.performance_date)}</td>
                      <td className="px-3 py-2 text-slate-600">{formatDate(vd.load_in_date)}</td>
                      <td className="px-3 py-2 text-slate-600">{formatDate(vd.load_out_date)}</td>
                      <td className="px-3 py-2 text-slate-600">{zar(vd.fee)}</td>
                      <td className="px-3 py-2"><StatusBadge tone={venueDateStatusTone(vd.status)}>{vd.status}</StatusBadge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function TouringPage() {
  const { tokens } = useAuth();
  const [productions, setProductions] = useState<TouringProduction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchTouringProductions(tokens.access)
      .then((r) => setProductions(r.results))
      .catch(() => setError('Failed to load touring productions'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  const outgoing = productions.filter((p) => p.is_outgoing);
  const incoming = productions.filter((p) => !p.is_outgoing);

  return (
    <AppShell pageTitle="Touring Productions">
      <div className="space-y-6">
        <PageHeader
          title="Touring Productions"
          description="Outgoing tours and incoming touring productions"
        />

        {loading ? (
          <LoadingState label="Loading touring productions…" />
        ) : error ? (
          <ErrorState message={error} />
        ) : (
          <>
            <section className="space-y-3">
              <h2 className="text-base font-semibold text-slate-900">Outgoing Tours</h2>
              {outgoing.length === 0 ? (
                <EmptyState title="No outgoing tours" description="No outgoing touring productions found." />
              ) : (
                <div className="space-y-3">
                  {outgoing.map((p) => <TouringCard key={p.id} production={p} />)}
                </div>
              )}
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-semibold text-slate-900">Incoming Productions</h2>
              {incoming.length === 0 ? (
                <EmptyState title="No incoming productions" description="No incoming touring productions found." />
              ) : (
                <div className="space-y-3">
                  {incoming.map((p) => <TouringCard key={p.id} production={p} />)}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}

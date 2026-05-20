'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { fetchSeasonSummary, fetchSeasonCloseOut } from '@/lib/api/endpoints';
import type { SeasonSummary, SeasonCloseOut } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type SeasonListItem = {
  id: string;
  name: string;
  year: number;
  organisation: string;
  created_at: string;
};

function formatZAR(val: string | null | undefined) {
  if (!val) return 'R 0.00';
  return 'R ' + parseFloat(val).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function netClass(val: string | null | undefined): string {
  if (!val) return 'text-gray-900';
  const n = parseFloat(val);
  if (n > 0) return 'text-emerald-700 font-semibold';
  if (n < 0) return 'text-red-600 font-semibold';
  return 'text-gray-900';
}

// ─────────────────────────────────────────────
// Close-out summary panel
// ─────────────────────────────────────────────
function CloseOutPanel({ data }: { data: SeasonCloseOut }) {
  return (
    <div className="mt-4 rounded-lg border border-gray-200 bg-gray-50 p-4 space-y-3">
      <h4 className="text-sm font-semibold text-gray-800">Close-Out Summary — {data.season_name} ({data.year})</h4>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <caption className="sr-only">Season close-out P&L</caption>
          <thead className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600">
            <tr>
              <th className="pb-2 pr-4" scope="col">Show</th>
              <th className="pb-2 pr-4" scope="col">Status</th>
              <th className="pb-2 pr-4 text-right" scope="col">Performances</th>
              <th className="pb-2 pr-4 text-right" scope="col">Ticket Revenue</th>
              <th className="pb-2 pr-4 text-right" scope="col">Artist Costs</th>
              <th className="pb-2 text-right" scope="col">Net</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.shows.map((show) => (
              <tr key={show.show_id}>
                <td className="py-2 pr-4 font-medium text-gray-900">{show.title}</td>
                <td className="py-2 pr-4 text-gray-500 capitalize">{show.status}</td>
                <td className="py-2 pr-4 text-right text-gray-600">{show.performances}</td>
                <td className="py-2 pr-4 text-right text-gray-700">{formatZAR(show.ticket_revenue)}</td>
                <td className="py-2 pr-4 text-right text-gray-700">{formatZAR(show.artist_costs)}</td>
                <td className={`py-2 text-right ${netClass(show.net)}`}>{formatZAR(show.net)}</td>
              </tr>
            ))}
            {/* Totals row */}
            <tr className="border-t-2 border-gray-300 bg-gray-100">
              <td className="py-2 pr-4 font-semibold text-gray-900" colSpan={3}>Totals</td>
              <td className="py-2 pr-4 text-right font-semibold text-gray-800">{formatZAR(data.totals.total_revenue)}</td>
              <td className="py-2 pr-4 text-right font-semibold text-gray-800">{formatZAR(data.totals.total_costs)}</td>
              <td className={`py-2 text-right ${netClass(data.totals.net_position)}`}>{formatZAR(data.totals.net_position)}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Season card
// ─────────────────────────────────────────────
function SeasonCard({ season, token }: { season: SeasonListItem; token: string }) {
  const [summary, setSummary] = useState<SeasonSummary | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [summaryError, setSummaryError] = useState('');

  const [closeOut, setCloseOut] = useState<SeasonCloseOut | null>(null);
  const [loadingCloseOut, setLoadingCloseOut] = useState(false);
  const [closeOutError, setCloseOutError] = useState('');

  async function loadSummary() {
    if (summary || loadingSummary) return;
    setLoadingSummary(true);
    setSummaryError('');
    try {
      const data = await fetchSeasonSummary(token, season.id);
      setSummary(data);
    } catch {
      setSummaryError('Could not load season summary.');
    } finally {
      setLoadingSummary(false);
    }
  }

  async function loadCloseOut() {
    if (closeOut || loadingCloseOut) return;
    setLoadingCloseOut(true);
    setCloseOutError('');
    try {
      const data = await fetchSeasonCloseOut(token, season.id);
      setCloseOut(data);
    } catch {
      setCloseOutError('Could not load close-out summary.');
    } finally {
      setLoadingCloseOut(false);
    }
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 space-y-4">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h3 className="text-base font-semibold text-gray-900">{season.name}</h3>
          <p className="text-sm text-gray-500 mt-0.5">{season.year}</p>
        </div>
        <div className="flex gap-2 shrink-0">
          {!summary && (
            <button
              className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              disabled={loadingSummary}
              onClick={loadSummary}
            >
              {loadingSummary ? 'Loading…' : 'Load Summary'}
            </button>
          )}
          {!closeOut && (
            <button
              className="rounded-lg border border-indigo-300 bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-700 hover:bg-indigo-100 disabled:opacity-50"
              disabled={loadingCloseOut}
              onClick={loadCloseOut}
            >
              {loadingCloseOut ? 'Loading…' : 'Close-Out Summary'}
            </button>
          )}
        </div>
      </div>

      {summaryError && <p className="text-xs text-red-600">{summaryError}</p>}
      {closeOutError && <p className="text-xs text-red-600">{closeOutError}</p>}

      {summary && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-lg bg-gray-50 p-3">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Shows</p>
            <p className="mt-1 text-2xl font-bold text-gray-900">{summary.show_count.toLocaleString()}</p>
          </div>
          <div className="rounded-lg bg-gray-50 p-3">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Performances</p>
            <p className="mt-1 text-2xl font-bold text-gray-900">{summary.performance_count.toLocaleString()}</p>
          </div>
          <div className="rounded-lg bg-blue-50 p-3">
            <p className="text-xs font-medium text-blue-600 uppercase tracking-wide">Tickets Sold</p>
            <p className="mt-1 text-2xl font-bold text-blue-800">{summary.tickets_sold.toLocaleString()}</p>
          </div>
          <div className="rounded-lg bg-emerald-50 p-3">
            <p className="text-xs font-medium text-emerald-600 uppercase tracking-wide">Gross Revenue</p>
            <p className="mt-1 text-lg font-bold text-emerald-800 leading-tight">{formatZAR(summary.gross_revenue)}</p>
          </div>
        </div>
      )}

      {closeOut && <CloseOutPanel data={closeOut} />}
    </div>
  );
}

export default function SeasonsPage() {
  const { tokens } = useAuth();
  const [seasons, setSeasons] = useState<SeasonListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    fetch('/api/v1/programming/seasons/', {
      headers: { Authorization: `Bearer ${tokens.access}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error(`Status ${r.status}`);
        return r.json();
      })
      .then((data) => {
        if (!mounted) return;
        setSeasons(Array.isArray(data) ? data : (data.results ?? []));
      })
      .catch(() => {
        if (mounted) setError('Season data could not be loaded.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="Financial and production summary by season"
          title="Season Analytics"
        />
        {error ? <ErrorState message={error} /> : null}
        {loading ? (
          <LoadingState label="Loading seasons" />
        ) : seasons.length === 0 ? (
          <EmptyState
            description="Seasons will appear here when programming records are available."
            title="No seasons found"
          />
        ) : (
          <div className="space-y-4">
            {seasons.map((season) => (
              <SeasonCard key={season.id} season={season} token={tokens?.access ?? ''} />
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}

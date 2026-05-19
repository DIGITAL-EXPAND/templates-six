'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { fetchSeasonSummary } from '@/lib/api/endpoints';
import type { SeasonSummary } from '@/lib/api/types';
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

function SeasonCard({ season, token }: { season: SeasonListItem; token: string }) {
  const [summary, setSummary] = useState<SeasonSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function loadSummary() {
    if (summary || loading) return;
    setLoading(true);
    setError('');
    try {
      const data = await fetchSeasonSummary(token, season.id);
      setSummary(data);
    } catch {
      setError('Could not load season summary.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-base font-semibold text-gray-900">{season.name}</h3>
          <p className="text-sm text-gray-500 mt-0.5">{season.year}</p>
        </div>
        {!summary && (
          <button
            className="shrink-0 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            disabled={loading}
            onClick={loadSummary}
          >
            {loading ? 'Loading…' : 'Load Summary'}
          </button>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-600">{error}</p>
      )}

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

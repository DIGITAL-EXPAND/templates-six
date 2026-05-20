'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { ArrowRight } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { fetchShows, fetchOperatingContexts } from '@/lib/api/endpoints';
import type { ShowItem, OperatingContextListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const zar = (val: string) =>
  'R ' + parseFloat(val).toLocaleString('en-ZA', { minimumFractionDigits: 2 });

export default function ShowsPage() {
  const { tokens } = useAuth();
  const [shows, setShows] = useState<ShowItem[]>([]);
  const [contexts, setContexts] = useState<OperatingContextListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.allSettled([
      fetchShows(tokens.access),
      fetchOperatingContexts(tokens.access),
    ]).then(([showsRes, ctxRes]) => {
      if (showsRes.status === 'fulfilled') setShows(showsRes.value);
      if (ctxRes.status === 'fulfilled') setContexts(ctxRes.value.results ?? []);
      if (showsRes.status === 'rejected') setError('Shows could not be loaded.');
      setLoading(false);
    });
  }, [tokens?.access]);

  const contextTitle = (id: string | null) =>
    id ? (contexts.find((c) => c.id === id)?.title ?? id) : '—';

  return (
    <AppShell pageTitle="Shows">
      <PageHeader title="Shows" description="Production show management and lifecycle" />

      {loading && <LoadingState label="Loading shows..." />}
      {error && <ErrorState message={error} />}

      {!loading && !error && shows.length === 0 && (
        <EmptyState
          title="No shows yet"
          description="Shows are created from intake requests converted to productions."
        />
      )}

      {!loading && !error && shows.length > 0 && (
        <div className="mt-6 overflow-hidden rounded-xl border border-gray-200 bg-white">
          <table className="w-full text-sm">
            <caption className="sr-only">Shows list</caption>
            <thead className="border-b border-gray-100 bg-gray-50 text-left">
              <tr>
                <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Production</th>
                <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Budget Approved</th>
                <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Revenue Target</th>
                <th className="px-4 py-3 font-semibold text-gray-700 text-right" scope="col">Lifecycle</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {shows.map((show) => (
                <tr key={show.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {contextTitle(show.operating_context)}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{zar(show.budget_approved)}</td>
                  <td className="px-4 py-3 text-gray-600">{zar(show.revenue_target)}</td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/programming/shows/${show.id}`}
                      className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-800"
                    >
                      View Lifecycle <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  );
}

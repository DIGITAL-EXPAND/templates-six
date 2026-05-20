'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchShareholderCompacts, fetchCompactProgress } from '@/lib/api/endpoints';
import type { ShareholderCompact, CompactTarget, FundingTranche } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function zar(val: string | number) {
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function compactStatusTone(status: string): StatusTone {
  switch (status) {
    case 'draft': return 'neutral';
    case 'submitted': return 'info';
    case 'agreed': return 'good';
    case 'in_progress': return 'info';
    case 'under_review': return 'warning';
    case 'closed': return 'neutral';
    default: return 'neutral';
  }
}

function ragTone(pct: number): StatusTone {
  if (pct >= 90) return 'good';
  if (pct >= 60) return 'warning';
  return 'danger';
}

function latestActual(target: CompactTarget): string | null {
  if (!target.actuals || target.actuals.length === 0) return null;
  const sorted = [...target.actuals].sort((a, b) => b.quarter - a.quarter);
  return sorted[0].actual_value;
}

type ProgressData = { targets: (CompactTarget & { achievement_pct: number })[] };

export default function ShareholderCompactPage() {
  const { tokens } = useAuth();
  const [compacts, setCompacts] = useState<ShareholderCompact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [progressMap, setProgressMap] = useState<Record<string, ProgressData>>({});
  const [progressLoading, setProgressLoading] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!tokens?.access) return;
    fetchShareholderCompacts(tokens.access)
      .then((res) => setCompacts(res.results))
      .catch(() => setError('Failed to load shareholder compacts'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  async function toggleProgress(compact: ShareholderCompact) {
    if (expandedId === compact.id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(compact.id);
    if (!progressMap[compact.id] && tokens?.access) {
      setProgressLoading((prev) => ({ ...prev, [compact.id]: true }));
      try {
        const data = await fetchCompactProgress(tokens.access, compact.id);
        setProgressMap((prev) => ({ ...prev, [compact.id]: data }));
      } catch {
        // keep expanded but show no data
      } finally {
        setProgressLoading((prev) => ({ ...prev, [compact.id]: false }));
      }
    }
  }

  if (loading) return <AppShell><LoadingState label="Loading shareholder compacts…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  return (
    <AppShell>
      <PageHeader title="Shareholder Compact" />
      {compacts.length === 0 ? (
        <EmptyState title="No shareholder compacts found." />
      ) : (
        <div className="space-y-4 p-4">
          {compacts.map((compact) => {
            const isExpanded = expandedId === compact.id;
            const progress = progressMap[compact.id];
            const isLoadingProgress = progressLoading[compact.id];
            const tranches = compact.tranches ?? [];
            const receivedCount = tranches.filter((t) => t.is_received).length;

            return (
              <div key={compact.id} className="rounded-lg border border-gray-200 bg-white shadow-sm">
                <div className="p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 flex-wrap">
                        <h2 className="text-lg font-semibold text-gray-900">
                          FY {compact.financial_year}
                        </h2>
                        <StatusBadge tone={compactStatusTone(compact.status)}>
                          {compact.status.replace(/_/g, ' ')}
                        </StatusBadge>
                      </div>
                      <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-sm text-gray-600">
                        <div>
                          <span className="font-medium text-gray-700">Executive Authority: </span>
                          {compact.executive_authority || '—'}
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Grant Allocation: </span>
                          {zar(compact.total_grant_allocation)}
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Signed: </span>
                          {compact.signed_date ?? 'Not yet signed'}
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Tranches: </span>
                          {receivedCount}/{tranches.length} received
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => toggleProgress(compact)}
                      className="shrink-0 rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
                    >
                      {isExpanded ? 'Hide Progress' : 'View Progress'}
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="border-t border-gray-100 p-5">
                    {isLoadingProgress ? (
                      <LoadingState label="Loading progress data…" />
                    ) : (
                      <div className="space-y-6">
                        {/* Targets / KPI Progress */}
                        <div>
                          <h3 className="text-sm font-semibold text-gray-800 mb-3">Performance Targets</h3>
                          {progress && progress.targets.length > 0 ? (
                            <div className="overflow-x-auto">
                              <table className="min-w-full text-sm">
                                <thead>
                                  <tr className="border-b border-gray-200 text-left text-xs text-gray-500 uppercase tracking-wider">
                                    <th className="pb-2 pr-4">Indicator</th>
                                    <th className="pb-2 pr-4">Category</th>
                                    <th className="pb-2 pr-4">Target</th>
                                    <th className="pb-2 pr-4">Latest Actual</th>
                                    <th className="pb-2 pr-4">Weight %</th>
                                    <th className="pb-2">Achievement</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                  {progress.targets.map((t) => {
                                    const actual = latestActual(t);
                                    return (
                                      <tr key={t.id} className="py-2">
                                        <td className="py-2 pr-4 font-medium text-gray-900">{t.indicator_name}</td>
                                        <td className="py-2 pr-4">
                                          <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700">
                                            {t.category}
                                          </span>
                                        </td>
                                        <td className="py-2 pr-4 text-gray-600">{t.target_value} {t.unit}</td>
                                        <td className="py-2 pr-4 text-gray-600">
                                          {actual !== null
                                            ? `${actual} ${t.unit}`
                                            : <span className="text-gray-400 italic">Not reported</span>}
                                        </td>
                                        <td className="py-2 pr-4 text-gray-600">{t.weight_percent}%</td>
                                        <td className="py-2">
                                          <StatusBadge tone={ragTone(t.achievement_pct)}>
                                            {t.achievement_pct.toFixed(0)}%
                                          </StatusBadge>
                                        </td>
                                      </tr>
                                    );
                                  })}
                                </tbody>
                              </table>
                            </div>
                          ) : (
                            <p className="text-sm text-gray-500 italic">No target data available.</p>
                          )}
                        </div>

                        {/* Funding Tranches */}
                        <div>
                          <h3 className="text-sm font-semibold text-gray-800 mb-3">Funding Tranches</h3>
                          {tranches.length > 0 ? (
                            <div className="overflow-x-auto">
                              <table className="min-w-full text-sm">
                                <thead>
                                  <tr className="border-b border-gray-200 text-left text-xs text-gray-500 uppercase tracking-wider">
                                    <th className="pb-2 pr-4">#</th>
                                    <th className="pb-2 pr-4">Description</th>
                                    <th className="pb-2 pr-4">Amount</th>
                                    <th className="pb-2 pr-4">Due Date</th>
                                    <th className="pb-2">Status</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                  {tranches.map((tranche) => (
                                    <tr key={tranche.id} className="py-2">
                                      <td className="py-2 pr-4 text-gray-600">{tranche.tranche_number}</td>
                                      <td className="py-2 pr-4 text-gray-900">{tranche.description || '—'}</td>
                                      <td className="py-2 pr-4 font-medium text-gray-900">{zar(tranche.amount)}</td>
                                      <td className="py-2 pr-4 text-gray-600">{tranche.due_date}</td>
                                      <td className="py-2">
                                        <StatusBadge tone={tranche.is_received ? 'good' : 'warning'}>
                                          {tranche.is_received ? 'Received' : 'Pending'}
                                        </StatusBadge>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          ) : (
                            <p className="text-sm text-gray-500 italic">No tranches defined.</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}

'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { useAuth } from '@/lib/auth/auth-provider';
import { fetchSection32Reports, submitSection32Report } from '@/lib/api/endpoints';
import type { Section32Report } from '@/lib/api/types';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function zar(val: string | number) {
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function statusTone(status: string): StatusTone {
  switch (status) {
    case 'draft': return 'neutral';
    case 'reviewed': return 'info';
    case 'submitted': return 'warning';
    case 'acknowledged': return 'good';
    default: return 'neutral';
  }
}

function achievementTone(pct: number): StatusTone {
  if (pct >= 90) return 'good';
  if (pct >= 60) return 'warning';
  return 'danger';
}

function achievementPct(actual: string, budget: string): number {
  const b = parseFloat(budget);
  if (!b) return 0;
  return Math.round((parseFloat(actual) / b) * 100);
}

export default function Section32Page() {
  const { tokens } = useAuth();
  const [reports, setReports] = useState<Section32Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<string | null>(null);

  const token = tokens?.access ?? '';

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetchSection32Reports(token)
      .then((d) => setReports(d.results))
      .catch(() => setError('Failed to load Section 32 reports'))
      .finally(() => setLoading(false));
  }, [token]);

  async function handleSubmit(id: string) {
    if (!token) return;
    setSubmitting(id);
    try {
      const updated = await submitSection32Report(token, id);
      setReports((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
    } catch {
      // silent
    } finally {
      setSubmitting(null);
    }
  }

  // Group by financial year
  const byYear: Record<string, Section32Report[]> = {};
  for (const r of reports) {
    if (!byYear[r.financial_year]) byYear[r.financial_year] = [];
    byYear[r.financial_year].push(r);
  }

  return (
    <AppShell>
      <PageHeader
        title="Section 32 Reports"
        description="Monthly financial reports to National Treasury (PFMA s.32)"
      />

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}
      {!loading && !error && reports.length === 0 && (
        <EmptyState title="No Section 32 reports found." />
      )}

      {!loading && !error && Object.entries(byYear).sort(([a], [b]) => b.localeCompare(a)).map(([year, yearReports]) => (
        <div key={year} className="mb-8">
          <h2 className="text-base font-semibold text-gray-800 mb-3">{year}</h2>
          <div className="space-y-3">
            {yearReports.sort((a, b) => b.month - a.month).map((report) => {
              const revPct = achievementPct(report.total_revenue_actual, report.total_revenue_budget);
              const expPct = achievementPct(report.total_expenditure_actual, report.total_expenditure_budget);
              const isOpen = expanded === report.id;
              const canSubmit = report.status === 'draft' || report.status === 'reviewed';

              return (
                <div key={report.id} className="bg-white rounded-lg border border-gray-200">
                  <button
                    className="w-full flex items-start gap-4 p-4 text-left hover:bg-gray-50 rounded-lg"
                    onClick={() => setExpanded(isOpen ? null : report.id)}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-2">
                        <span className="font-semibold text-gray-900">
                          {MONTH_NAMES[(report.month - 1) % 12]} — Period end {formatDate(report.reporting_period_end)}
                        </span>
                        <StatusBadge tone={statusTone(report.status)}>
                          {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                        </StatusBadge>
                        {report.treasury_reference && (
                          <span className="text-xs text-gray-500">Ref: {report.treasury_reference}</span>
                        )}
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                        <div>
                          <div className="text-gray-500 text-xs mb-0.5">Revenue</div>
                          <div className="flex items-center gap-2">
                            <span>{zar(report.total_revenue_actual)} / {zar(report.total_revenue_budget)}</span>
                            <StatusBadge tone={achievementTone(revPct)}>{revPct}%</StatusBadge>
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-500 text-xs mb-0.5">Expenditure</div>
                          <div className="flex items-center gap-2">
                            <span>{zar(report.total_expenditure_actual)} / {zar(report.total_expenditure_budget)}</span>
                            <StatusBadge tone={achievementTone(expPct)}>{expPct}%</StatusBadge>
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-500 text-xs mb-0.5">IUFW YTD</div>
                          <span className="font-mono text-sm">
                            {zar(parseFloat(report.fruitless_wasteful_ytd || '0') + parseFloat(report.irregular_ytd || '0'))}
                          </span>
                        </div>
                      </div>
                    </div>
                    {canSubmit && (
                      <button
                        onClick={(e) => { e.stopPropagation(); handleSubmit(report.id); }}
                        disabled={submitting === report.id}
                        className="shrink-0 px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
                      >
                        {submitting === report.id ? 'Submitting…' : 'Submit to Treasury'}
                      </button>
                    )}
                  </button>

                  {isOpen && report.programme_lines && report.programme_lines.length > 0 && (
                    <div className="border-t border-gray-100 px-4 pb-4">
                      <h3 className="text-sm font-semibold text-gray-700 mt-3 mb-2">Programme Lines</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="text-left text-gray-500 border-b border-gray-200">
                              <th className="pb-1.5 pr-3">Programme</th>
                              <th className="pb-1.5 pr-3 text-right">Budget</th>
                              <th className="pb-1.5 pr-3 text-right">YTD Spend</th>
                              <th className="pb-1.5 pr-3 text-right">This Month</th>
                              <th className="pb-1.5 pr-3 text-right">Variance</th>
                              <th className="pb-1.5">Explanation</th>
                            </tr>
                          </thead>
                          <tbody>
                            {report.programme_lines.map((line) => {
                              const variance = parseFloat(line.variance);
                              return (
                                <tr key={line.id} className="border-b border-gray-100 hover:bg-gray-50">
                                  <td className="py-1.5 pr-3 font-medium">{line.programme_name}</td>
                                  <td className="py-1.5 pr-3 text-right font-mono">{zar(line.budget_allocation)}</td>
                                  <td className="py-1.5 pr-3 text-right font-mono">{zar(line.expenditure_ytd)}</td>
                                  <td className="py-1.5 pr-3 text-right font-mono">{zar(line.expenditure_this_month)}</td>
                                  <td className={`py-1.5 pr-3 text-right font-mono ${variance < 0 ? 'text-red-600' : 'text-green-700'}`}>
                                    {zar(line.variance)}
                                  </td>
                                  <td className="py-1.5 text-xs text-gray-500">{line.variance_explanation || '—'}</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                  {isOpen && (!report.programme_lines || report.programme_lines.length === 0) && (
                    <div className="border-t border-gray-100 px-4 py-3 text-sm text-gray-500">
                      No programme lines recorded.
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </AppShell>
  );
}

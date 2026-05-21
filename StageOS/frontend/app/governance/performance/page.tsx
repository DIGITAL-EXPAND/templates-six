'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchPerformanceReports, submitPerformanceReport } from '@/lib/api/endpoints';
import type { PerformanceReport } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function reportStatusTone(status: string): StatusTone {
  switch (status) {
    case 'draft': return 'neutral';
    case 'submitted': return 'info';
    case 'reviewed': return 'warning';
    case 'approved': return 'good';
    case 'published': return 'good';
    default: return 'neutral';
  }
}

function groupByCompact(reports: PerformanceReport[]): Record<string, PerformanceReport[]> {
  const groups: Record<string, PerformanceReport[]> = {};
  for (const r of reports) {
    if (!groups[r.compact]) groups[r.compact] = [];
    groups[r.compact].push(r);
  }
  return groups;
}

export default function PerformancePage() {
  const { tokens } = useAuth();
  const [reports, setReports] = useState<PerformanceReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [submittingId, setSubmittingId] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchPerformanceReports(tokens.access)
      .then((res) => setReports(res.results))
      .catch(() => setError('Failed to load performance reports'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  async function handleSubmit(reportId: string) {
    if (!tokens?.access) return;
    setSubmittingId(reportId);
    try {
      const updated = await submitPerformanceReport(tokens.access, reportId);
      setReports((prev) => prev.map((r) => (r.id === reportId ? updated : r)));
    } catch {
      // silently fail — user can retry
    } finally {
      setSubmittingId(null);
    }
  }

  function toggleExpand(id: string) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  if (loading) return <AppShell><LoadingState label="Loading performance reports…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  if (reports.length === 0) {
    return (
      <AppShell>
        <PageHeader
          title="Performance Information"
          description="Quarterly performance reports against Shareholder Compact"
        />
        <div className="px-4">
          <EmptyState title="No performance reports found." description="Performance reports are created when a Shareholder Compact is active." />
        </div>
      </AppShell>
    );
  }

  const groups = groupByCompact(reports);

  return (
    <AppShell>
      <PageHeader
        title="Performance Information"
        description="Quarterly performance reports against Shareholder Compact"
      />

      <div className="px-4 pb-8 space-y-8">
        {Object.entries(groups).map(([compact, compactReports]) => (
          <div key={compact}>
            <h2 className="text-base font-semibold text-gray-700 mb-3 border-b border-gray-200 pb-2">
              Financial Year: {compact}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {([1, 2, 3, 4] as const).map((quarter) => {
                const report = compactReports.find((r) => r.quarter === quarter);
                if (!report) {
                  return (
                    <div
                      key={quarter}
                      className="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-4"
                    >
                      <div className="text-sm font-semibold text-gray-400">Q{quarter} — No Report</div>
                    </div>
                  );
                }
                const isExpanded = expandedId === report.id;
                return (
                  <div key={report.id} className="rounded-lg border border-gray-200 bg-white shadow-sm">
                    <button
                      type="button"
                      onClick={() => toggleExpand(report.id)}
                      className="w-full text-left p-4 hover:bg-gray-50 transition-colors rounded-t-lg"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-gray-900">Q{report.quarter}</span>
                        <StatusBadge tone={reportStatusTone(report.status)}>
                          {report.status}
                        </StatusBadge>
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatDate(report.reporting_period_start)} – {formatDate(report.reporting_period_end)}
                      </div>
                    </button>
                    <div className="px-4 pb-4 flex items-center gap-3">
                      {report.status === 'draft' && (
                        <button
                          type="button"
                          onClick={() => handleSubmit(report.id)}
                          disabled={submittingId === report.id}
                          className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
                        >
                          {submittingId === report.id ? 'Submitting…' : 'Submit Report'}
                        </button>
                      )}
                    </div>
                    {isExpanded && (
                      <div className="border-t border-gray-100 px-4 pb-4 space-y-3 pt-3">
                        {report.executive_summary && (
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1">Executive Summary</div>
                            <p className="text-sm text-gray-800 whitespace-pre-line">{report.executive_summary}</p>
                          </div>
                        )}
                        {report.key_achievements && (
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1">Key Achievements</div>
                            <p className="text-sm text-gray-800 whitespace-pre-line">{report.key_achievements}</p>
                          </div>
                        )}
                        {report.challenges && (
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1">Challenges</div>
                            <p className="text-sm text-gray-800 whitespace-pre-line">{report.challenges}</p>
                          </div>
                        )}
                        {report.corrective_actions && (
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1">Corrective Actions</div>
                            <p className="text-sm text-gray-800 whitespace-pre-line">{report.corrective_actions}</p>
                          </div>
                        )}
                        <div className="flex gap-6 text-xs text-gray-400 pt-1">
                          {report.submitted_date && (
                            <span>Submitted: {formatDate(report.submitted_date)}</span>
                          )}
                          {report.approved_date && (
                            <span>Approved: {formatDate(report.approved_date)}</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </AppShell>
  );
}

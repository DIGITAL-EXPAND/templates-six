'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { useAuth } from '@/lib/auth/auth-provider';
import { fetchAnnualReports, approveAnnualReport } from '@/lib/api/endpoints';
import type { AnnualReport } from '@/lib/api/types';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function reportStatusTone(status: string): StatusTone {
  switch (status) {
    case 'planning': return 'neutral';
    case 'drafting': return 'info';
    case 'review': return 'warning';
    case 'board_approval': return 'warning';
    case 'approved': return 'good';
    case 'submitted': return 'info';
    case 'published': return 'good';
    default: return 'neutral';
  }
}

function sectionStatusTone(status: string): StatusTone {
  switch (status) {
    case 'not_started': return 'neutral';
    case 'in_progress': return 'info';
    case 'draft_complete': return 'warning';
    case 'reviewed': return 'info';
    case 'approved': return 'good';
    default: return 'neutral';
  }
}

function auditOutcomeTone(outcome: string): StatusTone {
  switch (outcome) {
    case 'clean': return 'good';
    case 'unqualified_emphasis': return 'info';
    case 'qualified':
    case 'adverse':
    case 'disclaimer': return 'danger';
    default: return 'neutral';
  }
}

function auditOutcomeLabel(outcome: string): string {
  switch (outcome) {
    case 'clean': return 'Clean';
    case 'unqualified_emphasis': return 'Unqualified (Emphasis)';
    case 'qualified': return 'Qualified';
    case 'adverse': return 'Adverse';
    case 'disclaimer': return 'Disclaimer';
    default: return outcome || '—';
  }
}

export default function AnnualReportPage() {
  const { tokens } = useAuth();
  const [reports, setReports] = useState<AnnualReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [approving, setApproving] = useState<string | null>(null);

  const token = tokens?.access ?? '';

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetchAnnualReports(token)
      .then((d) => setReports(d.results))
      .catch(() => setError('Failed to load annual reports'))
      .finally(() => setLoading(false));
  }, [token]);

  async function handleApprove(id: string) {
    if (!token) return;
    setApproving(id);
    try {
      const updated = await approveAnnualReport(token, id);
      setReports((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
    } catch {
      // silent
    } finally {
      setApproving(null);
    }
  }

  return (
    <AppShell>
      <PageHeader
        title="Annual Report"
        description="Compilation workflow for the Annual Report to Parliament"
      />

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}
      {!loading && !error && reports.length === 0 && (
        <EmptyState title="No annual reports found." />
      )}

      {!loading && !error && (
        <div className="space-y-4">
          {reports.sort((a, b) => b.financial_year.localeCompare(a.financial_year)).map((report) => {
            const isOpen = expanded === report.id;
            const progressPct = report.sections_total_count > 0
              ? Math.round((report.sections_complete_count / report.sections_total_count) * 100)
              : 0;

            return (
              <div key={report.id} className="bg-white rounded-lg border border-gray-200">
                <button
                  className="w-full flex items-start gap-4 p-4 text-left hover:bg-gray-50 rounded-lg"
                  onClick={() => setExpanded(isOpen ? null : report.id)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-2">
                      <span className="text-base font-semibold text-gray-900">
                        Annual Report {report.financial_year}
                      </span>
                      <StatusBadge tone={reportStatusTone(report.status)}>
                        {report.status.replace(/_/g, ' ')}
                      </StatusBadge>
                      {report.overall_audit_outcome && (
                        <StatusBadge tone={auditOutcomeTone(report.overall_audit_outcome)}>
                          {auditOutcomeLabel(report.overall_audit_outcome)}
                        </StatusBadge>
                      )}
                    </div>
                    {report.theme && (
                      <p className="text-sm text-gray-600 italic mb-2">&ldquo;{report.theme}&rdquo;</p>
                    )}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm mb-3">
                      <div>
                        <span className="text-gray-500 text-xs">Tabling Date</span>
                        <div>{formatDate(report.tabling_date)}</div>
                      </div>
                      <div>
                        <span className="text-gray-500 text-xs">Board Approved</span>
                        <div>{formatDate(report.approved_by_board_date)}</div>
                      </div>
                      <div>
                        <span className="text-gray-500 text-xs">Published</span>
                        <div>{formatDate(report.publication_date)}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-48">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all"
                          style={{ width: `${progressPct}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">
                        {report.sections_complete_count}/{report.sections_total_count} sections complete ({progressPct}%)
                      </span>
                    </div>
                  </div>
                  {report.status === 'board_approval' && (
                    <button
                      onClick={(e) => { e.stopPropagation(); handleApprove(report.id); }}
                      disabled={approving === report.id}
                      className="shrink-0 px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
                    >
                      {approving === report.id ? 'Approving…' : 'Approve Report'}
                    </button>
                  )}
                </button>

                {isOpen && (
                  <div className="border-t border-gray-100 px-4 pb-4">
                    <h3 className="text-sm font-semibold text-gray-700 mt-3 mb-2">Sections</h3>
                    {report.sections && report.sections.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="text-left text-gray-500 border-b border-gray-200">
                              <th className="pb-1.5 pr-3">Title</th>
                              <th className="pb-1.5 pr-3">Status</th>
                              <th className="pb-1.5 pr-3">Due Date</th>
                              <th className="pb-1.5 pr-3 text-right">Words</th>
                              <th className="pb-1.5">Reviewer Notes</th>
                            </tr>
                          </thead>
                          <tbody>
                            {[...report.sections].sort((a, b) => a.order - b.order).map((section) => (
                              <tr key={section.id} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-1.5 pr-3 font-medium">{section.title}</td>
                                <td className="py-1.5 pr-3">
                                  <StatusBadge tone={sectionStatusTone(section.status)}>
                                    {section.status.replace(/_/g, ' ')}
                                  </StatusBadge>
                                </td>
                                <td className="py-1.5 pr-3 text-gray-600">{formatDate(section.due_date)}</td>
                                <td className="py-1.5 pr-3 text-right font-mono">{section.word_count.toLocaleString()}</td>
                                <td className="py-1.5 text-xs text-gray-500 max-w-48 truncate">
                                  {section.reviewer_notes || '—'}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">No sections defined yet.</p>
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

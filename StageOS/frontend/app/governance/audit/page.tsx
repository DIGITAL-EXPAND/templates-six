'use client';
// Shows AG audit requests list and evidence tracker
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchAGAuditRequests, fetchAGAuditEvidence } from '@/lib/api/endpoints';
import type { AGAuditRequest, AGAuditEvidence } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function auditStatusTone(status: string): StatusTone {
  switch (status) {
    case 'notice_received': return 'info';
    case 'preparation':
    case 'fieldwork':
    case 'management_comments':
    case 'draft_report': return 'warning';
    case 'final_report': return 'info';
    case 'closed': return 'good';
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

function EvidenceRow({ auditId, token }: { auditId: string; token: string }) {
  const [evidence, setEvidence] = useState<AGAuditEvidence[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchAGAuditEvidence(token, auditId)
      .then(setEvidence)
      .catch(() => setError(true));
  }, [auditId, token]);

  if (error) {
    return (
      <tr>
        <td colSpan={6} className="px-4 py-3 text-sm text-red-600 bg-red-50">
          Failed to load evidence items.
        </td>
      </tr>
    );
  }

  if (evidence === null) {
    return (
      <tr>
        <td colSpan={6} className="px-4 py-3 text-sm text-gray-500 bg-gray-50">
          Loading evidence…
        </td>
      </tr>
    );
  }

  if (evidence.length === 0) {
    return (
      <tr>
        <td colSpan={6} className="px-4 py-3 text-sm text-gray-500 bg-gray-50 italic">
          No evidence items recorded.
        </td>
      </tr>
    );
  }

  return (
    <>
      <tr>
        <td colSpan={6} className="bg-gray-50 px-4 pt-2 pb-0">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-200">
                <th className="py-1 pr-3 font-medium">Category</th>
                <th className="py-1 pr-3 font-medium">Description</th>
                <th className="py-1 pr-3 font-medium">Document Ref</th>
                <th className="py-1 pr-3 font-medium">AG Query Ref</th>
                <th className="py-1 pr-3 font-medium">Provided</th>
                <th className="py-1 font-medium">Provided Date</th>
              </tr>
            </thead>
            <tbody>
              {evidence.map((ev) => (
                <tr key={ev.id} className="border-b border-gray-100 last:border-0">
                  <td className="py-1 pr-3 text-gray-700">{ev.category || '—'}</td>
                  <td className="py-1 pr-3 text-gray-700 max-w-xs truncate">{ev.description || '—'}</td>
                  <td className="py-1 pr-3 text-gray-600 font-mono">{ev.document_reference || '—'}</td>
                  <td className="py-1 pr-3 text-gray-600 font-mono">{ev.ag_query_ref || '—'}</td>
                  <td className="py-1 pr-3">
                    <StatusBadge tone={ev.is_provided ? 'good' : 'neutral'}>
                      {ev.is_provided ? 'Yes' : 'No'}
                    </StatusBadge>
                  </td>
                  <td className="py-1 text-gray-600">{formatDate(ev.provided_date)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </td>
      </tr>
    </>
  );
}

export default function AGAuditPage() {
  const { tokens } = useAuth();
  const [audits, setAudits] = useState<AGAuditRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchAGAuditRequests(tokens.access)
      .then((data) => setAudits(data.results))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  const totalAudits = audits.length;
  const cleanAudits = audits.filter((a) => a.audit_outcome === 'clean').length;
  const qualifiedAdverse = audits.filter((a) =>
    ['qualified', 'adverse', 'disclaimer'].includes(a.audit_outcome),
  ).length;
  const evidenceProvided = audits.reduce((sum, a) => {
    return sum + (a.evidence_items?.filter((e) => e.is_provided).length ?? 0);
  }, 0);

  return (
    <AppShell>
      <PageHeader
        title="AG Audit Support"
        description="Auditor-General audit management and evidence tracking"
      />

      {/* Summary strip */}
      <div className="grid grid-cols-2 gap-4 mb-6 sm:grid-cols-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Total Audits</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">{totalAudits}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Clean Audits</p>
          <p className="mt-1 text-2xl font-semibold text-green-600">{cleanAudits}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Qualified / Adverse</p>
          <p className="mt-1 text-2xl font-semibold text-red-600">{qualifiedAdverse}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Evidence Items Provided</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900">{evidenceProvided}</p>
        </div>
      </div>

      {loading && <LoadingState label="Loading audit requests…" />}
      {error && <ErrorState message="Failed to load AG audit requests." />}
      {!loading && !error && audits.length === 0 && (
        <EmptyState
          title="No audit requests"
          description="No Auditor-General audit requests have been recorded yet."
        />
      )}

      {!loading && !error && audits.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr className="text-left text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-3 font-medium">Financial Year</th>
                <th className="px-4 py-3 font-medium">Audit Type</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Outcome</th>
                <th className="px-4 py-3 font-medium">Notice Date</th>
                <th className="px-4 py-3 font-medium">Final Report</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {audits.map((audit) => (
                <>
                  <tr key={audit.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-gray-900">{audit.financial_year}</td>
                    <td className="px-4 py-3 text-gray-700 capitalize">{audit.audit_type.replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={auditStatusTone(audit.status)}>
                        {audit.status.replace(/_/g, ' ')}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={auditOutcomeTone(audit.audit_outcome)}>
                        {auditOutcomeLabel(audit.audit_outcome)}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{formatDate(audit.notice_date)}</td>
                    <td className="px-4 py-3 text-gray-600">{formatDate(audit.final_report_date)}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() =>
                          setExpandedId(expandedId === audit.id ? null : audit.id)
                        }
                        className="text-xs text-blue-600 hover:text-blue-800 underline"
                      >
                        {expandedId === audit.id ? 'Hide Evidence' : 'View Evidence'}
                      </button>
                    </td>
                  </tr>
                  {expandedId === audit.id && tokens?.access && (
                    <EvidenceRow key={`ev-${audit.id}`} auditId={audit.id} token={tokens.access} />
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  );
}

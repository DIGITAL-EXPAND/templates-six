'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchLiquorLicences, fetchSafetyRecords } from '@/lib/api/endpoints';
import type { LiquorLicence, SafetyComplianceRecord } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function formatZAR(val: string | null | undefined) {
  if (!val) return '—';
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function liquorStatusTone(status: string): StatusTone {
  switch (status) {
    case 'active':
    case 'approved': return 'good';
    case 'renewal_due': return 'warning';
    case 'expired':
    case 'suspended': return 'danger';
    case 'applied': return 'info';
    case 'required': return 'danger';
    case 'not_applicable': return 'neutral';
    default: return 'neutral';
  }
}

export default function SafetyPage() {
  const { tokens } = useAuth();
  const [licences, setLicences] = useState<LiquorLicence[]>([]);
  const [safetyRecords, setSafetyRecords] = useState<SafetyComplianceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.all([
      fetchLiquorLicences(tokens.access).then((res) => setLicences(res.results)),
      fetchSafetyRecords(tokens.access).then((res) => setSafetyRecords(res.results)),
    ])
      .catch(() => setError('Failed to load compliance data'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  if (loading) return <AppShell><LoadingState label="Loading compliance data…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  return (
    <AppShell>
      <PageHeader
        title="Safety & Compliance"
        description="Liquor licences, fire certificates, OHS and crowd management"
      />

      {/* Liquor Licences */}
      <div className="px-4 pb-6">
        <h2 className="text-base font-semibold text-gray-900 mb-3">Liquor Licences</h2>
        {licences.length === 0 ? (
          <EmptyState title="No liquor licences." description="No liquor licence records found." />
        ) : (
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">Venue</th>
                  <th className="px-4 py-3">Licence Number</th>
                  <th className="px-4 py-3">Holder</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Issue Date</th>
                  <th className="px-4 py-3">Expiry Date</th>
                  <th className="px-4 py-3">Annual Fee</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {licences.map((lic) => (
                  <tr key={lic.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-gray-900">{lic.venue_name ?? lic.venue}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">{lic.licence_number || '—'}</td>
                    <td className="px-4 py-3 text-gray-700">{lic.licence_holder || '—'}</td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={liquorStatusTone(lic.status)}>
                        {lic.status.replace(/_/g, ' ')}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-gray-600">{formatDate(lic.issue_date)}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-gray-600">{formatDate(lic.expiry_date)}</td>
                    <td className="px-4 py-3 text-gray-700">{formatZAR(lic.annual_fee)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Safety Compliance Records */}
      <div className="px-4 pb-8">
        <h2 className="text-base font-semibold text-gray-900 mb-3">Safety Compliance Records</h2>
        {safetyRecords.length === 0 ? (
          <EmptyState title="No safety records." description="No safety compliance records found." />
        ) : (
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Venue / Production</th>
                  <th className="px-4 py-3">Compliant</th>
                  <th className="px-4 py-3">Certificate #</th>
                  <th className="px-4 py-3">Issue Date</th>
                  <th className="px-4 py-3">Expiry Date</th>
                  <th className="px-4 py-3">Issuing Body</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {safetyRecords.map((rec) => (
                  <tr
                    key={rec.id}
                    className={`hover:bg-gray-50 transition-colors ${rec.is_compliant ? 'border-l-4 border-green-400' : 'border-l-4 border-red-400'}`}
                  >
                    <td className="px-4 py-3 font-medium text-gray-900 capitalize">
                      {rec.compliance_type.replace(/_/g, ' ')}
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {rec.venue ?? rec.operating_context ?? '—'}
                    </td>
                    <td className="px-4 py-3 text-lg">
                      {rec.is_compliant ? (
                        <span className="text-green-600">✓</span>
                      ) : (
                        <span className="text-red-600">✗</span>
                      )}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">{rec.certificate_number || '—'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-gray-600">{formatDate(rec.issue_date)}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-gray-600">{formatDate(rec.expiry_date)}</td>
                    <td className="px-4 py-3 text-gray-700">{rec.issuing_body || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppShell>
  );
}

'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchCSDVerifications } from '@/lib/api/endpoints';
import type { SupplierCSDVerification } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function csdStatusTone(status: string): StatusTone {
  switch (status) {
    case 'not_verified':
    case 'pending': return 'warning';
    case 'verified': return 'good';
    case 'failed':
    case 'expired':
    case 'excluded': return 'danger';
    default: return 'neutral';
  }
}

function taxComplianceTone(status: string): StatusTone {
  switch (status) {
    case 'compliant': return 'good';
    case 'non_compliant': return 'danger';
    default: return 'neutral';
  }
}

export default function CSDRegisterPage() {
  const { tokens } = useAuth();
  const [verifications, setVerifications] = useState<SupplierCSDVerification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchCSDVerifications(tokens.access)
      .then((data) => setVerifications(data.results))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  const verified = verifications.filter((v) => v.verification_status === 'verified').length;
  const notVerifiedOrPending = verifications.filter((v) =>
    ['not_verified', 'pending'].includes(v.verification_status),
  ).length;
  const failedExcluded = verifications.filter((v) =>
    ['failed', 'expired', 'excluded'].includes(v.verification_status),
  ).length;

  return (
    <AppShell>
      <PageHeader
        title="CSD Verification Register"
        description="Central Supplier Database verification status for all suppliers"
      />

      {/* Summary strip */}
      <div className="grid grid-cols-1 gap-4 mb-6 sm:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Verified</p>
          <p className="mt-1 text-2xl font-semibold text-green-600">{verified}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Not Verified / Pending</p>
          <p className="mt-1 text-2xl font-semibold text-yellow-600">{notVerifiedOrPending}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Failed / Excluded</p>
          <p className="mt-1 text-2xl font-semibold text-red-600">{failedExcluded}</p>
        </div>
      </div>

      {loading && <LoadingState label="Loading CSD verifications…" />}
      {error && <ErrorState message="Failed to load CSD verification register." />}
      {!loading && !error && verifications.length === 0 && (
        <EmptyState
          title="No verifications"
          description="No CSD verifications have been recorded yet."
        />
      )}

      {!loading && !error && verifications.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr className="text-left text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-3 font-medium">Supplier ID</th>
                <th className="px-4 py-3 font-medium">CSD Number</th>
                <th className="px-4 py-3 font-medium">Verification Status</th>
                <th className="px-4 py-3 font-medium">Tax Compliance</th>
                <th className="px-4 py-3 font-medium">Tax Clearance Expiry</th>
                <th className="px-4 py-3 font-medium">B-BBEE Level</th>
                <th className="px-4 py-3 font-medium">B-BBEE Expiry</th>
                <th className="px-4 py-3 font-medium">Blacklisted</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {verifications.map((v) => (
                <tr key={v.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-gray-600">
                    {v.supplier ? v.supplier.slice(0, 8) + '…' : '—'}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-700">
                    {v.csd_supplier_number || '—'}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge tone={csdStatusTone(v.verification_status)}>
                      {v.verification_status.replace(/_/g, ' ')}
                    </StatusBadge>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge tone={taxComplianceTone(v.tax_compliance_status)}>
                      {v.tax_compliance_status.replace(/_/g, ' ')}
                    </StatusBadge>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{formatDate(v.tax_clearance_expiry)}</td>
                  <td className="px-4 py-3 text-gray-700 text-center">
                    {v.bee_level != null ? `Level ${v.bee_level}` : '—'}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{formatDate(v.bee_certificate_expiry)}</td>
                  <td className="px-4 py-3 text-center">
                    {v.is_blacklisted ? (
                      <span className="text-red-600 font-bold text-base" title={v.blacklist_reason}>✗</span>
                    ) : (
                      <span className="text-green-600 font-bold text-base">✓</span>
                    )}
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

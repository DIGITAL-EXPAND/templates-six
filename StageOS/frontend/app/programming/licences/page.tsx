'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchProductionLicences } from '@/lib/api/endpoints';
import type { ProductionLicence } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function zar(val: string | null | undefined): string {
  if (!val) return '—';
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function licensingBodyTone(body: string): StatusTone {
  switch (body) {
    case 'samro': return 'info';
    case 'risa': return 'warning';
    case 'capasso': return 'good';
    case 'dalro':
    case 'filmsa':
    case 'other':
    default: return 'neutral';
  }
}

function licenceStatusTone(status: string): StatusTone {
  switch (status) {
    case 'not_required': return 'neutral';
    case 'required': return 'danger';
    case 'applied': return 'info';
    case 'approved':
    case 'paid':
    case 'received': return 'good';
    case 'expired':
    case 'rejected': return 'danger';
    default: return 'neutral';
  }
}

export default function ProductionLicencesPage() {
  const { tokens } = useAuth();
  const [licences, setLicences] = useState<ProductionLicence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchProductionLicences(tokens.access)
      .then((data) => setLicences(data.results))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  const required = licences.filter((l) => l.status === 'required').length;
  const applied = licences.filter((l) => l.status === 'applied').length;
  const approved = licences.filter((l) =>
    ['approved', 'paid', 'received'].includes(l.status),
  ).length;
  const expiredRejected = licences.filter((l) =>
    ['expired', 'rejected'].includes(l.status),
  ).length;

  return (
    <AppShell>
      <PageHeader
        title="Production Licences"
        description="SAMRO, RISA, CAPASSO and other IP licensing"
      />

      {/* Summary strip */}
      <div className="grid grid-cols-2 gap-4 mb-6 sm:grid-cols-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Required</p>
          <p className="mt-1 text-2xl font-semibold text-yellow-600">{required}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Applied</p>
          <p className="mt-1 text-2xl font-semibold text-blue-600">{applied}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Approved / Paid / Received</p>
          <p className="mt-1 text-2xl font-semibold text-green-600">{approved}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Expired / Rejected</p>
          <p className="mt-1 text-2xl font-semibold text-red-600">{expiredRejected}</p>
        </div>
      </div>

      {loading && <LoadingState label="Loading production licences…" />}
      {error && <ErrorState message="Failed to load production licences." />}
      {!loading && !error && licences.length === 0 && (
        <EmptyState
          title="No licences"
          description="No production licences have been recorded yet."
        />
      )}

      {!loading && !error && licences.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr className="text-left text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-3 font-medium">Production</th>
                <th className="px-4 py-3 font-medium">Licensing Body</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Licence Number</th>
                <th className="px-4 py-3 font-medium">Application Date</th>
                <th className="px-4 py-3 font-medium">Approval Date</th>
                <th className="px-4 py-3 font-medium">Expiry Date</th>
                <th className="px-4 py-3 font-medium">Fee</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {licences.map((licence) => (
                <tr key={licence.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-gray-600">
                    {licence.operating_context
                      ? licence.operating_context.slice(0, 8) + '…'
                      : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge tone={licensingBodyTone(licence.licensing_body)}>
                      {licence.licensing_body.toUpperCase()}
                    </StatusBadge>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge tone={licenceStatusTone(licence.status)}>
                      {licence.status.replace(/_/g, ' ')}
                    </StatusBadge>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-700">
                    {licence.licence_number || '—'}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{formatDate(licence.application_date)}</td>
                  <td className="px-4 py-3 text-gray-600">{formatDate(licence.approval_date)}</td>
                  <td className="px-4 py-3 text-gray-600">{formatDate(licence.expiry_date)}</td>
                  <td className="px-4 py-3 text-gray-700">{zar(licence.fee_amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  );
}

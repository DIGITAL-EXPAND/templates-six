'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchUnionAgreements, fetchUnionRates } from '@/lib/api/endpoints';
import type { UnionAgreement, UnionCallRate } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const zar = (val: string) =>
  'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function unionTone(union: string): 'info' | 'warning' | 'good' | 'neutral' {
  if (union === 'saga') return 'info';
  if (union === 'musa') return 'warning';
  if (union === 'equity') return 'good';
  return 'neutral';
}

function rateTypeTone(type: string): 'good' | 'info' | 'warning' | 'neutral' {
  if (type === 'per_performance') return 'good';
  if (type === 'daily') return 'info';
  if (type === 'weekly') return 'warning';
  return 'neutral';
}

export default function UnionPage() {
  const { tokens } = useAuth();
  const [agreements, setAgreements] = useState<UnionAgreement[]>([]);
  const [rates, setRates] = useState<UnionCallRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.allSettled([
      fetchUnionAgreements(tokens.access),
      fetchUnionRates(tokens.access),
    ]).then(([agRes, rateRes]) => {
      if (agRes.status === 'fulfilled') setAgreements(agRes.value.results ?? []);
      if (rateRes.status === 'fulfilled') setRates(rateRes.value.results ?? []);
      if (agRes.status === 'rejected' && rateRes.status === 'rejected') setError('Failed to load union data.');
      setLoading(false);
    });
  }, [tokens?.access]);

  const getAgreementName = (id: string) =>
    agreements.find((a) => a.id === id)?.agreement_name ?? id.slice(0, 8) + '…';

  if (loading) return <AppShell pageTitle="Union Agreements &amp; Rates"><LoadingState label="Loading union agreements..." /></AppShell>;
  if (error) return <AppShell pageTitle="Union Agreements &amp; Rates"><ErrorState message={error} /></AppShell>;

  const activeAgreements = agreements.filter((a) => a.is_active);

  return (
    <AppShell pageTitle="Union Agreements & Rates">
      <PageHeader title="Union Agreements & Rates" description="Collective agreements and minimum call rates" />

      {/* Section 1 — Active Agreements */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Active Agreements</h2>
        {activeAgreements.length === 0 ? (
          <EmptyState title="No active agreements" description="Active union agreements will appear here." />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {activeAgreements.map((a) => (
              <div key={a.id} className="bg-white border border-gray-200 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-2">
                  <StatusBadge tone={unionTone(a.union)}>{a.union.toUpperCase()}</StatusBadge>
                </div>
                <h3 className="font-semibold mb-3">{a.agreement_name}</h3>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Effective</dt>
                    <dd>{formatDate(a.effective_date)}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Expiry</dt>
                    <dd>{formatDate(a.expiry_date)}</dd>
                  </div>
                  <div className="border-t border-gray-100 pt-2 mt-2">
                    <dt className="text-gray-500 mb-1 text-xs uppercase font-medium">Key Rules</dt>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Min call hours</span>
                        <span className="font-medium">{a.minimum_call_hours}h</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Turnaround</span>
                        <span className="font-medium">{a.turnaround_hours}h</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">OT multiplier</span>
                        <span className="font-medium">{a.overtime_multiplier}x</span>
                      </div>
                    </div>
                  </div>
                </dl>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Section 2 — Minimum Rates */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Minimum Rates</h2>
        {rates.length === 0 ? (
          <EmptyState title="No rates" description="Minimum call rates will appear here once added." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
              <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3 text-left">Role Category</th>
                  <th className="px-4 py-3 text-left">Rate Type</th>
                  <th className="px-4 py-3 text-right">Minimum Rate</th>
                  <th className="px-4 py-3 text-left">Effective Date</th>
                  <th className="px-4 py-3 text-left">Agreement</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {rates.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{r.role_category.replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={rateTypeTone(r.rate_type)}>{r.rate_type.replace(/_/g, ' ')}</StatusBadge>
                    </td>
                    <td className="px-4 py-3 text-right">{zar(r.minimum_rate)}</td>
                    <td className="px-4 py-3">{formatDate(r.effective_date)}</td>
                    <td className="px-4 py-3 text-gray-600">{getAgreementName(r.agreement)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </AppShell>
  );
}

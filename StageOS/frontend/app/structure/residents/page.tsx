'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchResidentCompanies } from '@/lib/api/endpoints';
import type { ResidentCompany } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const zar = (val: string) =>
  'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function companyTypeTone(type: string): 'info' | 'good' | 'warning' | 'neutral' {
  if (type === 'theatre_company') return 'info';
  if (type === 'dance_company' || type === 'opera_company') return 'good';
  if (type === 'music_ensemble') return 'warning';
  return 'neutral';
}

function statusTone(status: string): 'good' | 'neutral' | 'warning' | 'danger' | 'info' {
  if (status === 'active') return 'good';
  if (status === 'completed') return 'neutral';
  if (status === 'suspended') return 'warning';
  if (status === 'terminated') return 'danger';
  if (status === 'prospective') return 'info';
  return 'neutral';
}

export default function ResidentCompaniesPage() {
  const { tokens } = useAuth();
  const [companies, setCompanies] = useState<ResidentCompany[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    fetchResidentCompanies(tokens.access)
      .then((d) => setCompanies(d.results ?? []))
      .catch(() => setError('Failed to load resident companies.'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  if (loading) return <AppShell pageTitle="Resident Companies"><LoadingState label="Loading resident companies..." /></AppShell>;
  if (error) return <AppShell pageTitle="Resident Companies"><ErrorState message={error} /></AppShell>;

  return (
    <AppShell pageTitle="Resident Companies">
      <PageHeader title="Resident Companies" description="Theatre, dance and music companies in residence" />

      {companies.length === 0 ? (
        <EmptyState title="No resident companies" description="Resident companies will appear here once added." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {companies.map((c) => (
            <div key={c.id} className="bg-white border border-gray-200 rounded-lg p-5">
              <div className="flex items-start justify-between gap-2 mb-3">
                <h3 className="font-semibold text-base">{c.name}</h3>
                <StatusBadge tone={statusTone(c.status)}>{c.status}</StatusBadge>
              </div>
              <div className="flex gap-2 mb-4">
                <StatusBadge tone={companyTypeTone(c.company_type)}>{c.company_type.replace(/_/g, ' ')}</StatusBadge>
              </div>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-500">Artistic Director</dt>
                  <dd className="font-medium">{c.artistic_director || '—'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Venue</dt>
                  <dd className="font-mono text-xs text-gray-600">{c.venue.slice(0, 8)}…</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Residency Period</dt>
                  <dd className="text-right">{formatDate(c.residency_start_date)} – {formatDate(c.residency_end_date)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Performance Slots/Year</dt>
                  <dd className="font-medium">{c.performance_slots_per_year}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Annual Subsidy</dt>
                  <dd className="font-medium">{zar(c.annual_subsidy)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Rental Discount</dt>
                  <dd className="font-medium">{c.rental_rate_discount_pct}%</dd>
                </div>
              </dl>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}

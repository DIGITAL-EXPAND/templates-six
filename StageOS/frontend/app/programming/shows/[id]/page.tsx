'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { StatusBadge } from '@/components/ui/status-badge';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { fetchShowLifecycle } from '@/lib/api/endpoints';
import type { ShowLifecycle } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const zar = (val: string) =>
  'R ' + parseFloat(val).toLocaleString('en-ZA', { minimumFractionDigits: 2 });

const milestoneLabel: Record<string, string> = {
  deposit: 'Deposit (50%)',
  balance: 'Balance',
  final: 'Final',
  full: 'Full Payment',
};

const paymentTone: Record<string, 'neutral' | 'info' | 'warning' | 'good' | 'danger'> = {
  pending: 'neutral',
  invoice_received: 'info',
  approved: 'warning',
  paid: 'good',
  disputed: 'danger',
};

const engagementTone: Record<string, 'neutral' | 'info' | 'good' | 'warning' | 'danger'> = {
  proposed: 'neutral',
  confirmed: 'info',
  contracted: 'good',
  performed: 'good',
  cancelled: 'danger',
};

function humanise(val: string) {
  return val.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-5 py-3">
        <h2 className="text-sm font-semibold text-gray-700">{title}</h2>
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}

export default function ShowLifecyclePage() {
  const params = useParams<{ id: string }>();
  const { tokens } = useAuth();
  const [data, setData] = useState<ShowLifecycle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access || !params.id) return;
    fetchShowLifecycle(tokens.access, params.id)
      .then((d) => { setData(d); setLoading(false); })
      .catch(() => { setError('Show lifecycle could not be loaded.'); setLoading(false); });
  }, [params.id, tokens?.access]);

  if (loading) return <AppShell><LoadingState label="Loading show lifecycle..." /></AppShell>;
  if (error || !data) return <AppShell><ErrorState message={error || 'Not found'} /></AppShell>;

  const netPos = parseFloat(data.financial_summary.net_position);

  return (
    <AppShell pageTitle={data.title || 'Show Lifecycle'}>
      <div className="space-y-5">
        <Link
          href="/programming/shows"
          className="inline-flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-slate-950"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Shows
        </Link>

        {/* Header */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">{data.title || 'Untitled Show'}</h1>
              <p className="mt-1 text-sm text-gray-500">Show Lifecycle Overview</p>
            </div>
            <StatusBadge tone="info">{humanise(data.status)}</StatusBadge>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs text-gray-500">Budget Approved</p>
              <p className="text-lg font-semibold text-gray-900">{zar(data.budget_approved)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Revenue Target</p>
              <p className="text-lg font-semibold text-gray-900">{zar(data.revenue_target)}</p>
            </div>
          </div>
        </div>

        {/* Financial Summary */}
        <SectionCard title="Financial Summary">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-gray-500">Ticket Revenue</p>
              <p className="text-lg font-semibold text-gray-900">
                {zar(data.financial_summary.ticket_revenue)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Artist Costs Paid</p>
              <p className="text-lg font-semibold text-gray-900">
                {zar(data.financial_summary.artist_costs_paid)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Net Position</p>
              <p className={`text-lg font-semibold ${netPos >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                {zar(data.financial_summary.net_position)}
              </p>
            </div>
          </div>
        </SectionCard>

        {/* Performances */}
        <SectionCard title={`Performances (${data.performances.length})`}>
          {data.performances.length === 0 ? (
            <EmptyState title="No performances scheduled" description="" />
          ) : (
            <table className="w-full text-sm">
              <thead className="border-b border-gray-100 text-left">
                <tr>
                  <th className="pb-2 font-semibold text-gray-600">Date</th>
                  <th className="pb-2 font-semibold text-gray-600">Start</th>
                  <th className="pb-2 font-semibold text-gray-600">End</th>
                  <th className="pb-2 font-semibold text-gray-600">Expected Audience</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.performances.map((p) => (
                  <tr key={p.id}>
                    <td className="py-2 text-gray-900">{p.date}</td>
                    <td className="py-2 text-gray-600">{p.start_time}</td>
                    <td className="py-2 text-gray-600">{p.end_time ?? '—'}</td>
                    <td className="py-2 text-gray-600">{p.expected_audience}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </SectionCard>

        {/* Artist Engagements */}
        <SectionCard title={`Artist Engagements (${data.engagements.length})`}>
          {data.engagements.length === 0 ? (
            <EmptyState title="No artist engagements" description="" />
          ) : (
            <table className="w-full text-sm">
              <thead className="border-b border-gray-100 text-left">
                <tr>
                  <th className="pb-2 font-semibold text-gray-600">Artist</th>
                  <th className="pb-2 font-semibold text-gray-600">Role</th>
                  <th className="pb-2 font-semibold text-gray-600">Fee</th>
                  <th className="pb-2 font-semibold text-gray-600">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.engagements.map((e) => (
                  <tr key={e.id}>
                    <td className="py-2 font-medium text-gray-900">{e.artist_name}</td>
                    <td className="py-2 text-gray-600">{e.role}</td>
                    <td className="py-2 text-gray-600">{zar(e.fee)}</td>
                    <td className="py-2">
                      <StatusBadge tone={engagementTone[e.status] ?? 'neutral'}>
                        {humanise(e.status)}
                      </StatusBadge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </SectionCard>

        {/* Payments */}
        <SectionCard title={`Artist Payments (${data.payments.length})`}>
          {data.payments.length === 0 ? (
            <EmptyState title="No payments recorded" description="" />
          ) : (
            <table className="w-full text-sm">
              <thead className="border-b border-gray-100 text-left">
                <tr>
                  <th className="pb-2 font-semibold text-gray-600">Milestone</th>
                  <th className="pb-2 font-semibold text-gray-600">Amount</th>
                  <th className="pb-2 font-semibold text-gray-600">Status</th>
                  <th className="pb-2 font-semibold text-gray-600">Paid Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.payments.map((p) => (
                  <tr key={p.id}>
                    <td className="py-2 text-gray-900">{milestoneLabel[p.milestone] ?? p.milestone}</td>
                    <td className="py-2 text-gray-600">{zar(p.amount)}</td>
                    <td className="py-2">
                      <StatusBadge tone={paymentTone[p.status] ?? 'neutral'}>
                        {humanise(p.status)}
                      </StatusBadge>
                    </td>
                    <td className="py-2 text-gray-500">{p.paid_date ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </SectionCard>

        {/* Production Info */}
        <SectionCard title="Production Details">
          <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
            <div>
              <p className="text-xs text-gray-500">Contracts</p>
              <p className="text-lg font-semibold text-gray-900">{data.contracts.length}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Technical Rider</p>
              <p className="text-sm font-medium text-gray-900">
                {data.technical_rider
                  ? humanise(data.technical_rider.status)
                  : 'Not submitted'}
              </p>
              {data.technical_rider?.load_in_date && (
                <p className="text-xs text-gray-500">Load-in: {data.technical_rider.load_in_date}</p>
              )}
              {data.technical_rider && (
                <p className="text-xs text-gray-500">Crew: {data.technical_rider.crew_size}</p>
              )}
            </div>
            <div>
              <p className="text-xs text-gray-500">Show Calls</p>
              <p className="text-lg font-semibold text-gray-900">{data.show_calls_count}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Post-Show Reports</p>
              <p className="text-lg font-semibold text-gray-900">{data.post_show_reports_count}</p>
            </div>
          </div>
        </SectionCard>
      </div>
    </AppShell>
  );
}

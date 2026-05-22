'use client';

import { useEffect, useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchCoProducers, fetchCoProductionSettlements, agreeCoProductionSettlement } from '@/lib/api/endpoints';
import type { CoProducer, CoProductionSettlement } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const zar = (val: string) =>
  'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function roleTone(role: string): 'good' | 'info' | 'warning' | 'neutral' {
  if (role === 'lead_producer') return 'good';
  if (role === 'co_producer') return 'info';
  if (role === 'presenting_partner') return 'warning';
  return 'neutral';
}

function settlementTone(status: string): 'neutral' | 'info' | 'warning' | 'good' {
  if (status === 'draft') return 'neutral';
  if (status === 'reviewed') return 'info';
  if (status === 'agreed') return 'warning';
  if (status === 'paid') return 'good';
  return 'neutral';
}

export default function CoProductionPage() {
  const { tokens } = useAuth();
  const [producers, setProducers] = useState<CoProducer[]>([]);
  const [settlements, setSettlements] = useState<CoProductionSettlement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedSettlement, setExpandedSettlement] = useState<string | null>(null);
  const [agreeing, setAgreeing] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.allSettled([
      fetchCoProducers(tokens.access),
      fetchCoProductionSettlements(tokens.access),
    ]).then(([prodRes, settlRes]) => {
      if (prodRes.status === 'fulfilled') setProducers(prodRes.value.results ?? []);
      if (settlRes.status === 'fulfilled') setSettlements(settlRes.value.results ?? []);
      if (prodRes.status === 'rejected' && settlRes.status === 'rejected') setError('Failed to load co-production data.');
      setLoading(false);
    });
  }, [tokens?.access]);

  const handleAgree = async (id: string) => {
    if (!tokens?.access) return;
    setAgreeing(id);
    try {
      const updated = await agreeCoProductionSettlement(tokens.access, id);
      setSettlements((prev) => prev.map((s) => s.id === id ? updated : s));
    } catch {
      // silently fail
    } finally {
      setAgreeing(null);
    }
  };

  if (loading) return <AppShell pageTitle="Co-Productions"><LoadingState label="Loading co-productions..." /></AppShell>;
  if (error) return <AppShell pageTitle="Co-Productions"><ErrorState message={error} /></AppShell>;

  return (
    <AppShell pageTitle="Co-Productions">
      <PageHeader title="Co-Productions" description="Co-production partners and financial settlement" />

      {/* Section 1 — Co-Producers */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Co-Producers</h2>
        {producers.length === 0 ? (
          <EmptyState title="No co-producers" description="Co-producers will appear here once added." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
              <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3 text-left">Production</th>
                  <th className="px-4 py-3 text-left">Partner Name</th>
                  <th className="px-4 py-3 text-left">Role</th>
                  <th className="px-4 py-3 text-right">Cost Share %</th>
                  <th className="px-4 py-3 text-right">Revenue Share %</th>
                  <th className="px-4 py-3 text-right">Upfront Contribution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {producers.map((p) => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">{p.operating_context.slice(0, 8)}…</td>
                    <td className="px-4 py-3 font-medium">{p.partner_name}</td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={roleTone(p.role)}>{p.role.replace(/_/g, ' ')}</StatusBadge>
                    </td>
                    <td className="px-4 py-3 text-right">{p.cost_share_percent}%</td>
                    <td className="px-4 py-3 text-right">{p.revenue_share_percent}%</td>
                    <td className="px-4 py-3 text-right">{zar(p.upfront_contribution)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Section 2 — Settlements */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Settlements</h2>
        {settlements.length === 0 ? (
          <EmptyState title="No settlements" description="Settlements will appear here once created." />
        ) : (
          <div className="space-y-3">
            {settlements.map((s) => {
              const netPositive = parseFloat(s.net_position) >= 0;
              const isExpanded = expandedSettlement === s.id;
              const canAgree = s.status === 'draft' || s.status === 'reviewed';
              return (
                <div key={s.id} className="border border-gray-200 rounded-lg overflow-hidden">
                  <div
                    className="bg-white px-4 py-3 flex items-center gap-4 cursor-pointer hover:bg-gray-50"
                    onClick={() => setExpandedSettlement(isExpanded ? null : s.id)}
                  >
                    {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                    <span className="font-mono text-xs text-gray-500 w-20">{s.operating_context.slice(0, 8)}…</span>
                    <span className="text-sm text-gray-600">{formatDate(s.settlement_date)}</span>
                    <span className="text-sm">Rev: {zar(s.total_revenue)}</span>
                    <span className="text-sm">Costs: {zar(s.total_costs)}</span>
                    <span className={`text-sm font-medium ${netPositive ? 'text-green-700' : 'text-red-700'}`}>
                      Net: {zar(s.net_position)}
                    </span>
                    <div className="ml-auto flex items-center gap-3">
                      <StatusBadge tone={settlementTone(s.status)}>{s.status}</StatusBadge>
                      {canAgree && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleAgree(s.id); }}
                          disabled={agreeing === s.id}
                          className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 disabled:opacity-50"
                        >
                          {agreeing === s.id ? 'Agreeing...' : 'Agree Settlement'}
                        </button>
                      )}
                    </div>
                  </div>
                  {isExpanded && s.lines && s.lines.length > 0 && (
                    <div className="border-t border-gray-100 bg-gray-50 px-4 py-3">
                      <table className="w-full text-sm">
                        <thead className="text-xs text-gray-500 uppercase">
                          <tr>
                            <th className="py-2 text-left">Partner</th>
                            <th className="py-2 text-right">Amount Due</th>
                            <th className="py-2 text-right">Amount Paid</th>
                            <th className="py-2 text-left">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {s.lines.map((l) => (
                            <tr key={l.id}>
                              <td className="py-2 font-mono text-xs">{l.co_producer.slice(0, 8)}…</td>
                              <td className="py-2 text-right">{zar(l.amount_due)}</td>
                              <td className="py-2 text-right">{zar(l.amount_paid)}</td>
                              <td className="py-2">
                                <StatusBadge tone={l.is_paid ? 'good' : 'neutral'}>{l.is_paid ? 'Paid' : 'Pending'}</StatusBadge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {isExpanded && (!s.lines || s.lines.length === 0) && (
                    <div className="border-t border-gray-100 bg-gray-50 px-4 py-3 text-sm text-gray-500">No settlement lines.</div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>
    </AppShell>
  );
}

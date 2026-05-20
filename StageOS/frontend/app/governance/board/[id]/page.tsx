'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ArrowLeft, Printer } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { StatusBadge } from '@/components/ui/status-badge';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { fetchBoardPack } from '@/lib/api/endpoints';
import type { BoardPackData } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const zar = (val: string) =>
  'R ' + parseFloat(val).toLocaleString('en-ZA', { minimumFractionDigits: 2 });

function humanise(val: string) {
  return val.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

const resolutionTone: Record<string, 'neutral' | 'good' | 'danger' | 'warning' | 'info'> = {
  proposed: 'neutral',
  passed: 'good',
  failed: 'danger',
  deferred: 'warning',
  noted: 'info',
  withdrawn: 'neutral',
};

function kpiPct(target: string, actual: string): number {
  const t = parseFloat(target);
  if (t <= 0) return 0;
  return Math.min(100, (parseFloat(actual) / t) * 100);
}

function pctColor(pct: number) {
  if (pct >= 90) return 'text-green-700';
  if (pct >= 60) return 'text-amber-600';
  return 'text-red-600';
}

function riskScore(likelihood: number, impact: number) {
  return likelihood * impact;
}

function riskScoreColor(score: number) {
  if (score >= 15) return 'text-red-600 font-semibold';
  if (score >= 8) return 'text-amber-600 font-semibold';
  return 'text-green-700';
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

export default function BoardMeetingDetailPage() {
  const params = useParams<{ id: string }>();
  const { tokens } = useAuth();
  const [pack, setPack] = useState<BoardPackData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access || !params.id) return;
    fetchBoardPack(tokens.access, params.id)
      .then((d) => { setPack(d); setLoading(false); })
      .catch(() => { setError('Board pack could not be loaded.'); setLoading(false); });
  }, [params.id, tokens?.access]);

  if (loading) return <AppShell><LoadingState label="Loading board pack..." /></AppShell>;
  if (error || !pack) return <AppShell><ErrorState message={error || 'Not found'} /></AppShell>;

  const { meeting, kpi_summary, open_risks, resolutions, budget_summary } = pack;

  return (
    <AppShell pageTitle={meeting.title}>
      <div className="space-y-5" id="board-pack-content">
        <div className="flex items-center justify-between">
          <Link
            href="/governance/board"
            className="inline-flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-slate-950"
          >
            <ArrowLeft className="h-4 w-4" /> Back to Board Meetings
          </Link>
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            <Printer className="h-4 w-4" /> Print Board Pack
          </button>
        </div>

        {/* Meeting Header */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">{meeting.title}</h1>
              <p className="mt-1 text-sm text-gray-500">
                {meeting.meeting_date} · {humanise(meeting.meeting_type)}
              </p>
            </div>
            <div className="flex gap-2">
              <StatusBadge tone={meeting.status === 'concluded' ? 'good' : 'info'}>
                {humanise(meeting.status)}
              </StatusBadge>
              <StatusBadge tone={meeting.quorum_achieved ? 'good' : 'danger'}>
                Quorum {meeting.quorum_achieved ? 'Met' : 'Not Met'}
              </StatusBadge>
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-600">Members present: {meeting.members_present}</p>
        </div>

        {/* Budget Summary */}
        {budget_summary && (
          <SectionCard title="Budget Summary">
            <p className="mb-3 text-sm font-medium text-gray-700">{budget_summary.title}</p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-500">Total Income</p>
                <p className="text-lg font-semibold text-green-700">{zar(budget_summary.total_income)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Total Expenditure</p>
                <p className="text-lg font-semibold text-gray-900">{zar(budget_summary.total_expenditure)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Net Position</p>
                <p className={`text-lg font-semibold ${parseFloat(budget_summary.net_position) >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                  {zar(budget_summary.net_position)}
                </p>
              </div>
            </div>
          </SectionCard>
        )}

        {/* KPI Table */}
        <SectionCard title={`KPIs (${kpi_summary.length})`}>
          {kpi_summary.length === 0 ? (
            <EmptyState title="No KPIs recorded" description="" />
          ) : (
            <table className="w-full text-sm">
              <thead className="border-b border-gray-100 text-left">
                <tr>
                  <th className="pb-2 font-semibold text-gray-600">KPI</th>
                  <th className="pb-2 font-semibold text-gray-600">Period</th>
                  <th className="pb-2 font-semibold text-gray-600">Target</th>
                  <th className="pb-2 font-semibold text-gray-600">Actual</th>
                  <th className="pb-2 font-semibold text-gray-600">% of Target</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {kpi_summary.map((k, i) => {
                  const pct = kpiPct(k.target, k.actual);
                  return (
                    <tr key={i}>
                      <td className="py-2 font-medium text-gray-900">{k.name}</td>
                      <td className="py-2 text-gray-500">{humanise(k.period)}</td>
                      <td className="py-2 text-gray-600">{k.target} {k.unit}</td>
                      <td className="py-2 text-gray-600">{k.actual} {k.unit}</td>
                      <td className={`py-2 ${pctColor(pct)}`}>{pct.toFixed(1)}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </SectionCard>

        {/* Open Risks */}
        <SectionCard title={`Open Risks (${open_risks.length})`}>
          {open_risks.length === 0 ? (
            <EmptyState title="No open risks" description="" />
          ) : (
            <table className="w-full text-sm">
              <thead className="border-b border-gray-100 text-left">
                <tr>
                  <th className="pb-2 font-semibold text-gray-600">Risk</th>
                  <th className="pb-2 font-semibold text-gray-600">Likelihood</th>
                  <th className="pb-2 font-semibold text-gray-600">Impact</th>
                  <th className="pb-2 font-semibold text-gray-600">Risk Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {open_risks.map((r, i) => {
                  const score = riskScore(r.likelihood, r.impact);
                  return (
                    <tr key={i}>
                      <td className="py-2 font-medium text-gray-900">{r.title}</td>
                      <td className="py-2 text-gray-600">{r.likelihood}/5</td>
                      <td className="py-2 text-gray-600">{r.impact}/5</td>
                      <td className={`py-2 ${riskScoreColor(score)}`}>{score}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </SectionCard>

        {/* Resolutions */}
        <SectionCard title={`Resolutions (${resolutions.length})`}>
          {resolutions.length === 0 ? (
            <EmptyState title="No resolutions" description="" />
          ) : (
            <table className="w-full text-sm">
              <thead className="border-b border-gray-100 text-left">
                <tr>
                  <th className="pb-2 font-semibold text-gray-600">#</th>
                  <th className="pb-2 font-semibold text-gray-600">Title</th>
                  <th className="pb-2 font-semibold text-gray-600">Status</th>
                  <th className="pb-2 font-semibold text-gray-600">Proposed By</th>
                  <th className="pb-2 font-semibold text-gray-600">Due</th>
                  <th className="pb-2 font-semibold text-gray-600">Done</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {resolutions.map((r) => (
                  <tr key={r.id}>
                    <td className="py-2 text-gray-500">{r.number || '—'}</td>
                    <td className="py-2 font-medium text-gray-900">{r.title}</td>
                    <td className="py-2">
                      <StatusBadge tone={resolutionTone[r.status] ?? 'neutral'}>
                        {humanise(r.status)}
                      </StatusBadge>
                    </td>
                    <td className="py-2 text-gray-600">{r.proposed_by || '—'}</td>
                    <td className="py-2 text-gray-500">{r.action_due_date ?? '—'}</td>
                    <td className="py-2 text-center">
                      {r.action_completed ? (
                        <span className="text-green-600">✓</span>
                      ) : (
                        <span className="text-gray-300">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </SectionCard>

        <p className="text-right text-xs text-gray-400">
          Generated: {new Date(pack.generated_at).toLocaleString('en-ZA')}
        </p>
      </div>
    </AppShell>
  );
}

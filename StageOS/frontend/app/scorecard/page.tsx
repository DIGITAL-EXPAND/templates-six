'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AlertTriangle, CheckCircle2, Clock, FileSignature, TrendingUp } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { fetchScorecard } from '@/lib/api/endpoints';
import type { Scorecard } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

// ── Helpers ────────────────────────────────────────────────────────────────────

type RAG = 'green' | 'amber' | 'red' | 'neutral';

function ragColour(rag: RAG) {
  const map: Record<RAG, { card: string; num: string }> = {
    green:   { card: 'bg-green-50 border-green-200',  num: 'text-green-700' },
    amber:   { card: 'bg-amber-50 border-amber-200',  num: 'text-amber-700' },
    red:     { card: 'bg-red-50 border-red-200',      num: 'text-red-700'   },
    neutral: { card: 'bg-gray-50 border-gray-200',    num: 'text-gray-700'  },
  };
  return map[rag];
}

function MetricCard({
  label,
  value,
  rag,
  sub,
}: {
  label: string;
  value: number | string;
  rag: RAG;
  sub?: string;
}) {
  const c = ragColour(rag);
  return (
    <div className={`rounded-xl border p-5 ${c.card}`}>
      <div className={`text-3xl font-bold ${c.num}`}>{value}</div>
      <div className="mt-1 text-sm font-medium text-gray-700">{label}</div>
      {sub && <div className="mt-0.5 text-xs text-gray-500">{sub}</div>}
    </div>
  );
}

const SHOW_STATUS_COLOURS: Record<string, string> = {
  confirmed:   'bg-blue-100 text-blue-800',
  on_sale:     'bg-green-100 text-green-800',
  running:     'bg-purple-100 text-purple-800',
  programming: 'bg-gray-100 text-gray-700',
  closed:      'bg-gray-200 text-gray-500',
  cancelled:   'bg-red-100 text-red-700',
};

// ── Page ───────────────────────────────────────────────────────────────────────

export default function ScorecardPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';

  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    fetchScorecard(token)
      .then(setScorecard)
      .catch(() => setError('Could not load scorecard data.'))
      .finally(() => setLoading(false));
  }, [token]);

  return (
    <AppShell>
      {loading ? (
        <div className="flex h-48 items-center justify-center text-sm text-gray-400">
          Loading scorecard…
        </div>
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
          {error}
        </div>
      ) : scorecard ? (
        <ScorecardContent scorecard={scorecard} />
      ) : null}
    </AppShell>
  );
}

function ScorecardContent({ scorecard }: { scorecard: Scorecard }) {
  const {
    tasks,
    pending_approvals,
    contracts_expiring_30d,
    active_contexts,
    upcoming_shows,
    unread_notifications,
    departments,
  } = scorecard;

  const deptOverdueRag: RAG =
    tasks.dept_overdue === 0 ? 'green' : tasks.dept_overdue <= 5 ? 'amber' : 'red';
  const myOverdueRag: RAG =
    tasks.my_overdue === 0 ? 'green' : tasks.my_overdue <= 2 ? 'amber' : 'red';

  return (
    <div className="space-y-7">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Department Scorecard</h1>
        {departments.length > 0 && (
          <p className="mt-1 text-sm text-gray-500">
            {departments.map((d) => d.name).join(' · ')}
          </p>
        )}
      </div>

      {/* RAG summary */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="My Overdue Tasks"
          rag={myOverdueRag}
          sub={`${tasks.my_open + tasks.my_in_progress} active total`}
          value={tasks.my_overdue}
        />
        <MetricCard
          label="Dept Overdue Tasks"
          rag={deptOverdueRag}
          sub={`${tasks.dept_open + tasks.dept_in_progress} active in dept`}
          value={tasks.dept_overdue}
        />
        <MetricCard
          label="Pending Approvals"
          rag={pending_approvals === 0 ? 'green' : 'amber'}
          sub="Awaiting sign-off"
          value={pending_approvals}
        />
        <MetricCard
          label="Contracts Expiring"
          rag={contracts_expiring_30d === 0 ? 'green' : 'red'}
          sub="Within 30 days"
          value={contracts_expiring_30d}
        />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Tasks breakdown */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <div className="mb-4 flex items-center gap-2">
            <Clock className="h-4 w-4 text-gray-400" />
            <h2 className="font-semibold text-gray-800">Task Summary</h2>
          </div>
          <div className="space-y-3">
            {[
              { label: 'My open tasks',          value: tasks.my_open,        colour: 'text-gray-700' },
              { label: 'My in-progress tasks',   value: tasks.my_in_progress, colour: 'text-blue-700' },
              { label: 'My overdue',             value: tasks.my_overdue,     colour: tasks.my_overdue > 0 ? 'text-red-700 font-bold' : 'text-gray-700' },
              { label: 'Dept open tasks',        value: tasks.dept_open,      colour: 'text-gray-700' },
              { label: 'Dept in-progress',       value: tasks.dept_in_progress, colour: 'text-blue-700' },
              { label: 'Dept overdue',           value: tasks.dept_overdue,   colour: tasks.dept_overdue > 0 ? 'text-red-700 font-bold' : 'text-gray-700' },
            ].map(({ label, value, colour }) => (
              <div className="flex items-center justify-between text-sm" key={label}>
                <span className="text-gray-600">{label}</span>
                <span className={colour}>{value}</span>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <Link
              className="text-sm font-medium text-teal-700 hover:underline"
              href="/tasks"
            >
              View all tasks →
            </Link>
          </div>
        </div>

        {/* Productions & contracts */}
        <div className="space-y-5">
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-gray-400" />
              <h2 className="font-semibold text-gray-800">Active Productions</h2>
            </div>
            <div className="text-4xl font-bold text-gray-900">{active_contexts}</div>
            <p className="mt-1 text-sm text-gray-500">operating contexts in flight</p>
            <Link className="mt-3 block text-sm font-medium text-teal-700 hover:underline" href="/workspaces">
              View productions →
            </Link>
          </div>

          {contracts_expiring_30d > 0 && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-5">
              <div className="mb-2 flex items-center gap-2">
                <FileSignature className="h-4 w-4 text-red-500" />
                <h2 className="font-semibold text-red-800">Contracts Expiring Soon</h2>
              </div>
              <div className="text-3xl font-bold text-red-700">{contracts_expiring_30d}</div>
              <p className="mt-1 text-sm text-red-700">contracts expire within 30 days</p>
              <Link className="mt-3 block text-sm font-medium text-red-700 hover:underline" href="/contracts">
                Review contracts →
              </Link>
            </div>
          )}

          {unread_notifications > 0 && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-amber-800">Unread Notifications</h2>
                <span className="rounded-full bg-amber-600 px-2.5 py-0.5 text-xs font-bold text-white">
                  {unread_notifications}
                </span>
              </div>
              <Link className="mt-3 block text-sm font-medium text-amber-700 hover:underline" href="/notifications">
                View notifications →
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Upcoming shows */}
      {upcoming_shows.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <div className="mb-4 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-gray-400" />
            <h2 className="font-semibold text-gray-800">Upcoming / Active Shows</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {upcoming_shows.map((show) => (
              <div className="flex items-center justify-between py-3" key={show.id}>
                <span className="text-sm font-medium text-gray-800">{show.title}</span>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                    SHOW_STATUS_COLOURS[show.status] ?? 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {show.status.replace(/_/g, ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Departments */}
      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <h2 className="mb-3 font-semibold text-gray-800">Your Department Roles</h2>
        <div className="flex flex-wrap gap-2">
          {departments.map((d) => (
            <span
              className={`rounded-full px-3 py-1 text-sm font-medium ${
                d.is_manager
                  ? 'bg-teal-100 text-teal-800 ring-1 ring-teal-300'
                  : 'bg-gray-100 text-gray-700'
              }`}
              key={d.id}
            >
              {d.name}
              {d.is_manager ? ' (Manager)' : ''}
            </span>
          ))}
        </div>
      </div>

      {/* Attention banner if all clear */}
      {tasks.dept_overdue === 0 &&
       tasks.my_overdue === 0 &&
       pending_approvals === 0 &&
       contracts_expiring_30d === 0 && (
        <div className="rounded-xl border border-green-200 bg-green-50 px-5 py-4">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <p className="text-sm font-semibold text-green-800">
              All clear — no overdue tasks, pending approvals, or expiring contracts.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { ChevronDown, ChevronRight, TrendingDown, TrendingUp } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { fetchBudgets, fetchBudgetLines } from '@/lib/api/endpoints';
import type { BudgetItem, BudgetLineItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function formatZAR(value: string) {
  return 'R ' + parseFloat(value).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

const STATUS_BADGE: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-700',
  submitted: 'bg-blue-100 text-blue-700',
  approved: 'bg-green-100 text-green-700',
  active: 'bg-teal-100 text-teal-700',
  closed: 'bg-slate-100 text-slate-600',
  revised: 'bg-amber-100 text-amber-700',
};

function StatusBadge({ status }: { status: string }) {
  const cls = STATUS_BADGE[status] ?? 'bg-slate-100 text-slate-600';
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${cls}`}>
      {status}
    </span>
  );
}

function NetPositionCell({ value }: { value: string }) {
  const num = parseFloat(value);
  if (num > 0) {
    return (
      <span className="inline-flex items-center gap-1 font-semibold text-green-700">
        <TrendingUp className="h-4 w-4" />
        {formatZAR(value)}
      </span>
    );
  }
  if (num < 0) {
    return (
      <span className="inline-flex items-center gap-1 font-semibold text-red-700">
        <TrendingDown className="h-4 w-4" />
        {formatZAR(value)}
      </span>
    );
  }
  return <span className="font-semibold text-slate-600">{formatZAR(value)}</span>;
}

function BudgetLinesPanel({ budgetId, token }: { budgetId: string; token: string }) {
  const [lines, setLines] = useState<BudgetLineItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    fetchBudgetLines(token, budgetId)
      .then((res) => { if (mounted) setLines(res.results); })
      .catch(() => { if (mounted) setError('Budget lines could not be loaded.'); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token, budgetId]);

  if (loading) return <div className="px-4 py-3 text-sm text-slate-500">Loading lines…</div>;
  if (error) return <div className="px-4 py-3 text-sm text-red-600">{error}</div>;
  if (!lines.length) return <div className="px-4 py-3 text-sm text-slate-400">No budget lines recorded.</div>;

  // Group by category
  const byCategory = lines.reduce<Record<string, BudgetLineItem[]>>((acc, line) => {
    const cat = line.category || 'Uncategorised';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(line);
    return acc;
  }, {});

  const isIncome = (category: string) =>
    category.toLowerCase().includes('income') || category.toLowerCase().includes('revenue');

  const totalBudgeted = lines.reduce((sum, l) => sum + parseFloat(l.amount || '0'), 0);
  const totalActual = lines.reduce((sum, l) => sum + parseFloat(l.actual_amount || '0'), 0);

  return (
    <div className="divide-y divide-slate-100 border-t border-slate-100">
      {Object.entries(byCategory).map(([category, categoryLines]) => (
        <div key={category}>
          <div className="bg-slate-50 px-4 py-1.5 text-xs font-bold uppercase tracking-wide text-slate-500">
            {category}
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-slate-400">
                <th className="px-4 py-1.5 font-medium">Description</th>
                <th className="px-4 py-1.5 text-right font-medium">Qty</th>
                <th className="px-4 py-1.5 text-right font-medium">Unit Cost</th>
                <th className="px-4 py-1.5 text-right font-medium">Budgeted</th>
                <th className="px-4 py-1.5 text-right font-medium">Actual</th>
                <th className="px-4 py-1.5 text-right font-medium">Variance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {categoryLines.map((line) => (
                <tr key={line.id} className={isIncome(category) ? 'text-green-800' : 'text-slate-700'}>
                  <td className="px-4 py-2">{line.description}</td>
                  <td className="px-4 py-2 text-right tabular-nums">{line.quantity}</td>
                  <td className="px-4 py-2 text-right tabular-nums">{formatZAR(line.unit_cost)}</td>
                  <td className="px-4 py-2 text-right tabular-nums font-medium">{formatZAR(line.amount)}</td>
                  <td className="px-4 py-2 text-right tabular-nums">{formatZAR(line.actual_amount)}</td>
                  <td className={`px-4 py-2 text-right tabular-nums ${parseFloat(line.variance) < 0 ? 'text-red-600' : 'text-green-700'}`}>
                    {formatZAR(line.variance)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
      <div className="flex items-center justify-end gap-8 bg-slate-100 px-4 py-2 text-sm font-bold text-slate-800">
        <span>Totals</span>
        <span className="tabular-nums">{formatZAR(String(totalBudgeted))}</span>
        <span className="tabular-nums">{formatZAR(String(totalActual))}</span>
      </div>
    </div>
  );
}

function BudgetCard({ budget, token }: { budget: BudgetItem; token: string }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <article className="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <div className="flex flex-col gap-2 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-base font-bold text-slate-950 truncate">{budget.name}</h3>
            <StatusBadge status={budget.status} />
          </div>
          <div className="mt-1 text-xs text-slate-500">
            Financial year: <span className="font-medium text-slate-700">{budget.financial_year}</span>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-6 text-sm">
          <div className="text-right">
            <div className="text-xs text-slate-400">Income</div>
            <div className="font-semibold text-green-700 tabular-nums">{formatZAR(budget.total_income)}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400">Expenditure</div>
            <div className="font-semibold text-slate-700 tabular-nums">{formatZAR(budget.total_expenditure)}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400">Net position</div>
            <NetPositionCell value={budget.net_position} />
          </div>
          <button
            aria-expanded={expanded}
            className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            onClick={() => setExpanded((prev) => !prev)}
            type="button"
          >
            {expanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
            View Lines
          </button>
        </div>
      </div>
      {expanded && <BudgetLinesPanel budgetId={budget.id} token={token} />}
    </article>
  );
}

export default function BudgetPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';
  const [budgets, setBudgets] = useState<BudgetItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    fetchBudgets(token)
      .then((res) => { if (mounted) setBudgets(res.results); })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('Budgets could not be loaded.');
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token]);

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="View and manage organisational budgets, income and expenditure lines."
          eyebrow="Governance"
          title="Budget Management"
        />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? (
          <LoadingState label="Loading budgets" />
        ) : (
          <section className="space-y-3">
            {budgets.length ? (
              budgets.map((budget) => (
                <BudgetCard budget={budget} key={budget.id} token={token} />
              ))
            ) : (
              <EmptyState
                description="Budget records will appear here once they are created."
                title="No budgets found"
              />
            )}
          </section>
        )}
      </div>
    </AppShell>
  );
}

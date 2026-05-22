'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchRecurringProductions, createRecurringProduction } from '@/lib/api/endpoints';
import type { RecurringProduction } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function frequencyTone(freq: string): StatusTone {
  switch (freq) {
    case 'weekly': return 'danger';
    case 'fortnightly': return 'warning';
    case 'monthly': return 'info';
    case 'annually': return 'neutral';
    default: return 'neutral';
  }
}

const FREQUENCY_OPTIONS = ['weekly', 'fortnightly', 'monthly', 'annually'] as const;

const emptyForm = {
  name: '',
  description: '',
  frequency: 'monthly',
  next_occurrence_date: '',
  auto_create: false,
};

export default function RecurringPage() {
  const { tokens } = useAuth();
  const [productions, setProductions] = useState<RecurringProduction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ ...emptyForm });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchRecurringProductions(tokens.access)
      .then((r) => setProductions(r.results))
      .catch(() => setError('Failed to load recurring productions'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const created = await createRecurringProduction(tokens.access, {
        ...form,
        next_occurrence_date: form.next_occurrence_date || null,
        is_active: true,
      });
      setProductions((prev) => [created, ...prev]);
      setForm({ ...emptyForm });
      setShowForm(false);
    } catch {
      setFormError('Failed to create recurring production.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell pageTitle="Recurring Productions">
      <div className="space-y-6">
        <PageHeader
          title="Recurring Productions"
          description="Scheduled recurring and seasonal productions"
        />

        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">All Recurring Productions</h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-indigo-700"
          >
            {showForm ? 'Cancel' : 'New Recurring'}
          </button>
        </div>

        {showForm && (
          <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
            <h3 className="text-sm font-semibold text-slate-800">New Recurring Production</h3>
            {formError && <ErrorState message={formError} />}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Name</label>
                <input required className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Frequency</label>
                <select className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm" value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}>
                  {FREQUENCY_OPTIONS.map((f) => <option key={f} value={f}>{f.charAt(0).toUpperCase() + f.slice(1)}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Next Occurrence Date</label>
                <input type="date" className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm" value={form.next_occurrence_date} onChange={(e) => setForm({ ...form, next_occurrence_date: e.target.value })} />
              </div>
              <div className="flex items-center gap-2 mt-5">
                <input type="checkbox" id="auto_create" checked={form.auto_create} onChange={(e) => setForm({ ...form, auto_create: e.target.checked })} className="rounded border-slate-300" />
                <label htmlFor="auto_create" className="text-xs font-medium text-slate-700">Auto-create occurrences</label>
              </div>
              <div className="col-span-2">
                <label className="block text-xs font-medium text-slate-700 mb-1">Description</label>
                <textarea rows={2} className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
            </div>
            <div className="flex justify-end">
              <button type="submit" disabled={submitting} className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50">
                {submitting ? 'Saving…' : 'Create'}
              </button>
            </div>
          </form>
        )}

        {loading ? (
          <LoadingState label="Loading recurring productions…" />
        ) : error ? (
          <ErrorState message={error} />
        ) : productions.length === 0 ? (
          <EmptyState title="No recurring productions" description="Create your first recurring production above." />
        ) : (
          <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  {['Name', 'Frequency', 'Next Occurrence', 'Active', 'Auto-Create', 'Description'].map((h) => (
                    <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {productions.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50">
                    <td className="px-3 py-2 font-medium text-slate-900">{p.name}</td>
                    <td className="px-3 py-2"><StatusBadge tone={frequencyTone(p.frequency)}>{p.frequency}</StatusBadge></td>
                    <td className="px-3 py-2 text-slate-600">{formatDate(p.next_occurrence_date)}</td>
                    <td className="px-3 py-2"><StatusBadge tone={p.is_active ? 'good' : 'neutral'}>{p.is_active ? 'Active' : 'Inactive'}</StatusBadge></td>
                    <td className="px-3 py-2"><StatusBadge tone={p.auto_create ? 'good' : 'neutral'}>{p.auto_create ? 'Auto' : 'Manual'}</StatusBadge></td>
                    <td className="px-3 py-2 text-slate-600 max-w-sm truncate">{p.description || '—'}</td>
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

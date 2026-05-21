'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchConflictDeclarations, createConflictDeclaration } from '@/lib/api/endpoints';
import type { ConflictOfInterest } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function statusTone(status: ConflictOfInterest['status']): StatusTone {
  switch (status) {
    case 'declared_none': return 'good';
    case 'declared_conflict': return 'warning';
    case 'recused': return 'info';
    case 'pending': return 'neutral';
    case 'overdue': return 'danger';
    default: return 'neutral';
  }
}

const emptyForm = {
  declaration_date: '',
  financial_year: '',
  status: 'declared_none' as ConflictOfInterest['status'],
  category: 'financial',
  entity_name: '',
  description: '',
  matter_reference: '',
  is_annual_declaration: false,
};

export default function DeclarationsPage() {
  const { tokens } = useAuth();
  const [declarations, setDeclarations] = useState<ConflictOfInterest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ ...emptyForm });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchConflictDeclarations(tokens.access)
      .then((res) => setDeclarations(res.results))
      .catch(() => setError('Failed to load conflict declarations'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const created = await createConflictDeclaration(tokens.access, form);
      setDeclarations((prev) => [created, ...prev]);
      setForm({ ...emptyForm });
      setShowForm(false);
    } catch {
      setFormError('Failed to submit declaration. Please check your inputs.');
    } finally {
      setSubmitting(false);
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setForm((prev) => ({ ...prev, [name]: checked }));
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  }

  if (loading) return <AppShell><LoadingState label="Loading declarations…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  const annualCount = declarations.filter((d) => d.is_annual_declaration).length;
  const conflictCount = declarations.filter((d) => d.status === 'declared_conflict').length;
  const recusalCount = declarations.filter((d) => d.status === 'recused').length;

  return (
    <AppShell>
      <PageHeader
        title="Conflict of Interest Register"
        description="Annual and ad-hoc declarations of interest — Companies Act & PFMA requirement"
      />

      {/* Summary strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Annual Declarations</div>
          <div className="text-2xl font-bold text-gray-900">{annualCount}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Conflicts Declared</div>
          <div className="text-2xl font-bold text-yellow-600">{conflictCount}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Recusals</div>
          <div className="text-2xl font-bold text-blue-600">{recusalCount}</div>
        </div>
      </div>

      {/* New Declaration button */}
      <div className="px-4 pb-2">
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'New Declaration'}
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div className="mx-4 mb-4 rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900 mb-4">New Conflict of Interest Declaration</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Declaration Date</label>
                <input
                  name="declaration_date"
                  type="date"
                  value={form.declaration_date}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Financial Year</label>
                <input
                  name="financial_year"
                  value={form.financial_year}
                  onChange={handleChange}
                  placeholder="e.g. 2025/2026"
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  name="status"
                  value={form.status}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="declared_none">Declared None</option>
                  <option value="declared_conflict">Declared Conflict</option>
                  <option value="recused">Recused</option>
                  <option value="pending">Pending</option>
                  <option value="overdue">Overdue</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  name="category"
                  value={form.category}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="financial">Financial</option>
                  <option value="family">Family</option>
                  <option value="directorship">Directorship</option>
                  <option value="employment">Employment</option>
                  <option value="gift">Gift</option>
                  <option value="tender">Tender</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Entity Name</label>
                <input
                  name="entity_name"
                  value={form.entity_name}
                  onChange={handleChange}
                  placeholder="Related entity or person"
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Matter Reference</label>
                <input
                  name="matter_reference"
                  value={form.matter_reference}
                  onChange={handleChange}
                  placeholder="Reference number or matter"
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                rows={3}
                required
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_annual_declaration"
                name="is_annual_declaration"
                checked={form.is_annual_declaration}
                onChange={handleChange}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="is_annual_declaration" className="text-sm font-medium text-gray-700">
                Annual Declaration
              </label>
            </div>
            {formError && <p className="text-sm text-red-600">{formError}</p>}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={submitting}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {submitting ? 'Submitting…' : 'Submit Declaration'}
              </button>
              <button
                type="button"
                onClick={() => { setShowForm(false); setForm({ ...emptyForm }); }}
                className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Declarations table */}
      {declarations.length === 0 ? (
        <div className="px-4">
          <EmptyState title="No declarations recorded." description="Use 'New Declaration' to add a conflict of interest declaration." />
        </div>
      ) : (
        <div className="px-4 pb-8">
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">Declarant ID</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Financial Year</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Entity / Matter</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {declarations.map((d) => (
                  <tr key={d.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">
                      {d.declarant_name ?? d.declarant.slice(0, 8)}
                    </td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{formatDate(d.declaration_date)}</td>
                    <td className="px-4 py-3 text-gray-700">{d.financial_year}</td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={d.is_annual_declaration ? 'info' : 'neutral'}>
                        {d.is_annual_declaration ? 'Annual' : 'Ad-hoc'}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={statusTone(d.status)}>
                        {d.status.replace(/_/g, ' ')}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3 capitalize text-gray-700">{d.category}</td>
                    <td className="px-4 py-3 text-gray-700">
                      <span className="font-medium">{d.entity_name || '—'}</span>
                      {d.matter_reference && (
                        <span className="ml-2 text-xs text-gray-400">#{d.matter_reference}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AppShell>
  );
}

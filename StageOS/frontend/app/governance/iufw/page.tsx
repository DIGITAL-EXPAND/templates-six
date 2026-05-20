'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchIUFWIncidents, createIUFWIncident } from '@/lib/api/endpoints';
import type { IUFWIncident } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function zar(val: string | number) {
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function iufwTypeTone(type: IUFWIncident['iufw_type']): StatusTone {
  switch (type) {
    case 'irregular': return 'warning';
    case 'unauthorised': return 'danger';
    case 'fruitless': return 'warning';
    case 'wasteful': return 'neutral';
    default: return 'neutral';
  }
}

function iufwStatusTone(status: string): StatusTone {
  switch (status) {
    case 'identified': return 'info';
    case 'under_investigation': return 'warning';
    case 'referred_discipline':
    case 'referred_criminal': return 'danger';
    case 'condoned':
    case 'recovered':
    case 'written_off':
    case 'closed': return 'neutral';
    default: return 'neutral';
  }
}

const IUFW_TYPES: { value: IUFWIncident['iufw_type']; label: string }[] = [
  { value: 'irregular', label: 'Irregular' },
  { value: 'unauthorised', label: 'Unauthorised' },
  { value: 'fruitless', label: 'Fruitless' },
  { value: 'wasteful', label: 'Wasteful' },
];

function totalByType(incidents: IUFWIncident[], type: IUFWIncident['iufw_type']): number {
  return incidents
    .filter((i) => i.iufw_type === type)
    .reduce((sum, i) => sum + parseFloat(i.amount || '0'), 0);
}

const emptyForm = {
  iufw_type: 'irregular' as IUFWIncident['iufw_type'],
  financial_year: '',
  description: '',
  amount: '',
  discovered_date: '',
  responsible_description: '',
  root_cause: '',
};

export default function IUFWRegisterPage() {
  const { tokens } = useAuth();
  const [incidents, setIncidents] = useState<IUFWIncident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ ...emptyForm });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchIUFWIncidents(tokens.access)
      .then((res) => setIncidents(res.results))
      .catch(() => setError('Failed to load IUFW incidents'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const created = await createIUFWIncident(tokens.access, {
        ...form,
        amount: form.amount,
      });
      setIncidents((prev) => [created, ...prev]);
      setForm({ ...emptyForm });
      setShowForm(false);
    } catch {
      setFormError('Failed to log incident. Please check your inputs and try again.');
    } finally {
      setSubmitting(false);
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  if (loading) return <AppShell><LoadingState label="Loading IUFW register…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  return (
    <AppShell>
      <PageHeader
        title="IUFW Incident Register"
        description="Irregular, Unauthorised, Fruitless & Wasteful Expenditure"
      />

      {/* Summary strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4">
        {IUFW_TYPES.map(({ value, label }) => (
          <div key={value} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">{label}</div>
            <div className="text-lg font-bold text-gray-900">{zar(totalByType(incidents, value))}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {incidents.filter((i) => i.iufw_type === value).length} incident(s)
            </div>
          </div>
        ))}
      </div>

      {/* Log incident button */}
      <div className="px-4 pb-2">
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'Log Incident'}
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div className="mx-4 mb-4 rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Log New IUFW Incident</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  name="iufw_type"
                  value={form.iufw_type}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {IUFW_TYPES.map(({ value, label }) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
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
                <label className="block text-sm font-medium text-gray-700 mb-1">Amount (ZAR)</label>
                <input
                  name="amount"
                  type="number"
                  value={form.amount}
                  onChange={handleChange}
                  placeholder="0.00"
                  required
                  min="0"
                  step="0.01"
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Discovered Date</label>
                <input
                  name="discovered_date"
                  type="date"
                  value={form.discovered_date}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Responsible Party</label>
                <input
                  name="responsible_description"
                  value={form.responsible_description}
                  onChange={handleChange}
                  placeholder="Name / department"
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
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Root Cause</label>
              <textarea
                name="root_cause"
                value={form.root_cause}
                onChange={handleChange}
                rows={2}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            {formError && <p className="text-sm text-red-600">{formError}</p>}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={submitting}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {submitting ? 'Logging…' : 'Log Incident'}
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

      {/* Incidents table */}
      {incidents.length === 0 ? (
        <EmptyState title="No IUFW incidents logged." />
      ) : (
        <div className="px-4 pb-8">
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">Reference</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Description</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Discovered</th>
                  <th className="px-4 py-3 text-center">Board</th>
                  <th className="px-4 py-3 text-center">AG</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {incidents.map((incident) => (
                  <tr key={incident.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">{incident.reference_number}</td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={iufwTypeTone(incident.iufw_type)}>
                        {incident.iufw_type}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={iufwStatusTone(incident.status)}>
                        {incident.status.replace(/_/g, ' ')}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3 text-gray-700 max-w-xs">
                      <span title={incident.description}>
                        {incident.description.length > 60
                          ? incident.description.slice(0, 60) + '…'
                          : incident.description}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">{zar(incident.amount)}</td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{incident.discovered_date}</td>
                    <td className="px-4 py-3 text-center text-base">
                      {incident.reported_to_board ? '✓' : '✗'}
                    </td>
                    <td className="px-4 py-3 text-center text-base">
                      {incident.reported_to_ag ? '✓' : '✗'}
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

'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchRFQList, createRFQ } from '@/lib/api/endpoints';
import type { ThreeQuoteRequirement, SupplierQuote } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function zar(val: string | number | null | undefined) {
  if (val === null || val === undefined || val === '') return '—';
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function rfqStatusTone(status: string): StatusTone {
  switch (status) {
    case 'open': return 'info';
    case 'quotes_received': return 'warning';
    case 'awarded': return 'good';
    case 'cancelled': return 'neutral';
    case 'waiver_approved': return 'warning';
    default: return 'neutral';
  }
}

const emptyForm = {
  description: '',
  estimated_value: '',
  required_by_date: '',
  budget_line: '',
};

export default function RFQPage() {
  const { tokens } = useAuth();
  const [rfqs, setRfqs] = useState<ThreeQuoteRequirement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ ...emptyForm });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchRFQList(tokens.access)
      .then((res) => setRfqs(res.results))
      .catch(() => setError('Failed to load RFQ list'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const created = await createRFQ(tokens.access, {
        description: form.description,
        estimated_value: form.estimated_value,
        required_by_date: form.required_by_date || null,
        budget_line: form.budget_line,
      });
      setRfqs((prev) => [created, ...prev]);
      setForm({ ...emptyForm });
      setShowForm(false);
    } catch {
      setFormError('Failed to create RFQ. Please check your inputs.');
    } finally {
      setSubmitting(false);
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function toggleExpand(id: string) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  if (loading) return <AppShell><LoadingState label="Loading RFQ register…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  const openCount = rfqs.filter((r) => r.status === 'open').length;
  const evaluatingCount = rfqs.filter((r) => r.status === 'quotes_received').length;
  const awardedCount = rfqs.filter((r) => r.status === 'awarded').length;
  const totalValue = rfqs.reduce((sum, r) => sum + parseFloat(r.estimated_value || '0'), 0);

  return (
    <AppShell>
      <PageHeader
        title="RFQ / Three-Quote Register"
        description="SCM policy compliance: three written quotes required for R30 000 – R500 000 expenditure"
      />

      {/* Summary strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Open RFQs</div>
          <div className="text-2xl font-bold text-blue-600">{openCount}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Being Evaluated</div>
          <div className="text-2xl font-bold text-yellow-600">{evaluatingCount}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Awarded</div>
          <div className="text-2xl font-bold text-green-600">{awardedCount}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Total Est. Value</div>
          <div className="text-lg font-bold text-gray-900">{zar(totalValue)}</div>
        </div>
      </div>

      {/* New RFQ button */}
      <div className="px-4 pb-2">
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'New RFQ'}
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div className="mx-4 mb-4 rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Create New RFQ</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input
                  name="description"
                  value={form.description}
                  onChange={handleChange}
                  placeholder="Goods or services required"
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Estimated Value (ZAR)</label>
                <input
                  name="estimated_value"
                  type="number"
                  value={form.estimated_value}
                  onChange={handleChange}
                  placeholder="0.00"
                  required
                  min="0"
                  step="0.01"
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Required By</label>
                <input
                  name="required_by_date"
                  type="date"
                  value={form.required_by_date}
                  onChange={handleChange}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Budget Line</label>
                <input
                  name="budget_line"
                  value={form.budget_line}
                  onChange={handleChange}
                  placeholder="Budget line reference"
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            {formError && <p className="text-sm text-red-600">{formError}</p>}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={submitting}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {submitting ? 'Creating…' : 'Create RFQ'}
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

      {/* RFQ table */}
      {rfqs.length === 0 ? (
        <div className="px-4">
          <EmptyState title="No RFQs registered." description="Use 'New RFQ' to create a three-quote requirement." />
        </div>
      ) : (
        <div className="px-4 pb-8">
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">Reference</th>
                  <th className="px-4 py-3">Description</th>
                  <th className="px-4 py-3">Est. Value</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Required By</th>
                  <th className="px-4 py-3 text-center">Quotes</th>
                  <th className="px-4 py-3">Awarded Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {rfqs.map((rfq) => (
                  <>
                    <tr
                      key={rfq.id}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => toggleExpand(rfq.id)}
                    >
                      <td className="px-4 py-3 font-mono text-xs text-gray-700">{rfq.reference_number}</td>
                      <td className="px-4 py-3 text-gray-800 max-w-xs">
                        <span title={rfq.description}>
                          {rfq.description.length > 50 ? rfq.description.slice(0, 50) + '…' : rfq.description}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-medium text-gray-900 whitespace-nowrap">{zar(rfq.estimated_value)}</td>
                      <td className="px-4 py-3">
                        <StatusBadge tone={rfqStatusTone(rfq.status)}>
                          {rfq.status.replace(/_/g, ' ')}
                        </StatusBadge>
                      </td>
                      <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{formatDate(rfq.required_by_date)}</td>
                      <td className="px-4 py-3 text-center font-medium text-gray-700">{rfq.quotes_count}</td>
                      <td className="px-4 py-3 text-gray-700">{zar(rfq.awarded_amount)}</td>
                    </tr>
                    {expandedId === rfq.id && rfq.quotes && rfq.quotes.length > 0 && (
                      <tr key={`${rfq.id}-quotes`} className="bg-gray-50">
                        <td colSpan={7} className="px-6 py-3">
                          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">Supplier Quotes</div>
                          <table className="min-w-full text-xs">
                            <thead>
                              <tr className="text-left text-xs font-semibold text-gray-500 border-b border-gray-200">
                                <th className="pr-4 pb-1">Supplier</th>
                                <th className="pr-4 pb-1">Amount</th>
                                <th className="pr-4 pb-1">Date</th>
                                <th className="pr-4 pb-1">Reference</th>
                                <th className="pr-4 pb-1 text-center">Preferred</th>
                                <th className="pr-4 pb-1 text-center">Disqualified</th>
                              </tr>
                            </thead>
                            <tbody>
                              {rfq.quotes.map((q: SupplierQuote) => (
                                <tr key={q.id} className="border-b border-gray-100 last:border-0">
                                  <td className="pr-4 py-1 text-gray-800">{q.supplier_name}</td>
                                  <td className="pr-4 py-1 font-medium text-gray-900">{zar(q.quote_amount)}</td>
                                  <td className="pr-4 py-1 text-gray-600">{formatDate(q.quote_date)}</td>
                                  <td className="pr-4 py-1 font-mono text-gray-600">{q.quote_reference}</td>
                                  <td className="pr-4 py-1 text-center">{q.is_preferred ? '★' : ''}</td>
                                  <td className="pr-4 py-1 text-center">
                                    {q.disqualified ? (
                                      <span className="line-through text-red-500">Yes</span>
                                    ) : ''}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    )}
                    {expandedId === rfq.id && (!rfq.quotes || rfq.quotes.length === 0) && (
                      <tr key={`${rfq.id}-no-quotes`} className="bg-gray-50">
                        <td colSpan={7} className="px-6 py-3 text-sm text-gray-500 italic">No quotes loaded for this RFQ.</td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AppShell>
  );
}

'use client';
import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Receipt } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { useAuth } from '@/lib/auth/auth-provider';
import type { TillReconciliationItem } from '@/lib/api/types';

type NewReconForm = {
  recon_date: string;
  cash_counted: string;
  card_total: string;
  system_total: string;
  variance_explained: string;
};

const emptyForm: NewReconForm = {
  recon_date: '',
  cash_counted: '',
  card_total: '',
  system_total: '',
  variance_explained: '',
};

export default function ReconciliationPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';
  const [records, setRecords] = useState<TillReconciliationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewReconForm>(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => {
    if (!token) return;
    fetch('/api/v1/ticketing/till-reconciliations/', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(data => setRecords(data.results ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const totalVariance = records.reduce((sum, r) => sum + parseFloat(r.variance || '0'), 0);

  function updateField(field: keyof NewReconForm, value: string) {
    setForm(prev => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!token) return;
    setSubmitting(true);
    setFormError('');
    try {
      const cash = parseFloat(form.cash_counted) || 0;
      const card = parseFloat(form.card_total) || 0;
      const system = parseFloat(form.system_total) || 0;
      const variance = (cash + card - system).toFixed(2);

      const resp = await fetch('/api/v1/ticketing/till-reconciliations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          recon_date: form.recon_date,
          cash_counted: form.cash_counted,
          card_total: form.card_total,
          system_total: form.system_total,
          variance,
          variance_explained: form.variance_explained,
        }),
      });
      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        setFormError(JSON.stringify(data));
        return;
      }
      const created: TillReconciliationItem = await resp.json();
      setRecords(prev => [created, ...prev]);
      setForm(emptyForm);
      setShowForm(false);
    } catch {
      setFormError('Failed to create reconciliation record.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Till Reconciliation</h1>
            <p className="mt-1 text-sm text-gray-500">Daily cash and card reconciliation records</p>
          </div>
          <button
            className="inline-flex items-center gap-2 rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-50"
            onClick={() => setShowForm(prev => !prev)}
          >
            <Receipt className="h-4 w-4" />
            {showForm ? 'Cancel' : 'New Reconciliation'}
          </button>
        </div>

        {/* New reconciliation form */}
        {showForm && (
          <form
            className="rounded-xl border border-gray-200 bg-white p-5 space-y-4"
            onSubmit={handleSubmit}
          >
            <h2 className="text-base font-bold text-gray-900">New Reconciliation</h2>
            {formError && (
              <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                {formError}
              </div>
            )}
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Date</label>
                <input
                  className="h-10 w-full rounded-lg border border-gray-200 px-3 text-sm"
                  onChange={e => updateField('recon_date', e.target.value)}
                  required
                  type="date"
                  value={form.recon_date}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Cash Counted (R)</label>
                <input
                  className="h-10 w-full rounded-lg border border-gray-200 px-3 text-sm"
                  min="0"
                  onChange={e => updateField('cash_counted', e.target.value)}
                  placeholder="0.00"
                  required
                  step="0.01"
                  type="number"
                  value={form.cash_counted}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Card Total (R)</label>
                <input
                  className="h-10 w-full rounded-lg border border-gray-200 px-3 text-sm"
                  min="0"
                  onChange={e => updateField('card_total', e.target.value)}
                  placeholder="0.00"
                  required
                  step="0.01"
                  type="number"
                  value={form.card_total}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">System Total (R)</label>
                <input
                  className="h-10 w-full rounded-lg border border-gray-200 px-3 text-sm"
                  min="0"
                  onChange={e => updateField('system_total', e.target.value)}
                  placeholder="0.00"
                  required
                  step="0.01"
                  type="number"
                  value={form.system_total}
                />
              </div>
            </div>
            {/* Computed variance preview */}
            {form.cash_counted && form.card_total && form.system_total && (
              <div className="text-sm text-gray-600">
                Computed variance:{' '}
                <span className={parseFloat(form.cash_counted) + parseFloat(form.card_total) - parseFloat(form.system_total) !== 0 ? 'font-bold text-red-600' : 'font-bold text-green-600'}>
                  R {(parseFloat(form.cash_counted) + parseFloat(form.card_total) - parseFloat(form.system_total)).toFixed(2)}
                </span>
              </div>
            )}
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">Variance Explanation</label>
              <textarea
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm min-h-20"
                onChange={e => updateField('variance_explained', e.target.value)}
                placeholder="Explain any variance..."
                value={form.variance_explained}
              />
            </div>
            <button
              className="inline-flex h-10 items-center rounded-lg bg-teal-700 px-5 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-50"
              disabled={submitting}
              type="submit"
            >
              {submitting ? 'Saving…' : 'Save Reconciliation'}
            </button>
          </form>
        )}

        {/* Summary strip */}
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">{records.length}</div>
            <div className="text-xs text-gray-500 mt-1">Reconciliations</div>
          </div>
          <div className={`rounded-xl border p-4 text-center ${Math.abs(totalVariance) > 0.01 ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}`}>
            <div className={`text-2xl font-bold ${Math.abs(totalVariance) > 0.01 ? 'text-red-700' : 'text-green-700'}`}>
              R {totalVariance.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
            </div>
            <div className={`text-xs mt-1 ${Math.abs(totalVariance) > 0.01 ? 'text-red-500' : 'text-green-600'}`}>
              Total Variance
            </div>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {records.filter(r => parseFloat(r.variance) === 0).length}
            </div>
            <div className="text-xs text-gray-500 mt-1">Balanced Records</div>
          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="text-sm text-gray-400 py-8 text-center">Loading reconciliations…</div>
        ) : records.length === 0 ? (
          <div className="flex flex-col items-center py-16 text-gray-400">
            <Receipt className="h-10 w-10 mb-3" />
            <p className="text-sm">No reconciliation records yet</p>
          </div>
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  {['Date', 'Cash', 'Card', 'System Total', 'Variance', 'Signed Off By'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {records.map(r => {
                  const variance = parseFloat(r.variance);
                  const hasVariance = Math.abs(variance) > 0.01;
                  return (
                    <tr key={r.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-xs text-gray-700">
                        {new Date(r.recon_date).toLocaleDateString('en-ZA')}
                      </td>
                      <td className="px-4 py-3 font-medium">
                        R {parseFloat(r.cash_counted).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 font-medium">
                        R {parseFloat(r.card_total).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 font-medium">
                        R {parseFloat(r.system_total).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`font-bold ${hasVariance ? 'text-red-600' : 'text-green-600'}`}>
                          R {variance.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                        </span>
                        {hasVariance && r.variance_explained && (
                          <div className="text-xs text-gray-400 mt-0.5 max-w-[200px] truncate" title={r.variance_explained}>
                            {r.variance_explained}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-600">{r.signed_off_by || '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
              {/* Summary row */}
              <tfoot className="border-t-2 border-gray-200 bg-gray-50">
                <tr>
                  <td className="px-4 py-3 text-xs font-semibold text-gray-600 uppercase">Totals</td>
                  <td className="px-4 py-3 font-bold">
                    R {records.reduce((s, r) => s + parseFloat(r.cash_counted || '0'), 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-3 font-bold">
                    R {records.reduce((s, r) => s + parseFloat(r.card_total || '0'), 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-3 font-bold">
                    R {records.reduce((s, r) => s + parseFloat(r.system_total || '0'), 0).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-bold ${Math.abs(totalVariance) > 0.01 ? 'text-red-600' : 'text-green-600'}`}>
                      R {totalVariance.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                    </span>
                  </td>
                  <td />
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </div>
    </AppShell>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchSetlistWorks, createSetlistWork, fetchSAMROReport } from '@/lib/api/endpoints';
import type { SetlistWork } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function licensingTone(body: string): 'info' | 'warning' | 'good' | 'neutral' {
  if (body === 'samro') return 'info';
  if (body === 'risa') return 'warning';
  if (body === 'capasso') return 'good';
  return 'neutral';
}

const LICENSING_BODIES = ['samro', 'risa', 'capasso', 'dalro', 'none'];

export default function SetlistPage() {
  const { tokens } = useAuth();
  const [works, setWorks] = useState<SetlistWork[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Form
  const [form, setForm] = useState({
    performance: '',
    title: '',
    composer: '',
    arranger: '',
    publisher: '',
    isrc_code: '',
    iswc_code: '',
    duration_minutes: '',
    licensing_body: 'samro',
    is_original_work: false,
    is_public_domain: false,
  });
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState('');

  // SAMRO report
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [report, setReport] = useState<{ works: Record<string, string>[]; total_works: number } | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    fetchSetlistWorks(tokens.access)
      .then((d) => setWorks(d.results ?? []))
      .catch(() => setError('Failed to load setlist works.'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tokens?.access) return;
    setSaving(true);
    setSaveError('');
    try {
      const created = await createSetlistWork(tokens.access, form);
      setWorks((prev) => [created, ...prev]);
      setForm({ performance: '', title: '', composer: '', arranger: '', publisher: '', isrc_code: '', iswc_code: '', duration_minutes: '', licensing_body: 'samro', is_original_work: false, is_public_domain: false });
    } catch {
      setSaveError('Failed to add work.');
    } finally {
      setSaving(false);
    }
  };

  const generateReport = async () => {
    if (!tokens?.access || !dateFrom || !dateTo) return;
    setReportLoading(true);
    setReportError('');
    try {
      const data = await fetchSAMROReport(tokens.access, dateFrom, dateTo);
      setReport(data);
    } catch {
      setReportError('Failed to generate report.');
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <AppShell pageTitle="Setlist Management">
      <PageHeader title="Setlist Management" description="Works performed and SAMRO/RISA/CAPASSO licensing data" />

      {/* Section 1 — Add Works */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Add Work to Setlist</h2>
        <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-lg p-4 mb-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Performance ID</label>
            <input className="w-full border border-gray-300 rounded px-3 py-2 text-sm" value={form.performance} onChange={(e) => setForm({ ...form, performance: e.target.value })} required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input className="w-full border border-gray-300 rounded px-3 py-2 text-sm" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Composer</label>
            <input className="w-full border border-gray-300 rounded px-3 py-2 text-sm" value={form.composer} onChange={(e) => setForm({ ...form, composer: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Arranger</label>
            <input className="w-full border border-gray-300 rounded px-3 py-2 text-sm" value={form.arranger} onChange={(e) => setForm({ ...form, arranger: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Publisher</label>
            <input className="w-full border border-gray-300 rounded px-3 py-2 text-sm" value={form.publisher} onChange={(e) => setForm({ ...form, publisher: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ISRC Code</label>
            <input className="w-full border border-gray-300 rounded px-3 py-2 text-sm" value={form.isrc_code} onChange={(e) => setForm({ ...form, isrc_code: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ISWC Code</label>
            <input className="w-full border border-gray-300 rounded px-3 py-2 text-sm" value={form.iswc_code} onChange={(e) => setForm({ ...form, iswc_code: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Duration (minutes)</label>
            <input type="number" className="w-full border border-gray-300 rounded px-3 py-2 text-sm" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Licensing Body</label>
            <select className="w-full border border-gray-300 rounded px-3 py-2 text-sm" value={form.licensing_body} onChange={(e) => setForm({ ...form, licensing_body: e.target.value })}>
              {LICENSING_BODIES.map((b) => <option key={b} value={b}>{b.toUpperCase()}</option>)}
            </select>
          </div>
          <div className="flex items-center gap-6 sm:col-span-2">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.is_original_work} onChange={(e) => setForm({ ...form, is_original_work: e.target.checked })} />
              Original Work
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.is_public_domain} onChange={(e) => setForm({ ...form, is_public_domain: e.target.checked })} />
              Public Domain
            </label>
          </div>
          <div className="sm:col-span-2 lg:col-span-3 flex items-center gap-4">
            <button type="submit" disabled={saving} className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50">
              {saving ? 'Adding...' : 'Add Work'}
            </button>
            {saveError && <span className="text-red-600 text-sm">{saveError}</span>}
          </div>
        </form>

        <h3 className="font-medium mb-3">Recent Works</h3>
        {loading && <LoadingState label="Loading works..." />}
        {error && <ErrorState message={error} />}
        {!loading && !error && works.length === 0 && <EmptyState title="No works yet" description="Add works using the form above." />}
        {!loading && works.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
              <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3 text-left">Title</th>
                  <th className="px-4 py-3 text-left">Composer</th>
                  <th className="px-4 py-3 text-left">Licensing Body</th>
                  <th className="px-4 py-3 text-left">Duration</th>
                  <th className="px-4 py-3 text-left">ISRC</th>
                  <th className="px-4 py-3 text-left">Flags</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {works.map((w) => (
                  <tr key={w.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{w.title}</td>
                    <td className="px-4 py-3 text-gray-600">{w.composer || '—'}</td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={licensingTone(w.licensing_body)}>{w.licensing_body.toUpperCase()}</StatusBadge>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{w.duration_minutes ? `${w.duration_minutes} min` : '—'}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">{w.isrc_code || '—'}</td>
                    <td className="px-4 py-3 flex gap-1">
                      {w.is_original_work && <StatusBadge tone="good">Original</StatusBadge>}
                      {w.is_public_domain && <StatusBadge tone="neutral">PD</StatusBadge>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Section 2 — SAMRO Report */}
      <section>
        <h2 className="text-lg font-semibold mb-4">SAMRO Report</h2>
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4 flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date From</label>
            <input type="date" className="border border-gray-300 rounded px-3 py-2 text-sm" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date To</label>
            <input type="date" className="border border-gray-300 rounded px-3 py-2 text-sm" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
          </div>
          <button onClick={generateReport} disabled={reportLoading || !dateFrom || !dateTo} className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50">
            {reportLoading ? 'Generating...' : 'Generate Report'}
          </button>
        </div>

        {reportError && <ErrorState message={reportError} />}

        {report && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm text-gray-600">Total works: <strong>{report.total_works}</strong></p>
              <button onClick={() => window.print()} className="border border-gray-300 px-3 py-1.5 rounded text-sm hover:bg-gray-50">Print Report</button>
            </div>
            {report.works.length === 0 ? (
              <EmptyState title="No works in this period" description="Adjust the date range and try again." />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
                  <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
                    <tr>
                      <th className="px-4 py-3 text-left">Perf. Date</th>
                      <th className="px-4 py-3 text-left">Title</th>
                      <th className="px-4 py-3 text-left">Composer</th>
                      <th className="px-4 py-3 text-left">Publisher</th>
                      <th className="px-4 py-3 text-left">ISRC</th>
                      <th className="px-4 py-3 text-left">Duration</th>
                      <th className="px-4 py-3 text-left">Licensing Body</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {report.works.map((w, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-4 py-3">{formatDate(w.performance_date)}</td>
                        <td className="px-4 py-3 font-medium">{w.title}</td>
                        <td className="px-4 py-3 text-gray-600">{w.composer || '—'}</td>
                        <td className="px-4 py-3 text-gray-600">{w.publisher || '—'}</td>
                        <td className="px-4 py-3 font-mono text-xs text-gray-500">{w.isrc_code || '—'}</td>
                        <td className="px-4 py-3">{w.duration_minutes ? `${w.duration_minutes} min` : '—'}</td>
                        <td className="px-4 py-3">
                          {w.licensing_body ? (
                            <StatusBadge tone={licensingTone(w.licensing_body)}>{w.licensing_body.toUpperCase()}</StatusBadge>
                          ) : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </section>
    </AppShell>
  );
}

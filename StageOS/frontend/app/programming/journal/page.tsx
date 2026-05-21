'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchJournalEntries, createJournalEntry, fetchOperatingContexts } from '@/lib/api/endpoints';
import type { ProductionJournalEntry, OperatingContextListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function entryTypeTone(type: string): StatusTone {
  switch (type) {
    case 'incident':
    case 'concern':
      return 'danger';
    case 'decision':
    case 'action':
      return 'warning';
    case 'achievement':
      return 'good';
    case 'change':
      return 'info';
    default:
      return 'neutral';
  }
}

const emptyForm = {
  entry_date: '',
  entry_type: 'general',
  title: '',
  body: '',
  requires_follow_up: false,
  follow_up_by: '',
  is_confidential: false,
};

export default function JournalPage() {
  const { tokens } = useAuth();
  const [entries, setEntries] = useState<ProductionJournalEntry[]>([]);
  const [contexts, setContexts] = useState<OperatingContextListItem[]>([]);
  const [selectedContext, setSelectedContext] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ ...emptyForm });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchOperatingContexts(tokens.access)
      .then((res) => setContexts(res.results))
      .catch(() => {});
  }, [tokens?.access]);

  useEffect(() => {
    if (!tokens?.access) return;
    setLoading(true);
    fetchJournalEntries(tokens.access, selectedContext || undefined)
      .then((res) => setEntries(res.results))
      .catch(() => setError('Failed to load journal entries'))
      .finally(() => setLoading(false));
  }, [tokens?.access, selectedContext]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setForm((prev) => ({ ...prev, [name]: checked }));
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const payload: Partial<ProductionJournalEntry> = {
        entry_date: form.entry_date,
        entry_type: form.entry_type,
        title: form.title,
        body: form.body,
        requires_follow_up: form.requires_follow_up,
        follow_up_by: form.requires_follow_up && form.follow_up_by ? form.follow_up_by : null,
        is_confidential: form.is_confidential,
        ...(selectedContext ? { operating_context: selectedContext } : {}),
      };
      const created = await createJournalEntry(tokens.access, payload);
      setEntries((prev) => [created, ...prev]);
      setForm({ ...emptyForm });
      setShowForm(false);
    } catch {
      setFormError('Failed to create entry. Please check your inputs.');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <AppShell><LoadingState label="Loading journal…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  return (
    <AppShell>
      <PageHeader
        title="Production Journal"
        description="Daily production diary — decisions, incidents, and notes"
      />

      {/* Context selector */}
      <div className="px-4 pb-3 flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Filter by production:</label>
          <select
            value={selectedContext}
            onChange={(e) => setSelectedContext(e.target.value)}
            className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All productions</option>
            {contexts.map((c) => (
              <option key={c.id} value={c.id}>{c.title}</option>
            ))}
          </select>
        </div>
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'Add Entry'}
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div className="mx-4 mb-4 rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900 mb-4">New Journal Entry</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Entry Date</label>
                <input
                  name="entry_date"
                  type="date"
                  value={form.entry_date}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Entry Type</label>
                <select
                  name="entry_type"
                  value={form.entry_type}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="general">General</option>
                  <option value="incident">Incident</option>
                  <option value="decision">Decision</option>
                  <option value="change">Change</option>
                  <option value="achievement">Achievement</option>
                  <option value="concern">Concern</option>
                  <option value="action">Action</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                name="title"
                type="text"
                value={form.title}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Body</label>
              <textarea
                name="body"
                value={form.body}
                onChange={handleChange}
                rows={4}
                required
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="requires_follow_up"
                name="requires_follow_up"
                checked={form.requires_follow_up}
                onChange={handleChange}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="requires_follow_up" className="text-sm font-medium text-gray-700">
                Requires Follow-up
              </label>
            </div>
            {form.requires_follow_up && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Follow-up By</label>
                <input
                  name="follow_up_by"
                  type="date"
                  value={form.follow_up_by}
                  onChange={handleChange}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_confidential"
                name="is_confidential"
                checked={form.is_confidential}
                onChange={handleChange}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="is_confidential" className="text-sm font-medium text-gray-700">
                Confidential
              </label>
            </div>
            {formError && <p className="text-sm text-red-600">{formError}</p>}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={submitting}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {submitting ? 'Saving…' : 'Save Entry'}
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

      {/* Journal entries */}
      {entries.length === 0 ? (
        <div className="px-4">
          <EmptyState title="No journal entries." description="Add the first production journal entry using the button above." />
        </div>
      ) : (
        <div className="px-4 pb-8 space-y-3">
          {entries.map((entry) => (
            <div key={entry.id} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-500 whitespace-nowrap">{formatDate(entry.entry_date)}</span>
                  <StatusBadge tone={entryTypeTone(entry.entry_type)}>
                    {entry.entry_type.replace(/_/g, ' ')}
                  </StatusBadge>
                  {entry.is_confidential && (
                    <StatusBadge tone="neutral">Confidential</StatusBadge>
                  )}
                </div>
                {entry.author && (
                  <span className="text-xs text-gray-400">{entry.author}</span>
                )}
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">{entry.title}</h4>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{entry.body}</p>
              {entry.requires_follow_up && !entry.follow_up_completed && (
                <div className="mt-2 inline-flex items-center gap-1 rounded bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 border border-yellow-200">
                  Follow-up required{entry.follow_up_by ? ` by ${formatDate(entry.follow_up_by)}` : ''}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}

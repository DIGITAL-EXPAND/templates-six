'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import {
  fetchComplaints,
  createComplaint,
  fetchAccessibilityRequirements,
} from '@/lib/api/endpoints';
import type { AudienceComplaint, AccessibilityRequirement } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function complaintStatusTone(s: string): StatusTone {
  switch (s) {
    case 'received': return 'neutral';
    case 'acknowledged': return 'info';
    case 'under_review': return 'warning';
    case 'resolved': return 'good';
    case 'escalated': return 'danger';
    case 'closed': return 'neutral';
    default: return 'neutral';
  }
}

function accessTypeTone(t: string): StatusTone {
  switch (t) {
    case 'wheelchair':
    case 'hearing_loop':
    case 'audio_description':
    case 'sign_language':
      return 'info';
    case 'relaxed':
      return 'good';
    default:
      return 'neutral';
  }
}

type Tab = 'complaints' | 'accessibility';

export default function ComplaintsPage() {
  const { tokens } = useAuth();
  const [tab, setTab] = useState<Tab>('complaints');
  const [complaints, setComplaints] = useState<AudienceComplaint[]>([]);
  const [accessibility, setAccessibility] = useState<AccessibilityRequirement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Log complaint form
  const [showForm, setShowForm] = useState(false);
  const [formDate, setFormDate] = useState('');
  const [formCategory, setFormCategory] = useState('general');
  const [formDescription, setFormDescription] = useState('');
  const [formName, setFormName] = useState('');
  const [formAnonymous, setFormAnonymous] = useState(false);
  const [formSubmitting, setFormSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.all([
      fetchComplaints(tokens.access).then((r) => setComplaints(r.results)),
      fetchAccessibilityRequirements(tokens.access).then((r) => setAccessibility(r.results)),
    ])
      .catch(() => setError('Failed to load complaints data'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  async function handleCreateComplaint() {
    if (!tokens?.access || !formDescription.trim()) return;
    setFormSubmitting(true);
    try {
      const c = await createComplaint(tokens.access, {
        complaint_date: formDate || new Date().toISOString().split('T')[0],
        category: formCategory,
        description: formDescription,
        complainant_name: formAnonymous ? '' : formName,
        is_anonymous: formAnonymous,
      });
      setComplaints((prev) => [c, ...prev]);
      setShowForm(false);
      setFormDate('');
      setFormCategory('general');
      setFormDescription('');
      setFormName('');
      setFormAnonymous(false);
    } catch {
      // ignore
    } finally {
      setFormSubmitting(false);
    }
  }

  if (loading) return <AppShell><LoadingState label="Loading complaints data…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  const received = complaints.filter((c) => c.status === 'received').length;
  const underReview = complaints.filter((c) => c.status === 'under_review').length;
  const resolved = complaints.filter((c) => c.status === 'resolved').length;
  const escalated = complaints.filter((c) => c.status === 'escalated').length;

  const tabs: { key: Tab; label: string }[] = [
    { key: 'complaints', label: 'Complaints' },
    { key: 'accessibility', label: 'Accessibility' },
  ];

  return (
    <AppShell>
      <PageHeader
        title="Audience Complaints & Accessibility"
        description="Log and manage audience complaints and accessibility requirements"
      />

      {/* Tab bar */}
      <div className="px-4 mb-4">
        <div className="flex gap-1 border-b border-gray-200">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="px-4 pb-6">

        {/* COMPLAINTS TAB */}
        {tab === 'complaints' && (
          <div className="space-y-4">
            {/* Summary strip */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Received</p>
                <p className="mt-1 text-2xl font-bold text-gray-900">{received}</p>
              </div>
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 shadow-sm">
                <p className="text-xs text-amber-600 uppercase tracking-wider">Under Review</p>
                <p className="mt-1 text-2xl font-bold text-amber-700">{underReview}</p>
              </div>
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
                <p className="text-xs text-emerald-600 uppercase tracking-wider">Resolved</p>
                <p className="mt-1 text-2xl font-bold text-emerald-700">{resolved}</p>
              </div>
              <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 shadow-sm">
                <p className="text-xs text-rose-600 uppercase tracking-wider">Escalated</p>
                <p className="mt-1 text-2xl font-bold text-rose-700">{escalated}</p>
              </div>
            </div>

            {/* Log Complaint toggle */}
            <div>
              <button
                onClick={() => setShowForm((v) => !v)}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                {showForm ? 'Cancel' : 'Log Complaint'}
              </button>
            </div>

            {showForm && (
              <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm space-y-3">
                <h3 className="text-sm font-semibold text-gray-800">New Complaint</h3>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Date</label>
                    <input
                      type="date"
                      className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                      value={formDate}
                      onChange={(e) => setFormDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Category</label>
                    <select
                      className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                      value={formCategory}
                      onChange={(e) => setFormCategory(e.target.value)}
                    >
                      <option value="general">General</option>
                      <option value="sound">Sound</option>
                      <option value="sightlines">Sightlines</option>
                      <option value="accessibility">Accessibility</option>
                      <option value="staff_behaviour">Staff Behaviour</option>
                      <option value="facilities">Facilities</option>
                      <option value="safety">Safety</option>
                      <option value="ticketing">Ticketing</option>
                      <option value="content">Content</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Complainant Name</label>
                    <input
                      className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                      value={formName}
                      onChange={(e) => setFormName(e.target.value)}
                      placeholder="Full name"
                      disabled={formAnonymous}
                    />
                  </div>
                  <div className="flex items-center gap-2 pt-5">
                    <input
                      type="checkbox"
                      id="anonymous"
                      checked={formAnonymous}
                      onChange={(e) => setFormAnonymous(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="anonymous" className="text-sm text-gray-700">Anonymous</label>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Description *</label>
                  <textarea
                    className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                    rows={3}
                    value={formDescription}
                    onChange={(e) => setFormDescription(e.target.value)}
                    placeholder="Describe the complaint in detail"
                  />
                </div>
                <button
                  onClick={handleCreateComplaint}
                  disabled={formSubmitting || !formDescription.trim()}
                  className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {formSubmitting ? 'Saving…' : 'Submit Complaint'}
                </button>
              </div>
            )}

            {complaints.length === 0 ? (
              <EmptyState title="No complaints" description="No audience complaints recorded." />
            ) : (
              <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <th className="px-4 py-3">Reference</th>
                      <th className="px-4 py-3">Date</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Complainant</th>
                      <th className="px-4 py-3">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {complaints.map((c) => (
                      <tr key={c.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-mono text-xs text-gray-600">{c.reference_number}</td>
                        <td className="px-4 py-3 text-gray-600">{formatDate(c.complaint_date)}</td>
                        <td className="px-4 py-3">
                          <StatusBadge tone="neutral">{c.category.replace(/_/g, ' ')}</StatusBadge>
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge tone={complaintStatusTone(c.status)}>{c.status.replace(/_/g, ' ')}</StatusBadge>
                        </td>
                        <td className="px-4 py-3 text-gray-600">{c.is_anonymous ? <span className="italic text-gray-400">Anonymous</span> : c.complainant_name || '—'}</td>
                        <td className="px-4 py-3 text-gray-600">
                          {c.description.length > 50 ? c.description.substring(0, 50) + '…' : c.description}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ACCESSIBILITY TAB */}
        {tab === 'accessibility' && (
          <div>
            {accessibility.length === 0 ? (
              <EmptyState title="No accessibility requirements" description="No accessibility requirements recorded." />
            ) : (
              <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <th className="px-4 py-3">Production</th>
                      <th className="px-4 py-3">Performance Date</th>
                      <th className="px-4 py-3">Requirement Type</th>
                      <th className="px-4 py-3">Patron Name</th>
                      <th className="px-4 py-3">Confirmed</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {accessibility.map((a) => (
                      <tr key={a.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-mono text-xs text-gray-600">{a.operating_context.substring(0, 8)}…</td>
                        <td className="px-4 py-3 text-gray-600">{formatDate(a.performance_date)}</td>
                        <td className="px-4 py-3">
                          <StatusBadge tone={accessTypeTone(a.requirement_type)}>{a.requirement_type.replace(/_/g, ' ')}</StatusBadge>
                        </td>
                        <td className="px-4 py-3 text-gray-900">{a.patron_name || '—'}</td>
                        <td className="px-4 py-3 text-center">
                          {a.is_confirmed
                            ? <span className="text-emerald-600 font-bold">✓</span>
                            : <span className="text-gray-400">—</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}

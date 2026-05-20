'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchRentalEnquiries, createRentalEnquiry } from '@/lib/api/endpoints';
import type { VenueRentalEnquiry } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function rentalStatusTone(status: string): StatusTone {
  switch (status) {
    case 'new': return 'info';
    case 'availability_checked':
    case 'quote_sent': return 'warning';
    case 'quote_accepted':
    case 'agreement_drafted':
    case 'agreement_signed': return 'info';
    case 'deposit_received':
    case 'confirmed':
    case 'completed': return 'good';
    case 'cancelled': return 'danger';
    default: return 'neutral';
  }
}

const emptyForm = {
  client_name: '',
  client_email: '',
  client_phone: '',
  client_organisation: '',
  event_type: '',
  event_name: '',
  event_date: '',
  expected_attendance: '',
  special_requirements: '',
  venue: '',
};

export default function VenueRentalsPage() {
  const { tokens } = useAuth();
  const [enquiries, setEnquiries] = useState<VenueRentalEnquiry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    fetchRentalEnquiries(tokens.access)
      .then((data) => setEnquiries(data.results))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setSubmitError('');
    try {
      const created = await createRentalEnquiry(tokens.access, {
        ...form,
        expected_attendance: parseInt(form.expected_attendance || '0', 10),
      });
      setEnquiries((prev) => [created, ...prev]);
      setForm(emptyForm);
      setShowForm(false);
    } catch {
      setSubmitError('Failed to create enquiry. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <PageHeader
          title="Venue Rentals"
          description="External rental enquiries and quote management"
        />
        <button
          onClick={() => setShowForm((v) => !v)}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'New Enquiry'}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="mb-6 rounded-lg border border-gray-200 bg-white p-6 space-y-4"
        >
          <h3 className="text-sm font-semibold text-gray-900">New Rental Enquiry</h3>
          {submitError && (
            <p className="text-sm text-red-600">{submitError}</p>
          )}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Client Name *</label>
              <input
                name="client_name"
                value={form.client_name}
                onChange={handleChange}
                required
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Client Email</label>
              <input
                name="client_email"
                type="email"
                value={form.client_email}
                onChange={handleChange}
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Client Phone</label>
              <input
                name="client_phone"
                value={form.client_phone}
                onChange={handleChange}
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Organisation</label>
              <input
                name="client_organisation"
                value={form.client_organisation}
                onChange={handleChange}
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Event Type *</label>
              <input
                name="event_type"
                value={form.event_type}
                onChange={handleChange}
                required
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Event Name *</label>
              <input
                name="event_name"
                value={form.event_name}
                onChange={handleChange}
                required
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Event Date *</label>
              <input
                name="event_date"
                type="date"
                value={form.event_date}
                onChange={handleChange}
                required
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Expected Attendance</label>
              <input
                name="expected_attendance"
                type="number"
                min="0"
                value={form.expected_attendance}
                onChange={handleChange}
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Venue</label>
              <input
                name="venue"
                value={form.venue}
                onChange={handleChange}
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Special Requirements</label>
            <textarea
              name="special_requirements"
              value={form.special_requirements}
              onChange={handleChange}
              rows={3}
              className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {submitting ? 'Submitting…' : 'Submit Enquiry'}
            </button>
            <button
              type="button"
              onClick={() => { setShowForm(false); setForm(emptyForm); setSubmitError(''); }}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading && <LoadingState label="Loading rental enquiries…" />}
      {error && <ErrorState message="Failed to load rental enquiries." />}
      {!loading && !error && enquiries.length === 0 && (
        <EmptyState
          title="No enquiries"
          description="No venue rental enquiries have been recorded yet."
        />
      )}

      {!loading && !error && enquiries.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr className="text-left text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-3 font-medium">Reference</th>
                <th className="px-4 py-3 font-medium">Client</th>
                <th className="px-4 py-3 font-medium">Event Name</th>
                <th className="px-4 py-3 font-medium">Event Type</th>
                <th className="px-4 py-3 font-medium">Date</th>
                <th className="px-4 py-3 font-medium">Attendance</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {enquiries.map((enq) => (
                <tr key={enq.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-gray-600">{enq.reference_number || '—'}</td>
                  <td className="px-4 py-3 text-gray-900">
                    <div className="font-medium">{enq.client_name}</div>
                    {enq.client_organisation && (
                      <div className="text-xs text-gray-500">{enq.client_organisation}</div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-700">{enq.event_name || '—'}</td>
                  <td className="px-4 py-3 text-gray-600">{enq.event_type || '—'}</td>
                  <td className="px-4 py-3 text-gray-600">{formatDate(enq.event_date)}</td>
                  <td className="px-4 py-3 text-gray-700">
                    {enq.expected_attendance ? enq.expected_attendance.toLocaleString() : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge tone={rentalStatusTone(enq.status)}>
                      {enq.status.replace(/_/g, ' ')}
                    </StatusBadge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  );
}

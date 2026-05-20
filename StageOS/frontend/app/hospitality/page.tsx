'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { useAuth } from '@/lib/auth/auth-provider';
import { createHospitalityRequest } from '@/lib/api/endpoints';

type HospitalityRequest = {
  id: string;
  request_type: string;
  event_date: string;
  guest_count: number;
  contact_name: string;
  contact_phone: string;
  status: 'draft' | 'submitted' | 'confirmed' | 'declined' | 'completed';
  assigned_to_name: string;
  operating_context_title: string;
};

const statusTone = {
  draft: 'neutral',
  submitted: 'info',
  confirmed: 'good',
  declined: 'danger',
  completed: 'good',
} as const;

const statusLabel = {
  draft: 'Draft',
  submitted: 'Submitted',
  confirmed: 'Confirmed',
  declined: 'Declined',
  completed: 'Completed',
} as const;

const typeLabel: Record<string, string> = {
  vip_hosting: 'VIP Hosting',
  catering: 'Catering',
  private_dining: 'Private Dining',
  restaurant_reservation: 'Restaurant Reservation',
  other: 'Other',
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

type FormState = {
  request_type: string;
  event_date: string;
  guest_count: string;
  contact_name: string;
  contact_phone: string;
  special_requirements: string;
};

const emptyForm: FormState = {
  request_type: 'vip_hosting',
  event_date: '',
  guest_count: '1',
  contact_name: '',
  contact_phone: '',
  special_requirements: '',
};

export default function HospitalityPage() {
  const { tokens } = useAuth();
  const [requests, setRequests] = useState<HospitalityRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New request form
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    fetch('/api/v1/hospitality/requests/', {
      headers: { Authorization: `Bearer ${tokens.access}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error('Failed to load hospitality requests');
        return r.json();
      })
      .then((data) => {
        setRequests(Array.isArray(data) ? data : (data.results ?? []));
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, [tokens?.access]);

  function handleFormChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tokens?.access) return;
    setFormError('');
    setSubmitting(true);
    try {
      const created = await createHospitalityRequest(tokens.access, {
        request_type: form.request_type,
        event_date: form.event_date,
        guest_count: parseInt(form.guest_count, 10),
        contact_name: form.contact_name,
        contact_phone: form.contact_phone || undefined,
        special_requirements: form.special_requirements || undefined,
      });
      // Add to list — back-fill missing fields with defaults
      setRequests((prev) => [
        {
          id: created.id,
          request_type: created.request_type,
          event_date: created.event_date,
          guest_count: parseInt(form.guest_count, 10),
          contact_name: created.contact_name,
          contact_phone: form.contact_phone,
          status: (created.status as HospitalityRequest['status']) ?? 'draft',
          assigned_to_name: '',
          operating_context_title: '',
        },
        ...prev,
      ]);
      setForm(emptyForm);
      setShowForm(false);
    } catch {
      setFormError('Failed to create request. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell pageTitle="Hospitality">
      <div className="space-y-6">
        <div className="flex items-start justify-between gap-4">
          <PageHeader
            title="Hospitality"
            description="VIP hosting, catering and event hospitality"
          />
          <button
            className="shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            onClick={() => setShowForm((v) => !v)}
          >
            {showForm ? 'Cancel' : 'New Request'}
          </button>
        </div>

        {/* ── New Request Form ── */}
        {showForm && (
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-base font-semibold text-gray-800">New Hospitality Request</h2>
            <form className="grid grid-cols-1 gap-4 sm:grid-cols-2" onSubmit={handleSubmit}>
              {/* Request Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="request_type">
                  Request Type
                </label>
                <select
                  className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  id="request_type"
                  name="request_type"
                  required
                  value={form.request_type}
                  onChange={handleFormChange}
                >
                  <option value="vip_hosting">VIP Hosting</option>
                  <option value="catering">Catering</option>
                  <option value="private_dining">Private Dining</option>
                  <option value="restaurant_reservation">Restaurant Reservation</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Event Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="event_date">
                  Event Date
                </label>
                <input
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  id="event_date"
                  name="event_date"
                  required
                  type="date"
                  value={form.event_date}
                  onChange={handleFormChange}
                />
              </div>

              {/* Guest Count */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="guest_count">
                  Guest Count
                </label>
                <input
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  id="guest_count"
                  min="1"
                  name="guest_count"
                  required
                  type="number"
                  value={form.guest_count}
                  onChange={handleFormChange}
                />
              </div>

              {/* Contact Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="contact_name">
                  Contact Name
                </label>
                <input
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  id="contact_name"
                  name="contact_name"
                  required
                  type="text"
                  value={form.contact_name}
                  onChange={handleFormChange}
                />
              </div>

              {/* Contact Phone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="contact_phone">
                  Contact Phone
                </label>
                <input
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  id="contact_phone"
                  name="contact_phone"
                  type="text"
                  value={form.contact_phone}
                  onChange={handleFormChange}
                />
              </div>

              {/* Special Requirements */}
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="special_requirements">
                  Special Requirements
                </label>
                <textarea
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  id="special_requirements"
                  name="special_requirements"
                  rows={3}
                  value={form.special_requirements}
                  onChange={handleFormChange}
                />
              </div>

              {formError && (
                <p className="sm:col-span-2 text-sm text-red-600">{formError}</p>
              )}

              <div className="sm:col-span-2 flex justify-end">
                <button
                  className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                  disabled={submitting}
                  type="submit"
                >
                  {submitting ? 'Submitting…' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        )}

        {loading && <LoadingState label="Loading hospitality requests..." />}
        {error && <ErrorState message={error} />}

        {!loading && !error && requests.length === 0 && (
          <EmptyState
            title="No hospitality requests yet"
            description="Create a new request to manage VIP hosting, catering and other hospitality services."
          />
        )}

        {!loading && !error && requests.length > 0 && (
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
            <table className="w-full text-sm">
              <caption className="sr-only">Hospitality requests list</caption>
              <thead className="border-b border-gray-100 bg-gray-50 text-left">
                <tr>
                  <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Contact</th>
                  <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Type</th>
                  <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Event Date</th>
                  <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Guests</th>
                  <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Production</th>
                  <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {requests.map((req) => (
                  <tr className="hover:bg-gray-50" key={req.id}>
                    <td className="px-4 py-3 font-medium text-gray-900">{req.contact_name}</td>
                    <td className="px-4 py-3 text-gray-600">{typeLabel[req.request_type] ?? req.request_type}</td>
                    <td className="px-4 py-3 text-gray-600">{formatDate(req.event_date)}</td>
                    <td className="px-4 py-3 text-gray-600">{req.guest_count}</td>
                    <td className="px-4 py-3 text-gray-500">{req.operating_context_title || '—'}</td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={statusTone[req.status] ?? 'neutral'}>
                        {statusLabel[req.status] ?? req.status}
                      </StatusBadge>
                    </td>
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

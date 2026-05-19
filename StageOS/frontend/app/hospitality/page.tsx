'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { useAuth } from '@/lib/auth/auth-provider';

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

export default function HospitalityPage() {
  const { tokens } = useAuth();
  const [requests, setRequests] = useState<HospitalityRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <AppShell pageTitle="Hospitality">
      <PageHeader
        title="Hospitality"
        description="VIP hosting, catering and event hospitality"
      />

      {loading && <LoadingState label="Loading hospitality requests..." />}
      {error && <ErrorState message={error} />}

      {!loading && !error && requests.length === 0 && (
        <EmptyState
          title="No hospitality requests yet"
          description="Create a new request to manage VIP hosting, catering and other hospitality services."
        />
      )}

      {!loading && !error && requests.length > 0 && (
        <div className="mt-6 overflow-hidden rounded-xl border border-gray-200 bg-white">
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
    </AppShell>
  );
}

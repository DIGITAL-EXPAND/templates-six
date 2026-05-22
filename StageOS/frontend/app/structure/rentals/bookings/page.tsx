'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchRentalBookings, fetchRentalInvoices, createRentalInvoice } from '@/lib/api/endpoints';
import type { RentalBooking, RentalInvoice } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const zar = (val: string) =>
  'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function bookingStatusTone(status: string): 'info' | 'warning' | 'good' | 'danger' | 'neutral' {
  if (status === 'confirmed') return 'info';
  if (status === 'setup_in_progress' || status === 'event_in_progress') return 'warning';
  if (status === 'completed') return 'good';
  if (status === 'cancelled') return 'danger';
  return 'neutral';
}

function invoiceTypeTone(type: string): 'info' | 'warning' | 'good' | 'neutral' {
  if (type === 'deposit') return 'info';
  if (type === 'balance') return 'warning';
  if (type === 'full') return 'good';
  return 'neutral';
}

const INVOICE_TYPES = ['deposit', 'balance', 'full'];

export default function RentalBookingsPage() {
  const { tokens } = useAuth();
  const [bookings, setBookings] = useState<RentalBooking[]>([]);
  const [invoices, setInvoices] = useState<RentalInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [invoiceTypes, setInvoiceTypes] = useState<Record<string, string>>({});
  const [creating, setCreating] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.allSettled([
      fetchRentalBookings(tokens.access),
      fetchRentalInvoices(tokens.access),
    ]).then(([bRes, iRes]) => {
      if (bRes.status === 'fulfilled') setBookings(bRes.value.results ?? []);
      if (iRes.status === 'fulfilled') setInvoices(iRes.value.results ?? []);
      if (bRes.status === 'rejected' && iRes.status === 'rejected') setError('Failed to load rental data.');
      setLoading(false);
    });
  }, [tokens?.access]);

  const handleCreateInvoice = async (bookingId: string) => {
    if (!tokens?.access) return;
    const type = invoiceTypes[bookingId] || 'deposit';
    setCreating(bookingId);
    try {
      const inv = await createRentalInvoice(tokens.access, bookingId, type);
      setInvoices((prev) => [inv, ...prev]);
    } catch {
      // silently fail
    } finally {
      setCreating(null);
    }
  };

  if (loading) return <AppShell pageTitle="Rental Bookings"><LoadingState label="Loading bookings..." /></AppShell>;
  if (error) return <AppShell pageTitle="Rental Bookings"><ErrorState message={error} /></AppShell>;

  return (
    <AppShell pageTitle="Rental Bookings">
      <PageHeader title="Rental Bookings" description="Confirmed bookings, invoices and payment tracking" />

      {/* Section 1 — Bookings */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Bookings</h2>
        {bookings.length === 0 ? (
          <EmptyState title="No bookings" description="Confirmed rental bookings will appear here." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
              <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3 text-left">Booking #</th>
                  <th className="px-4 py-3 text-left">Client (Enquiry)</th>
                  <th className="px-4 py-3 text-left">Confirmed Date</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-left">Contract</th>
                  <th className="px-4 py-3 text-left">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {bookings.map((b) => (
                  <tr key={b.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{b.booking_number}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">{b.enquiry.slice(0, 8)}…</td>
                    <td className="px-4 py-3">{formatDate(b.confirmed_date)}</td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={bookingStatusTone(b.status)}>{b.status.replace(/_/g, ' ')}</StatusBadge>
                    </td>
                    <td className="px-4 py-3">{b.contract_signed ? '✓' : '—'}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <select
                          className="border border-gray-300 rounded px-2 py-1 text-xs"
                          value={invoiceTypes[b.id] || 'deposit'}
                          onChange={(e) => setInvoiceTypes({ ...invoiceTypes, [b.id]: e.target.value })}
                        >
                          {INVOICE_TYPES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                        </select>
                        <button
                          onClick={() => handleCreateInvoice(b.id)}
                          disabled={creating === b.id}
                          className="text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 disabled:opacity-50"
                        >
                          {creating === b.id ? '...' : 'Create Invoice'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Section 2 — Invoices */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Invoices</h2>
        {invoices.length === 0 ? (
          <EmptyState title="No invoices" description="Invoices will appear here after creation." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
              <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
                <tr>
                  <th className="px-4 py-3 text-left">Invoice #</th>
                  <th className="px-4 py-3 text-left">Booking #</th>
                  <th className="px-4 py-3 text-left">Type</th>
                  <th className="px-4 py-3 text-left">Invoice Date</th>
                  <th className="px-4 py-3 text-left">Due Date</th>
                  <th className="px-4 py-3 text-right">Total</th>
                  <th className="px-4 py-3 text-left">Paid</th>
                  <th className="px-4 py-3 text-left">Paid Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {invoices.map((inv) => {
                  const booking = bookings.find((b) => b.id === inv.booking);
                  return (
                    <tr key={inv.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium">{inv.invoice_number}</td>
                      <td className="px-4 py-3 text-gray-600">{booking?.booking_number ?? inv.booking.slice(0, 8) + '…'}</td>
                      <td className="px-4 py-3">
                        <StatusBadge tone={invoiceTypeTone(inv.invoice_type)}>{inv.invoice_type.replace(/_/g, ' ')}</StatusBadge>
                      </td>
                      <td className="px-4 py-3">{formatDate(inv.invoice_date)}</td>
                      <td className="px-4 py-3">{formatDate(inv.due_date)}</td>
                      <td className="px-4 py-3 text-right">{zar(inv.total)}</td>
                      <td className="px-4 py-3">
                        <StatusBadge tone={inv.is_paid ? 'good' : 'danger'}>{inv.is_paid ? 'Paid' : 'Outstanding'}</StatusBadge>
                      </td>
                      <td className="px-4 py-3">{formatDate(inv.paid_date)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </AppShell>
  );
}

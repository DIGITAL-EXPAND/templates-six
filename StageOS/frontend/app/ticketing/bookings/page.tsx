'use client';
import { useEffect, useState } from 'react';
import { Users } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { useAuth } from '@/lib/auth/auth-provider';
import type { BookingItem } from '@/lib/api/types';

export default function BookingsPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';
  const [bookings, setBookings] = useState<BookingItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    fetch('/api/v1/ticketing/bookings/', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(data => setBookings(data.results ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const totalRevenue = bookings.reduce((sum, b) => sum + parseFloat(b.total_amount || '0'), 0);
  const totalTickets = bookings.reduce((sum, b) => sum + b.tickets.length, 0);

  return (
    <AppShell>
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Box Office Bookings</h1>
          <p className="mt-1 text-sm text-gray-500">Patron bookings across all productions</p>
        </div>

        {/* Summary strip */}
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">{bookings.length}</div>
            <div className="text-xs text-gray-500 mt-1">Total Bookings</div>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
            <div className="text-2xl font-bold text-teal-700">{totalTickets}</div>
            <div className="text-xs text-gray-500 mt-1">Tickets Sold</div>
          </div>
          <div className="rounded-xl border border-green-200 bg-green-50 p-4 text-center">
            <div className="text-2xl font-bold text-green-700">
              R {totalRevenue.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-green-600 mt-1">Total Revenue</div>
          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="text-sm text-gray-400 py-8 text-center">Loading bookings…</div>
        ) : bookings.length === 0 ? (
          <div className="flex flex-col items-center py-16 text-gray-400">
            <Users className="h-10 w-10 mb-3" />
            <p className="text-sm">No bookings yet</p>
          </div>
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  {['Reference', 'Patron', 'Channel', 'Tickets', 'Total', 'Date'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {bookings.map(b => (
                  <tr key={b.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">{b.booking_reference}</td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{b.patron_name}</div>
                      {b.patron_email && <div className="text-xs text-gray-400">{b.patron_email}</div>}
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs capitalize">{b.channel.replace(/_/g, ' ')}</span>
                    </td>
                    <td className="px-4 py-3 text-center font-medium">{b.tickets.length}</td>
                    <td className="px-4 py-3 font-semibold text-gray-900">
                      R {parseFloat(b.total_amount).toLocaleString('en-ZA', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {new Date(b.booked_at).toLocaleDateString('en-ZA')}
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

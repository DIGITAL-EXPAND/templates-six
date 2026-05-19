'use client';

import { useEffect, useState } from 'react';
import { Mail, Phone, Users } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { useAuth } from '@/lib/auth/auth-provider';
import type { PatronItem, PatronSummary } from '@/lib/api/types';

const SEGMENT_COLOURS: Record<string, string> = {
  general:    'bg-gray-100 text-gray-700',
  subscriber: 'bg-blue-100 text-blue-700',
  vip:        'bg-purple-100 text-purple-700',
  youth:      'bg-green-100 text-green-700',
  educator:   'bg-teal-100 text-teal-700',
  corporate:  'bg-orange-100 text-orange-700',
  media:      'bg-pink-100 text-pink-700',
  donor:      'bg-amber-100 text-amber-700',
};

const SEGMENT_LABELS: Record<string, string> = {
  general: 'General', subscriber: 'Subscriber', vip: 'VIP',
  youth: 'Youth', educator: 'Educator', corporate: 'Corporate',
  media: 'Media', donor: 'Donor',
};

function formatZAR(val: string | null | undefined) {
  if (!val) return 'R 0.00';
  return 'R ' + parseFloat(val).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

export default function PatronsPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';
  const [patrons, setPatrons] = useState<PatronItem[]>([]);
  const [summary, setSummary] = useState<PatronSummary | null>(null);
  const [search, setSearch] = useState('');
  const [segmentFilter, setSegmentFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    Promise.all([
      fetch('/api/v1/patrons/?page_size=100', { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch('/api/v1/patrons/summary/', { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
    ])
      .then(([patronData, summaryData]) => {
        if (!mounted) return;
        setPatrons(patronData.results ?? []);
        setSummary(summaryData);
      })
      .catch(() => {})
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token]);

  const filtered = patrons.filter(p => {
    const matchSearch = !search || p.full_name.toLowerCase().includes(search.toLowerCase()) || p.email.toLowerCase().includes(search.toLowerCase());
    const matchSegment = segmentFilter === 'all' || p.segment === segmentFilter;
    return matchSearch && matchSegment;
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Patron CRM</h1>
          <p className="mt-1 text-sm text-gray-500">Audience database, attendance history and communication records</p>
        </div>

        {/* Summary strip */}
        {summary && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
              <div className="text-2xl font-bold text-gray-900">{summary.total}</div>
              <div className="text-xs text-gray-500 mt-1">Total Patrons</div>
            </div>
            <div className="rounded-xl border border-teal-200 bg-teal-50 p-4 text-center">
              <div className="text-2xl font-bold text-teal-700">{summary.opted_in}</div>
              <div className="text-xs text-teal-600 mt-1">Marketing Opt-In</div>
            </div>
            <div className="rounded-xl border border-green-200 bg-green-50 p-4 text-center">
              <div className="text-2xl font-bold text-green-700">{formatZAR(summary.total_revenue)}</div>
              <div className="text-xs text-green-600 mt-1">Lifetime Revenue</div>
            </div>
            <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-center">
              <div className="text-2xl font-bold text-blue-700">{formatZAR(summary.avg_spend)}</div>
              <div className="text-xs text-blue-600 mt-1">Avg Spend/Patron</div>
            </div>
          </div>
        )}

        {/* Segment breakdown */}
        {summary && summary.by_segment.length > 0 && (
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <h2 className="mb-3 text-sm font-semibold text-gray-700">By Segment</h2>
            <div className="flex flex-wrap gap-2">
              {summary.by_segment.map(s => (
                <span key={s.segment} className={`rounded-full px-3 py-1 text-xs font-medium ${SEGMENT_COLOURS[s.segment] ?? 'bg-gray-100 text-gray-700'}`}>
                  {SEGMENT_LABELS[s.segment] ?? s.segment} ({s.count})
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap gap-3">
          <input
            className="h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-teal-500 focus:outline-none"
            onChange={e => setSearch(e.target.value)}
            placeholder="Search name or email…"
            type="search"
            value={search}
          />
          <select
            className="h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-teal-500 focus:outline-none"
            onChange={e => setSegmentFilter(e.target.value)}
            value={segmentFilter}
          >
            <option value="all">All segments</option>
            {Object.entries(SEGMENT_LABELS).map(([v, l]) => (
              <option key={v} value={v}>{l}</option>
            ))}
          </select>
        </div>

        {/* Patron list */}
        {loading ? (
          <div className="py-12 text-center text-sm text-gray-400">Loading patrons…</div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center py-16 text-gray-400">
            <Users className="h-10 w-10 mb-3" />
            <p className="text-sm">No patrons found</p>
          </div>
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  {['Name', 'Segment', 'Contact', 'Visits', 'Spend', 'Last Visit', 'POPIA'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{p.full_name}</div>
                      {p.city && <div className="text-xs text-gray-400">{p.city}</div>}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SEGMENT_COLOURS[p.segment] ?? 'bg-gray-100 text-gray-700'}`}>
                        {SEGMENT_LABELS[p.segment] ?? p.segment}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {p.email && <div className="flex items-center gap-1 text-xs text-gray-500"><Mail className="h-3 w-3" />{p.email}</div>}
                      {p.phone && <div className="flex items-center gap-1 text-xs text-gray-500"><Phone className="h-3 w-3" />{p.phone}</div>}
                    </td>
                    <td className="px-4 py-3 text-center font-medium text-gray-700">{p.total_bookings}</td>
                    <td className="px-4 py-3 font-semibold text-gray-800">{formatZAR(p.total_spend)}</td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {p.last_visit_date ? new Date(p.last_visit_date).toLocaleDateString('en-ZA') : '—'}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {p.popia_consent_given
                        ? <span className="text-green-600 text-xs font-medium">✓ Given</span>
                        : <span className="text-red-500 text-xs">Required</span>}
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

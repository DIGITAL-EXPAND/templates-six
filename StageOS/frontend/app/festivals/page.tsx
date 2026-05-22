'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchFestivals, fetchFestivalPasses, createFestivalPass } from '@/lib/api/endpoints';
import type { Festival, FestivalPass } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function festivalStatusTone(status: string): 'neutral' | 'info' | 'warning' | 'good' | 'danger' {
  if (status === 'planning') return 'neutral';
  if (status === 'open_submissions') return 'info';
  if (status === 'programme_finalised' || status === 'accreditation_open') return 'warning';
  if (status === 'in_progress' || status === 'completed') return 'good';
  if (status === 'cancelled') return 'danger';
  return 'neutral';
}

function passTypeTone(type: string): 'good' | 'info' | 'warning' | 'neutral' {
  if (type === 'artist' || type === 'full_festival') return 'good';
  if (type === 'press' || type === 'accreditation') return 'info';
  if (type === 'vip') return 'warning';
  return 'neutral';
}

const PASS_TYPES = ['artist', 'press', 'vip', 'full_festival', 'day_pass', 'accreditation', 'crew', 'volunteer'];

interface PassForm {
  pass_type: string;
  holder_name: string;
  holder_email: string;
  organisation_name: string;
  valid_days: string;
  venue_access: string;
}

const emptyForm = (): PassForm => ({
  pass_type: 'artist',
  holder_name: '',
  holder_email: '',
  organisation_name: '',
  valid_days: '',
  venue_access: '',
});

export default function FestivalsPage() {
  const { tokens } = useAuth();
  const [festivals, setFestivals] = useState<Festival[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeFestival, setActiveFestival] = useState<string | null>(null);
  const [passes, setPasses] = useState<Record<string, FestivalPass[]>>({});
  const [passLoading, setPassLoading] = useState<string | null>(null);
  const [showPassForm, setShowPassForm] = useState<string | null>(null);
  const [passForm, setPassForm] = useState<PassForm>(emptyForm());
  const [issuingPass, setIssuingPass] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchFestivals(tokens.access)
      .then((d) => setFestivals(d.results ?? []))
      .catch(() => setError('Failed to load festivals.'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  const loadPasses = async (festivalId: string) => {
    if (!tokens?.access || passes[festivalId]) return;
    setPassLoading(festivalId);
    try {
      const data = await fetchFestivalPasses(tokens.access, festivalId);
      setPasses((prev) => ({ ...prev, [festivalId]: data.results ?? [] }));
    } catch {
      // silently fail
    } finally {
      setPassLoading(null);
    }
  };

  const togglePasses = (festivalId: string) => {
    if (activeFestival === festivalId) {
      setActiveFestival(null);
    } else {
      setActiveFestival(festivalId);
      loadPasses(festivalId);
    }
  };

  const handleIssuePass = async (festivalId: string) => {
    if (!tokens?.access) return;
    setIssuingPass(true);
    try {
      const created = await createFestivalPass(tokens.access, { ...passForm, festival: festivalId });
      setPasses((prev) => ({ ...prev, [festivalId]: [created, ...(prev[festivalId] ?? [])] }));
      setPassForm(emptyForm());
      setShowPassForm(null);
    } catch {
      // silently fail
    } finally {
      setIssuingPass(false);
    }
  };

  if (loading) return <AppShell pageTitle="Festival Management"><LoadingState label="Loading festivals..." /></AppShell>;
  if (error) return <AppShell pageTitle="Festival Management"><ErrorState message={error} /></AppShell>;

  return (
    <AppShell pageTitle="Festival Management">
      <PageHeader title="Festival Management" description="Multi-venue festival programming and accreditation" />

      {festivals.length === 0 ? (
        <EmptyState title="No festivals" description="Festivals will appear here once created." />
      ) : (
        <div className="space-y-4">
          {festivals.map((f) => {
            const isActive = activeFestival === f.id;
            const festPasses = passes[f.id] ?? [];
            return (
              <div key={f.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="font-semibold text-lg">{f.name}</h3>
                        <StatusBadge tone={festivalStatusTone(f.status)}>{f.status.replace(/_/g, ' ')}</StatusBadge>
                      </div>
                      <p className="text-sm text-gray-500 mb-3">Edition: {f.edition}</p>
                      <div className="flex flex-wrap gap-6 text-sm text-gray-600">
                        <span><strong>Dates:</strong> {formatDate(f.start_date)} – {formatDate(f.end_date)}</span>
                        <span><strong>Expected Attendance:</strong> {f.expected_attendance.toLocaleString()}</span>
                        <span><strong>Max Accreditation:</strong> {f.max_accreditation.toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => togglePasses(f.id)}
                        className="text-sm border border-gray-300 px-3 py-1.5 rounded hover:bg-gray-50"
                      >
                        {isActive ? 'Hide Passes' : 'View Passes'}
                      </button>
                      <button className="text-sm border border-gray-300 px-3 py-1.5 rounded hover:bg-gray-50">
                        View Schedule
                      </button>
                    </div>
                  </div>
                </div>

                {isActive && (
                  <div className="border-t border-gray-100 bg-gray-50 p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-sm">Festival Passes</h4>
                      <button
                        onClick={() => setShowPassForm(showPassForm === f.id ? null : f.id)}
                        className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                      >
                        {showPassForm === f.id ? 'Cancel' : 'Issue Pass'}
                      </button>
                    </div>

                    {showPassForm === f.id && (
                      <div className="bg-white border border-gray-200 rounded p-4 mb-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Pass Type</label>
                          <select className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" value={passForm.pass_type} onChange={(e) => setPassForm({ ...passForm, pass_type: e.target.value })}>
                            {PASS_TYPES.map((t) => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
                          </select>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Holder Name</label>
                          <input className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" value={passForm.holder_name} onChange={(e) => setPassForm({ ...passForm, holder_name: e.target.value })} />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Holder Email</label>
                          <input type="email" className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" value={passForm.holder_email} onChange={(e) => setPassForm({ ...passForm, holder_email: e.target.value })} />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Organisation</label>
                          <input className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" value={passForm.organisation_name} onChange={(e) => setPassForm({ ...passForm, organisation_name: e.target.value })} />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Valid Days</label>
                          <input className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" value={passForm.valid_days} onChange={(e) => setPassForm({ ...passForm, valid_days: e.target.value })} />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Venue Access</label>
                          <input className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" value={passForm.venue_access} onChange={(e) => setPassForm({ ...passForm, venue_access: e.target.value })} />
                        </div>
                        <div className="sm:col-span-2 lg:col-span-3">
                          <button onClick={() => handleIssuePass(f.id)} disabled={issuingPass} className="bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50">
                            {issuingPass ? 'Issuing...' : 'Issue Pass'}
                          </button>
                        </div>
                      </div>
                    )}

                    {passLoading === f.id && <LoadingState label="Loading passes..." />}
                    {passLoading !== f.id && festPasses.length === 0 && <p className="text-sm text-gray-500">No passes issued yet.</p>}
                    {festPasses.length > 0 && (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="text-xs text-gray-500 uppercase">
                            <tr>
                              <th className="py-2 text-left">Pass #</th>
                              <th className="py-2 text-left">Type</th>
                              <th className="py-2 text-left">Holder</th>
                              <th className="py-2 text-left">Organisation</th>
                              <th className="py-2 text-left">Valid Days</th>
                              <th className="py-2 text-left">Venue Access</th>
                              <th className="py-2 text-left">Active</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-200">
                            {festPasses.map((p) => (
                              <tr key={p.id}>
                                <td className="py-2 font-mono text-xs">{p.pass_number}</td>
                                <td className="py-2"><StatusBadge tone={passTypeTone(p.pass_type)}>{p.pass_type.replace(/_/g, ' ')}</StatusBadge></td>
                                <td className="py-2">{p.holder_name}</td>
                                <td className="py-2 text-gray-600">{p.organisation_name || '—'}</td>
                                <td className="py-2 text-gray-600">{p.valid_days || '—'}</td>
                                <td className="py-2 text-gray-600">{p.venue_access || '—'}</td>
                                <td className="py-2"><StatusBadge tone={p.is_active ? 'good' : 'neutral'}>{p.is_active ? 'Active' : 'Inactive'}</StatusBadge></td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}

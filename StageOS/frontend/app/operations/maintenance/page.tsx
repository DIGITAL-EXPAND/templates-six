'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import {
  fetchMaintenanceTickets,
  createMaintenanceTicket,
  resolveMaintenanceTicket,
  fetchMaintenanceSchedules,
  fetchInspections,
  fetchVenueDowntime,
} from '@/lib/api/endpoints';
import type {
  MaintenanceTicket,
  MaintenanceSchedule,
  InspectionRecord,
  VenueDowntime,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function priorityTone(p: string): StatusTone {
  switch (p) {
    case 'critical': return 'danger';
    case 'high': return 'warning';
    case 'medium': return 'info';
    default: return 'neutral';
  }
}

function ticketStatusTone(s: string): StatusTone {
  switch (s) {
    case 'logged': return 'neutral';
    case 'assigned': return 'info';
    case 'in_progress': return 'warning';
    case 'awaiting_parts': return 'warning';
    case 'resolved': return 'good';
    case 'closed': return 'good';
    case 'escalated': return 'danger';
    default: return 'neutral';
  }
}

const CATEGORIES = [
  'electrical', 'plumbing', 'hvac', 'structural', 'rigging',
  'lighting_infrastructure', 'audio_infrastructure', 'stage_equipment',
  'foh_equipment', 'it_systems', 'fire_systems', 'general',
];

type Tab = 'tickets' | 'schedules' | 'inspections' | 'downtime';

export default function MaintenancePage() {
  const { tokens } = useAuth();
  const [tab, setTab] = useState<Tab>('tickets');

  const [tickets, setTickets] = useState<MaintenanceTicket[]>([]);
  const [schedules, setSchedules] = useState<MaintenanceSchedule[]>([]);
  const [inspections, setInspections] = useState<InspectionRecord[]>([]);
  const [downtime, setDowntime] = useState<VenueDowntime[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Ticket form state
  const [showForm, setShowForm] = useState(false);
  const [formTitle, setFormTitle] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formCategory, setFormCategory] = useState('general');
  const [formPriority, setFormPriority] = useState('medium');
  const [formVenue, setFormVenue] = useState('');
  const [formLocation, setFormLocation] = useState('');
  const [formImpacting, setFormImpacting] = useState(false);
  const [formSubmitting, setFormSubmitting] = useState(false);

  // Resolve state: ticketId -> notes text
  const [resolveNotes, setResolveNotes] = useState<Record<string, string>>({});
  const [resolveOpen, setResolveOpen] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.all([
      fetchMaintenanceTickets(tokens.access).then((r) => setTickets(r.results)),
      fetchMaintenanceSchedules(tokens.access).then((r) => setSchedules(r.results)),
      fetchInspections(tokens.access).then((r) => setInspections(r.results)),
      fetchVenueDowntime(tokens.access).then((r) => setDowntime(r.results)),
    ])
      .catch(() => setError('Failed to load maintenance data'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  async function handleCreateTicket() {
    if (!tokens?.access || !formTitle.trim()) return;
    setFormSubmitting(true);
    try {
      const t = await createMaintenanceTicket(tokens.access, {
        title: formTitle,
        description: formDescription,
        category: formCategory,
        priority: formPriority as MaintenanceTicket['priority'],
        venue: formVenue || null,
        location_detail: formLocation,
        is_production_impacting: formImpacting,
      });
      setTickets((prev) => [t, ...prev]);
      setShowForm(false);
      setFormTitle('');
      setFormDescription('');
      setFormCategory('general');
      setFormPriority('medium');
      setFormVenue('');
      setFormLocation('');
      setFormImpacting(false);
    } catch {
      // ignore
    } finally {
      setFormSubmitting(false);
    }
  }

  async function handleResolve(id: string) {
    if (!tokens?.access) return;
    try {
      const updated = await resolveMaintenanceTicket(tokens.access, id, resolveNotes[id] ?? '');
      setTickets((prev) => prev.map((t) => (t.id === id ? updated : t)));
      setResolveOpen((prev) => ({ ...prev, [id]: false }));
    } catch {
      // ignore
    }
  }

  if (loading) return <AppShell><LoadingState label="Loading maintenance data…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  const openTickets = tickets.filter((t) => !['resolved', 'closed'].includes(t.status));
  const criticalTickets = tickets.filter((t) => t.priority === 'critical' && !['resolved', 'closed'].includes(t.status));
  const impactingTickets = tickets.filter((t) => t.is_production_impacting && !['resolved', 'closed'].includes(t.status));
  const today = new Date().toISOString().split('T')[0];
  const overdueTickets = tickets.filter((t) => t.target_resolution_date && t.target_resolution_date < today && !['resolved', 'closed'].includes(t.status));

  const tabs: { key: Tab; label: string }[] = [
    { key: 'tickets', label: 'Tickets' },
    { key: 'schedules', label: 'Schedules' },
    { key: 'inspections', label: 'Inspections' },
    { key: 'downtime', label: 'Downtime' },
  ];

  return (
    <AppShell>
      <PageHeader
        title="Maintenance & Facilities"
        description="Maintenance tickets, schedules, inspections, and venue downtime"
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

        {/* TICKETS TAB */}
        {tab === 'tickets' && (
          <div className="space-y-4">
            {/* Summary strip */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Total Open</p>
                <p className="mt-1 text-2xl font-bold text-gray-900">{openTickets.length}</p>
              </div>
              <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 shadow-sm">
                <p className="text-xs text-rose-600 uppercase tracking-wider">Critical</p>
                <p className="mt-1 text-2xl font-bold text-rose-700">{criticalTickets.length}</p>
              </div>
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 shadow-sm">
                <p className="text-xs text-amber-600 uppercase tracking-wider">Production Impacting</p>
                <p className="mt-1 text-2xl font-bold text-amber-700">{impactingTickets.length}</p>
              </div>
              <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 shadow-sm">
                <p className="text-xs text-rose-600 uppercase tracking-wider">Overdue</p>
                <p className="mt-1 text-2xl font-bold text-rose-700">{overdueTickets.length}</p>
              </div>
            </div>

            {/* Log Ticket toggle */}
            <div>
              <button
                onClick={() => setShowForm((v) => !v)}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                {showForm ? 'Cancel' : 'Log Ticket'}
              </button>
            </div>

            {showForm && (
              <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm space-y-3">
                <h3 className="text-sm font-semibold text-gray-800">New Maintenance Ticket</h3>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Title *</label>
                    <input
                      className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                      value={formTitle}
                      onChange={(e) => setFormTitle(e.target.value)}
                      placeholder="Brief title"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Category</label>
                    <select
                      className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                      value={formCategory}
                      onChange={(e) => setFormCategory(e.target.value)}
                    >
                      {CATEGORIES.map((c) => (
                        <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Priority</label>
                    <select
                      className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                      value={formPriority}
                      onChange={(e) => setFormPriority(e.target.value)}
                    >
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Venue</label>
                    <input
                      className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                      value={formVenue}
                      onChange={(e) => setFormVenue(e.target.value)}
                      placeholder="Venue name"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Location Detail</label>
                    <input
                      className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                      value={formLocation}
                      onChange={(e) => setFormLocation(e.target.value)}
                      placeholder="E.g. Stage right, fly floor"
                    />
                  </div>
                  <div className="flex items-center gap-2 pt-5">
                    <input
                      type="checkbox"
                      id="impacting"
                      checked={formImpacting}
                      onChange={(e) => setFormImpacting(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="impacting" className="text-sm text-gray-700">Production Impacting</label>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
                  <textarea
                    className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                    rows={3}
                    value={formDescription}
                    onChange={(e) => setFormDescription(e.target.value)}
                    placeholder="Detailed description of the issue"
                  />
                </div>
                <button
                  onClick={handleCreateTicket}
                  disabled={formSubmitting || !formTitle.trim()}
                  className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {formSubmitting ? 'Saving…' : 'Submit Ticket'}
                </button>
              </div>
            )}

            {tickets.length === 0 ? (
              <EmptyState title="No tickets" description="No maintenance tickets found." />
            ) : (
              <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <th className="px-4 py-3">Ticket #</th>
                      <th className="px-4 py-3">Title</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Priority</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Venue</th>
                      <th className="px-4 py-3">Impact</th>
                      <th className="px-4 py-3">Target Date</th>
                      <th className="px-4 py-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {tickets.map((ticket) => (
                      <>
                        <tr key={ticket.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-mono text-xs text-gray-600">{ticket.ticket_number}</td>
                          <td className="px-4 py-3 font-medium text-gray-900">{ticket.title}</td>
                          <td className="px-4 py-3 text-gray-600 capitalize">{ticket.category.replace(/_/g, ' ')}</td>
                          <td className="px-4 py-3">
                            <StatusBadge tone={priorityTone(ticket.priority)}>{ticket.priority}</StatusBadge>
                          </td>
                          <td className="px-4 py-3">
                            <StatusBadge tone={ticketStatusTone(ticket.status)}>{ticket.status.replace(/_/g, ' ')}</StatusBadge>
                          </td>
                          <td className="px-4 py-3 text-gray-600">{ticket.venue ?? '—'}</td>
                          <td className="px-4 py-3 text-center">{ticket.is_production_impacting ? '⚠' : ''}</td>
                          <td className={`px-4 py-3 ${ticket.target_resolution_date && ticket.target_resolution_date < today && !['resolved','closed'].includes(ticket.status) ? 'text-rose-600 font-semibold' : 'text-gray-600'}`}>
                            {formatDate(ticket.target_resolution_date)}
                          </td>
                          <td className="px-4 py-3">
                            {!['resolved', 'closed'].includes(ticket.status) && (
                              <button
                                onClick={() => setResolveOpen((prev) => ({ ...prev, [ticket.id]: !prev[ticket.id] }))}
                                className="rounded bg-emerald-600 px-2 py-1 text-xs font-medium text-white hover:bg-emerald-700"
                              >
                                Resolve
                              </button>
                            )}
                          </td>
                        </tr>
                        {resolveOpen[ticket.id] && (
                          <tr key={`${ticket.id}-resolve`} className="bg-emerald-50">
                            <td colSpan={9} className="px-4 py-3">
                              <div className="flex gap-2 items-end">
                                <div className="flex-1">
                                  <label className="block text-xs font-medium text-gray-600 mb-1">Resolution Notes</label>
                                  <textarea
                                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
                                    rows={2}
                                    value={resolveNotes[ticket.id] ?? ''}
                                    onChange={(e) => setResolveNotes((prev) => ({ ...prev, [ticket.id]: e.target.value }))}
                                    placeholder="Describe how the issue was resolved"
                                  />
                                </div>
                                <button
                                  onClick={() => handleResolve(ticket.id)}
                                  className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
                                >
                                  Confirm
                                </button>
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* SCHEDULES TAB */}
        {tab === 'schedules' && (
          <div>
            {schedules.length === 0 ? (
              <EmptyState title="No schedules" description="No maintenance schedules configured." />
            ) : (
              <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <th className="px-4 py-3">Title</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Frequency</th>
                      <th className="px-4 py-3">Last Completed</th>
                      <th className="px-4 py-3">Next Due</th>
                      <th className="px-4 py-3">Active</th>
                      <th className="px-4 py-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {schedules.map((s) => {
                      const overdue = s.next_due_date && s.next_due_date < today;
                      return (
                        <tr key={s.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-medium text-gray-900">{s.title}</td>
                          <td className="px-4 py-3 text-gray-600 capitalize">{s.category.replace(/_/g, ' ')}</td>
                          <td className="px-4 py-3">
                            <StatusBadge tone="info">{s.frequency.replace(/_/g, ' ')}</StatusBadge>
                          </td>
                          <td className="px-4 py-3 text-gray-600">{formatDate(s.last_completed_date)}</td>
                          <td className={`px-4 py-3 font-medium ${overdue ? 'text-rose-600' : 'text-gray-700'}`}>
                            {formatDate(s.next_due_date)}
                          </td>
                          <td className="px-4 py-3">
                            <StatusBadge tone={s.is_active ? 'good' : 'neutral'}>
                              {s.is_active ? 'Active' : 'Inactive'}
                            </StatusBadge>
                          </td>
                          <td className="px-4 py-3">
                            <button className="rounded bg-blue-600 px-2 py-1 text-xs font-medium text-white hover:bg-blue-700">
                              Mark Complete
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* INSPECTIONS TAB */}
        {tab === 'inspections' && (
          <div>
            {inspections.length === 0 ? (
              <EmptyState title="No inspections" description="No inspection records found." />
            ) : (
              <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <th className="px-4 py-3">Type</th>
                      <th className="px-4 py-3">Venue</th>
                      <th className="px-4 py-3">Date</th>
                      <th className="px-4 py-3">Inspector</th>
                      <th className="px-4 py-3">Passed</th>
                      <th className="px-4 py-3">Certificate #</th>
                      <th className="px-4 py-3">Expiry Date</th>
                      <th className="px-4 py-3">Next Due</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {inspections.map((ins) => {
                      const thirtyDays = new Date();
                      thirtyDays.setDate(thirtyDays.getDate() + 30);
                      const expiryDate = ins.expiry_date ? new Date(ins.expiry_date) : null;
                      const expiringSoon = expiryDate && expiryDate <= thirtyDays;
                      return (
                        <tr key={ins.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-gray-900 capitalize">{ins.inspection_type.replace(/_/g, ' ')}</td>
                          <td className="px-4 py-3 text-gray-600">{ins.venue}</td>
                          <td className="px-4 py-3 text-gray-600">{formatDate(ins.inspection_date)}</td>
                          <td className="px-4 py-3 text-gray-600">{ins.inspector_name}</td>
                          <td className="px-4 py-3 text-center">
                            {ins.passed
                              ? <span className="text-emerald-600 font-bold">✓</span>
                              : <span className="text-rose-600 font-bold">✗</span>}
                          </td>
                          <td className="px-4 py-3 font-mono text-xs text-gray-600">{ins.certificate_number || '—'}</td>
                          <td className={`px-4 py-3 font-medium ${expiringSoon ? 'text-rose-600' : 'text-gray-700'}`}>
                            {formatDate(ins.expiry_date)}
                          </td>
                          <td className="px-4 py-3 text-gray-600">{formatDate(ins.next_inspection_date)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* DOWNTIME TAB */}
        {tab === 'downtime' && (
          <div>
            {downtime.length === 0 ? (
              <EmptyState title="No downtime records" description="No venue downtime recorded." />
            ) : (
              <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <th className="px-4 py-3">Venue</th>
                      <th className="px-4 py-3">Reason</th>
                      <th className="px-4 py-3">Start</th>
                      <th className="px-4 py-3">End</th>
                      <th className="px-4 py-3">Hours</th>
                      <th className="px-4 py-3">Production Impact</th>
                      <th className="px-4 py-3">Resolved</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {downtime.map((d) => (
                      <tr key={d.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium text-gray-900">{d.venue}</td>
                        <td className="px-4 py-3 text-gray-600">{d.reason}</td>
                        <td className="px-4 py-3 text-gray-600">{formatDate(d.start_datetime)}</td>
                        <td className="px-4 py-3 text-gray-600">{d.end_datetime ? formatDate(d.end_datetime) : <span className="text-amber-600 font-semibold">Ongoing</span>}</td>
                        <td className="px-4 py-3 text-gray-600">{d.downtime_hours != null ? d.downtime_hours.toFixed(1) : '—'}</td>
                        <td className="px-4 py-3 text-gray-600">{d.production_impact || '—'}</td>
                        <td className="px-4 py-3">
                          <StatusBadge tone={d.is_resolved ? 'good' : 'warning'}>
                            {d.is_resolved ? 'Resolved' : 'Active'}
                          </StatusBadge>
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

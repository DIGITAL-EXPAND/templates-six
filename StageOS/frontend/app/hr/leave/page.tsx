'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchLeaveRequests, createLeaveRequest, approveLeaveRequest } from '@/lib/api/endpoints';
import type { LeaveRequest } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function leaveTypeTone(type: string): StatusTone {
  switch (type) {
    case 'annual': return 'info';
    case 'sick': return 'warning';
    case 'maternity':
    case 'paternity': return 'good';
    case 'study': return 'info';
    case 'unpaid':
    case 'family':
    case 'other': return 'neutral';
    default: return 'neutral';
  }
}

function leaveStatusTone(status: string): StatusTone {
  switch (status) {
    case 'pending': return 'warning';
    case 'approved': return 'good';
    case 'declined': return 'danger';
    case 'cancelled': return 'neutral';
    case 'in_progress':
    case 'completed': return 'good';
    default: return 'neutral';
  }
}

const emptyForm = {
  leave_type: 'annual',
  start_date: '',
  end_date: '',
  days_requested: '',
  reason: '',
};

export default function LeavePage() {
  const { tokens } = useAuth();
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ ...emptyForm });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [approvingId, setApprovingId] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchLeaveRequests(tokens.access)
      .then((res) => setRequests(res.results))
      .catch(() => setError('Failed to load leave requests'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const created = await createLeaveRequest(tokens.access, {
        leave_type: form.leave_type,
        start_date: form.start_date,
        end_date: form.end_date,
        days_requested: form.days_requested,
        reason: form.reason,
      });
      setRequests((prev) => [created, ...prev]);
      setForm({ ...emptyForm });
      setShowForm(false);
    } catch {
      setFormError('Failed to submit leave request.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleApprove(id: string) {
    if (!tokens?.access) return;
    setApprovingId(id);
    try {
      const updated = await approveLeaveRequest(tokens.access, id);
      setRequests((prev) => prev.map((r) => (r.id === id ? updated : r)));
    } catch {
      // silently ignore
    } finally {
      setApprovingId(null);
    }
  }

  if (loading) return <AppShell><LoadingState label="Loading leave requests…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  const pending = requests.filter((r) => r.status === 'pending').length;
  const approved = requests.filter((r) => r.status === 'approved').length;
  const declined = requests.filter((r) => r.status === 'declined').length;
  const totalDaysApproved = requests
    .filter((r) => r.status === 'approved')
    .reduce((sum, r) => sum + parseFloat(r.days_requested || '0'), 0);

  return (
    <AppShell>
      <PageHeader
        title="Leave Management"
        description="Staff leave requests and approvals"
      />

      {/* Summary strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Pending</div>
          <div className="text-2xl font-bold text-yellow-600">{pending}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Approved</div>
          <div className="text-2xl font-bold text-green-600">{approved}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Declined</div>
          <div className="text-2xl font-bold text-red-600">{declined}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Total Days Approved</div>
          <div className="text-2xl font-bold text-gray-900">{totalDaysApproved}</div>
        </div>
      </div>

      {/* Apply button */}
      <div className="px-4 pb-2">
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'Apply for Leave'}
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div className="mx-4 mb-4 rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Leave Application</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Leave Type</label>
                <select
                  name="leave_type"
                  value={form.leave_type}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="annual">Annual Leave</option>
                  <option value="sick">Sick Leave</option>
                  <option value="maternity">Maternity Leave</option>
                  <option value="paternity">Paternity Leave</option>
                  <option value="study">Study Leave</option>
                  <option value="unpaid">Unpaid Leave</option>
                  <option value="family">Family Responsibility</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Days Requested</label>
                <input
                  name="days_requested"
                  type="number"
                  min="0.5"
                  step="0.5"
                  value={form.days_requested}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                <input
                  name="start_date"
                  type="date"
                  value={form.start_date}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input
                  name="end_date"
                  type="date"
                  value={form.end_date}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
              <textarea
                name="reason"
                value={form.reason}
                onChange={handleChange}
                rows={3}
                required
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            {formError && <p className="text-sm text-red-600">{formError}</p>}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={submitting}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {submitting ? 'Submitting…' : 'Submit Application'}
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

      {/* Leave requests table */}
      {requests.length === 0 ? (
        <div className="px-4">
          <EmptyState title="No leave requests." description="Use 'Apply for Leave' to submit a new request." />
        </div>
      ) : (
        <div className="px-4 pb-8">
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">Employee</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Start</th>
                  <th className="px-4 py-3">End</th>
                  <th className="px-4 py-3">Days</th>
                  <th className="px-4 py-3">Reason</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {requests.map((req) => (
                  <tr key={req.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">
                      {req.employee_name ?? req.employee.slice(0, 8)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={leaveTypeTone(req.leave_type)}>
                        {req.leave_type.replace(/_/g, ' ')}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge tone={leaveStatusTone(req.status)}>
                        {req.status.replace(/_/g, ' ')}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-gray-600">{formatDate(req.start_date)}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-gray-600">{formatDate(req.end_date)}</td>
                    <td className="px-4 py-3 text-gray-700">{req.days_requested}</td>
                    <td className="px-4 py-3 text-gray-600 max-w-xs">
                      {req.reason.length > 40 ? req.reason.slice(0, 40) + '…' : req.reason}
                    </td>
                    <td className="px-4 py-3">
                      {req.status === 'pending' && (
                        <button
                          onClick={() => handleApprove(req.id)}
                          disabled={approvingId === req.id}
                          className="rounded-md bg-green-600 px-3 py-1 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
                        >
                          {approvingId === req.id ? 'Approving…' : 'Approve'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AppShell>
  );
}

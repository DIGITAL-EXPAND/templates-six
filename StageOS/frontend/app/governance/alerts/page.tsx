'use client';
import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchExpiryAlerts, acknowledgeExpiryAlert, fetchOverdueTasks } from '@/lib/api/endpoints';
import type { ExpiryAlert } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';
type OverdueTask = { id: string; title: string; due_date: string; days_overdue: number; status: string };

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function alertTypeTone(alertType: string): StatusTone {
  switch (alertType) {
    case 'csd_verification':
    case 'tax_clearance':
      return 'danger';
    case 'liquor_licence':
    case 'safety_cert':
    case 'board_term':
    case 'contract':
      return 'warning';
    case 'bee_certificate':
      return 'info';
    default:
      return 'neutral';
  }
}

function daysRemainingClass(days: number): string {
  if (days <= 7) return 'font-bold text-red-600';
  if (days <= 30) return 'font-semibold text-amber-600';
  return 'text-emerald-600';
}

function taskStatusTone(status: string): StatusTone {
  switch (status) {
    case 'open': return 'info';
    case 'in_progress': return 'warning';
    case 'blocked': return 'danger';
    case 'done': return 'good';
    case 'cancelled': return 'neutral';
    default: return 'neutral';
  }
}

export default function ExpiryAlertsPage() {
  const { tokens } = useAuth();

  // Expiry Alerts
  const [alerts, setAlerts] = useState<ExpiryAlert[]>([]);
  const [alertsLoading, setAlertsLoading] = useState(true);
  const [alertsError, setAlertsError] = useState<string | null>(null);
  const [acknowledgingId, setAcknowledgingId] = useState<string | null>(null);

  // Overdue Tasks
  const [overdueTasks, setOverdueTasks] = useState<OverdueTask[]>([]);
  const [tasksLoading, setTasksLoading] = useState(true);
  const [tasksError, setTasksError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchExpiryAlerts(tokens.access)
      .then((data) => setAlerts(Array.isArray(data) ? data : []))
      .catch(() => setAlertsError('Failed to load expiry alerts'))
      .finally(() => setAlertsLoading(false));

    fetchOverdueTasks(tokens.access)
      .then((data) => setOverdueTasks(data.overdue_tasks ?? []))
      .catch(() => setTasksError('Failed to load overdue tasks'))
      .finally(() => setTasksLoading(false));
  }, [tokens?.access]);

  async function handleAcknowledge(id: string) {
    if (!tokens?.access) return;
    setAcknowledgingId(id);
    try {
      const updated = await acknowledgeExpiryAlert(tokens.access, id);
      setAlerts((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch {
      // silent
    } finally {
      setAcknowledgingId(null);
    }
  }

  const unacknowledged = useMemo(() => alerts.filter((a) => !a.is_acknowledged), [alerts]);
  const acknowledged = useMemo(() => alerts.filter((a) => a.is_acknowledged), [alerts]);

  const today = new Date();
  const criticalCount = unacknowledged.filter((a) => {
    const diff = Math.ceil((new Date(a.expiry_date).getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diff <= 7;
  }).length;
  const thisMonthCount = unacknowledged.filter((a) => {
    const diff = Math.ceil((new Date(a.expiry_date).getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diff > 7 && diff <= 30;
  }).length;

  const sortedOverdue = useMemo(
    () => [...overdueTasks].sort((a, b) => b.days_overdue - a.days_overdue),
    [overdueTasks],
  );

  return (
    <AppShell pageTitle="Expiry & Compliance Alerts">
      <div className="space-y-8">
        {/* Section 1 — Expiry Alerts */}
        <section className="space-y-4">
          <PageHeader
            title="Expiry & Compliance Alerts"
            description="Track upcoming expiries and compliance deadlines"
          />

          {alertsLoading ? (
            <LoadingState label="Loading alerts…" />
          ) : alertsError ? (
            <ErrorState message={alertsError} />
          ) : (
            <>
              {/* Summary Strip */}
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-center">
                  <div className="text-2xl font-bold text-red-700">{criticalCount}</div>
                  <div className="text-xs font-medium text-red-600 mt-1">Critical (≤7 days)</div>
                </div>
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-center">
                  <div className="text-2xl font-bold text-amber-700">{thisMonthCount}</div>
                  <div className="text-xs font-medium text-amber-600 mt-1">This Month (≤30 days)</div>
                </div>
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-center">
                  <div className="text-2xl font-bold text-emerald-700">{acknowledged.length}</div>
                  <div className="text-xs font-medium text-emerald-600 mt-1">Acknowledged</div>
                </div>
              </div>

              {unacknowledged.length === 0 ? (
                <EmptyState title="No upcoming expiry alerts" description="All alerts have been acknowledged or there are none due." />
              ) : (
                <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
                  <table className="min-w-full divide-y divide-slate-200 text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        {['Type', 'Description', 'Expiry Date', 'Days Remaining', 'Actions'].map((h) => (
                          <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {unacknowledged.map((a) => {
                        const daysRemaining = Math.ceil(
                          (new Date(a.expiry_date).getTime() - today.getTime()) / (1000 * 60 * 60 * 24),
                        );
                        return (
                          <tr key={a.id} className="hover:bg-slate-50">
                            <td className="px-3 py-2">
                              <StatusBadge tone={alertTypeTone(a.alert_type)}>
                                {a.alert_type.replaceAll('_', ' ')}
                              </StatusBadge>
                            </td>
                            <td className="px-3 py-2 text-slate-700 max-w-xs">{a.reference_description}</td>
                            <td className="px-3 py-2 text-slate-600">{formatDate(a.expiry_date)}</td>
                            <td className={`px-3 py-2 ${daysRemainingClass(daysRemaining)}`}>
                              {daysRemaining < 0 ? `${Math.abs(daysRemaining)}d overdue` : `${daysRemaining}d`}
                            </td>
                            <td className="px-3 py-2">
                              <button
                                onClick={() => handleAcknowledge(a.id)}
                                disabled={acknowledgingId === a.id}
                                className="rounded bg-slate-700 px-2 py-1 text-xs font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
                              >
                                {acknowledgingId === a.id ? '…' : 'Acknowledge'}
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </section>

        {/* Section 2 — Overdue Tasks */}
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Overdue Tasks</h2>

          {tasksLoading ? (
            <LoadingState label="Loading overdue tasks…" />
          ) : tasksError ? (
            <ErrorState message={tasksError} />
          ) : sortedOverdue.length === 0 ? (
            <EmptyState title="No overdue tasks" description="All tasks are on track." />
          ) : (
            <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {['Task Title', 'Due Date', 'Days Overdue', 'Status'].map((h) => (
                      <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {sortedOverdue.map((t) => (
                    <tr key={t.id} className="hover:bg-slate-50">
                      <td className="px-3 py-2 font-medium text-slate-900 max-w-xs truncate">{t.title}</td>
                      <td className="px-3 py-2 text-slate-600">{formatDate(t.due_date)}</td>
                      <td className="px-3 py-2 font-bold text-red-600">{t.days_overdue}d</td>
                      <td className="px-3 py-2">
                        <StatusBadge tone={taskStatusTone(t.status)}>{t.status.replaceAll('_', ' ')}</StatusBadge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </AppShell>
  );
}

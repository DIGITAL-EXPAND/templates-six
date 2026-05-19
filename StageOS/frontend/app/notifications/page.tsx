'use client';

import { useEffect, useState } from 'react';
import { Bell, CheckCheck } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { fetchNotifications, markNotificationRead } from '@/lib/api/endpoints';
import type { NotificationItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const TYPE_LABELS: Record<string, string> = {
  task_assigned:   'Task Assigned',
  task_updated:    'Task Updated',
  task_blocked:    'Task Blocked',
  task_completed:  'Task Completed',
  department_issue:'Department Issue',
  evidence_rejected: 'Evidence Rejected',
  approval_decided: 'Approval Decided',
  task_overdue:    'Task Overdue',
  contract_expiring: 'Contract Expiring',
  approval_stale:  'Approval Stale',
};

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-ZA', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function NotificationsPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [markingAll, setMarkingAll] = useState(false);

  useEffect(() => {
    if (!token) return;
    fetchNotifications(token)
      .then((r) => setNotifications(r.results))
      .catch(() => setNotifications([]))
      .finally(() => setLoading(false));
  }, [token]);

  async function handleMarkRead(id: string) {
    if (!token) return;
    const updated = await markNotificationRead(token, id);
    setNotifications((prev) =>
      prev.map((n) => (n.id === updated.id ? updated : n)),
    );
  }

  async function markAllRead() {
    if (!token) return;
    setMarkingAll(true);
    const unread = notifications.filter((n) => !n.read_at);
    const results = await Promise.allSettled(
      unread.map((n) => markNotificationRead(token, n.id)),
    );
    const updated: NotificationItem[] = [];
    results.forEach((r) => {
      if (r.status === 'fulfilled') updated.push(r.value);
    });
    setNotifications((prev) =>
      prev.map((n) => {
        const u = updated.find((u) => u.id === n.id);
        return u ?? n;
      }),
    );
    setMarkingAll(false);
  }

  const unreadCount = notifications.filter((n) => !n.read_at).length;

  return (
    <AppShell>
      <div className="mx-auto max-w-3xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
            <p className="mt-0.5 text-sm text-gray-500">
              {loading
                ? 'Loading…'
                : unreadCount > 0
                ? `${unreadCount} unread`
                : 'All caught up'}
            </p>
          </div>
          {unreadCount > 0 && (
            <button
              className="flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              disabled={markingAll}
              onClick={markAllRead}
              type="button"
            >
              <CheckCheck className="h-4 w-4" />
              Mark all read
            </button>
          )}
        </div>

        {/* Content */}
        {loading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div
                className="h-20 animate-pulse rounded-xl border border-gray-100 bg-gray-50"
                key={i}
              />
            ))}
          </div>
        ) : notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 py-20 text-center">
            <Bell className="h-10 w-10 text-gray-300" />
            <p className="mt-3 text-sm font-medium text-gray-500">No notifications yet</p>
            <p className="mt-1 text-xs text-gray-400">
              You'll see task updates, approvals and alerts here.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {notifications.map((n) => (
              <div
                className={`rounded-xl border p-4 transition-colors ${
                  n.read_at
                    ? 'border-gray-200 bg-white'
                    : 'border-teal-200 bg-teal-50/50'
                }`}
                key={n.id}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    {/* Title */}
                    <p
                      className={`text-sm ${
                        n.read_at ? 'text-gray-700' : 'font-semibold text-gray-900'
                      }`}
                    >
                      {n.title}
                    </p>

                    {/* Message */}
                    {n.message && (
                      <p className="mt-0.5 text-xs text-gray-500 line-clamp-2">{n.message}</p>
                    )}

                    {/* Meta */}
                    <div className="mt-1.5 flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[11px] font-medium text-gray-600">
                        {TYPE_LABELS[n.notification_type] ?? n.notification_type}
                      </span>
                      <span className="text-xs text-gray-400">
                        {formatDate(n.created_at)}
                      </span>
                      {n.department_name && (
                        <span className="text-xs text-gray-400">· {n.department_name}</span>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex shrink-0 items-center gap-2">
                    {!n.read_at && (
                      <>
                        <span className="h-2 w-2 rounded-full bg-teal-500" aria-label="Unread" />
                        <button
                          className="text-xs font-medium text-teal-700 hover:underline"
                          onClick={() => handleMarkRead(n.id)}
                          type="button"
                        >
                          Mark read
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}

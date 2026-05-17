'use client';

import { useMemo, useState } from 'react';
import { X } from 'lucide-react';
import { EmptyState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import type { AuditEventItem } from '@/lib/api/types';

function friendlyAction(value: string) {
  return value
    .replace(/[._-]/g, ' ')
    .split(' ')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function payloadSummary(event: AuditEventItem) {
  const payload = 'payload' in event ? (event as AuditEventItem & { payload?: unknown }).payload : undefined;
  if (!payload || typeof payload !== 'object') {
    return 'No additional activity details returned.';
  }
  return Object.keys(payload as Record<string, unknown>).slice(0, 6).join(', ') || 'No additional activity details returned.';
}

export function AuditFilterBar({
  value,
  targetTypes,
  eventTypes,
  onChange,
}: {
  value: { action: string; targetType: string; from: string; to: string; actor: string };
  targetTypes: string[];
  eventTypes: string[];
  onChange: (value: { action: string; targetType: string; from: string; to: string; actor: string }) => void;
}) {
  return (
    <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 md:grid-cols-3 xl:grid-cols-5">
      <select aria-label="Filter by action" className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, action: event.target.value })} value={value.action}>
        <option value="all">All actions</option>
        {eventTypes.map((eventType) => <option key={eventType} value={eventType}>{friendlyAction(eventType)}</option>)}
      </select>
      <select aria-label="Filter by target type" className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, targetType: event.target.value })} value={value.targetType}>
        <option value="all">All targets</option>
        {targetTypes.map((targetType) => <option key={targetType} value={targetType}>{friendlyAction(targetType)}</option>)}
      </select>
      <input aria-label="Filter by changed by" className="h-10 rounded-md border border-slate-200 px-3 text-sm text-slate-950" onChange={(event) => onChange({ ...value, actor: event.target.value })} placeholder="Changed by" value={value.actor} />
      <input aria-label="From date" className="h-10 rounded-md border border-slate-200 px-3 text-sm text-slate-950" onChange={(event) => onChange({ ...value, from: event.target.value })} type="date" value={value.from} />
      <input aria-label="To date" className="h-10 rounded-md border border-slate-200 px-3 text-sm text-slate-950" onChange={(event) => onChange({ ...value, to: event.target.value })} type="date" value={value.to} />
    </section>
  );
}

export function AuditTrailList({
  events,
  onSelect,
}: {
  events: AuditEventItem[];
  onSelect: (event: AuditEventItem) => void;
}) {
  if (!events.length) {
    return <EmptyState title="No audit activity found" description="Audit Trail activity will appear here when the backend returns records for your role." />;
  }

  return (
    <div className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
      {events.map((event) => (
        <button className="block w-full px-4 py-3 text-left hover:bg-slate-50" key={event.id} onClick={() => onSelect(event)} type="button">
          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-sm font-bold text-slate-950">{friendlyAction(event.event_type)}</div>
              <div className="mt-1 text-xs text-slate-500">
                Changed by {event.actor_email ?? event.actor ?? 'System'} · Date and time {new Date(event.created_at).toLocaleString()}
              </div>
            </div>
            <StatusBadge>{event.target_type ? friendlyAction(event.target_type) : 'Activity'}</StatusBadge>
          </div>
        </button>
      ))}
    </div>
  );
}

export function AuditEventDetailDrawer({
  event,
  onClose,
}: {
  event: AuditEventItem | null;
  onClose: () => void;
}) {
  if (!event) {
    return null;
  }

  const detailRows = [
    ['Action performed', friendlyAction(event.event_type)],
    ['Changed by', event.actor_email ?? event.actor ?? 'System'],
    ['Target type', event.target_type ? friendlyAction(event.target_type) : 'Not returned'],
    ['Target id', event.target_id || 'Not returned'],
    ['Reason/comment', event.reason || 'Not returned'],
    ['Date and time', new Date(event.created_at).toLocaleString()],
    ['Payload summary', payloadSummary(event)],
  ];

  return (
    <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-xl overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-blue-700">Audit Trail</p>
          <h2 className="mt-1 text-xl font-bold text-slate-950">{friendlyAction(event.event_type)}</h2>
        </div>
        <button aria-label="Close audit detail" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700" onClick={onClose} type="button">
          <X className="h-4 w-4" />
        </button>
      </div>
      <dl className="mt-5 grid gap-3">
        {detailRows.map(([label, value]) => (
          <div className="rounded-md border border-slate-200 p-3" key={label}>
            <dt className="text-xs font-bold uppercase tracking-normal text-slate-500">{label}</dt>
            <dd className="mt-1 break-words text-sm text-slate-700">{value}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-4 text-sm text-slate-500">Sensitive raw payload values are intentionally summarized in this view.</p>
    </aside>
  );
}

export function useFilteredAuditEvents(events: AuditEventItem[], filters: { action: string; targetType: string; from: string; to: string; actor: string }) {
  return useMemo(() => events.filter((event) => {
    if (filters.action !== 'all' && event.event_type !== filters.action) return false;
    if (filters.targetType !== 'all' && event.target_type !== filters.targetType) return false;
    const actor = (event.actor_email ?? event.actor ?? '').toLowerCase();
    if (filters.actor && !actor.includes(filters.actor.toLowerCase())) return false;
    if (filters.from && new Date(event.created_at) < new Date(filters.from)) return false;
    if (filters.to && new Date(event.created_at) > new Date(`${filters.to}T23:59:59`)) return false;
    return true;
  }), [events, filters]);
}

export function uniqueAuditValues(events: AuditEventItem[], key: 'event_type' | 'target_type') {
  return Array.from(new Set(events.map((event) => event[key]).filter(Boolean) as string[])).sort();
}


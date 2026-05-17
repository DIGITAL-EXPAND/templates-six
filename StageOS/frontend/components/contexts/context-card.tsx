import Link from 'next/link';
import { CalendarDays, MapPin } from 'lucide-react';
import { StatusBadge } from '@/components/ui/status-badge';
import type { OperatingContextListItem } from '@/lib/api/types';
import { workspaceTypeLabel } from '@/lib/workspaces/labels';

function riskTone(risk?: string) {
  if (risk === 'critical' || risk === 'high') {
    return 'danger';
  }
  if (risk === 'medium') {
    return 'warning';
  }
  return 'neutral';
}

export function ContextCard({ context }: { context: OperatingContextListItem }) {
  return (
    <Link
      className="block rounded-lg border border-slate-200 bg-white p-4 hover:border-blue-300 hover:shadow-sm"
      href={`/workspaces/${context.id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="truncate text-base font-bold text-slate-950">{context.title}</h2>
          <p className="mt-1 text-sm text-slate-500 capitalize">
            {workspaceTypeLabel(context.context_type)} · {context.status}
          </p>
        </div>
        <StatusBadge tone={riskTone(context.risk_level)}>{context.risk_level ?? 'low'}</StatusBadge>
      </div>
      <div className="mt-4 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
        <div className="flex min-w-0 items-center gap-2">
          <MapPin className="h-4 w-4 shrink-0 text-slate-400" />
          <span className="truncate">{context.site_detail?.name ?? 'Site not set'}</span>
        </div>
        <div className="flex min-w-0 items-center gap-2">
          <CalendarDays className="h-4 w-4 shrink-0 text-slate-400" />
          <span className="truncate">{context.opening_date ?? 'Opening date not set'}</span>
        </div>
      </div>
      <div className="mt-4 h-2 rounded-full bg-slate-100">
        <div
          className="h-2 rounded-full bg-blue-600"
          style={{ width: `${Math.min(context.readiness_score ?? 0, 100)}%` }}
        />
      </div>
      <div className="mt-2 text-xs font-semibold text-slate-500">
        {context.readiness_score ?? 0}% ready
      </div>
    </Link>
  );
}

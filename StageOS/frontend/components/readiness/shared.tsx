import { StatusBadge } from '@/components/ui/status-badge';

export function labelFromValue(value: string) {
  return value
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function tone(value: string) {
  if (['ready', 'verified', 'confirmed', 'active', 'completed', 'contracted', 'payment_ready', 'sent_to_erp', 'paid'].includes(value)) {
    return 'good';
  }
  if (['missing', 'rejected', 'suspended', 'blacklisted', 'cancelled'].includes(value)) {
    return 'danger';
  }
  if (['uploaded', 'pending_verification', 'documents_incomplete', 'awaiting_csd', 'ready_for_erp', 'proposed', 'contract_ready'].includes(value)) {
    return 'warning';
  }
  return 'neutral';
}

export function ReadinessBadge({ value }: { value: string }) {
  return <StatusBadge tone={tone(value)}>{labelFromValue(value)}</StatusBadge>;
}

export function RestrictedField({ value }: { value?: string | null }) {
  if (!value) {
    return <span className="text-slate-400">Restricted or not provided</span>;
  }
  return <span>{value}</span>;
}

export function BlockerAlert({ blockers }: { blockers: string[] }) {
  if (!blockers.length) {
    return null;
  }
  return (
    <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">
      <div className="font-bold">Readiness blocker</div>
      <ul className="mt-2 list-disc space-y-1 pl-5">
        {blockers.map((blocker) => (
          <li key={blocker}>{blocker}</li>
        ))}
      </ul>
    </div>
  );
}

export function money(value: string, currency = 'ZAR') {
  return new Intl.NumberFormat('en-ZA', {
    currency,
    style: 'currency',
  }).format(Number(value || 0));
}


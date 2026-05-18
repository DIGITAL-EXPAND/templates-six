const riskStyles: Record<string, string> = {
  low: 'border-green-200 bg-green-50 text-green-700',
  medium: 'border-amber-200 bg-amber-50 text-amber-700',
  high: 'border-orange-200 bg-orange-50 text-orange-700',
  critical: 'border-red-200 bg-red-50 text-red-700',
};

const riskLabels: Record<string, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
};

export function RiskBadge({ level }: { level: string }) {
  const styles = riskStyles[level] ?? 'border-slate-200 bg-slate-100 text-slate-700';
  const label = riskLabels[level] ?? level;
  return (
    <span
      aria-label={`Risk: ${label}`}
      className={`inline-flex h-7 items-center rounded-md border px-2 text-xs font-semibold ${styles}`}
    >
      {label}
    </span>
  );
}

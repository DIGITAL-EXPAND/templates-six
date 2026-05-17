import clsx from 'clsx';

const toneMap = {
  neutral: 'border-slate-200 bg-slate-100 text-slate-700',
  good: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  warning: 'border-amber-200 bg-amber-50 text-amber-700',
  danger: 'border-rose-200 bg-rose-50 text-rose-700',
  info: 'border-blue-200 bg-blue-50 text-blue-700',
};

type StatusTone = keyof typeof toneMap;

export function StatusBadge({
  children,
  tone = 'neutral',
}: {
  children: React.ReactNode;
  tone?: StatusTone;
}) {
  return (
    <span
      className={clsx(
        'inline-flex h-7 items-center rounded-md border px-2 text-xs font-semibold capitalize',
        toneMap[tone],
      )}
    >
      {children}
    </span>
  );
}

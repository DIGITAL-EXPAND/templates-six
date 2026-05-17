import type { WorkflowStepItem } from '@/lib/api/types';

export function WorkflowProgress({ steps }: { steps: WorkflowStepItem[] }) {
  const completed = steps.filter((step) => step.status === 'completed').length;
  const total = steps.length;
  const percentage = total ? Math.round((completed / total) * 100) : 0;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-bold text-slate-950">Process progress</h2>
        <span className="text-sm font-bold text-slate-600">{percentage}%</span>
      </div>
      <div className="mt-3 h-2 rounded-full bg-slate-100">
        <div className="h-2 rounded-full bg-blue-600" style={{ width: `${percentage}%` }} />
      </div>
      <p className="mt-2 text-sm text-slate-500">
        {completed} of {total} Process Steps completed
      </p>
    </div>
  );
}

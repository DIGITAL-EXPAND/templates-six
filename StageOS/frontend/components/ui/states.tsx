export function LoadingState({ label = 'Loading' }: { label?: string }) {
  return (
    <div aria-busy="true" className="rounded-lg border border-slate-200 bg-white p-6 text-sm font-medium text-slate-500">
      <span role="status">{label}</span>
    </div>
  );
}

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <h2 className="text-base font-bold text-slate-950">{title}</h2>
      {description ? <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p> : null}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-700">
      {message}
    </div>
  );
}

export function PermissionDeniedState() {
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-5 text-amber-950">
      <h2 className="text-base font-bold">Permission needed</h2>
      <p className="mt-2 text-sm leading-6">
        You are signed in, but the backend did not grant access to this information.
      </p>
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-5">
      <div className="h-16 animate-pulse rounded-lg bg-slate-200" />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div className="h-36 animate-pulse rounded-lg bg-slate-200" key={index} />
        ))}
      </div>
      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="h-80 animate-pulse rounded-lg bg-slate-200" />
        <div className="h-80 animate-pulse rounded-lg bg-slate-200" />
      </div>
    </div>
  );
}

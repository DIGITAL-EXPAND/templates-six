export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
}) {
  return (
    <section className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
      <div>
        {eyebrow ? <p className="text-sm font-semibold text-blue-700">{eyebrow}</p> : null}
        <h1 className="mt-1 text-2xl font-bold text-slate-950 md:text-3xl">{title}</h1>
        {description ? (
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="flex flex-col gap-2 sm:flex-row">{actions}</div> : null}
    </section>
  );
}

import { AppShell } from '@/components/app-shell/app-shell';

export function ModuleLanding({
  eyebrow,
  title,
  description,
  items,
}: {
  eyebrow: string;
  title: string;
  description: string;
  items: string[];
}) {
  return (
    <AppShell>
      <div className="space-y-5">
        <section>
          <p className="text-sm font-semibold text-blue-700">{eyebrow}</p>
          <h1 className="mt-1 text-2xl font-bold text-slate-950 md:text-3xl">{title}</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p>
        </section>
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {items.map((item) => (
            <article className="rounded-lg border border-slate-200 bg-white p-4" key={item}>
              <h2 className="text-base font-bold text-slate-950">{item}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                This surface will use backend permissions and live API responses as the workflow is built out.
              </p>
            </article>
          ))}
        </section>
      </div>
    </AppShell>
  );
}

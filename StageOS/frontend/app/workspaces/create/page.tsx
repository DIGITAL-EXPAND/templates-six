'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { ApiError } from '@/lib/api/client';
import { createWorkspace, fetchSites } from '@/lib/api/endpoints';
import type { SiteListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';
import { workspaceTypeOptions } from '@/lib/workspaces/labels';

export default function CreateWorkspacePage() {
  const router = useRouter();
  const { tokens, user } = useAuth();
  const [sites, setSites] = useState<SiteListItem[]>([]);
  const [loadingSites, setLoadingSites] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [title, setTitle] = useState('');
  const [workspaceType, setWorkspaceType] = useState('production');
  const [site, setSite] = useState('');
  const [priority, setPriority] = useState('medium');
  const [riskLevel, setRiskLevel] = useState('low');
  const [openingDate, setOpeningDate] = useState('');
  const [budget, setBudget] = useState('');
  const [synopsis, setSynopsis] = useState('');

  useEffect(() => {
    if (!tokens?.access) {
      return;
    }

    let mounted = true;
    fetchSites(tokens.access)
      .then((response) => {
        if (!mounted) {
          return;
        }
        setSites(response.results);
        setSite(response.results[0]?.id ?? '');
      })
      .catch(() => {
        if (mounted) {
          setError('Sites could not be loaded.');
        }
      })
      .finally(() => {
        if (mounted) {
          setLoadingSites(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!tokens?.access || !user) {
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const workspace = await createWorkspace(tokens.access, {
        title,
        context_type: workspaceType,
        site,
        owner: user.id,
        priority,
        risk_level: riskLevel,
        opening_date: openingDate || undefined,
        budget: budget || undefined,
        synopsis,
      });
      router.replace(`/workspaces/${workspace.id}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError('You do not have permission to create a Workspace.');
      } else {
        setError('Workspace could not be created. Check the required fields and try again.');
      }
    } finally {
      setSubmitting(false);
    }
  }

  const canSubmit = Boolean(title && site && user && !submitting);

  return (
    <AppShell>
      <div className="space-y-5">
        <Link
          className="inline-flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-slate-950"
          href="/workspaces"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Workspaces
        </Link>

        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm font-semibold text-blue-700">New Workspace</p>
          <h1 className="mt-1 text-2xl font-bold text-slate-950 md:text-3xl">Create Workspace</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Start a shared place for a production, venue booking, youth project, festival or programme.
          </p>
        </section>

        {error ? (
          <div className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-700">
            {error}
          </div>
        ) : null}

        {!loadingSites && !sites.length ? (
          <section className="rounded-lg border border-amber-200 bg-amber-50 p-5">
            <h2 className="text-base font-bold text-amber-950">A site is needed first</h2>
            <p className="mt-2 text-sm leading-6 text-amber-900">
              Workspaces are linked to a site. Add a site in Settings, then return here.
            </p>
          </section>
        ) : (
          <form className="grid gap-5 lg:grid-cols-[1fr_320px]" onSubmit={handleSubmit}>
            <section className="space-y-5 rounded-lg border border-slate-200 bg-white p-5">
              <div>
                <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="title">
                  Workspace name
                </label>
                <input
                  className="h-11 w-full rounded-md border border-slate-300 px-3 text-slate-950"
                  id="title"
                  onChange={(event) => setTitle(event.target.value)}
                  required
                  value={title}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="synopsis">
                  Short description
                </label>
                <textarea
                  className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950"
                  id="synopsis"
                  onChange={(event) => setSynopsis(event.target.value)}
                  value={synopsis}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="type">
                    Workspace type
                  </label>
                  <select
                    className="h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
                    id="type"
                    onChange={(event) => setWorkspaceType(event.target.value)}
                    value={workspaceType}
                  >
                    {workspaceTypeOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="site">
                    Site
                  </label>
                  <select
                    className="h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
                    disabled={loadingSites}
                    id="site"
                    onChange={(event) => setSite(event.target.value)}
                    required
                    value={site}
                  >
                    {sites.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </section>

            <section className="space-y-5 rounded-lg border border-slate-200 bg-white p-5">
              <div>
                <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="priority">
                  Priority
                </label>
                <select
                  className="h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
                  id="priority"
                  onChange={(event) => setPriority(event.target.value)}
                  value={priority}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="risk">
                  Risk level
                </label>
                <select
                  className="h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
                  id="risk"
                  onChange={(event) => setRiskLevel(event.target.value)}
                  value={riskLevel}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="opening-date">
                  Opening date
                </label>
                <input
                  className="h-11 w-full rounded-md border border-slate-300 px-3 text-slate-950"
                  id="opening-date"
                  onChange={(event) => setOpeningDate(event.target.value)}
                  type="date"
                  value={openingDate}
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="budget">
                  Budget
                </label>
                <input
                  className="h-11 w-full rounded-md border border-slate-300 px-3 text-slate-950"
                  id="budget"
                  min="0"
                  onChange={(event) => setBudget(event.target.value)}
                  step="0.01"
                  type="number"
                  value={budget}
                />
              </div>

              <button
                className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
                disabled={!canSubmit}
                type="submit"
              >
                {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                Create Workspace
              </button>
            </section>
          </form>
        )}
      </div>
    </AppShell>
  );
}

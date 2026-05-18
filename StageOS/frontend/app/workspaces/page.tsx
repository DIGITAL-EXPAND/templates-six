'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { Plus, Search } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { ContextCard } from '@/components/contexts/context-card';
import { ApiError } from '@/lib/api/client';
import { fetchOperatingContexts } from '@/lib/api/endpoints';
import type { OperatingContextListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export default function WorkspacesPage() {
  const { tokens } = useAuth();
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) {
      return;
    }

    let mounted = true;
    fetchOperatingContexts(tokens.access)
      .then((response) => {
        if (mounted) {
          setWorkspaces(response.results);
        }
      })
      .catch((err) => {
        if (!mounted) {
          return;
        }
        if (err instanceof ApiError && err.status === 403) {
          setError('You do not have access to Workspaces.');
        } else {
          setError('Workspaces could not be loaded.');
        }
      })
      .finally(() => {
        if (mounted) {
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  const filtered = useMemo(() => {
    return workspaces.filter((workspace) => {
      const matchesQuery = workspace.title.toLowerCase().includes(query.toLowerCase());
      const matchesStatus = status === 'all' || workspace.status === status;
      return matchesQuery && matchesStatus;
    });
  }, [workspaces, query, status]);

  const statuses = useMemo(
    () => ['all', ...Array.from(new Set(workspaces.map((workspace) => workspace.status)))],
    [workspaces],
  );

  return (
    <AppShell>
      <div className="space-y-5">
        <section className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold text-blue-700">Planning and delivery</p>
            <h1 className="mt-1 text-2xl font-bold text-slate-950 md:text-3xl">Shows & Events</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
              Manage shows, venue bookings, youth projects, festivals and programmes from one place.
            </p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Link
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700"
              href="/workspaces/create"
            >
              <Plus className="h-4 w-4" />
              Add Show or Event
            </Link>
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                aria-label="Search Shows & Events"
                className="h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-900 sm:w-72"
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search Shows & Events"
                type="search"
                value={query}
              />
            </div>
            <select
              aria-label="Filter by status"
              className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
              onChange={(event) => setStatus(event.target.value)}
              value={status}
            >
              {statuses.map((item) => (
                <option key={item} value={item}>
                  {item === 'all' ? 'All statuses' : item}
                </option>
              ))}
            </select>
          </div>
        </section>

        {error ? (
          <div className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-700">
            {error}
          </div>
        ) : null}

        {loading ? (
          <div className="grid gap-4 lg:grid-cols-2">
            {Array.from({ length: 4 }).map((_, index) => (
              <div className="h-44 animate-pulse rounded-lg bg-slate-200" key={index} />
            ))}
          </div>
        ) : filtered.length ? (
          <div className="grid gap-4 lg:grid-cols-2">
            {filtered.map((workspace) => (
              <ContextCard context={workspace} key={workspace.id} />
            ))}
          </div>
        ) : (
          <div className="rounded-lg border border-slate-200 bg-white p-8">
            <h2 className="text-base font-bold text-slate-950">No Shows or Events yet</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              Add a show or event when you are ready to plan a production, booking, youth project,
              festival or programme.
            </p>
          </div>
        )}
      </div>
    </AppShell>
  );
}

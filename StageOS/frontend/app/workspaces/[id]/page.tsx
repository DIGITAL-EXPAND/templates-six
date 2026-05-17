'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ArrowLeft, CalendarDays, MapPin, UserRound } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { ContextTabs } from '@/components/contexts/context-tabs';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchContextReadiness, fetchOperatingContext } from '@/lib/api/endpoints';
import type { ContextReadiness, OperatingContextListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';
import { workspaceTypeLabel } from '@/lib/workspaces/labels';

export default function WorkspaceDetailPage() {
  const params = useParams<{ id: string }>();
  const { tokens } = useAuth();
  const [workspace, setWorkspace] = useState<OperatingContextListItem | null>(null);
  const [readiness, setReadiness] = useState<ContextReadiness | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access || !params.id) {
      return;
    }

    let mounted = true;
    Promise.allSettled([
      fetchOperatingContext(tokens.access, params.id),
      fetchContextReadiness(tokens.access, params.id),
    ])
      .then(([workspaceResult, readinessResult]) => {
        if (!mounted) {
          return;
        }
        if (workspaceResult.status === 'fulfilled') {
          setWorkspace(workspaceResult.value);
        } else {
          setError('This Workspace could not be loaded.');
        }
        if (readinessResult.status === 'fulfilled') {
          setReadiness(readinessResult.value);
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
  }, [params.id, tokens?.access]);

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

        {loading ? (
          <div className="space-y-4">
            <div className="h-36 animate-pulse rounded-lg bg-slate-200" />
            <div className="h-96 animate-pulse rounded-lg bg-slate-200" />
          </div>
        ) : error || !workspace ? (
          <div className="rounded-lg border border-rose-200 bg-rose-50 p-5 text-sm font-medium text-rose-700">
            {error || 'This Workspace could not be loaded.'}
          </div>
        ) : (
          <>
            <section className="rounded-lg border border-slate-200 bg-white p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="min-w-0">
                  <div className="mb-3 flex flex-wrap items-center gap-2">
                    <StatusBadge tone="info">{workspaceTypeLabel(workspace.context_type)}</StatusBadge>
                    <StatusBadge>{workspace.status}</StatusBadge>
                    <StatusBadge
                      tone={
                        workspace.risk_level === 'critical' || workspace.risk_level === 'high'
                          ? 'danger'
                          : 'neutral'
                      }
                    >
                      {workspace.risk_level ?? 'low'}
                    </StatusBadge>
                  </div>
                  <h1 className="text-2xl font-bold text-slate-950 md:text-3xl">{workspace.title}</h1>
                  <p className="mt-2 text-sm font-semibold text-slate-500">
                    {workspaceTypeLabel(workspace.context_type)}
                  </p>
                  <div className="mt-4 grid gap-2 text-sm text-slate-600 md:grid-cols-3">
                    <div className="flex min-w-0 items-center gap-2">
                      <MapPin className="h-4 w-4 shrink-0 text-slate-400" />
                      <span className="truncate">{workspace.site_detail?.name ?? 'Site not set'}</span>
                    </div>
                    <div className="flex min-w-0 items-center gap-2">
                      <CalendarDays className="h-4 w-4 shrink-0 text-slate-400" />
                      <span className="truncate">{workspace.opening_date ?? 'Opening date not set'}</span>
                    </div>
                    <div className="flex min-w-0 items-center gap-2">
                      <UserRound className="h-4 w-4 shrink-0 text-slate-400" />
                      <span className="truncate">{workspace.owner_detail?.full_name ?? 'Owner not set'}</span>
                    </div>
                  </div>
                </div>
                <div className="w-full rounded-md border border-slate-200 p-4 lg:w-64">
                  <div className="text-xs font-bold uppercase tracking-normal text-slate-500">Readiness</div>
                  <div className="mt-2 text-3xl font-bold text-slate-950">
                    {workspace.readiness_score ?? 0}%
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-slate-100">
                    <div
                      className="h-2 rounded-full bg-blue-600"
                      style={{ width: `${Math.min(workspace.readiness_score ?? 0, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            </section>
            <ContextTabs context={workspace} readiness={readiness} />
          </>
        )}
      </div>
    </AppShell>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { fetchBoardMeetings, fetchBoardResolutions } from '@/lib/api/endpoints';
import type { BoardMeetingItem, BoardResolutionItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const MEETING_TYPE_LABELS: Record<string, string> = {
  ordinary: 'Board Meeting',
  special: 'Special',
  committee: 'Committee',
  agm: 'AGM',
  audit_committee: 'Audit Committee',
  risk_committee: 'Risk Committee',
};

const MEETING_STATUS_BADGE: Record<string, string> = {
  scheduled: 'bg-blue-100 text-blue-700',
  concluded: 'bg-green-100 text-green-700',
  cancelled: 'bg-slate-100 text-slate-600',
  postponed: 'bg-amber-100 text-amber-700',
};

const RESOLUTION_STATUS_BADGE: Record<string, string> = {
  passed: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  deferred: 'bg-amber-100 text-amber-700',
  withdrawn: 'bg-slate-100 text-slate-600',
};

function StatusBadge({ status, map }: { status: string; map: Record<string, string> }) {
  const cls = map[status] ?? 'bg-slate-100 text-slate-600';
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${cls}`}>
      {status.replace(/_/g, ' ')}
    </span>
  );
}

function ResolutionCard({ resolution }: { resolution: BoardResolutionItem }) {
  return (
    <article className="rounded-md border border-slate-200 bg-slate-50 p-3 space-y-1.5">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <span className="text-xs font-mono text-slate-400 mr-2">{resolution.resolution_number}</span>
          <span className="text-sm font-bold text-slate-900">{resolution.title}</span>
        </div>
        <StatusBadge map={RESOLUTION_STATUS_BADGE} status={resolution.status} />
      </div>
      {resolution.description ? (
        <p className="text-sm text-slate-600">{resolution.description}</p>
      ) : null}
      <div className="flex flex-wrap gap-4 text-xs text-slate-500">
        <span>For: <strong className="text-green-700">{resolution.votes_for}</strong></span>
        <span>Against: <strong className="text-red-700">{resolution.votes_against}</strong></span>
        <span>Abstained: <strong className="text-slate-700">{resolution.votes_abstained}</strong></span>
      </div>
      {resolution.action_required ? (
        <div className="text-xs text-slate-600">
          <span className="font-semibold">Action required: </span>
          {resolution.action_required}
          {resolution.action_due_date ? (
            <span className="ml-2 text-slate-400">Due {resolution.action_due_date}</span>
          ) : null}
          {resolution.action_completed ? (
            <span className="ml-2 font-semibold text-green-700">Completed</span>
          ) : null}
        </div>
      ) : null}
    </article>
  );
}

function ResolutionsPanel({ meetingId, token }: { meetingId: string; token: string }) {
  const [resolutions, setResolutions] = useState<BoardResolutionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    fetchBoardResolutions(token, meetingId)
      .then((res) => { if (mounted) setResolutions(res.results); })
      .catch(() => { if (mounted) setError('Resolutions could not be loaded.'); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token, meetingId]);

  if (loading) return <div className="px-4 py-3 text-sm text-slate-500">Loading resolutions…</div>;
  if (error) return <div className="px-4 py-3 text-sm text-red-600">{error}</div>;
  if (!resolutions.length) return <div className="px-4 py-3 text-sm text-slate-400">No resolutions recorded for this meeting.</div>;

  return (
    <div className="border-t border-slate-100 p-4 space-y-2">
      {resolutions.map((resolution) => (
        <ResolutionCard key={resolution.id} resolution={resolution} />
      ))}
    </div>
  );
}

function MeetingCard({ meeting, token }: { meeting: BoardMeetingItem; token: string }) {
  const [expanded, setExpanded] = useState(false);
  const meetingDate = new Date(meeting.meeting_date).toLocaleDateString('en-ZA', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  return (
    <article className="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <div className="flex flex-col gap-2 p-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex-1 min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-blue-700 bg-blue-50 rounded px-2 py-0.5">
              {MEETING_TYPE_LABELS[meeting.meeting_type] ?? meeting.meeting_type}
            </span>
            <StatusBadge map={MEETING_STATUS_BADGE} status={meeting.status} />
          </div>
          <h3 className="text-base font-bold text-slate-950">{meeting.title}</h3>
          <div className="flex flex-wrap gap-4 text-xs text-slate-500">
            <span>{meetingDate}</span>
            {meeting.venue ? <span>{meeting.venue}</span> : null}
            {meeting.chaired_by ? <span>Chaired by: <span className="text-slate-700">{meeting.chaired_by}</span></span> : null}
            <span>
              Members present: <span className="font-semibold text-slate-700">{meeting.members_present}</span>
              {meeting.quorum_required > 0 ? (
                <span> / {meeting.quorum_required} required</span>
              ) : null}
              {meeting.quorum_achieved ? (
                <span className="ml-1 text-green-700 font-semibold">(Quorum)</span>
              ) : (
                <span className="ml-1 text-amber-700 font-semibold">(No quorum)</span>
              )}
            </span>
          </div>
        </div>
        <button
          aria-expanded={expanded}
          className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 shrink-0"
          onClick={() => setExpanded((prev) => !prev)}
          type="button"
        >
          {expanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
          Resolutions
        </button>
      </div>
      {expanded && <ResolutionsPanel meetingId={meeting.id} token={token} />}
    </article>
  );
}

export default function BoardMeetingsPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';
  const [meetings, setMeetings] = useState<BoardMeetingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    fetchBoardMeetings(token)
      .then((res) => { if (mounted) setMeetings(res.results); })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('Board meetings could not be loaded.');
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token]);

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="View board meetings, member attendance and formal resolutions."
          eyebrow="Governance"
          title="Board Meetings"
        />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? (
          <LoadingState label="Loading board meetings" />
        ) : (
          <section className="space-y-3">
            {meetings.length ? (
              meetings.map((meeting) => (
                <MeetingCard key={meeting.id} meeting={meeting} token={token} />
              ))
            ) : (
              <EmptyState
                description="Board meetings will appear here once they are recorded."
                title="No board meetings found"
              />
            )}
          </section>
        )}
      </div>
    </AppShell>
  );
}

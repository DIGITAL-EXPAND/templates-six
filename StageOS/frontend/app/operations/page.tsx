'use client';

import { useEffect, useMemo, useState } from 'react';
import { Star } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DepartmentExecutiveActionsPanel } from '@/components/governance/department-executive-actions-panel';
import {
  FOHPlanList,
  FohFilters,
  IncidentActionDialog,
  fohBlockers,
  planChecklist,
  planIncidents,
  type FohAction,
} from '@/components/operations/operations-components';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  checkChecklistItem,
  createIncident,
  fetchChecklists,
  fetchFohPlans,
  fetchIncidents,
  fetchOperatingContexts,
  setFohPlanAction,
} from '@/lib/api/endpoints';
import type { ChecklistItem, FohPlanItem, IncidentItem, OperatingContextListItem, PostShowReportItem, ShowCallItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const SHOW_CALL_STATUS_COLOURS: Record<string, string> = {
  draft:       'bg-gray-100 text-gray-600',
  distributed: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-amber-100 text-amber-700',
  completed:   'bg-green-100 text-green-700',
  cancelled:   'bg-red-100 text-red-600',
};

function formatZAR(val: string | null | undefined) {
  if (!val) return 'R 0.00';
  return 'R ' + parseFloat(val).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function StarRating({ rating }: { rating: number | null }) {
  if (rating === null) return <span className="text-gray-400 text-xs">—</span>;
  const filled = Math.round(rating);
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <Star
          key={i}
          className={`h-3 w-3 ${i <= filled ? 'text-amber-400 fill-amber-400' : 'text-gray-200'}`}
        />
      ))}
    </div>
  );
}

function ShowCallsSection({ token }: { token: string }) {
  const [calls, setCalls] = useState<ShowCallItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    fetch('/api/v1/operations/show-calls/?page_size=50', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { if (mounted) setCalls(data.results ?? []); })
      .catch(() => {})
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token]);

  if (loading) return <div className="py-8 text-center text-sm text-gray-400">Loading show calls…</div>;
  if (!calls.length) return <div className="py-8 text-center text-sm text-gray-400">No show calls found.</div>;

  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            {['Show Date', 'Call Time', 'House Open', 'Start Time', 'Expected Audience', 'Status'].map(h => (
              <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {calls.map(call => (
            <tr key={call.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-medium text-gray-900">
                {new Date(call.show_date).toLocaleDateString('en-ZA')}
              </td>
              <td className="px-4 py-3 text-gray-700">{call.call_time}</td>
              <td className="px-4 py-3 text-gray-500">{call.house_open_time ?? '—'}</td>
              <td className="px-4 py-3 text-gray-500">{call.show_start_time ?? '—'}</td>
              <td className="px-4 py-3 text-center text-gray-700">
                {call.expected_audience !== null ? call.expected_audience.toLocaleString() : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${SHOW_CALL_STATUS_COLOURS[call.status] ?? 'bg-gray-100 text-gray-600'}`}>
                  {call.status.replace('_', ' ')}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PostShowReportsSection({ token }: { token: string }) {
  const [reports, setReports] = useState<PostShowReportItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    fetch('/api/v1/operations/post-show-reports/?page_size=50', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { if (mounted) setReports(data.results ?? []); })
      .catch(() => {})
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token]);

  if (loading) return <div className="py-8 text-center text-sm text-gray-400">Loading post-show reports…</div>;
  if (!reports.length) return <div className="py-8 text-center text-sm text-gray-400">No post-show reports found.</div>;

  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            {['Show Date', 'Audience', 'Walk-ins', 'Comps', 'Incidents', 'Rating', 'Cash', 'Card'].map(h => (
              <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {reports.map(report => (
            <tr key={report.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-medium text-gray-900">
                {new Date(report.show_date).toLocaleDateString('en-ZA')}
              </td>
              <td className="px-4 py-3 text-center font-medium text-gray-800">{report.actual_audience.toLocaleString()}</td>
              <td className="px-4 py-3 text-center text-gray-600">{report.walk_ins}</td>
              <td className="px-4 py-3 text-center text-gray-600">{report.comps_used}</td>
              <td className="px-4 py-3 text-center">
                <span className={report.incidents_count > 0 ? 'font-semibold text-red-600' : 'text-gray-400'}>
                  {report.incidents_count}
                </span>
              </td>
              <td className="px-4 py-3">
                <StarRating rating={report.overall_rating} />
              </td>
              <td className="px-4 py-3 text-gray-700">{formatZAR(report.cash_collected)}</td>
              <td className="px-4 py-3 text-gray-700">{formatZAR(report.card_collected)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function OperationsPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';
  const [plans, setPlans] = useState<FohPlanItem[]>([]);
  const [checklists, setChecklists] = useState<ChecklistItem[]>([]);
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [filters, setFilters] = useState({ status: 'all', workspace: 'all', incomplete: false, incidents: false, accessibility: false });
  const [action, setAction] = useState<FohAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.all([fetchFohPlans(tokens.access), fetchChecklists(tokens.access), fetchIncidents(tokens.access), fetchOperatingContexts(tokens.access)])
      .then(([planResponse, checklistResponse, incidentResponse, workspaceResponse]) => {
        if (!mounted) return;
        setPlans(planResponse.results);
        setChecklists(checklistResponse.results);
        setIncidents(incidentResponse.results);
        setWorkspaces(workspaceResponse.results);
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('FOH / Operations plans could not be loaded.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  const filteredPlans = useMemo(() => plans.filter((plan) => {
    const items = planChecklist(checklists, plan.id);
    const planIncidentItems = planIncidents(incidents, plan);
    if (filters.status !== 'all' && plan.status !== filters.status) return false;
    if (filters.workspace !== 'all' && plan.operating_context !== filters.workspace) return false;
    if (filters.incomplete && !items.some((item) => !item.is_checked)) return false;
    if (filters.incidents && !planIncidentItems.length) return false;
    if (filters.accessibility && !fohBlockers(plan, items, planIncidentItems).some((blocker) => blocker.toLowerCase().includes('accessibility'))) return false;
    return true;
  }), [checklists, filters, incidents, plans]);

  async function handleAction(values: { comment: string; incidentType: string; severity: string; description: string }) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    setError('');
    try {
      if (action.kind === 'check') {
        const updated = await checkChecklistItem(tokens.access, action.item.id, values.comment);
        setChecklists((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      } else if (action.kind === 'incident') {
        const created = await createIncident(tokens.access, { operating_context: action.plan.operating_context, foh_plan: action.plan.id, incident_type: values.incidentType, occurred_at: new Date().toISOString(), description: values.description, response: values.comment, severity: values.severity });
        setIncidents((current) => [created, ...current]);
      } else {
        const updated = await setFohPlanAction(tokens.access, action.plan.id, action.kind, values.comment);
        setPlans((current) => current.map((plan) => (plan.id === updated.id ? updated : plan)));
      }
      setAction(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to perform this FOH / Operations action.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('FOH / Operations action could not be completed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader description="Coordinate FOH plans, show-day checklists, audience access and incidents." eyebrow="FOH / Operations" title="FOH / Operations" />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading FOH / Operations plans" /> : (
          <>
            <FohFilters onChange={setFilters} value={filters} workspaces={workspaces} />
            <DepartmentExecutiveActionsPanel departmentTypes={['operations']} targetTypes={['FOHPlan', 'ShowDayChecklist', 'Incident']} />
            {filteredPlans.length ? <FOHPlanList checklists={checklists} incidents={incidents} onAction={setAction} plans={filteredPlans} workspaces={workspaces} /> : <EmptyState description="FOH plans will appear here when records are available or filters are cleared." title="No FOH plans found" />}
          </>
        )}

        {/* Show Day */}
        {token && (
          <>
            <section className="space-y-3">
              <h2 className="text-base font-semibold text-gray-800">Show Calls</h2>
              <p className="text-xs text-gray-500">Scheduled show calls with call times, house open and audience numbers.</p>
              <ShowCallsSection token={token} />
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-semibold text-gray-800">Post-Show Reports</h2>
              <p className="text-xs text-gray-500">Actual audience numbers, ratings and revenue collected per show.</p>
              <PostShowReportsSection token={token} />
            </section>
          </>
        )}
      </div>
      <IncidentActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </AppShell>
  );
}

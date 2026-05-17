'use client';

import { useEffect, useMemo, useState } from 'react';
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
import type { ChecklistItem, FohPlanItem, IncidentItem, OperatingContextListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export default function OperationsPage() {
  const { tokens } = useAuth();
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
      </div>
      <IncidentActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </AppShell>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { FOHPlanList, IncidentActionDialog, type FohAction } from '@/components/operations/operations-components';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { checkChecklistItem, createIncident, fetchChecklists, fetchFohPlans, fetchIncidents, fetchOperatingContexts, setFohPlanAction } from '@/lib/api/endpoints';
import type { ChecklistItem, FohPlanItem, IncidentItem, OperatingContextListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceOperationsTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [plans, setPlans] = useState<FohPlanItem[]>([]);
  const [checklists, setChecklists] = useState<ChecklistItem[]>([]);
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [action, setAction] = useState<FohAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.all([fetchFohPlans(tokens.access), fetchChecklists(tokens.access), fetchIncidents(tokens.access, { operating_context: workspaceId }), fetchOperatingContexts(tokens.access)])
      .then(([planResponse, checklistResponse, incidentResponse, workspaceResponse]) => {
        if (!mounted) return;
        const scoped = planResponse.results.filter((plan) => plan.operating_context === workspaceId);
        const planIds = new Set(scoped.map((plan) => plan.id));
        setPlans(scoped);
        setChecklists(checklistResponse.results.filter((item) => planIds.has(item.foh_plan)));
        setIncidents(incidentResponse.results);
        setWorkspaces(workspaceResponse.results);
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('FOH / Operations readiness could not be loaded for this Workspace.');
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access, workspaceId]);

  async function handleAction(values: { comment: string; incidentType: string; severity: string; description: string }) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    try {
      if (action.kind === 'check') {
        const updated = await checkChecklistItem(tokens.access, action.item.id, values.comment);
        setChecklists((current) => current.map((item) => item.id === updated.id ? updated : item));
      } else if (action.kind === 'incident') {
        const created = await createIncident(tokens.access, { operating_context: action.plan.operating_context, foh_plan: action.plan.id, incident_type: values.incidentType, occurred_at: new Date().toISOString(), description: values.description, response: values.comment, severity: values.severity });
        setIncidents((current) => [created, ...current]);
      } else {
        const updated = await setFohPlanAction(tokens.access, action.plan.id, action.kind, values.comment);
        setPlans((current) => current.map((plan) => plan.id === updated.id ? updated : plan));
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

  if (loading) return <LoadingState label="Loading Workspace FOH / Operations" />;
  return <div className="space-y-4">{permissionDenied ? <PermissionDeniedState /> : null}{error ? <ErrorState message={error} /> : null}{plans.length ? <FOHPlanList checklists={checklists} incidents={incidents} onAction={setAction} plans={plans} workspaces={workspaces} /> : <EmptyState description="FOH / Operations plans linked to this Workspace will appear here." title="No FOH plan yet" />}<IncidentActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} /></div>;
}


'use client';

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DepartmentExecutiveActionsPanel } from '@/components/governance/department-executive-actions-panel';
import {
  CampaignFilters,
  CampaignList,
  DeliverableActionDialog,
  campaignDeliverables,
  isDeliverableOverdue,
  type MarketingAction,
} from '@/components/marketing/marketing-components';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  completeCampaignDeliverable,
  fetchCampaignDeliverables,
  fetchCampaigns,
  fetchDocuments,
  fetchOperatingContexts,
  fetchUsers,
  setCampaignAction,
} from '@/lib/api/endpoints';
import type { CampaignDeliverableItem, CampaignItem, DocumentItem, OperatingContextListItem, UserListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export default function MarketingPage() {
  const { tokens } = useAuth();
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [deliverables, setDeliverables] = useState<CampaignDeliverableItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [filters, setFilters] = useState({ status: 'all', level: 'all', workspace: 'all', type: 'all', overdue: false, missingEvidence: false });
  const [action, setAction] = useState<MarketingAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loadedAt, setLoadedAt] = useState(0);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.all([fetchCampaigns(tokens.access), fetchCampaignDeliverables(tokens.access), fetchDocuments(tokens.access), fetchOperatingContexts(tokens.access), fetchUsers(tokens.access)])
      .then(([campaignResponse, deliverableResponse, documentResponse, workspaceResponse, userResponse]) => {
        if (!mounted) return;
        setCampaigns(campaignResponse.results);
        setDeliverables(deliverableResponse.results);
        setDocuments(documentResponse.results);
        setWorkspaces(workspaceResponse.results);
        setUsers(userResponse.results);
        setLoadedAt(Date.now());
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('Marketing campaigns could not be loaded.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  const levels = useMemo(() => Array.from(new Set(campaigns.map((campaign) => campaign.campaign_level))).sort(), [campaigns]);
  const types = useMemo(() => Array.from(new Set(deliverables.map((deliverable) => deliverable.deliverable_type))).sort(), [deliverables]);
  const filteredCampaigns = useMemo(() => campaigns.filter((campaign) => {
    const items = campaignDeliverables(deliverables, campaign.id);
    if (filters.status !== 'all' && campaign.status !== filters.status) return false;
    if (filters.level !== 'all' && campaign.campaign_level !== filters.level) return false;
    if (filters.workspace !== 'all' && campaign.operating_context !== filters.workspace) return false;
    if (filters.type !== 'all' && !items.some((item) => item.deliverable_type === filters.type)) return false;
    if (filters.overdue && !items.some((item) => isDeliverableOverdue(item, loadedAt))) return false;
    if (filters.missingEvidence && !items.some((item) => !item.evidence_document)) return false;
    return true;
  }), [campaigns, deliverables, filters, loadedAt]);

  async function handleAction(values: { comment: string; evidence: string }) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    setError('');
    try {
      if (action.kind === 'complete') {
        const updated = await completeCampaignDeliverable(tokens.access, action.deliverable.id, { comment: values.comment, evidence_document: values.evidence || null });
        setDeliverables((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      } else {
        const updated = await setCampaignAction(tokens.access, action.campaign.id, action.kind, values.comment);
        setCampaigns((current) => current.map((campaign) => (campaign.id === updated.id ? updated : campaign)));
      }
      setAction(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to perform this marketing action.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Marketing action could not be completed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader description="Track campaign readiness, deliverables, evidence and launch actions across Workspaces." eyebrow="Marketing" title="Marketing" />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? <LoadingState label="Loading marketing campaigns" /> : (
          <>
            <CampaignFilters levels={levels} onChange={setFilters} types={types} value={filters} workspaces={workspaces} />
            <DepartmentExecutiveActionsPanel departmentTypes={['marketing']} targetTypes={['Campaign', 'CampaignDeliverable']} />
            {filteredCampaigns.length ? <CampaignList campaigns={filteredCampaigns} deliverables={deliverables} documents={documents} now={loadedAt} onAction={setAction} users={users} workspaces={workspaces} /> : <EmptyState description="Campaigns will appear here when records are available or filters are cleared." title="No campaigns found" />}
          </>
        )}
      </div>
      <DeliverableActionDialog action={action} documents={documents} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </AppShell>
  );
}

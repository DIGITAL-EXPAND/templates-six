'use client';

import { useEffect, useState } from 'react';
import { CampaignList, DeliverableActionDialog, type MarketingAction } from '@/components/marketing/marketing-components';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import { completeCampaignDeliverable, fetchCampaignDeliverables, fetchCampaigns, fetchDocuments, fetchOperatingContexts, fetchUsers, setCampaignAction } from '@/lib/api/endpoints';
import type { CampaignDeliverableItem, CampaignItem, DocumentItem, OperatingContextListItem, UserListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceMarketingTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [deliverables, setDeliverables] = useState<CampaignDeliverableItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [action, setAction] = useState<MarketingAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loadedAt, setLoadedAt] = useState(0);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.all([fetchCampaigns(tokens.access), fetchCampaignDeliverables(tokens.access), fetchDocuments(tokens.access, { operating_context: workspaceId }), fetchOperatingContexts(tokens.access), fetchUsers(tokens.access)])
      .then(([campaignResponse, deliverableResponse, documentResponse, workspaceResponse, userResponse]) => {
        if (!mounted) return;
        const scoped = campaignResponse.results.filter((campaign) => campaign.operating_context === workspaceId);
        const campaignIds = new Set(scoped.map((campaign) => campaign.id));
        setCampaigns(scoped);
        setDeliverables(deliverableResponse.results.filter((deliverable) => campaignIds.has(deliverable.campaign)));
        setDocuments(documentResponse.results);
        setWorkspaces(workspaceResponse.results);
        setUsers(userResponse.results);
        setLoadedAt(Date.now());
      })
      .catch((err) => {
        if (!mounted) return;
        if (err instanceof ApiError && err.status === 403) setPermissionDenied(true);
        else setError('Marketing could not be loaded for this Workspace.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [tokens?.access, workspaceId]);

  async function handleAction(values: { comment: string; evidence: string }) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    try {
      if (action.kind === 'complete') {
        const updated = await completeCampaignDeliverable(tokens.access, action.deliverable.id, { comment: values.comment, evidence_document: values.evidence || null });
        setDeliverables((current) => current.map((item) => item.id === updated.id ? updated : item));
      } else {
        const updated = await setCampaignAction(tokens.access, action.campaign.id, action.kind, values.comment);
        setCampaigns((current) => current.map((campaign) => campaign.id === updated.id ? updated : campaign));
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

  if (loading) return <LoadingState label="Loading Workspace marketing" />;
  return <div className="space-y-4">{permissionDenied ? <PermissionDeniedState /> : null}{error ? <ErrorState message={error} /> : null}{campaigns.length ? <CampaignList campaigns={campaigns} deliverables={deliverables} documents={documents} now={loadedAt} onAction={setAction} users={users} workspaces={workspaces} /> : <EmptyState description="Marketing campaigns linked to this Workspace will appear here." title="No marketing campaign yet" />}<DeliverableActionDialog action={action} documents={documents} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} /></div>;
}


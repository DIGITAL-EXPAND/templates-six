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
import type { AudienceReportItem, CampaignDeliverableItem, CampaignItem, DocumentItem, OperatingContextListItem, SocialPostItem, UserListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const PLATFORM_COLOURS: Record<string, string> = {
  facebook:  'bg-blue-100 text-blue-700',
  instagram: 'bg-pink-100 text-pink-700',
  twitter:   'bg-sky-100 text-sky-700',
  linkedin:  'bg-indigo-100 text-indigo-700',
  tiktok:    'bg-gray-900 text-white',
  youtube:   'bg-red-100 text-red-700',
};

const POST_STATUS_COLOURS: Record<string, string> = {
  draft:     'bg-gray-100 text-gray-600',
  scheduled: 'bg-amber-100 text-amber-700',
  published: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-600',
};

function formatZAR(val: string | null | undefined) {
  if (!val) return 'R 0.00';
  return 'R ' + parseFloat(val).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function SocialPostsSection({ token }: { token: string }) {
  const [posts, setPosts] = useState<SocialPostItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    fetch('/api/v1/marketing/social-posts/?page_size=50', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { if (mounted) setPosts(data.results ?? []); })
      .catch(() => {})
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token]);

  if (loading) return <div className="py-8 text-center text-sm text-gray-400">Loading social posts…</div>;
  if (!posts.length) return <div className="py-8 text-center text-sm text-gray-400">No social posts found.</div>;

  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            {['Platform', 'Content', 'Status', 'Reach', 'Impressions', 'Engagements', 'Scheduled'].map(h => (
              <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {posts.map(post => (
            <tr key={post.id} className="hover:bg-gray-50">
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${PLATFORM_COLOURS[post.platform.toLowerCase()] ?? 'bg-gray-100 text-gray-700'}`}>
                  {post.platform}
                </span>
              </td>
              <td className="px-4 py-3 max-w-xs">
                <p className="truncate text-gray-700">{post.content}</p>
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${POST_STATUS_COLOURS[post.status] ?? 'bg-gray-100 text-gray-600'}`}>
                  {post.status}
                </span>
              </td>
              <td className="px-4 py-3 text-center text-gray-700">{post.reach.toLocaleString()}</td>
              <td className="px-4 py-3 text-center text-gray-700">{post.impressions.toLocaleString()}</td>
              <td className="px-4 py-3 text-center text-gray-700">{post.engagements.toLocaleString()}</td>
              <td className="px-4 py-3 text-xs text-gray-500">
                {post.scheduled_at ? new Date(post.scheduled_at).toLocaleDateString('en-ZA') : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AudienceReportsSection({ token }: { token: string }) {
  const [reports, setReports] = useState<AudienceReportItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    fetch('/api/v1/marketing/audience-reports/?page_size=50', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { if (mounted) setReports(data.results ?? []); })
      .catch(() => {})
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token]);

  if (loading) return <div className="py-8 text-center text-sm text-gray-400">Loading audience reports…</div>;
  if (!reports.length) return <div className="py-8 text-center text-sm text-gray-400">No audience reports found.</div>;

  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            {['Date', 'Attendance', 'Capacity', 'Occupancy', 'Revenue', 'Avg Ticket', 'Rating', 'Finalised'].map(h => (
              <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {reports.map(report => {
            const occupancyPct = Math.round(report.occupancy_rate * 100);
            return (
              <tr key={report.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-xs text-gray-500">
                  {new Date(report.created_at).toLocaleDateString('en-ZA')}
                </td>
                <td className="px-4 py-3 text-center font-medium text-gray-900">{report.total_attendance.toLocaleString()}</td>
                <td className="px-4 py-3 text-center text-gray-600">{report.capacity_total.toLocaleString()}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-16 rounded-full bg-gray-100 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${occupancyPct >= 80 ? 'bg-green-500' : occupancyPct >= 50 ? 'bg-amber-400' : 'bg-red-400'}`}
                        style={{ width: `${Math.min(occupancyPct, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-700">{occupancyPct}%</span>
                  </div>
                </td>
                <td className="px-4 py-3 font-semibold text-gray-800">{formatZAR(report.gross_revenue)}</td>
                <td className="px-4 py-3 text-gray-700">{formatZAR(report.average_ticket_price)}</td>
                <td className="px-4 py-3 text-gray-700">{report.average_rating}</td>
                <td className="px-4 py-3 text-center">
                  {report.is_finalised
                    ? <span className="text-green-600 text-xs font-medium">Yes</span>
                    : <span className="text-amber-500 text-xs">Pending</span>}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default function MarketingPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';
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

        {/* Social Posts */}
        {token && (
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-gray-800">Social Posts</h2>
            <p className="text-xs text-gray-500">Platform posts with reach and engagement metrics.</p>
            <SocialPostsSection token={token} />
          </section>
        )}

        {/* Audience Reports */}
        {token && (
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-gray-800">Audience Reports</h2>
            <p className="text-xs text-gray-500">Occupancy rates, revenue totals and ratings per production.</p>
            <AudienceReportsSection token={token} />
          </section>
        )}
      </div>
      <DeliverableActionDialog action={action} documents={documents} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} />
    </AppShell>
  );
}

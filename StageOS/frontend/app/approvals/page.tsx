'use client';

import { useEffect, useMemo, useState } from 'react';
import { ApprovalDecisionDialog, type ApprovalAction } from '@/components/approvals/approval-decision-dialog';
import { ApprovalList } from '@/components/approvals/approval-list';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { AppShell } from '@/components/app-shell/app-shell';
import { ApiError } from '@/lib/api/client';
import {
  decideApproval,
  fetchApprovalRequests,
  fetchApprovalSteps,
  fetchDocuments,
  fetchOperatingContexts,
  fetchOperatingProfile,
  fetchUsers,
} from '@/lib/api/endpoints';
import type {
  ApprovalDecision,
  ApprovalRequestItem,
  ApprovalStepItem,
  DocumentItem,
  OperatingContextListItem,
  OperatingProfile,
  UserListItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';
import { canApproveDepartment, dashboardKind } from '@/lib/role-experience';

export default function ApprovalsPage() {
  const { tokens } = useAuth();
  const [approvals, setApprovals] = useState<ApprovalRequestItem[]>([]);
  const [steps, setSteps] = useState<ApprovalStepItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [profile, setProfile] = useState<OperatingProfile | null>(null);
  const [decisionFilter, setDecisionFilter] = useState<'all' | ApprovalDecision>('pending');
  const [workspaceFilter, setWorkspaceFilter] = useState('all');
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequestItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) {
      return;
    }
    let mounted = true;
    Promise.all([
      fetchOperatingProfile(tokens.access),
      fetchApprovalSteps(tokens.access),
      fetchOperatingContexts(tokens.access),
      fetchUsers(tokens.access),
      fetchDocuments(tokens.access),
    ])
      .then(async ([profileResponse, stepResponse, workspaceResponse, userResponse, documentResponse]) => {
        if (!mounted) {
          return;
        }
        setProfile(profileResponse);
        setSteps(stepResponse.results);
        setWorkspaces(workspaceResponse.results);
        setUsers(userResponse.results);
        setDocuments(documentResponse.results);

        // Filter approvals to the user's primary department unless admin/executive
        const role = dashboardKind(profileResponse);
        const isAdminLevel = role === 'admin' || role === 'executive';
        const deptId = profileResponse.primary_department?.id;
        const approvalParams =
          !isAdminLevel && deptId ? { department: deptId } : undefined;
        const approvalResponse = await fetchApprovalRequests(tokens.access, approvalParams);
        if (mounted) setApprovals(approvalResponse.results);
      })
      .catch((err) => {
        if (!mounted) {
          return;
        }
        if (err instanceof ApiError && err.status === 403) {
          setPermissionDenied(true);
        } else {
          setError('Approvals could not be loaded.');
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

  const visibleApprovals = useMemo(() => {
    return approvals.filter((approval) => {
      if (decisionFilter !== 'all' && approval.decision !== decisionFilter) {
        return false;
      }
      if (workspaceFilter !== 'all' && approval.operating_context !== workspaceFilter) {
        return false;
      }
      return true;
    });
  }, [approvals, decisionFilter, workspaceFilter]);

  async function handleDecision(action: ApprovalAction, values: { comment: string; evidence: string }) {
    if (!tokens?.access || !selectedApproval) {
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const updated = await decideApproval(tokens.access, selectedApproval.id, action, {
        comment: values.comment,
        evidence: values.evidence || null,
      });
      setApprovals((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setSelectedApproval(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError('You do not have permission to approve this item.');
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Approval decision could not be submitted.');
      }
    } finally {
      setSubmitting(false);
    }
  }

  function canDecideApproval(approval: ApprovalRequestItem) {
    const role = dashboardKind(profile);
    if (['admin', 'executive'].includes(role)) return true;
    const step = steps.find((item) => item.id === approval.approval_step);
    return canApproveDepartment(profile, step?.approver_department);
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="Review approval requests, evidence and decision history across Workspaces."
          eyebrow="Approvals"
          title="Approvals"
        />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? (
          <LoadingState label="Loading approvals" />
        ) : (
          <>
            <div className="grid gap-2 md:grid-cols-2">
              <select
                aria-label="Filter approvals by decision"
                className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
                onChange={(event) => setDecisionFilter(event.target.value as 'all' | ApprovalDecision)}
                value={decisionFilter}
              >
                <option value="all">All decisions</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="changes_requested">Changes requested</option>
              </select>
              <select
                aria-label="Filter approvals by Workspace"
                className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700"
                onChange={(event) => setWorkspaceFilter(event.target.value)}
                value={workspaceFilter}
              >
                <option value="all">All Workspaces</option>
                {workspaces.map((workspace) => (
                  <option key={workspace.id} value={workspace.id}>
                    {workspace.title}
                  </option>
                ))}
              </select>
            </div>
            {visibleApprovals.length ? (
              <ApprovalList
                approvals={visibleApprovals}
                documents={documents}
                canDecide={canDecideApproval}
                onSelect={setSelectedApproval}
                steps={steps}
                users={users}
                workspaces={workspaces}
              />
            ) : (
              <EmptyState
                description="Approval requests will appear here when Workspaces are submitted for review."
                title="No approvals found"
              />
            )}
          </>
        )}
      </div>
      <ApprovalDecisionDialog
        approval={selectedApproval}
        documents={documents}
        onClose={() => setSelectedApproval(null)}
        onSubmit={handleDecision}
        submitting={submitting}
      />
    </AppShell>
  );
}

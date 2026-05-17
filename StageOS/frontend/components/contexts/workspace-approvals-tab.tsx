'use client';

import { useEffect, useState } from 'react';
import { ApprovalDecisionDialog, type ApprovalAction } from '@/components/approvals/approval-decision-dialog';
import { ApprovalList } from '@/components/approvals/approval-list';
import { ApprovalTimeline } from '@/components/approvals/approval-timeline';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
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
  ApprovalRequestItem,
  ApprovalStepItem,
  DocumentItem,
  OperatingContextListItem,
  OperatingProfile,
  UserListItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';
import { canApproveDepartment, dashboardKind } from '@/lib/role-experience';

export function WorkspaceApprovalsTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [approvals, setApprovals] = useState<ApprovalRequestItem[]>([]);
  const [steps, setSteps] = useState<ApprovalStepItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [profile, setProfile] = useState<OperatingProfile | null>(null);
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
      fetchApprovalRequests(tokens.access, { operating_context: workspaceId }),
      fetchApprovalSteps(tokens.access),
      fetchOperatingContexts(tokens.access),
      fetchUsers(tokens.access),
      fetchDocuments(tokens.access, { operating_context: workspaceId }),
      fetchOperatingProfile(tokens.access),
    ])
      .then(([approvalResponse, stepResponse, workspaceResponse, userResponse, documentResponse, profileResponse]) => {
        if (!mounted) {
          return;
        }
        setApprovals(approvalResponse.results);
        setSteps(stepResponse.results);
        setWorkspaces(workspaceResponse.results);
        setUsers(userResponse.results);
        setDocuments(documentResponse.results);
        setProfile(profileResponse);
      })
      .catch((err) => {
        if (!mounted) {
          return;
        }
        if (err instanceof ApiError && err.status === 403) {
          setPermissionDenied(true);
        } else {
          setError('Approvals could not be loaded for this Workspace.');
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
  }, [tokens?.access, workspaceId]);

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

  if (loading) {
    return <LoadingState label="Loading Workspace approvals" />;
  }

  const pending = approvals.filter((approval) => approval.decision === 'pending');
  const completed = approvals.filter((approval) => approval.decision !== 'pending');

  function canDecideApproval(approval: ApprovalRequestItem) {
    const role = dashboardKind(profile);
    if (['admin', 'executive'].includes(role)) return true;
    const step = steps.find((item) => item.id === approval.approval_step);
    return canApproveDepartment(profile, step?.approver_department);
  }

  return (
    <div className="space-y-4">
      {permissionDenied ? <PermissionDeniedState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {approvals.length ? (
        <>
          <ApprovalTimeline approvals={approvals} steps={steps} users={users} />
          {pending.length ? (
            <ApprovalList
              approvals={pending}
              documents={documents}
              canDecide={canDecideApproval}
              onSelect={setSelectedApproval}
              steps={steps}
              users={users}
              workspaces={workspaces}
            />
          ) : (
            <EmptyState description="No pending approvals for this Workspace." title="No pending decisions" />
          )}
          {completed.length ? (
            <ApprovalList
              approvals={completed}
              documents={documents}
              canDecide={canDecideApproval}
              onSelect={setSelectedApproval}
              steps={steps}
              users={users}
              workspaces={workspaces}
            />
          ) : null}
        </>
      ) : (
        <EmptyState
          description="Approval requests linked to this Workspace will appear here."
          title="No approvals yet"
        />
      )}
      <ApprovalDecisionDialog
        approval={selectedApproval}
        documents={documents}
        onClose={() => setSelectedApproval(null)}
        onSubmit={handleDecision}
        submitting={submitting}
      />
    </div>
  );
}

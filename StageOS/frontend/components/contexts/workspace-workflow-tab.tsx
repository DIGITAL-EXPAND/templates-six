'use client';

import { useEffect, useMemo, useState } from 'react';
import { WorkflowProgress } from '@/components/workflows/workflow-progress';
import { WorkflowStepList } from '@/components/workflows/workflow-step-list';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  advanceWorkflowStep,
  fetchApprovalRequests,
  fetchApprovalSteps,
  fetchDepartments,
  fetchDocuments,
  fetchUsers,
  fetchWorkflowInstances,
  fetchWorkflowSteps,
  fetchWorkflowStepTemplates,
  fetchWorkflowTemplates,
} from '@/lib/api/endpoints';
import type {
  ApprovalRequestItem,
  ApprovalStepItem,
  DepartmentListItem,
  DocumentItem,
  UserListItem,
  WorkflowInstanceItem,
  WorkflowStepItem,
  WorkflowStepTemplateItem,
  WorkflowTemplateItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceWorkflowTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [instances, setInstances] = useState<WorkflowInstanceItem[]>([]);
  const [steps, setSteps] = useState<WorkflowStepItem[]>([]);
  const [templates, setTemplates] = useState<WorkflowTemplateItem[]>([]);
  const [stepTemplates, setStepTemplates] = useState<WorkflowStepTemplateItem[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRequestItem[]>([]);
  const [approvalSteps, setApprovalSteps] = useState<ApprovalStepItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [advancingId, setAdvancingId] = useState('');

  useEffect(() => {
    if (!tokens?.access) {
      return;
    }
    let mounted = true;
    Promise.all([
      fetchWorkflowInstances(tokens.access, { operating_context: workspaceId }),
      fetchWorkflowTemplates(tokens.access),
      fetchWorkflowStepTemplates(tokens.access),
      fetchApprovalRequests(tokens.access, { operating_context: workspaceId }),
      fetchApprovalSteps(tokens.access),
      fetchDepartments(tokens.access),
      fetchUsers(tokens.access),
      fetchDocuments(tokens.access, { operating_context: workspaceId }),
    ])
      .then(async ([instanceResponse, templateResponse, stepTemplateResponse, approvalResponse, approvalStepResponse, departmentResponse, userResponse, documentResponse]) => {
        const workflowIds = instanceResponse.results.map((instance) => instance.id);
        const stepResponses = await Promise.all(
          workflowIds.map((workflowId) => fetchWorkflowSteps(tokens.access, { workflow_instance: workflowId })),
        );
        if (!mounted) {
          return;
        }
        setInstances(instanceResponse.results);
        setTemplates(templateResponse.results);
        setStepTemplates(stepTemplateResponse.results);
        setApprovals(approvalResponse.results);
        setApprovalSteps(approvalStepResponse.results);
        setDepartments(departmentResponse.results);
        setUsers(userResponse.results);
        setDocuments(documentResponse.results);
        setSteps(stepResponses.flatMap((response) => response.results));
      })
      .catch((err) => {
        if (!mounted) {
          return;
        }
        if (err instanceof ApiError && err.status === 403) {
          setPermissionDenied(true);
        } else {
          setError('Process could not be loaded for this Workspace.');
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

  const orderedSteps = useMemo(
    () => [...steps].sort((a, b) => a.workflow_instance.localeCompare(b.workflow_instance) || a.step_number - b.step_number),
    [steps],
  );

  async function handleAdvance(step: WorkflowStepItem, evidenceDocument: string, approvalRequest: string) {
    if (!tokens?.access) {
      return;
    }
    setAdvancingId(step.id);
    setError('');
    try {
      const updated = await advanceWorkflowStep(tokens.access, step.id, {
        notes: step.notes,
        evidence_document: evidenceDocument || step.evidence_document,
        approval_request: approvalRequest || step.approval_request,
      });
      setSteps((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setPermissionDenied(true);
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Process Step could not be completed.');
      }
    } finally {
      setAdvancingId('');
    }
  }

  if (loading) {
    return <LoadingState label="Loading Workspace Process" />;
  }

  return (
    <div className="space-y-4">
      {permissionDenied ? <PermissionDeniedState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {orderedSteps.length ? (
        <>
          <WorkflowProgress steps={orderedSteps} />
          <WorkflowStepList
            advancingId={advancingId}
            approvalSteps={approvalSteps}
            approvals={approvals}
            departments={departments}
            documents={documents}
            instances={instances}
            onAdvance={handleAdvance}
            stepTemplates={stepTemplates}
            steps={orderedSteps}
            templates={templates}
            users={users}
          />
        </>
      ) : (
        <EmptyState
          description="Process Steps will appear here once a Process has been started for this Workspace."
          title="No Process Steps yet"
        />
      )}
    </div>
  );
}

import { useState } from 'react';
import { StatusBadge } from '@/components/ui/status-badge';
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
import {
  departmentName,
  documentTitle,
  dueLabel,
  stepTemplate,
  userName,
  workflowName,
} from './helpers';

function statusTone(status: string) {
  if (status === 'completed') {
    return 'good';
  }
  if (status === 'blocked') {
    return 'danger';
  }
  if (status === 'in_progress') {
    return 'info';
  }
  return 'neutral';
}

export function WorkflowStepCard({
  step,
  instances,
  templates,
  stepTemplates,
  departments,
  users,
  documents,
  approvals,
  approvalSteps,
  advancingId,
  onAdvance,
}: {
  step: WorkflowStepItem;
  instances: WorkflowInstanceItem[];
  templates: WorkflowTemplateItem[];
  stepTemplates: WorkflowStepTemplateItem[];
  departments: DepartmentListItem[];
  users: UserListItem[];
  documents: DocumentItem[];
  approvals: ApprovalRequestItem[];
  approvalSteps: ApprovalStepItem[];
  advancingId: string;
  onAdvance: (step: WorkflowStepItem, evidenceDocument: string, approvalRequest: string) => void;
}) {
  const template = stepTemplate(stepTemplates, step);
  const [evidenceDocument, setEvidenceDocument] = useState(step.evidence_document ?? '');
  const [approvalRequest, setApprovalRequest] = useState(step.approval_request ?? '');
  const approvedApprovals = approvals.filter((approval) => ['approved', 'exception_approved'].includes(approval.decision));
  const blockers = step.blockers?.length ? step.blockers : [];

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-semibold text-blue-700">{workflowName(instances, templates, step)}</p>
          <h2 className="mt-1 text-base font-bold text-slate-950">
            Process Step {step.step_number}: {template?.name ?? 'Step unavailable'}
          </h2>
        </div>
        <StatusBadge tone={statusTone(step.status)}>{step.status.replace('_', ' ')}</StatusBadge>
      </div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="font-bold text-slate-700">Owner department</dt>
          <dd className="mt-1 text-slate-600">{departmentName(departments, step.owner_department ?? template?.owner_department)}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Assigned user</dt>
          <dd className="mt-1 text-slate-600">{userName(users, step.assigned_to)}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Responsible role</dt>
          <dd className="mt-1 text-slate-600">{step.owner_role_description || template?.owner_role_description || 'No role set'}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Due / SLA</dt>
          <dd className="mt-1 text-slate-600">{dueLabel(step.due_date)}{step.sla_days ? ` · ${step.sla_days} days` : ''}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Evidence</dt>
          <dd className="mt-1 text-slate-600">{documentTitle(documents, step.evidence_document)}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Evidence required</dt>
          <dd className="mt-1 text-slate-600">{step.requires_evidence || template?.requires_evidence ? 'Yes' : 'No'}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Approval required</dt>
          <dd className="mt-1 text-slate-600">{step.requires_approval || template?.requires_approval ? 'Yes' : 'No'}</dd>
        </div>
        <div>
          <dt className="font-bold text-slate-700">Linked Approval</dt>
          <dd className="mt-1 text-slate-600">{approvalSteps.find((item) => item.id === approvals.find((approval) => approval.id === step.approval_request)?.approval_step)?.name ?? 'No Approval linked'}</dd>
        </div>
      </dl>
      {step.requires_evidence ? (
        <label className="mt-4 block text-sm font-bold text-slate-800">
          Evidence for completion
          <select className="mt-2 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950" onChange={(event) => setEvidenceDocument(event.target.value)} value={evidenceDocument}>
            <option value="">Select evidence</option>
            {documents.map((document) => <option key={document.id} value={document.id}>{document.title}</option>)}
          </select>
        </label>
      ) : null}
      {step.requires_approval ? (
        <label className="mt-4 block text-sm font-bold text-slate-800">
          Approved Approval
          <select className="mt-2 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950" onChange={(event) => setApprovalRequest(event.target.value)} value={approvalRequest}>
            <option value="">Select approved Approval</option>
            {approvedApprovals.map((approval) => <option key={approval.id} value={approval.id}>{approvalSteps.find((item) => item.id === approval.approval_step)?.name ?? 'Approval'} · {approval.decision.replace('_', ' ')}</option>)}
          </select>
        </label>
      ) : null}
      {blockers.length ? (
        <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm font-medium text-amber-900">
          {blockers.join(' ')}
        </div>
      ) : null}
      <button
        className="mt-4 h-10 rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        disabled={step.status === 'completed' || advancingId === step.id}
        onClick={() => onAdvance(step, evidenceDocument, approvalRequest)}
        type="button"
      >
        {advancingId === step.id ? 'Completing step' : 'Complete step'}
      </button>
    </article>
  );
}

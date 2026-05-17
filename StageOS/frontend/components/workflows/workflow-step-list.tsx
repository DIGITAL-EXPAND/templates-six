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
import { WorkflowStepCard } from './workflow-step-card';

export function WorkflowStepList({
  steps,
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
  steps: WorkflowStepItem[];
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
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {steps.map((step) => (
        <WorkflowStepCard
          advancingId={advancingId}
          approvalSteps={approvalSteps}
          approvals={approvals}
          departments={departments}
          documents={documents}
          instances={instances}
          key={step.id}
          onAdvance={onAdvance}
          step={step}
          stepTemplates={stepTemplates}
          templates={templates}
          users={users}
        />
      ))}
    </div>
  );
}

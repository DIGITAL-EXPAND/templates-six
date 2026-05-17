'use client';

import { FormEvent, useMemo, useState } from 'react';
import type { DocumentItem, OperatingContextListItem, TaskItem } from '@/lib/api/types';

export type EvidenceFormValues = {
  operating_context: string;
  task: string;
  document: string;
  submission_note: string;
};

export function EvidenceSubmissionForm({
  workspaces,
  tasks,
  documents,
  defaultWorkspaceId = '',
  onSubmit,
}: {
  workspaces: OperatingContextListItem[];
  tasks: TaskItem[];
  documents: DocumentItem[];
  defaultWorkspaceId?: string;
  onSubmit: (values: EvidenceFormValues) => Promise<void>;
}) {
  const initialWorkspace = defaultWorkspaceId || workspaces[0]?.id || '';
  const [values, setValues] = useState<EvidenceFormValues>({
    operating_context: initialWorkspace,
    task: '',
    document: '',
    submission_note: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const filteredTasks = useMemo(
    () => tasks.filter((task) => task.operating_context === values.operating_context),
    [tasks, values.operating_context],
  );
  const filteredDocuments = useMemo(
    () => documents.filter((document) => document.operating_context === values.operating_context),
    [documents, values.operating_context],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(values);
      setValues((current) => ({ ...current, submission_note: '' }));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="grid gap-4 rounded-lg border border-slate-200 bg-white p-4" onSubmit={handleSubmit}>
      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="evidence-workspace">
            Workspace
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            disabled={Boolean(defaultWorkspaceId)}
            id="evidence-workspace"
            onChange={(event) =>
              setValues({ ...values, operating_context: event.target.value, task: '', document: '' })
            }
            required
            value={values.operating_context}
          >
            {workspaces.map((workspace) => (
              <option key={workspace.id} value={workspace.id}>
                {workspace.title}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="evidence-task">
            Task
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            id="evidence-task"
            onChange={(event) => setValues({ ...values, task: event.target.value })}
            value={values.task}
          >
            <option value="">No task linked</option>
            {filteredTasks.map((task) => (
              <option key={task.id} value={task.id}>
                {task.title}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="evidence-document">
            Document
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            id="evidence-document"
            onChange={(event) => setValues({ ...values, document: event.target.value })}
            required
            value={values.document}
          >
            <option value="">Select document</option>
            {filteredDocuments.map((document) => (
              <option key={document.id} value={document.id}>
                {document.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="evidence-note">
          Evidence note
        </label>
        <textarea
          className="min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950"
          id="evidence-note"
          onChange={(event) => setValues({ ...values, submission_note: event.target.value })}
          value={values.submission_note}
        />
      </div>

      <button
        className="inline-flex h-10 w-fit items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        disabled={submitting || !values.operating_context || !values.document}
        type="submit"
      >
        {submitting ? 'Submitting' : 'Submit Evidence'}
      </button>
    </form>
  );
}

'use client';

import { FormEvent, useState } from 'react';
import type { OperatingContextListItem } from '@/lib/api/types';

const documentTypes = [
  'brief',
  'plan',
  'proposal',
  'contract',
  'rider',
  'report',
  'evidence',
  'csd_pack',
  'show_report',
  'closeout',
  'marketing_asset',
  'consent_form',
  'attendance_register',
  'assessment',
  'other',
];

export type DocumentFormValues = {
  operating_context: string;
  title: string;
  document_type: string;
  file_name: string;
  file: File | null;
  version: number;
};

export function DocumentForm({
  workspaces,
  defaultWorkspaceId = '',
  onSubmit,
}: {
  workspaces: OperatingContextListItem[];
  defaultWorkspaceId?: string;
  onSubmit: (values: DocumentFormValues) => Promise<void>;
}) {
  const [values, setValues] = useState<DocumentFormValues>({
    operating_context: defaultWorkspaceId || workspaces[0]?.id || '',
    title: '',
    document_type: 'evidence',
    file_name: '',
    file: null,
    version: 1,
  });
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(values);
      setValues((current) => ({
        ...current,
        title: '',
        file_name: '',
        file: null,
        version: 1,
      }));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="grid gap-4 rounded-lg border border-slate-200 bg-white p-4" onSubmit={handleSubmit}>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="document-title">
            Document title
          </label>
          <input
            className="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950"
            id="document-title"
            onChange={(event) => setValues({ ...values, title: event.target.value })}
            required
            value={values.title}
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="document-workspace">
            Workspace
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            disabled={Boolean(defaultWorkspaceId)}
            id="document-workspace"
            onChange={(event) => setValues({ ...values, operating_context: event.target.value })}
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
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="document-type">
            Type
          </label>
          <select
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
            id="document-type"
            onChange={(event) => setValues({ ...values, document_type: event.target.value })}
            value={values.document_type}
          >
            {documentTypes.map((type) => (
              <option key={type} value={type}>
                {type.replaceAll('_', ' ')}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="file-name">
            File name or upload
          </label>
          <input
            className="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950"
            id="file-name"
            onChange={(event) => setValues({ ...values, file_name: event.target.value })}
            required={!values.file}
            value={values.file_name}
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="version">
            Version
          </label>
          <input
            className="h-10 w-full rounded-md border border-slate-300 px-3 text-slate-950"
            id="version"
            min={1}
            onChange={(event) => setValues({ ...values, version: Number(event.target.value) })}
            required
            type="number"
            value={values.version}
          />
        </div>
      </div>
      <div>
        <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="document-file">
          Stored file
        </label>
        <input
          className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-950"
          id="document-file"
          onChange={(event) => {
            const file = event.target.files?.[0] ?? null;
            setValues({ ...values, file, file_name: file?.name ?? values.file_name });
          }}
          type="file"
        />
      </div>
      <p className="text-xs text-slate-500">
        Uploading a file stores it through the backend. Without a file, StageOS creates a metadata-only record.
      </p>
      <button
        className="inline-flex h-10 w-fit items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        disabled={submitting || !values.operating_context}
        type="submit"
      >
        {submitting ? 'Creating' : 'Add Document'}
      </button>
    </form>
  );
}

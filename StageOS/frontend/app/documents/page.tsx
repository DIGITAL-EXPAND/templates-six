'use client';

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DocumentForm, type DocumentFormValues } from '@/components/documents/document-form';
import { DocumentList } from '@/components/documents/document-list';
import { EvidenceList } from '@/components/documents/evidence-list';
import {
  EvidenceSubmissionForm,
  type EvidenceFormValues,
} from '@/components/documents/evidence-submission-form';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { PageHeader } from '@/components/ui/page-header';
import { ApiError } from '@/lib/api/client';
import {
  acceptEvidence,
  createDocument,
  downloadDocument,
  fetchDocuments,
  fetchEvidence,
  fetchOperatingContexts,
  fetchTasks,
  fetchUsers,
  rejectEvidence,
  submitEvidence,
  uploadDocumentFile,
} from '@/lib/api/endpoints';
import type {
  DocumentItem,
  EvidenceSubmissionItem,
  OperatingContextListItem,
  TaskItem,
  UserListItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type DocumentCategory = 'all' | 'evidence' | 'contract' | 'report' | 'template';

const CATEGORY_LABELS: Record<DocumentCategory, string> = {
  all: 'All Files',
  evidence: 'Evidence / Supporting Files',
  contract: 'Contracts & Agreements',
  report: 'Reports & Data',
  template: 'Templates',
};

const CATEGORY_TYPES: Record<Exclude<DocumentCategory, 'all'>, string[]> = {
  evidence: ['evidence', 'supporting_file', 'supporting'],
  contract: ['contract', 'agreement', 'legal'],
  report: ['report', 'data', 'export'],
  template: ['template'],
};

export default function DocumentsPage() {
  const { tokens } = useAuth();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [evidence, setEvidence] = useState<EvidenceSubmissionItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [acceptingId, setAcceptingId] = useState('');
  const [rejectingId, setRejectingId] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<DocumentCategory>('all');

  const filteredDocuments = useMemo(() => {
    if (categoryFilter === 'all') return documents;
    const allowedTypes = CATEGORY_TYPES[categoryFilter];
    return documents.filter((doc) =>
      allowedTypes.some((t) => doc.document_type?.toLowerCase().includes(t)),
    );
  }, [documents, categoryFilter]);

  useEffect(() => {
    if (!tokens?.access) {
      return;
    }

    let mounted = true;
    Promise.all([
      fetchDocuments(tokens.access),
      fetchEvidence(tokens.access),
      fetchOperatingContexts(tokens.access),
      fetchTasks(tokens.access),
      fetchUsers(tokens.access),
    ])
      .then(([documentResponse, evidenceResponse, workspaceResponse, taskResponse, userResponse]) => {
        if (!mounted) {
          return;
        }
        setDocuments(documentResponse.results);
        setEvidence(evidenceResponse.results);
        setWorkspaces(workspaceResponse.results);
        setTasks(taskResponse.results);
        setUsers(userResponse.results);
      })
      .catch((err) => {
        if (!mounted) {
          return;
        }
        if (err instanceof ApiError && err.status === 403) {
          setPermissionDenied(true);
        } else {
          setError('Documents and evidence could not be loaded.');
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

  async function handleCreateDocument(values: DocumentFormValues) {
    if (!tokens?.access) {
      return;
    }
    setError('');
    try {
      const document = values.file
        ? await uploadDocumentFile(tokens.access, {
            operating_context: values.operating_context,
            title: values.title,
            document_type: values.document_type,
            file: values.file,
            version: values.version,
          })
        : await createDocument(tokens.access, values);
      setDocuments((current) => [document, ...current]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setPermissionDenied(true);
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Document could not be created.');
      }
    }
  }

  async function handleSubmitEvidence(values: EvidenceFormValues) {
    if (!tokens?.access) {
      return;
    }
    setError('');
    try {
      const submission = await submitEvidence(tokens.access, {
        operating_context: values.operating_context,
        task: values.task || null,
        document: values.document,
        submission_note: values.submission_note,
      });
      setEvidence((current) => [submission, ...current]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setPermissionDenied(true);
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Evidence could not be submitted.');
      }
    }
  }

  async function handleAcceptEvidence(item: EvidenceSubmissionItem) {
    if (!tokens?.access) {
      return;
    }
    setAcceptingId(item.id);
    setError('');
    try {
      const updated = await acceptEvidence(tokens.access, item.id);
      setEvidence((current) => current.map((entry) => (entry.id === updated.id ? updated : entry)));
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setPermissionDenied(true);
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Evidence could not be accepted.');
      }
    } finally {
      setAcceptingId('');
    }
  }

  async function handleRejectEvidence(item: EvidenceSubmissionItem) {
    if (!tokens?.access) {
      return;
    }
    const reason = window.prompt('Rejection reason');
    if (!reason) {
      return;
    }
    setRejectingId(item.id);
    setError('');
    try {
      const updated = await rejectEvidence(tokens.access, item.id, reason);
      setEvidence((current) => current.map((entry) => (entry.id === updated.id ? updated : entry)));
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setPermissionDenied(true);
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Evidence could not be rejected.');
      }
    } finally {
      setRejectingId('');
    }
  }

  async function handleDownloadDocument(item: DocumentItem) {
    if (!tokens?.access) return;
    setError('');
    try {
      const blob = await downloadDocument(tokens.access, item.id);
      const url = URL.createObjectURL(blob);
      const link = window.document.createElement('a');
      link.href = url;
      link.download = item.file_name || 'document';
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setError('Document could not be downloaded.');
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="Manage documents, evidence submissions, accepted evidence and locked records."
          eyebrow="Evidence"
          title="Documents"
        />

        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}

        {loading ? (
          <LoadingState label="Loading documents and evidence" />
        ) : (
          <>
            <DocumentForm onSubmit={handleCreateDocument} workspaces={workspaces} />
            <EvidenceSubmissionForm
              documents={documents}
              onSubmit={handleSubmitEvidence}
              tasks={tasks}
              workspaces={workspaces}
            />

            {/* Category filter bar */}
            <div className="flex flex-wrap gap-2">
              {(Object.keys(CATEGORY_LABELS) as DocumentCategory[]).map((cat) => (
                <button
                  className={`rounded-full border px-3 py-1 text-xs font-semibold transition-colors ${
                    categoryFilter === cat
                      ? 'border-teal-600 bg-teal-600 text-white'
                      : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                  key={cat}
                  onClick={() => setCategoryFilter(cat)}
                  type="button"
                >
                  {CATEGORY_LABELS[cat]}
                </button>
              ))}
            </div>

            {filteredDocuments.length ? (
              <DocumentList documents={filteredDocuments} onDownload={handleDownloadDocument} users={users} workspaces={workspaces} />
            ) : (
              <EmptyState
                description="Add document metadata first, then link it as evidence where needed."
                title="No documents found"
              />
            )}
            {evidence.length ? (
              <EvidenceList
                acceptingId={acceptingId}
                documents={documents}
                evidence={evidence}
                onAccept={handleAcceptEvidence}
                onReject={handleRejectEvidence}
                rejectingId={rejectingId}
                tasks={tasks}
                users={users}
              />
            ) : (
              <EmptyState
                description="Submit evidence against a Workspace or task once a document exists."
                title="No evidence submissions found"
              />
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}

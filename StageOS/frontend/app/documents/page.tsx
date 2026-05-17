'use client';

import { useEffect, useState } from 'react';
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
            {documents.length ? (
              <DocumentList documents={documents} onDownload={handleDownloadDocument} users={users} workspaces={workspaces} />
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

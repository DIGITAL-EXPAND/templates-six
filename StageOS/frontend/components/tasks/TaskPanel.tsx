'use client';

import { useEffect, useRef, useState } from 'react';
import { AlertTriangle, Paperclip, Send, X } from 'lucide-react';
import {
  blockTask,
  completeTask,
  createTaskComment,
  fetchEvidence,
  fetchTaskComments,
  reopenTask,
  startTask,
  submitEvidence,
  uploadDocumentFile,
} from '@/lib/api/endpoints';
import type {
  EvidenceSubmissionItem,
  TaskCommentItem,
  TaskItem,
} from '@/lib/api/types';
import { EVIDENCE_LABELS, TASK_LABELS } from '@/lib/labels';
import { apiRequest } from '@/lib/api/client';
import { useAuth } from '@/lib/auth/auth-provider';

export interface TaskPanelProps {
  taskId: string | null;
  onClose: () => void;
  onTaskUpdate?: (task: TaskItem) => void;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function fetchTaskById(token: string, id: string) {
  return apiRequest<TaskItem>(`/api/v1/tasks/${id}/`, { method: 'GET', token });
}

function formatDate(dateStr: string | null | undefined, showRelative = true) {
  if (!dateStr) return 'No due date';
  const date = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diff = Math.round((date.getTime() - today.getTime()) / 86400000);
  const formatted = date.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short', year: 'numeric' });
  if (!showRelative) return formatted;
  if (diff < 0) return `${formatted} (${Math.abs(diff)} day${Math.abs(diff) !== 1 ? 's' : ''} overdue)`;
  if (diff === 0) return `${formatted} (today)`;
  if (diff === 1) return `${formatted} (tomorrow)`;
  return formatted;
}

function isOverdue(task: TaskItem) {
  if (!task.due_date || task.status === 'done' || task.status === 'cancelled') return false;
  return task.due_date < new Date().toISOString().slice(0, 10);
}

function formatRelativeTime(isoStr: string) {
  const diff = Date.now() - new Date(isoStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

// ── Status / Priority badges ─────────────────────────────────────────────────

type TaskStatus = TaskItem['status'];
type Priority = TaskItem['priority'];

const STATUS_CLASSES: Record<TaskStatus, string> = {
  open:        'bg-gray-100 text-gray-700',
  in_progress: 'bg-blue-100 text-blue-700',
  blocked:     'bg-red-100 text-red-700',
  done:        'bg-green-100 text-green-700',
  cancelled:   'bg-gray-100 text-gray-400',
};

const PRIORITY_CLASSES: Record<Priority, string> = {
  critical: 'bg-red-100 text-red-700',
  high:     'bg-orange-100 text-orange-700',
  medium:   'bg-blue-100 text-blue-700',
  low:      'bg-gray-100 text-gray-600',
};

function StatusBadge({ status }: { status: TaskStatus }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_CLASSES[status]}`}>
      {TASK_LABELS.statusShort[status]}
    </span>
  );
}

function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${PRIORITY_CLASSES[priority]}`}>
      {TASK_LABELS.priorities[priority]}
    </span>
  );
}

// ── Evidence badge ────────────────────────────────────────────────────────────

function EvidenceStatusBadge({ item }: { item: EvidenceSubmissionItem }) {
  if (item.accepted) {
    return (
      <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700">
        {EVIDENCE_LABELS.accepted}
      </span>
    );
  }
  if (item.rejected) {
    return (
      <span className="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
        {EVIDENCE_LABELS.rejected}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700">
      {EVIDENCE_LABELS.pending}
    </span>
  );
}

// ── Spinner ───────────────────────────────────────────────────────────────────

function Spinner() {
  return (
    <div className="flex h-full items-center justify-center py-16">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-teal-600" />
    </div>
  );
}

// ── Avatar ────────────────────────────────────────────────────────────────────

function Avatar({ name }: { name: string }) {
  const initials = name
    .split(' ')
    .map((n) => n[0] ?? '')
    .slice(0, 2)
    .join('')
    .toUpperCase();
  return (
    <span className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-700">
      {initials || '?'}
    </span>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export function TaskPanel({ taskId, onClose, onTaskUpdate }: TaskPanelProps) {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';

  const [task, setTask] = useState<TaskItem | null>(null);
  const [comments, setComments] = useState<TaskCommentItem[]>([]);
  const [evidence, setEvidence] = useState<EvidenceSubmissionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [actionError, setActionError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  // Comment composer
  const [commentBody, setCommentBody] = useState('');
  const [postingComment, setPostingComment] = useState(false);

  // Block reason
  const [blockReason, setBlockReason] = useState('');
  const [showBlockForm, setShowBlockForm] = useState(false);

  // File upload
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const isOpen = taskId !== null;

  // Fetch task + comments + evidence whenever taskId changes
  useEffect(() => {
    if (!taskId || !token) {
      setTask(null);
      setComments([]);
      setEvidence([]);
      return;
    }

    let mounted = true;
    setLoading(true);
    setError('');
    setActionError('');
    setShowBlockForm(false);
    setBlockReason('');

    Promise.allSettled([
      fetchTaskById(token, taskId),
      fetchTaskComments(token, taskId),
      fetchEvidence(token, { task: taskId }),
    ]).then(([taskRes, commentsRes, evidenceRes]) => {
      if (!mounted) return;
      if (taskRes.status === 'fulfilled') {
        setTask(taskRes.value);
      } else {
        setError('Could not load this action. Please try again.');
      }
      if (commentsRes.status === 'fulfilled') {
        setComments(commentsRes.value.results);
      }
      if (evidenceRes.status === 'fulfilled') {
        setEvidence(evidenceRes.value.results);
      }
      setLoading(false);
    });

    return () => { mounted = false; };
  }, [taskId, token]);

  // ── Action handlers ─────────────────────────────────────────────────────────

  async function handleStart() {
    if (!task || !token) return;
    setActionLoading(true);
    setActionError('');
    try {
      const updated = await startTask(token, task.id);
      setTask(updated);
      onTaskUpdate?.(updated);
    } catch {
      setActionError('Could not start this action. Please try again.');
    } finally {
      setActionLoading(false);
    }
  }

  async function handleComplete() {
    if (!task || !token) return;
    const hasAcceptedEvidence = evidence.some((e) => e.accepted);
    setActionLoading(true);
    setActionError('');
    try {
      const updated = await completeTask(token, task.id, hasAcceptedEvidence);
      setTask(updated);
      onTaskUpdate?.(updated);
    } catch {
      setActionError('Could not mark this action as done. Please try again.');
    } finally {
      setActionLoading(false);
    }
  }

  async function handleBlock() {
    if (!task || !token || !blockReason.trim()) return;
    setActionLoading(true);
    setActionError('');
    try {
      const updated = await blockTask(token, task.id, blockReason.trim());
      setTask(updated);
      onTaskUpdate?.(updated);
      setShowBlockForm(false);
      setBlockReason('');
    } catch {
      setActionError('Could not mark this action as stuck. Please try again.');
    } finally {
      setActionLoading(false);
    }
  }

  async function handleReopen() {
    if (!task || !token) return;
    setActionLoading(true);
    setActionError('');
    try {
      const updated = await reopenTask(token, task.id);
      setTask(updated);
      onTaskUpdate?.(updated);
    } catch {
      setActionError('Could not reopen this action. Please try again.');
    } finally {
      setActionLoading(false);
    }
  }

  async function handlePostComment() {
    if (!task || !token || !commentBody.trim()) return;
    setPostingComment(true);
    try {
      const comment = await createTaskComment(token, { task: task.id, body: commentBody.trim() });
      setComments((prev) => [...prev, comment]);
      setCommentBody('');
    } catch {
      setActionError('Could not post note. Please try again.');
    } finally {
      setPostingComment(false);
    }
  }

  async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || !task || !token) return;
    setUploadingFile(true);
    setUploadError('');
    try {
      const doc = await uploadDocumentFile(token, {
        operating_context: task.operating_context,
        title: file.name,
        document_type: 'evidence',
        file,
      });
      const submission = await submitEvidence(token, {
        operating_context: task.operating_context,
        task: task.id,
        document: doc.id,
        submission_note: `Uploaded for: ${task.title}`,
      });
      setEvidence((prev) => [...prev, submission]);
      // Refresh task to get updated evidence_provided flag
      const updated = await fetchTaskById(token, task.id);
      setTask(updated);
      onTaskUpdate?.(updated);
    } catch {
      setUploadError('File upload failed. Please try again.');
    } finally {
      setUploadingFile(false);
      // Reset input so same file can be re-uploaded if needed
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }

  // ── Derived state ────────────────────────────────────────────────────────────

  const hasAcceptedEvidence = evidence.some((e) => e.accepted);
  const canMarkDone = !task?.evidence_required || hasAcceptedEvidence;
  const overdue = task ? isOverdue(task) : false;

  // ── Work-type label ──────────────────────────────────────────────────────────

  function workTypeLabel(wt: TaskItem['work_type']) {
    return TASK_LABELS.workTypes[wt] ?? wt.replace(/_/g, ' ');
  }

  // ── Panel body ───────────────────────────────────────────────────────────────

  return (
    <>
      {/* Backdrop (mobile) */}
      <div
        className={`fixed inset-0 z-40 bg-black/30 transition-opacity duration-300 md:hidden ${
          isOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
        aria-hidden="true"
        onClick={onClose}
      />

      {/* Panel */}
      <aside
        aria-label="Action detail panel"
        className={`fixed inset-y-0 right-0 z-50 flex w-full max-w-[480px] flex-col bg-white shadow-xl transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* ── Header ─────────────────────────────────────────────────────────── */}
        <div className="border-b border-gray-200 px-5 py-4">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              {task ? (
                <>
                  <p className="truncate text-lg font-semibold text-gray-900">{task.title}</p>
                  {task.operating_context ? (
                    <p className="mt-0.5 text-sm text-gray-500">Production</p>
                  ) : null}
                </>
              ) : loading ? (
                <p className="text-sm text-gray-400">Loading…</p>
              ) : (
                <p className="text-sm text-gray-400">No action selected</p>
              )}
            </div>
            <button
              aria-label="Close panel"
              className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50"
              onClick={onClose}
              type="button"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {task ? (
            <div className="mt-3 flex flex-wrap gap-2">
              <StatusBadge status={task.status} />
              <PriorityBadge priority={task.priority} />
              {overdue ? (
                <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700">
                  Overdue
                </span>
              ) : null}
            </div>
          ) : null}
        </div>

        {/* ── Body (scrollable) ───────────────────────────────────────────────── */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <Spinner />
          ) : error ? (
            <div className="m-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          ) : task ? (
            <div className="divide-y divide-gray-100">

              {/* Details section */}
              <section className="px-5 py-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400">Details</h3>
                <dl className="mt-3 grid gap-3 text-sm">
                  <div className="flex items-start gap-3">
                    <dt className="w-28 shrink-0 font-medium text-gray-500">Assigned to</dt>
                    <dd className="flex items-center gap-2 text-gray-900">
                      {task.assigned_to ? (
                        <>
                          <Avatar name={task.assigned_to} />
                          <span className="truncate">{task.assigned_to}</span>
                        </>
                      ) : (
                        <span className="text-gray-400">Unassigned</span>
                      )}
                    </dd>
                  </div>
                  {task.assigned_by ? (
                    <div className="flex items-start gap-3">
                      <dt className="w-28 shrink-0 font-medium text-gray-500">Assigned by</dt>
                      <dd className="text-gray-900">{task.assigned_by}</dd>
                    </div>
                  ) : null}
                  <div className="flex items-start gap-3">
                    <dt className="w-28 shrink-0 font-medium text-gray-500">Due</dt>
                    <dd className={`${overdue ? 'font-semibold text-red-600' : 'text-gray-900'}`}>
                      {formatDate(task.due_date)}
                    </dd>
                  </div>
                  <div className="flex items-start gap-3">
                    <dt className="w-28 shrink-0 font-medium text-gray-500">Category</dt>
                    <dd className="text-gray-900">{workTypeLabel(task.work_type)}</dd>
                  </div>
                  {task.description ? (
                    <div className="flex items-start gap-3">
                      <dt className="w-28 shrink-0 font-medium text-gray-500">Description</dt>
                      <dd className="whitespace-pre-line text-gray-900">{task.description}</dd>
                    </div>
                  ) : null}
                </dl>
              </section>

              {/* Blocked banner */}
              {task.status === 'blocked' && task.blocked_reason ? (
                <section className="px-5 py-4">
                  <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-3">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-600" />
                    <div>
                      <p className="text-sm font-semibold text-red-800">Stuck — needs help</p>
                      <p className="mt-1 text-sm text-red-700">{task.blocked_reason}</p>
                    </div>
                  </div>
                </section>
              ) : null}

              {/* Files & Evidence section */}
              <section className="px-5 py-4">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                    {EVIDENCE_LABELS.plural}
                  </h3>
                  <button
                    className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-xs font-semibold text-gray-700 shadow-sm hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={uploadingFile}
                    onClick={() => fileInputRef.current?.click()}
                    type="button"
                  >
                    <Paperclip className="h-3 w-3" />
                    {uploadingFile ? 'Uploading…' : EVIDENCE_LABELS.upload}
                  </button>
                  <input
                    accept="*/*"
                    className="hidden"
                    onChange={handleFileSelect}
                    ref={fileInputRef}
                    type="file"
                  />
                </div>

                {task.evidence_required && !hasAcceptedEvidence ? (
                  <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
                    {TASK_LABELS.evidenceRequired}
                  </div>
                ) : null}

                {uploadError ? (
                  <p className="mt-2 text-xs text-red-600">{uploadError}</p>
                ) : null}

                {evidence.length > 0 ? (
                  <ul className="mt-3 divide-y divide-gray-100 rounded-lg border border-gray-200">
                    {evidence.map((item) => (
                      <li className="flex items-start justify-between gap-3 px-3 py-2.5" key={item.id}>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium text-gray-900">
                            {item.submission_note || 'Uploaded file'}
                          </p>
                          <p className="text-xs text-gray-400">{formatDate(item.created_at, false)}</p>
                          {item.rejected && item.rejection_reason ? (
                            <p className="mt-1 text-xs text-red-600">{item.rejection_reason}</p>
                          ) : null}
                        </div>
                        <EvidenceStatusBadge item={item} />
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-3 text-sm text-gray-400">No files uploaded yet.</p>
                )}
              </section>

              {/* Notes & Discussion */}
              <section className="px-5 py-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400">Notes</h3>

                {comments.length > 0 ? (
                  <ul className="mt-3 space-y-3">
                    {comments.map((comment) => (
                      <li className="flex items-start gap-2.5" key={comment.id}>
                        <Avatar name={comment.author_name ?? comment.author_email ?? 'U'} />
                        <div className="flex-1 rounded-lg border border-gray-100 bg-gray-50 px-3 py-2">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-xs font-semibold text-gray-700">
                              {comment.author_name ?? comment.author_email ?? 'Team member'}
                            </span>
                            <span className="text-xs text-gray-400">{formatRelativeTime(comment.created_at)}</span>
                          </div>
                          <p className="mt-1 whitespace-pre-line text-sm text-gray-800">{comment.body}</p>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-3 text-sm text-gray-400">No notes yet.</p>
                )}

                {/* Compose note */}
                <div className="mt-4">
                  <textarea
                    className="w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
                    onChange={(e) => setCommentBody(e.target.value)}
                    placeholder="Add a note…"
                    rows={3}
                    value={commentBody}
                  />
                  <div className="mt-2 flex justify-end">
                    <button
                      className="inline-flex items-center gap-2 rounded-lg bg-teal-600 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-gray-300"
                      disabled={!commentBody.trim() || postingComment}
                      onClick={handlePostComment}
                      type="button"
                    >
                      <Send className="h-3.5 w-3.5" />
                      {postingComment ? 'Posting…' : 'Post'}
                    </button>
                  </div>
                </div>
              </section>

              {/* Block form (shown inline when needed) */}
              {showBlockForm ? (
                <section className="px-5 py-4">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                    Describe what&apos;s blocking you
                  </h3>
                  <textarea
                    autoFocus
                    className="mt-3 w-full resize-none rounded-lg border border-red-200 px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-red-400 focus:outline-none focus:ring-1 focus:ring-red-400"
                    onChange={(e) => setBlockReason(e.target.value)}
                    placeholder="What's stopping you from progressing?"
                    rows={3}
                    value={blockReason}
                  />
                  <div className="mt-2 flex gap-2">
                    <button
                      className="rounded-lg border border-red-200 px-4 py-2 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                      disabled={!blockReason.trim() || actionLoading}
                      onClick={handleBlock}
                      type="button"
                    >
                      {actionLoading ? 'Saving…' : "Mark as Stuck"}
                    </button>
                    <button
                      className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50"
                      onClick={() => { setShowBlockForm(false); setBlockReason(''); }}
                      type="button"
                    >
                      Cancel
                    </button>
                  </div>
                </section>
              ) : null}

            </div>
          ) : null}
        </div>

        {/* ── Footer (sticky action bar) ──────────────────────────────────────── */}
        {task && !loading ? (
          <div className="border-t border-gray-200 bg-white px-5 py-4">
            {actionError ? (
              <p className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs font-medium text-red-700">
                {actionError}
              </p>
            ) : null}

            <div className="flex flex-wrap items-center gap-2">
              {task.status === 'open' ? (
                <button
                  className="flex-1 rounded-lg bg-teal-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-gray-300"
                  disabled={actionLoading}
                  onClick={handleStart}
                  type="button"
                >
                  {actionLoading ? 'Starting…' : TASK_LABELS.actions.start}
                </button>
              ) : null}

              {task.status === 'in_progress' ? (
                <>
                  <button
                    className="flex-1 rounded-lg bg-teal-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-gray-300 disabled:opacity-60"
                    disabled={actionLoading || !canMarkDone}
                    onClick={handleComplete}
                    title={!canMarkDone ? TASK_LABELS.evidenceRequired : undefined}
                    type="button"
                  >
                    {actionLoading ? 'Saving…' : TASK_LABELS.actions.complete}
                  </button>
                  <button
                    className="rounded-lg border border-red-200 px-4 py-2.5 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:cursor-not-allowed"
                    disabled={actionLoading}
                    onClick={() => setShowBlockForm(true)}
                    type="button"
                  >
                    {TASK_LABELS.actions.block}
                  </button>
                </>
              ) : null}

              {task.status === 'blocked' ? (
                <button
                  className="flex-1 rounded-lg bg-teal-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-gray-300"
                  disabled={actionLoading}
                  onClick={handleStart}
                  type="button"
                >
                  {actionLoading ? 'Saving…' : 'Start Working Again'}
                </button>
              ) : null}

              {task.status === 'done' ? (
                <button
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed"
                  disabled={actionLoading}
                  onClick={handleReopen}
                  type="button"
                >
                  {actionLoading ? 'Saving…' : TASK_LABELS.actions.reopen}
                </button>
              ) : null}
            </div>

            {task.status !== 'cancelled' && task.status !== 'done' ? (
              <div className="mt-3 border-t border-gray-100 pt-3">
                <button
                  className="text-xs font-medium text-red-500 hover:text-red-700"
                  onClick={onClose}
                  type="button"
                >
                  {TASK_LABELS.actions.cancel}
                </button>
              </div>
            ) : null}
          </div>
        ) : null}
      </aside>
    </>
  );
}

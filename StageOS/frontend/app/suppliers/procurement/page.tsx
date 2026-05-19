'use client';

import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  approvePurchaseRequisition,
  fetchOperatingProfile,
  fetchPurchaseRequisitions,
  rejectPurchaseRequisition,
} from '@/lib/api/endpoints';
import type { OperatingProfile, PurchaseRequisitionItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function formatZAR(value: string) {
  return 'R ' + parseFloat(value).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

const STATUS_BADGE: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-700',
  submitted: 'bg-blue-100 text-blue-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  po_issued: 'bg-purple-100 text-purple-700',
  cancelled: 'bg-slate-100 text-slate-600',
};

const ALL_STATUSES = ['draft', 'submitted', 'approved', 'rejected', 'po_issued', 'cancelled'];

const MANAGER_AUTHORITY_LEVELS = ['department_manager', 'executive', 'gm'];

function StatusBadge({ status }: { status: string }) {
  const cls = STATUS_BADGE[status] ?? 'bg-slate-100 text-slate-600';
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      {status.replace(/_/g, ' ')}
    </span>
  );
}

type RejectModalProps = {
  requisition: PurchaseRequisitionItem;
  onClose: () => void;
  onConfirm: (reason: string) => void;
  submitting: boolean;
};

function RejectModal({ onClose, onConfirm, requisition, submitting }: RejectModalProps) {
  const [reason, setReason] = useState('');

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (reason.trim()) onConfirm(reason);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-xl space-y-4">
        <h2 className="text-base font-bold text-slate-950">Reject Requisition</h2>
        <p className="text-sm text-slate-600">
          Rejecting: <strong>{requisition.title}</strong> ({requisition.requisition_number})
        </p>
        <form className="space-y-3" onSubmit={handleSubmit}>
          <textarea
            className="min-h-24 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            onChange={(event) => setReason(event.target.value)}
            placeholder="Reason for rejection (required)"
            required
            value={reason}
          />
          <div className="flex gap-2 justify-end">
            <button
              className="inline-flex h-9 items-center justify-center rounded-md border border-slate-200 px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              disabled={submitting}
              onClick={onClose}
              type="button"
            >
              Cancel
            </button>
            <button
              className="inline-flex h-9 items-center justify-center rounded-md bg-red-600 px-4 text-sm font-bold text-white disabled:opacity-50"
              disabled={submitting || !reason.trim()}
              type="submit"
            >
              Reject
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

type PRRowProps = {
  requisition: PurchaseRequisitionItem;
  canManage: boolean;
  onApprove: (requisition: PurchaseRequisitionItem) => void;
  onReject: (requisition: PurchaseRequisitionItem) => void;
  submitting: boolean;
};

function PRRow({ canManage, onApprove, onReject, requisition, submitting }: PRRowProps) {
  const requiredBy = requisition.required_by_date
    ? new Date(requisition.required_by_date).toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: 'numeric' })
    : '—';

  const canAct = canManage && requisition.status === 'submitted';

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex-1 min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-xs text-slate-400">{requisition.requisition_number}</span>
            <StatusBadge status={requisition.status} />
          </div>
          <h3 className="text-base font-bold text-slate-950">{requisition.title}</h3>
          {requisition.description ? (
            <p className="text-sm text-slate-600 line-clamp-2">{requisition.description}</p>
          ) : null}
          <div className="flex flex-wrap gap-4 text-xs text-slate-500 pt-0.5">
            <span>
              Value: <span className="font-semibold text-slate-800 tabular-nums">{formatZAR(requisition.estimated_value)}</span>
            </span>
            {requisition.department ? (
              <span>Dept: <span className="text-slate-700">{requisition.department}</span></span>
            ) : null}
            <span>Required by: <span className="text-slate-700">{requiredBy}</span></span>
          </div>
          {requisition.rejection_reason ? (
            <div className="text-xs text-red-600 mt-1">
              <span className="font-semibold">Rejection reason: </span>
              {requisition.rejection_reason}
            </div>
          ) : null}
        </div>
        {canAct ? (
          <div className="flex gap-2 shrink-0">
            <button
              className="inline-flex h-8 items-center justify-center rounded-md bg-green-700 px-3 text-xs font-bold text-white disabled:opacity-50 hover:bg-green-800"
              disabled={submitting}
              onClick={() => onApprove(requisition)}
              type="button"
            >
              Approve
            </button>
            <button
              className="inline-flex h-8 items-center justify-center rounded-md border border-red-200 bg-white px-3 text-xs font-bold text-red-700 disabled:opacity-50 hover:bg-red-50"
              disabled={submitting}
              onClick={() => onReject(requisition)}
              type="button"
            >
              Reject
            </button>
          </div>
        ) : null}
      </div>
    </article>
  );
}

export default function ProcurementPage() {
  const { tokens } = useAuth();
  const token = tokens?.access ?? '';
  const [requisitions, setRequisitions] = useState<PurchaseRequisitionItem[]>([]);
  const [operatingProfile, setOperatingProfile] = useState<OperatingProfile | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [rejectTarget, setRejectTarget] = useState<PurchaseRequisitionItem | null>(null);

  const authority = operatingProfile?.primary_position?.authority_level ?? '';
  const canManage = MANAGER_AUTHORITY_LEVELS.includes(authority);

  useEffect(() => {
    if (!token) return;
    let mounted = true;
    Promise.allSettled([fetchPurchaseRequisitions(token), fetchOperatingProfile(token)])
      .then(([requisitionResult, profileResult]) => {
        if (!mounted) return;
        if (requisitionResult.status === 'fulfilled') {
          setRequisitions(requisitionResult.value.results);
        } else if (requisitionResult.reason instanceof ApiError && requisitionResult.reason.status === 403) {
          setPermissionDenied(true);
        } else {
          setError('Purchase requisitions could not be loaded.');
        }
        if (profileResult.status === 'fulfilled') setOperatingProfile(profileResult.value);
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [token]);

  const filtered = useMemo(
    () =>
      statusFilter === 'all'
        ? requisitions
        : requisitions.filter((r) => r.status === statusFilter),
    [requisitions, statusFilter],
  );

  async function handleApprove(requisition: PurchaseRequisitionItem) {
    if (!token) return;
    setSubmitting(true);
    setError('');
    try {
      const updated = await approvePurchaseRequisition(token, requisition.id);
      setRequisitions((current) => current.map((r) => (r.id === updated.id ? updated : r)));
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Approval failed.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleReject(reason: string) {
    if (!token || !rejectTarget) return;
    setSubmitting(true);
    setError('');
    try {
      const updated = await rejectPurchaseRequisition(token, rejectTarget.id, reason);
      setRequisitions((current) => current.map((r) => (r.id === updated.id ? updated : r)));
      setRejectTarget(null);
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Rejection failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="Manage purchase requisitions, track approvals and monitor procurement status."
          eyebrow="Suppliers"
          title="Procurement"
        />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? (
          <LoadingState label="Loading purchase requisitions" />
        ) : (
          <>
            <div className="flex items-center gap-3">
              <label className="text-sm font-semibold text-slate-700" htmlFor="status-filter">
                Filter by status
              </label>
              <select
                className="h-9 rounded-md border border-slate-200 px-3 text-sm"
                id="status-filter"
                onChange={(event) => setStatusFilter(event.target.value)}
                value={statusFilter}
              >
                <option value="all">All statuses</option>
                {ALL_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {status.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </div>
            <section className="space-y-3">
              {filtered.length ? (
                filtered.map((requisition) => (
                  <PRRow
                    canManage={canManage}
                    key={requisition.id}
                    onApprove={handleApprove}
                    onReject={setRejectTarget}
                    requisition={requisition}
                    submitting={submitting}
                  />
                ))
              ) : (
                <EmptyState
                  description="No purchase requisitions match the current filter."
                  title="No requisitions found"
                />
              )}
            </section>
          </>
        )}
      </div>
      {rejectTarget ? (
        <RejectModal
          onClose={() => setRejectTarget(null)}
          onConfirm={handleReject}
          requisition={rejectTarget}
          submitting={submitting}
        />
      ) : null}
    </AppShell>
  );
}

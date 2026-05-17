'use client';

import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { ArrowRight, CheckCircle2, Clock3, FilePlus2, PauseCircle, XCircle } from 'lucide-react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DepartmentExecutiveActionsPanel } from '@/components/governance/department-executive-actions-panel';
import { PageHeader } from '@/components/ui/page-header';
import { ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { ApiError } from '@/lib/api/client';
import {
  convertIntakeRequestToWorkspace,
  createIntakeRequest,
  fetchIntakeRequests,
  fetchSites,
  fetchUsers,
  setIntakeRequestAction,
} from '@/lib/api/endpoints';
import type { IntakeRequestItem, SiteListItem, UserListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

const requestTypes = [
  ['venue_booking', 'Venue Booking Request'],
  ['production_proposal', 'Production Proposal'],
  ['co_production_proposal', 'Co-Production Proposal'],
  ['youth_programme_proposal', 'Youth Programme Proposal'],
  ['festival_request', 'Festival Request'],
  ['workshop_series_request', 'Workshop Series Request'],
  ['training_programme_request', 'Training Programme Request'],
  ['civic_event_request', 'Civic Event Request'],
  ['governance_item_request', 'Governance Item Request'],
  ['internal_programming_request', 'Internal Programming Request'],
] as const;

const statusTone: Record<string, 'neutral' | 'info' | 'good' | 'warning' | 'danger'> = {
  submitted: 'info',
  under_review: 'warning',
  changes_requested: 'warning',
  deferred: 'neutral',
  approved: 'good',
  declined: 'danger',
  converted: 'good',
  archived: 'neutral',
};

function labelFromValue(value: string) {
  return value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

type FormState = {
  request_type: string;
  event_title: string;
  client_name: string;
  client_organisation: string;
  contact_email: string;
  requested_start_date: string;
  expected_audience: string;
  ticketing_required: boolean;
  technical_summary: string;
  foh_notes: string;
  accessibility_requirements: string;
  notes: string;
};

const emptyForm: FormState = {
  request_type: 'venue_booking',
  event_title: '',
  client_name: '',
  client_organisation: '',
  contact_email: '',
  requested_start_date: '',
  expected_audience: '',
  ticketing_required: false,
  technical_summary: '',
  foh_notes: '',
  accessibility_requirements: '',
  notes: '',
};

export default function ProgrammingPage() {
  const { tokens } = useAuth();
  const [requests, setRequests] = useState<IntakeRequestItem[]>([]);
  const [sites, setSites] = useState<SiteListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [comment, setComment] = useState('');
  const [selectedSite, setSelectedSite] = useState('');
  const [selectedOwner, setSelectedOwner] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([
      fetchIntakeRequests(tokens.access),
      fetchSites(tokens.access),
      fetchUsers(tokens.access),
    ])
      .then(([requestResult, siteResult, userResult]) => {
        if (!mounted) return;
        if (requestResult.status === 'fulfilled') setRequests(requestResult.value.results);
        else if (requestResult.reason instanceof ApiError && requestResult.reason.status === 403) setPermissionDenied(true);
        else setError('Private intake requests could not be loaded.');
        if (siteResult.status === 'fulfilled') setSites(siteResult.value.results);
        if (userResult.status === 'fulfilled') {
          setUsers(userResult.value.results);
          setSelectedOwner(userResult.value.results[0]?.id ?? '');
        }
        if (siteResult.status === 'fulfilled') setSelectedSite(siteResult.value.results[0]?.id ?? '');
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access]);

  const counts = useMemo(() => ({
    submitted: requests.filter((item) => item.status === 'submitted').length,
    review: requests.filter((item) => item.status === 'under_review').length,
    approved: requests.filter((item) => item.status === 'approved').length,
    converted: requests.filter((item) => item.status === 'converted').length,
  }), [requests]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setError('');
    try {
      const created = await createIntakeRequest(tokens.access, {
        ...form,
        requested_start_date: form.requested_start_date || null,
        expected_audience: form.expected_audience ? Number(form.expected_audience) : null,
      });
      setRequests((current) => [created, ...current]);
      setForm(emptyForm);
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Intake request could not be created.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAction(item: IntakeRequestItem, action: 'start-review' | 'approve' | 'decline' | 'defer' | 'request-changes') {
    if (!tokens?.access) return;
    setSubmitting(true);
    setError('');
    try {
      const updated = await setIntakeRequestAction(tokens.access, item.id, action, comment);
      setRequests((current) => current.map((request) => (request.id === updated.id ? updated : request)));
      setComment('');
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Intake request action failed.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleConvert(item: IntakeRequestItem) {
    if (!tokens?.access || !selectedOwner) return;
    setSubmitting(true);
    setError('');
    try {
      const result = await convertIntakeRequestToWorkspace(tokens.access, item.id, {
        site: selectedSite || undefined,
        owner: selectedOwner,
        priority: 'medium',
        risk_level: 'low',
      });
      setRequests((current) => current.map((request) => (
        request.id === item.id ? { ...request, status: 'converted', converted_context: result.workspace_id } : request
      )));
    } catch (err) {
      setError(err instanceof ApiError ? JSON.stringify(err.payload ?? { detail: err.message }) : 'Workspace conversion failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="Review private requests before approved work becomes a Workspace."
          eyebrow="Programming"
          title="Private Intake"
        />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        <DepartmentExecutiveActionsPanel departmentTypes={['programming']} targetTypes={['IntakeRequest', 'IntakeReview', 'VenueHold', 'ProducerAssignment']} />
        {loading ? <LoadingState label="Loading private intake" /> : (
          <>
            <section className="grid gap-4 md:grid-cols-4">
              <Metric icon={FilePlus2} label="Submitted" value={counts.submitted} />
              <Metric icon={Clock3} label="Under review" value={counts.review} />
              <Metric icon={CheckCircle2} label="Approved" value={counts.approved} />
              <Metric icon={ArrowRight} label="Converted" value={counts.converted} />
            </section>

            <section className="grid gap-5 xl:grid-cols-[0.9fr_1.4fr]">
              <form className="space-y-3 rounded-lg border border-slate-200 bg-white p-4" onSubmit={handleCreate}>
                <h2 className="text-base font-bold text-slate-950">New Intake Request</h2>
                <select className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setForm({ ...form, request_type: event.target.value })} value={form.request_type}>
                  {requestTypes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
                <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setForm({ ...form, event_title: event.target.value })} placeholder="Event title" required value={form.event_title} />
                <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setForm({ ...form, client_name: event.target.value })} placeholder="Client name" required value={form.client_name} />
                <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setForm({ ...form, client_organisation: event.target.value })} placeholder="Organisation or company" value={form.client_organisation} />
                <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setForm({ ...form, contact_email: event.target.value })} placeholder="Contact email" type="email" value={form.contact_email} />
                <div className="grid gap-3 md:grid-cols-2">
                  <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setForm({ ...form, requested_start_date: event.target.value })} type="date" value={form.requested_start_date} />
                  <input className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm" min="0" onChange={(event) => setForm({ ...form, expected_audience: event.target.value })} placeholder="Expected audience" type="number" value={form.expected_audience} />
                </div>
                <label className="flex items-center gap-2 text-sm font-semibold text-slate-700">
                  <input checked={form.ticketing_required} onChange={(event) => setForm({ ...form, ticketing_required: event.target.checked })} type="checkbox" />
                  Ticketing required
                </label>
                <textarea className="min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" onChange={(event) => setForm({ ...form, technical_summary: event.target.value })} placeholder="Technical summary" value={form.technical_summary} />
                <textarea className="min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" onChange={(event) => setForm({ ...form, foh_notes: event.target.value })} placeholder="FOH / hospitality notes" value={form.foh_notes} />
                <textarea className="min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" onChange={(event) => setForm({ ...form, accessibility_requirements: event.target.value })} placeholder="Accessibility requirements" value={form.accessibility_requirements} />
                <textarea className="min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm" onChange={(event) => setForm({ ...form, notes: event.target.value })} placeholder="Notes" value={form.notes} />
                <button className="inline-flex h-10 items-center justify-center rounded-md bg-blue-700 px-4 text-sm font-bold text-white disabled:opacity-50" disabled={submitting} type="submit">
                  Create Request
                </button>
              </form>

              <section className="space-y-3">
                <div className="grid gap-3 md:grid-cols-3">
                  <input className="h-10 rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setComment(event.target.value)} placeholder="Decision comment" value={comment} />
                  <select className="h-10 rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setSelectedSite(event.target.value)} value={selectedSite}>
                    <option value="">Select conversion site</option>
                    {sites.map((site) => <option key={site.id} value={site.id}>{site.name}</option>)}
                  </select>
                  <select className="h-10 rounded-md border border-slate-200 px-3 text-sm" onChange={(event) => setSelectedOwner(event.target.value)} value={selectedOwner}>
                    <option value="">Select Workspace owner</option>
                    {users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}
                  </select>
                </div>
                {requests.length ? requests.map((item) => (
                  <article className="rounded-lg border border-slate-200 bg-white p-4" key={item.id}>
                    <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <h2 className="text-base font-bold text-slate-950">{item.event_title}</h2>
                          <StatusBadge tone={statusTone[item.status] ?? 'neutral'}>{labelFromValue(item.status)}</StatusBadge>
                        </div>
                        <p className="mt-1 text-sm text-slate-600">{labelFromValue(item.request_type)} · {item.client_name}</p>
                        <p className="mt-2 text-sm leading-6 text-slate-500">{item.notes || item.technical_summary || 'No notes captured.'}</p>
                        {item.decision_comment ? <p className="mt-2 text-xs font-semibold text-slate-500">Decision: {item.decision_comment}</p> : null}
                      </div>
                      <div className="flex flex-wrap gap-2 md:justify-end">
                        <ActionButton disabled={submitting || item.status === 'converted'} icon={Clock3} label="Review" onClick={() => handleAction(item, 'start-review')} />
                        <ActionButton disabled={submitting || item.status === 'converted'} icon={CheckCircle2} label="Approve" onClick={() => handleAction(item, 'approve')} />
                        <ActionButton disabled={submitting || item.status === 'converted'} icon={PauseCircle} label="Defer" onClick={() => handleAction(item, 'defer')} />
                        <ActionButton disabled={submitting || item.status === 'converted'} icon={XCircle} label="Changes" onClick={() => handleAction(item, 'request-changes')} />
                        <ActionButton disabled={submitting || item.status !== 'approved' || !selectedOwner} icon={ArrowRight} label="Workspace" onClick={() => handleConvert(item)} />
                      </div>
                    </div>
                  </article>
                )) : (
                  <div className="rounded-lg border border-dashed border-slate-300 bg-white px-4 py-10 text-center text-sm text-slate-500">
                    No private intake requests returned for your role.
                  </div>
                )}
              </section>
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}

function Metric({ icon: Icon, label, value }: { icon: typeof FilePlus2; label: string; value: number }) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <Icon className="h-5 w-5 text-blue-700" />
      <div className="mt-3 text-2xl font-bold text-slate-950">{value}</div>
      <div className="text-sm font-semibold text-slate-500">{label}</div>
    </article>
  );
}

function ActionButton({
  disabled,
  icon: Icon,
  label,
  onClick,
}: {
  disabled: boolean;
  icon: typeof FilePlus2;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      className="inline-flex h-9 items-center gap-1 rounded-md border border-slate-200 bg-white px-3 text-xs font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-40"
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      <Icon className="h-3.5 w-3.5" />
      {label}
    </button>
  );
}

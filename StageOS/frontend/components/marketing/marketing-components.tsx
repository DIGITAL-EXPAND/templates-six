'use client';

import { FormEvent, useState } from 'react';
import { X } from 'lucide-react';
import { BlockerAlert, labelFromValue, money, ReadinessBadge, RestrictedField } from '@/components/readiness/shared';
import type { CampaignDeliverableItem, CampaignItem, DocumentItem, OperatingContextListItem, UserListItem } from '@/lib/api/types';

export type MarketingAction =
  | { kind: 'launch' | 'pause' | 'close'; campaign: CampaignItem }
  | { kind: 'complete'; deliverable: CampaignDeliverableItem };

export function isDeliverableOverdue(deliverable: CampaignDeliverableItem, now: number) {
  return Boolean(deliverable.due_date && deliverable.status !== 'complete' && new Date(deliverable.due_date).getTime() < now);
}

export function campaignDeliverables(deliverables: CampaignDeliverableItem[], campaignId: string) {
  return deliverables.filter((deliverable) => deliverable.campaign === campaignId);
}

function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  return workspaces.find((workspace) => workspace.id === id)?.title ?? 'Workspace unavailable';
}

function userName(users: UserListItem[], id: string) {
  return users.find((user) => user.id === id)?.full_name ?? 'Owner unavailable';
}

function documentTitle(documents: DocumentItem[], id: string | null) {
  if (!id) return 'Evidence missing';
  return documents.find((document) => document.id === id)?.title ?? 'Document unavailable';
}

export function CampaignFilters({
  levels,
  types,
  value,
  workspaces,
  onChange,
}: {
  levels: string[];
  types: string[];
  value: { status: string; level: string; workspace: string; type: string; overdue: boolean; missingEvidence: boolean };
  workspaces: OperatingContextListItem[];
  onChange: (value: { status: string; level: string; workspace: string; type: string; overdue: boolean; missingEvidence: boolean }) => void;
}) {
  return (
    <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 md:grid-cols-3 xl:grid-cols-6">
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, status: event.target.value })} value={value.status}>
        <option value="all">All statuses</option><option value="planning">Planning</option><option value="active">Active</option><option value="paused">Paused</option><option value="closed">Closed</option>
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, level: event.target.value })} value={value.level}>
        <option value="all">All levels</option>{levels.map((level) => <option key={level} value={level}>{labelFromValue(level)}</option>)}
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, workspace: event.target.value })} value={value.workspace}>
        <option value="all">All Workspaces</option>{workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.title}</option>)}
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, type: event.target.value })} value={value.type}>
        <option value="all">All deliverables</option>{types.map((type) => <option key={type} value={type}>{labelFromValue(type)}</option>)}
      </select>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.overdue} onChange={(event) => onChange({ ...value, overdue: event.target.checked })} type="checkbox" />Overdue</label>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.missingEvidence} onChange={(event) => onChange({ ...value, missingEvidence: event.target.checked })} type="checkbox" />Evidence missing</label>
    </section>
  );
}

export function CampaignList(props: {
  campaigns: CampaignItem[];
  deliverables: CampaignDeliverableItem[];
  documents: DocumentItem[];
  now: number;
  users: UserListItem[];
  workspaces: OperatingContextListItem[];
  onAction: (action: MarketingAction) => void;
}) {
  return <div className="grid gap-4 xl:grid-cols-2">{props.campaigns.map((campaign) => <CampaignCard {...props} campaign={campaign} key={campaign.id} />)}</div>;
}

function CampaignCard({ campaign, deliverables, documents, now, users, workspaces, onAction }: {
  campaign: CampaignItem; deliverables: CampaignDeliverableItem[]; documents: DocumentItem[]; now: number; users: UserListItem[]; workspaces: OperatingContextListItem[]; onAction: (action: MarketingAction) => void;
}) {
  const items = campaignDeliverables(deliverables, campaign.id);
  const blockers = [
    ...items.filter((item) => isDeliverableOverdue(item, now)).map((item) => `${item.title} is overdue.`),
    ...items.filter((item) => !item.evidence_document && item.status === 'complete').map((item) => `${item.title} has no evidence linked.`),
  ];
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between"><div><h2 className="text-base font-bold text-slate-950">{workspaceName(workspaces, campaign.operating_context)}</h2><p className="mt-1 text-sm text-slate-500">{labelFromValue(campaign.campaign_level)} · Owner: {userName(users, campaign.owner)}</p></div><ReadinessBadge value={campaign.status} /></div>
      <dl className="mt-4 grid gap-3 text-sm md:grid-cols-3"><div><dt className="font-bold text-slate-700">Budget</dt><dd className="mt-1 text-slate-600">{money(campaign.budget)}</dd></div><div><dt className="font-bold text-slate-700">Deliverables</dt><dd className="mt-1 text-slate-600">{items.filter((item) => item.status === 'complete').length}/{items.length}</dd></div><div><dt className="font-bold text-slate-700">Evidence gaps</dt><dd className="mt-1 text-slate-600">{items.filter((item) => !item.evidence_document).length}</dd></div></dl>
      <div className="mt-4"><BlockerAlert blockers={blockers} /></div>
      <CampaignDeliverableList deliverables={items} documents={documents} now={now} onAction={onAction} />
      <div className="mt-4 flex flex-wrap gap-2"><button className="h-9 rounded-md bg-blue-600 px-3 text-sm font-bold text-white" onClick={() => onAction({ kind: 'launch', campaign })} type="button">Launch</button><button className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700" onClick={() => onAction({ kind: 'pause', campaign })} type="button">Pause</button><button className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700" onClick={() => onAction({ kind: 'close', campaign })} type="button">Close</button></div>
    </article>
  );
}

export function CampaignDeliverableList({ deliverables, documents, now, onAction }: { deliverables: CampaignDeliverableItem[]; documents: DocumentItem[]; now: number; onAction: (action: MarketingAction) => void }) {
  return <div className="mt-4 divide-y divide-slate-100 rounded-md border border-slate-200">{deliverables.length ? deliverables.map((item) => <div className="flex flex-col gap-3 p-3 md:flex-row md:items-center md:justify-between" key={item.id}><div><div className="text-sm font-bold text-slate-900">{item.title}</div><div className="mt-1 text-xs text-slate-500">{labelFromValue(item.deliverable_type)} · Due {item.due_date ?? 'not set'} · {documentTitle(documents, item.evidence_document)}</div>{isDeliverableOverdue(item, now) ? <div className="mt-1 text-xs font-bold text-rose-700">Overdue</div> : null}</div><div className="flex flex-wrap items-center gap-2"><ReadinessBadge value={item.status} /><button className="h-8 rounded-md border border-slate-200 px-2 text-xs font-bold text-slate-700" onClick={() => onAction({ kind: 'complete', deliverable: item })} type="button">Complete</button></div></div>) : <div className="p-3 text-sm text-slate-500">No deliverables returned.</div>}</div>;
}

export function DeliverableActionDialog({ action, documents, submitting, onClose, onSubmit }: { action: MarketingAction | null; documents: DocumentItem[]; submitting: boolean; onClose: () => void; onSubmit: (values: { comment: string; evidence: string }) => void }) {
  const [comment, setComment] = useState('');
  const [evidence, setEvidence] = useState('');
  if (!action) return null;
  const title = action.kind === 'complete' ? 'Complete deliverable' : `${labelFromValue(action.kind)} campaign`;
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); onSubmit({ comment, evidence }); }
  return <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-md overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-semibold text-blue-700">Marketing action</p><h2 className="mt-1 text-xl font-bold text-slate-950">{title}</h2></div><button aria-label="Close marketing action" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700" onClick={onClose} type="button"><X className="h-4 w-4" /></button></div><form className="mt-5 space-y-4" onSubmit={submit}>{action.kind === 'complete' ? <div><label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="marketing-evidence">Evidence document</label><select className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950" id="marketing-evidence" onChange={(event) => setEvidence(event.target.value)} value={evidence}><option value="">No evidence selected</option>{documents.map((document) => <option key={document.id} value={document.id}>{document.title}</option>)}</select></div> : null}<div><label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="marketing-comment">Comment</label><textarea className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950" id="marketing-comment" onChange={(event) => setComment(event.target.value)} value={comment} /></div><button className="h-10 w-full rounded-md bg-blue-600 px-4 text-sm font-bold text-white disabled:bg-slate-400" disabled={submitting} type="submit">{submitting ? 'Submitting' : title}</button></form></aside>;
}


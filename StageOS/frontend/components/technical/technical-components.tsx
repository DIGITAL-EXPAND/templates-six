'use client';

import { FormEvent, useState } from 'react';
import { X } from 'lucide-react';
import { BlockerAlert, labelFromValue, ReadinessBadge } from '@/components/readiness/shared';
import type { CrewRequirementItem, EquipmentRequirementItem, OperatingContextListItem, TechnicalRiderItem, UserListItem } from '@/lib/api/types';

export type TechnicalAction = { kind: 'submit' | 'approve' | 'reject' | 'request-revision'; rider: TechnicalRiderItem };

function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  return workspaces.find((workspace) => workspace.id === id)?.title ?? 'Workspace unavailable';
}

function userName(users: UserListItem[], id: string | null) {
  if (!id) return 'Not approved';
  return users.find((user) => user.id === id)?.full_name ?? 'User unavailable';
}

export function riderCrew(crew: CrewRequirementItem[], riderId: string) {
  return crew.filter((item) => item.rider === riderId);
}

export function riderEquipment(equipment: EquipmentRequirementItem[], riderId: string) {
  return equipment.filter((item) => item.rider === riderId);
}

export function technicalBlockers(rider: TechnicalRiderItem, crew: CrewRequirementItem[], equipment: EquipmentRequirementItem[]) {
  const blockers: string[] = [];
  if (rider.status !== 'approved') blockers.push('Technical rider is not approved.');
  if (!rider.lighting && !rider.sound && !rider.av) blockers.push('Core technical requirements are incomplete.');
  if (!crew.length && rider.crew_size > 0) blockers.push('Crew requirements have not been detailed.');
  if (!equipment.length) blockers.push('Equipment requirements have not been captured.');
  return blockers;
}

export function TechnicalFilters({ value, workspaces, sources, onChange }: { value: { status: string; workspace: string; source: string; pending: boolean; missing: boolean }; workspaces: OperatingContextListItem[]; sources: string[]; onChange: (value: { status: string; workspace: string; source: string; pending: boolean; missing: boolean }) => void }) {
  return <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 md:grid-cols-3 xl:grid-cols-5"><select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, status: event.target.value })} value={value.status}><option value="all">All statuses</option><option value="draft">Draft</option><option value="submitted">Submitted</option><option value="under_review">Under review</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select><select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, workspace: event.target.value })} value={value.workspace}><option value="all">All Workspaces</option>{workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.title}</option>)}</select><select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, source: event.target.value })} value={value.source}><option value="all">All equipment sources</option>{sources.map((source) => <option key={source} value={source}>{labelFromValue(source)}</option>)}</select><label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.pending} onChange={(event) => onChange({ ...value, pending: event.target.checked })} type="checkbox" />Pending approval</label><label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.missing} onChange={(event) => onChange({ ...value, missing: event.target.checked })} type="checkbox" />Gaps</label></section>;
}

export function TechnicalRiderList(props: { riders: TechnicalRiderItem[]; crew: CrewRequirementItem[]; equipment: EquipmentRequirementItem[]; users: UserListItem[]; workspaces: OperatingContextListItem[]; onAction: (action: TechnicalAction) => void }) {
  return <div className="grid gap-4 xl:grid-cols-2">{props.riders.map((rider) => <TechnicalRiderCard {...props} key={rider.id} rider={rider} />)}</div>;
}

function TechnicalRiderCard({ rider, crew, equipment, users, workspaces, onAction }: { rider: TechnicalRiderItem; crew: CrewRequirementItem[]; equipment: EquipmentRequirementItem[]; users: UserListItem[]; workspaces: OperatingContextListItem[]; onAction: (action: TechnicalAction) => void }) {
  const riderCrewItems = riderCrew(crew, rider.id);
  const riderEquipmentItems = riderEquipment(equipment, rider.id);
  return <article className="rounded-lg border border-slate-200 bg-white p-4"><div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between"><div><h2 className="text-base font-bold text-slate-950">{workspaceName(workspaces, rider.operating_context)}</h2><p className="mt-1 text-sm text-slate-500">Load-in {rider.load_in_date ?? 'not set'} · Strike {rider.strike_date ?? 'not set'}</p></div><ReadinessBadge value={rider.status} /></div><dl className="mt-4 grid gap-3 text-sm md:grid-cols-3"><div><dt className="font-bold text-slate-700">Crew size</dt><dd className="mt-1 text-slate-600">{rider.crew_size}</dd></div><div><dt className="font-bold text-slate-700">Equipment</dt><dd className="mt-1 text-slate-600">{riderEquipmentItems.length}</dd></div><div><dt className="font-bold text-slate-700">Approved by</dt><dd className="mt-1 text-slate-600">{userName(users, rider.approved_by)}</dd></div></dl><div className="mt-4"><BlockerAlert blockers={technicalBlockers(rider, riderCrewItems, riderEquipmentItems)} /></div><RequirementList title="Crew requirements" items={riderCrewItems.map((item) => `${item.quantity}x ${item.role}`)} /><RequirementList title="Equipment requirements" items={riderEquipmentItems.map((item) => `${item.quantity}x ${item.item} (${labelFromValue(item.source)})`)} /><div className="mt-4 grid gap-2 sm:grid-cols-4"><button className="h-9 rounded-md bg-blue-600 px-3 text-sm font-bold text-white" onClick={() => onAction({ kind: 'submit', rider })} type="button">Submit</button><button className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700" onClick={() => onAction({ kind: 'approve', rider })} type="button">Approve</button><button className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700" onClick={() => onAction({ kind: 'request-revision', rider })} type="button">Request revision</button><button className="h-9 rounded-md border border-rose-200 px-3 text-sm font-bold text-rose-700" onClick={() => onAction({ kind: 'reject', rider })} type="button">Reject</button></div></article>;
}

function RequirementList({ title, items }: { title: string; items: string[] }) {
  return <div className="mt-4 rounded-md border border-slate-200 p-3"><h3 className="text-sm font-bold text-slate-900">{title}</h3>{items.length ? <ul className="mt-2 space-y-1 text-sm text-slate-600">{items.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="mt-2 text-sm text-slate-500">No requirements returned.</p>}</div>;
}

export function TechnicalActionDialog({ action, submitting, onClose, onSubmit }: { action: TechnicalAction | null; submitting: boolean; onClose: () => void; onSubmit: (comment: string) => void }) {
  const [comment, setComment] = useState('');
  if (!action) return null;
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); onSubmit(comment); }
  return <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-md overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-semibold text-blue-700">Technical action</p><h2 className="mt-1 text-xl font-bold text-slate-950">{labelFromValue(action.kind)}</h2></div><button aria-label="Close technical action" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700" onClick={onClose} type="button"><X className="h-4 w-4" /></button></div><form className="mt-5 space-y-4" onSubmit={submit}><div><label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="technical-comment">Comment</label><textarea className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950" id="technical-comment" onChange={(event) => setComment(event.target.value)} value={comment} /></div><button className="h-10 w-full rounded-md bg-blue-600 px-4 text-sm font-bold text-white disabled:bg-slate-400" disabled={submitting} type="submit">{submitting ? 'Submitting' : labelFromValue(action.kind)}</button></form></aside>;
}


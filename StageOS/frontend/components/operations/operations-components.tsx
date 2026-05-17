'use client';

import { FormEvent, useState } from 'react';
import { X } from 'lucide-react';
import { BlockerAlert, labelFromValue, ReadinessBadge } from '@/components/readiness/shared';
import type { ChecklistItem, FohPlanItem, IncidentItem, OperatingContextListItem } from '@/lib/api/types';

export type FohAction =
  | { kind: 'confirm' | 'close'; plan: FohPlanItem }
  | { kind: 'check'; item: ChecklistItem }
  | { kind: 'incident'; plan: FohPlanItem };

function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  return workspaces.find((workspace) => workspace.id === id)?.title ?? 'Workspace unavailable';
}

export function planChecklist(items: ChecklistItem[], planId: string) {
  return items.filter((item) => item.foh_plan === planId);
}

export function planIncidents(incidents: IncidentItem[], plan: FohPlanItem) {
  return incidents.filter((incident) => incident.foh_plan === plan.id || incident.operating_context === plan.operating_context);
}

export function fohBlockers(plan: FohPlanItem, checklist: ChecklistItem[], incidents: IncidentItem[]) {
  const blockers: string[] = [];
  if (plan.status !== 'confirmed' && plan.status !== 'closed') blockers.push('FOH plan is not confirmed.');
  if (checklist.some((item) => !item.is_checked)) blockers.push('Show-day checklist is incomplete.');
  if (incidents.some((incident) => incident.severity === 'high' || incident.severity === 'critical')) blockers.push('High or critical incidents are logged.');
  if (!plan.accessibility_provisions) blockers.push('Accessibility provisions are not captured.');
  return blockers;
}

export function FohFilters({ value, workspaces, onChange }: { value: { status: string; workspace: string; incomplete: boolean; incidents: boolean; accessibility: boolean }; workspaces: OperatingContextListItem[]; onChange: (value: { status: string; workspace: string; incomplete: boolean; incidents: boolean; accessibility: boolean }) => void }) {
  return <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 md:grid-cols-3 xl:grid-cols-5"><select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, status: event.target.value })} value={value.status}><option value="all">All statuses</option><option value="planning">Planning</option><option value="confirmed">Confirmed</option><option value="active">Active</option><option value="closed">Closed</option></select><select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, workspace: event.target.value })} value={value.workspace}><option value="all">All Workspaces</option>{workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.title}</option>)}</select><label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.incomplete} onChange={(event) => onChange({ ...value, incomplete: event.target.checked })} type="checkbox" />Checklist incomplete</label><label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.incidents} onChange={(event) => onChange({ ...value, incidents: event.target.checked })} type="checkbox" />Incidents</label><label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.accessibility} onChange={(event) => onChange({ ...value, accessibility: event.target.checked })} type="checkbox" />Accessibility issue</label></section>;
}

export function FOHPlanList(props: { plans: FohPlanItem[]; checklists: ChecklistItem[]; incidents: IncidentItem[]; workspaces: OperatingContextListItem[]; onAction: (action: FohAction) => void }) {
  return <div className="grid gap-4 xl:grid-cols-2">{props.plans.map((plan) => <FOHPlanCard {...props} key={plan.id} plan={plan} />)}</div>;
}

function FOHPlanCard({ plan, checklists, incidents, workspaces, onAction }: { plan: FohPlanItem; checklists: ChecklistItem[]; incidents: IncidentItem[]; workspaces: OperatingContextListItem[]; onAction: (action: FohAction) => void }) {
  const items = planChecklist(checklists, plan.id);
  const planIncidentItems = planIncidents(incidents, plan);
  return <article className="rounded-lg border border-slate-200 bg-white p-4"><div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between"><div><h2 className="text-base font-bold text-slate-950">{workspaceName(workspaces, plan.operating_context)}</h2><p className="mt-1 text-sm text-slate-500">Ushers {plan.ushers} · Security {plan.security} · Cleaning {plan.cleaning} · VIP {plan.vip_count}</p></div><ReadinessBadge value={plan.status} /></div><div className="mt-4"><BlockerAlert blockers={fohBlockers(plan, items, planIncidentItems)} /></div><section className="mt-4 rounded-md border border-slate-200 p-3"><h3 className="text-sm font-bold text-slate-900">Show-day checklist</h3>{items.length ? <div className="mt-2 divide-y divide-slate-100">{items.map((item) => <div className="flex items-center justify-between gap-3 py-2" key={item.id}><span className="text-sm text-slate-700">{item.item}</span><button className="h-8 rounded-md border border-slate-200 px-2 text-xs font-bold text-slate-700 disabled:text-slate-400" disabled={item.is_checked} onClick={() => onAction({ kind: 'check', item })} type="button">{item.is_checked ? 'Checked' : 'Check'}</button></div>)}</div> : <p className="mt-2 text-sm text-slate-500">No checklist items returned.</p>}</section><section className="mt-4 rounded-md border border-slate-200 p-3"><h3 className="text-sm font-bold text-slate-900">Incidents</h3>{planIncidentItems.length ? <div className="mt-2 space-y-2">{planIncidentItems.slice(0, 3).map((incident) => <div className="rounded-md bg-slate-50 p-2" key={incident.id}><div className="text-sm font-bold text-slate-900">{labelFromValue(incident.incident_type)}</div><div className="mt-1 text-xs text-slate-500">{labelFromValue(incident.severity)} · {new Date(incident.occurred_at).toLocaleDateString()}</div></div>)}</div> : <p className="mt-2 text-sm text-slate-500">No incidents returned.</p>}</section><div className="mt-4 flex flex-wrap gap-2"><button className="h-9 rounded-md bg-blue-600 px-3 text-sm font-bold text-white" onClick={() => onAction({ kind: 'confirm', plan })} type="button">Confirm plan</button><button className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700" onClick={() => onAction({ kind: 'close', plan })} type="button">Close plan</button><button className="h-9 rounded-md border border-rose-200 px-3 text-sm font-bold text-rose-700" onClick={() => onAction({ kind: 'incident', plan })} type="button">Log incident</button></div></article>;
}

export function IncidentActionDialog({ action, submitting, onClose, onSubmit }: { action: FohAction | null; submitting: boolean; onClose: () => void; onSubmit: (values: { comment: string; incidentType: string; severity: string; description: string }) => void }) {
  const [comment, setComment] = useState('');
  const [incidentType, setIncidentType] = useState('other');
  const [severity, setSeverity] = useState('medium');
  const [description, setDescription] = useState('');
  if (!action) return null;
  const isIncident = action.kind === 'incident';
  const title = isIncident ? 'Log incident' : action.kind === 'check' ? 'Check checklist item' : `${labelFromValue(action.kind)} FOH plan`;
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); onSubmit({ comment, incidentType, severity, description }); }
  return <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-md overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-semibold text-blue-700">FOH / Operations action</p><h2 className="mt-1 text-xl font-bold text-slate-950">{title}</h2></div><button aria-label="Close FOH action" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700" onClick={onClose} type="button"><X className="h-4 w-4" /></button></div><form className="mt-5 space-y-4" onSubmit={submit}>{isIncident ? <><div><label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="incident-type">Incident type</label><select className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950" id="incident-type" onChange={(event) => setIncidentType(event.target.value)} value={incidentType}><option value="patron_complaint">Patron complaint</option><option value="accessibility_issue">Accessibility issue</option><option value="safety_incident">Safety incident</option><option value="equipment_failure">Equipment failure</option><option value="security_breach">Security breach</option><option value="other">Other</option></select></div><div><label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="incident-severity">Severity</label><select className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950" id="incident-severity" onChange={(event) => setSeverity(event.target.value)} value={severity}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select></div><div><label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="incident-description">Description</label><textarea className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950" id="incident-description" onChange={(event) => setDescription(event.target.value)} value={description} /></div></> : null}<div><label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="foh-comment">Comment</label><textarea className="min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950" id="foh-comment" onChange={(event) => setComment(event.target.value)} value={comment} /></div><button className="h-10 w-full rounded-md bg-blue-600 px-4 text-sm font-bold text-white disabled:bg-slate-400" disabled={submitting} type="submit">{submitting ? 'Submitting' : title}</button></form></aside>;
}


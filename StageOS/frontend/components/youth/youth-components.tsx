'use client';

import { FormEvent, useMemo, useState } from 'react';
import { X } from 'lucide-react';
import { BlockerAlert, labelFromValue, ReadinessBadge, RestrictedField } from '@/components/readiness/shared';
import type {
  AttendanceRecordItem,
  ConsentRecordItem,
  FacilitatorAssignmentItem,
  LearnerGroupItem,
  OperatingContextListItem,
  ShowcaseOutputItem,
  UserListItem,
  YouthActivityItem,
  YouthAssessmentItem,
  YouthProjectItem,
  YouthSessionItem,
} from '@/lib/api/types';

export type YouthAction =
  | { kind: 'activate' | 'complete'; project: YouthProjectItem }
  | { kind: 'complete-session'; session: YouthSessionItem }
  | { kind: 'receive-consent' | 'withdraw-consent'; consent: ConsentRecordItem }
  | { kind: 'vet-facilitator'; facilitator: FacilitatorAssignmentItem };

export function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  return workspaces.find((workspace) => workspace.id === id)?.title ?? 'Workspace unavailable';
}

export function youthActivities(activities: YouthActivityItem[], projectId: string) {
  return activities.filter((activity) => activity.youth_project === projectId);
}

export function youthSessions(sessions: YouthSessionItem[], activities: YouthActivityItem[]) {
  const activityIds = new Set(activities.map((activity) => activity.id));
  return sessions.filter((session) => activityIds.has(session.activity));
}

export function youthFacilitators(facilitators: FacilitatorAssignmentItem[], projectId: string) {
  return facilitators.filter((facilitator) => facilitator.youth_project === projectId);
}

export function youthConsent(consent: ConsentRecordItem[], projectId: string) {
  return consent.filter((record) => record.youth_project === projectId);
}

export function youthAssessments(assessments: YouthAssessmentItem[], projectId: string) {
  return assessments.filter((assessment) => assessment.youth_project === projectId);
}

export function youthShowcases(showcases: ShowcaseOutputItem[], projectId: string) {
  return showcases.filter((showcase) => showcase.youth_project === projectId);
}

export function youthBlockers(
  project: YouthProjectItem,
  sessions: YouthSessionItem[],
  consent: ConsentRecordItem[],
  facilitators: FacilitatorAssignmentItem[],
) {
  const blockers: string[] = [];
  if (!['active', 'completed'].includes(project.status)) blockers.push('Youth Project is not active yet.');
  if (consent.some((record) => !record.guardian_consent_received)) blockers.push('Consent is incomplete.');
  if (sessions.some((session) => !session.attendance_captured && session.status === 'completed')) blockers.push('Attendance is pending for completed sessions.');
  if (facilitators.some((facilitator) => !facilitator.is_vetted)) blockers.push('Facilitator vetting is pending.');
  return blockers;
}

export function YouthProjectFilters({
  value,
  workspaces,
  onChange,
}: {
  value: { status: string; workspace: string; active: boolean; completed: boolean; consent: boolean; attendance: boolean; vetting: boolean; search: string };
  workspaces: OperatingContextListItem[];
  onChange: (value: { status: string; workspace: string; active: boolean; completed: boolean; consent: boolean; attendance: boolean; vetting: boolean; search: string }) => void;
}) {
  return (
    <section className="grid gap-2 rounded-lg border border-slate-200 bg-white p-3 md:grid-cols-3 xl:grid-cols-7">
      <input aria-label="Search Youth Projects" className="h-10 rounded-md border border-slate-200 px-3 text-sm text-slate-950" onChange={(event) => onChange({ ...value, search: event.target.value })} placeholder="Search Youth Project" value={value.search} />
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, status: event.target.value })} value={value.status}>
        <option value="all">All statuses</option><option value="planning">Planning</option><option value="recruiting">Recruiting</option><option value="active">Active</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option>
      </select>
      <select className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700" onChange={(event) => onChange({ ...value, workspace: event.target.value })} value={value.workspace}>
        <option value="all">All Workspaces</option>{workspaces.map((workspace) => <option key={workspace.id} value={workspace.id}>{workspace.title}</option>)}
      </select>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.active} onChange={(event) => onChange({ ...value, active: event.target.checked })} type="checkbox" />Active</label>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.consent} onChange={(event) => onChange({ ...value, consent: event.target.checked })} type="checkbox" />Consent incomplete</label>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.attendance} onChange={(event) => onChange({ ...value, attendance: event.target.checked })} type="checkbox" />Attendance pending</label>
      <label className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700"><input checked={value.vetting} onChange={(event) => onChange({ ...value, vetting: event.target.checked })} type="checkbox" />Vetting pending</label>
    </section>
  );
}

export function YouthProjectList(props: YouthProjectListProps) {
  return <div className="grid gap-4 xl:grid-cols-2">{props.projects.map((project) => <YouthProjectCard {...props} key={project.id} project={project} />)}</div>;
}

type YouthProjectListProps = {
  projects: YouthProjectItem[];
  activities: YouthActivityItem[];
  sessions: YouthSessionItem[];
  consent: ConsentRecordItem[];
  facilitators: FacilitatorAssignmentItem[];
  assessments: YouthAssessmentItem[];
  showcases: ShowcaseOutputItem[];
  workspaces: OperatingContextListItem[];
  onSelect: (project: YouthProjectItem) => void;
};

function YouthProjectCard({ project, activities, sessions, consent, facilitators, assessments, showcases, workspaces, onSelect }: YouthProjectListProps & { project: YouthProjectItem }) {
  const projectActivities = youthActivities(activities, project.id);
  const projectSessions = youthSessions(sessions, projectActivities);
  const projectConsent = youthConsent(consent, project.id);
  const projectFacilitators = youthFacilitators(facilitators, project.id);
  const consentRate = projectConsent.length ? Math.round(projectConsent.filter((record) => record.guardian_consent_received).length / projectConsent.length * 100) : 0;
  return <article className="rounded-lg border border-slate-200 bg-white p-4"><div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between"><div><h2 className="text-base font-bold text-slate-950">{workspaceName(workspaces, project.operating_context)}</h2><p className="mt-1 text-sm text-slate-500">Youth Project · Ages {project.age_range_min ?? 'n/a'}-{project.age_range_max ?? 'n/a'}</p></div><ReadinessBadge value={project.status} /></div><dl className="mt-4 grid gap-3 text-sm md:grid-cols-4"><div><dt className="font-bold text-slate-700">Learners</dt><dd className="mt-1 text-slate-600">{project.target_learners}</dd></div><div><dt className="font-bold text-slate-700">Schools</dt><dd className="mt-1 text-slate-600">{project.target_schools}</dd></div><div><dt className="font-bold text-slate-700">Activities</dt><dd className="mt-1 text-slate-600">{projectActivities.length}</dd></div><div><dt className="font-bold text-slate-700">Sessions</dt><dd className="mt-1 text-slate-600">{projectSessions.length}</dd></div><div><dt className="font-bold text-slate-700">Consent</dt><dd className="mt-1 text-slate-600">{consentRate}%</dd></div><div><dt className="font-bold text-slate-700">Vetted facilitators</dt><dd className="mt-1 text-slate-600">{projectFacilitators.filter((item) => item.is_vetted).length}/{projectFacilitators.length}</dd></div><div><dt className="font-bold text-slate-700">Assessments</dt><dd className="mt-1 text-slate-600">{youthAssessments(assessments, project.id).length}</dd></div><div><dt className="font-bold text-slate-700">Showcases / Outputs</dt><dd className="mt-1 text-slate-600">{youthShowcases(showcases, project.id).length}</dd></div></dl><div className="mt-4"><BlockerAlert blockers={youthBlockers(project, projectSessions, projectConsent, projectFacilitators)} /></div><button className="mt-4 h-10 rounded-md bg-blue-600 px-4 text-sm font-bold text-white hover:bg-blue-700" onClick={() => onSelect(project)} type="button">View Youth Project</button></article>;
}

export function YouthProjectDetail({ project, activities, sessions, learnerGroups, facilitators, consent, attendance, assessments, showcases, users, workspaces, onAction, onClose }: {
  project: YouthProjectItem | null;
  activities: YouthActivityItem[];
  sessions: YouthSessionItem[];
  learnerGroups: LearnerGroupItem[];
  facilitators: FacilitatorAssignmentItem[];
  consent: ConsentRecordItem[];
  attendance: AttendanceRecordItem[];
  assessments: YouthAssessmentItem[];
  showcases: ShowcaseOutputItem[];
  users: UserListItem[];
  workspaces: OperatingContextListItem[];
  onAction: (action: YouthAction) => void;
  onClose: () => void;
}) {
  const [section, setSection] = useState('overview');
  const data = useMemo(() => {
    if (!project) return null;
    const projectActivities = youthActivities(activities, project.id);
    const projectSessions = youthSessions(sessions, projectActivities);
    return {
      activities: projectActivities,
      sessions: projectSessions,
      facilitators: youthFacilitators(facilitators, project.id),
      consent: youthConsent(consent, project.id),
      assessments: youthAssessments(assessments, project.id),
      showcases: youthShowcases(showcases, project.id),
    };
  }, [activities, assessments, consent, facilitators, project, sessions, showcases]);
  if (!project || !data) return null;
  return <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-4xl overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-semibold text-blue-700">Youth Development</p><h2 className="mt-1 text-xl font-bold text-slate-950">{workspaceName(workspaces, project.operating_context)}</h2><p className="mt-1 text-sm text-slate-500">Youth Project · {project.target_learners} target learners · {project.target_schools} target schools</p></div><button aria-label="Close Youth Project detail" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700" onClick={onClose} type="button"><X className="h-4 w-4" /></button></div><div className="mt-5 flex flex-wrap gap-2">{['overview', 'activities', 'sessions', 'consent', 'attendance', 'facilitators', 'assessments', 'showcases'].map((item) => <button className={`h-9 rounded-md px-3 text-sm font-bold ${section === item ? 'bg-slate-950 text-white' : 'bg-slate-100 text-slate-700'}`} key={item} onClick={() => setSection(item)} type="button">{item === 'showcases' ? 'Showcases / Outputs' : labelFromValue(item)}</button>)}</div><div className="mt-5 space-y-4"><div className="flex flex-wrap gap-2"><ReadinessBadge value={project.status} /><button className="h-9 rounded-md bg-blue-600 px-3 text-sm font-bold text-white" onClick={() => onAction({ kind: 'activate', project })} type="button">Activate</button><button className="h-9 rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700" onClick={() => onAction({ kind: 'complete', project })} type="button">Complete</button><a className="inline-flex h-9 items-center rounded-md border border-slate-200 px-3 text-sm font-bold text-slate-700" href="/reports">Open Youth Summary Report</a></div><BlockerAlert blockers={youthBlockers(project, data.sessions, data.consent, data.facilitators)} />{section === 'overview' ? <YouthSummaryCards project={project} activities={data.activities} sessions={data.sessions} consent={data.consent} facilitators={data.facilitators} assessments={data.assessments} showcases={data.showcases} /> : null}{section === 'activities' ? <YouthActivityList activities={data.activities} /> : null}{section === 'sessions' ? <YouthSessionList activities={data.activities} sessions={data.sessions} onAction={onAction} /> : null}{section === 'consent' ? <ConsentPanel consent={data.consent} groups={learnerGroups} onAction={onAction} /> : null}{section === 'attendance' ? <AttendancePanel attendance={attendance} groups={learnerGroups} sessions={data.sessions} /> : null}{section === 'facilitators' ? <FacilitatorPanel activities={data.activities} facilitators={data.facilitators} onAction={onAction} users={users} /> : null}{section === 'assessments' ? <AssessmentList assessments={data.assessments} activities={data.activities} users={users} /> : null}{section === 'showcases' ? <ShowcaseOutputList showcases={data.showcases} workspaces={workspaces} /> : null}</div></aside>;
}

export function YouthSummaryCards({ project, activities, sessions, consent, facilitators, assessments, showcases }: { project: YouthProjectItem; activities: YouthActivityItem[]; sessions: YouthSessionItem[]; consent: ConsentRecordItem[]; facilitators: FacilitatorAssignmentItem[]; assessments: YouthAssessmentItem[]; showcases: ShowcaseOutputItem[] }) {
  const consentRate = consent.length ? Math.round(consent.filter((record) => record.guardian_consent_received).length / consent.length * 100) : 0;
  const attendanceReady = sessions.length ? Math.round(sessions.filter((session) => session.attendance_captured).length / sessions.length * 100) : 0;
  return <div className="grid gap-3 md:grid-cols-4">{[['Target learners', project.target_learners], ['Activities', activities.length], ['Sessions completed', sessions.filter((session) => session.status === 'completed').length], ['Consent rate', `${consentRate}%`], ['Attendance captured', `${attendanceReady}%`], ['Vetted facilitators', `${facilitators.filter((item) => item.is_vetted).length}/${facilitators.length}`], ['Assessments', assessments.length], ['Showcases / Outputs', showcases.length]].map(([label, value]) => <div className="rounded-md border border-slate-200 p-3" key={label}><div className="text-xs font-bold uppercase tracking-normal text-slate-500">{label}</div><div className="mt-2 text-2xl font-bold text-slate-950">{value}</div></div>)}</div>;
}

export function YouthActivityList({ activities }: { activities: YouthActivityItem[] }) {
  return <List title="Activities" empty="No activities returned. Create/edit activity can be added once needed through existing CRUD patterns." items={activities.map((activity) => ({ id: activity.id, title: activity.name, meta: `${labelFromValue(activity.activity_type)} · ${labelFromValue(activity.recurrence)} · ${activity.start_date ?? 'No start'} to ${activity.end_date ?? 'No end'}`, detail: activity.description || 'No description captured.' }))} />;
}

export function YouthSessionList({ activities, sessions, onAction }: { activities: YouthActivityItem[]; sessions: YouthSessionItem[]; onAction: (action: YouthAction) => void }) {
  return <div className="rounded-lg border border-slate-200"><div className="border-b border-slate-200 px-4 py-3"><h3 className="text-base font-bold text-slate-950">Sessions</h3></div><div className="divide-y divide-slate-100">{sessions.length ? sessions.map((session) => <div className="flex flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between" key={session.id}><div><div className="text-sm font-bold text-slate-900">{activities.find((activity) => activity.id === session.activity)?.name ?? 'Activity unavailable'}</div><div className="mt-1 text-xs text-slate-500">{session.session_date} · {session.start_time ?? 'No start'}-{session.end_time ?? 'No end'} · Attendance {session.attendance_captured ? 'captured' : 'pending'}</div><RestrictedField value={session.facilitator_notes} /></div><div className="flex flex-wrap gap-2"><ReadinessBadge value={session.status} /><button className="h-8 rounded-md border border-slate-200 px-2 text-xs font-bold text-slate-700" onClick={() => onAction({ kind: 'complete-session', session })} type="button">Complete session</button></div></div>) : <div className="p-4 text-sm text-slate-500">No sessions returned.</div>}</div></div>;
}

export function ConsentPanel({ consent, groups, onAction }: { consent: ConsentRecordItem[]; groups: LearnerGroupItem[]; onAction: (action: YouthAction) => void }) {
  return <div className="rounded-lg border border-slate-200"><div className="border-b border-slate-200 px-4 py-3"><h3 className="text-base font-bold text-slate-950">Consent</h3></div><div className="divide-y divide-slate-100">{consent.length ? consent.map((record) => <div className="flex flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between" key={record.id}><div><div className="text-sm font-bold text-slate-900">{record.learner_identifier}</div><div className="mt-1 text-xs text-slate-500">{groups.find((group) => group.id === record.learner_group)?.name ?? 'No learner group'} · Photo {record.photo_consent ? 'yes' : 'no'} · Data {record.data_processing_consent ? 'yes' : 'no'}</div></div><div className="flex flex-wrap gap-2"><ReadinessBadge value={record.guardian_consent_received ? 'verified' : 'missing'} /><button className="h-8 rounded-md border border-slate-200 px-2 text-xs font-bold text-slate-700" onClick={() => onAction({ kind: 'receive-consent', consent: record })} type="button">Receive</button><button className="h-8 rounded-md border border-rose-200 px-2 text-xs font-bold text-rose-700" onClick={() => onAction({ kind: 'withdraw-consent', consent: record })} type="button">Withdraw</button></div></div>) : <div className="p-4 text-sm text-slate-500">No consent records returned or access is restricted.</div>}</div></div>;
}

export function AttendancePanel({ attendance, groups, sessions }: { attendance: AttendanceRecordItem[]; groups: LearnerGroupItem[]; sessions: YouthSessionItem[] }) {
  const sessionIds = new Set(sessions.map((session) => session.id));
  const scoped = attendance.filter((record) => sessionIds.has(record.session));
  return <List title="Attendance" empty="No attendance records returned or access is restricted." items={scoped.map((record) => ({ id: record.id, title: record.learner_identifier, meta: `${groups.find((group) => group.id === record.learner_group)?.name ?? 'No learner group'} · ${record.present ? 'Present' : 'Absent'} · Arrival ${record.arrival_time ?? 'not set'}`, detail: record.notes || 'No notes captured.' }))} />;
}

export function FacilitatorPanel({ activities, facilitators, users, onAction }: { activities: YouthActivityItem[]; facilitators: FacilitatorAssignmentItem[]; users: UserListItem[]; onAction: (action: YouthAction) => void }) {
  return <div className="rounded-lg border border-slate-200"><div className="border-b border-slate-200 px-4 py-3"><h3 className="text-base font-bold text-slate-950">Facilitators</h3></div><div className="divide-y divide-slate-100">{facilitators.length ? facilitators.map((facilitator) => <div className="flex flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between" key={facilitator.id}><div><div className="text-sm font-bold text-slate-900">{users.find((user) => user.id === facilitator.facilitator)?.full_name ?? 'Facilitator unavailable'}</div><div className="mt-1 text-xs text-slate-500">{facilitator.role} · {activities.find((activity) => activity.id === facilitator.activity)?.name ?? 'Project-level'} · {facilitator.start_date ?? 'No start'} to {facilitator.end_date ?? 'No end'}</div><RestrictedField value={facilitator.vetting_notes} /></div><div className="flex flex-wrap gap-2"><ReadinessBadge value={facilitator.is_vetted ? 'verified' : 'pending_verification'} /><button className="h-8 rounded-md border border-slate-200 px-2 text-xs font-bold text-slate-700" onClick={() => onAction({ kind: 'vet-facilitator', facilitator })} type="button">Vet</button></div></div>) : <div className="p-4 text-sm text-slate-500">No facilitators returned.</div>}</div></div>;
}

export function AssessmentList({ assessments, activities, users }: { assessments: YouthAssessmentItem[]; activities: YouthActivityItem[]; users: UserListItem[] }) {
  return <List title="Assessments" empty="No assessments returned or access is restricted." items={assessments.map((assessment) => ({ id: assessment.id, title: assessment.learner_identifier, meta: `${labelFromValue(assessment.assessment_type)} · ${assessment.score || 'No score'} · ${activities.find((activity) => activity.id === assessment.activity)?.name ?? 'No activity'} · ${users.find((user) => user.id === assessment.assessor)?.full_name ?? 'Assessor unavailable'}`, detail: assessment.notes || 'No notes captured.' }))} />;
}

export function ShowcaseOutputList({ showcases, workspaces }: { showcases: ShowcaseOutputItem[]; workspaces: OperatingContextListItem[] }) {
  return <List title="Showcases / Outputs" empty="No showcases or outputs returned." items={showcases.map((showcase) => ({ id: showcase.id, title: showcase.title, meta: `${labelFromValue(showcase.output_type)} · ${showcase.date ?? 'No date'} · ${showcase.output_context ? workspaceName(workspaces, showcase.output_context) : 'No linked public output'}`, detail: showcase.description || 'No description captured.' }))} />;
}

function List({ title, empty, items }: { title: string; empty: string; items: { id: string; title: string; meta: string; detail: string }[] }) {
  return <div className="rounded-lg border border-slate-200"><div className="border-b border-slate-200 px-4 py-3"><h3 className="text-base font-bold text-slate-950">{title}</h3></div><div className="divide-y divide-slate-100">{items.length ? items.map((item) => <div className="px-4 py-3" key={item.id}><div className="text-sm font-bold text-slate-900">{item.title}</div><div className="mt-1 text-xs text-slate-500">{item.meta}</div><p className="mt-2 text-sm text-slate-600">{item.detail}</p></div>) : <div className="p-4 text-sm text-slate-500">{empty}</div>}</div></div>;
}

export function YouthActionDialog({ action, submitting, onClose, onSubmit }: { action: YouthAction | null; submitting: boolean; onClose: () => void; onSubmit: (comment: string) => void }) {
  const [comment, setComment] = useState('');
  if (!action) return null;
  const title = action.kind === 'complete-session' ? 'Complete session' : labelFromValue(action.kind);
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); onSubmit(comment); }
  return <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-md overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-semibold text-blue-700">Youth Development action</p><h2 className="mt-1 text-xl font-bold text-slate-950">{title}</h2></div><button aria-label="Close Youth action" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 text-slate-700" onClick={onClose} type="button"><X className="h-4 w-4" /></button></div><form className="mt-5 space-y-4" onSubmit={submit}><div><label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="youth-comment">Comment</label><textarea className="min-h-28 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-950" id="youth-comment" onChange={(event) => setComment(event.target.value)} value={comment} /></div><button className="h-10 w-full rounded-md bg-blue-600 px-4 text-sm font-bold text-white disabled:bg-slate-400" disabled={submitting} type="submit">{submitting ? 'Submitting' : title}</button></form></aside>;
}


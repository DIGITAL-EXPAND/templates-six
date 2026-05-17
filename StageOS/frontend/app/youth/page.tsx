'use client';

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DepartmentExecutiveActionsPanel } from '@/components/governance/department-executive-actions-panel';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import {
  YouthActionDialog,
  YouthProjectDetail,
  YouthProjectFilters,
  YouthProjectList,
  youthActivities,
  youthBlockers,
  youthConsent,
  youthFacilitators,
  youthSessions,
  type YouthAction,
} from '@/components/youth/youth-components';
import { ApiError } from '@/lib/api/client';
import {
  completeYouthSession,
  fetchAttendanceRecords,
  fetchConsentRecords,
  fetchFacilitators,
  fetchLearnerGroups,
  fetchOperatingContexts,
  fetchShowcaseOutputs,
  fetchUsers,
  fetchYouthActivities,
  fetchYouthAssessments,
  fetchYouthProjects,
  fetchYouthSessions,
  setConsentAction,
  setYouthProjectAction,
  vetFacilitator,
} from '@/lib/api/endpoints';
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
import { useAuth } from '@/lib/auth/auth-provider';

export default function YouthPage() {
  const { tokens } = useAuth();
  const [projects, setProjects] = useState<YouthProjectItem[]>([]);
  const [activities, setActivities] = useState<YouthActivityItem[]>([]);
  const [sessions, setSessions] = useState<YouthSessionItem[]>([]);
  const [learnerGroups, setLearnerGroups] = useState<LearnerGroupItem[]>([]);
  const [facilitators, setFacilitators] = useState<FacilitatorAssignmentItem[]>([]);
  const [consent, setConsent] = useState<ConsentRecordItem[]>([]);
  const [attendance, setAttendance] = useState<AttendanceRecordItem[]>([]);
  const [assessments, setAssessments] = useState<YouthAssessmentItem[]>([]);
  const [showcases, setShowcases] = useState<ShowcaseOutputItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [selectedProject, setSelectedProject] = useState<YouthProjectItem | null>(null);
  const [action, setAction] = useState<YouthAction | null>(null);
  const [filters, setFilters] = useState({ status: 'all', workspace: 'all', active: false, completed: false, consent: false, attendance: false, vetting: false, search: '' });
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!tokens?.access) return;
    let mounted = true;
    Promise.allSettled([
      fetchYouthProjects(tokens.access),
      fetchYouthActivities(tokens.access),
      fetchYouthSessions(tokens.access),
      fetchLearnerGroups(tokens.access),
      fetchFacilitators(tokens.access),
      fetchConsentRecords(tokens.access),
      fetchAttendanceRecords(tokens.access),
      fetchYouthAssessments(tokens.access),
      fetchShowcaseOutputs(tokens.access),
      fetchOperatingContexts(tokens.access),
      fetchUsers(tokens.access),
    ])
      .then(([projectResult, activityResult, sessionResult, groupResult, facilitatorResult, consentResult, attendanceResult, assessmentResult, showcaseResult, workspaceResult, userResult]) => {
        if (!mounted) return;
        if (projectResult.status === 'fulfilled') setProjects(projectResult.value.results);
        else if (projectResult.reason instanceof ApiError && projectResult.reason.status === 403) setPermissionDenied(true);
        else setError('Youth Development records could not be loaded.');
        if (activityResult.status === 'fulfilled') setActivities(activityResult.value.results);
        if (sessionResult.status === 'fulfilled') setSessions(sessionResult.value.results);
        if (groupResult.status === 'fulfilled') setLearnerGroups(groupResult.value.results);
        if (facilitatorResult.status === 'fulfilled') setFacilitators(facilitatorResult.value.results);
        if (consentResult.status === 'fulfilled') setConsent(consentResult.value.results);
        if (attendanceResult.status === 'fulfilled') setAttendance(attendanceResult.value.results);
        if (assessmentResult.status === 'fulfilled') setAssessments(assessmentResult.value.results);
        if (showcaseResult.status === 'fulfilled') setShowcases(showcaseResult.value.results);
        if (workspaceResult.status === 'fulfilled') setWorkspaces(workspaceResult.value.results);
        if (userResult.status === 'fulfilled') setUsers(userResult.value.results);
      })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [tokens?.access]);

  const filteredProjects = useMemo(() => projects.filter((project) => {
    const projectActivities = youthActivities(activities, project.id);
    const projectSessions = youthSessions(sessions, projectActivities);
    const projectConsent = youthConsent(consent, project.id);
    const projectFacilitators = youthFacilitators(facilitators, project.id);
    const blockers = youthBlockers(project, projectSessions, projectConsent, projectFacilitators);
    const workspace = workspaces.find((item) => item.id === project.operating_context);
    const query = filters.search.trim().toLowerCase();
    if (filters.status !== 'all' && project.status !== filters.status) return false;
    if (filters.workspace !== 'all' && project.operating_context !== filters.workspace) return false;
    if (filters.active && project.status !== 'active') return false;
    if (filters.completed && project.status !== 'completed') return false;
    if (filters.consent && !blockers.some((blocker) => blocker.toLowerCase().includes('consent'))) return false;
    if (filters.attendance && !blockers.some((blocker) => blocker.toLowerCase().includes('attendance'))) return false;
    if (filters.vetting && !blockers.some((blocker) => blocker.toLowerCase().includes('vetting'))) return false;
    if (query && !`${workspace?.title ?? ''} ${project.status}`.toLowerCase().includes(query)) return false;
    return true;
  }), [activities, consent, facilitators, filters, projects, sessions, workspaces]);

  async function handleAction(comment: string) {
    if (!tokens?.access || !action) return;
    setSubmitting(true);
    setError('');
    try {
      if (action.kind === 'activate' || action.kind === 'complete') {
        const updated = await setYouthProjectAction(tokens.access, action.project.id, action.kind, comment);
        setProjects((current) => current.map((project) => project.id === updated.id ? updated : project));
        setSelectedProject((current) => current?.id === updated.id ? updated : current);
      } else if (action.kind === 'complete-session') {
        const updated = await completeYouthSession(tokens.access, action.session.id, comment);
        setSessions((current) => current.map((session) => session.id === updated.id ? updated : session));
      } else if (action.kind === 'receive-consent' || action.kind === 'withdraw-consent') {
        const updated = await setConsentAction(tokens.access, action.consent.id, action.kind, comment);
        setConsent((current) => current.map((record) => record.id === updated.id ? updated : record));
      } else if (action.kind === 'vet-facilitator') {
        const updated = await vetFacilitator(tokens.access, action.facilitator.id, comment);
        setFacilitators((current) => current.map((facilitator) => facilitator.id === updated.id ? updated : facilitator));
      }
      setAction(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) setError('You do not have permission to view Youth Development records.');
      else if (err instanceof ApiError) setError(JSON.stringify(err.payload ?? { detail: err.message }));
      else setError('Youth Development action could not be completed.');
    } finally {
      setSubmitting(false);
    }
  }

  return <AppShell><div className="space-y-5"><PageHeader description="Manage Youth Projects, activities, sessions, consent, attendance, facilitators, assessments and showcases." eyebrow="Youth Development" title="Youth Development" />{permissionDenied ? <PermissionDeniedState /> : null}{error ? <ErrorState message={error} /> : null}{loading ? <LoadingState label="Loading Youth Development records" /> : <><YouthProjectFilters onChange={setFilters} value={filters} workspaces={workspaces} /><DepartmentExecutiveActionsPanel departmentTypes={['youth']} targetTypes={['YouthProject', 'Session', 'ConsentRecord', 'FacilitatorAssignment', 'Assessment']} />{filteredProjects.length ? <YouthProjectList activities={activities} assessments={assessments} consent={consent} facilitators={facilitators} onSelect={setSelectedProject} projects={filteredProjects} sessions={sessions} showcases={showcases} workspaces={workspaces} /> : <EmptyState description="Youth Projects will appear here when records are available or filters are cleared." title="No Youth Projects found" />}</>}</div><YouthProjectDetail activities={activities} assessments={assessments} attendance={attendance} consent={consent} facilitators={facilitators} learnerGroups={learnerGroups} onAction={setAction} onClose={() => setSelectedProject(null)} project={selectedProject} sessions={sessions} showcases={showcases} users={users} workspaces={workspaces} /><YouthActionDialog action={action} onClose={() => setAction(null)} onSubmit={handleAction} submitting={submitting} /></AppShell>;
}

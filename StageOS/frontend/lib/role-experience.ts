import {
  BadgeCheck,
  BarChart3,
  BriefcaseBusiness,
  CalendarClock,
  ClipboardCheck,
  FileText,
  Handshake,
  History,
  Home,
  Landmark,
  Megaphone,
  Mic2,
  Scale,
  Settings,
  Ticket,
  Truck,
  Users,
  Wrench,
} from 'lucide-react';
import type { OperatingProfile } from '@/lib/api/types';
import { NAV_LABELS } from '@/lib/labels';

export type DashboardKind =
  | 'admin'
  | 'executive'
  | 'gm'
  | 'programming'
  | 'marketing'
  | 'technical'
  | 'foh'
  | 'contracts'
  | 'scm'
  | 'ticketing'
  | 'youth'
  | 'governance'
  | 'hospitality'
  | 'board'
  | 'client'
  | 'supplier'
  | 'artist'
  | 'generic';

export function dashboardKind(profile: OperatingProfile | null): DashboardKind {
  const userType = profile?.user.user_type;
  const authority = profile?.primary_position?.authority_level;
  const department = profile?.primary_department?.name ?? '';
  if (userType === 'internal_admin') return 'admin';
  if (userType === 'executive') return 'executive';
  if (authority === 'gm') return 'gm';
  if (userType === 'read_only') return 'board';
  if (userType === 'client_external') return 'client';
  if (userType === 'supplier_external') return 'supplier';
  if (userType === 'artist_external') return 'artist';
  if (department.includes('Programming')) return 'programming';
  if (department.includes('Marketing')) return 'marketing';
  if (department.includes('Technical')) return 'technical';
  if (department.includes('FOH')) return 'foh';
  if (department.includes('Contracts')) return 'contracts';
  if (department.includes('SCM')) return 'scm';
  if (department.includes('Ticketing')) return 'ticketing';
  if (department.includes('Youth')) return 'youth';
  if (department.includes('Governance')) return 'governance';
  if (department.includes('Hospitality')) return 'hospitality';
  return 'generic';
}

// All individual navigation items, using theatre-friendly NAV_LABELS
const allItems = {
  dashboard:   { label: NAV_LABELS.home,           href: '/dashboard',  icon: Home },
  calendar:    { label: NAV_LABELS.calendar,        href: '/calendar',   icon: CalendarClock },
  workspaces:  { label: NAV_LABELS.productions,     href: '/workspaces', icon: CalendarClock },
  programming: { label: NAV_LABELS.proposals,       href: '/programming',icon: Landmark },
  marketing:   { label: NAV_LABELS.marketing,       href: '/marketing',  icon: Megaphone },
  technical:   { label: NAV_LABELS.technical,       href: '/technical',  icon: Wrench },
  operations:  { label: NAV_LABELS.frontOfHouse,    href: '/operations', icon: Users },
  contracts:   { label: NAV_LABELS.agreements,      href: '/contracts',  icon: BriefcaseBusiness },
  suppliers:   { label: NAV_LABELS.suppliers,       href: '/suppliers',  icon: Truck },
  artists:     { label: NAV_LABELS.performers,      href: '/artists',    icon: Mic2 },
  ticketing:   { label: NAV_LABELS.boxOffice,       href: '/ticketing',  icon: Ticket },
  youth:       { label: NAV_LABELS.youthProgrammes, href: '/youth',      icon: Handshake },
  governance:  { label: NAV_LABELS.governance,      href: '/governance', icon: Scale },
  documents:   { label: NAV_LABELS.files,           href: '/documents',  icon: FileText },
  tasks:       { label: NAV_LABELS.myWork,          href: '/tasks',      icon: ClipboardCheck },
  approvals:   { label: NAV_LABELS.signOff,         href: '/approvals',  icon: BadgeCheck },
  reports:     { label: NAV_LABELS.reports,         href: '/reports',    icon: BarChart3 },
  audit:       { label: NAV_LABELS.activityLog,     href: '/audit',      icon: History },
  settings:    { label: NAV_LABELS.settings,        href: '/settings',   icon: Settings },
};

function departmentItem(kind: DashboardKind) {
  if (kind === 'marketing')   return allItems.marketing;
  if (kind === 'technical')   return allItems.technical;
  if (kind === 'foh')         return allItems.operations;
  if (kind === 'contracts')   return allItems.contracts;
  if (kind === 'scm')         return allItems.suppliers;
  if (kind === 'ticketing')   return allItems.ticketing;
  if (kind === 'youth')       return allItems.youth;
  if (kind === 'governance')  return allItems.governance;
  if (kind === 'hospitality') return allItems.operations;
  return allItems.programming;
}

export function navigationGroups(profile: OperatingProfile | null) {
  const kind = dashboardKind(profile);
  const authority = profile?.primary_position?.authority_level;

  if (kind === 'admin') {
    return [
      {
        label: 'Main Menu',
        items: [allItems.dashboard, allItems.calendar, allItems.workspaces],
      },
      {
        label: 'Planning',
        items: [
          allItems.programming,
          allItems.tasks,
          allItems.documents,
          allItems.approvals,
          allItems.contracts,
          allItems.suppliers,
          allItems.artists,
        ],
      },
      {
        label: 'Departments',
        items: [
          allItems.marketing,
          allItems.technical,
          allItems.operations,
          allItems.ticketing,
          allItems.youth,
        ],
      },
      {
        label: 'Oversight',
        items: [allItems.governance, allItems.reports, allItems.audit, allItems.settings],
      },
    ];
  }

  if (kind === 'executive') {
    return [
      {
        label: 'Oversight',
        items: [
          allItems.dashboard,
          allItems.calendar,
          allItems.workspaces,
          allItems.governance,
          allItems.reports,
          allItems.audit,
          allItems.tasks,
        ],
      },
    ];
  }

  if (kind === 'gm') {
    return [
      {
        label: 'Operations',
        items: [
          allItems.dashboard,
          allItems.calendar,
          allItems.workspaces,
          allItems.reports,
          allItems.tasks,
        ],
      },
    ];
  }

  if (kind === 'board') {
    return [
      {
        label: 'Board',
        items: [allItems.dashboard, allItems.reports, allItems.governance, allItems.tasks],
      },
    ];
  }

  if (['client', 'supplier', 'artist'].includes(kind)) {
    const externalItem =
      kind === 'client'
        ? allItems.programming
        : kind === 'supplier'
        ? allItems.suppliers
        : allItems.artists;
    return [
      {
        label: 'My Area',
        items: [allItems.dashboard, externalItem, allItems.documents, allItems.tasks],
      },
    ];
  }

  if (authority === 'department_manager') {
    return [
      {
        label: 'Department',
        items: [
          allItems.dashboard,
          allItems.calendar,
          allItems.workspaces,
          departmentItem(kind),
          allItems.tasks,
          allItems.documents,
          allItems.reports,
        ],
      },
    ];
  }

  return [
    {
      label: 'My Work',
      items: [allItems.dashboard, allItems.tasks, allItems.documents],
    },
  ];
}

export function canApproveDepartment(
  profile: OperatingProfile | null,
  departmentId?: string | null,
) {
  if (!profile || !departmentId) return false;
  return profile.can_approve_departments.some((department) => department.id === departmentId);
}

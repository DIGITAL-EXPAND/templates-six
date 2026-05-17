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
  ShieldAlert,
  Ticket,
  Truck,
  Users,
  Wrench,
} from 'lucide-react';

export const moduleGroups = [
  {
    label: 'Main Menu',
    items: [
      { label: 'Dashboard', href: '/dashboard', icon: Home },
      { label: 'Workspaces', href: '/workspaces', icon: CalendarClock },
      { label: 'Calendar', href: '/calendar', icon: CalendarClock },
    ],
  },
  {
    label: 'Planning',
    items: [
      { label: 'Programming', href: '/programming', icon: Landmark },
      { label: 'Tasks', href: '/tasks', icon: ClipboardCheck },
      { label: 'Documents', href: '/documents', icon: FileText },
      { label: 'Approvals', href: '/approvals', icon: BadgeCheck },
      { label: 'Contracts', href: '/contracts', icon: BriefcaseBusiness },
      { label: 'Suppliers', href: '/suppliers', icon: Truck },
      { label: 'Artists', href: '/artists', icon: Mic2 },
    ],
  },
  {
    label: 'Departments',
    items: [
      { label: 'Marketing', href: '/marketing', icon: Megaphone },
      { label: 'Technical', href: '/technical', icon: Wrench },
      { label: 'FOH / Operations', href: '/operations', icon: Users },
      { label: 'Ticketing', href: '/ticketing', icon: Ticket },
      { label: 'Youth Development', href: '/youth', icon: Handshake },
    ],
  },
  {
    label: 'Oversight',
    items: [
      { label: 'Governance', href: '/governance', icon: Scale },
      { label: 'Reports', href: '/reports', icon: BarChart3 },
      { label: 'Audit Trail', href: '/audit', icon: History },
      { label: 'Settings', href: '/settings', icon: Settings },
    ],
  },
] as const;

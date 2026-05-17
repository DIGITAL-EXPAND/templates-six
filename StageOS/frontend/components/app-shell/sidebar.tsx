'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';
import { ChevronLeft, ChevronRight, Settings, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { fetchOperatingProfile } from '@/lib/api/endpoints';
import type { OperatingProfile } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';
import { dashboardKind, navigationGroups } from '@/lib/role-experience';
import { DASHBOARD_LABELS } from '@/lib/labels';

function getInitials(firstName: string, lastName: string): string {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
}

export type SidebarProps = {
  open: boolean;
  collapsed: boolean;
  onClose: () => void;
  onCollapsedChange: (collapsed: boolean) => void;
};

export function Sidebar({ open, collapsed, onClose, onCollapsedChange }: SidebarProps) {
  const pathname = usePathname();
  const { tokens, user } = useAuth();
  const [profile, setProfile] = useState<OperatingProfile | null>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchOperatingProfile(tokens.access)
      .then(setProfile)
      .catch(() => setProfile(null));
  }, [tokens?.access]);

  // Persist collapse state to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('stageos-sidebar-collapsed', collapsed ? '1' : '0');
    } catch {
      // ignore in restricted environments
    }
  }, [collapsed]);

  const moduleGroups = navigationGroups(profile);
  const kind = dashboardKind(profile);
  const kindInfo = DASHBOARD_LABELS[kind];
  const roleLabel = kindInfo?.subheading ?? 'Team Member';

  const orgName = profile?.organisation?.name ?? 'StageOS';
  const firstName = user?.first_name ?? '';
  const lastName = user?.last_name ?? '';
  const displayName = user?.full_name ?? user?.email ?? 'User';
  const initials =
    firstName || lastName
      ? getInitials(firstName, lastName)
      : (user?.email?.charAt(0) ?? 'U').toUpperCase();

  return (
    <>
      {/* Mobile overlay backdrop */}
      {open && (
        <button
          aria-label="Close navigation"
          className="fixed inset-0 z-30 bg-gray-950/50 backdrop-blur-[1px] md:hidden"
          onClick={onClose}
          type="button"
        />
      )}

      <aside
        className={clsx(
          // Base: fixed on mobile (overlaid), static column on desktop
          'fixed inset-y-0 left-0 z-40 flex flex-col bg-gray-950 text-white transition-all duration-200',
          // Desktop: always visible, translate reset
          'md:static md:z-auto md:translate-x-0',
          // Mobile: slide in/out
          open ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
          // Width
          collapsed ? 'md:w-16' : 'md:w-64',
          'w-64',
        )}
      >
        {/* ── Header ─────────────────────────────────────────── */}
        <div
          className={clsx(
            'flex shrink-0 flex-col border-b border-white/10',
            collapsed ? 'px-2 py-3' : 'px-4 py-4',
          )}
        >
          {/* Logo row */}
          <div className={clsx('flex items-center', collapsed ? 'justify-center' : 'gap-3')}>
            <Link
              aria-label="Go to dashboard"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-teal-600 text-sm font-black text-white"
              href="/dashboard"
              onClick={onClose}
            >
              SO
            </Link>

            {/* Brand + org — hidden when collapsed */}
            {!collapsed && (
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-bold text-white">StageOS</div>
                <div className="truncate text-[11px] text-gray-400">{orgName}</div>
              </div>
            )}

            {/* Mobile close */}
            <button
              aria-label="Close navigation"
              className="ml-auto inline-flex h-8 w-8 items-center justify-center rounded-md text-gray-400 hover:bg-white/10 hover:text-white md:hidden"
              onClick={onClose}
              ref={closeBtnRef}
              type="button"
            >
              <X className="h-4 w-4" />
            </button>

            {/* Desktop collapse toggle */}
            <button
              aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              className="hidden md:inline-flex h-7 w-7 items-center justify-center rounded-md text-gray-400 hover:bg-white/10 hover:text-white"
              onClick={() => onCollapsedChange(!collapsed)}
              type="button"
            >
              {collapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </button>
          </div>

          {/* User card — shown when expanded */}
          {!collapsed && (
            <div className="mt-3 rounded-md border border-white/10 bg-white/[0.06] px-3 py-2">
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-teal-600 text-xs font-bold text-white">
                  {initials}
                </span>
                <div className="min-w-0">
                  <div className="truncate text-xs font-semibold text-white">{displayName}</div>
                  <div className="truncate text-[11px] text-gray-400">{roleLabel}</div>
                </div>
              </div>
            </div>
          )}

          {/* Collapsed: avatar only */}
          {collapsed && (
            <div className="mt-2 flex justify-center">
              <span
                className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-600 text-xs font-bold text-white"
                title={displayName}
              >
                {initials}
              </span>
            </div>
          )}
        </div>

        {/* ── Navigation ─────────────────────────────────────── */}
        <nav
          aria-label="Primary navigation"
          className="flex-1 overflow-y-auto overflow-x-hidden py-3"
          style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(255,255,255,0.1) transparent' }}
        >
          {moduleGroups.map((group) => (
            <div className={clsx('mb-4', collapsed ? 'px-2' : 'px-3')} key={group.label}>
              {/* Group heading — hidden when collapsed */}
              {!collapsed && (
                <div className="mb-1 px-3 text-[11px] font-semibold uppercase tracking-wider text-gray-500">
                  {group.label}
                </div>
              )}

              {/* Separator in collapsed mode */}
              {collapsed && <div className="mb-2 border-t border-white/10" />}

              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const active =
                    pathname === item.href || pathname.startsWith(`${item.href}/`);

                  return (
                    <Link
                      className={clsx(
                        'group flex items-center rounded-md text-sm font-medium transition-colors',
                        collapsed ? 'h-10 w-10 justify-center' : 'h-9 gap-3 px-3',
                        active
                          ? 'bg-teal-600 text-white'
                          : 'text-gray-400 hover:bg-white/10 hover:text-white',
                      )}
                      href={item.href}
                      key={item.href}
                      onClick={onClose}
                      title={collapsed ? item.label : undefined}
                    >
                      <Icon
                        aria-hidden="true"
                        className={clsx(
                          'h-4 w-4 shrink-0',
                          active ? 'text-white' : 'text-gray-500 group-hover:text-white',
                        )}
                      />
                      {!collapsed && (
                        <span className="min-w-0 flex-1 truncate">{item.label}</span>
                      )}
                      {!collapsed && active && (
                        <ChevronRight aria-hidden="true" className="h-3.5 w-3.5 text-teal-200" />
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* ── Footer ─────────────────────────────────────────── */}
        <div
          className={clsx(
            'shrink-0 border-t border-white/10',
            collapsed
              ? 'flex flex-col items-center gap-2 px-2 py-3'
              : 'flex items-center gap-2 px-4 py-3',
          )}
        >
          <Link
            aria-label="Settings"
            className={clsx(
              'flex items-center rounded-md text-gray-400 transition-colors hover:bg-white/10 hover:text-white',
              collapsed
                ? 'h-10 w-10 justify-center'
                : 'h-9 flex-1 gap-3 px-3 text-sm font-medium',
            )}
            href="/settings"
            onClick={onClose}
            title={collapsed ? 'Settings' : undefined}
          >
            <Settings aria-hidden="true" className="h-4 w-4 shrink-0" />
            {!collapsed && <span>Settings</span>}
          </Link>
        </div>
      </aside>
    </>
  );
}

'use client';

import Link from 'next/link';
import { Bell, ChevronDown, LogOut, Menu, Search, User } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { fetchNotifications, markNotificationRead } from '@/lib/api/endpoints';
import type { NotificationItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function getInitials(firstName: string, lastName: string, email: string): string {
  if (firstName || lastName) {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  }
  return (email.charAt(0) ?? 'U').toUpperCase();
}

type TopbarProps = {
  onMenuClick: () => void;
  pageTitle?: string;
};

export function Topbar({ onMenuClick, pageTitle }: TopbarProps) {
  const { tokens, user, logout } = useAuth();

  // Notification state
  const [notifOpen, setNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const notifRef = useRef<HTMLDivElement>(null);

  // User dropdown state
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Fetch unread notifications
  useEffect(() => {
    if (!tokens?.access) return;
    fetchNotifications(tokens.access)
      .then((response) => setNotifications(response.results))
      .catch(() => setNotifications([]));
  }, [tokens?.access]);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClick(event: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setNotifOpen(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  async function markRead(notification: NotificationItem) {
    if (!tokens?.access || notification.read_at) return;
    const updated = await markNotificationRead(tokens.access, notification.id);
    setNotifications((current) =>
      current.map((item) => (item.id === updated.id ? updated : item)),
    );
  }

  async function markAllRead() {
    const unreadItems = notifications.filter((n) => !n.read_at);
    for (const notification of unreadItems) {
      await markRead(notification);
    }
  }

  const unreadCount = notifications.filter((n) => !n.read_at).length;

  const firstName = user?.first_name ?? '';
  const lastName = user?.last_name ?? '';
  const email = user?.email ?? '';
  const displayName = user?.full_name ?? email;
  const initials = getInitials(firstName, lastName, email);

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-gray-200 bg-white px-4">
      {/* Mobile hamburger */}
      <button
        aria-label="Open navigation"
        className="inline-flex h-9 w-9 items-center justify-center rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-900 md:hidden"
        onClick={onMenuClick}
        type="button"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Page title */}
      {pageTitle && (
        <span className="hidden text-sm font-semibold text-gray-900 md:block">{pageTitle}</span>
      )}

      {/* Global search */}
      <div className="relative ml-2 hidden max-w-sm flex-1 md:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          aria-label="Search productions"
          className="h-9 w-full rounded-md border border-gray-200 bg-gray-50 pl-9 pr-3 text-sm text-gray-900 placeholder:text-gray-500 focus:border-teal-600 focus:bg-white focus:outline-none"
          placeholder="Search productions..."
          readOnly
          type="search"
        />
      </div>

      {/* Right-hand controls */}
      <div className="ml-auto flex items-center gap-1">
        {/* Notification bell */}
        <div className="relative" ref={notifRef}>
          <button
            aria-label={`Notifications${unreadCount ? `, ${unreadCount} unread` : ''}`}
            className="relative inline-flex h-9 w-9 items-center justify-center rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-900"
            onClick={() => {
              setNotifOpen((v) => !v);
              setUserMenuOpen(false);
            }}
            type="button"
          >
            <Bell className="h-4 w-4" />
            {unreadCount > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-teal-600 px-1 text-[10px] font-bold leading-none text-white">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </button>

          {notifOpen && (
            <div className="absolute right-0 top-11 z-50 w-[min(22rem,calc(100vw-1rem))] rounded-lg border border-gray-200 bg-white shadow-lg">
              {/* Panel header */}
              <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
                <div>
                  <p className="text-sm font-semibold text-gray-900">Notifications</p>
                  <p className="text-xs text-gray-500">
                    {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up'}
                  </p>
                </div>
                {unreadCount > 0 && (
                  <button
                    className="rounded-md px-2 py-1 text-xs font-semibold text-teal-700 hover:bg-teal-50"
                    onClick={markAllRead}
                    type="button"
                  >
                    Mark all read
                  </button>
                )}
              </div>

              {/* Notification list */}
              <div
                className="max-h-80 divide-y divide-gray-100 overflow-y-auto"
                style={{ scrollbarWidth: 'thin' }}
              >
                {notifications.length === 0 ? (
                  <div className="px-4 py-8 text-center text-sm text-gray-500">
                    No notifications
                  </div>
                ) : (
                  notifications.slice(0, 10).map((notification) => (
                    <button
                      className="block w-full px-4 py-3 text-left hover:bg-gray-50"
                      key={notification.id}
                      onClick={() => markRead(notification)}
                      type="button"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="min-w-0 truncate text-sm font-medium text-gray-900">
                          {notification.title}
                        </span>
                        {!notification.read_at && (
                          <span className="mt-0.5 shrink-0 rounded-full bg-teal-600 px-2 py-0.5 text-[10px] font-bold text-white">
                            New
                          </span>
                        )}
                      </div>
                      <p className="mt-0.5 line-clamp-2 text-xs text-gray-500">
                        {notification.message ||
                          notification.department_name ||
                          'StageOS notification'}
                      </p>
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User avatar + dropdown */}
        <div className="relative" ref={userMenuRef}>
          <button
            aria-label="Account menu"
            className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-gray-100"
            onClick={() => {
              setUserMenuOpen((v) => !v);
              setNotifOpen(false);
            }}
            type="button"
          >
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-teal-600 text-xs font-bold text-white">
              {initials}
            </span>
            <span className="hidden max-w-[10rem] truncate font-medium text-gray-700 lg:block">
              {displayName}
            </span>
            <ChevronDown className="hidden h-3.5 w-3.5 text-gray-400 lg:block" />
          </button>

          {userMenuOpen && (
            <div className="absolute right-0 top-11 z-50 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
              <Link
                className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                href="/settings/profile"
                onClick={() => setUserMenuOpen(false)}
              >
                <User className="h-4 w-4 text-gray-400" />
                My Profile
              </Link>
              <hr className="my-1 border-gray-100" />
              <button
                className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                onClick={() => {
                  setUserMenuOpen(false);
                  logout();
                }}
                type="button"
              >
                <LogOut className="h-4 w-4 text-gray-400" />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

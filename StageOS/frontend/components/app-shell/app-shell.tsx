'use client';

import { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Sidebar } from './sidebar';
import { Topbar } from './topbar';

function readCollapsedFromStorage(): boolean {
  try {
    return localStorage.getItem('stageos-sidebar-collapsed') === '1';
  } catch {
    return false;
  }
}

type AppShellProps = {
  children: React.ReactNode;
  pageTitle?: string;
};

export function AppShell({ children, pageTitle }: AppShellProps) {
  // Mobile drawer open state
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Desktop collapsed state — initialised from localStorage
  const [collapsed, setCollapsed] = useState(false);

  // Read persisted collapsed state after mount (avoids SSR mismatch)
  useEffect(() => {
    setCollapsed(readCollapsedFromStorage());
  }, []);

  function handleCollapsedChange(next: boolean) {
    setCollapsed(next);
    // Sidebar also persists, but we mirror here so layout reacts immediately
    try {
      localStorage.setItem('stageos-sidebar-collapsed', next ? '1' : '0');
    } catch {
      // ignore
    }
  }

  return (
    <ProtectedRoute>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:rounded-md focus:bg-teal-600 focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-white"
      >
        Skip to main content
      </a>
      {/*
        Layout:
          [Sidebar (fixed left on mobile / static column on desktop)]
          [Main column]
            [Topbar (sticky)]
            [Page content (scrollable)]
      */}
      <div className="flex min-h-screen bg-gray-50 text-gray-900">
        {/* Sidebar */}
        <Sidebar
          collapsed={collapsed}
          onClose={() => setSidebarOpen(false)}
          onCollapsedChange={handleCollapsedChange}
          open={sidebarOpen}
        />

        {/* Main content column */}
        <div
          className={[
            'flex min-w-0 flex-1 flex-col',
            // On desktop, add left margin matching sidebar width so content
            // isn't hidden behind the fixed sidebar on mobile.
            // (Sidebar is static on desktop so no margin needed there — flex handles it.)
          ].join(' ')}
        >
          {/* Topbar */}
          <Topbar
            onMenuClick={() => setSidebarOpen(true)}
            pageTitle={pageTitle}
          />

          {/* Scrollable page area */}
          <main id="main-content" className="flex-1 overflow-x-hidden px-4 py-6 sm:px-6 md:px-8">
            <div className="mx-auto w-full max-w-[1500px]">{children}</div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}

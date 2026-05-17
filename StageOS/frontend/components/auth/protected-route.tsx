'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useAuth } from '@/lib/auth/auth-provider';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { status } = useAuth();

  useEffect(() => {
    if (status === 'anonymous') {
      router.replace('/login');
    }
  }, [router, status]);

  if (status === 'loading') {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50 px-6">
        <div className="text-sm font-medium text-slate-600">Loading StageOS</div>
      </main>
    );
  }

  if (status !== 'authenticated') {
    return null;
  }

  return children;
}

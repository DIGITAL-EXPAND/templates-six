'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowRight, LockKeyhole, ShieldCheck } from 'lucide-react';
import { ApiError } from '@/lib/api/client';
import { useAuth } from '@/lib/auth/auth-provider';

export default function LoginPage() {
  const router = useRouter();
  const { login, status } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (status === 'authenticated') {
      router.replace('/dashboard');
    }
  }, [router, status]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await login(email, password);
      router.replace('/dashboard');
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError('The email or password is incorrect.');
      } else {
        setError('Sign in failed. Check the API connection and try again.');
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-slate-950 lg:grid-cols-[minmax(0,1fr)_520px]">
      <section className="hidden bg-[url('https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?auto=format&fit=crop&w=1800&q=80')] bg-cover bg-center lg:block">
        <div className="flex h-full flex-col justify-between bg-slate-950/62 p-12 text-white">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-md bg-teal-400 text-sm font-black text-slate-950">SO</div>
            <div>
              <div className="text-lg font-bold leading-5">StageOS</div>
              <div className="text-xs font-semibold text-slate-300">Theatre operating control</div>
            </div>
          </div>
          <div className="max-w-3xl">
            <p className="mb-3 text-sm font-bold uppercase tracking-normal text-teal-200">
              Intake to audit trail
            </p>
            <h1 className="text-5xl font-black tracking-normal xl:text-6xl">
              Live delivery command for venues, teams, evidence, and risk.
            </h1>
            <div className="mt-8 grid gap-3 text-sm font-semibold text-slate-200 xl:grid-cols-3">
              <div className="border-l-2 border-teal-300 pl-3">Role-aware dashboards</div>
              <div className="border-l-2 border-teal-300 pl-3">Evidence-backed delivery</div>
              <div className="border-l-2 border-teal-300 pl-3">Calendar and audit controls</div>
            </div>
          </div>
        </div>
      </section>
      <section className="flex items-center justify-center bg-slate-100 px-5 py-10">
        <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-2xl shadow-slate-950/10">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-md bg-slate-950 text-white">
              <LockKeyhole className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xl font-black text-slate-950">Sign in</div>
              <div className="text-sm font-medium text-slate-600">Use your StageOS account</div>
            </div>
          </div>
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="email">
                Email
              </label>
              <input
                autoComplete="email"
                className="h-11 w-full rounded-md border border-slate-300 bg-slate-50 px-3 text-slate-950 outline-none hover:border-slate-400 focus:border-teal-600 focus:bg-white"
                id="email"
                onChange={(event) => setEmail(event.target.value)}
                required
                type="email"
                value={email}
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="password">
                Password
              </label>
              <input
                autoComplete="current-password"
                className="h-11 w-full rounded-md border border-slate-300 bg-slate-50 px-3 text-slate-950 outline-none hover:border-slate-400 focus:border-teal-600 focus:bg-white"
                id="password"
                onChange={(event) => setPassword(event.target.value)}
                required
                type="password"
                value={password}
              />
            </div>
            {error ? (
              <div className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">
                {error}
              </div>
            ) : null}
            <button
              className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-teal-700 px-4 text-sm font-black text-white shadow-sm hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={submitting || status === 'loading'}
              type="submit"
            >
              {submitting ? 'Signing in' : 'Sign in securely'}
              <ArrowRight className="h-4 w-4" />
            </button>
            <div className="text-right">
              <Link href="/forgot-password" className="text-sm text-gray-500 hover:text-gray-700">
                Forgot password?
              </Link>
            </div>
          </form>
          <div className="mt-5 flex items-start gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold leading-5 text-slate-600">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-teal-700" />
            Access is controlled by your organisation, department and authority level.
          </div>
        </div>
      </section>
    </main>
  );
}

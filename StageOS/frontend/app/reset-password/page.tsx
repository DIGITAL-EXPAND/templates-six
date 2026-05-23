'use client';

import { FormEvent, useState, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { ArrowRight, LockKeyhole } from 'lucide-react';

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  if (!token) {
    return (
      <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800">
        Invalid or expired reset link.{' '}
        <Link href="/forgot-password" className="font-bold underline">
          Request a new one.
        </Link>
      </div>
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');

    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }

    setSubmitting(true);

    try {
      const res = await fetch('/api/v1/accounts/password-reset/confirm/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError((data as { detail?: string }).detail ?? 'Reset failed. The link may have expired.');
        return;
      }

      setSuccess(true);
    } catch {
      setError('Unable to connect. Check your network and try again.');
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <div className="space-y-5">
        <div className="rounded-md border border-teal-200 bg-teal-50 px-4 py-3 text-sm font-medium text-teal-800">
          Password reset successfully.
        </div>
        <Link
          href="/login"
          className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-teal-700 px-4 text-sm font-black text-white shadow-sm hover:bg-teal-800"
        >
          Sign in with new password
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      <div>
        <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="password">
          New Password
        </label>
        <input
          autoComplete="new-password"
          className="h-11 w-full rounded-md border border-slate-300 bg-slate-50 px-3 text-slate-950 outline-none hover:border-slate-400 focus:border-teal-600 focus:bg-white"
          id="password"
          onChange={(event) => setPassword(event.target.value)}
          required
          type="password"
          value={password}
        />
      </div>
      <div>
        <label className="mb-2 block text-sm font-bold text-slate-800" htmlFor="confirm">
          Confirm Password
        </label>
        <input
          autoComplete="new-password"
          className="h-11 w-full rounded-md border border-slate-300 bg-slate-50 px-3 text-slate-950 outline-none hover:border-slate-400 focus:border-teal-600 focus:bg-white"
          id="confirm"
          onChange={(event) => setConfirm(event.target.value)}
          required
          type="password"
          value={confirm}
        />
      </div>

      {error ? (
        <div className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">
          {error}
        </div>
      ) : null}

      <button
        className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-teal-700 px-4 text-sm font-black text-white shadow-sm hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        disabled={submitting}
        type="submit"
      >
        {submitting ? 'Resetting…' : 'Reset Password'}
        <ArrowRight className="h-4 w-4" />
      </button>

      <div className="text-right">
        <Link href="/login" className="text-sm text-slate-500 hover:text-slate-700">
          Back to sign in
        </Link>
      </div>
    </form>
  );
}

export default function ResetPasswordPage() {
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
              Account recovery
            </p>
            <h1 className="text-5xl font-black tracking-normal xl:text-6xl">
              Choose a new password to restore access.
            </h1>
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
              <div className="text-xl font-black text-slate-950">Reset password</div>
              <div className="text-sm font-medium text-slate-600">Set your new password</div>
            </div>
          </div>
          <Suspense fallback={<div className="text-sm text-slate-500">Loading…</div>}>
            <ResetPasswordForm />
          </Suspense>
        </div>
      </section>
    </main>
  );
}

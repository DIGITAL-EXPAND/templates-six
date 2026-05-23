'use client';

import { FormEvent, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, LockKeyhole } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const res = await fetch('/api/v1/accounts/password-reset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError((data as { detail?: string }).detail ?? 'Something went wrong. Please try again.');
        return;
      }

      setSuccess(true);
    } catch {
      setError('Unable to connect. Check your network and try again.');
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
              Account recovery
            </p>
            <h1 className="text-5xl font-black tracking-normal xl:text-6xl">
              Reset your password to regain access.
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
              <div className="text-xl font-black text-slate-950">Forgot password</div>
              <div className="text-sm font-medium text-slate-600">Enter your account email</div>
            </div>
          </div>

          {success ? (
            <div className="space-y-5">
              <div className="rounded-md border border-teal-200 bg-teal-50 px-4 py-3 text-sm font-medium text-teal-800">
                If this email is registered, a reset link has been sent to your inbox.
              </div>
              <Link
                href="/login"
                className="block text-center text-sm font-semibold text-slate-600 hover:text-slate-900"
              >
                Back to sign in
              </Link>
            </div>
          ) : (
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
                {submitting ? 'Sending…' : 'Send Reset Link'}
                <ArrowRight className="h-4 w-4" />
              </button>

              <div className="text-right">
                <Link href="/login" className="text-sm text-slate-500 hover:text-slate-700">
                  Back to sign in
                </Link>
              </div>
            </form>
          )}
        </div>
      </section>
    </main>
  );
}

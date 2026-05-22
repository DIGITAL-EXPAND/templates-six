'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { useAuth } from '@/lib/auth/auth-provider';
import {
  fetchTrialBalance,
  fetchGLJournals,
  postGLJournal,
  fetchDeferredIncome,
  recogniseDeferredIncome,
} from '@/lib/api/endpoints';
import type { GLJournalEntry, DeferredIncome } from '@/lib/api/types';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

type TrialBalanceLine = {
  account_code: string;
  account_name: string;
  category: string;
  total_debit: number;
  total_credit: number;
  net: number;
};

function zar(val: number | string) {
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

type Tab = 'trial_balance' | 'journals';

export default function GLPage() {
  const { tokens } = useAuth();
  const [tab, setTab] = useState<Tab>('trial_balance');

  // Trial Balance state
  const [fy, setFy] = useState('2025/2026');
  const [fyInput, setFyInput] = useState('2025/2026');
  const [trialBalance, setTrialBalance] = useState<TrialBalanceLine[] | null>(null);
  const [tbLoading, setTbLoading] = useState(false);
  const [tbError, setTbError] = useState<string | null>(null);

  // Journal state
  const [journals, setJournals] = useState<GLJournalEntry[]>([]);
  const [jLoading, setJLoading] = useState(true);
  const [jError, setJError] = useState<string | null>(null);
  const [expandedJournal, setExpandedJournal] = useState<string | null>(null);
  const [postingId, setPostingId] = useState<string | null>(null);

  // Deferred income state
  const [deferred, setDeferred] = useState<DeferredIncome[]>([]);
  const [dLoading, setDLoading] = useState(true);
  const [dError, setDError] = useState<string | null>(null);
  const [recogniseId, setRecogniseId] = useState<string | null>(null);
  const [recogniseAmount, setRecogniseAmount] = useState('');
  const [recognising, setRecognising] = useState(false);

  const token = tokens?.access ?? '';

  // Load journals on mount
  useEffect(() => {
    if (!token) return;
    setJLoading(true);
    fetchGLJournals(token)
      .then((d) => setJournals(d.results))
      .catch(() => setJError('Failed to load journals'))
      .finally(() => setJLoading(false));
  }, [token]);

  // Load deferred income on mount
  useEffect(() => {
    if (!token) return;
    setDLoading(true);
    fetchDeferredIncome(token)
      .then((d) => setDeferred(d.results))
      .catch(() => setDError('Failed to load deferred income'))
      .finally(() => setDLoading(false));
  }, [token]);

  function loadTrialBalance() {
    if (!token) return;
    setFy(fyInput);
    setTbLoading(true);
    setTbError(null);
    fetchTrialBalance(token, fyInput)
      .then((data) => setTrialBalance(data))
      .catch(() => setTbError('Failed to load trial balance'))
      .finally(() => setTbLoading(false));
  }

  async function handlePost(journalId: string) {
    if (!token) return;
    setPostingId(journalId);
    try {
      const updated = await postGLJournal(token, journalId);
      setJournals((prev) => prev.map((j) => (j.id === updated.id ? updated : j)));
    } catch {
      // silent
    } finally {
      setPostingId(null);
    }
  }

  async function handleRecognise(id: string) {
    if (!token || !recogniseAmount) return;
    setRecognising(true);
    try {
      const updated = await recogniseDeferredIncome(token, id, parseFloat(recogniseAmount));
      setDeferred((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
      setRecogniseId(null);
      setRecogniseAmount('');
    } catch {
      // silent
    } finally {
      setRecognising(false);
    }
  }

  // Group trial balance by category
  const tbByCategory: Record<string, TrialBalanceLine[]> = {};
  if (trialBalance) {
    for (const line of trialBalance) {
      if (!tbByCategory[line.category]) tbByCategory[line.category] = [];
      tbByCategory[line.category].push(line);
    }
  }

  const grandDebit = trialBalance?.reduce((s, l) => s + l.total_debit, 0) ?? 0;
  const grandCredit = trialBalance?.reduce((s, l) => s + l.total_credit, 0) ?? 0;
  const isBalanced = Math.abs(grandDebit - grandCredit) < 0.01;

  return (
    <AppShell>
      <PageHeader
        title="General Ledger"
        description="GRAP-compliant chart of accounts, journal entries, and deferred income"
      />

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {(['trial_balance', 'journals'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
              tab === t
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {t === 'trial_balance' ? 'Trial Balance' : 'Journal Entries'}
          </button>
        ))}
      </div>

      {/* Trial Balance Tab */}
      {tab === 'trial_balance' && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <div className="flex gap-3 mb-4 items-end">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Financial Year</label>
              <input
                className="border border-gray-300 rounded px-3 py-1.5 text-sm"
                value={fyInput}
                onChange={(e) => setFyInput(e.target.value)}
                placeholder="2025/2026"
              />
            </div>
            <button
              onClick={loadTrialBalance}
              disabled={tbLoading}
              className="px-4 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            >
              {tbLoading ? 'Loading…' : 'Load'}
            </button>
          </div>

          {tbError && <ErrorState message={tbError} />}

          {trialBalance && (
            <>
              {!isBalanced && (
                <div className="mb-3 p-3 bg-yellow-50 border border-yellow-300 rounded text-sm text-yellow-800">
                  Warning: Trial balance is out of balance — debits ({zar(grandDebit)}) ≠ credits ({zar(grandCredit)})
                </div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-500 border-b border-gray-200">
                      <th className="pb-2 pr-3">Code</th>
                      <th className="pb-2 pr-3">Account</th>
                      <th className="pb-2 pr-3 text-right">Debit</th>
                      <th className="pb-2 pr-3 text-right">Credit</th>
                      <th className="pb-2 text-right">Net</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(tbByCategory).map(([cat, lines]) => {
                      const catDebit = lines.reduce((s, l) => s + l.total_debit, 0);
                      const catCredit = lines.reduce((s, l) => s + l.total_credit, 0);
                      const catNet = lines.reduce((s, l) => s + l.net, 0);
                      return (
                        <>
                          <tr key={`cat-${cat}`} className="bg-gray-50">
                            <td colSpan={5} className="py-1.5 px-2 font-semibold text-gray-700 text-xs uppercase tracking-wide">
                              {cat}
                            </td>
                          </tr>
                          {lines.map((line) => (
                            <tr key={line.account_code} className="border-b border-gray-100 hover:bg-gray-50">
                              <td className="py-1.5 pr-3 font-mono text-xs text-gray-500">{line.account_code}</td>
                              <td className="py-1.5 pr-3">{line.account_name}</td>
                              <td className="py-1.5 pr-3 text-right font-mono">{zar(line.total_debit)}</td>
                              <td className="py-1.5 pr-3 text-right font-mono">{zar(line.total_credit)}</td>
                              <td className={`py-1.5 text-right font-mono ${line.net < 0 ? 'text-red-600' : ''}`}>{zar(line.net)}</td>
                            </tr>
                          ))}
                          <tr key={`tot-${cat}`} className="border-b-2 border-gray-300 bg-gray-100">
                            <td colSpan={2} className="py-1.5 pr-3 font-semibold text-xs">Category Total</td>
                            <td className="py-1.5 pr-3 text-right font-mono font-semibold">{zar(catDebit)}</td>
                            <td className="py-1.5 pr-3 text-right font-mono font-semibold">{zar(catCredit)}</td>
                            <td className={`py-1.5 text-right font-mono font-semibold ${catNet < 0 ? 'text-red-600' : ''}`}>{zar(catNet)}</td>
                          </tr>
                        </>
                      );
                    })}
                    <tr className="bg-blue-50 font-bold">
                      <td colSpan={2} className="py-2 pr-3">Grand Total</td>
                      <td className="py-2 pr-3 text-right font-mono">{zar(grandDebit)}</td>
                      <td className="py-2 pr-3 text-right font-mono">{zar(grandCredit)}</td>
                      <td className={`py-2 text-right font-mono ${!isBalanced ? 'text-red-600' : 'text-green-700'}`}>
                        {zar(grandDebit - grandCredit)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </>
          )}

          {!trialBalance && !tbLoading && !tbError && (
            <p className="text-sm text-gray-500">Select a financial year and click Load.</p>
          )}
        </div>
      )}

      {/* Journal Entries Tab */}
      {tab === 'journals' && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          {jLoading && <LoadingState />}
          {jError && <ErrorState message={jError} />}
          {!jLoading && !jError && journals.length === 0 && <EmptyState message="No journal entries found." />}
          {!jLoading && !jError && journals.length > 0 && (
            <div className="divide-y divide-gray-100">
              {journals.map((j) => (
                <div key={j.id}>
                  <button
                    className="w-full flex items-center gap-3 py-3 text-left hover:bg-gray-50 px-2 rounded"
                    onClick={() => setExpandedJournal(expandedJournal === j.id ? null : j.id)}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-mono text-sm font-semibold">{j.reference}</span>
                        <StatusBadge tone={j.is_posted ? 'good' : 'warning'}>
                          {j.is_posted ? 'Posted' : 'Unposted'}
                        </StatusBadge>
                        <StatusBadge tone={j.is_balanced ? 'good' : 'danger'}>
                          {j.is_balanced ? 'Balanced' : 'Unbalanced'}
                        </StatusBadge>
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5 truncate">{j.description}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-sm font-mono">{zar(j.total_debits)}</div>
                      <div className="text-xs text-gray-500">{formatDate(j.entry_date)} · P{j.period}</div>
                    </div>
                    {!j.is_posted && j.is_balanced && (
                      <button
                        onClick={(e) => { e.stopPropagation(); handlePost(j.id); }}
                        disabled={postingId === j.id}
                        className="ml-2 px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-50 shrink-0"
                      >
                        {postingId === j.id ? 'Posting…' : 'Post'}
                      </button>
                    )}
                  </button>
                  {expandedJournal === j.id && (
                    <div className="mx-2 mb-3 border border-gray-200 rounded overflow-x-auto">
                      <table className="w-full text-xs">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-1.5 text-left font-medium text-gray-500">Code</th>
                            <th className="px-3 py-1.5 text-left font-medium text-gray-500">Account</th>
                            <th className="px-3 py-1.5 text-right font-medium text-gray-500">Debit</th>
                            <th className="px-3 py-1.5 text-right font-medium text-gray-500">Credit</th>
                            <th className="px-3 py-1.5 text-left font-medium text-gray-500">Description</th>
                          </tr>
                        </thead>
                        <tbody>
                          {j.lines.map((line) => (
                            <tr key={line.id} className="border-t border-gray-100">
                              <td className="px-3 py-1.5 font-mono text-gray-500">{line.account_code}</td>
                              <td className="px-3 py-1.5">{line.account_name}</td>
                              <td className="px-3 py-1.5 text-right font-mono">{parseFloat(line.debit) > 0 ? zar(line.debit) : '—'}</td>
                              <td className="px-3 py-1.5 text-right font-mono">{parseFloat(line.credit) > 0 ? zar(line.credit) : '—'}</td>
                              <td className="px-3 py-1.5 text-gray-500">{line.description || '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Deferred Income — always visible */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="text-base font-semibold mb-4">Deferred Income (GRAP 23)</h2>
        {dLoading && <LoadingState />}
        {dError && <ErrorState message={dError} />}
        {!dLoading && !dError && deferred.length === 0 && <EmptyState message="No deferred income records." />}
        {!dLoading && !dError && deferred.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-200">
                  <th className="pb-2 pr-3">Grant</th>
                  <th className="pb-2 pr-3">Grantor</th>
                  <th className="pb-2 pr-3">Year</th>
                  <th className="pb-2 pr-3">Type</th>
                  <th className="pb-2 pr-3 text-right">Total</th>
                  <th className="pb-2 pr-3 text-right">Recognised</th>
                  <th className="pb-2 pr-3 text-right">Deferred</th>
                  <th className="pb-2 pr-3">Progress</th>
                  <th className="pb-2"></th>
                </tr>
              </thead>
              <tbody>
                {deferred.map((d) => {
                  const total = parseFloat(d.total_grant_amount) || 1;
                  const recognised = parseFloat(d.amount_recognised) || 0;
                  const pct = Math.min(100, Math.round((recognised / total) * 100));
                  return (
                    <>
                      <tr key={d.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-2 pr-3 font-medium">{d.grant_name}</td>
                        <td className="py-2 pr-3 text-gray-600">{d.grantor}</td>
                        <td className="py-2 pr-3 text-gray-600">{d.financial_year}</td>
                        <td className="py-2 pr-3">
                          <StatusBadge tone="info">{d.recognition_type}</StatusBadge>
                        </td>
                        <td className="py-2 pr-3 text-right font-mono">{zar(d.total_grant_amount)}</td>
                        <td className="py-2 pr-3 text-right font-mono">{zar(d.amount_recognised)}</td>
                        <td className="py-2 pr-3 text-right font-mono">{zar(d.amount_deferred)}</td>
                        <td className="py-2 pr-3">
                          <div className="flex items-center gap-2">
                            <div className="w-24 bg-gray-200 rounded-full h-1.5">
                              <div
                                className="bg-blue-500 h-1.5 rounded-full"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-500">{pct}%</span>
                          </div>
                        </td>
                        <td className="py-2">
                          {!d.is_fully_recognised && (
                            <button
                              onClick={() => {
                                setRecogniseId(recogniseId === d.id ? null : d.id);
                                setRecogniseAmount('');
                              }}
                              className="text-xs px-2 py-1 border border-blue-500 text-blue-600 rounded hover:bg-blue-50"
                            >
                              Recognise
                            </button>
                          )}
                          {d.is_fully_recognised && (
                            <StatusBadge tone="good">Done</StatusBadge>
                          )}
                        </td>
                      </tr>
                      {recogniseId === d.id && (
                        <tr key={`recognise-${d.id}`}>
                          <td colSpan={9} className="pb-3 px-2">
                            <div className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded p-3">
                              <label className="text-sm text-gray-700">Amount to recognise:</label>
                              <input
                                type="number"
                                value={recogniseAmount}
                                onChange={(e) => setRecogniseAmount(e.target.value)}
                                className="border border-gray-300 rounded px-2 py-1 text-sm w-36"
                                placeholder="0.00"
                              />
                              <button
                                onClick={() => handleRecognise(d.id)}
                                disabled={recognising || !recogniseAmount}
                                className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
                              >
                                {recognising ? 'Saving…' : 'Confirm'}
                              </button>
                              <button
                                onClick={() => setRecogniseId(null)}
                                className="text-sm text-gray-500 hover:text-gray-700"
                              >
                                Cancel
                              </button>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppShell>
  );
}

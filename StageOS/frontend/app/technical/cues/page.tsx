'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchCueSheets, fetchCueLines, fetchOperatingContexts } from '@/lib/api/endpoints';
import type { CueSheet, CueLine, OperatingContextListItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function deptTone(dept: string): StatusTone {
  switch (dept) {
    case 'lx': return 'warning';
    case 'sq': return 'info';
    case 'fly': return 'neutral';
    case 'auto': return 'good';
    case 'proj': return 'info';
    case 'pyro': return 'danger';
    case 'sm': return 'neutral';
    default: return 'neutral';
  }
}

export default function CueSheetsPage() {
  const { tokens } = useAuth();
  const [contexts, setContexts] = useState<OperatingContextListItem[]>([]);
  const [selectedContext, setSelectedContext] = useState<string>('');
  const [sheets, setSheets] = useState<CueSheet[]>([]);
  const [expandedSheet, setExpandedSheet] = useState<string | null>(null);
  const [sheetLines, setSheetLines] = useState<Record<string, CueLine[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingLines, setLoadingLines] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!tokens?.access) return;
    fetchOperatingContexts(tokens.access)
      .then((r) => setContexts(r.results))
      .catch(() => setError('Failed to load productions'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  useEffect(() => {
    if (!tokens?.access) return;
    setLoading(true);
    fetchCueSheets(tokens.access, selectedContext || undefined)
      .then((r) => setSheets(r.results))
      .catch(() => setError('Failed to load cue sheets'))
      .finally(() => setLoading(false));
  }, [tokens?.access, selectedContext]);

  async function handleExpandSheet(sheetId: string) {
    if (expandedSheet === sheetId) {
      setExpandedSheet(null);
      return;
    }
    setExpandedSheet(sheetId);
    if (sheetLines[sheetId]) return;
    if (!tokens?.access) return;
    setLoadingLines((prev) => ({ ...prev, [sheetId]: true }));
    try {
      const r = await fetchCueLines(tokens.access, sheetId);
      setSheetLines((prev) => ({ ...prev, [sheetId]: r.results }));
    } catch {
      // ignore
    } finally {
      setLoadingLines((prev) => ({ ...prev, [sheetId]: false }));
    }
  }

  if (loading && contexts.length === 0) return <AppShell><LoadingState label="Loading cue sheets…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  return (
    <AppShell>
      <PageHeader
        title="Cue Sheets"
        description="Production cue sheets by department"
      />

      <div className="px-4 pb-6 space-y-4">
        {/* Production selector */}
        <div className="flex items-center gap-3">
          <label className="text-sm font-medium text-gray-700">Production:</label>
          <select
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm"
            value={selectedContext}
            onChange={(e) => setSelectedContext(e.target.value)}
          >
            <option value="">All Productions</option>
            {contexts.map((c) => (
              <option key={c.id} value={c.id}>{c.title}</option>
            ))}
          </select>
        </div>

        {loading && <LoadingState label="Loading cue sheets…" />}

        {!loading && sheets.length === 0 && (
          <EmptyState title="No cue sheets" description="No cue sheets found for the selected production." />
        )}

        {!loading && sheets.length > 0 && (
          <div className="space-y-2">
            {sheets.map((sheet) => (
              <div key={sheet.id} className="rounded-lg border border-gray-200 bg-white shadow-sm overflow-hidden">
                {/* Sheet header row */}
                <button
                  className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 transition-colors"
                  onClick={() => handleExpandSheet(sheet.id)}
                >
                  <div className="flex items-center gap-3">
                    <span className="font-medium text-gray-900">{sheet.title}</span>
                    <StatusBadge tone={deptTone(sheet.department)}>{sheet.department.toUpperCase()}</StatusBadge>
                    {sheet.is_master && <StatusBadge tone="good">Master</StatusBadge>}
                    <span className="text-xs text-gray-500">v{sheet.version}</span>
                  </div>
                  <span className="text-gray-400 text-sm">{expandedSheet === sheet.id ? '▲' : '▼'}</span>
                </button>

                {/* Expanded cue lines */}
                {expandedSheet === sheet.id && (
                  <div className="border-t border-gray-200">
                    {loadingLines[sheet.id] ? (
                      <div className="px-4 py-3 text-sm text-gray-500">Loading cues…</div>
                    ) : !sheetLines[sheet.id] || sheetLines[sheet.id].length === 0 ? (
                      <div className="px-4 py-3 text-sm text-gray-500">No cue lines found.</div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="min-w-full text-sm">
                          <thead>
                            <tr className="bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                              <th className="px-4 py-2">Cue #</th>
                              <th className="px-4 py-2">Page Ref</th>
                              <th className="px-4 py-2">Action</th>
                              <th className="px-4 py-2">Standby Note</th>
                              <th className="px-4 py-2">Follow On</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {[...sheetLines[sheet.id]]
                              .sort((a, b) => a.order - b.order)
                              .map((line) => (
                                <tr key={line.id} className="hover:bg-gray-50">
                                  <td className="px-4 py-2 font-mono text-xs font-semibold text-gray-700">{line.cue_number}</td>
                                  <td className="px-4 py-2 text-gray-600">{line.page_ref || '—'}</td>
                                  <td className="px-4 py-2 font-medium text-gray-900">{line.action}</td>
                                  <td className="px-4 py-2 text-gray-500 italic">{line.standby_note || '—'}</td>
                                  <td className="px-4 py-2 text-center">{line.follow_on ? <span className="text-blue-600 font-bold">→</span> : ''}</td>
                                </tr>
                              ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}

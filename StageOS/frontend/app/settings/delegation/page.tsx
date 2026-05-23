'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchDelegationMatrices, fetchDelegationMatrixRules } from '@/lib/api/endpoints';
import type { DelegationMatrix, DelegationRule } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function zar(val: string | number) {
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

const CATEGORY_ORDER = ['Procurement', 'Contracts', 'HR', 'Finance', 'Operations', 'Legal'];

function groupRules(rules: DelegationRule[]): Record<string, DelegationRule[]> {
  const grouped: Record<string, DelegationRule[]> = {};
  for (const rule of rules) {
    const cat = rule.category || 'Other';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(rule);
  }
  return grouped;
}

function sortedCategories(grouped: Record<string, DelegationRule[]>): string[] {
  const known = CATEGORY_ORDER.filter((c) => grouped[c]);
  const other = Object.keys(grouped).filter((c) => !CATEGORY_ORDER.includes(c)).sort();
  return [...known, ...other];
}

export default function DelegationMatrixPage() {
  const { tokens } = useAuth();
  const [matrices, setMatrices] = useState<DelegationMatrix[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rulesMap, setRulesMap] = useState<Record<string, DelegationRule[]>>({});
  const [rulesLoading, setRulesLoading] = useState<Record<string, boolean>>({});
  const [expandedId, setExpandedId] = useState<string | null>(null);

  function loadRules(matrixId: string, token: string) {
    if (rulesMap[matrixId]) return;
    setRulesLoading((prev) => ({ ...prev, [matrixId]: true }));
    fetchDelegationMatrixRules(token, matrixId)
      .then((res) => setRulesMap((prev) => ({ ...prev, [matrixId]: Array.isArray(res) ? res : (res as { results: DelegationRule[] }).results })))
      .catch(() => setRulesMap((prev) => ({ ...prev, [matrixId]: [] })))
      .finally(() => setRulesLoading((prev) => ({ ...prev, [matrixId]: false })));
  }

  useEffect(() => {
    if (!tokens?.access) return;
    const token = tokens.access;
    fetchDelegationMatrices(token)
      .then((res) => {
        setMatrices(res.results);
        // Auto-expand the active matrix
        const active = res.results.find((m) => m.is_active);
        if (active) {
          setExpandedId(active.id);
          loadRules(active.id, token);
        }
      })
      .catch(() => setError('Failed to load delegation matrices'))
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tokens?.access]);

  function toggleExpand(matrixId: string) {
    if (expandedId === matrixId) {
      setExpandedId(null);
    } else {
      setExpandedId(matrixId);
      if (tokens?.access) loadRules(matrixId, tokens.access);
    }
  }

  if (loading) return <AppShell><LoadingState label="Loading delegation matrix…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  return (
    <AppShell>
      <PageHeader
        title="Delegation of Authority Matrix"
        description="Approved limits and authority levels"
      />

      {matrices.length === 0 ? (
        <EmptyState title="No delegation matrices configured." />
      ) : (
        <div className="space-y-4 p-4">
          {matrices.map((matrix) => {
            const isExpanded = expandedId === matrix.id;
            const rules = rulesMap[matrix.id] ?? [];
            const isLoadingRules = rulesLoading[matrix.id];
            const grouped = groupRules(rules);
            const categories = sortedCategories(grouped);

            return (
              <div key={matrix.id} className="rounded-lg border border-gray-200 bg-white shadow-sm">
                {/* Matrix header */}
                <div
                  className="flex cursor-pointer items-center justify-between p-5 select-none"
                  onClick={() => toggleExpand(matrix.id)}
                >
                  <div className="flex items-center gap-4 flex-wrap">
                    <h2 className="text-base font-semibold text-gray-900">{matrix.name}</h2>
                    <span className="text-sm text-gray-500">v{matrix.version}</span>
                    <span className="text-sm text-gray-500">Effective: {matrix.effective_date}</span>
                    {matrix.is_active && (
                      <StatusBadge tone="good">Active</StatusBadge>
                    )}
                  </div>
                  <span className="text-sm text-gray-400">{isExpanded ? '▲' : '▼'}</span>
                </div>

                {/* Rules table */}
                {isExpanded && (
                  <div className="border-t border-gray-100">
                    {isLoadingRules ? (
                      <div className="p-5">
                        <LoadingState label="Loading rules…" />
                      </div>
                    ) : rules.length === 0 ? (
                      <div className="p-5">
                        <EmptyState title="No rules defined for this matrix." />
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="min-w-full text-sm">
                          <thead>
                            <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                              <th className="px-4 py-3">Action</th>
                              <th className="px-4 py-3">Delegated To</th>
                              <th className="px-4 py-3">Threshold</th>
                              <th className="px-4 py-3">Countersign</th>
                              <th className="px-4 py-3">Board Approval</th>
                            </tr>
                          </thead>
                          <tbody>
                            {categories.map((cat) => (
                              <>
                                <tr key={`cat-${cat}`} className="bg-gray-100">
                                  <td
                                    colSpan={5}
                                    className="px-4 py-2 text-xs font-bold uppercase tracking-wider text-gray-600"
                                  >
                                    {cat}
                                  </td>
                                </tr>
                                {(grouped[cat] ?? []).map((rule) => (
                                  <tr key={rule.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                    <td className="px-4 py-3 text-gray-900">{rule.action_description}</td>
                                    <td className="px-4 py-3 text-gray-700">{rule.delegated_to}</td>
                                    <td className="px-4 py-3 text-gray-700 whitespace-nowrap">
                                      {rule.threshold_amount !== null
                                        ? zar(rule.threshold_amount)
                                        : <span className="text-gray-400 italic">No limit</span>}
                                    </td>
                                    <td className="px-4 py-3">
                                      {rule.requires_countersign ? (
                                        <span className="text-gray-800">{rule.countersign_level || 'Yes'}</span>
                                      ) : (
                                        <span className="text-gray-400">—</span>
                                      )}
                                    </td>
                                    <td className="px-4 py-3">
                                      {rule.requires_board_approval ? (
                                        <StatusBadge tone="warning">Required</StatusBadge>
                                      ) : (
                                        <span className="text-gray-400">—</span>
                                      )}
                                    </td>
                                  </tr>
                                ))}
                              </>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}

'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchProps, fetchWardrobe } from '@/lib/api/endpoints';
import type { PropsItem, WardrobeItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function conditionTone(c: string): StatusTone {
  switch (c) {
    case 'excellent': return 'good';
    case 'good': return 'good';
    case 'fair': return 'warning';
    case 'poor': return 'danger';
    case 'written_off': return 'neutral';
    default: return 'neutral';
  }
}

type Tab = 'props' | 'wardrobe';

export default function PropsWardrobePage() {
  const { tokens } = useAuth();
  const [tab, setTab] = useState<Tab>('props');
  const [props, setProps] = useState<PropsItem[]>([]);
  const [wardrobe, setWardrobe] = useState<WardrobeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.all([
      fetchProps(tokens.access).then((r) => setProps(r.results)),
      fetchWardrobe(tokens.access).then((r) => setWardrobe(r.results)),
    ])
      .catch(() => setError('Failed to load props and wardrobe data'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  if (loading) return <AppShell><LoadingState label="Loading props and wardrobe…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  const totalProps = props.length;
  const availableProps = props.filter((p) => p.is_available).length;
  const hiredProps = props.filter((p) => p.is_hired).length;
  const productionProps = props.filter((p) => p.current_production).length;

  const tabs: { key: Tab; label: string }[] = [
    { key: 'props', label: 'Props' },
    { key: 'wardrobe', label: 'Wardrobe' },
  ];

  return (
    <AppShell>
      <PageHeader
        title="Props & Wardrobe"
        description="Manage props inventory and wardrobe items"
      />

      {/* Tab bar */}
      <div className="px-4 mb-4">
        <div className="flex gap-1 border-b border-gray-200">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="px-4 pb-6">

        {/* PROPS TAB */}
        {tab === 'props' && (
          <div className="space-y-4">
            {/* Summary strip */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Total</p>
                <p className="mt-1 text-2xl font-bold text-gray-900">{totalProps}</p>
              </div>
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 shadow-sm">
                <p className="text-xs text-emerald-600 uppercase tracking-wider">Available</p>
                <p className="mt-1 text-2xl font-bold text-emerald-700">{availableProps}</p>
              </div>
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 shadow-sm">
                <p className="text-xs text-amber-600 uppercase tracking-wider">Hired</p>
                <p className="mt-1 text-2xl font-bold text-amber-700">{hiredProps}</p>
              </div>
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 shadow-sm">
                <p className="text-xs text-blue-600 uppercase tracking-wider">In Production</p>
                <p className="mt-1 text-2xl font-bold text-blue-700">{productionProps}</p>
              </div>
            </div>

            {props.length === 0 ? (
              <EmptyState title="No props" description="No props found in inventory." />
            ) : (
              <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <th className="px-4 py-3">Name</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Condition</th>
                      <th className="px-4 py-3">Storage</th>
                      <th className="px-4 py-3">Hired</th>
                      <th className="px-4 py-3">Available</th>
                      <th className="px-4 py-3">Production</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {props.map((p) => (
                      <tr key={p.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium text-gray-900">{p.name}</td>
                        <td className="px-4 py-3 text-gray-600 capitalize">{p.category.replace(/_/g, ' ')}</td>
                        <td className="px-4 py-3">
                          <StatusBadge tone={conditionTone(p.condition)}>{p.condition.replace(/_/g, ' ')}</StatusBadge>
                        </td>
                        <td className="px-4 py-3 text-gray-600">{p.storage_location || '—'}</td>
                        <td className="px-4 py-3 text-center">{p.is_hired ? '✓' : '—'}</td>
                        <td className="px-4 py-3">
                          <StatusBadge tone={p.is_available ? 'good' : 'neutral'}>
                            {p.is_available ? 'Available' : 'In Use'}
                          </StatusBadge>
                        </td>
                        <td className="px-4 py-3 text-gray-600 text-xs">{p.current_production ? p.current_production.substring(0, 20) + '…' : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* WARDROBE TAB */}
        {tab === 'wardrobe' && (
          <div>
            {wardrobe.length === 0 ? (
              <EmptyState title="No wardrobe items" description="No wardrobe items found." />
            ) : (
              <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                      <th className="px-4 py-3">Name</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Character</th>
                      <th className="px-4 py-3">Size</th>
                      <th className="px-4 py-3">Condition</th>
                      <th className="px-4 py-3">Hired</th>
                      <th className="px-4 py-3">Assigned To</th>
                      <th className="px-4 py-3">Production</th>
                      <th className="px-4 py-3">Cleaning</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {wardrobe.map((w) => (
                      <tr key={w.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium text-gray-900">{w.name}</td>
                        <td className="px-4 py-3 text-gray-600 capitalize">{w.category.replace(/_/g, ' ')}</td>
                        <td className="px-4 py-3 text-gray-600">{w.character || '—'}</td>
                        <td className="px-4 py-3 text-gray-600">{w.size || '—'}</td>
                        <td className="px-4 py-3">
                          <StatusBadge tone={conditionTone(w.condition)}>{w.condition.replace(/_/g, ' ')}</StatusBadge>
                        </td>
                        <td className="px-4 py-3 text-center">{w.is_hired ? '✓' : '—'}</td>
                        <td className="px-4 py-3 text-gray-600">{w.assigned_to_performer || '—'}</td>
                        <td className="px-4 py-3 text-gray-600 text-xs">{w.current_production ? w.current_production.substring(0, 20) + '…' : '—'}</td>
                        <td className="px-4 py-3 text-center">{w.cleaning_required ? '🧺' : ''}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}

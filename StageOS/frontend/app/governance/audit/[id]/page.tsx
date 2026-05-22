'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { use } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { useAuth } from '@/lib/auth/auth-provider';
import { fetchAGAuditPackage } from '@/lib/api/endpoints';
import type { AGAuditPackage } from '@/lib/api/types';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function completenessTone(pct: number): StatusTone {
  if (pct >= 90) return 'good';
  if (pct >= 60) return 'warning';
  return 'danger';
}

export default function AuditPackagePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { tokens } = useAuth();
  const [pkg, setPkg] = useState<AGAuditPackage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const token = tokens?.access ?? '';

  useEffect(() => {
    if (!token || !id) return;
    setLoading(true);
    fetchAGAuditPackage(token, id)
      .then((data) => setPkg(data))
      .catch(() => setError('Failed to load audit package.'))
      .finally(() => setLoading(false));
  }, [token, id]);

  return (
    <AppShell>
      <div className="flex items-center gap-3 mb-2">
        <Link href="/governance/audit" className="text-sm text-blue-600 hover:underline">
          ← Back to Audits
        </Link>
      </div>

      <PageHeader
        title="AG Audit Package"
        description={pkg ? `${pkg.audit_type} — ${pkg.financial_year}` : 'Evidence package detail'}
      />

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}

      {pkg && (
        <>
          {/* Completeness overview */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <div className="flex items-center gap-6">
              {/* Circle */}
              <div className="relative flex items-center justify-center w-24 h-24 shrink-0">
                <div
                  className="w-24 h-24 rounded-full flex items-center justify-center border-8"
                  style={{
                    borderColor: pkg.completeness_pct >= 90 ? '#22c55e' : pkg.completeness_pct >= 60 ? '#f59e0b' : '#ef4444',
                  }}
                >
                  <span className="text-xl font-bold">{pkg.completeness_pct}%</span>
                </div>
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <StatusBadge tone={completenessTone(pkg.completeness_pct)}>
                    {pkg.status.replace(/_/g, ' ')}
                  </StatusBadge>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500 text-xs">Total Items</div>
                    <div className="font-semibold">{pkg.total_evidence_items}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 text-xs">Provided</div>
                    <div className="font-semibold text-green-700">{pkg.provided}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 text-xs">Outstanding</div>
                    <div className="font-semibold text-red-600">{pkg.outstanding_count}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 text-xs">Generated</div>
                    <div className="font-semibold">{formatDate(pkg.generated_at)}</div>
                  </div>
                </div>
              </div>
              <button
                onClick={() => window.print()}
                className="shrink-0 px-4 py-2 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50"
              >
                Print Package
              </button>
            </div>
          </div>

          {/* Evidence by category */}
          <div className="space-y-4">
            {Object.entries(pkg.by_category).map(([category, catData]) => {
              const catPct = catData.total > 0 ? Math.round((catData.provided / catData.total) * 100) : 0;
              const outstanding = catData.items || [];
              return (
                <div key={category} className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <h3 className="font-semibold text-gray-900 capitalize">{category.replace(/_/g, ' ')}</h3>
                    <div className="flex items-center gap-2 flex-1">
                      <div className="flex-1 max-w-32 bg-gray-200 rounded-full h-2">
                        <div
                          className="h-2 rounded-full"
                          style={{
                            width: `${catPct}%`,
                            backgroundColor: catPct >= 90 ? '#22c55e' : catPct >= 60 ? '#f59e0b' : '#ef4444',
                          }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">{catData.provided}/{catData.total}</span>
                    </div>
                  </div>
                  {outstanding.length > 0 ? (
                    <div className="space-y-1.5">
                      <p className="text-xs text-gray-500 font-medium">Outstanding items:</p>
                      {outstanding.map((item) => (
                        <div key={item.id} className="flex items-center gap-3 text-sm bg-red-50 border border-red-100 rounded px-3 py-1.5">
                          <span className="font-mono text-xs text-red-700 shrink-0">{item.ag_query_ref}</span>
                          <span className="text-gray-700">{item.description}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-green-700 font-medium">All items provided for this category.</p>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </AppShell>
  );
}

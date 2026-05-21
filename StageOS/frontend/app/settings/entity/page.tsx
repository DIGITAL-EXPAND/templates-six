'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchEntityConfig } from '@/lib/api/endpoints';
import type { TenantEntityConfig } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function entityTypeTone(entityType: TenantEntityConfig['entity_type']): StatusTone {
  switch (entityType) {
    case 'pfma_schedule_3a': return 'info';
    case 'mfma_municipal': return 'warning';
    case 'section_21_npo': return 'neutral';
    case 'private_company': return 'neutral';
    default: return 'neutral';
  }
}

function entityTypeLabel(entityType: TenantEntityConfig['entity_type']): string {
  switch (entityType) {
    case 'pfma_schedule_3a': return 'PFMA Schedule 3A';
    case 'mfma_municipal': return 'MFMA Municipal';
    case 'section_21_npo': return 'Section 21 NPO';
    case 'private_company': return 'Private Company';
    default: return entityType;
  }
}

function BoolFlag({ value, label }: { value: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className={value ? 'text-green-600 font-bold' : 'text-gray-300'}>
        {value ? '✓' : '—'}
      </span>
      <span className="text-sm text-gray-700">{label}</span>
    </div>
  );
}

export default function EntityConfigPage() {
  const { tokens } = useAuth();
  const [config, setConfig] = useState<TenantEntityConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchEntityConfig(tokens.access)
      .then((res) => {
        setConfig(res.results?.[0] ?? null);
      })
      .catch(() => setError('Failed to load entity configuration'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  if (loading) return <AppShell><LoadingState label="Loading entity configuration…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  return (
    <AppShell>
      <PageHeader
        title="Entity Configuration"
        description="Public entity type and compliance framework settings"
      />

      {!config ? (
        <div className="px-4">
          <EmptyState
            title="Entity configuration not yet set up"
            description="Contact your system administrator to configure the entity type and compliance framework."
          />
        </div>
      ) : (
        <div className="px-4 pb-8 space-y-6">
          {/* Entity Type */}
          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Entity Type</h2>
            <StatusBadge tone={entityTypeTone(config.entity_type)}>
              {entityTypeLabel(config.entity_type)}
            </StatusBadge>
          </div>

          {/* Compliance Flags */}
          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Compliance Framework</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <BoolFlag value={config.auditor_general_client} label="Auditor General Client" />
              <BoolFlag value={config.pfma_applicable} label="PFMA Applicable" />
              <BoolFlag value={config.mfma_applicable} label="MFMA Applicable" />
              <BoolFlag value={config.grap_reporting} label="GRAP Reporting" />
              <BoolFlag value={config.treasury_reporting_required} label="Treasury Reporting Required" />
              <BoolFlag value={config.shareholder_compact_required} label="Shareholder Compact Required" />
              <BoolFlag value={config.delegation_framework_required} label="Delegation Framework Required" />
            </div>
          </div>

          {/* Authorities and Financial Year */}
          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Governance Details</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1">Executive Authority</div>
                <div className="text-sm text-gray-800">{config.executive_authority || '—'}</div>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1">Accounting Authority</div>
                <div className="text-sm text-gray-800">{config.accounting_authority || '—'}</div>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1">Financial Year End</div>
                <div className="text-sm text-gray-800">{config.financial_year_end || '—'}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}

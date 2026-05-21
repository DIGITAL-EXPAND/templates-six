'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchBoardMembers } from '@/lib/api/endpoints';
import type { BoardMemberProfile } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function memberStatusTone(status: string): StatusTone {
  switch (status) {
    case 'active': return 'good';
    case 'resigned':
    case 'removed': return 'danger';
    case 'term_expired': return 'neutral';
    default: return 'neutral';
  }
}

function daysUntil(iso: string | null | undefined): number | null {
  if (!iso) return null;
  return Math.ceil((new Date(iso).getTime() - Date.now()) / 86400000);
}

export default function BoardMembersPage() {
  const { tokens } = useAuth();
  const [members, setMembers] = useState<BoardMemberProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    fetchBoardMembers(tokens.access)
      .then((res) => setMembers(res.results))
      .catch(() => setError('Failed to load board members'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  if (loading) return <AppShell><LoadingState label="Loading board members…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  const activeCount = members.filter((m) => m.status === 'active').length;
  const expiringCount = members.filter((m) => {
    const days = daysUntil(m.term_end_date);
    return days !== null && days >= 0 && days <= 90;
  }).length;
  const declarationsCount = members.filter((m) => m.annual_declaration_submitted).length;
  const independentCount = members.filter((m) => m.is_independent).length;

  return (
    <AppShell>
      <PageHeader
        title="Board Member Profiles"
        description="Board composition, tenure tracking, and declaration status"
      />

      {/* Summary strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Active Members</div>
          <div className="text-2xl font-bold text-green-700">{activeCount}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Terms Expiring (90 days)</div>
          <div className="text-2xl font-bold text-yellow-600">{expiringCount}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Declarations Submitted</div>
          <div className="text-2xl font-bold text-blue-700">{declarationsCount}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Independent Members</div>
          <div className="text-2xl font-bold text-gray-900">{independentCount}</div>
        </div>
      </div>

      {/* Board member cards */}
      {members.length === 0 ? (
        <div className="px-4">
          <EmptyState title="No board members found." description="No board member profiles have been recorded." />
        </div>
      ) : (
        <div className="px-4 pb-8 grid grid-cols-1 lg:grid-cols-2 gap-4">
          {members.map((member) => {
            const termDays = daysUntil(member.term_end_date);
            const termExpiringSoon = termDays !== null && termDays >= 0 && termDays <= 90;
            return (
              <div key={member.id} className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
                {/* Header */}
                <div className="flex flex-wrap items-start justify-between gap-2 mb-3">
                  <div>
                    <h3 className="text-base font-bold text-gray-900">{member.full_name}</h3>
                    <p className="text-sm text-gray-600">{member.role_title}</p>
                  </div>
                  <StatusBadge tone={memberStatusTone(member.status)}>
                    {member.status.replace(/_/g, ' ')}
                  </StatusBadge>
                </div>

                {/* Details grid */}
                <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs mb-3">
                  <div>
                    <span className="font-semibold text-gray-500 uppercase tracking-wider">Appointment</span>
                    <p className="text-gray-700 mt-0.5">{formatDate(member.appointment_date)}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-500 uppercase tracking-wider">Term End</span>
                    <p className={`mt-0.5 ${termExpiringSoon ? 'text-yellow-700 font-semibold' : 'text-gray-700'}`}>
                      {formatDate(member.term_end_date)}
                      {termExpiringSoon && termDays !== null && (
                        <span className="ml-1 text-yellow-600">({termDays}d)</span>
                      )}
                    </p>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-500 uppercase tracking-wider">Term #</span>
                    <p className="text-gray-700 mt-0.5">{member.term_number}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-500 uppercase tracking-wider">Appointing Authority</span>
                    <p className="text-gray-700 mt-0.5">{member.appointing_authority || '—'}</p>
                  </div>
                  {member.expertise_areas && (
                    <div className="col-span-2">
                      <span className="font-semibold text-gray-500 uppercase tracking-wider">Expertise</span>
                      <p className="text-gray-700 mt-0.5">{member.expertise_areas}</p>
                    </div>
                  )}
                  {member.committee_memberships && (
                    <div className="col-span-2">
                      <span className="font-semibold text-gray-500 uppercase tracking-wider">Committees</span>
                      <p className="text-gray-700 mt-0.5">{member.committee_memberships}</p>
                    </div>
                  )}
                </div>

                {/* Badges */}
                <div className="flex flex-wrap gap-2">
                  <StatusBadge tone={member.is_independent ? 'good' : 'neutral'}>
                    {member.is_independent ? 'Independent' : 'Non-Independent'}
                  </StatusBadge>
                  {member.annual_declaration_submitted ? (
                    <StatusBadge tone="good">✓ Declared</StatusBadge>
                  ) : (
                    <StatusBadge tone="warning">✗ Pending Declaration</StatusBadge>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}

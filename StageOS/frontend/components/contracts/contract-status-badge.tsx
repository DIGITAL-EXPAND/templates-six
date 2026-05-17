import { StatusBadge } from '@/components/ui/status-badge';
import type { ContractStatus } from '@/lib/api/types';
import { contractStatusLabel } from './helpers';

function tone(status: ContractStatus) {
  if (status === 'signed' || status === 'counter_signed') {
    return 'good';
  }
  if (status === 'expired' || status === 'cancelled') {
    return 'danger';
  }
  if (status === 'issued' || status.endsWith('_review')) {
    return 'warning';
  }
  return 'neutral';
}

export function ContractStatusBadge({ status }: { status: ContractStatus }) {
  return <StatusBadge tone={tone(status)}>{contractStatusLabel(status)}</StatusBadge>;
}


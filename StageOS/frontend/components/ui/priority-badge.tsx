import { StatusBadge } from './status-badge';
import type { Priority } from '@/lib/api/types';

export function PriorityBadge({ priority }: { priority: Priority }) {
  if (priority === 'critical' || priority === 'high') {
    return <StatusBadge tone="danger">{priority}</StatusBadge>;
  }
  if (priority === 'medium') {
    return <StatusBadge tone="warning">{priority}</StatusBadge>;
  }
  return <StatusBadge>{priority}</StatusBadge>;
}

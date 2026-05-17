import { StatusBadge } from './status-badge';

export function EvidenceBadge({
  required,
  provided,
}: {
  required: boolean;
  provided: boolean;
}) {
  if (!required) {
    return <StatusBadge>Not required</StatusBadge>;
  }
  if (provided) {
    return <StatusBadge tone="good">Provided</StatusBadge>;
  }
  return <StatusBadge tone="warning">Required</StatusBadge>;
}

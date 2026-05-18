type AuditEventItem = {
  id: string;
  event_type: string;
  actor?: { email?: string };
  old_value?: string;
  new_value?: string;
  created_at: string;
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-ZA', { dateStyle: 'medium', timeStyle: 'short' });
}

export function AuditTimeline({ events }: { events: AuditEventItem[] }) {
  if (events.length === 0) {
    return <p className="text-sm text-gray-500">No activity recorded yet.</p>;
  }
  return (
    <ol aria-label="Activity timeline" className="space-y-3">
      {events.map((event) => (
        <li className="flex gap-3" key={event.id}>
          <div aria-hidden="true" className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-teal-500" />
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-gray-900">
              {event.event_type.replace(/_/g, ' ')}
              {event.actor?.email && (
                <span className="ml-1 font-normal text-gray-500">by {event.actor.email}</span>
              )}
            </p>
            {(event.old_value || event.new_value) && (
              <p className="mt-0.5 text-xs text-gray-500">
                {event.old_value && <span>From: {event.old_value} </span>}
                {event.new_value && <span>→ {event.new_value}</span>}
              </p>
            )}
            <time className="text-xs text-gray-400" dateTime={event.created_at}>
              {formatDate(event.created_at)}
            </time>
          </div>
        </li>
      ))}
    </ol>
  );
}

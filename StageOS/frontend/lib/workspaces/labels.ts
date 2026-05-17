export const workspaceTypeLabels: Record<string, string> = {
  production: 'Production',
  venue_rental: 'Venue Booking',
  venue_booking: 'Venue Booking',
  co_production: 'Co-Production',
  youth_project: 'Youth Project',
  festival: 'Festival',
  workshop_series: 'Workshop Series',
  training_programme: 'Training Programme',
  governance_item: 'Governance Item',
  civic_event: 'Governance Item',
};

export const workspaceTypeOptions = [
  { value: 'production', label: 'Production' },
  { value: 'venue_rental', label: 'Venue Booking' },
  { value: 'co_production', label: 'Co-Production' },
  { value: 'youth_project', label: 'Youth Project' },
  { value: 'festival', label: 'Festival' },
  { value: 'workshop_series', label: 'Workshop Series' },
  { value: 'governance_item', label: 'Governance Item' },
];

export function workspaceTypeLabel(value: string) {
  return workspaceTypeLabels[value] ?? value;
}

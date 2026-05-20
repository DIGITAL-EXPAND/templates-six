'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchVenues, fetchSpacesForVenue, fetchVenueCapacityConfigs } from '@/lib/api/endpoints';
import type { VenueCapacityConfigItem } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type VenueRow = { id: string; name: string; venue_type: string; site: string; site_name: string; capacity: number; is_active: boolean };
type SpaceRow = { id: string; name: string; space_type: string; venue: string; venue_name: string; capacity: number; is_bookable: boolean };

function humanise(val: string) {
  return val.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

const configurationLabels: Record<string, string> = {
  theatre: 'Theatre (fixed rows)',
  cabaret: 'Cabaret (round tables)',
  standing: 'Standing',
  thrust: 'Thrust',
  traverse: 'Traverse',
  in_the_round: 'In the Round',
  promenade: 'Promenade',
  flexible: 'Flexible',
};

export default function VenueManagementPage() {
  const { tokens } = useAuth();
  const [venues, setVenues] = useState<VenueRow[]>([]);
  const [spaces, setSpaces] = useState<SpaceRow[]>([]);
  const [configs, setConfigs] = useState<VenueCapacityConfigItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.allSettled([
      fetchVenues(tokens.access),
      fetchSpacesForVenue(tokens.access),
      fetchVenueCapacityConfigs(tokens.access),
    ]).then(([venuesRes, spacesRes, configsRes]) => {
      if (venuesRes.status === 'fulfilled') setVenues(venuesRes.value);
      if (spacesRes.status === 'fulfilled') setSpaces(spacesRes.value);
      if (configsRes.status === 'fulfilled') setConfigs(configsRes.value);
      if (venuesRes.status === 'rejected') setError('Venues could not be loaded.');
      setLoading(false);
    });
  }, [tokens?.access]);

  const spaceConfigs = (spaceId: string) => configs.filter((c) => c.space === spaceId);
  const venueSpaces = (venueId: string) => spaces.filter((s) => s.venue === venueId);

  return (
    <AppShell pageTitle="Venue Management">
      <PageHeader
        title="Venue Management"
        description="Theatres, spaces and seating configurations"
      />

      {loading && <LoadingState label="Loading venues..." />}
      {error && <ErrorState message={error} />}

      {!loading && !error && venues.length === 0 && (
        <EmptyState
          title="No venues configured"
          description="Venues and spaces are managed by your system administrator."
        />
      )}

      {!loading && !error && venues.length > 0 && (
        <div className="mt-6 space-y-6">
          {venues.map((venue) => (
            <div key={venue.id} className="rounded-xl border border-gray-200 bg-white overflow-hidden">
              {/* Venue Header */}
              <div className="border-b border-gray-100 bg-gray-50 px-5 py-4 flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-gray-900">{venue.name}</h2>
                  <p className="text-sm text-gray-500">
                    {humanise(venue.venue_type)} · {venue.site_name || 'No site'} · Capacity: {venue.capacity}
                  </p>
                </div>
                <StatusBadge tone={venue.is_active ? 'good' : 'neutral'}>
                  {venue.is_active ? 'Active' : 'Inactive'}
                </StatusBadge>
              </div>

              {/* Spaces */}
              {venueSpaces(venue.id).length === 0 ? (
                <p className="px-5 py-4 text-sm text-gray-400">No spaces defined for this venue.</p>
              ) : (
                <div className="divide-y divide-gray-50">
                  {venueSpaces(venue.id).map((space) => (
                    <div key={space.id} className="px-5 py-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-gray-800">{space.name}</p>
                          <p className="text-sm text-gray-500">
                            {humanise(space.space_type)} · Default capacity: {space.capacity}
                            {!space.is_bookable && ' · Not bookable'}
                          </p>
                        </div>
                      </div>

                      {/* Capacity Configurations */}
                      {spaceConfigs(space.id).length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {spaceConfigs(space.id).map((cfg) => (
                            <span
                              key={cfg.id}
                              className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${
                                cfg.is_default
                                  ? 'bg-indigo-100 text-indigo-700'
                                  : 'bg-gray-100 text-gray-600'
                              }`}
                            >
                              {configurationLabels[cfg.configuration] ?? humanise(cfg.configuration)}
                              <span className="font-semibold">· {cfg.capacity}</span>
                              {cfg.is_default && <span className="ml-1 text-indigo-500">★</span>}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}

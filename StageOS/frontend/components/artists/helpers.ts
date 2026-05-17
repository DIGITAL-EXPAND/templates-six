import type { ArtistDocumentItem, ArtistEngagementItem, ArtistItem } from '@/lib/api/types';

export function artistDisplayName(artist: ArtistItem) {
  return artist.professional_name || artist.legal_name;
}

export function artistDocuments(documents: ArtistDocumentItem[], artistId: string) {
  return documents.filter((document) => document.artist === artistId);
}

export function artistEngagements(engagements: ArtistEngagementItem[], artistId: string) {
  return engagements.filter((engagement) => engagement.artist === artistId);
}

export function artistBlockers(artist: ArtistItem, documents: ArtistDocumentItem[], engagements: ArtistEngagementItem[]) {
  const blockers: string[] = [];
  if (artist.status === 'documents_incomplete') {
    blockers.push('Artist documents are incomplete.');
  }
  if (documents.some((document) => document.status === 'missing' || document.status === 'rejected')) {
    blockers.push('Artist documents are missing or rejected.');
  }
  if (engagements.some((engagement) => !engagement.contract)) {
    blockers.push('One or more engagements do not have a linked contract.');
  }
  if (!['contract_ready', 'contracted', 'payment_ready'].includes(artist.status)) {
    blockers.push('Contract readiness has not been reached.');
  }
  return blockers;
}


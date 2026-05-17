import type {
  ContractRecordItem,
  DocumentItem,
  OperatingContextListItem,
  SignatureRecordItem,
} from '@/lib/api/types';

export function friendlyContractType(value: string) {
  return value
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export function contractStatusLabel(value: string) {
  return friendlyContractType(value);
}

export function workspaceName(workspaces: OperatingContextListItem[], id: string) {
  return workspaces.find((workspace) => workspace.id === id)?.title ?? 'Workspace unavailable';
}

export function documentTitle(documents: DocumentItem[], id: string | null) {
  if (!id) {
    return 'No signed document linked';
  }
  return documents.find((document) => document.id === id)?.title ?? 'Document unavailable';
}

export function money(contract: ContractRecordItem) {
  return new Intl.NumberFormat('en-ZA', {
    currency: contract.currency || 'ZAR',
    style: 'currency',
  }).format(Number(contract.value || 0));
}

export function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleDateString() : 'Not set';
}

export function contractSignatures(signatures: SignatureRecordItem[], contractId: string) {
  return signatures
    .filter((signature) => signature.contract === contractId)
    .sort((a, b) => a.signature_order - b.signature_order);
}

export function isPendingSignature(contract: ContractRecordItem) {
  return contract.signatures_received < contract.signatures_required && contract.status !== 'cancelled';
}

export function isExpired(contract: ContractRecordItem, now: number) {
  return Boolean(contract.expiry_date && new Date(contract.expiry_date).getTime() < now);
}

export function isExpiringSoon(contract: ContractRecordItem, now: number) {
  if (!contract.expiry_date) {
    return false;
  }
  const expiry = new Date(contract.expiry_date).getTime();
  const thirtyDays = 30 * 24 * 60 * 60 * 1000;
  return expiry >= now && expiry <= now + thirtyDays;
}


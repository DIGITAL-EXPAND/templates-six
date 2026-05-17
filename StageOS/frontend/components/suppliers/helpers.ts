import type {
  PaymentPackItem,
  SupplierDocumentItem,
  SupplierEngagementItem,
  SupplierItem,
} from '@/lib/api/types';

export function supplierDocuments(documents: SupplierDocumentItem[], supplierId: string) {
  return documents.filter((document) => document.supplier === supplierId);
}

export function supplierEngagements(engagements: SupplierEngagementItem[], supplierId: string) {
  return engagements.filter((engagement) => engagement.supplier === supplierId);
}

export function supplierPaymentPacks(packs: PaymentPackItem[], engagements: SupplierEngagementItem[]) {
  const engagementIds = new Set(engagements.map((engagement) => engagement.id));
  return packs.filter((pack) => engagementIds.has(pack.supplier_engagement));
}

export function supplierBlockers(
  supplier: SupplierItem,
  documents: SupplierDocumentItem[],
  packs: PaymentPackItem[],
) {
  const blockers: string[] = [];
  if (!supplier.csd_verified) {
    blockers.push('CSD readiness has not been verified.');
  }
  if (supplier.status !== 'ready') {
    blockers.push('Supplier status is not ready.');
  }
  if (documents.some((document) => document.status === 'missing' || document.status === 'rejected')) {
    blockers.push('Supplier documents are missing or rejected.');
  }
  if (packs.some((pack) => pack.status === 'awaiting_csd' || pack.status === 'rejected')) {
    blockers.push('Payment readiness has blockers.');
  }
  return blockers;
}


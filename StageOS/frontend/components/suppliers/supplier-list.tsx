import type { OperatingContextListItem, PaymentPackItem, SupplierDocumentItem, SupplierEngagementItem, SupplierItem } from '@/lib/api/types';
import { SupplierCard } from './supplier-card';

export function SupplierList({
  suppliers,
  documents,
  engagements,
  packs,
  workspaces,
  onSelect,
}: {
  suppliers: SupplierItem[];
  documents: SupplierDocumentItem[];
  engagements: SupplierEngagementItem[];
  packs: PaymentPackItem[];
  workspaces: OperatingContextListItem[];
  onSelect: (supplier: SupplierItem) => void;
}) {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {suppliers.map((supplier) => (
        <SupplierCard
          documents={documents}
          engagements={engagements}
          key={supplier.id}
          onSelect={onSelect}
          packs={packs}
          supplier={supplier}
          workspaces={workspaces}
        />
      ))}
    </div>
  );
}


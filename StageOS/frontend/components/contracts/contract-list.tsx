import type {
  ContractRecordItem,
  DocumentItem,
  OperatingContextListItem,
  SignatureRecordItem,
} from '@/lib/api/types';
import { ContractCard } from './contract-card';

export function ContractList({
  contracts,
  documents,
  now,
  signatures,
  workspaces,
  onSelect,
}: {
  contracts: ContractRecordItem[];
  documents: DocumentItem[];
  now: number;
  signatures: SignatureRecordItem[];
  workspaces: OperatingContextListItem[];
  onSelect: (contract: ContractRecordItem) => void;
}) {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {contracts.map((contract) => (
        <ContractCard
          contract={contract}
          documents={documents}
          key={contract.id}
          now={now}
          onSelect={onSelect}
          signatures={signatures}
          workspaces={workspaces}
        />
      ))}
    </div>
  );
}


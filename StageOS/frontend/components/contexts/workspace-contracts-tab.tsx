'use client';

import { useEffect, useMemo, useState } from 'react';
import { ContractActionDialog, type ContractAction } from '@/components/contracts/contract-action-dialog';
import { ContractDetailDrawer } from '@/components/contracts/contract-detail-drawer';
import { ContractList } from '@/components/contracts/contract-list';
import { isPendingSignature } from '@/components/contracts/helpers';
import { EmptyState, ErrorState, LoadingState, PermissionDeniedState } from '@/components/ui/states';
import { ApiError } from '@/lib/api/client';
import {
  cancelContract,
  fetchContracts,
  fetchDocuments,
  fetchOperatingContexts,
  fetchSignatures,
  issueContract,
  lockFinalContract,
  signContractSignature,
  submitContractForReview,
} from '@/lib/api/endpoints';
import type {
  ContractRecordItem,
  DocumentItem,
  OperatingContextListItem,
  SignatureRecordItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

export function WorkspaceContractsTab({ workspaceId }: { workspaceId: string }) {
  const { tokens } = useAuth();
  const [contracts, setContracts] = useState<ContractRecordItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [signatures, setSignatures] = useState<SignatureRecordItem[]>([]);
  const [selectedContract, setSelectedContract] = useState<ContractRecordItem | null>(null);
  const [actionContract, setActionContract] = useState<ContractRecordItem | null>(null);
  const [action, setAction] = useState<ContractAction | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [signingId, setSigningId] = useState('');
  const [loadedAt, setLoadedAt] = useState(0);

  useEffect(() => {
    if (!tokens?.access) {
      return;
    }

    let mounted = true;
    Promise.all([
      fetchContracts(tokens.access, { operating_context: workspaceId }),
      fetchOperatingContexts(tokens.access),
      fetchDocuments(tokens.access, { operating_context: workspaceId }),
    ])
      .then(async ([contractResponse, workspaceResponse, documentResponse]) => {
        const signatureResponses = await Promise.all(
          contractResponse.results.map((contract) => fetchSignatures(tokens.access, { contract: contract.id })),
        );
        if (!mounted) {
          return;
        }
        setContracts(contractResponse.results);
        setWorkspaces(workspaceResponse.results);
        setDocuments(documentResponse.results);
        setSignatures(signatureResponses.flatMap((response) => response.results));
        setLoadedAt(Date.now());
      })
      .catch((err) => {
        if (!mounted) {
          return;
        }
        if (err instanceof ApiError && err.status === 403) {
          setPermissionDenied(true);
        } else {
          setError('Contracts could not be loaded for this Workspace.');
        }
      })
      .finally(() => {
        if (mounted) {
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [tokens?.access, workspaceId]);

  const blockers = useMemo(
    () =>
      contracts.filter(
        (contract) =>
          isPendingSignature(contract) || contract.status.endsWith('_review') || (contract.status === 'signed' && !contract.signed_document),
      ).length,
    [contracts],
  );

  function openAction(nextAction: ContractAction, contract: ContractRecordItem) {
    setAction(nextAction);
    setActionContract(contract);
  }

  function updateContract(updated: ContractRecordItem) {
    setContracts((current) => current.map((contract) => (contract.id === updated.id ? updated : contract)));
    setSelectedContract((current) => (current?.id === updated.id ? updated : current));
  }

  async function handleAction(values: { reviewType: string; comment: string }) {
    if (!tokens?.access || !actionContract || !action) {
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const updated =
        action === 'issue'
          ? await issueContract(tokens.access, actionContract.id)
          : action === 'review'
            ? await submitContractForReview(tokens.access, actionContract.id, values.reviewType)
            : action === 'lock'
              ? await lockFinalContract(tokens.access, actionContract.id, values.comment)
              : await cancelContract(tokens.access, actionContract.id, values.comment);
      updateContract(updated);
      setAction(null);
      setActionContract(null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError('You do not have permission to perform this contract action.');
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Contract action could not be completed.');
      }
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSign(signature: SignatureRecordItem) {
    if (!tokens?.access) {
      return;
    }
    setSigningId(signature.id);
    setError('');
    try {
      const updated = await signContractSignature(tokens.access, signature.id);
      setSignatures((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError('You do not have permission to perform this contract action.');
      } else if (err instanceof ApiError) {
        setError(JSON.stringify(err.payload ?? { detail: err.message }));
      } else {
        setError('Signature could not be recorded.');
      }
    } finally {
      setSigningId('');
    }
  }

  if (loading) {
    return <LoadingState label="Loading Workspace contracts" />;
  }

  return (
    <div className="space-y-4">
      {permissionDenied ? <PermissionDeniedState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {contracts.length ? (
        <>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-md border border-slate-200 p-3">
              <div className="text-xs font-bold uppercase tracking-normal text-slate-500">Contracts</div>
              <div className="mt-2 text-2xl font-bold text-slate-950">{contracts.length}</div>
            </div>
            <div className="rounded-md border border-slate-200 p-3">
              <div className="text-xs font-bold uppercase tracking-normal text-slate-500">Pending signature</div>
              <div className="mt-2 text-2xl font-bold text-slate-950">
                {contracts.filter(isPendingSignature).length}
              </div>
            </div>
            <div className="rounded-md border border-slate-200 p-3">
              <div className="text-xs font-bold uppercase tracking-normal text-slate-500">Blockers</div>
              <div className="mt-2 text-2xl font-bold text-slate-950">{blockers}</div>
            </div>
          </div>
          <ContractList
            contracts={contracts}
            documents={documents}
            now={loadedAt}
            onSelect={setSelectedContract}
            signatures={signatures}
            workspaces={workspaces}
          />
        </>
      ) : (
        <EmptyState
          description="Contracts linked to this Workspace will appear here."
          title="No contracts yet"
        />
      )}
      <ContractDetailDrawer
        contract={selectedContract}
        documents={documents}
        now={loadedAt}
        onAction={openAction}
        onClose={() => setSelectedContract(null)}
        onSign={handleSign}
        signatures={signatures}
        signingId={signingId}
        workspaces={workspaces}
      />
      <ContractActionDialog
        action={action}
        contract={actionContract}
        onClose={() => {
          setAction(null);
          setActionContract(null);
        }}
        onSubmit={handleAction}
        submitting={submitting}
      />
    </div>
  );
}


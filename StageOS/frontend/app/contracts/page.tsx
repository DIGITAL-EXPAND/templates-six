'use client';

import { useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { DepartmentExecutiveActionsPanel } from '@/components/governance/department-executive-actions-panel';
import { ContractActionDialog, type ContractAction } from '@/components/contracts/contract-action-dialog';
import { ContractDetailDrawer } from '@/components/contracts/contract-detail-drawer';
import { ContractFilters, type ContractFiltersValue } from '@/components/contracts/contract-filters';
import { ContractList } from '@/components/contracts/contract-list';
import { isExpired, isExpiringSoon, isPendingSignature } from '@/components/contracts/helpers';
import { PageHeader } from '@/components/ui/page-header';
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

export default function ContractsPage() {
  const { tokens } = useAuth();
  const [contracts, setContracts] = useState<ContractRecordItem[]>([]);
  const [workspaces, setWorkspaces] = useState<OperatingContextListItem[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [signatures, setSignatures] = useState<SignatureRecordItem[]>([]);
  const [selectedContract, setSelectedContract] = useState<ContractRecordItem | null>(null);
  const [actionContract, setActionContract] = useState<ContractRecordItem | null>(null);
  const [action, setAction] = useState<ContractAction | null>(null);
  const [filters, setFilters] = useState<ContractFiltersValue>({
    status: 'all',
    contractType: 'all',
    workspace: 'all',
    pendingSignature: false,
    expiry: 'all',
    search: '',
  });
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
      fetchContracts(tokens.access),
      fetchOperatingContexts(tokens.access),
      fetchDocuments(tokens.access),
      fetchSignatures(tokens.access),
    ])
      .then(([contractResponse, workspaceResponse, documentResponse, signatureResponse]) => {
        if (!mounted) {
          return;
        }
        setContracts(contractResponse.results);
        setWorkspaces(workspaceResponse.results);
        setDocuments(documentResponse.results);
        setSignatures(signatureResponse.results);
        setLoadedAt(Date.now());
      })
      .catch((err) => {
        if (!mounted) {
          return;
        }
        if (err instanceof ApiError && err.status === 403) {
          setPermissionDenied(true);
        } else {
          setError('Contracts could not be loaded.');
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
  }, [tokens?.access]);

  const contractTypes = useMemo(
    () => Array.from(new Set(contracts.map((contract) => contract.contract_type))).sort(),
    [contracts],
  );

  const filteredContracts = useMemo(() => {
    const query = filters.search.trim().toLowerCase();
    return contracts.filter((contract) => {
      if (filters.status !== 'all' && contract.status !== filters.status) {
        return false;
      }
      if (filters.contractType !== 'all' && contract.contract_type !== filters.contractType) {
        return false;
      }
      if (filters.workspace !== 'all' && contract.operating_context !== filters.workspace) {
        return false;
      }
      if (filters.pendingSignature && !isPendingSignature(contract)) {
        return false;
      }
      if (filters.expiry === 'expired' && !isExpired(contract, loadedAt)) {
        return false;
      }
      if (filters.expiry === 'expiring_soon' && !isExpiringSoon(contract, loadedAt)) {
        return false;
      }
      if (query && !contract.counterparty_name.toLowerCase().includes(query)) {
        return false;
      }
      return true;
    });
  }, [contracts, filters, loadedAt]);

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

  return (
    <AppShell>
      <div className="space-y-5">
        <PageHeader
          description="Monitor agreement readiness, reviews, signatures and final signed documents."
          eyebrow="Contracts"
          title="Contracts"
        />
        {permissionDenied ? <PermissionDeniedState /> : null}
        {error ? <ErrorState message={error} /> : null}
        {loading ? (
          <LoadingState label="Loading contracts" />
        ) : (
          <>
            <ContractFilters
              contractTypes={contractTypes}
              onChange={setFilters}
              value={filters}
              workspaces={workspaces}
            />
            <DepartmentExecutiveActionsPanel departmentTypes={['contracts']} targetTypes={['ContractRecord', 'SignatureRecord']} />
            {filteredContracts.length ? (
              <ContractList
                contracts={filteredContracts}
                documents={documents}
                now={loadedAt}
                onSelect={setSelectedContract}
                signatures={signatures}
                workspaces={workspaces}
              />
            ) : (
              <EmptyState
                description="Contracts will appear here when the backend returns agreement records."
                title="No contracts found"
              />
            )}
          </>
        )}
      </div>
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
    </AppShell>
  );
}

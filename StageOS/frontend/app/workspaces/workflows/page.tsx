'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import {
  fetchWorkflowTemplates,
  fetchWorkflowInstances,
  fetchWorkflowSteps,
  advanceWorkflowStep,
  launchWorkflow,
  fetchOperatingContexts,
} from '@/lib/api/endpoints';
import type {
  WorkflowTemplateItem,
  WorkflowInstanceItem,
  WorkflowStepItem,
  OperatingContextListItem,
} from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function instanceStatusTone(
  status: WorkflowInstanceItem['status'],
): 'info' | 'good' | 'danger' | 'warning' | 'neutral' {
  if (status === 'active') return 'info';
  if (status === 'completed') return 'good';
  if (status === 'cancelled') return 'danger';
  if (status === 'paused') return 'warning';
  return 'neutral';
}

function stepStatusTone(
  status: WorkflowStepItem['status'],
): 'neutral' | 'info' | 'good' | 'danger' {
  if (status === 'pending') return 'neutral';
  if (status === 'in_progress') return 'info';
  if (status === 'completed') return 'good';
  if (status === 'skipped') return 'neutral';
  if (status === 'blocked') return 'danger';
  return 'neutral';
}

// ─────────────────────────────────────────────
// Step rows (lazy loaded per instance)
// ─────────────────────────────────────────────
function WorkflowStepsPanel({
  instanceId,
  token,
}: {
  instanceId: string;
  token: string;
}) {
  const [steps, setSteps] = useState<WorkflowStepItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [advancing, setAdvancing] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    fetchWorkflowSteps(token, { workflow_instance: instanceId })
      .then((data) => {
        if (mounted) setSteps(data.results ?? []);
      })
      .catch(() => {
        if (mounted) setError('Could not load steps.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [instanceId, token]);

  async function handleAdvance(stepId: string) {
    setAdvancing(stepId);
    try {
      const updated = await advanceWorkflowStep(token, stepId, { notes: '' });
      setSteps((prev) => prev.map((s) => (s.id === stepId ? updated : s)));
    } catch {
      // silently ignore
    } finally {
      setAdvancing(null);
    }
  }

  if (loading) return <p className="px-4 py-2 text-sm text-gray-500">Loading steps…</p>;
  if (error) return <p className="px-4 py-2 text-sm text-red-600">{error}</p>;
  if (steps.length === 0) return <p className="px-4 py-2 text-sm text-gray-400">No steps found.</p>;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <caption className="sr-only">Workflow steps</caption>
        <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-600">
          <tr>
            <th className="px-4 py-2" scope="col">#</th>
            <th className="px-4 py-2" scope="col">Step</th>
            <th className="px-4 py-2" scope="col">Status</th>
            <th className="px-4 py-2" scope="col">Due</th>
            <th className="px-4 py-2" scope="col">Blockers</th>
            <th className="px-4 py-2" scope="col"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {steps.map((step) => (
            <tr className="hover:bg-gray-50" key={step.id}>
              <td className="px-4 py-2 text-gray-500">{step.step_number}</td>
              <td className="px-4 py-2 font-medium text-gray-900">
                {step.owner_role_description}
              </td>
              <td className="px-4 py-2">
                <StatusBadge tone={stepStatusTone(step.status)}>
                  {step.status.replace('_', ' ')}
                </StatusBadge>
              </td>
              <td className="px-4 py-2 text-gray-500">{formatDate(step.due_date)}</td>
              <td className="px-4 py-2">
                {step.blockers && step.blockers.length > 0 ? (
                  <ul className="space-y-0.5">
                    {step.blockers.map((b, i) => (
                      <li className="text-xs text-red-600" key={i}>
                        {b}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <span className="text-gray-400">—</span>
                )}
              </td>
              <td className="px-4 py-2">
                {step.status === 'in_progress' && (
                  <button
                    className="rounded-lg border border-blue-300 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 hover:bg-blue-100 disabled:opacity-50"
                    disabled={advancing === step.id}
                    onClick={() => handleAdvance(step.id)}
                  >
                    {advancing === step.id ? 'Advancing…' : 'Advance'}
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─────────────────────────────────────────────
// Instance row with expandable steps
// ─────────────────────────────────────────────
function InstanceRow({
  instance,
  templates,
  contexts,
  token,
}: {
  instance: WorkflowInstanceItem;
  templates: WorkflowTemplateItem[];
  contexts: OperatingContextListItem[];
  token: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const templateName =
    templates.find((t) => t.id === instance.template)?.name ?? instance.template;
  const contextTitle =
    contexts.find((c) => c.id === instance.operating_context)?.title ??
    instance.operating_context;

  return (
    <>
      <tr className="hover:bg-gray-50">
        <td className="px-4 py-3 font-medium text-gray-900">{contextTitle}</td>
        <td className="px-4 py-3 text-gray-600">{templateName}</td>
        <td className="px-4 py-3">
          <StatusBadge tone={instanceStatusTone(instance.status)}>
            {instance.status}
          </StatusBadge>
        </td>
        <td className="px-4 py-3 text-gray-500">{formatDate(instance.started_at)}</td>
        <td className="px-4 py-3">
          <button
            className="text-xs font-medium text-blue-600 underline hover:text-blue-800"
            onClick={() => setExpanded((v) => !v)}
          >
            {expanded ? 'Hide Steps' : 'View Steps'}
          </button>
        </td>
      </tr>
      {expanded && (
        <tr>
          <td className="bg-gray-50 px-2 py-3" colSpan={5}>
            <WorkflowStepsPanel instanceId={instance.id} token={token} />
          </td>
        </tr>
      )}
    </>
  );
}

// ─────────────────────────────────────────────
// Launch form (inline, per template)
// ─────────────────────────────────────────────
function LaunchForm({
  template,
  contexts,
  token,
  onLaunched,
}: {
  template: WorkflowTemplateItem;
  contexts: OperatingContextListItem[];
  token: string;
  onLaunched: (instance: WorkflowInstanceItem) => void;
}) {
  const [contextId, setContextId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!contextId) {
      setErr('Select a production context.');
      return;
    }
    setErr('');
    setSubmitting(true);
    try {
      const instance = await launchWorkflow(token, template.id, contextId);
      onLaunched(instance);
    } catch {
      setErr('Failed to launch workflow. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="mt-2 flex items-end gap-2 flex-wrap" onSubmit={handleSubmit}>
      <div>
        <label className="sr-only" htmlFor={`ctx-${template.id}`}>
          Production context
        </label>
        <select
          className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          id={`ctx-${template.id}`}
          value={contextId}
          onChange={(e) => setContextId(e.target.value)}
        >
          <option value="">Select production…</option>
          {contexts.map((c) => (
            <option key={c.id} value={c.id}>
              {c.title}
            </option>
          ))}
        </select>
      </div>
      <button
        className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        disabled={submitting}
        type="submit"
      >
        {submitting ? 'Launching…' : 'Launch'}
      </button>
      {err && <p className="text-xs text-red-600">{err}</p>}
    </form>
  );
}

// ─────────────────────────────────────────────
// Main page
// ─────────────────────────────────────────────
export default function WorkflowsPage() {
  const { tokens } = useAuth();
  const [templates, setTemplates] = useState<WorkflowTemplateItem[]>([]);
  const [instances, setInstances] = useState<WorkflowInstanceItem[]>([]);
  const [contexts, setContexts] = useState<OperatingContextListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [launchingId, setLaunchingId] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    const token = tokens.access;
    let mounted = true;

    Promise.all([
      fetchWorkflowTemplates(token),
      fetchWorkflowInstances(token),
      fetchOperatingContexts(token),
    ])
      .then(([tmplData, instData, ctxData]) => {
        if (!mounted) return;
        setTemplates(tmplData.results ?? []);
        setInstances(instData.results ?? []);
        setContexts(ctxData.results ?? []);
      })
      .catch(() => {
        if (mounted) setError('Failed to load workflow data.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [tokens?.access]);

  function handleInstanceLaunched(instance: WorkflowInstanceItem) {
    setInstances((prev) => [instance, ...prev]);
    setLaunchingId(null);
  }

  if (loading) return <AppShell pageTitle="Workflows"><LoadingState label="Loading workflows…" /></AppShell>;
  if (error) return <AppShell pageTitle="Workflows"><ErrorState message={error} /></AppShell>;

  return (
    <AppShell pageTitle="Workflows">
      <div className="space-y-8">
        <PageHeader
          title="Workflow Management"
          description="Production workflow templates and active instances"
        />

        {/* ── Workflow Templates ── */}
        <section>
          <h2 className="mb-3 text-base font-semibold text-gray-800">Workflow Templates</h2>
          {templates.length === 0 ? (
            <EmptyState title="No templates" description="No workflow templates have been configured." />
          ) : (
            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
              <table className="w-full text-sm">
                <caption className="sr-only">Workflow templates</caption>
                <thead className="border-b border-gray-100 bg-gray-50 text-left">
                  <tr>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Name</th>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Context Type</th>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Version</th>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Active</th>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Steps configured</th>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Launch</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {templates.map((tmpl) => (
                    <tr className="hover:bg-gray-50 align-top" key={tmpl.id}>
                      <td className="px-4 py-3 font-medium text-gray-900">
                        <div>{tmpl.name}</div>
                        {tmpl.description && (
                          <p className="mt-0.5 text-xs text-gray-500">{tmpl.description}</p>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-600">{tmpl.context_type}</td>
                      <td className="px-4 py-3 text-gray-600">v{tmpl.version}</td>
                      <td className="px-4 py-3">
                        <StatusBadge tone={tmpl.is_active ? 'good' : 'neutral'}>
                          {tmpl.is_active ? 'Active' : 'Inactive'}
                        </StatusBadge>
                      </td>
                      <td className="px-4 py-3 text-gray-500">—</td>
                      <td className="px-4 py-3">
                        {launchingId === tmpl.id ? (
                          <LaunchForm
                            contexts={contexts}
                            template={tmpl}
                            token={tokens?.access ?? ''}
                            onLaunched={handleInstanceLaunched}
                          />
                        ) : (
                          <button
                            className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
                            onClick={() => setLaunchingId(tmpl.id)}
                          >
                            Launch
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* ── Active Workflow Instances ── */}
        <section>
          <h2 className="mb-3 text-base font-semibold text-gray-800">Active Workflow Instances</h2>
          {instances.length === 0 ? (
            <EmptyState title="No instances" description="Launch a workflow from a template above to get started." />
          ) : (
            <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
              <table className="w-full text-sm">
                <caption className="sr-only">Workflow instances</caption>
                <thead className="border-b border-gray-100 bg-gray-50 text-left">
                  <tr>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Production</th>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Template</th>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Status</th>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col">Started</th>
                    <th className="px-4 py-3 font-semibold text-gray-700" scope="col"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {instances.map((inst) => (
                    <InstanceRow
                      contexts={contexts}
                      instance={inst}
                      key={inst.id}
                      templates={templates}
                      token={tokens?.access ?? ''}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </AppShell>
  );
}

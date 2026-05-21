'use client';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/app-shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/states';
import { StatusBadge } from '@/components/ui/status-badge';
import { fetchDonors, fetchDonations, createDonor } from '@/lib/api/endpoints';
import type { Donor, Donation } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/auth-provider';

type StatusTone = 'good' | 'warning' | 'danger' | 'neutral' | 'info';

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-ZA', { dateStyle: 'medium' });
}

function formatZAR(val: string | null | undefined) {
  if (!val) return '—';
  return 'R ' + parseFloat(String(val)).toLocaleString('en-ZA', { minimumFractionDigits: 2 });
}

function categoryTone(category: string): StatusTone {
  switch (category) {
    case 'corporate': return 'info';
    case 'foundation': return 'good';
    case 'government': return 'warning';
    case 'arts_council': return 'good';
    case 'individual':
    case 'other': return 'neutral';
    default: return 'neutral';
  }
}

function donationStatusTone(status: string): StatusTone {
  switch (status) {
    case 'received':
    case 'acknowledged': return 'good';
    case 'pledged':
    case 'invoiced': return 'warning';
    case 'prospect': return 'neutral';
    case 'lapsed': return 'danger';
    default: return 'neutral';
  }
}

const emptyForm = {
  name: '',
  category: 'corporate',
  contact_person: '',
  email: '',
  phone: '',
  is_section_18a: false,
  tax_exempt_number: '',
};

export default function DonorsPage() {
  const { tokens } = useAuth();
  const [donors, setDonors] = useState<Donor[]>([]);
  const [donations, setDonations] = useState<Donation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ ...emptyForm });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [expandedDonorId, setExpandedDonorId] = useState<string | null>(null);

  useEffect(() => {
    if (!tokens?.access) return;
    Promise.all([
      fetchDonors(tokens.access).then((res) => setDonors(res.results)),
      fetchDonations(tokens.access).then((res) => setDonations(res.results)),
    ])
      .catch(() => setError('Failed to load donors data'))
      .finally(() => setLoading(false));
  }, [tokens?.access]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setForm((prev) => ({ ...prev, [name]: checked }));
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tokens?.access) return;
    setSubmitting(true);
    setFormError(null);
    try {
      const created = await createDonor(tokens.access, {
        name: form.name,
        category: form.category,
        contact_person: form.contact_person,
        email: form.email,
        phone: form.phone,
        is_section_18a: form.is_section_18a,
        tax_exempt_number: form.is_section_18a ? form.tax_exempt_number : '',
      });
      setDonors((prev) => [created, ...prev]);
      setForm({ ...emptyForm });
      setShowForm(false);
    } catch {
      setFormError('Failed to create donor record.');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <AppShell><LoadingState label="Loading donors…" /></AppShell>;
  if (error) return <AppShell><ErrorState message={error} /></AppShell>;

  const totalPledged = donations.reduce((sum, d) => sum + parseFloat(d.amount_pledged || '0'), 0);
  const totalReceived = donations.reduce((sum, d) => sum + parseFloat(d.amount_received || '0'), 0);

  function donorDonations(donorId: string) {
    return donations.filter((d) => d.donor === donorId);
  }

  return (
    <AppShell>
      <PageHeader
        title="Donors & Sponsors"
        description="Section 18A donors, corporate sponsors, and funding partners"
      />

      {/* Summary strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Total Donors</div>
          <div className="text-2xl font-bold text-gray-900">{donors.length}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Total Pledged</div>
          <div className="text-2xl font-bold text-gray-900">{'R ' + totalPledged.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Total Received</div>
          <div className="text-2xl font-bold text-green-700">{'R ' + totalReceived.toLocaleString('en-ZA', { minimumFractionDigits: 2 })}</div>
        </div>
      </div>

      {/* Add Donor button */}
      <div className="px-4 pb-2">
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'Add Donor'}
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div className="mx-4 mb-4 rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900 mb-4">New Donor / Sponsor</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  name="category"
                  value={form.category}
                  onChange={handleChange}
                  required
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="corporate">Corporate</option>
                  <option value="foundation">Foundation</option>
                  <option value="government">Government</option>
                  <option value="arts_council">Arts Council</option>
                  <option value="individual">Individual</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Contact Person</label>
                <input
                  name="contact_person"
                  value={form.contact_person}
                  onChange={handleChange}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  name="phone"
                  value={form.phone}
                  onChange={handleChange}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_section_18a"
                name="is_section_18a"
                checked={form.is_section_18a}
                onChange={handleChange}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="is_section_18a" className="text-sm font-medium text-gray-700">
                Section 18A Donor
              </label>
            </div>
            {form.is_section_18a && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tax Exempt Number</label>
                <input
                  name="tax_exempt_number"
                  value={form.tax_exempt_number}
                  onChange={handleChange}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
            {formError && <p className="text-sm text-red-600">{formError}</p>}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={submitting}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {submitting ? 'Saving…' : 'Save Donor'}
              </button>
              <button
                type="button"
                onClick={() => { setShowForm(false); setForm({ ...emptyForm }); }}
                className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Donors table */}
      {donors.length === 0 ? (
        <div className="px-4">
          <EmptyState title="No donors registered." description="Use 'Add Donor' to register a new donor or sponsor." />
        </div>
      ) : (
        <div className="px-4 pb-8">
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Contact</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">18A</th>
                  <th className="px-4 py-3">Donations</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {donors.map((donor) => {
                  const dDonations = donorDonations(donor.id);
                  const isExpanded = expandedDonorId === donor.id;
                  return (
                    <>
                      <tr key={donor.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 font-medium text-gray-900">{donor.name}</td>
                        <td className="px-4 py-3">
                          <StatusBadge tone={categoryTone(donor.category)}>
                            {donor.category.replace(/_/g, ' ')}
                          </StatusBadge>
                        </td>
                        <td className="px-4 py-3 text-gray-700">{donor.contact_person || '—'}</td>
                        <td className="px-4 py-3 text-gray-600">{donor.email || '—'}</td>
                        <td className="px-4 py-3">
                          {donor.is_section_18a ? (
                            <StatusBadge tone="good">18A</StatusBadge>
                          ) : (
                            <StatusBadge tone="neutral">—</StatusBadge>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          {dDonations.length > 0 && (
                            <button
                              onClick={() => setExpandedDonorId(isExpanded ? null : donor.id)}
                              className="text-blue-600 hover:underline text-xs font-medium"
                            >
                              {isExpanded ? 'Hide' : `View ${dDonations.length}`}
                            </button>
                          )}
                          {dDonations.length === 0 && <span className="text-gray-400 text-xs">None</span>}
                        </td>
                      </tr>
                      {isExpanded && dDonations.length > 0 && (
                        <tr key={`${donor.id}-expanded`}>
                          <td colSpan={6} className="bg-gray-50 px-8 py-3">
                            <table className="min-w-full text-xs">
                              <thead>
                                <tr className="text-left font-semibold uppercase tracking-wider text-gray-400">
                                  <th className="pr-4 py-1">Financial Year</th>
                                  <th className="pr-4 py-1">Status</th>
                                  <th className="pr-4 py-1">Pledged</th>
                                  <th className="pr-4 py-1">Received</th>
                                  <th className="pr-4 py-1">Purpose</th>
                                  <th className="pr-4 py-1">18A Issued</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-gray-200">
                                {dDonations.map((don) => (
                                  <tr key={don.id} className="text-gray-700">
                                    <td className="pr-4 py-1">{don.financial_year}</td>
                                    <td className="pr-4 py-1">
                                      <StatusBadge tone={donationStatusTone(don.status)}>
                                        {don.status.replace(/_/g, ' ')}
                                      </StatusBadge>
                                    </td>
                                    <td className="pr-4 py-1">{formatZAR(don.amount_pledged)}</td>
                                    <td className="pr-4 py-1">{formatZAR(don.amount_received)}</td>
                                    <td className="pr-4 py-1">{don.purpose || '—'}</td>
                                    <td className="pr-4 py-1">{don.section_18a_issued ? '✓' : '✗'}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </td>
                        </tr>
                      )}
                    </>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AppShell>
  );
}

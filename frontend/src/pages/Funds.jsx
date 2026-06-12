import { useEffect, useState } from "react";

import { getApiError } from "../api/client.js";
import { dssApi, fundsApi } from "../api/resources.js";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import PageHeader from "../components/PageHeader.jsx";

const money = new Intl.NumberFormat("en-NG", {
  style: "currency",
  currency: "NGN",
  maximumFractionDigits: 0,
});

const initialForm = {
  property_id: "",
  fiscal_year: new Date().getFullYear(),
  annual_budget: 0,
  current_balance: 0,
  reserved_balance: 0,
  currency: "NGN",
};

export default function Funds() {
  const [funds, setFunds] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [allocationForm, setAllocationForm] = useState({
    property_id: "",
    fiscal_year: new Date().getFullYear(),
  });
  const [allocationResult, setAllocationResult] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function loadFunds() {
    try {
      const response = await fundsApi.list();
      setFunds(response.data);
    } catch (err) {
      setError(getApiError(err, "Unable to load funds"));
    }
  }

  useEffect(() => {
    loadFunds();
  }, []);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleCreate(event) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      await fundsApi.create({
        ...form,
        property_id: Number(form.property_id),
        fiscal_year: Number(form.fiscal_year),
        annual_budget: Number(form.annual_budget),
        current_balance: Number(form.current_balance),
        reserved_balance: Number(form.reserved_balance),
      });
      setForm(initialForm);
      await loadFunds();
    } catch (err) {
      setError(getApiError(err, "Unable to save fund"));
    } finally {
      setSaving(false);
    }
  }

  async function handleAutoAllocate(event) {
    event.preventDefault();
    setError("");
    setAllocationResult(null);

    try {
      const response = await dssApi.autoAllocate({
        property_id: Number(allocationForm.property_id),
        fiscal_year: Number(allocationForm.fiscal_year),
      });
      setAllocationResult(response.data);
      await loadFunds();
    } catch (err) {
      setError(getApiError(err, "Unable to allocate funds"));
    }
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Funds" eyebrow="Accounts" />
      <ErrorBanner message={error} />

      <section className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="space-y-5">
          <form className="panel p-4" onSubmit={handleCreate}>
            <h2 className="text-sm font-semibold text-ink">New Fund Account</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <label className="block">
                <span className="label">Property ID</span>
                <input className="field mt-1" type="number" min="1" value={form.property_id} onChange={(e) => updateField("property_id", e.target.value)} required />
              </label>
              <label className="block">
                <span className="label">Fiscal Year</span>
                <input className="field mt-1" type="number" min="2000" value={form.fiscal_year} onChange={(e) => updateField("fiscal_year", e.target.value)} required />
              </label>
              <label className="block">
                <span className="label">Annual Budget</span>
                <input className="field mt-1" type="number" min="0" value={form.annual_budget} onChange={(e) => updateField("annual_budget", e.target.value)} required />
              </label>
              <label className="block">
                <span className="label">Current Balance</span>
                <input className="field mt-1" type="number" min="0" value={form.current_balance} onChange={(e) => updateField("current_balance", e.target.value)} required />
              </label>
              <label className="block">
                <span className="label">Reserved Balance</span>
                <input className="field mt-1" type="number" min="0" value={form.reserved_balance} onChange={(e) => updateField("reserved_balance", e.target.value)} required />
              </label>
              <label className="block">
                <span className="label">Currency</span>
                <input className="field mt-1" maxLength="3" value={form.currency} onChange={(e) => updateField("currency", e.target.value)} required />
              </label>
            </div>
            <button className="btn-primary mt-4 w-full" disabled={saving} type="submit">
              {saving ? "Saving" : "Save fund"}
            </button>
          </form>

          <form className="panel p-4" onSubmit={handleAutoAllocate}>
            <h2 className="text-sm font-semibold text-ink">Automatic Allocation</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <label className="block">
                <span className="label">Property ID</span>
                <input className="field mt-1" type="number" min="1" value={allocationForm.property_id} onChange={(e) => setAllocationForm((current) => ({ ...current, property_id: e.target.value }))} required />
              </label>
              <label className="block">
                <span className="label">Fiscal Year</span>
                <input className="field mt-1" type="number" min="2000" value={allocationForm.fiscal_year} onChange={(e) => setAllocationForm((current) => ({ ...current, fiscal_year: e.target.value }))} required />
              </label>
            </div>
            <button className="btn-secondary mt-4 w-full" type="submit">Run allocation</button>
            {allocationResult ? (
              <div className="mt-4 rounded-md border border-teal-200 bg-teal-50 p-3 text-sm text-teal-900">
                {allocationResult.allocations_created} allocations, {money.format(Number(allocationResult.total_allocated || 0))} reserved.
              </div>
            ) : null}
          </form>
        </div>

        <div className="panel overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px]">
              <thead className="table-head">
                <tr>
                  <th className="px-4 py-3">Property</th>
                  <th className="px-4 py-3">Fiscal Year</th>
                  <th className="px-4 py-3">Budget</th>
                  <th className="px-4 py-3">Balance</th>
                  <th className="px-4 py-3">Reserved</th>
                </tr>
              </thead>
              <tbody>
                {funds.map((fund) => (
                  <tr key={fund.id}>
                    <td className="table-cell">#{fund.property_id}</td>
                    <td className="table-cell">{fund.fiscal_year}</td>
                    <td className="table-cell">{money.format(Number(fund.annual_budget || 0))}</td>
                    <td className="table-cell font-semibold text-brand">{money.format(Number(fund.current_balance || 0))}</td>
                    <td className="table-cell text-amber">{money.format(Number(fund.reserved_balance || 0))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!funds.length ? <div className="p-4"><EmptyState title="No fund accounts found" /></div> : null}
        </div>
      </section>
    </div>
  );
}

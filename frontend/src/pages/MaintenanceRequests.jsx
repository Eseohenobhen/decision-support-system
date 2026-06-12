import { useEffect, useState } from "react";

import { getApiError } from "../api/client.js";
import { maintenanceApi } from "../api/resources.js";
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
  title: "",
  description: "",
  priority: "medium",
  priority_score: 50,
  estimated_cost: 0,
  required_by: "",
};

export default function MaintenanceRequests() {
  const [requests, setRequests] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function loadRequests(filterStatus = status) {
    try {
      const params = filterStatus ? { status: filterStatus } : {};
      const response = await maintenanceApi.list(params);
      setRequests(response.data);
    } catch (err) {
      setError(getApiError(err, "Unable to load requests"));
    }
  }

  useEffect(() => {
    loadRequests("");
  }, []);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleCreate(event) {
    event.preventDefault();
    setSaving(true);
    setError("");

    const payload = {
      ...form,
      property_id: Number(form.property_id),
      priority_score: Number(form.priority_score),
      estimated_cost: Number(form.estimated_cost),
      required_by: form.required_by ? new Date(form.required_by).toISOString() : null,
    };

    try {
      await maintenanceApi.create(payload);
      setForm(initialForm);
      await loadRequests();
    } catch (err) {
      setError(getApiError(err, "Unable to save request"));
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(value) {
    setStatus(value);
    await loadRequests(value);
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Maintenance Requests" eyebrow="Work Queue" />
      <ErrorBanner message={error} />

      <section className="grid gap-5 xl:grid-cols-[0.85fr_1.25fr]">
        <form className="panel p-4" onSubmit={handleCreate}>
          <h2 className="text-sm font-semibold text-ink">New Request</h2>
          <div className="mt-4 grid gap-3">
            <label className="block">
              <span className="label">Property ID</span>
              <input className="field mt-1" type="number" min="1" value={form.property_id} onChange={(e) => updateField("property_id", e.target.value)} required />
            </label>
            <label className="block">
              <span className="label">Title</span>
              <input className="field mt-1" value={form.title} onChange={(e) => updateField("title", e.target.value)} required />
            </label>
            <label className="block">
              <span className="label">Description</span>
              <textarea className="field mt-1 min-h-24" value={form.description} onChange={(e) => updateField("description", e.target.value)} required />
            </label>
            <div className="grid gap-3 sm:grid-cols-3">
              <label className="block">
                <span className="label">Priority</span>
                <select className="field mt-1" value={form.priority} onChange={(e) => updateField("priority", e.target.value)}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </label>
              <label className="block">
                <span className="label">Score</span>
                <input className="field mt-1" type="number" min="1" max="100" value={form.priority_score} onChange={(e) => updateField("priority_score", e.target.value)} required />
              </label>
              <label className="block">
                <span className="label">Estimate</span>
                <input className="field mt-1" type="number" min="0" value={form.estimated_cost} onChange={(e) => updateField("estimated_cost", e.target.value)} required />
              </label>
            </div>
            <label className="block">
              <span className="label">Required By</span>
              <input className="field mt-1" type="datetime-local" value={form.required_by} onChange={(e) => updateField("required_by", e.target.value)} />
            </label>
          </div>
          <button className="btn-primary mt-4 w-full" disabled={saving} type="submit">
            {saving ? "Saving" : "Save request"}
          </button>
        </form>

        <div className="panel overflow-hidden">
          <div className="flex flex-col gap-3 border-b border-line px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-sm font-semibold text-ink">Request Register</h2>
            <select className="field max-w-48" value={status} onChange={(e) => handleStatusChange(e.target.value)}>
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="allocated">Allocated</option>
              <option value="in_progress">In progress</option>
              <option value="completed">Completed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px]">
              <thead className="table-head">
                <tr>
                  <th className="px-4 py-3">Request</th>
                  <th className="px-4 py-3">Property</th>
                  <th className="px-4 py-3">Priority</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Estimate</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((request) => (
                  <tr key={request.id}>
                    <td className="table-cell">
                      <p className="font-semibold text-ink">{request.title}</p>
                      <p className="max-w-xs truncate text-xs text-slate-500">{request.description}</p>
                    </td>
                    <td className="table-cell">#{request.property_id}</td>
                    <td className="table-cell capitalize">{request.priority}</td>
                    <td className="table-cell">{request.priority_score}</td>
                    <td className="table-cell capitalize">{request.status.replaceAll("_", " ")}</td>
                    <td className="table-cell">{money.format(Number(request.estimated_cost || 0))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!requests.length ? <div className="p-4"><EmptyState title="No maintenance requests found" /></div> : null}
        </div>
      </section>
    </div>
  );
}

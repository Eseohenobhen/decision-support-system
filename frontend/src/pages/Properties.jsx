import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getApiError } from "../api/client.js";
import { propertiesApi } from "../api/resources.js";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import PageHeader from "../components/PageHeader.jsx";

const initialForm = {
  code: "",
  name: "",
  address: "",
  city: "",
  state: "",
  country: "Nigeria",
  total_units: 0,
  manager_id: "",
};

export default function Properties() {
  const [properties, setProperties] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function loadProperties() {
    try {
      const response = await propertiesApi.list();
      setProperties(response.data);
    } catch (err) {
      setError(getApiError(err, "Unable to load properties"));
    }
  }

  useEffect(() => {
    loadProperties();
  }, []);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      await propertiesApi.create({
        ...form,
        manager_id: Number(form.manager_id),
        total_units: Number(form.total_units),
      });
      setForm(initialForm);
      await loadProperties();
    } catch (err) {
      setError(getApiError(err, "Unable to save property"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Properties" eyebrow="Portfolio" />
      <ErrorBanner message={error} />

      <section className="grid gap-5 xl:grid-cols-[0.9fr_1.4fr]">
        <form className="panel p-4" onSubmit={handleSubmit}>
          <h2 className="text-sm font-semibold text-ink">New Property</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="code">Code</label>
              <input className="field mt-1" id="code" value={form.code} onChange={(e) => updateField("code", e.target.value)} required />
            </div>
            <div>
              <label className="label" htmlFor="manager">Manager ID</label>
              <input className="field mt-1" id="manager" type="number" min="1" value={form.manager_id} onChange={(e) => updateField("manager_id", e.target.value)} required />
            </div>
            <div className="sm:col-span-2">
              <label className="label" htmlFor="name">Name</label>
              <input className="field mt-1" id="name" value={form.name} onChange={(e) => updateField("name", e.target.value)} required />
            </div>
            <div className="sm:col-span-2">
              <label className="label" htmlFor="address">Address</label>
              <textarea className="field mt-1 min-h-24" id="address" value={form.address} onChange={(e) => updateField("address", e.target.value)} required />
            </div>
            <div>
              <label className="label" htmlFor="city">City</label>
              <input className="field mt-1" id="city" value={form.city} onChange={(e) => updateField("city", e.target.value)} required />
            </div>
            <div>
              <label className="label" htmlFor="state">State</label>
              <input className="field mt-1" id="state" value={form.state} onChange={(e) => updateField("state", e.target.value)} required />
            </div>
            <div>
              <label className="label" htmlFor="country">Country</label>
              <input className="field mt-1" id="country" value={form.country} onChange={(e) => updateField("country", e.target.value)} required />
            </div>
            <div>
              <label className="label" htmlFor="units">Units</label>
              <input className="field mt-1" id="units" type="number" min="0" value={form.total_units} onChange={(e) => updateField("total_units", e.target.value)} required />
            </div>
          </div>
          <button className="btn-primary mt-4 w-full" disabled={saving} type="submit">
            {saving ? "Saving" : "Save property"}
          </button>
        </form>

        <div className="panel overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px]">
              <thead className="table-head">
                <tr>
                  <th className="px-4 py-3">Property</th>
                  <th className="px-4 py-3">Location</th>
                  <th className="px-4 py-3">Units</th>
                  <th className="px-4 py-3">Manager</th>
                  <th className="px-4 py-3">Open</th>
                </tr>
              </thead>
              <tbody>
                {properties.map((property) => (
                  <tr key={property.id}>
                    <td className="table-cell">
                      <p className="font-semibold text-ink">{property.name}</p>
                      <p className="text-xs text-slate-500">{property.code}</p>
                    </td>
                    <td className="table-cell">{property.city}, {property.state}</td>
                    <td className="table-cell">{property.total_units}</td>
                    <td className="table-cell">#{property.manager_id}</td>
                    <td className="table-cell">
                      <Link className="font-semibold text-brand hover:text-teal-800" to={`/properties/${property.id}`}>
                        Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!properties.length ? <div className="p-4"><EmptyState title="No properties found" /></div> : null}
        </div>
      </section>
    </div>
  );
}

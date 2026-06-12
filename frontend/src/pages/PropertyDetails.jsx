import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getApiError } from "../api/client.js";
import { fundsApi, maintenanceApi, propertiesApi } from "../api/resources.js";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatTile from "../components/StatTile.jsx";

const money = new Intl.NumberFormat("en-NG", {
  style: "currency",
  currency: "NGN",
  maximumFractionDigits: 0,
});

export default function PropertyDetails() {
  const { propertyId } = useParams();
  const [property, setProperty] = useState(null);
  const [funds, setFunds] = useState([]);
  const [requests, setRequests] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDetails() {
      try {
        const [propertyRes, fundRes, requestRes] = await Promise.all([
          propertiesApi.detail(propertyId),
          fundsApi.list(),
          maintenanceApi.list({ property_id: propertyId }),
        ]);
        setProperty(propertyRes.data);
        setFunds(fundRes.data.filter((fund) => Number(fund.property_id) === Number(propertyId)));
        setRequests(requestRes.data);
      } catch (err) {
        setError(getApiError(err, "Unable to load property"));
      }
    }

    loadDetails();
  }, [propertyId]);

  const currentBalance = funds.reduce((sum, fund) => sum + Number(fund.current_balance || 0), 0);
  const reservedBalance = funds.reduce((sum, fund) => sum + Number(fund.reserved_balance || 0), 0);

  return (
    <div className="space-y-5">
      <PageHeader
        title={property?.name || "Property Details"}
        eyebrow={property?.code || "Portfolio"}
        actions={<Link className="btn-secondary" to="/properties">Back</Link>}
      />
      <ErrorBanner message={error} />

      {property ? (
        <>
          <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatTile label="Units" value={property.total_units} />
            <StatTile label="Fund Balance" value={money.format(currentBalance)} tone="teal" />
            <StatTile label="Reserved" value={money.format(reservedBalance)} tone="amber" />
            <StatTile label="Requests" value={requests.length} />
          </section>

          <section className="grid gap-5 xl:grid-cols-2">
            <div className="panel p-4">
              <h2 className="text-sm font-semibold text-ink">Address</h2>
              <p className="mt-3 text-sm text-slate-700">{property.address}</p>
              <p className="mt-1 text-sm text-slate-700">{property.city}, {property.state}, {property.country}</p>
            </div>
            <div className="panel p-4">
              <h2 className="text-sm font-semibold text-ink">Manager</h2>
              <p className="mt-3 text-sm text-slate-700">User #{property.manager_id}</p>
            </div>
          </section>

          <section className="panel overflow-hidden">
            <div className="border-b border-line px-4 py-3">
              <h2 className="text-sm font-semibold text-ink">Maintenance Requests</h2>
            </div>
            {requests.length ? (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[640px]">
                  <thead className="table-head">
                    <tr>
                      <th className="px-4 py-3">Title</th>
                      <th className="px-4 py-3">Priority</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Estimate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {requests.map((request) => (
                      <tr key={request.id}>
                        <td className="table-cell font-medium text-ink">{request.title}</td>
                        <td className="table-cell">{request.priority_score}</td>
                        <td className="table-cell capitalize">{request.status.replaceAll("_", " ")}</td>
                        <td className="table-cell">{money.format(Number(request.estimated_cost || 0))}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-4"><EmptyState title="No requests for this property" /></div>
            )}
          </section>
        </>
      ) : null}
    </div>
  );
}

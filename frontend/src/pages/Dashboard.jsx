import { useEffect, useMemo, useState } from "react";

import { fundsApi, maintenanceApi, propertiesApi } from "../api/resources.js";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatTile from "../components/StatTile.jsx";
import { getApiError } from "../api/client.js";

const money = new Intl.NumberFormat("en-NG", {
  style: "currency",
  currency: "NGN",
  maximumFractionDigits: 0,
});

export default function Dashboard() {
  const [properties, setProperties] = useState([]);
  const [funds, setFunds] = useState([]);
  const [requests, setRequests] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const [propertyRes, fundRes, requestRes] = await Promise.all([
          propertiesApi.list(),
          fundsApi.list(),
          maintenanceApi.list(),
        ]);
        setProperties(propertyRes.data);
        setFunds(fundRes.data);
        setRequests(requestRes.data);
      } catch (err) {
        setError(getApiError(err, "Unable to load dashboard"));
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const metrics = useMemo(() => {
    const currentBalance = funds.reduce(
      (sum, fund) => sum + Number(fund.current_balance || 0),
      0,
    );
    const reservedBalance = funds.reduce(
      (sum, fund) => sum + Number(fund.reserved_balance || 0),
      0,
    );
    const highPriority = requests.filter((request) => request.priority_score >= 70).length;
    return {
      currentBalance,
      reservedBalance,
      availableBalance: currentBalance - reservedBalance,
      highPriority,
    };
  }, [funds, requests]);

  return (
    <div className="space-y-5">
      <PageHeader title="Dashboard" eyebrow="Operations" />
      <ErrorBanner message={error} />

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatTile label="Properties" value={loading ? "..." : properties.length} />
        <StatTile label="Available Fund" value={money.format(metrics.availableBalance)} tone="teal" />
        <StatTile label="Reserved Fund" value={money.format(metrics.reservedBalance)} tone="amber" />
        <StatTile label="High Priority" value={metrics.highPriority} tone="red" />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="panel overflow-hidden">
          <div className="border-b border-line px-4 py-3">
            <h2 className="text-sm font-semibold text-ink">Recent Maintenance Requests</h2>
          </div>
          {requests.length ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px]">
                <thead className="table-head">
                  <tr>
                    <th className="px-4 py-3">Request</th>
                    <th className="px-4 py-3">Priority</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Estimate</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.slice(0, 6).map((request) => (
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
            <div className="p-4">
              <EmptyState title="No maintenance requests" />
            </div>
          )}
        </div>

        <div className="panel overflow-hidden">
          <div className="border-b border-line px-4 py-3">
            <h2 className="text-sm font-semibold text-ink">Fund Accounts</h2>
          </div>
          <div className="divide-y divide-line">
            {funds.slice(0, 5).map((fund) => (
              <div key={fund.id} className="px-4 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-ink">FY {fund.fiscal_year}</p>
                  <p className="text-sm font-semibold text-brand">
                    {money.format(Number(fund.current_balance || 0))}
                  </p>
                </div>
                <p className="mt-1 text-xs text-slate-500">Property #{fund.property_id}</p>
              </div>
            ))}
            {!funds.length ? (
              <div className="p-4">
                <EmptyState title="No funds available" />
              </div>
            ) : null}
          </div>
        </div>
      </section>
    </div>
  );
}

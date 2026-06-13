import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

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
    return {
      totalProperties: properties.length,
      totalFundsManaged: currentBalance,
      availableFunds: currentBalance - reservedBalance,
      allocatedFunds: reservedBalance,
    };
  }, [funds, properties]);

  const chartData = useMemo(() => {
    const now = new Date();
    const months = Array.from({ length: 6 }, (_, index) => {
      const date = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() - (5 - index), 1));
      const label = date.toLocaleDateString("en-NG", {
        month: "short",
        year: "numeric",
      });
      return {
        key: `${date.getUTCFullYear()}-${date.getUTCMonth() + 1}`,
        label,
      };
    });

    const spendingByMonth = requests.reduce((acc, request) => {
      const date = request.requested_at ? new Date(request.requested_at) : null;
      if (!date || Number.isNaN(date.valueOf())) {
        return acc;
      }
      const key = `${date.getUTCFullYear()}-${date.getUTCMonth() + 1}`;
      const approved = Number(request.approved_cost ?? 0);
      if (approved > 0) {
        acc[key] = (acc[key] || 0) + approved;
      }
      return acc;
    }, {});

    const requestedByMonth = requests.reduce((acc, request) => {
      const date = request.requested_at ? new Date(request.requested_at) : null;
      if (!date || Number.isNaN(date.valueOf())) {
        return acc;
      }
      const key = `${date.getUTCFullYear()}-${date.getUTCMonth() + 1}`;
      acc[key] = (acc[key] || 0) + Number(request.estimated_cost || 0);
      return acc;
    }, {});

    return months.map(({ key, label }) => ({
      month: label,
      monthlyMaintenanceSpending: spendingByMonth[key] || 0,
      allocationTrend: requestedByMonth[key] || 0,
    }));
  }, [requests]);

  return (
    <div className="space-y-5">
      <PageHeader title="Dashboard" eyebrow="Operations" />
      <ErrorBanner message={error} />

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatTile
          label="Total Properties"
          value={loading ? "..." : metrics.totalProperties}
        />
        <StatTile
          label="Total Funds Managed"
          value={loading ? "..." : money.format(metrics.totalFundsManaged)}
        />
        <StatTile
          label="Available Funds"
          value={loading ? "..." : money.format(metrics.availableFunds)}
          tone="teal"
        />
        <StatTile
          label="Allocated Funds"
          value={loading ? "..." : money.format(metrics.allocatedFunds)}
          tone="amber"
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
        <div className="panel px-4 py-4">
          <div className="mb-4 flex items-center justify-between gap-3 border-b border-line pb-3">
            <div>
              <h2 className="text-sm font-semibold text-ink">Monthly Maintenance Spending</h2>
              <p className="text-xs text-slate-500">Approved maintenance cost per month.</p>
            </div>
          </div>
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 12, left: -12, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tickLine={false} axisLine={false} />
                <YAxis tickFormatter={(value) => money.format(value)} width={72} />
                <Tooltip formatter={(value) => money.format(value)} />
                <Bar dataKey="monthlyMaintenanceSpending" fill="#22c55e" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel px-4 py-4">
          <div className="mb-4 flex items-center justify-between gap-3 border-b border-line pb-3">
            <div>
              <h2 className="text-sm font-semibold text-ink">Allocation Trend</h2>
              <p className="text-xs text-slate-500">Trend of requested and approved allocations.</p>
            </div>
          </div>
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 20, right: 12, left: -12, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tickLine={false} axisLine={false} />
                <YAxis tickFormatter={(value) => money.format(value)} width={72} />
                <Tooltip formatter={(value) => money.format(value)} />
                <Legend verticalAlign="top" height={32} />
                <Line type="monotone" dataKey="allocationTrend" stroke="#2563eb" strokeWidth={3} dot={false} name="Requested Cost" />
                <Line type="monotone" dataKey="monthlyMaintenanceSpending" stroke="#f59e0b" strokeWidth={3} dot={false} name="Approved Spending" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
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

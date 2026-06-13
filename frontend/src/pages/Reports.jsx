import { useState } from "react";

import PageHeader from "../components/PageHeader.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { reportsApi } from "../api/resources.js";
import { getApiError } from "../api/client.js";

const reportItems = [
  {
    key: "propertySummary",
    label: "Property Summary",
    description: "Download a detailed summary of all properties and managers.",
    filename: "property-summary",
  },
  {
    key: "fundAllocation",
    label: "Fund Allocation Report",
    description: "Export current fund balances, reserved funds, and allocations.",
    filename: "fund-allocation-report",
  },
  {
    key: "maintenanceHistory",
    label: "Maintenance History",
    description: "Generate a complete history of maintenance requests and approvals.",
    filename: "maintenance-history",
  },
  {
    key: "monthlyFinancial",
    label: "Monthly Financial Report",
    description: "Create a monthly financial report for fund transactions.",
    filename: "monthly-financial-report",
  },
];

const availableFormats = ["pdf", "xlsx"];

export default function Reports() {
  const [format, setFormat] = useState("pdf");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function downloadReport(apiMethod, filename) {
    try {
      setError("");
      setLoading(true);
      const response = await reportsApi[apiMethod](format);
      const blob = new Blob([response.data], { type: response.headers["content-type"] });
      const downloadUrl = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = downloadUrl;
      anchor.download = `${filename}.${format}`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      setError(getApiError(err, "Unable to download report"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Reports" eyebrow="Analytics" />
      <ErrorBanner message={error} />

      <section className="panel p-6">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-ink">Export Reports</h2>
            <p className="text-sm text-slate-500">
              Choose a report and download it as PDF or Excel.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <label className="label mb-0">Format</label>
            <select
              className="field w-full max-w-xs"
              value={format}
              onChange={(event) => setFormat(event.target.value)}
            >
              {availableFormats.map((option) => (
                <option key={option} value={option}>
                  {option.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {reportItems.map((report) => (
            <div key={report.key} className="rounded-3xl border border-line bg-white p-5 shadow-sm">
              <p className="text-sm font-semibold text-ink">{report.label}</p>
              <p className="mt-2 text-sm leading-6 text-slate-600">{report.description}</p>
              <button
                className="btn-primary mt-5 w-full"
                disabled={loading}
                type="button"
                onClick={() => downloadReport(report.key, report.filename)}
              >
                {loading ? "Preparing…" : `Download ${format.toUpperCase()}`}
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

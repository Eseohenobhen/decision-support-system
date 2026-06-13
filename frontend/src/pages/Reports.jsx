import PageHeader from "../components/PageHeader.jsx";

export default function Reports() {
  return (
    <div className="space-y-5">
      <PageHeader title="Reports" eyebrow="Analytics" />
      <div className="panel p-6">
        <p className="text-sm text-slate-600">
          Reporting tools and export options will appear here once enabled.
        </p>
      </div>
    </div>
  );
}

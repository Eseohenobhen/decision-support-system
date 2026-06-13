import PageHeader from "../components/PageHeader.jsx";

export default function DSSRecommendations() {
  return (
    <div className="space-y-5">
      <PageHeader title="DSS Recommendations" eyebrow="Decision Support" />
      <div className="panel p-6">
        <p className="text-sm text-slate-600">
          This area will display decision-support recommendations for maintenance allocations.
        </p>
      </div>
    </div>
  );
}

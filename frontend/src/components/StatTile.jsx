export default function StatTile({ label, value, tone = "default" }) {
  const tones = {
    default: "border-line bg-white",
    teal: "border-teal-200 bg-teal-50",
    amber: "border-amber-200 bg-amber-50",
    red: "border-red-200 bg-red-50",
  };

  return (
    <div className={`rounded-lg border px-4 py-3 ${tones[tone]}`}>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
    </div>
  );
}

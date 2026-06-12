export default function EmptyState({ title, detail }) {
  return (
    <div className="rounded-md border border-dashed border-line bg-field px-4 py-8 text-center">
      <p className="text-sm font-semibold text-ink">{title}</p>
      {detail ? <p className="mt-1 text-sm text-slate-500">{detail}</p> : null}
    </div>
  );
}

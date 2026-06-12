export default function PageHeader({ title, eyebrow, actions }) {
  return (
    <div className="flex flex-col gap-3 border-b border-line bg-white px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        {eyebrow ? <p className="label">{eyebrow}</p> : null}
        <h1 className="mt-1 text-xl font-semibold text-ink">{title}</h1>
      </div>
      {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
    </div>
  );
}

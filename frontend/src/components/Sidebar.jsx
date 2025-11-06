
export default function Sidebar({ current, setCurrent }) {
  const tabs = ["Dashboard","Prompt","Sources","Saved"];
  return (
    <div className="sidebar">
      {tabs.map((t) => (
        <button key={t} onClick={() => setCurrent(t)} className={current === t ? "active" : ""}>
          {t === "Dashboard" ? "📰 Νέα" : t === "Prompt" ? "💬 Prompt" : t === "Sources" ? "🌐 Πηγές" : "⭐ Saved"}
        </button>
      ))}
    </div>
  );
}

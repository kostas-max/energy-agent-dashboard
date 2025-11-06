
import { useEffect, useState } from "react";
export default function Saved() {
  const [items, setItems] = useState([]);
  useEffect(()=>{ fetch("http://localhost:8000/saved").then(r=>r.json()).then(d=>setItems(d.news||[])); },[]);
  return (
    <div>
      <h2>⭐ Saved</h2>
      {items.map((n,i)=>(
        <div key={i} className="card">
          <a href={n.url} target="_blank" rel="noreferrer"><b>{n.title}</b></a>
          <div style={{color:"#6B7280", fontSize:14}}>{n.date} — {n.source} — {n.topic}</div>
          {n.summary && <p>{n.summary}</p>}
        </div>
      ))}
      {!items.length && <div className="card">Δεν υπάρχουν αποθηκευμένα σημαντικά.</div>}
    </div>
  );
}

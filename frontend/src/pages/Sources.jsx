
import { useEffect, useState } from "react";
export default function Sources() {
  const [list,setList]=useState([]); const [url,setUrl]=useState("");
  const load=()=>{ fetch("http://localhost:8000/sources").then(r=>r.json()).then(d=>setList(d.sources||[])); };
  useEffect(()=>{ load(); },[]);
  const add=async()=>{ await fetch("http://localhost:8000/sources/add",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url})}); setUrl(""); load(); };
  const remove=async(u)=>{ await fetch("http://localhost:8000/sources/remove",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:u})}); load(); };
  return (
    <div>
      <h2>🌐 Πηγές</h2>
      <div className="card" style={{display:"flex",gap:8}}>
        <input style={{flex:1}} value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://..." />
        <button onClick={add}>Προσθήκη</button>
      </div>
      {list.map((s,i)=>(
        <div key={i} className="card" style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
          <div><div><b>{s.url}</b></div><div style={{color:"#6B7280",fontSize:14}}>{s.type} — Last check: {s.last_check || "-"}</div></div>
          <button onClick={()=>remove(s.url)}>Διαγραφή</button>
        </div>
      ))}
      {!list.length && <div className="card">Δεν υπάρχουν πηγές.</div>}
    </div>
  );
}

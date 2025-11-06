
import { useState } from "react";
export default function PromptConsole() {
  const [prompt, setPrompt] = useState(""); const [history, setHistory] = useState([]);
  const send = async () => {
    const res = await fetch("http://localhost:8000/prompt",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt})});
    const data = await res.json();
    setHistory([...history,{role:"user",text:prompt},{role:"agent",text:data.reply}]); setPrompt("");
  };
  return (
    <div>
      <h2>💬 Prompt</h2>
      <div className="card" style={{minHeight:200,maxHeight:300,overflowY:"auto"}}>
        {history.map((m,i)=>(<div key={i} style={{margin:"6px 0", color:m.role==="user"?"#2563EB":"#047857"}}><b>{m.role==="user"?"Εσύ:":"Agent:"}</b> {m.text}</div>))}
      </div>
      <div style={{display:"flex",gap:8}}>
        <input style={{flex:1}} value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="Γράψε εντολή..." />
        <button onClick={send}>Αποστολή</button>
      </div>
    </div>
  );
}

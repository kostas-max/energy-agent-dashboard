
import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import PromptConsole from "./pages/PromptConsole";
import Sources from "./pages/Sources";
import Saved from "./pages/Saved";
import "./styles.css";

export default function App() {
  const [tab, setTab] = useState("Dashboard");
  return (
    <div className="app-container">
      <Sidebar current={tab} setCurrent={setTab} />
      <div className="content">
        {tab === "Dashboard" && <Dashboard />}
        {tab === "Prompt" && <PromptConsole />}
        {tab === "Sources" && <Sources />}
        {tab === "Saved" && <Saved />}
      </div>
    </div>
  );
}

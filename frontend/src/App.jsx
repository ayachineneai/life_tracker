import { BrowserRouter, NavLink, Routes, Route } from "react-router-dom"
import Dashboard from "./pages/Dashboard"
import Weight from "./pages/Weight"
import Diet from "./pages/Diet"
import Training from "./pages/Training"
import Cardio from "./pages/Cardio"
import Spending from "./pages/Spending"
import Piano from "./pages/Piano"
import "./App.css"

const nav = [
  { to: "/",         label: "📊 大盘" },
  { to: "/weight",   label: "⚖️ 体重" },
  { to: "/diet",     label: "🍱 饮食" },
  { to: "/training", label: "🏋️ 训练" },
  { to: "/cardio",   label: "🏃 有氧" },
  { to: "/spending", label: "💰 消费" },
  { to: "/piano",    label: "🎹 练琴" },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="layout">
        <nav className="sidebar">
          <div className="logo">Life Tracker</div>
          {nav.map(n => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === "/"}
              className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <main className="content">
          <Routes>
            <Route path="/"         element={<Dashboard />} />
            <Route path="/weight"   element={<Weight />} />
            <Route path="/diet"     element={<Diet />} />
            <Route path="/training" element={<Training />} />
            <Route path="/cardio"   element={<Cardio />} />
            <Route path="/spending" element={<Spending />} />
            <Route path="/piano"    element={<Piano />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

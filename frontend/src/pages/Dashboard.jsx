import { useNavigate } from "react-router-dom"
import ReactECharts from "echarts-for-react"
import { api } from "../api"
import { useFetch } from "../hooks/useFetch"

function MiniLine({ data, xKey, yKey, color }) {
  if (!data?.length) return <div className="empty">暂无数据</div>
  return (
    <ReactECharts style={{ height: 80 }} option={{
      grid: { top: 4, bottom: 4, left: 4, right: 4 },
      xAxis: { type: "category", data: data.map(d => d[xKey]), show: false },
      yAxis: { type: "value", show: false },
      series: [{
        type: "line", data: data.map(d => d[yKey]),
        smooth: true, symbol: "none",
        lineStyle: { color, width: 2 },
        areaStyle: { color, opacity: 0.1 },
      }],
      tooltip: { trigger: "axis" },
    }} />
  )
}

function StatCard({ label, value, unit, color, to, children }) {
  const nav = useNavigate()
  return (
    <div className="card" onClick={() => nav(to)}>
      <div className="card-label">{label}</div>
      <div>
        <span className="card-value" style={{ color }}>{value ?? "—"}</span>
        {unit && <span className="card-unit">{unit}</span>}
      </div>
      {children}
    </div>
  )
}

export default function Dashboard() {
  const { data, loading } = useFetch(api.dashboard)

  if (loading) return <div className="loading">加载中…</div>

  const { today, trends } = data

  return (
    <div>
      <h1>监控大盘</h1>

      <div className="cards">
        <StatCard label="最新体重" value={today.weight_kg} unit="kg" color="#4f46e5" to="/weight">
          <MiniLine data={trends.weight} xKey="date" yKey="weight_kg" color="#4f46e5" />
        </StatCard>

        <StatCard label="今日摄入" value={today.calories} unit="kcal" color="#f59e0b" to="/diet">
          <MiniLine data={trends.calories} xKey="date" yKey="calories" color="#f59e0b" />
        </StatCard>

        <StatCard label="今日训练" value={today.training_count} unit="次" color="#10b981" to="/training" />

        <StatCard label="今日练琴" value={today.piano_min} unit="分钟" color="#8b5cf6" to="/piano">
          <MiniLine data={trends.piano} xKey="date" yKey="duration_min" color="#8b5cf6" />
        </StatCard>

        <StatCard label="今日消费" value={today.spending?.toFixed(0)} unit="元" color="#ef4444" to="/spending">
          <MiniLine data={trends.spending} xKey="date" yKey="amount" color="#ef4444" />
        </StatCard>

        <StatCard label="本月消费" value={today.month_spending?.toFixed(0)} unit="元" color="#f97316" to="/spending" />
      </div>
    </div>
  )
}

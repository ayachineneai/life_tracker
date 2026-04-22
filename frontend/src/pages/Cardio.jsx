import ReactECharts from "echarts-for-react"
import { api } from "../api"
import { useFetch } from "../hooks/useFetch"

export default function Cardio() {
  const { data: records, loading: l1 } = useFetch(() => api.cardio({ limit: 60 }))
  const { data: byType,  loading: l2 } = useFetch(api.cardioByType)

  if (l1 || l2) return <div className="loading">加载中…</div>
  if (!records?.length) return <div className="empty">暂无数据</div>

  const sorted = [...records].reverse()

  const barOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: sorted.map(d => d.occurred_at.slice(0, 10)) },
    yAxis: { type: "value", name: "分钟" },
    series: [{
      type: "bar", data: sorted.map(d => d.duration_min),
      itemStyle: { color: "#06b6d4", borderRadius: [4, 4, 0, 0] },
    }],
  }

  const pieOption = {
    tooltip: { trigger: "item", formatter: "{b}: {c} 分钟 ({d}%)" },
    series: [{
      type: "pie", radius: ["40%", "70%"],
      data: byType?.map(d => ({ name: d.type, value: d.total_min })) ?? [],
    }],
  }

  return (
    <div>
      <h1>🏃 有氧</h1>
      <div className="charts" style={{ marginBottom: 24 }}>
        <div className="chart-box">
          <h2>训练时长</h2>
          <ReactECharts option={barOption} style={{ height: 280 }} />
        </div>
        <div className="chart-box">
          <h2>类型分布</h2>
          <ReactECharts option={pieOption} style={{ height: 280 }} />
        </div>
      </div>
      <div className="section">
        <h2>记录</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th><th>类型</th><th>时长</th>
              <th>速度</th><th>坡度</th><th>距离</th>
              <th>训练时间</th><th>记录时间</th>
            </tr>
          </thead>
          <tbody>
            {records.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.type}</td>
                <td>{r.duration_min} 分钟</td>
                <td>{r.speed_kmh    ? `${r.speed_kmh} km/h`  : "—"}</td>
                <td>{r.incline_pct  ? `${r.incline_pct}%`    : "—"}</td>
                <td>{r.distance_km  ? `${r.distance_km} km`  : "—"}</td>
                <td>{r.occurred_at}</td>
                <td>{r.recorded_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

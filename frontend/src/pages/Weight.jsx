import ReactECharts from "echarts-for-react"
import { api } from "../api"
import { useFetch } from "../hooks/useFetch"

export default function Weight() {
  const { data, loading } = useFetch(() => api.weight({ limit: 90 }))

  if (loading) return <div className="loading">加载中…</div>
  if (!data?.length) return <div className="empty">暂无数据</div>

  const sorted = [...data].reverse()

  const chartOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: sorted.map(d => d.occurred_at.slice(0, 10)) },
    yAxis: { type: "value", scale: true, name: "kg" },
    series: [{
      type: "line", data: sorted.map(d => d.weight_kg),
      smooth: true, symbol: "circle", symbolSize: 6,
      lineStyle: { color: "#4f46e5" },
      itemStyle: { color: "#4f46e5" },
      areaStyle: { color: "#4f46e5", opacity: 0.08 },
    }],
  }

  return (
    <div>
      <h1>⚖️ 体重</h1>
      <div className="section">
        <h2>趋势</h2>
        <ReactECharts option={chartOption} style={{ height: 300 }} />
      </div>
      <div className="section">
        <h2>记录</h2>
        <table>
          <thead><tr><th>ID</th><th>体重</th><th>称重时间</th><th>记录时间</th></tr></thead>
          <tbody>
            {data.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.weight_kg} kg</td>
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

import ReactECharts from "echarts-for-react"
import { api } from "../api"
import { useFetch } from "../hooks/useFetch"

export default function Diet() {
  const { data: daily, loading: l1 } = useFetch(() => api.dietDaily({ limit: 30 }))
  const { data: records, loading: l2 } = useFetch(() => api.diet({ limit: 50 }))

  if (l1 || l2) return <div className="loading">加载中…</div>

  const chartOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: daily?.map(d => d.date) ?? [] },
    yAxis: { type: "value", name: "kcal" },
    series: [{
      type: "bar", data: daily?.map(d => d.calories) ?? [],
      itemStyle: { color: "#f59e0b", borderRadius: [4, 4, 0, 0] },
    }],
  }

  return (
    <div>
      <h1>🍱 饮食</h1>
      <div className="section">
        <h2>每日热量</h2>
        <ReactECharts option={chartOption} style={{ height: 280 }} />
      </div>
      <div className="section">
        <h2>记录</h2>
        <table>
          <thead><tr><th>ID</th><th>热量</th><th>内容</th><th>用餐时间</th><th>记录时间</th></tr></thead>
          <tbody>
            {records?.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.calories} kcal</td>
                <td>{r.notes || "—"}</td>
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

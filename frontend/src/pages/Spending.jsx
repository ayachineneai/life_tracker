import ReactECharts from "echarts-for-react"
import { api } from "../api"
import { useFetch } from "../hooks/useFetch"

export default function Spending() {
  const { data: byCategory, loading: l1 } = useFetch(api.spendingByCategory)
  const { data: monthly, loading: l2 }    = useFetch(api.spendingMonthly)
  const { data: records, loading: l3 }    = useFetch(() => api.spending({ limit: 100 }))

  if (l1 || l2 || l3) return <div className="loading">加载中…</div>

  const pieOption = {
    tooltip: { trigger: "item", formatter: "{b}: ¥{c} ({d}%)" },
    series: [{
      type: "pie", radius: ["40%", "70%"],
      data: byCategory?.map(d => ({ name: d.category, value: d.total.toFixed(2) })) ?? [],
      label: { formatter: "{b}\n¥{c}" },
    }],
  }

  const barOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: monthly?.map(d => d.month).reverse() ?? [] },
    yAxis: { type: "value", name: "元" },
    series: [{
      type: "bar", data: monthly?.map(d => d.total.toFixed(2)).reverse() ?? [],
      itemStyle: { color: "#ef4444", borderRadius: [4, 4, 0, 0] },
    }],
  }

  return (
    <div>
      <h1>💰 消费</h1>
      <div className="charts" style={{ marginBottom: 24 }}>
        <div className="chart-box">
          <h2>分类占比</h2>
          <ReactECharts option={pieOption} style={{ height: 300 }} />
        </div>
        <div className="chart-box">
          <h2>月度趋势</h2>
          <ReactECharts option={barOption} style={{ height: 300 }} />
        </div>
      </div>
      <div className="section">
        <h2>记录</h2>
        <table>
          <thead><tr><th>ID</th><th>金额</th><th>类别</th><th>备注</th><th>支付时间</th><th>记录时间</th></tr></thead>
          <tbody>
            {records?.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>¥{r.amount}</td>
                <td>{r.category}</td>
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

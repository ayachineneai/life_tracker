import ReactECharts from "echarts-for-react"
import { api } from "../api"
import { useFetch } from "../hooks/useFetch"

export default function Piano() {
  const { data: records, loading: l1 } = useFetch(() => api.piano({ limit: 60 }))
  const { data: byPiece, loading: l2 } = useFetch(api.pianoByPiece)

  if (l1 || l2) return <div className="loading">加载中…</div>
  if (!records?.length) return <div className="empty">暂无数据</div>

  const sorted = [...records].reverse()

  const lineOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: sorted.map(d => d.occurred_at.slice(0, 10)) },
    yAxis: { type: "value", name: "分钟" },
    series: [{
      type: "bar", data: sorted.map(d => d.duration_min),
      itemStyle: { color: "#8b5cf6", borderRadius: [4, 4, 0, 0] },
    }],
  }

  const pieOption = {
    tooltip: { trigger: "item", formatter: "{b}: {c} 分钟 ({d}%)" },
    series: [{
      type: "pie", radius: ["40%", "70%"],
      data: byPiece?.map(d => ({ name: d.piece, value: d.total_min })) ?? [],
    }],
  }

  return (
    <div>
      <h1>🎹 练琴</h1>
      <div className="charts" style={{ marginBottom: 24 }}>
        <div className="chart-box">
          <h2>练琴时长</h2>
          <ReactECharts option={lineOption} style={{ height: 280 }} />
        </div>
        <div className="chart-box">
          <h2>曲目分布</h2>
          <ReactECharts option={pieOption} style={{ height: 280 }} />
        </div>
      </div>
      <div className="section">
        <h2>记录</h2>
        <table>
          <thead><tr><th>ID</th><th>曲目</th><th>时长</th><th>小节</th><th>练琴时间</th><th>记录时间</th></tr></thead>
          <tbody>
            {records.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.piece}</td>
                <td>{r.duration_min} 分钟</td>
                <td>{r.measures_from && r.measures_to ? `${r.measures_from}–${r.measures_to}` : "—"}</td>
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

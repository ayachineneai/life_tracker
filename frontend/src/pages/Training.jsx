import { useState } from "react"
import ReactECharts from "echarts-for-react"
import { api } from "../api"
import { useFetch } from "../hooks/useFetch"

function ExerciseChart({ name }) {
  const { data, loading } = useFetch(() => api.exerciseHistory(name), [name])
  if (loading) return <div className="loading">加载中…</div>
  if (!data?.length) return null

  const sorted = [...data].reverse()
  const option = {
    tooltip: { trigger: "axis" },
    legend: { data: ["最大重量", "总组数"] },
    xAxis: { type: "category", data: sorted.map(d => d.started_at?.slice(0, 10)) },
    yAxis: [
      { type: "value", name: "kg" },
      { type: "value", name: "组", position: "right" },
    ],
    series: [
      {
        name: "最大重量", type: "line", smooth: true,
        data: sorted.map(d => Math.max(...d.sets.map(s => s.weight_kg))),
        itemStyle: { color: "#10b981" },
      },
      {
        name: "总组数", type: "bar", yAxisIndex: 1,
        data: sorted.map(d => d.sets.length),
        itemStyle: { color: "#10b981", opacity: 0.3, borderRadius: [4, 4, 0, 0] },
      },
    ],
  }
  return <ReactECharts option={option} style={{ height: 240 }} />
}

export default function Training() {
  const { data, loading } = useFetch(() => api.training({ limit: 20 }))
  const [selected, setSelected] = useState(null)

  if (loading) return <div className="loading">加载中…</div>
  if (!data?.length) return <div className="empty">暂无数据</div>

  const exercises = [...new Set(data.flatMap(s => s.exercises.map(e => e.exercise)))]

  return (
    <div>
      <h1>🏋️ 训练</h1>

      {exercises.length > 0 && (
        <div className="section">
          <h2>动作进步曲线</h2>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
            {exercises.map(e => (
              <button key={e}
                onClick={() => setSelected(e)}
                style={{
                  padding: "4px 12px", borderRadius: 20, border: "none", cursor: "pointer",
                  background: selected === e ? "#10b981" : "#f0f0f0",
                  color: selected === e ? "#fff" : "#333", fontSize: 13,
                }}>
                {e}
              </button>
            ))}
          </div>
          {selected && <ExerciseChart name={selected} />}
        </div>
      )}

      <div className="section">
        <h2>训练记录</h2>
        {data.map(s => (
          <div key={s.id} style={{ marginBottom: 20, borderBottom: "1px solid #f0f0f0", paddingBottom: 16 }}>
            <div style={{ fontWeight: 600, marginBottom: 8 }}>
              {s.title}
              <span style={{ fontSize: 12, color: "#888", marginLeft: 12 }}>
                {s.started_at} {s.ended_at ? `→ ${s.ended_at}` : ""}
              </span>
            </div>
            <table>
              <thead><tr><th>动作</th><th>组数</th><th>组详情</th></tr></thead>
              <tbody>
                {s.exercises.map(e => (
                  <tr key={e.id}>
                    <td>{e.exercise}</td>
                    <td>{e.sets.length} 组</td>
                    <td>{e.sets.map((s, i) => `第${i+1}组: ${s.reps}次 × ${s.weight_kg}kg`).join(" | ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  )
}

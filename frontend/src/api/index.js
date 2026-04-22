const BASE = import.meta.env.VITE_API_URL ?? ""

async function get(path, params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v))
  ).toString()
  const res = await fetch(`${BASE}${path}${query ? "?" + query : ""}`)
  return res.json()
}

export const api = {
  dashboard:           ()             => get("/api/dashboard"),
  weight:              (p)            => get("/api/weight", p),
  diet:                (p)            => get("/api/diet", p),
  dietDaily:           (p)            => get("/api/diet/daily", p),
  training:            (p)            => get("/api/training", p),
  exerciseHistory:     (name, p)      => get(`/api/training/exercise/${encodeURIComponent(name)}`, p),
  spending:            (p)            => get("/api/spending", p),
  spendingByCategory:  (p)            => get("/api/spending/by-category", p),
  spendingMonthly:     ()             => get("/api/spending/monthly"),
  piano:               (p)            => get("/api/piano", p),
  pianoByPiece:        (p)            => get("/api/piano/by-piece", p),
  cardio:              (p)            => get("/api/cardio", p),
  cardioByType:        (p)            => get("/api/cardio/by-type", p),
}

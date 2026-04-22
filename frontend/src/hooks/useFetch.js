import { useState, useEffect } from "react"

export function useFetch(fn, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fn().then(d => { setData(d); setLoading(false) })
  }, deps)

  return { data, loading }
}

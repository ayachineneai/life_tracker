import json
import os
import sqlite3
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "/Users/ayachinene/WorkSpace/mcp/life_data.db")

app = FastAPI(title="Life Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows(conn, sql, params=None):
    return [dict(r) for r in conn.execute(sql, params or []).fetchall()]


# ── Dashboard ────────────────────────────────────────────────────────────────

@app.get("/api/dashboard")
def dashboard():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    month_start = datetime.now().strftime("%Y-%m-01")

    with get_db() as conn:
        # 最新体重
        latest_weight = conn.execute(
            "SELECT weight_kg, occurred_at FROM weight ORDER BY occurred_at DESC LIMIT 1"
        ).fetchone()

        # 今日热量
        today_calories = conn.execute(
            "SELECT COALESCE(SUM(calories), 0) as total FROM diet WHERE occurred_at >= ?",
            (today,)
        ).fetchone()["total"]

        # 今日训练
        today_training = conn.execute(
            "SELECT COUNT(*) as count FROM training_sessions WHERE started_at >= ?",
            (today,)
        ).fetchone()["count"]

        # 今日练琴
        today_piano = conn.execute(
            "SELECT COALESCE(SUM(duration_min), 0) as total FROM piano WHERE occurred_at >= ?",
            (today,)
        ).fetchone()["total"]

        # 今日消费
        today_spending = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM spending WHERE occurred_at >= ?",
            (today,)
        ).fetchone()["total"]

        # 本月消费
        month_spending = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM spending WHERE occurred_at >= ?",
            (month_start,)
        ).fetchone()["total"]

        # 近 7 天体重趋势
        weight_trend = rows(conn,
            "SELECT DATE(occurred_at) as date, weight_kg FROM weight "
            "WHERE occurred_at >= ? ORDER BY occurred_at",
            ((datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),)
        )

        # 近 7 天热量趋势
        calorie_trend = rows(conn,
            "SELECT DATE(occurred_at) as date, SUM(calories) as calories FROM diet "
            "WHERE occurred_at >= ? GROUP BY DATE(occurred_at) ORDER BY date",
            ((datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),)
        )

        # 近 7 天消费趋势
        spending_trend = rows(conn,
            "SELECT DATE(occurred_at) as date, SUM(amount) as amount FROM spending "
            "WHERE occurred_at >= ? GROUP BY DATE(occurred_at) ORDER BY date",
            ((datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),)
        )

        # 近 7 天练琴趋势
        piano_trend = rows(conn,
            "SELECT DATE(occurred_at) as date, SUM(duration_min) as duration_min FROM piano "
            "WHERE occurred_at >= ? GROUP BY DATE(occurred_at) ORDER BY date",
            ((datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),)
        )

    return {
        "today": {
            "weight_kg": dict(latest_weight)["weight_kg"] if latest_weight else None,
            "calories": today_calories,
            "training_count": today_training,
            "piano_min": today_piano,
            "spending": today_spending,
            "month_spending": month_spending,
        },
        "trends": {
            "weight": weight_trend,
            "calories": calorie_trend,
            "spending": spending_trend,
            "piano": piano_trend,
        }
    }


# ── Weight ────────────────────────────────────────────────────────────────────

@app.get("/api/weight")
def get_weight(start: str = "", end: str = "", limit: int = 90):
    sql, params, clauses = "SELECT * FROM weight", [], []
    if start: clauses.append("occurred_at >= ?"); params.append(start)
    if end:   clauses.append("occurred_at <= ?"); params.append(end)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return rows(conn, sql, params)


# ── Diet ──────────────────────────────────────────────────────────────────────

@app.get("/api/diet")
def get_diet(start: str = "", end: str = "", limit: int = 90):
    sql, params, clauses = "SELECT * FROM diet", [], []
    if start: clauses.append("occurred_at >= ?"); params.append(start)
    if end:   clauses.append("occurred_at <= ?"); params.append(end)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return rows(conn, sql, params)


@app.get("/api/diet/daily")
def get_diet_daily(start: str = "", end: str = ""):
    sql = """
        SELECT DATE(occurred_at) as date, SUM(calories) as calories, COUNT(*) as meals
        FROM diet
    """
    params, clauses = [], []
    if start: clauses.append("occurred_at >= ?"); params.append(start)
    if end:   clauses.append("occurred_at <= ?"); params.append(end)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " GROUP BY DATE(occurred_at) ORDER BY date"
    with get_db() as conn:
        return rows(conn, sql, params)


# ── Training ──────────────────────────────────────────────────────────────────

@app.get("/api/training")
def get_training(start: str = "", end: str = "", limit: int = 30):
    sql, params, clauses = "SELECT * FROM training_sessions", [], []
    if start: clauses.append("started_at >= ?"); params.append(start)
    if end:   clauses.append("started_at <= ?"); params.append(end)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY started_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        sessions = rows(conn, sql, params)
        for s in sessions:
            ex_rows = conn.execute(
                "SELECT * FROM training_exercises WHERE session_id = ?", (s["id"],)
            ).fetchall()
            s["exercises"] = [{**dict(r), "sets": json.loads(r["sets"])} for r in ex_rows]
    return sessions


@app.get("/api/training/exercise/{exercise_name}")
def get_exercise_history(exercise_name: str, limit: int = 30):
    """Get history of a specific exercise for progress tracking."""
    with get_db() as conn:
        ex_rows = conn.execute(
            """SELECT e.*, s.started_at FROM training_exercises e
               JOIN training_sessions s ON e.session_id = s.id
               WHERE e.exercise = ? ORDER BY s.started_at DESC LIMIT ?""",
            (exercise_name, limit)
        ).fetchall()
        return [{**dict(r), "sets": json.loads(r["sets"])} for r in ex_rows]


# ── Cardio ───────────────────────────────────────────────────────────────────

@app.get("/api/cardio")
def get_cardio(start: str = "", end: str = "", type: str = "", limit: int = 60):
    sql, params, clauses = "SELECT * FROM cardio", [], []
    if start: clauses.append("occurred_at >= ?"); params.append(start)
    if end:   clauses.append("occurred_at <= ?"); params.append(end)
    if type:  clauses.append("type = ?");         params.append(type)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return rows(conn, sql, params)


@app.get("/api/cardio/by-type")
def get_cardio_by_type(start: str = "", end: str = ""):
    sql = """
        SELECT type, COUNT(*) as sessions, SUM(duration_min) as total_min
        FROM cardio
    """
    params, clauses = [], []
    if start: clauses.append("occurred_at >= ?"); params.append(start)
    if end:   clauses.append("occurred_at <= ?"); params.append(end)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " GROUP BY type ORDER BY total_min DESC"
    with get_db() as conn:
        return rows(conn, sql, params)


# ── Spending ──────────────────────────────────────────────────────────────────

@app.get("/api/spending")
def get_spending(start: str = "", end: str = "", category: str = "", limit: int = 100):
    sql, params, clauses = "SELECT * FROM spending", [], []
    if start:    clauses.append("occurred_at >= ?"); params.append(start)
    if end:      clauses.append("occurred_at <= ?"); params.append(end)
    if category: clauses.append("category = ?");    params.append(category)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return rows(conn, sql, params)


@app.get("/api/spending/by-category")
def get_spending_by_category(start: str = "", end: str = ""):
    sql = "SELECT category, SUM(amount) as total, COUNT(*) as count FROM spending"
    params, clauses = [], []
    if start: clauses.append("occurred_at >= ?"); params.append(start)
    if end:   clauses.append("occurred_at <= ?"); params.append(end)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " GROUP BY category ORDER BY total DESC"
    with get_db() as conn:
        return rows(conn, sql, params)


@app.get("/api/spending/monthly")
def get_spending_monthly():
    sql = """
        SELECT strftime('%Y-%m', occurred_at) as month,
               SUM(amount) as total, COUNT(*) as count
        FROM spending
        GROUP BY month ORDER BY month DESC LIMIT 12
    """
    with get_db() as conn:
        return rows(conn, sql)


# ── Piano ─────────────────────────────────────────────────────────────────────

@app.get("/api/piano")
def get_piano(start: str = "", end: str = "", limit: int = 90):
    sql, params, clauses = "SELECT * FROM piano", [], []
    if start: clauses.append("occurred_at >= ?"); params.append(start)
    if end:   clauses.append("occurred_at <= ?"); params.append(end)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return rows(conn, sql, params)


@app.get("/api/piano/by-piece")
def get_piano_by_piece(start: str = "", end: str = ""):
    sql = "SELECT piece, SUM(duration_min) as total_min, COUNT(*) as sessions FROM piano"
    params, clauses = [], []
    if start: clauses.append("occurred_at >= ?"); params.append(start)
    if end:   clauses.append("occurred_at <= ?"); params.append(end)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " GROUP BY piece ORDER BY total_min DESC"
    with get_db() as conn:
        return rows(conn, sql, params)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)

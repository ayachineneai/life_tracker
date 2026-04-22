import json
import os
import sqlite3
from datetime import datetime

import uvicorn
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

load_dotenv()

DB_PATH    = os.getenv("DB_PATH", "/Users/ayachinene/WorkSpace/mcp/life_data.db")
TRANSPORT  = os.getenv("TRANSPORT", "stdio")
HOST       = os.getenv("HOST", "0.0.0.0")
PORT       = int(os.getenv("PORT", "8000"))
MCP_TOKEN  = os.getenv("MCP_TOKEN", "")

VALID_TABLES = {"weight", "diet", "training_sessions", "training_exercises", "cardio", "piano", "spending"}

mcp = FastMCP("Life Tracker")


# ── Auth middleware ───────────────────────────────────────────────────────────

class BearerAuthMiddleware:
    def __init__(self, app: ASGIApp, token: str):
        self.app = app
        self.token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            auth = headers.get(b"authorization", b"").decode()
            provided = auth.removeprefix("Bearer ").strip()
            if provided != self.token:
                res = Response("Unauthorized", status_code=401)
                await res(scope, receive, send)
                return
        await self.app(scope, receive, send)


# ── DB ────────────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS weight (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            weight_kg    REAL NOT NULL,
            occurred_at  TEXT NOT NULL,
            recorded_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS diet (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            calories     REAL NOT NULL,
            notes        TEXT,
            image_path   TEXT,
            occurred_at  TEXT NOT NULL,
            recorded_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS training_sessions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            notes        TEXT,
            started_at   TEXT NOT NULL,
            ended_at     TEXT,
            recorded_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS training_exercises (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id   INTEGER NOT NULL REFERENCES training_sessions(id),
            exercise     TEXT NOT NULL,
            sets         TEXT NOT NULL,
            recorded_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cardio (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            type         TEXT NOT NULL,
            duration_min INTEGER NOT NULL,
            speed_kmh    REAL,
            incline_pct  REAL,
            distance_km  REAL,
            occurred_at  TEXT NOT NULL,
            recorded_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS spending (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            amount       REAL NOT NULL,
            category     TEXT NOT NULL,
            notes        TEXT,
            occurred_at  TEXT NOT NULL,
            recorded_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS piano (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            piece          TEXT    NOT NULL,
            duration_min   INTEGER NOT NULL,
            measures_from  INTEGER,
            measures_to    INTEGER,
            occurred_at    TEXT NOT NULL,
            recorded_at    TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Weight ────────────────────────────────────────────────────────────────────

@mcp.tool()
def add_weight(weight_kg: float, occurred_at: str) -> str:
    """Record body weight (kg). occurred_at: when you weighed yourself, e.g. '2026-04-22 08:00:00'."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO weight (weight_kg, occurred_at, recorded_at) VALUES (?, ?, ?)",
            (weight_kg, occurred_at, now())
        )
    return f"Saved weight {weight_kg}kg at {occurred_at}"


@mcp.tool()
def get_weight(start_date: str = "", end_date: str = "", limit: int = 30) -> list:
    """Get weight records with their IDs."""
    sql, params, clauses = "SELECT * FROM weight", [], []
    if start_date: clauses.append("occurred_at >= ?"); params.append(start_date)
    if end_date:   clauses.append("occurred_at <= ?"); params.append(end_date)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


@mcp.tool()
def update_weight(id: int, weight_kg: float = 0, occurred_at: str = "") -> str:
    """Update a weight record by id."""
    fields, params = [], []
    if weight_kg:   fields.append("weight_kg = ?");   params.append(weight_kg)
    if occurred_at: fields.append("occurred_at = ?"); params.append(occurred_at)
    if not fields: return "Nothing to update"
    params.append(id)
    with get_db() as conn:
        conn.execute(f"UPDATE weight SET {', '.join(fields)} WHERE id = ?", params)
    return f"Updated weight id={id}"


# ── Diet ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def add_diet(
    calories: float,
    occurred_at: str,
    notes: str = "",
    image_path: str = "",
) -> str:
    """Record a meal.
    calories: kcal.
    occurred_at: when the meal happened, e.g. '2026-04-22 08:00:00'.
    notes: what was eaten, e.g. '米饭、鸡胸肉、西兰花'.
    image_path: optional local file path."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO diet (calories, notes, image_path, occurred_at, recorded_at) VALUES (?, ?, ?, ?, ?)",
            (calories, notes or None, image_path or None, occurred_at, now())
        )
    return f"Saved diet {calories}kcal at {occurred_at}"


@mcp.tool()
def get_diet(start_date: str = "", end_date: str = "", limit: int = 30) -> list:
    """Get diet records with their IDs."""
    sql, params, clauses = "SELECT * FROM diet", [], []
    if start_date: clauses.append("created_at >= ?"); params.append(start_date)
    if end_date:   clauses.append("created_at <= ?"); params.append(end_date)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


@mcp.tool()
def update_diet(
    id: int,
    calories: float = 0,
    notes: str = "",
    image_path: str = "",
    occurred_at: str = "",
) -> str:
    """Update a diet record by id."""
    fields, params = [], []
    if calories:     fields.append("calories = ?");    params.append(calories)
    if notes:        fields.append("notes = ?");       params.append(notes)
    if image_path:   fields.append("image_path = ?");  params.append(image_path)
    if occurred_at:  fields.append("occurred_at = ?"); params.append(occurred_at)
    if not fields: return "Nothing to update"
    params.append(id)
    with get_db() as conn:
        conn.execute(f"UPDATE diet SET {', '.join(fields)} WHERE id = ?", params)
    return f"Updated diet id={id}"


# ── Training ──────────────────────────────────────────────────────────────────

@mcp.tool()
def add_training_session(title: str, started_at: str, notes: str = "") -> dict:
    """Start a training session. Returns session_id for adding exercises.
    started_at: when the training started, e.g. '2026-04-22 09:00:00'."""
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO training_sessions (title, notes, started_at, recorded_at) VALUES (?, ?, ?, ?)",
            (title, notes or None, started_at, now())
        )
        return {"session_id": cur.lastrowid, "started_at": started_at}


@mcp.tool()
def end_training_session(session_id: int, ended_at: str) -> str:
    """Mark a training session as finished.
    ended_at: when the training ended, e.g. '2026-04-22 10:30:00'."""
    with get_db() as conn:
        conn.execute("UPDATE training_sessions SET ended_at = ? WHERE id = ?", (ended_at, session_id))
    return f"Session {session_id} ended at {ended_at}"


@mcp.tool()
def get_training_sessions(start_date: str = "", end_date: str = "", limit: int = 20) -> list:
    """Get training sessions with all exercises."""
    sql, params, clauses = "SELECT * FROM training_sessions", [], []
    if start_date: clauses.append("started_at >= ?"); params.append(start_date)
    if end_date:   clauses.append("started_at <= ?"); params.append(end_date)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY started_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        sessions = [dict(r) for r in conn.execute(sql, params).fetchall()]
        for s in sessions:
            rows = conn.execute(
                "SELECT * FROM training_exercises WHERE session_id = ?", (s["id"],)
            ).fetchall()
            s["exercises"] = [{**dict(r), "sets": json.loads(r["sets"])} for r in rows]
    return sessions


@mcp.tool()
def update_training_session(
    id: int, title: str = "", started_at: str = "", ended_at: str = "", notes: str = ""
) -> str:
    """Update a training session by id."""
    fields, params = [], []
    if title:      fields.append("title = ?");      params.append(title)
    if started_at: fields.append("started_at = ?"); params.append(started_at)
    if ended_at:   fields.append("ended_at = ?");   params.append(ended_at)
    if notes:      fields.append("notes = ?");      params.append(notes)
    if not fields: return "Nothing to update"
    params.append(id)
    with get_db() as conn:
        conn.execute(f"UPDATE training_sessions SET {', '.join(fields)} WHERE id = ?", params)
    return f"Updated session id={id}"


@mcp.tool()
def add_exercise(session_id: int, exercise: str, sets: list) -> str:
    """Add an exercise to a training session.
    sets: [{"reps": 10, "weight_kg": 80}, {"reps": 8, "weight_kg": 85}]"""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO training_exercises (session_id, exercise, sets, recorded_at) VALUES (?, ?, ?, ?)",
            (session_id, exercise, json.dumps(sets), now())
        )
    return f"Saved {exercise} {len(sets)} sets"


@mcp.tool()
def update_exercise(id: int, exercise: str = "", sets: list = []) -> str:
    """Update an exercise record by id."""
    fields, params = [], []
    if exercise: fields.append("exercise = ?"); params.append(exercise)
    if sets:     fields.append("sets = ?");     params.append(json.dumps(sets))
    if not fields: return "Nothing to update"
    params.append(id)
    with get_db() as conn:
        conn.execute(f"UPDATE training_exercises SET {', '.join(fields)} WHERE id = ?", params)
    return f"Updated exercise id={id}"


# ── Cardio ───────────────────────────────────────────────────────────────────

@mcp.tool()
def add_cardio(
    type: str, duration_min: int, occurred_at: str,
    speed_kmh: float = 0, incline_pct: float = 0, distance_km: float = 0,
) -> str:
    """Record a cardio session.
    type: 爬坡 / 跑步 / 骑行 / 椭圆机 etc.
    speed_kmh / incline_pct / distance_km are optional depending on type."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO cardio (type, duration_min, speed_kmh, incline_pct, distance_km, occurred_at, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (type, duration_min, speed_kmh or None, incline_pct or None, distance_km or None, occurred_at, now())
        )
    return f"Saved cardio: {type} {duration_min}min at {occurred_at}"


@mcp.tool()
def get_cardio(start_date: str = "", end_date: str = "", type: str = "", limit: int = 50) -> list:
    """Get cardio records with their IDs."""
    sql, params, clauses = "SELECT * FROM cardio", [], []
    if start_date: clauses.append("occurred_at >= ?"); params.append(start_date)
    if end_date:   clauses.append("occurred_at <= ?"); params.append(end_date)
    if type:       clauses.append("type = ?");         params.append(type)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


@mcp.tool()
def update_cardio(
    id: int, type: str = "", duration_min: int = 0,
    speed_kmh: float = 0, incline_pct: float = 0,
    distance_km: float = 0, occurred_at: str = "",
) -> str:
    """Update a cardio record by id."""
    fields, params = [], []
    if type:         fields.append("type = ?");         params.append(type)
    if duration_min: fields.append("duration_min = ?"); params.append(duration_min)
    if speed_kmh:    fields.append("speed_kmh = ?");    params.append(speed_kmh)
    if incline_pct:  fields.append("incline_pct = ?");  params.append(incline_pct)
    if distance_km:  fields.append("distance_km = ?");  params.append(distance_km)
    if occurred_at:  fields.append("occurred_at = ?");  params.append(occurred_at)
    if not fields: return "Nothing to update"
    params.append(id)
    with get_db() as conn:
        conn.execute(f"UPDATE cardio SET {', '.join(fields)} WHERE id = ?", params)
    return f"Updated cardio id={id}"


# ── Spending ─────────────────────────────────────────────────────────────────

@mcp.tool()
def add_spending(amount: float, category: str, occurred_at: str, notes: str = "") -> str:
    """Record a spending. category: e.g. 餐饮/交通/购物/娱乐/医疗.
    occurred_at: when the payment happened, e.g. '2026-04-22 14:00:00'."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO spending (amount, category, notes, occurred_at, recorded_at) VALUES (?, ?, ?, ?, ?)",
            (amount, category, notes or None, occurred_at, now())
        )
    return f"Saved spending {amount} ({category}) at {occurred_at}"


@mcp.tool()
def get_spending(start_date: str = "", end_date: str = "", category: str = "", limit: int = 50) -> list:
    """Get spending records with their IDs."""
    sql, params, clauses = "SELECT * FROM spending", [], []
    if start_date: clauses.append("occurred_at >= ?"); params.append(start_date)
    if end_date:   clauses.append("occurred_at <= ?"); params.append(end_date)
    if category:   clauses.append("category = ?");    params.append(category)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


@mcp.tool()
def update_spending(
    id: int, amount: float = 0, category: str = "", notes: str = "", occurred_at: str = ""
) -> str:
    """Update a spending record by id."""
    fields, params = [], []
    if amount:      fields.append("amount = ?");      params.append(amount)
    if category:    fields.append("category = ?");    params.append(category)
    if notes:       fields.append("notes = ?");       params.append(notes)
    if occurred_at: fields.append("occurred_at = ?"); params.append(occurred_at)
    if not fields: return "Nothing to update"
    params.append(id)
    with get_db() as conn:
        conn.execute(f"UPDATE spending SET {', '.join(fields)} WHERE id = ?", params)
    return f"Updated spending id={id}"


# ── Piano ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def add_piano(
    piece: str, duration_min: int, occurred_at: str,
    measures_from: int = 0, measures_to: int = 0,
) -> str:
    """Record a piano practice session.
    occurred_at: when you practiced, e.g. '2026-04-22 20:00:00'.
    measures_from/to: bar range, e.g. 1 to 32."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO piano (piece, duration_min, measures_from, measures_to, occurred_at, recorded_at) VALUES (?, ?, ?, ?, ?, ?)",
            (piece, duration_min, measures_from or None, measures_to or None, occurred_at, now())
        )
    return f"Saved piano: {piece} {duration_min}min at {occurred_at}"


@mcp.tool()
def get_piano(start_date: str = "", end_date: str = "", limit: int = 30) -> list:
    """Get piano practice records with their IDs."""
    sql, params, clauses = "SELECT * FROM piano", [], []
    if start_date: clauses.append("occurred_at >= ?"); params.append(start_date)
    if end_date:   clauses.append("occurred_at <= ?"); params.append(end_date)
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY occurred_at DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


@mcp.tool()
def update_piano(
    id: int, piece: str = "", duration_min: int = 0,
    measures_from: int = 0, measures_to: int = 0, occurred_at: str = ""
) -> str:
    """Update a piano record by id."""
    fields, params = [], []
    if piece:         fields.append("piece = ?");         params.append(piece)
    if duration_min:  fields.append("duration_min = ?");  params.append(duration_min)
    if measures_from: fields.append("measures_from = ?"); params.append(measures_from)
    if measures_to:   fields.append("measures_to = ?");   params.append(measures_to)
    if occurred_at:   fields.append("occurred_at = ?");   params.append(occurred_at)
    if not fields: return "Nothing to update"
    params.append(id)
    with get_db() as conn:
        conn.execute(f"UPDATE piano SET {', '.join(fields)} WHERE id = ?", params)
    return f"Updated piano id={id}"


# ── 通用删除 ──────────────────────────────────────────────────────────────────

@mcp.tool()
def delete_record(table: str, id: int) -> str:
    """Delete any record by table name and id.
    table: weight / diet / training_sessions / training_exercises / piano"""
    if table not in VALID_TABLES:
        return f"Invalid table: {table}"
    with get_db() as conn:
        conn.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
    return f"Deleted {table} id={id}"


# ── 启动 ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if TRANSPORT == "http":
        app = mcp.streamable_http_app()
        authed = BearerAuthMiddleware(app, MCP_TOKEN)
        uvicorn.run(authed, host=HOST, port=PORT)
    else:
        mcp.run()

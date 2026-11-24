from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3, os, secrets, hmac, functools
from datetime import datetime, timezone

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "competition.db")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
# Admin password: set SMART_GUARD_ADMIN_PASSWORD, otherwise a random one is generated and printed at startup.
ADMIN_PASSWORD = os.environ.get("SMART_GUARD_ADMIN_PASSWORD") or secrets.token_urlsafe(9)

def admin_required(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            if request.path.startswith("/api/"):
                return jsonify(error="Admin login required"), 401
            return redirect("/")
        return view(*args, **kwargs)
    return wrapper

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS laptops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            last_seen TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(team_id, name),
            FOREIGN KEY(team_id) REFERENCES teams(id)
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            laptop_id INTEGER,
            event_type TEXT NOT NULL,
            detail TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'info',
            created_at TEXT NOT NULL,
            reviewed INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(team_id) REFERENCES teams(id),
            FOREIGN KEY(laptop_id) REFERENCES laptops(id)
        );
        """)

def add_event(con, team_id, laptop_id, event_type, detail, severity="info"):
    con.execute(
        "INSERT INTO events(team_id,laptop_id,event_type,detail,severity,created_at) VALUES(?,?,?,?,?,?)",
        (team_id, laptop_id, event_type[:60], detail[:500], severity, now())
    )

@app.route("/")
def index():
    if not session.get("admin"):
        return render_template("login.html", error=None)
    return render_template("index.html")

@app.get("/join")
def join_page():
    return render_template("join.html")

@app.post("/login")
def login():
    pw = request.form.get("password", "")
    if hmac.compare_digest(pw.encode(), ADMIN_PASSWORD.encode()):
        session["admin"] = True
        return redirect("/")
    return render_template("login.html", error="Password தவறு"), 401

@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.get("/api/teams")
@admin_required
def teams():
    with db() as con:
        rows = con.execute("""
          SELECT t.id,t.name,t.code,t.created_at,
          COUNT(l.id) AS laptop_count,
          SUM(CASE WHEN l.last_seen >= datetime('now','-90 seconds') THEN 1 ELSE 0 END) AS online_count
          FROM teams t LEFT JOIN laptops l ON l.team_id=t.id GROUP BY t.id ORDER BY t.id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows])

@app.post("/api/teams")
@admin_required
def create_team():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(error="Team name is required"), 400
    code = secrets.token_urlsafe(5).replace("-", "").replace("_", "").upper()[:8]
    try:
        with db() as con:
            con.execute("INSERT INTO teams(name,code,created_at) VALUES(?,?,?)", (name, code, now()))
        return jsonify(ok=True, name=name, code=code)
    except sqlite3.IntegrityError:
        return jsonify(error="இந்த Team Name ஏற்கனவே உள்ளது"), 409

def get_or_create_laptop(con, team, laptop_name):
    row = con.execute("SELECT id FROM laptops WHERE team_id=? AND name=?", (team["id"], laptop_name)).fetchone()
    if row:
        laptop_id = row["id"]
        con.execute("UPDATE laptops SET last_seen=? WHERE id=?", (now(), laptop_id))
    else:
        cur = con.execute("INSERT INTO laptops(team_id,name,last_seen,created_at) VALUES(?,?,?,?)",
                          (team["id"], laptop_name, now(), now()))
        laptop_id = cur.lastrowid
    return laptop_id

@app.post("/api/heartbeat")
def heartbeat():
    data = request.get_json(silent=True) or {}
    code = (data.get("team_code") or "").strip().upper()
    laptop_name = (data.get("laptop_name") or "").strip()[:80]
    if not code or not laptop_name:
        return jsonify(error="team_code and laptop_name are required"), 400
    with db() as con:
        team = con.execute("SELECT * FROM teams WHERE code=?", (code,)).fetchone()
        if not team:
            return jsonify(error="Invalid team code"), 404
        laptop_id = get_or_create_laptop(con, team, laptop_name)
        return jsonify(ok=True, laptop_id=laptop_id, server_time=now())

@app.post("/api/events")
def receive_event():
    data = request.get_json(silent=True) or {}
    code = (data.get("team_code") or "").strip().upper()
    laptop_name = (data.get("laptop_name") or "").strip()[:80]
    event_type = (data.get("event_type") or "browser_event").strip()
    detail = (data.get("detail") or "").strip()
    severity = (data.get("severity") or "info").lower()
    if severity not in ("info", "warning", "alert"):
        severity = "info"
    if not code or not laptop_name or not detail:
        return jsonify(error="team_code, laptop_name and detail are required"), 400
    with db() as con:
        team = con.execute("SELECT * FROM teams WHERE code=?", (code,)).fetchone()
        if not team:
            return jsonify(error="Invalid team code"), 404
        laptop_id = get_or_create_laptop(con, team, laptop_name)
        add_event(con, team["id"], laptop_id, event_type, detail, severity)
    return jsonify(ok=True)

@app.get("/api/dashboard")
@admin_required
def dashboard():
    with db() as con:
        teams = con.execute("""
          SELECT t.id,t.name,t.code,
          COUNT(DISTINCT l.id) AS laptop_count,
          COUNT(DISTINCT CASE WHEN l.last_seen >= datetime('now','-90 seconds') THEN l.id END) AS online_count
          FROM teams t LEFT JOIN laptops l ON l.team_id=t.id GROUP BY t.id ORDER BY t.name
        """).fetchall()
        laptops = con.execute("""
          SELECT l.id,l.name,l.last_seen,t.name AS team_name,t.code,
          CASE WHEN l.last_seen >= datetime('now','-90 seconds') THEN 1 ELSE 0 END AS online,
          EXISTS(SELECT 1 FROM events e WHERE e.laptop_id=l.id AND e.event_type='RESTRICTED_AI_SITE') AS ai_used
          FROM laptops l JOIN teams t ON t.id=l.team_id ORDER BY t.name,l.name
        """).fetchall()
        events = con.execute("""
          SELECT e.id,e.event_type,e.detail,e.severity,e.created_at,e.reviewed,
          t.name AS team_name,l.name AS laptop_name
          FROM events e JOIN teams t ON t.id=e.team_id
          LEFT JOIN laptops l ON l.id=e.laptop_id ORDER BY e.id DESC LIMIT 100
        """).fetchall()
        alert_count = con.execute("SELECT COUNT(*) FROM events WHERE severity='alert' AND reviewed=0").fetchone()[0]
        latest_ai_alert = con.execute("SELECT COALESCE(MAX(id),0) FROM events WHERE event_type='RESTRICTED_AI_SITE'").fetchone()[0]
    return jsonify(teams=[dict(x) for x in teams], laptops=[dict(x) for x in laptops],
                   events=[dict(x) for x in events], pending_alerts=alert_count, latest_ai_alert_id=latest_ai_alert)

@app.post("/api/events/<int:event_id>/review")
@admin_required
def review_event(event_id):
    with db() as con:
        cur = con.execute("UPDATE events SET reviewed=1 WHERE id=?", (event_id,))
        if cur.rowcount == 0:
            return jsonify(error="Event not found"), 404
    return jsonify(ok=True)

@app.get("/api/server-info")
@admin_required
def server_info():
    import socket
    ip = "127.0.0.1"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("10.255.255.255", 1))  # no packet is actually sent
        ip = sock.getsockname()[0]
        sock.close()
    except OSError:
        pass
    return jsonify(lan_url=f"http://{ip}:5000", port=5000)

@app.get("/health")
def health():
    return jsonify(ok=True, service="Smart Competition Guard")

# Initialize database for both local and Render deployment
init_db()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False
    )
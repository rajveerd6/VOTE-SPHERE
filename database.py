# database.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'election.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_roll(roll):
    """Normalize roll: '1' -> '1', '01' -> '1', '09' -> '9'."""
    roll = (roll or '').strip()
    try:
        # If it's a plain number, strip leading zeros
        if roll.isdigit():
            return str(int(roll))
    except Exception:
        pass
    return roll


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        gender TEXT NOT NULL CHECK(gender IN ('Girl', 'Boy'))
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll TEXT NOT NULL UNIQUE,
        candidate_id INTEGER NOT NULL,
        gender TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (roll) REFERENCES voters(roll),
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')

    # Both admin panel and view-result use the same password: IamAdmin
    c.execute("INSERT OR IGNORE INTO settings VALUES ('admin_password', 'IamAdmin')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('result_password', 'IamAdmin')")

    conn.commit()
    conn.close()


# ---------- Candidates ----------
def get_all_candidates():
    conn = get_db()
    rows = conn.execute("SELECT id, name FROM candidates ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_candidate(name):
    conn = get_db()
    try:
        conn.execute("INSERT INTO candidates (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except Exception as e:
        return str(e)
    finally:
        conn.close()


def remove_candidate(cid):
    conn = get_db()
    conn.execute("DELETE FROM votes WHERE candidate_id = ?", (cid,))
    conn.execute("DELETE FROM candidates WHERE id = ?", (cid,))
    conn.commit()
    conn.close()


# ---------- Voters ----------
def get_all_voters():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, roll, name, gender FROM voters ORDER BY CAST(roll AS INTEGER)"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_voter_by_roll(roll):
    roll = normalize_roll(roll)
    conn = get_db()
    row = conn.execute("SELECT * FROM voters WHERE roll = ?", (roll,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_voter(roll, name, gender):
    roll = normalize_roll(roll)
    conn = get_db()
    try:
        conn.execute("INSERT INTO voters (roll, name, gender) VALUES (?, ?, ?)",
                     (roll, name, gender))
        conn.commit()
        return True
    except Exception as e:
        return str(e)
    finally:
        conn.close()


def remove_voter(roll):
    roll = normalize_roll(roll)
    conn = get_db()
    conn.execute("DELETE FROM votes WHERE roll = ?", (roll,))
    conn.execute("DELETE FROM voters WHERE roll = ?", (roll,))
    conn.commit()
    conn.close()


# ---------- Votes ----------
def has_voted(roll):
    roll = normalize_roll(roll)
    conn = get_db()
    row = conn.execute("SELECT 1 FROM votes WHERE roll = ?", (roll,)).fetchone()
    conn.close()
    return row is not None


def cast_vote(roll, candidate_id, gender):
    roll = normalize_roll(roll)
    conn = get_db()
    try:
        conn.execute("INSERT INTO votes (roll, candidate_id, gender) VALUES (?, ?, ?)",
                     (roll, candidate_id, gender))
        conn.commit()
        return True
    except Exception as e:
        return str(e)
    finally:
        conn.close()


def get_all_votes():
    """Full audit — who voted whom."""
    conn = get_db()
    rows = conn.execute('''
        SELECT v.roll, vo.name AS voter_name, c.name AS candidate_name, v.gender, v.timestamp
        FROM votes v
        JOIN voters vo ON v.roll = vo.roll
        JOIN candidates c ON v.candidate_id = c.id
        ORDER BY v.timestamp
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_results():
    """
    Public results — no voter identity.
    Per candidate: total votes, boys votes, girls votes.
    """
    conn = get_db()
    rows = conn.execute('''
        SELECT c.id, c.name,
               SUM(CASE WHEN v.gender = 'Girl' THEN 1 ELSE 0 END) AS girls,
               SUM(CASE WHEN v.gender = 'Boy' THEN 1 ELSE 0 END) AS boys,
               COUNT(v.id) AS total
        FROM candidates c
        LEFT JOIN votes v ON v.candidate_id = c.id
        GROUP BY c.id, c.name
        ORDER BY total DESC, c.name ASC
    ''').fetchall()
    conn.close()
    results = [dict(r) for r in rows]
    winner = results[0] if results and results[0]['total'] > 0 else None
    return {"candidates": results, "winner": winner}


def reset_votes():
    conn = get_db()
    conn.execute("DELETE FROM votes")
    conn.commit()
    conn.close()


def reset_everything():
    conn = get_db()
    conn.execute("DELETE FROM votes")
    conn.execute("DELETE FROM voters")
    conn.execute("DELETE FROM candidates")
    conn.commit()
    conn.close()


# ---------- Settings ----------
def get_setting(key):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row['value'] if row else None


def set_setting(key, value):
    conn = get_db()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value)
    )
    conn.commit()
    conn.close()
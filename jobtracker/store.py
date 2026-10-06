"""SQLite-backed storage for job applications."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date

STATUSES = ("applied", "screening", "interview", "offer", "rejected", "withdrawn")

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'applied',
    source TEXT NOT NULL DEFAULT '',
    pay_per_hour REAL,
    applied_on TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
)
"""


@dataclass
class Application:
    id: int
    company: str
    role: str
    status: str
    source: str
    pay_per_hour: float | None
    applied_on: str
    notes: str


class Store:
    def __init__(self, path: str = "applications.db"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def add(
        self,
        company: str,
        role: str,
        source: str = "",
        pay_per_hour: float | None = None,
        applied_on: str | None = None,
        notes: str = "",
    ) -> int:
        if not company.strip() or not role.strip():
            raise ValueError("company and role are required")
        cur = self.conn.execute(
            "INSERT INTO applications (company, role, source, pay_per_hour, applied_on, notes)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (company.strip(), role.strip(), source, pay_per_hour, applied_on or date.today().isoformat(), notes),
        )
        self.conn.commit()
        return cur.lastrowid

    def set_status(self, app_id: int, status: str) -> None:
        if status not in STATUSES:
            raise ValueError(f"status must be one of: {', '.join(STATUSES)}")
        cur = self.conn.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
        if cur.rowcount == 0:
            raise KeyError(f"no application with id {app_id}")
        self.conn.commit()

    def list(self, status: str | None = None) -> list[Application]:
        query = "SELECT * FROM applications"
        params: tuple = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        rows = self.conn.execute(query + " ORDER BY applied_on DESC, id DESC", params).fetchall()
        return [Application(**dict(r)) for r in rows]

    def summary(self) -> dict[str, int]:
        counts = {s: 0 for s in STATUSES}
        for row in self.conn.execute("SELECT status, COUNT(*) AS n FROM applications GROUP BY status"):
            counts[row["status"]] = row["n"]
        counts["total"] = sum(counts.values())
        return counts

    def close(self) -> None:
        self.conn.close()

import json
import hashlib
from datetime import datetime, timezone

from database.db import DatabaseManager


class AuditService:
    _actor_user_id = None
    _actor_username = None

    def __init__(self):
        self.db = DatabaseManager()

    @classmethod
    def set_actor(cls, user_id=None, username=None):
        cls._actor_user_id = user_id
        cls._actor_username = username

    @classmethod
    def clear_actor(cls):
        cls.set_actor()

    def log_event(self, action_type, record_id=None, summary=None, actor_username=None, actor_user_id=None):
        safe_summary = summary if isinstance(summary, dict) else {"result": str(summary or "")}
        payload = json.dumps(safe_summary, sort_keys=True, separators=(",", ":"))
        previous_hash = self.db.execute_scalar("SELECT event_hash FROM audit_events ORDER BY id DESC LIMIT 1") or "GENESIS"
        occurred_at = datetime.now(timezone.utc).isoformat()
        canonical = json.dumps({
            "occurred_at_utc": occurred_at,
            "actor_user_id": actor_user_id if actor_user_id is not None else self._actor_user_id,
            "actor_username": actor_username if actor_username is not None else self._actor_username,
            "action_type": action_type,
            "record_id": str(record_id) if record_id is not None else None,
            "summary_json": payload,
            "previous_hash": previous_hash,
        }, sort_keys=True, separators=(",", ":"))
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.db.execute_query(
            "INSERT INTO audit_events "
            "(occurred_at_utc, actor_user_id, actor_username, action_type, record_id, summary_json, previous_hash, event_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                occurred_at,
                actor_user_id if actor_user_id is not None else self._actor_user_id,
                actor_username if actor_username is not None else self._actor_username,
                action_type,
                str(record_id) if record_id is not None else None,
                payload,
                previous_hash,
                event_hash,
            ),
        )

    def list_events(self, action_filter="", limit=500):
        query = "SELECT * FROM audit_events"
        params = []
        if action_filter:
            query += " WHERE action_type LIKE ?"
            params.append(f"%{action_filter}%")
        query += " ORDER BY id DESC LIMIT ?"
        params.append(int(limit))
        return self.db.execute_read(query, tuple(params))
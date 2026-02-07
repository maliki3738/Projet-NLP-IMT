import os
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiomysql

from chainlit.data.base import BaseDataLayer
from chainlit.data.utils import queue_until_user_message
from chainlit.types import Feedback, PaginatedResponse, Pagination, ThreadDict, ThreadFilter

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _now() -> datetime:
    return datetime.utcnow()


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _dt_to_iso(value: Optional[datetime]) -> Optional[str]:
    if not value:
        return None
    return value.isoformat() + "Z"


def _json_dumps(value: Any) -> str:
    return json.dumps(value or {}, ensure_ascii=False)


def _json_loads(value: Optional[str]) -> Dict:
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


class MySQLDataLayer(BaseDataLayer):
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[aiomysql.Pool] = None

    @classmethod
    def from_env(cls) -> "MySQLDataLayer":
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL manquant pour MySQL Data Layer")
        return cls(database_url)

    async def connect(self):
        if self.pool:
            return
        url = urlparse(self.database_url)
        self.pool = await aiomysql.create_pool(
            host=url.hostname or "localhost",
            port=url.port or 3306,
            user=url.username or "root",
            password=url.password or "",
            db=(url.path or "/").lstrip("/") or "chainlit",
            autocommit=True,
            cursorclass=aiomysql.DictCursor,
            minsize=1,
            maxsize=5,
            pool_recycle=3600,
            echo=False,
        )

    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:  # type: ignore
            async with conn.cursor() as cur:
                await cur.execute(query, params or {})
                if cur.description:
                    rows = await cur.fetchall()
                    return list(rows)
                return []

    async def get_user(self, identifier: str):
        rows = await self.execute(
            "SELECT * FROM User WHERE identifier=%(identifier)s",
            {"identifier": identifier},
        )
        if not rows:
            return None
        row = rows[0]
        return {
            "id": row["id"],
            "identifier": row["identifier"],
            "createdAt": _dt_to_iso(row["createdAt"]),
            "metadata": _json_loads(row.get("metadata")),
        }

    async def create_user(self, user):
        now = _now()
        user_id = str(uuid.uuid4())
        await self.execute(
            """
            INSERT INTO User (id, identifier, metadata, createdAt, updatedAt)
            VALUES (%(id)s, %(identifier)s, %(metadata)s, %(createdAt)s, %(updatedAt)s)
            ON DUPLICATE KEY UPDATE metadata=%(metadata)s, updatedAt=%(updatedAt)s
            """,
            {
                "id": user_id,
                "identifier": user.identifier,
                "metadata": _json_dumps(user.metadata),
                "createdAt": now,
                "updatedAt": now,
            },
        )
        return await self.get_user(user.identifier)

    async def delete_feedback(self, feedback_id: str) -> bool:
        await self.execute("DELETE FROM Feedback WHERE id=%(id)s", {"id": feedback_id})
        return True

    async def upsert_feedback(self, feedback: Feedback) -> str:
        feedback_id = feedback.id or str(uuid.uuid4())
        now = _now()
        await self.execute(
            """
            INSERT INTO Feedback (id, stepId, name, value, comment, createdAt, updatedAt)
            VALUES (%(id)s, %(stepId)s, %(name)s, %(value)s, %(comment)s, %(createdAt)s, %(updatedAt)s)
            ON DUPLICATE KEY UPDATE value=%(value)s, comment=%(comment)s, updatedAt=%(updatedAt)s
            """,
            {
                "id": feedback_id,
                "stepId": feedback.forId,
                "name": "user_feedback",
                "value": float(feedback.value),
                "comment": feedback.comment,
                "createdAt": now,
                "updatedAt": now,
            },
        )
        return feedback_id

    @queue_until_user_message()
    async def create_element(self, element):
        now = _now()
        await self.execute(
            """
            INSERT INTO Element (id, threadId, forId, name, type, url, path, content, mime, metadata, createdAt, updatedAt)
            VALUES (%(id)s, %(threadId)s, %(forId)s, %(name)s, %(type)s, %(url)s, %(path)s, %(content)s, %(mime)s, %(metadata)s, %(createdAt)s, %(updatedAt)s)
            ON DUPLICATE KEY UPDATE updatedAt=%(updatedAt)s
            """,
            {
                "id": element.id,
                "threadId": element.thread_id,
                "forId": element.for_id,
                "name": element.name,
                "type": element.type,
                "url": element.url,
                "path": element.path,
                "content": element.content,
                "mime": element.mime,
                "metadata": _json_dumps(getattr(element, 'metadata', {})),
                "createdAt": now,
                "updatedAt": now,
            },
        )

    async def get_element(self, thread_id: str, element_id: str):
        rows = await self.execute(
            "SELECT * FROM Element WHERE id=%(id)s AND threadId=%(threadId)s",
            {"id": element_id, "threadId": thread_id},
        )
        if not rows:
            return None
        row = rows[0]
        return {
            "id": row["id"],
            "threadId": row["threadId"],
            "forId": row["forId"],
            "name": row["name"],
            "type": row["type"],
            "url": row["url"],
            "path": row["path"],
            "content": row["content"],
            "mime": row["mime"],
            "metadata": _json_loads(row.get("metadata")),
        }

    @queue_until_user_message()
    async def delete_element(self, element_id: str, thread_id: Optional[str] = None):
        if thread_id:
            await self.execute(
                "DELETE FROM Element WHERE id=%(id)s AND threadId=%(threadId)s",
                {"id": element_id, "threadId": thread_id},
            )
        else:
            await self.execute("DELETE FROM Element WHERE id=%(id)s", {"id": element_id})

    @queue_until_user_message()
    async def create_step(self, step_dict):
        now = _now()
        await self.execute(
            """
            INSERT INTO Step (
                id, threadId, parentId, name, type, input, output, metadata, tags,
                createdAt, startTime, endTime, isError, generation, feedback
            ) VALUES (
                %(id)s, %(threadId)s, %(parentId)s, %(name)s, %(type)s, %(input)s, %(output)s, %(metadata)s, %(tags)s,
                %(createdAt)s, %(startTime)s, %(endTime)s, %(isError)s, %(generation)s, %(feedback)s
            ) ON DUPLICATE KEY UPDATE output=%(output)s, metadata=%(metadata)s, tags=%(tags)s, endTime=%(endTime)s
            """,
            {
                "id": step_dict.get("id"),
                "threadId": step_dict.get("threadId"),
                "parentId": step_dict.get("parentId"),
                "name": step_dict.get("name"),
                "type": step_dict.get("type"),
                "input": step_dict.get("input"),
                "output": step_dict.get("output"),
                "metadata": _json_dumps(step_dict.get("metadata")),
                "tags": _json_dumps(step_dict.get("tags")),
                "createdAt": _parse_dt(step_dict.get("createdAt")) or now,
                "startTime": _parse_dt(step_dict.get("start")) or now,
                "endTime": _parse_dt(step_dict.get("end")),
                "isError": bool(step_dict.get("isError")) if step_dict.get("isError") is not None else False,
                "generation": _json_dumps(step_dict.get("generation")),
                "feedback": _json_dumps(step_dict.get("feedback")),
            },
        )

    @queue_until_user_message()
    async def update_step(self, step_dict):
        await self.create_step(step_dict)

    @queue_until_user_message()
    async def delete_step(self, step_id: str):
        await self.execute("DELETE FROM Step WHERE id=%(id)s", {"id": step_id})

    async def get_thread_author(self, thread_id: str) -> str:
        rows = await self.execute(
            "SELECT userIdentifier FROM Thread WHERE id=%(id)s",
            {"id": thread_id},
        )
        if not rows:
            return ""
        return rows[0].get("userIdentifier") or ""

    async def delete_thread(self, thread_id: str):
        await self.execute("DELETE FROM Step WHERE threadId=%(id)s", {"id": thread_id})
        await self.execute("DELETE FROM Element WHERE threadId=%(id)s", {"id": thread_id})
        await self.execute("DELETE FROM Thread WHERE id=%(id)s", {"id": thread_id})

    async def list_threads(self, pagination: Pagination, filters: ThreadFilter) -> PaginatedResponse[ThreadDict]:
        where = []
        params: Dict[str, Any] = {}

        if filters.userId:
            where.append("userId=%(userId)s")
            params["userId"] = filters.userId
        if filters.search:
            where.append("name LIKE %(search)s")
            params["search"] = f"%{filters.search}%"

        where_clause = f"WHERE {' AND '.join(where)}" if where else ""

        query = f"SELECT * FROM Thread {where_clause} ORDER BY createdAt DESC LIMIT %(limit)s"
        params["limit"] = pagination.first

        rows = await self.execute(query, params)
        threads: List[ThreadDict] = []
        for row in rows:
            threads.append(
                {
                    "id": row["id"],
                    "createdAt": _dt_to_iso(row["createdAt"]),
                    "name": row.get("name"),
                    "userId": row.get("userId"),
                    "userIdentifier": row.get("userIdentifier"),
                    "tags": _json_loads(row.get("tags")) if row.get("tags") else None,
                    "metadata": _json_loads(row.get("metadata")) if row.get("metadata") else None,
                    "steps": [],
                    "elements": [],
                }
            )

        return {"data": threads, "pageInfo": {"hasNextPage": False, "endCursor": None}}

    async def get_thread(self, thread_id: str) -> Optional[ThreadDict]:
        rows = await self.execute("SELECT * FROM Thread WHERE id=%(id)s", {"id": thread_id})
        if not rows:
            return None
        row = rows[0]

        steps_rows = await self.execute("SELECT * FROM Step WHERE threadId=%(id)s ORDER BY createdAt ASC", {"id": thread_id})
        steps = []
        for s in steps_rows:
            steps.append(
                {
                    "id": s["id"],
                    "threadId": s["threadId"],
                    "parentId": s.get("parentId"),
                    "name": s.get("name") or "",
                    "type": s.get("type") or "assistant_message",
                    "input": s.get("input") or "",
                    "output": s.get("output") or "",
                    "metadata": _json_loads(s.get("metadata")),
                    "tags": _json_loads(s.get("tags")) if s.get("tags") else None,
                    "createdAt": _dt_to_iso(s.get("createdAt")),
                    "start": _dt_to_iso(s.get("startTime")),
                    "end": _dt_to_iso(s.get("endTime")),
                    "generation": _json_loads(s.get("generation")) if s.get("generation") else None,
                    "feedback": _json_loads(s.get("feedback")) if s.get("feedback") else None,
                    "streaming": False,
                    "waitForAnswer": None,
                    "isError": s.get("isError"),
                    "modes": None,
                    "command": None,
                    "showInput": False,
                    "defaultOpen": None,
                    "language": None,
                }
            )

        return {
            "id": row["id"],
            "createdAt": _dt_to_iso(row["createdAt"]),
            "name": row.get("name"),
            "userId": row.get("userId"),
            "userIdentifier": row.get("userIdentifier"),
            "tags": _json_loads(row.get("tags")) if row.get("tags") else None,
            "metadata": _json_loads(row.get("metadata")) if row.get("metadata") else None,
            "steps": steps,
            "elements": [],
        }

    async def update_thread(self, thread_id: str, name: Optional[str] = None, user_id: Optional[str] = None, metadata: Optional[Dict] = None, tags: Optional[List[str]] = None):
        now = _now()
        await self.execute(
            """
            INSERT INTO Thread (id, name, userId, userIdentifier, metadata, tags, createdAt, updatedAt)
            VALUES (%(id)s, %(name)s, %(userId)s, %(userIdentifier)s, %(metadata)s, %(tags)s, %(createdAt)s, %(updatedAt)s)
            ON DUPLICATE KEY UPDATE name=%(name)s, userId=%(userId)s, metadata=%(metadata)s, tags=%(tags)s, updatedAt=%(updatedAt)s
            """,
            {
                "id": thread_id,
                "name": name,
                "userId": user_id,
                "userIdentifier": None,
                "metadata": _json_dumps(metadata),
                "tags": _json_dumps(tags),
                "createdAt": now,
                "updatedAt": now,
            },
        )

    async def build_debug_url(self) -> str:
        return ""

    async def close(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def get_favorite_steps(self, user_id: str):
        return []

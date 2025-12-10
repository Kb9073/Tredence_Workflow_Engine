import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket

_CONNECTIONS: Dict[str, Set[WebSocket]] = {}
_LOCK = asyncio.Lock()

async def register(ws: WebSocket, run_id: str):
    await ws.accept()
    async with _LOCK:
        if run_id not in _CONNECTIONS:
            _CONNECTIONS[run_id] = set()
        _CONNECTIONS[run_id].add(ws)

async def unregister(ws: WebSocket, run_id: str):
    async with _LOCK:
        conns = _CONNECTIONS.get(run_id)
        if not conns:
            return
        conns.discard(ws)
        if not conns:
            _CONNECTIONS.pop(run_id, None)

async def broadcast(run_id: str, message: str):
    async with _LOCK:
        conns = list(_CONNECTIONS.get(run_id, set()))
    if not conns:
        return
    payload = json.dumps({"run_id": run_id, "log": message})
    to_remove = []
    for ws in conns:
        try:
            await ws.send_text(payload)
        except Exception:
            to_remove.append(ws)
    if to_remove:
        async with _LOCK:
            for ws in to_remove:
                _CONNECTIONS.get(run_id, set()).discard(ws)

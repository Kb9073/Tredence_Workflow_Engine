from fastapi import FastAPI, HTTPException, WebSocket
from .models import GraphCreateRequest, RunRequest
from .engine import create_graph, run_graph_async, run_graph_background, get_run, get_graph, NODE_REGISTRY
from .notifier import register, unregister
from .tools import TOOLS
from . import workflows
import uuid
import json

app = FastAPI()


@app.post("/graph/create")
async def graph_create(req: GraphCreateRequest):
    g_id = str(uuid.uuid4())
    nodes = {n.name: n for n in req.nodes}
    for n in nodes.values():
        if n.func not in NODE_REGISTRY:
            raise HTTPException(status_code=400, detail="node function not registered")
    create_graph(g_id, nodes, req.edges, req.start_node)
    return {"graph_id": g_id}

@app.post("/graph/run")
async def graph_run(req: RunRequest):
    if not get_graph(req.graph_id):
        raise HTTPException(status_code=404, detail="graph not found")
    if req.wait:
        r = await run_graph_async(req.graph_id, req.initial_state)
        return {"run_id": r.run_id, "state": r.state, "log": r.log, "done": r.done, "error": r.error}
    r_id = run_graph_background(req.graph_id, req.initial_state)
    return {"run_id": r_id, "status": "started"}

@app.get("/graph/state/{run_id}")
async def graph_state(run_id: str):
    r = get_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="run not found")
    return {"run_id": r.run_id, "state": r.state, "log": r.log, "done": r.done, "error": r.error}

@app.get("/meta")
def meta():
    return {"nodes": list(NODE_REGISTRY.keys()), "tools": list(TOOLS.keys())}

@app.websocket("/ws/{run_id}")
async def websocket_endpoint(ws: WebSocket, run_id: str):
    await register(ws, run_id)
    try:
        run = get_run(run_id)
        if run:
            for entry in run.log:
                await ws.send_text(json.dumps({"run_id": run_id, "log": entry}))
        while True:
            await ws.receive_text()
    except Exception:
        pass
    finally:
        await unregister(ws, run_id)

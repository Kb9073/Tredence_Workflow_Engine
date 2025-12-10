from typing import Dict, Any, Optional, Callable
import asyncio
import uuid
from .models import RunState, NodeDef
from .notifier import broadcast

NODE_REGISTRY: Dict[str, Callable[..., Any]] = {}
GRAPHS: Dict[str, Dict[str, Any]] = {}
RUNS: Dict[str, RunState] = {}

def register_node(name: str):
    def wrapper(fn):
        NODE_REGISTRY[name] = fn
        return fn
    return wrapper

def create_graph(graph_id: str, nodes: Dict[str, NodeDef], edges: Dict[str, Optional[str]], start_node: str):
    GRAPHS[graph_id] = {"nodes": nodes, "edges": edges, "start_node": start_node}
    return graph_id

def get_graph(graph_id: str):
    return GRAPHS.get(graph_id)

def get_run(run_id: str):
    return RUNS.get(run_id)

async def _append_and_broadcast(run: RunState, message: str):
    run.log.append(message)
    try:
        await broadcast(run.run_id, message)
    except Exception:
        pass

async def run_graph_async(graph_id: str, initial_state: Dict[str, Any], run_id: Optional[str] = None):
    run_id = run_id or str(uuid.uuid4())
    g = get_graph(graph_id)
    if g is None:
        raise ValueError("graph not found")
    run = RunState(run_id=run_id, graph_id=graph_id, state=initial_state.copy())
    RUNS[run_id] = run
    nodes = g["nodes"]
    edges = g["edges"]
    current = g["start_node"]
    counter = 0
    await _append_and_broadcast(run, f"start:{current}")
    try:
        while current:
            counter += 1
            if counter > 1500:
                raise RuntimeError("loop limit")
            run.current_node = current
            await _append_and_broadcast(run, f"enter:{current}")
            n = nodes[current]
            fn = NODE_REGISTRY.get(n.func)
            if fn is None:
                raise RuntimeError("node missing")
            res = fn(run.state, n.config or {})
            if asyncio.iscoroutine(res):
                res = await res
            nxt = None
            delay = None
            if isinstance(res, dict):
                nxt = res.get("next")
                delay = res.get("wait")
                for k, v in res.items():
                    if k not in {"next", "wait"}:
                        run.state[k] = v
            if delay:
                await asyncio.sleep(delay)
            if not nxt:
                nxt = edges.get(current)
            await _append_and_broadcast(run, f"exit:{current}->{nxt}")
            current = nxt
        run.done = True
        await _append_and_broadcast(run, "end")
    except Exception as exc:
        run.error = str(exc)
        await _append_and_broadcast(run, f"error:{exc}")
    return run

def run_graph_background(graph_id: str, initial_state: Dict[str, Any]):
    run_id = str(uuid.uuid4())
    asyncio.create_task(run_graph_async(graph_id, initial_state, run_id=run_id))
    return run_id

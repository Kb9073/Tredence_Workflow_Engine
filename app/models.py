from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class NodeDef(BaseModel):
    name: str
    func: str
    config: Optional[Dict[str, Any]] = None

class GraphCreateRequest(BaseModel):
    nodes: List[NodeDef]
    edges: Dict[str, Optional[str]]
    start_node: str

class RunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]
    wait: bool = True

class RunState(BaseModel):
    run_id: str
    graph_id: str
    current_node: Optional[str] = None
    state: Dict[str, Any] = Field(default_factory=dict)
    log: List[str] = Field(default_factory=list)
    done: bool = False
    error: Optional[str] = None

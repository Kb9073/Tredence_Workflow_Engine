from typing import Dict, Callable, Any
import random

TOOLS: Dict[str, Callable[..., Any]] = {}

def register_tool(name: str):
    def wrapper(fn):
        TOOLS[name] = fn
        return fn
    return wrapper

def get_tool(name: str):
    return TOOLS[name]

@register_tool("extract_functions")
def extract_functions(code: str):
    out = []
    for line in code.splitlines():
        t = line.strip()
        if t.startswith("def "):
            name = t.split("(")[0].replace("def ", "").strip()
            out.append(name)
    return {"functions": out}

@register_tool("compute_complexity")
def compute_complexity(code: str):
    lines = [l for l in code.splitlines() if l.strip()]
    return {"complexity": 1 + len(lines) // 6}

@register_tool("detect_issues")
def detect_issues(code: str):
    base = code.count("print(") + code.count("TODO")
    extra = 1 if random.random() < 0.08 else 0
    return {"issues": base + extra}

@register_tool("suggest_improvements")
def suggest_improvements(state: Dict[str, Any]):
    analysis = state.get("analysis", {})
    c = analysis.get("complexity", 0)
    i = analysis.get("issues", 0)
    notes = []
    if i:
        notes.append("Remove debug prints and TODOs")
    if c >= 6:
        notes.append("Split large functions into smaller helpers")
    if not notes:
        notes.append("No critical suggestions")
    score = max(0, 100 - (i * 12 + c * 6))
    return {"suggestions": notes, "quality_score": score}

from .engine import register_node
from .tools import get_tool

@register_node("extract")
def extract_node(state: dict, cfg: dict):
    code = state.get("code", "")
    out = get_tool("extract_functions")(code)
    state["extracted"] = out
    return {"next": "analyze", "extracted": out}

@register_node("analyze")
def analyze_node(state: dict, cfg: dict):
    code = state.get("code", "")
    comp = get_tool("compute_complexity")(code)
    iss = get_tool("detect_issues")(code)
    data = {"complexity": comp["complexity"], "issues": iss["issues"]}
    state["analysis"] = data
    return {"next": "suggest", "analysis": data}

@register_node("suggest")
def suggest_node(state: dict, cfg: dict):
    out = get_tool("suggest_improvements")(state)
    state.setdefault("history", []).append(out)
    state["quality_score"] = out["quality_score"]
    th = cfg.get("threshold", 90)
    if state["quality_score"] >= th:
        return {"suggestions": out["suggestions"], "next": None}
    updated = state.get("code", "").replace("print(", "# print(").replace("TODO", "")
    state["code"] = updated
    return {"suggestions": out["suggestions"], "next": "analyze", "wait": 0.04}

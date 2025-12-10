Mini Workflow Engine (Tredence Backend Assignment)

This project implements a small but flexible workflow/graph engine using Python and FastAPI.
The main idea is simple: a workflow is made up of “nodes” and each node is just a Python function that takes a shared state dictionary, updates it, and decides which node should run next.
The engine executes these nodes in order, supports loops, branching, async execution, and can stream live logs through WebSockets.

Design Overview :
I kept the architecture intentionally clean so the core idea remains easy to understand:

The engine manages execution flow
Nodes contain the actual logic
State moves through each node
Transitions decide which node runs next
Workflows are created through a simple API
Logs can be streamed in real time over WebSockets
This keeps the code easy to maintain, extend, and reason about.

Key Features:
1) Workflow Execution Engine 
    Dynamic node registry /
    Shared State passed through nodes
    Natural Looping through next pointers 
    Synchronous / Background execution modes

2) Tool Registry 
    Extract Functions from code
    compute simple complexity 
    lightweight issue detection
    generating improvement suggestions
                                        
3) Real Time Logging (Web sockets)          
    Clients can subscribe to /ws/{run_id} to see:
        Node Entry
        node exit
        transitions
        final completion
        errors


Included Example Workflow: Code Review Pipeline

The included example simulates a simple code-review agent:  
extract → analyze → suggest → (repeat until quality_score ≥ threshold) → finish

extract: finds function names
analyze: assigns complexity + issue count
suggest: provides improvements and decides whether to loop.
This demonstrates branching, state updates, and looping inside the engine.

API Endpoints

1) Create a Workflow 

POST /graph/create
    {
    "nodes": [
        {"name": "extract", "func": "extract"},
        {"name": "analyze", "func": "analyze"},
        {"name": "suggest", "func": "suggest", "config": {"threshold": 90}}
    ],
    "edges": {
        "extract": "analyze",
        "analyze": "suggest",
        "suggest": null
    },
    "start_node": "extract"
    }

2) Run a Workflow

POST /graph/run
Input example:
    {
    "graph_id": "...",
    "initial_state": {"code": "def foo(): print('hi')"},
    "wait": true
    }

wait = true runs the workflow synchronously
wait = false starts it in the background

3) Check Status of a Run

GET /graph/state/{run_id}
Returns:

current state
log history
done flag
errors (if any)

4) Stream Logs Live

WS /ws/{run_id}
Connect using a WebSocket client and receive log events in real time.


Project Structure 
    app/
        main.py          # API + WebSocket entrypoint
        engine.py        # Workflow engine logic
        models.py        # Pydantic models
        notifier.py      # WebSocket broadcaster
        tools.py         # Tool registry
        workflows.py     # Example workflow nodes
    requirements.txt
    README.md

Running the Project:

1) Install Dependencies : pip install fastapi uvicorn pydantic

2) Start the Server : uvicorn app.main:app --reload


Closing Notes :

I aimed to design a clean, readable, and modular workflow system that demonstrates:
stateful execution

node-based transitions
async handling
and real-time visibility

The final result is a flexible mini-engine that can be extended with different workflows while keeping the core logic straightforward.


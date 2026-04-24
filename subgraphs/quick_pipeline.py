from langgraph.graph import StateGraph

def extract(state):
    for job in state.get("jobs", []):
        job["requirements"] = "Key requirements"
    return state

def match(state):
    for job in state.get("jobs", []):
        job["matches"] = "Matching skills"
    return state

def summary(state):
    for job in state.get("jobs", []):
        job["summary"] = f"Good fit for {job['title']}"
    return state

def build_quick_pipeline():
    builder = StateGraph(dict)

    builder.add_node("extract", extract)
    builder.add_node("match", match)
    builder.add_node("summary", summary)

    builder.set_entry_point("extract")

    builder.add_edge("extract", "match")
    builder.add_edge("match", "summary")

    return builder.compile()
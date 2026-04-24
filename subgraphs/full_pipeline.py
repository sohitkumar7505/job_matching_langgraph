from langgraph.graph import StateGraph

def analyze_jd(state):
    for job in state.get("jobs", []):
        job["analysis"] = "Deep JD analysis"
    return state

def tailor_resume(state):
    for job in state.get("jobs", []):
        job["tailored_resume"] = f"Resume for {job['title']}"
    return state

def cover_letter(state):
    for job in state.get("jobs", []):
        job["cover_letter"] = "Generated cover letter"
    return state

def quality_check(state):
    for job in state.get("jobs", []):
        # simulate poor quality first time
        if job["retries"] == 0:
            score = 6
        else:
            score = 8

        job["quality_score"] = score
    return state


def quality_router(state):
    for job in state.get("jobs", []):
        if job["quality_score"] < 7 and job["retries"] < 2:
            job["retries"] += 1
            return "retry"
    return "done"


def build_full_pipeline():
    builder = StateGraph(dict)

    builder.add_node("analyze", analyze_jd)
    builder.add_node("tailor", tailor_resume)
    builder.add_node("cover", cover_letter)
    builder.add_node("quality", quality_check)

    builder.set_entry_point("analyze")

    builder.add_edge("analyze", "tailor")
    builder.add_edge("tailor", "cover")
    builder.add_edge("cover", "quality")

    builder.add_conditional_edges(
        "quality",
        quality_router,
        {
            "retry": "tailor",
            "done": "__end__"
        }
    )

    return builder.compile()
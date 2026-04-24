from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from state import GraphState

from nodes.intake import intake_node
from nodes.scorer import scorer_node
from nodes.router import router_node
from nodes.aggregate import aggregate_node
from nodes.human_review import human_review_node
from nodes.strategy import strategy_node
from nodes.skip_logs import skip_node

from subgraphs.full_pipeline import build_full_pipeline
from subgraphs.quick_pipeline import build_quick_pipeline

# subgraphs
full_pipeline = build_full_pipeline()
quick_pipeline = build_quick_pipeline()

builder = StateGraph(GraphState)

builder.add_node("intake", intake_node)
builder.add_node("scorer", scorer_node)
builder.add_node("router", router_node)

builder.add_node("full_pipeline", full_pipeline)
builder.add_node("quick_pipeline", quick_pipeline)
builder.add_node("skip", skip_node)

builder.add_node("aggregate", aggregate_node)
builder.add_node("human_review", human_review_node)
builder.add_node("strategy", strategy_node)

builder.set_entry_point("intake")

builder.add_edge("intake", "scorer")
builder.add_edge("scorer", "router")

# conditional routing
builder.add_conditional_edges(
    "router",
    lambda state: state["next_pipeline"],
    {
        "full_pipeline": "full_pipeline",
        "quick_pipeline": "quick_pipeline",
        "skip": "skip"
    }
)

builder.add_edge("full_pipeline", "aggregate")
builder.add_edge("quick_pipeline", "aggregate")
builder.add_edge("skip", "aggregate")

builder.add_edge("aggregate", "human_review")
builder.add_edge("human_review", "strategy")

# persistence
memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}

    # first run → pauses
    state = graph.invoke({}, config=config)

    print("\n⏸ Paused for human input...")

    # resume after human input
    state = graph.invoke(None, config=config)


    print("\nFINAL OUTPUT:\n", state["final_output"])
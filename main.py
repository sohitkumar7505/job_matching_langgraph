from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from state import GraphState

from nodes.intake import intake_node
from nodes.scorer import scorer_node
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

builder.add_node("full_pipeline", full_pipeline)
builder.add_node("quick_pipeline", quick_pipeline)
builder.add_node("skip", skip_node)

builder.add_node("aggregate", aggregate_node)
builder.add_node("human_review", human_review_node)
builder.add_node("strategy", strategy_node)

builder.set_entry_point("intake")

builder.add_edge("intake", "scorer")

# conditional routing from scorer to pipelines
def route_by_category(state):
    jobs = state["jobs"]
    high = [j for j in jobs if j["category"] == "HIGH"]
    medium = [j for j in jobs if j["category"] == "MEDIUM"]
    low = [j for j in jobs if j["category"] == "LOW"]
    
    if high:
        return "full_pipeline"
    elif medium:
        return "quick_pipeline"
    else:
        return "skip"

builder.add_conditional_edges(
    "scorer",
    route_by_category,
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


    print("JOB MATCHING & APPLICATION STRATEGY ENGINE")


    # First run - scoring and processing
    print("📊 Starting job analysis and matching...\n")
    try:
        for event in graph.stream({}, config=config, stream_mode="updates"):
            # Show only important updates
            for node, data in event.items():
                if node == "__interrupt__":
                    print("\n⏸️  WAITING FOR HUMAN REVIEW...\n")
    except Exception as e:
        print(f"Error during processing: {e}")
        exit(1)

    print("\n" + "="*80)
    print("CONTINUING WITH HUMAN DECISION...")
    print("="*80)

    # Resume after human review decision
    try:
        for event in graph.stream(None, config=config, stream_mode="updates"):
            for node, data in event.items():
                if node != "__interrupt__":
                    pass  # Suppress verbose output
    except Exception as e:
        print(f"Error during completion: {e}")
        exit(1)

    # Get and display final output
    final_state = graph.get_state(config)
    
    if "final_output" in final_state.values and final_state.values["final_output"]:
        output = final_state.values["final_output"]
        
        print("\n" + "="*80)
        print("✅ FINAL APPLICATION STRATEGY")
        print("="*80)
        
        print(f"\n👤 Candidate: {output.get('candidate_name', 'N/A')}")
        print(f"📊 Total Jobs Analyzed: {output.get('total_jobs_analyzed', 0)}")
        
        stats = output.get('stats', {})
        print(f"\n📈 STATISTICS:")
        print(f"   ✅ Approved: {stats.get('approved_count', 0)}")
        print(f"   ❌ Skipped: {stats.get('skipped_count', 0)}")
        print(f"   ⭐ Average Score (Approved): {stats.get('average_approved_score', 0):.1f}/10")
        if stats.get('top_match'):
            print(f"   🏆 Top Match: {stats['top_match']} ({stats.get('top_match_score', 0)}/10)")
        
        approved = output.get('approved_jobs', [])
        print(f"\n✅ APPROVED JOBS ({len(approved)}):")
        for i, job in enumerate(approved, 1):
            title = job.get('title', 'N/A') if isinstance(job, dict) else str(job)
            score = job.get('score', 'N/A') if isinstance(job, dict) else 'N/A'
            print(f"   {i}. {title} (Score: {score}/10)")
        
        print(f"\n📝 RECOMMENDED APPLICATION ORDER:")
        for i, job_title in enumerate(output.get('recommended_apply_order', []), 1):
            print(f"   {i}. {job_title}")
        
        skipped = output.get('skipped_jobs', [])
        if skipped:
            print(f"\n❌ SKIPPED JOBS ({len(skipped)}):")
            for i, job in enumerate(skipped, 1):
                title = job.get('title', 'N/A') if isinstance(job, dict) else str(job)
                score = job.get('score', 'N/A') if isinstance(job, dict) else 'N/A'
                print(f"   {i}. {title} (Score: {score}/10)")
        
        print("\n" + "="*80)
        print("🎉 Application strategy completed successfully!")
        print("="*80 + "\n")
    else:
        print("\n⚠️  Graph completed but final output not available.")
        print("Final state:", final_state.values.keys())
def strategy_node(state):
    return {
        "final_output": {
            "candidate_name": state["candidate"]["name"],
            "total_jobs_analyzed": len(state["jobs"]),
            "approved_jobs": state["approved_jobs"],
            "skipped_jobs": state["skipped_jobs"],
            "recommended_apply_order": [
                job["title"] for job in state["approved_jobs"]
            ]
        }
    }
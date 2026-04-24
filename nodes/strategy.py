def strategy_node(state):
    """Generate final application strategy based on approved jobs."""
    
    approved_jobs = state.get("approved_jobs", [])
    skipped_jobs = state.get("skipped_jobs", [])
    
    # Sort approved jobs by score (highest first)
    sorted_approved = sorted(approved_jobs, key=lambda x: x.get("score", 0), reverse=True)
    
    # Generate recommendations
    recommended_order = [job["title"] for job in sorted_approved]
    
    return {
        "final_output": {
            "candidate_name": state["candidate"]["name"],
            "total_jobs_analyzed": len(state["jobs"]),
            "approved_jobs": approved_jobs,
            "skipped_jobs": skipped_jobs,
            "recommended_apply_order": recommended_order,
            "stats": {
                "approved_count": len(approved_jobs),
                "skipped_count": len(skipped_jobs),
                "average_approved_score": sum(j.get("score", 0) for j in approved_jobs) / len(approved_jobs) if approved_jobs else 0,
                "top_match": sorted_approved[0]["title"] if sorted_approved else None,
                "top_match_score": sorted_approved[0].get("score", 0) if sorted_approved else 0
            }
        }
    }
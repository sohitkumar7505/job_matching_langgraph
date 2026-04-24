def human_review_node(state):
    print("\n--- HUMAN REVIEW ---")

    for i, job in enumerate(state["processed_jobs"]):
        print(f"{i}: {job['title']} (Score: {job['score']})")

    decision = input("approve / reject: ")

    if decision == "approve":
        return {"approved_jobs": state["processed_jobs"]}
    else:
        return {"approved_jobs": []}
import json

def intake_node(state):
    with open("data/candidate.json") as f:
        candidate = json.load(f)

    with open("data/jobs.json") as f:
        jobs = json.load(f)

    for job in jobs:
        job["retries"] = 0

    return {"candidate": candidate, "jobs": jobs}
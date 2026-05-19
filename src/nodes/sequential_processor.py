from utility import stream_llm_response
from subgraphs.full_pipeline import analyze_jd, tailor_resume, cover_letter, quality_check
from subgraphs.quick_pipeline import extract_reqs, match_skills, quick_summary

def process_single_job_node(state):
    """Process one job at a time through its appropriate pipeline"""

    # Get the next job to process
    jobs = state.get("jobs", [])
    processed_jobs = state.get("processed_jobs", [])
    skipped_jobs = state.get("skipped_jobs", [])

    # Find unprocessed jobs
    unprocessed = [job for job in jobs if job not in processed_jobs and job not in skipped_jobs]

    if not unprocessed:
        print("\n✅ All jobs have been processed!")
        return state

    # Process the first unprocessed job
    job = unprocessed[0]
    candidate = state["candidate"]

    print(f"\n🚀 PROCESSING JOB: {job['title']}")
    print(f"   Category: {job.get('category', 'Unknown')}")
    print("="*80)

    # Route based on category
    if job.get("category") == "HIGH":
        print("   📋 Running FULL PIPELINE (detailed analysis + resume + cover letter)")
        print("   🔍 Step 1: Analyzing job description...")

        # Run full pipeline steps for this single job
        job_state = {"jobs": [job], "candidate": candidate}

        # Analyze JD
        analyze_jd(job_state)

        # Tailor resume
        print("   📝 Step 2: Tailoring resume...")
        tailor_resume(job_state)

        # Generate cover letter
        print("   ✉️  Step 3: Generating cover letter...")
        cover_letter(job_state)

        # Quality check
        print("   ✅ Step 4: Quality check...")
        quality_check(job_state)

        processed_jobs.append(job)
        print(f"   🎉 Job '{job['title']}' fully processed!")

    elif job.get("category") == "MEDIUM":
        print("   📋 Running QUICK PIPELINE (requirements + skill matching + summary)")
        print("   🔍 Step 1: Extracting requirements...")

        # Run quick pipeline steps for this single job
        job_state = {"jobs": [job], "candidate": candidate}

        # Extract requirements
        extract_reqs(job_state)

        # Match skills
        print("   🎯 Step 2: Matching skills...")
        match_skills(job_state)

        # Generate summary
        print("   📄 Step 3: Generating summary...")
        quick_summary(job_state)

        processed_jobs.append(job)
        print(f"   🎉 Job '{job['title']}' processed with quick analysis!")

    else:
        print("   ⏭️  Skipping low-match job...")
        skipped_jobs.append(job)
        print(f"   📝 Job '{job['title']}' marked as low priority")

    return {
        "processed_jobs": processed_jobs,
        "skipped_jobs": skipped_jobs,
        "jobs": jobs  # Keep original jobs list
    }
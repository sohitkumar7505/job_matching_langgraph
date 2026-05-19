def human_review_node(state):
    """Interactive human review node for job approvals."""
    
    print("\n" + "="*80)
    print("🔍 HUMAN IN THE LOOP - JOB REVIEW & APPROVAL")
    print("="*80)
    
    processed_jobs = state["processed_jobs"]
    skipped_jobs = state["skipped_jobs"]
    
    # Display jobs for review
    print("\n📋 PROCESSED JOBS (Ready for Application):\n")
    for idx, job in enumerate(processed_jobs, 1):
        print(f"\n{idx}. {job['title']}")
        print(f"   Location: {job['location']}")
        print(f"   Score: {job.get('score', 'N/A')}/10 | Category: {job.get('category', 'N/A')}")
        if job.get('tailored_resume'):
            print(f"   ✓ Resume tailored")
        if job.get('cover_letter'):
            print(f"   ✓ Cover letter generated")
        if job.get('summary'):
            print(f"   ✓ Quick summary prepared")
        print(f"   Quality Score: {job.get('quality_score', 'N/A')}/10")
    
    print(f"\n📊 SKIPPED JOBS (Low match):\n")
    for idx, job in enumerate(skipped_jobs, 1):
        print(f"{idx}. {job['title']} - Score: {job.get('score', 'N/A')}/10")
    
    # Get user decision
    print("\n" + "="*80)
    print("📝 DECISION OPTIONS:")
    print("   1. 'approve' - Approve all processed jobs")
    print("   2. 'approve 1,2' - Approve specific jobs by number")
    print("   3. 'reject' - Reject all")
    print("   4. 'review' - Review details of specific job")
    print("   5. 'revise 1,2' - Revise specific jobs")
    print("="*80)
    
    approved = []
    
    while True:
        decision_input = input("\n👤 Your decision: ").strip().lower()
        
        if decision_input == "approve":
            approved = processed_jobs
            print("✅ All jobs approved for application!")
            break
        
        elif decision_input.startswith("approve "):
            try:
                indices = [int(x.strip()) - 1 for x in decision_input.replace("approve ", "").split(",")]
                approved = [processed_jobs[i] for i in indices if 0 <= i < len(processed_jobs)]
                print(f"✅ Approved {len(approved)} job(s)")
                break
            except (ValueError, IndexError):
                print("❌ Invalid format. Use: approve 1,2,3")
                continue
        
        elif decision_input == "reject":
            print("❌ All jobs rejected")
            break
        
        elif decision_input.startswith("review "):
            try:
                idx = int(decision_input.replace("review ", "")) - 1
                job = processed_jobs[idx]
                print(f"\n📄 DETAILED REVIEW - {job['title']}")
                print(f"Description: {job['description'][:200]}...")
                if job.get('tailored_resume'):
                    print(f"Resume: {job['tailored_resume'][:300]}...")
                if job.get('cover_letter'):
                    print(f"Cover Letter: {job['cover_letter'][:300]}...")
                if job.get('summary'):
                    print(f"Summary: {job['summary'][:300]}...")
            except (ValueError, IndexError):
                print("❌ Invalid job number")
            continue
        
        elif decision_input.startswith("revise "):
            try:
                indices = [int(x.strip()) - 1 for x in decision_input.replace("revise ", "").split(",")]
                approved = [processed_jobs[i] for i in indices if 0 <= i < len(processed_jobs)]
                print(f"🔄 {len(approved)} job(s) marked for revision")
                break
            except (ValueError, IndexError):
                print("❌ Invalid format. Use: revise 1,2,3")
                continue
        
        else:
            print("❌ Invalid decision. Please try again.")
            continue
    
    return {"approved_jobs": approved}
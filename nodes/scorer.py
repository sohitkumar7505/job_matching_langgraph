import json
from utility import get_llm_response, get_system_prompt
from guardrails.input_guardrails import validate_input, InputValidationError
from guardrails.output_guardrails import validate_output, OutputValidationError


def build_scoring_prompt(job, candidate, version="1.1"):
    prompt_system = get_system_prompt(version)
    prompt_user = f"""
Candidate Profile:
- Name: {candidate['name']}
- Title: {candidate['title']}
- Experience: {candidate['experience_years']} years
- Skills: {', '.join(candidate['skills'])}
- Preferences: Role: {candidate.get('preferences', {}).get('role_type', 'N/A')}, Location: {candidate.get('preferences', {}).get('location', 'N/A')}

Job Details:
- Job ID: {job.get('job_id', 'unknown')}
- Title: {job['title']}
- Location: {job.get('location', 'N/A')}
- Description: {job.get('description', '')}
- Required Skills: {', '.join(job.get('required_skills', []))}
- Preferred Skills: {', '.join(job.get('preferred_skills', []))}
- Experience Required: {job.get('experience_required', 'N/A')} years

Please evaluate the candidate-job fit and return the required JSON object only.
"""
    return prompt_system + "\n\n" + prompt_user


def score_single_job(job, candidate):
    print(f"\n🎯 SCORING JOB: {job['title']}")
    print(f"   Location: {job.get('location', 'N/A')}")
    print("   Validating input and checking for prompt injection...")

    try:
        validate_input(candidate, job)
    except InputValidationError as e:
        print(f"   ⚠️  Input guardrail blocked scoring: {e}")
        job['score'] = 1
        job['category'] = 'LOW'
        job['score_reason'] = 'Input validation failed or prompt injection detected.'
        return job

    prompt = build_scoring_prompt(job, candidate, version="1.1")
    print("   Sending scoring prompt to LLM...")

    try:
        raw_response = get_llm_response(prompt)
        validated = validate_output(raw_response)
        job['score'] = validated.score
        job['category'] = validated.category
        job['score_reason'] = validated.reason
        print(f"   ✅ Score: {validated.score}/10 | Category: {validated.category}")
        print(f"   💡 Reason: {validated.reason}")
    except OutputValidationError as e:
        print(f"   ⚠️  Output guardrail failed: {e}")
        job['score'] = 1
        job['category'] = 'LOW'
        job['score_reason'] = 'LLM output failed validation.'
    except Exception as e:
        print(f"   ⚠️  Scoring failed: {e}")
        job['score'] = 1
        job['category'] = 'LOW'
        job['score_reason'] = 'LLM scoring failed due to an unexpected error.'

    return job


def scorer_node(state):
    jobs = state['jobs']
    candidate = state['candidate']

    print(f"\n📊 SCORING {len(jobs)} JOBS FOR CANDIDATE: {candidate['name']}")
    print("="*80)

    updated_jobs = []
    for i, job in enumerate(jobs, 1):
        print(f"\n[Job {i}/{len(jobs)}]")
        scored_job = score_single_job(job, candidate)
        updated_jobs.append(scored_job)

    return {'jobs': updated_jobs}

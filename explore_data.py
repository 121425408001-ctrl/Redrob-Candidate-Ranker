"""
explore_data.py - look at real candidates before we write scoring logic.

Run this to see:
1. What one normal candidate record actually looks like
2. Real examples of the "honeypot" trap patterns the hackathon hid in the data
"""

import json

print("=" * 70)
print("PART 1: A real candidate record")
print("=" * 70)

with open("data/sample_candidates.json") as f:
    sample = json.load(f)

c = sample[0]
p = c["profile"]
print(f"\nID: {c['candidate_id']}")
print(f"Title: {p['current_title']} at {p['current_company']}")
print(f"Location: {p['location']}, {p['country']}")
print(f"Years of experience: {p['years_of_experience']}")
print(f"Headline: {p['headline']}")

print(f"\nSkills listed: {len(c['skills'])}")
for s in c["skills"][:5]:
    print(f"  - {s['name']} ({s['proficiency']}, used {s['duration_months']} months, {s['endorsements']} endorsements)")

job = c["career_history"][0]
print(f"\nMost recent job: {job['title']} at {job['company']} ({job['duration_months']} months)")
print(f"  \"{job['description'][:200]}...\"")

rs = c["redrob_signals"]
print(f"\nBehavioral signals:")
print(f"  Last active: {rs['last_active_date']}")
print(f"  Open to work: {rs['open_to_work_flag']}")
print(f"  Recruiter response rate: {rs['recruiter_response_rate']}")
print(f"  Notice period: {rs['notice_period_days']} days")

print("\n" + "=" * 70)
print("PART 2: Hunting for honeypots in the full 100K candidates")
print("=" * 70)

honeypot_examples = []

with open("data/candidates.jsonl") as f:
    for line in f:
        cand = json.loads(line)
        for s in cand["skills"]:
            if s["proficiency"] == "expert" and s.get("duration_months", 0) == 0:
                honeypot_examples.append((
                    cand["candidate_id"],
                    f"Lists '{s['name']}' as EXPERT but used it for 0 months"
                ))
                break
        if len(honeypot_examples) >= 5:
            break

print(f"\nFound {len(honeypot_examples)} example(s) of impossible skill claims:")
for cand_id, reason in honeypot_examples:
    print(f"  {cand_id}: {reason}")

print("\nDone. These are exactly the kind of candidates our honeypot filter needs to catch.")

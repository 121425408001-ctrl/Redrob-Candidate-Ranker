"""
test_matching.py - run the must-have / career-match checks across all
100,000 candidates and report stats + real examples.
"""

import json
import collections
from matching import must_have_summary, is_consulting_only_career, company_tier_bonus, nice_to_have_score

met_distribution = collections.Counter()
consulting_only_count = 0
big_tech_count = 0
ai_specialist_count = 0
strong_examples = []

with open("data/candidates.jsonl") as f:
    for line in f:
        c = json.loads(line)
        scores, met = must_have_summary(c)
        met_distribution[met] += 1

        if is_consulting_only_career(c):
            consulting_only_count += 1

        bonus = company_tier_bonus(c)
        if bonus == 1.0:
            big_tech_count += 1
        elif bonus == 0.7:
            ai_specialist_count += 1

        if met >= 3 and bonus > 0:
            strong_examples.append((c["candidate_id"], c["profile"]["current_title"],
                                     c["profile"]["location"], met, bonus, scores))

print("How many of the 4 must-have categories candidates meet (>=0.5 score):")
for k in sorted(met_distribution):
    print(f"  {k}/4 categories: {met_distribution[k]} candidates")

print(f"\nConsulting-only career (auto disqualifier candidate): {consulting_only_count}")
print(f"Worked at a FAANG-tier company: {big_tech_count}")
print(f"Worked at a known AI-specialist company: {ai_specialist_count}")

print(f"\nCandidates meeting 3+ must-haves AND with a strong employer signal: {len(strong_examples)}")
for cid, title, loc, met, bonus, scores in strong_examples[:5]:
    print(f"\n  {cid}: {title} | {loc} | met {met}/4 | employer_bonus {bonus}")
    for cat, sc in scores.items():
        print(f"    {cat}: {sc:.2f}")

"""
test_filters.py - run the honeypot filter against all 100,000 candidates
and report how many we catch, with real examples.
"""

import json
from filters import find_honeypot_reasons

flagged_count = 0
examples_shown = 0

with open("data/candidates.jsonl") as f:
    for line in f:
        candidate = json.loads(line)
        reasons = find_honeypot_reasons(candidate)
        if reasons:
            flagged_count += 1
            if examples_shown < 5:
                print(f"\n{candidate['candidate_id']}:")
                for r in reasons:
                    print(f"  - {r}")
                examples_shown += 1

print(f"\n\nTotal candidates flagged as honeypots: {flagged_count} out of 100,000")

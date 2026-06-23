"""
rank.py - the main script. Run this to produce the final submission CSV.

What it does in order:
  1. Loads precomputed embeddings (from artifacts/ folder)
  2. Reads all 100,000 candidates
  3. Scores each one (honeypot check + must-have match + semantic + behavioral)
  4. Sorts by final score, takes top 100
  5. Writes output/submission.csv

Usage:
  python rank.py

Runtime: under 2 minutes on any modern CPU.
Requires precompute.py to have been run at least once first.
"""

import json
import csv
import os
import time
from tqdm import tqdm

from semantic import load_semantic_scores
from scorer import score_candidate, generate_reasoning

CANDIDATES_FILE = "data/candidates.jsonl"
OUTPUT_FILE     = "output/submission.csv"
TOP_N           = 100


def main():
    start = time.time()
    os.makedirs("output", exist_ok=True)

    print("Step 1/4: Loading semantic similarity scores...")
    semantic_scores = load_semantic_scores()

    print("Step 2/4: Scoring all 100,000 candidates...")
    results = []
    excluded = 0

    with open(CANDIDATES_FILE) as f:
        for line in tqdm(f, total=100000, desc="Scoring", unit="candidates"):
            candidate = json.loads(line)
            result    = score_candidate(candidate, semantic_scores)

            if result["excluded"]:
                excluded += 1
                continue

            results.append({
                "candidate_id": candidate["candidate_id"],
                "score":        result["final_score"],
                "reasoning":    generate_reasoning(candidate, result),
            })

    print(f"  Excluded {excluded} honepot candidates.")
    print(f"  Remaining pool: {len(results):,} candidates")

    print("Step 3/4: Ranking...")
    results.sort(key=lambda x: x["score"], reverse=True)
    top100 = results[:TOP_N]

    print("Step 4/4: Writing output/submission.csv...")
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "candidate_id", "score", "reasoning"])
        writer.writeheader()
        for rank, row in enumerate(top100, start=1):
            writer.writerow({
                "rank":         rank,
                "candidate_id": row["candidate_id"],
                "score":        row["score"],
                "reasoning":    row["reasoning"],
            })

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f} seconds.")
    print(f"Output: {OUTPUT_FILE}")
    print(f"\nTop 10 preview:")
    print(f"{'Rank':<5} {'Candidate':<15} {'Score':<8} Reasoning")
    print("-" * 80)
    for i, row in enumerate(top100[:10], start=1):
        preview = row["reasoning"][:70] + "..." if len(row["reasoning"]) > 70 else row["reasoning"]
        print(f"{i:<5} {row['candidate_id']:<15} {row['score']:<8.4f} {preview}")


if __name__ == "__main__":
    main()

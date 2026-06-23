# Redrob Candidate Ranker

An AI-powered candidate ranking system for the Redrob Senior AI Engineer role.
Built for the Bolt IoT Data & AI Challenge.

---

## What it does

Reads 100,000 candidate profiles and ranks them the way a great recruiter would —
not by counting keywords, but by checking whether a candidate's actual work history,
skill evidence, and platform behavior match what the role genuinely needs.

**Input:** `data/candidates.jsonl` (100,000 profiles)  
**Output:** `output/submission.csv` (top 100 ranked candidates with scores and reasoning)  
**Runtime:** under 2 minutes on any modern CPU

---

## How it works

The system scores every candidate through 5 layered checks:

### 1. Honeypot Detection (filters first)
Before any scoring happens, we cross-check each profile's own numbers against each other:
- A skill marked "expert" with 0 months of actual use → flagged
- Total career duration far exceeding stated years of experience → flagged
- Job duration that doesn't match its start/end dates → flagged

59 candidates were caught and excluded this way. None appear in the output.

### 2. Must-Have Matching
The JD lists 4 non-negotiables. We check for genuine evidence of each — not just
a skill tag, but real usage backed by months and endorsements:
- **Embeddings/retrieval experience** (Sentence Transformers, RAG, Semantic Search, etc.)
- **Vector DB / hybrid search** (Pinecone, Qdrant, Weaviate, FAISS, OpenSearch, etc.)
- **Python** (confirmed with duration and proficiency)
- **Ranking evaluation experience** (NDCG, MRR, A/B testing — checked in both skill tags
  and free-text career descriptions, since this category almost never appears as a tag)

A skill with 0 endorsements and 0 duration is treated as weak evidence, not a point
in a candidate's favour.

### 3. Semantic Similarity
Each candidate's full career narrative (headline + summary + job descriptions + skills)
is converted into a meaning vector using `all-MiniLM-L6-v2`. We compare this to the
JD's meaning vector using cosine similarity.

This catches candidates who genuinely did the work but never wrote "RAG" or "Pinecone"
— and penalises candidates who keyword-stuffed their profile without real depth behind it.

### 4. Behavioral Signals
The Redrob platform signals tell us how available and reachable a candidate actually is:
- **Recency:** candidates inactive for 6+ months are down-weighted heavily
- **Recruiter response rate:** a 95% responder ranks higher than a 20% ghost
- **Open to work flag:** small additional boost

### 5. Penalty Multipliers
Applied after the base score is calculated:
- Based outside India → 85% penalty (JD: no visa sponsorship)
- Entire career at IT-services firms (TCS, Infosys, Wipro, etc.) → 70% penalty (JD: explicit concern)
- Senior/Architect title with no recent hands-on NLP work → 30% penalty
- Notice period over 90 days → 15% penalty

---

## Final score formula
base = (must_have_avg × 0.35) + (coverage_breadth × 0.10)

+ (semantic_similarity × 0.25) + (experience_score × 0.15)

+ (behavioral_score × 0.15)

+ company_tier_bonus + nice_to_have_bonus
final_score = base × penalty_multipliers   (capped at 1.0)

All weights are traceable to specific lines in `data/job_description.docx`.

---

## Project structure
Redrob-Candidate-Ranker/

├── config.py                  # JD requirements as structured rules

├── filters.py                 # Honeypot detection (3 consistency checks)

├── matching.py                # Must-have scoring + employer tier signal

├── semantic.py                # Loads precomputed embeddings, computes similarity

├── scorer.py                  # Combines all signals into final score + reasoning

├── rank.py                    # Main script: reads candidates, writes output CSV

├── precompute.py              # One-time setup: encodes all 100K candidates

├── explore_data.py            # EDA script used during development

├── test_filters.py            # Verifies honeypot detection across full dataset

├── test_matching.py           # Verifies must-have scoring stats

├── requirements.txt           # Exact package versions

├── data/                      # Raw input files (not committed — too large for GitHub)

│   ├── candidates.jsonl

│   ├── job_description.docx

│   └── ...

├── artifacts/                 # Precomputed embeddings (not committed — 153MB)

│   ├── embeddings.npy

│   ├── candidate_ids.npy

│   └── jd_vector.npy

└── output/

└── submission.csv         # Final ranked output

---

## Setup and usage

### Requirements
- Python 3.9+
- ~2 GB disk space (for the embedding model cache)
- The `candidates.jsonl` file from the hackathon data pack

### 1. Clone the repo and set up environment

```bash
git clone https://github.com/121425408001-ctrl/Redrob-Candidate-Ranker.git
cd Redrob-Candidate-Ranker
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 2. Add the data file

Copy `candidates.jsonl` (and other hackathon data files) into the `data/` folder:
data/candidates.jsonl

### 3. Precompute embeddings (one-time, ~5-10 minutes)

```bash
python precompute.py
```

This downloads `all-MiniLM-L6-v2` (~90MB, once), encodes all 100,000 candidate
texts, and saves the result to `artifacts/`. You only need to run this once.

### 4. Run the ranker

```bash
python rank.py
```

Completes in under 2 minutes. Output written to `output/submission.csv`.

---

## Key design decisions

**Why no LLM calls during ranking?**
The submission is evaluated in an offline, CPU-only sandbox with a 5-minute time limit.
An LLM call per candidate (even a small one) would take hours for 100,000 profiles.
Pre-computed embeddings + fast arithmetic is both faster and more transparent.

**Why check free text AND skill tags?**
After analysing the full dataset, we found that "ranking evaluation experience" (NDCG,
MRR, A/B testing) almost never appears as a skill tag — it only shows up in job
description text. A system that only checked skill tags would miss this requirement
entirely for most candidates.

**Why are skill tags weighted by duration and endorsements?**
The dataset contains profiles where skills are marked "expert" with 0 months of use.
Weighting by real usage evidence directly defeats this form of gaming.

**Why penalty multipliers rather than hard filters for consulting firms?**
The JD uses language like "we'll probably not move forward" rather than "hard no."
A 70% penalty reflects that nuance — a consulting-background candidate with genuinely
strong skills still has a path to the top 100, just a harder one.

---

## What makes this different from keyword matching

A keyword-matching system would rank highly anyone who listed "Pinecone, FAISS, NDCG"
in their skills. Our system only ranks that person highly if:
- Those skills have real months and endorsements behind them
- Their career history text describes work consistent with the JD's requirements
- Their semantic similarity score confirms their story sounds like the JD's story
- They are in India, reachable, and available

The sample submission provided by the hackathon (HR Manager ranked #1, Content Writer
ranked #4) is a deliberate example of what keyword matching produces. Our top 10 are
all India-based ML/Search/NLP engineers with 5-9 years of hands-on retrieval
and ranking experience at real product companies.

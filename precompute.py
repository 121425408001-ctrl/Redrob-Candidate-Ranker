"""
precompute.py - ONE-TIME setup step that runs before ranking.

What it does:
  Converts every candidate's career story into a "meaning vector" (a list
  of 384 numbers) using a small AI model that understands language.
  Saves all 100K vectors to artifacts/embeddings.npy so the main ranking
  script can load them instantly without re-encoding.

Why pre-compute instead of encoding at ranking time:
  Encoding 100K texts takes 3-5 minutes on CPU. The hackathon's timed
  stage only allows 5 min total for ranking. Pre-computing means the
  actual ranking step just loads a file and does fast math - no encoding
  needed. The model itself runs fully offline once downloaded.

Run this ONCE after setting up the project:
  python precompute.py
"""

import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

CANDIDATES_FILE = "data/candidates.jsonl"
OUTPUT_DIR = "artifacts"
EMBEDDINGS_FILE = os.path.join(OUTPUT_DIR, "embeddings.npy")
IDS_FILE = os.path.join(OUTPUT_DIR, "candidate_ids.npy")
BATCH_SIZE = 64
MODEL_NAME = "all-MiniLM-L6-v2"

JD_QUERY = """
We are hiring a Senior AI Engineer to build the core retrieval and ranking
infrastructure behind an AI-powered hiring platform. This is a hands-on
engineering role, not a research or advisory position.

You will design and ship embedding-based candidate retrieval systems using
dense vector search. You will work with vector databases such as Pinecone,
Qdrant, Weaviate, FAISS, or Milvus to build hybrid search pipelines combining
semantic search with keyword filters. You will evaluate ranking quality using
offline metrics like NDCG and MRR, and run online A/B experiments to measure
real-world impact on recruiter workflows.

Strong Python is required. Experience with semantic search, information
retrieval, sentence transformers, and large-scale indexing is essential.
You should have shipped production ML systems, not just prototype notebooks.

Bonus if you have experience with learning-to-rank models, LLM fine-tuning
with LoRA or PEFT, or have worked in HR-tech or marketplace search.
Experience with MLOps tooling like MLflow, Weights & Biases, or Kubeflow
is also a plus.

We do NOT want pure researchers with no production experience, consultants
whose entire career is at TCS, Infosys, Wipro, Accenture or similar,
or engineers whose background is primarily computer vision, speech recognition,
or robotics with no NLP or information retrieval exposure.
"""


def candidate_text(c):
    parts = []
    p = c["profile"]
    if p.get("headline"):
        parts.append(p["headline"])
    if p.get("summary"):
        parts.append(p["summary"])
    for job in c["career_history"]:
        if job.get("description"):
            parts.append(f"{job['title']} at {job['company']}: {job['description']}")
    skill_names = [s["name"] for s in c["skills"]]
    if skill_names:
        parts.append("Skills: " + ", ".join(skill_names))
    return " ".join(parts)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Loading model: {MODEL_NAME}")
    print("(First run downloads ~80MB - subsequent runs load from cache instantly)")
    model = SentenceTransformer(MODEL_NAME)

    print("\nEncoding job description...")
    jd_vector = model.encode(JD_QUERY, normalize_embeddings=True)
    np.save(os.path.join(OUTPUT_DIR, "jd_vector.npy"), jd_vector)
    print(f"JD vector saved. Shape: {jd_vector.shape}")

    print("\nReading candidates...")
    candidate_ids = []
    texts = []
    with open(CANDIDATES_FILE) as f:
        for line in tqdm(f, desc="Reading", unit="candidates"):
            c = json.loads(line)
            candidate_ids.append(c["candidate_id"])
            texts.append(candidate_text(c))

    print(f"\nEncoding {len(texts):,} candidate texts in batches of {BATCH_SIZE}...")
    print("This takes 3-6 minutes on CPU. Go get a coffee.")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    np.save(EMBEDDINGS_FILE, embeddings)
    np.save(IDS_FILE, np.array(candidate_ids))

    print(f"\nDone!")
    print(f"  Embeddings: {EMBEDDINGS_FILE} ({embeddings.shape})")
    print(f"  IDs:        {IDS_FILE}")
    print(f"  File size:  {os.path.getsize(EMBEDDINGS_FILE) / 1e6:.1f} MB")
    print(f"\nYou only need to run this once. Run rank.py next.")


if __name__ == "__main__":
    main()

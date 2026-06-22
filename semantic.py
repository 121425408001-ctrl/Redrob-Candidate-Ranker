"""
semantic.py - loads the precomputed embeddings and computes how similar
each candidate's career story is to the job description.

This is the "understanding meaning, not just matching keywords" part.
A candidate who never wrote "RAG" or "Pinecone" but spent 2 years
building exactly that kind of system will score high here.

This file is imported by rank.py - it does NOT run on its own.
"""

import os
import numpy as np

ARTIFACTS_DIR = "artifacts"
EMBEDDINGS_FILE = os.path.join(ARTIFACTS_DIR, "embeddings.npy")
IDS_FILE = os.path.join(ARTIFACTS_DIR, "candidate_ids.npy")
JD_VECTOR_FILE = os.path.join(ARTIFACTS_DIR, "jd_vector.npy")


def load_semantic_scores():
    """
    Returns a dict: {candidate_id -> semantic_similarity_score (0.0 to 1.0)}

    Cosine similarity between two normalized vectors is just a dot product.
    Since we normalized at encode time, this is one matrix multiply
    across all 100K vectors - takes under a second.
    """
    if not os.path.exists(EMBEDDINGS_FILE):
        raise FileNotFoundError(
            f"Embeddings file not found at {EMBEDDINGS_FILE}.\n"
            f"Please run: python precompute.py"
        )

    print("Loading precomputed embeddings...", end=" ", flush=True)
    embeddings = np.load(EMBEDDINGS_FILE)
    candidate_ids = np.load(IDS_FILE)
    jd_vector = np.load(JD_VECTOR_FILE)
    print(f"done. ({len(candidate_ids):,} candidates)")

    similarities = embeddings @ jd_vector

    # Normalize to 0-1 range
    similarities = (similarities - similarities.min()) / (similarities.max() - similarities.min())

    return dict(zip(candidate_ids.tolist(), similarities.tolist()))

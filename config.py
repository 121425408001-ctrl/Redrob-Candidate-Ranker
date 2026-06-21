"""
config.py - the Senior AI Engineer JD, turned into rules our code can check.

Built from two passes through the real data:
1. Only 133 distinct skill names exist in the whole 100K pool, in 3 clear
   tiers by rarity: "noise" skills (~12,000 candidates each - generic
   stuff present in unrelated roles too), "trendy AI" skills (~5,000 each
   - genAI-curious, not necessarily deep), and "specialist" skills
   (~1,300-1,400 each - Python, PyTorch, NLP, Qdrant, etc. - this is
   where the real engineers are).
2. Only 63 distinct companies exist too. Most are generic filler
   (~23,500 candidates each, mixing real IT-services firms and joke
   names like "Hooli" at the same frequency - company name alone isn't
   a strong signal at this tier). But ~15 companies appear only 58-81
   times each and are genuine Indian AI-focused companies (Sarvam AI,
   Krutrim, Haptik, etc.) - working at one of these is real positive
   evidence. A handful of FAANG companies appear only 10-14 times each.

We also found "evaluation experience" barely exists as a skill tag at
all - it's almost only mentioned in free-text job descriptions - so
matching checks both skill tags AND career history text, not tags alone.
"""

# ---- Role basics (JD: "Experience Required: 5-9 years") ----
EXPERIENCE_BAND_MIN = 5
EXPERIENCE_BAND_MAX = 9
EXPERIENCE_IDEAL_MIN = 6
EXPERIENCE_IDEAL_MAX = 8

# ---- "Things you absolutely need" ----
MUST_HAVE_CATEGORIES = {
    "embeddings_retrieval": {
        "strong_skills": [
            "Information Retrieval", "Semantic Search", "Sentence Transformers",
            "Embeddings", "Vector Search", "RAG", "Recommendation Systems",
            "Hugging Face Transformers", "NLP", "Natural Language Processing",
            "Information Retrieval Systems", "Text Encoders", "Vector Representations",
            "Content Matching", "Search & Discovery", "Document Processing",
            "Haystack", "LlamaIndex",
        ],
        "text_keywords": [
            "embedding", "semantic search", "dense retrieval", "vector search",
            "retrieval system", "rag pipeline", "sentence-transformers", "sentence transformers",
        ],
    },
    "vector_db_hybrid_search": {
        "strong_skills": [
            "Pinecone", "FAISS", "Qdrant", "Weaviate", "Milvus", "pgvector",
            "OpenSearch", "Elasticsearch", "Search Backend", "Search Infrastructure",
            "Indexing Algorithms",
        ],
        "text_keywords": [
            "vector database", "vector db", "hybrid search",
            "approximate nearest neighbor", "ann index",
        ],
    },
    "python": {
        "strong_skills": ["Python"],
        "text_keywords": ["python"],
    },
    "eval_ranking_experience": {
        "strong_skills": ["Learning to Rank", "BM25", "Ranking Systems", "Information Retrieval Systems"],
        "text_keywords": [
            "ndcg", "mrr", "a/b test", "ab test", "offline evaluation",
            "online evaluation", "evaluation framework", "precision@", "recall@",
            "click-through", "ctr", "map@", "mean average precision",
        ],
    },
}

PROFICIENCY_WEIGHTS = {"beginner": 0.25, "intermediate": 0.5, "advanced": 0.75, "expert": 1.0}

# ---- "Things we'd like but won't reject you for" - bonus only ----
NICE_TO_HAVE_SKILLS = [
    "LoRA", "QLoRA", "PEFT", "Fine-tuning LLMs", "MLOps", "MLflow",
    "Kubeflow", "BentoML", "Weights & Biases", "Reinforcement Learning",
]

# ---- "Things we explicitly do NOT want" ----
CONSULTING_FIRMS = [
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "hcl", "tech mahindra", "mindtree", "mphasis",
]

CV_SPEECH_ROBOTICS_SKILLS = [
    "Computer Vision", "OpenCV", "YOLO", "Image Classification",
    "Object Detection", "CNN", "GANs", "Diffusion Models",
    "Speech Recognition", "ASR", "TTS",
]
NLP_IR_SKILLS = [
    "NLP", "Natural Language Processing", "Information Retrieval",
    "Information Retrieval Systems", "Semantic Search", "Search & Discovery",
    "Search Backend", "Search Infrastructure", "Text Encoders",
    "Document Processing", "Embeddings", "Vector Search", "RAG",
    "BM25", "Learning to Rank",
]

STALE_TITLE_KEYWORDS = ["architect", "head of", "director", "vp ", "vice president"]

# ---- Positive employer signal (confirmed exact company names) ----
AI_SPECIALIST_COMPANIES = [
    "Genpact AI", "Glance", "Rephrase.ai", "Aganitha", "Niramai", "Saarthi.ai",
    "Sarvam AI", "Mad Street Den", "Observe.AI", "Krutrim", "Wysa", "Haptik",
    "Verloop.io", "Yellow.ai", "Locobuzz",
]
BIG_TECH_COMPANIES = ["Google", "Netflix", "Amazon", "Salesforce", "Uber", "Meta", "Adobe"]

# ---- Location (JD: Pune/Noida preferred, these cities explicitly welcomed) ----
PREFERRED_LOCATIONS = ["pune", "noida"]
WELCOME_LOCATIONS = [
    "hyderabad", "pune", "mumbai", "delhi ncr", "noida",
    "gurgaon", "gurugram", "new delhi",
]

# ---- Notice period (JD: sub-30 ideal, 30+ in scope but higher bar) ----
NOTICE_PERIOD_GREAT_DAYS = 30
NOTICE_PERIOD_MAX_DAYS = 180

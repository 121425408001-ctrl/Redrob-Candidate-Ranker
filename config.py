"""
config.py - the Senior AI Engineer JD, turned into rules our code can check.

Every list/number below is traceable to a specific line in job_description.docx.
If we ever change a threshold here, we should be able to say why in one sentence.
"""

# ---- Role basics (JD: "Experience Required: 5-9 years") ----
EXPERIENCE_BAND_MIN = 5
EXPERIENCE_BAND_MAX = 9
EXPERIENCE_IDEAL_MIN = 6
EXPERIENCE_IDEAL_MAX = 8

MUST_HAVE_CATEGORIES = {
    "embeddings_retrieval": [
        "sentence-transformers", "sentence transformers", "openai embeddings",
        "bge", "e5", "embeddings", "embedding", "semantic search",
        "dense retrieval", "text embeddings",
    ],
    "vector_db_hybrid_search": [
        "pinecone", "weaviate", "qdrant", "milvus", "opensearch",
        "elasticsearch", "faiss", "vector database", "vector db",
        "hybrid search",
    ],
    "python": ["python"],
    "eval_frameworks": [
        "ndcg", "mrr", "map", "a/b test", "ab testing",
        "offline evaluation", "ranking evaluation", "online evaluation",
    ],
}

NICE_TO_HAVE_TERMS = [
    "lora", "qlora", "peft", "fine-tuning", "fine tuning",
    "learning to rank", "learning-to-rank", "xgboost",
    "hr-tech", "recruiting tech", "marketplace",
    "distributed systems", "large-scale inference",
    "open source", "open-source",
]

CONSULTING_FIRMS = ["tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini"]

CV_SPEECH_ROBOTICS_TERMS = [
    "computer vision", "speech recognition", "robotics",
    "image classification", "object detection",
]
NLP_IR_TERMS = [
    "nlp", "natural language processing", "information retrieval",
    "search", "retrieval", "ranking", "embeddings",
]

STALE_TITLE_KEYWORDS = ["architect", "head of", "director", "vp ", "vice president"]

PREFERRED_LOCATIONS = ["pune", "noida"]
WELCOME_LOCATIONS = [
    "hyderabad", "pune", "mumbai", "delhi ncr", "noida",
    "gurgaon", "gurugram", "new delhi",
]

NOTICE_PERIOD_GREAT_DAYS = 30
NOTICE_PERIOD_MAX_DAYS = 180

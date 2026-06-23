"""
scorer.py - computes a single final score for each candidate.

The formula has three layers:
  1. Base score (0-1): must-have match + semantic similarity + experience + behavioral
  2. Bonuses:          company tier, nice-to-have skills
  3. Penalty multipliers: consulting-only, non-India, stale title, long notice

Honeypot candidates are excluded before scoring (score = 0.0).

Every number here is traceable to a specific line in job_description.docx
or to a pattern we confirmed exists in the actual data.
"""

import datetime
import config
from filters import find_honeypot_reasons
from matching import (
    must_have_summary,
    nice_to_have_score,
    is_consulting_only_career,
    company_tier_bonus,
)

TODAY = datetime.date(2026, 6, 20)
CAT_LABELS = {
    "embeddings_retrieval":    "embeddings/retrieval",
    "vector_db_hybrid_search": "vector DB/hybrid search",
    "python":                  "Python",
    "eval_ranking_experience": "ranking evaluation",
}


def _experience_score(yoe):
    if 6.0 <= yoe <= 8.0:   return 1.0
    if 5.0 <= yoe <= 9.0:   return 0.8
    if 4.0 <= yoe < 5.0:    return 0.5
    if 9.0 < yoe <= 11.0:   return 0.5
    return 0.2


def _behavioral_score(rs):
    try:
        last_active = datetime.date.fromisoformat(rs["last_active_date"])
        days_inactive = (TODAY - last_active).days
    except Exception:
        days_inactive = 365

    if   days_inactive <= 14:  recency = 1.0
    elif days_inactive <= 30:  recency = 0.9
    elif days_inactive <= 90:  recency = 0.7
    elif days_inactive <= 180: recency = 0.4
    else:                      recency = 0.1

    response_rate = float(rs.get("recruiter_response_rate", 0.5))
    base = recency * 0.5 + response_rate * 0.5

    if rs.get("open_to_work_flag"):
        base = min(1.0, base * 1.1)

    return base, days_inactive


def _notice_multiplier(notice_days):
    if   notice_days <= 30:  return 1.00
    elif notice_days <= 60:  return 1.00
    elif notice_days <= 90:  return 0.95
    else:                    return 0.85


def _stale_title_penalty(candidate):
    title = candidate["profile"]["current_title"].lower()
    if not any(kw in title for kw in config.STALE_TITLE_KEYWORDS):
        return 1.0
    recent_hands_on = any(
        s.get("duration_months", 0) > 12 and s["name"] in config.NLP_IR_SKILLS
        for s in candidate["skills"]
    )
    return 0.7 if not recent_hands_on else 1.0


def score_candidate(candidate, semantic_scores):
    """
    Returns a dict with final_score and all intermediate values.
    final_score == 0.0 means the candidate was excluded (honeypot).
    """
    cid = candidate["candidate_id"]
    p   = candidate["profile"]
    rs  = candidate["redrob_signals"]

    # Step 0: honeypot check
    honeypot_reasons = find_honeypot_reasons(candidate)
    if honeypot_reasons:
        return {
            "final_score": 0.0,
            "excluded": True,
            "exclusion_reason": "; ".join(honeypot_reasons),
        }

    # Step 1: must-have match
    cat_scores, categories_met = must_have_summary(candidate)
    must_have_avg  = sum(cat_scores.values()) / 4
    coverage_bonus = categories_met / 4

    # Step 2: experience
    yoe = p["years_of_experience"]
    exp_score = _experience_score(yoe)

    # Step 3: semantic similarity
    sem_score = float(semantic_scores.get(cid, 0.5))

    # Step 4: behavioral
    beh_score, days_inactive = _behavioral_score(rs)

    # Step 5: bonuses
    nth_score  = nice_to_have_score(candidate)
    comp_bonus = company_tier_bonus(candidate)

    # Step 6: base score (weights sum to 1.0)
    base = (
        must_have_avg  * 0.35 +
        coverage_bonus * 0.10 +
        sem_score      * 0.25 +
        exp_score      * 0.15 +
        beh_score      * 0.15
    )
    base += comp_bonus * 0.05
    base += nth_score  * 0.03
    base  = min(1.0, base)

    # Step 7: penalty multipliers
    is_india        = p["country"].strip().lower() == "india"
    consulting_only = is_consulting_only_career(candidate)
    notice_days     = int(rs.get("notice_period_days", 90))

    penalty = 1.0
    if not is_india:    penalty *= 0.15
    if consulting_only: penalty *= 0.30
    penalty *= _stale_title_penalty(candidate)
    penalty *= _notice_multiplier(notice_days)

    final = round(min(1.0, base * penalty), 6)

    return {
        "final_score":      final,
        "excluded":         False,
        "must_have_avg":    must_have_avg,
        "categories_met":   categories_met,
        "category_scores":  cat_scores,
        "semantic_score":   sem_score,
        "exp_score":        exp_score,
        "behavioral_score": beh_score,
        "days_inactive":    days_inactive,
        "comp_bonus":       comp_bonus,
        "notice_days":      notice_days,
        "is_india":         is_india,
        "consulting_only":  consulting_only,
    }


def generate_reasoning(candidate, result):
    """
    Builds the 1-2 sentence reasoning string from the same numbers
    that produced the score. Never invents anything not in the data.
    """
    if result.get("excluded"):
        return f"Excluded: {result['exclusion_reason']}"

    p  = candidate["profile"]
    yoe = p["years_of_experience"]

    line1 = (
        f"{yoe:.1f} yrs, {p['current_title']} at {p['current_company']} "
        f"({p['location']})."
    )

    met    = result["categories_met"]
    cat_sc = result["category_scores"]
    strong = [CAT_LABELS[c] for c, sc in cat_sc.items() if sc >= 0.65]
    weak   = [CAT_LABELS[c] for c, sc in cat_sc.items() if sc < 0.30]

    coverage_str = f"Met {met}/4 must-haves"
    if strong:
        coverage_str += f"; strong in {', '.join(strong)}"
    if weak:
        coverage_str += f"; limited evidence of {', '.join(weak)}"
    coverage_str += "."

    signals = []
    d = result["days_inactive"]
    if   d <= 14: signals.append(f"active {d} days ago")
    elif d <= 30: signals.append(f"active ~{d} days ago")
    elif d <= 90: signals.append(f"last active {d} days ago")
    else:         signals.append(f"inactive {d}+ days")

    n = result["notice_days"]
    if   n <= 30: signals.append(f"{n}-day notice (immediate-ish)")
    elif n <= 60: signals.append(f"{n}-day notice")
    else:         signals.append(f"{n}-day notice (long)")

    if result["comp_bonus"] >= 1.0:
        signals.append("FAANG-tier employer history")
    elif result["comp_bonus"] > 0:
        signals.append("AI-specialist company background")

    if result["consulting_only"]:
        signals.append("entire career at IT-services firms (JD concern)")
    if not result["is_india"]:
        signals.append(f"based outside India ({p['location']}) — visa risk")

    line2 = "; ".join(signals).capitalize() + "." if signals else ""

    return f"{line1} {coverage_str} {line2}".strip()

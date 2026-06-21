"""
matching.py - checks one candidate against the JD's must-have requirements
and employer history, using the rules defined in config.py.
"""

import config


def career_text(candidate):
    parts = [ch.get("description", "") for ch in candidate["career_history"]]
    parts.append(candidate["profile"].get("summary", ""))
    parts.append(candidate["profile"].get("headline", ""))
    return " ".join(parts).lower()


def skill_strength(skill):
    """How much to trust a claimed skill - weak if barely used, even if proficiency says 'expert'."""
    proficiency_weight = config.PROFICIENCY_WEIGHTS.get(skill.get("proficiency"), 0.25)
    trust = max(0.2, min(1.0, skill.get("duration_months", 0) / 18))
    return proficiency_weight * trust


def category_score(candidate, category_name):
    """0.0-1.0 score for how well a candidate covers one must-have category."""
    rules = config.MUST_HAVE_CATEGORIES[category_name]
    skill_lookup = {s["name"]: s for s in candidate["skills"]}

    best_skill_score = 0.0
    for name in rules["strong_skills"]:
        if name in skill_lookup:
            best_skill_score = max(best_skill_score, skill_strength(skill_lookup[name]))

    text = career_text(candidate)
    text_bonus = 0.3 if any(kw in text for kw in rules["text_keywords"]) else 0.0

    return min(1.0, best_skill_score + text_bonus)


def must_have_summary(candidate):
    """Returns {category: score} and how many of the 4 categories are genuinely met."""
    scores = {cat: category_score(candidate, cat) for cat in config.MUST_HAVE_CATEGORIES}
    met = sum(1 for v in scores.values() if v >= 0.5)
    return scores, met


def nice_to_have_score(candidate):
    """Small bonus (0.0-1.0) for extra skills the JD said it'd like but won't require."""
    skill_names = {s["name"] for s in candidate["skills"]}
    hits = sum(1 for s in config.NICE_TO_HAVE_SKILLS if s in skill_names)
    return min(1.0, hits / 4)


def is_consulting_only_career(candidate):
    """True if every job in this candidate's history is at a pure IT-services firm."""
    companies = [ch["company"].lower() for ch in candidate["career_history"]]
    if not companies:
        return False
    return all(any(firm in comp for firm in config.CONSULTING_FIRMS) for comp in companies)


def company_tier_bonus(candidate):
    """Real positive signal: did they ever work at a known AI-focused company or big tech?"""
    companies = {ch["company"] for ch in candidate["career_history"]}
    if companies & set(config.BIG_TECH_COMPANIES):
        return 1.0
    if companies & set(config.AI_SPECIALIST_COMPANIES):
        return 0.7
    return 0.0

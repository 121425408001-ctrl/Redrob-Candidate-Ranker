"""
filters.py - catches "honeypot" candidates: profiles that are internally
impossible. The hackathon rules say there are ~80 of these hidden in the
100K pool, and if more than 10% of our top 100 are honeypots, we get
disqualified at Stage 3 - automatically, no matter how good our ranking
otherwise is.

We find these by comparing fields within a candidate's own profile
against each other - not by guessing which companies or names look fake.
"""

import datetime

TODAY = datetime.date(2026, 6, 20)


def _parse_date(date_str):
    return datetime.date.fromisoformat(date_str) if date_str else TODAY


def find_honeypot_reasons(candidate):
    """
    Checks one candidate for internal impossibilities.
    Returns a list of reasons (empty list = looks legit).
    """
    reasons = []

    # Check 1: a skill marked "expert" but supposedly never used
    for skill in candidate["skills"]:
        if skill["proficiency"] == "expert" and skill.get("duration_months", 0) == 0:
            reasons.append(f"Lists '{skill['name']}' as expert with 0 months of use")

    # Check 2: total time across all jobs is way more than stated years of experience
    total_months_worked = sum(job.get("duration_months", 0) for job in candidate["career_history"])
    stated_yoe_months = candidate["profile"]["years_of_experience"] * 12
    if total_months_worked > stated_yoe_months + 12:  # 1 year slack for rounding
        reasons.append(
            f"Career history totals {total_months_worked} months "
            f"but stated experience is only {stated_yoe_months:.0f} months"
        )

    # Check 3: a job's stated duration doesn't match its actual start/end dates
    for job in candidate["career_history"]:
        start = _parse_date(job["start_date"])
        end = _parse_date(job["end_date"]) if job["end_date"] else TODAY
        actual_months = (end.year - start.year) * 12 + (end.month - start.month)
        stated_months = job["duration_months"]
        if abs(actual_months - stated_months) > 6:  # 6 month slack
            reasons.append(
                f"Says {stated_months} months at {job['company']}, but dates "
                f"({job['start_date']} to {job['end_date'] or 'present'}) "
                f"only span ~{actual_months} months"
            )

    return reasons


def is_honeypot(candidate):
    return len(find_honeypot_reasons(candidate)) > 0

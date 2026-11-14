"""
Scoring and evaluation logic for First Day career simulator.
Pure Python, free of Streamlit dependencies, and fully unit-testable.
"""

from __future__ import annotations
from typing import Dict, List, Any


def compute_readiness(current_skills: Dict[str, int], target_skills: Dict[str, int]) -> float:
    """
    Computes hiring readiness percentage:
    readiness_pct = sum(min(level, target)) / sum(target) * 100
    Clamped between 0.0 and 100.0 and rounded to 1 decimal place.
    """
    if not target_skills:
        return 100.0

    total_target = sum(target_skills.values())
    if total_target == 0:
        return 100.0

    accumulated = 0
    for skill, target in target_skills.items():
        current = current_skills.get(skill, 0)
        accumulated += min(max(0, current), target)

    pct = (accumulated / total_target) * 100.0
    return round(min(100.0, max(0.0, pct)), 1)


def find_skill_gaps(current_skills: Dict[str, int], target_skills: Dict[str, int]) -> List[Dict[str, Any]]:
    """
    Identifies all required skills where current level is strictly less than target level.
    Returns a list of gap dictionaries:
    [{"skill": str, "current_level": int, "target_level": int, "gap": int}]
    """
    gaps: List[Dict[str, Any]] = []
    for skill, target in target_skills.items():
        current = current_skills.get(skill, 0)
        if current < target:
            gaps.append({
                "skill": skill,
                "current_level": current,
                "target_level": target,
                "gap": target - current
            })
    return gaps


def generate_roadmap(
    current_skills: Dict[str, int],
    target_skills: Dict[str, int],
    prerequisites_order: List[str]
) -> List[Dict[str, Any]]:
    """
    Constructs an ordered learning roadmap from missing skills.
    Sorting strategy:
    1. Prerequisite chain order (earlier foundational skills first)
    2. Descending gap magnitude (larger gaps first if equal prerequisite rank)
    """
    gaps = find_skill_gaps(current_skills, target_skills)
    order_map = {skill: idx for idx, skill in enumerate(prerequisites_order)}
    fallback_index = len(prerequisites_order) + 100

    def sort_key(item: Dict[str, Any]):
        prereq_rank = order_map.get(item["skill"], fallback_index)
        gap_magnitude = -item["gap"]  # negative for descending order
        return (prereq_rank, gap_magnitude, item["skill"])

    return sorted(gaps, key=sort_key)


def update_skills_after_review(
    current_skills: Dict[str, int],
    score: int,
    skills_demonstrated: List[str],
    max_level: int = 3
) -> Dict[str, int]:
    """
    Updates skill levels based on Arjun's review score:
    - score >= 70: increments each demonstrated skill by 1 (max capped at max_level).
    - score < 50: no level increases (records gaps for Ravi).
    - 50 <= score < 70: no level increase (requires mastery).
    """
    updated = dict(current_skills)
    if score >= 70:
        for skill in skills_demonstrated:
            current = updated.get(skill, 0)
            updated[skill] = min(max_level, current + 1)
    return updated


def is_passing_score(score: int, pass_threshold: int = 60) -> bool:
    """
    Determines if a ticket submission is sufficient to advance (>= 60)
    or requires coaching intervention (< 60).
    """
    return score >= pass_threshold


def get_weakest_skills(current_skills: Dict[str, int], target_skills: Dict[str, int]) -> List[str]:
    """
    Ranks required skills by need:
    1. Largest gap (target - current)
    2. Lowest current level
    """
    gaps = find_skill_gaps(current_skills, target_skills)
    gaps.sort(key=lambda g: (-g["gap"], g["current_level"], g["skill"]))
    return [g["skill"] for g in gaps]

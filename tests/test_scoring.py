"""
Unit test suite for scoring.py
Covers readiness calculation, gap analysis, roadmap ordering, and review level transitions.
"""

import pytest
from scoring import (
    compute_readiness,
    find_skill_gaps,
    generate_roadmap,
    update_skills_after_review,
    is_passing_score,
    get_weakest_skills,
)


@pytest.fixture
def full_stack_targets():
    return {
        "HTML": 2,
        "CSS": 2,
        "JavaScript": 3,
        "React": 3,
        "Node.js": 2,
        "SQL": 2,
        "Git": 2,
    }


@pytest.fixture
def data_analyst_targets():
    return {
        "Excel": 2,
        "SQL": 3,
        "Python": 3,
        "Statistics": 2,
        "Data Visualization": 2,
    }


@pytest.fixture
def demo_student_skills():
    return {
        "Python": 2,
        "SQL": 2,
        "HTML": 1,
    }


def test_readiness_empty_skills(full_stack_targets):
    readiness = compute_readiness({}, full_stack_targets)
    assert readiness == 0.0


def test_readiness_full_mastery(full_stack_targets):
    mastery_skills = {k: v for k, v in full_stack_targets.items()}
    readiness = compute_readiness(mastery_skills, full_stack_targets)
    assert readiness == 100.0


def test_readiness_exceeding_targets_clamped(full_stack_targets):
    overachieved = {k: 3 for k in full_stack_targets.keys()}
    readiness = compute_readiness(overachieved, full_stack_targets)
    # Total sum of targets is 16. Even if skills are 3, min(3, target) equals target, so 100.0%.
    assert readiness == 100.0


def test_readiness_demo_student_full_stack(demo_student_skills, full_stack_targets):
    # Targets total = 16.
    # Demo student has HTML=1 (target 2 -> min=1), SQL=2 (target 2 -> min=2), Python=2 (not in targets -> 0).
    # Accumulated = 1 + 2 = 3. 3 / 16 * 100 = 18.75% -> 18.8%
    readiness = compute_readiness(demo_student_skills, full_stack_targets)
    assert readiness == 18.8


def test_readiness_demo_student_data_analyst(demo_student_skills, data_analyst_targets):
    # Targets total = 12.
    # Demo student has Python=2 (target 3 -> min=2), SQL=2 (target 3 -> min=2).
    # Accumulated = 4 / 12 * 100 = 33.333% -> 33.3%
    readiness = compute_readiness(demo_student_skills, data_analyst_targets)
    assert readiness == 33.3


def test_readiness_empty_target():
    assert compute_readiness({"Python": 2}, {}) == 100.0


def test_find_skill_gaps(demo_student_skills, full_stack_targets):
    gaps = find_skill_gaps(demo_student_skills, full_stack_targets)
    gap_skills = {g["skill"]: g for g in gaps}

    # SQL is at target (2 == 2), so it should NOT be in gaps
    assert "SQL" not in gap_skills

    # HTML is 1 vs target 2 -> gap 1
    assert "HTML" in gap_skills
    assert gap_skills["HTML"]["gap"] == 1

    # JavaScript is 0 vs target 3 -> gap 3
    assert "JavaScript" in gap_skills
    assert gap_skills["JavaScript"]["gap"] == 3

    # React is 0 vs target 3 -> gap 3
    assert "React" in gap_skills
    assert gap_skills["React"]["gap"] == 3

    # Node.js is 0 vs target 2 -> gap 2
    assert "Node.js" in gap_skills
    assert gap_skills["Node.js"]["gap"] == 2


def test_generate_roadmap_ordering(demo_student_skills, full_stack_targets):
    prereq_order = ["HTML", "CSS", "Git", "JavaScript", "React", "Node.js", "SQL"]
    roadmap = generate_roadmap(demo_student_skills, full_stack_targets, prereq_order)
    skills_in_order = [item["skill"] for item in roadmap]

    # Prerequisite order must be preserved: HTML -> CSS -> Git -> JavaScript -> React -> Node.js
    assert skills_in_order.index("HTML") < skills_in_order.index("JavaScript")
    assert skills_in_order.index("JavaScript") < skills_in_order.index("React")
    assert skills_in_order.index("React") < skills_in_order.index("Node.js")


def test_update_skills_strong_review():
    current = {"HTML": 1, "JavaScript": 1, "React": 0}
    # Score 85 >= 70 raises demonstrated skills
    updated = update_skills_after_review(current, score=85, skills_demonstrated=["HTML", "JavaScript"])
    assert updated["HTML"] == 2
    assert updated["JavaScript"] == 2
    assert updated["React"] == 0  # not demonstrated, remains unchanged


def test_update_skills_max_clamped():
    current = {"HTML": 3}
    updated = update_skills_after_review(current, score=90, skills_demonstrated=["HTML"], max_level=3)
    assert updated["HTML"] == 3  # clamped to max 3


def test_update_skills_weak_review_no_change():
    current = {"HTML": 1, "JavaScript": 0}
    # Score 45 < 50 records gaps and does not raise level
    updated = update_skills_after_review(current, score=45, skills_demonstrated=["JavaScript"])
    assert updated["JavaScript"] == 0
    assert updated["HTML"] == 1


def test_update_skills_marginal_score_no_change():
    current = {"JavaScript": 1}
    # Score 62 (between 50 and 69) does not raise level
    updated = update_skills_after_review(current, score=62, skills_demonstrated=["JavaScript"])
    assert updated["JavaScript"] == 1


def test_is_passing_score():
    assert is_passing_score(60) is True
    assert is_passing_score(85) is True
    assert is_passing_score(59) is False
    assert is_passing_score(40) is False


def test_get_weakest_skills(demo_student_skills, full_stack_targets):
    weakest = get_weakest_skills(demo_student_skills, full_stack_targets)
    # Gaps of 3 (JavaScript, React) should rank ahead of gap of 1 (HTML)
    assert weakest[0] in ["JavaScript", "React"]
    assert weakest[1] in ["JavaScript", "React"]
    assert weakest[-1] == "HTML"

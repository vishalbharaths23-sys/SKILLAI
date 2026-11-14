"""
Integration tests for Orchestrator multi-agent coordination.
Tests demo student loading, weak vs strong submission loops, role transitions, and logging.
"""

import pytest
from state import LearnerState
from orchestrator import Orchestrator
from scoring import find_skill_gaps


@pytest.fixture
def orchestrator():
    return Orchestrator()


@pytest.fixture
def state(orchestrator):
    s = LearnerState()
    orchestrator.load_demo_student(s)
    return s


def test_load_demo_student_gaps_and_readiness(orchestrator, state):
    assert state.skills == {"Python": 2, "SQL": 2, "HTML": 1}
    assert state.current_role == "full_stack_developer"

    targets = orchestrator.get_role_targets("full_stack_developer")
    gaps = find_skill_gaps(state.skills, targets)
    gap_names = {g["skill"] for g in gaps}

    # Acceptance Criterion 1: Gaps shown must include JavaScript, React, Node.js
    assert "JavaScript" in gap_names
    assert "React" in gap_names
    assert "Node.js" in gap_names

    # Readiness should be 18.8%
    assert state.readiness_history[0]["readiness"] == 18.8
    assert state.current_ticket is not None

    # Agent log has handoff records
    sources = [log.source_agent for log in state.agent_logs]
    assert "Maya" in sources
    assert "Profiler" in sources


def test_weak_submission_triggers_ravi(orchestrator, state):
    initial_skills = dict(state.skills)
    ticket_id = state.current_ticket.id

    # Acceptance Criterion 2: Submitting a weak answer triggers Ravi and leaves skills un-bumped
    weak_answer = "idk honestly, this is broken and I can't do it."
    orchestrator.submit_solution(state, weak_answer)

    assert state.last_review is not None
    assert state.last_review.score < 60

    # Skills should not be increased
    assert state.skills == initial_skills

    # Ravi should have stepped in with a lesson and practice task
    assert state.active_lesson is not None
    assert len(state.active_lesson.resources) > 0

    # All resources MUST be valid and have title/url
    for res in state.active_lesson.resources:
        assert res.url.startswith("http")

    # Verify log contains handoff from Arjun to Ravi
    log_messages = [f"{l.source_agent} -> {l.target_agent}: {l.message}" for l in state.agent_logs]
    assert any("Arjun -> Ravi" in m for m in log_messages)


def test_strong_submission_raises_readiness(orchestrator, state):
    initial_readiness = state.readiness_history[-1]["readiness"]
    current_ticket = state.current_ticket

    # Acceptance Criterion 3: Submitting strong answer raises readiness
    strong_code = """
    // Fix Mobile Hamburger Nav Menu Toggle
    const hamburgerBtn = document.querySelector('.hamburger-btn');
    const navDrawer = document.querySelector('.nav-drawer');

    hamburgerBtn.addEventListener('click', () => {
        const isOpen = navDrawer.classList.toggle('is-open');
        hamburgerBtn.setAttribute('aria-expanded', String(isOpen));
    });
    """
    orchestrator.submit_solution(state, strong_code)

    assert state.last_review is not None
    assert state.last_review.score >= 70

    # Readiness must have increased
    new_readiness = state.readiness_history[-1]["readiness"]
    assert new_readiness > initial_readiness

    # Ticket completed
    assert current_ticket.id in state.completed_ticket_ids


def test_role_change_recomputes_gaps_and_tickets(orchestrator, state):
    # Acceptance Criterion 4: Switching role to Data Analyst regenerates gaps and tickets
    orchestrator.change_role(state, "data_analyst")

    assert state.current_role == "data_analyst"
    # Skills are preserved
    assert state.skills["Python"] == 2
    assert state.skills["SQL"] == 2

    # New readiness calculated for Data Analyst (4/12 -> 33.3%)
    assert state.readiness_history[-1]["readiness"] == 33.3

    # Current ticket must now belong to data_analyst
    assert state.current_ticket.role_id == "data_analyst"

    # Agent log tracks role change
    log_messages = [l.message for l in state.agent_logs]
    assert any("Role changed from Full Stack Developer to Data Analyst" in m for m in log_messages)

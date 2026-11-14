"""
Orchestrator for First Day AI career simulator.
Coordinates agent handoffs, logs all interactions, drives the learning loop,
and handles dynamic role transitions and demo student loading.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List

from state import (
    LearnerState,
    Ticket,
    SkillGapDetail,
    load_roles,
    load_tickets,
)
from scoring import (
    compute_readiness,
    update_skills_after_review,
    find_skill_gaps,
    is_passing_score,
)
from agents.maya_manager import assign_ticket
from agents.arjun_reviewer import review_submission
from agents.priya_recruiter import evaluate_readiness
from agents.ravi_coach import coach_gaps


class Orchestrator:
    def __init__(self):
        self.roles = load_roles()
        self.tickets = load_tickets()
        self._tickets_by_id = {t["id"]: Ticket.model_validate(t) for t in self.tickets}

    def get_role_targets(self, role_id: str) -> Dict[str, int]:
        role_info = self.roles.get(role_id, {})
        return role_info.get("required_skills", {})

    def get_role_title(self, role_id: str) -> str:
        role_info = self.roles.get(role_id, {})
        return role_info.get("title", role_id.replace("_", " ").title())

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        return self._tickets_by_id.get(ticket_id)

    def load_demo_student(self, state: LearnerState) -> None:
        """
        Initializes the demo student:
        - Skills: Python: 2, SQL: 2, HTML: 1
        - Goal: Full Stack Developer
        - Computes baseline readiness & verdict
        - Assigns first ticket via Maya
        """
        state.name = "Alex Rivera (Demo Student)"
        state.current_role = "full_stack_developer"
        state.skills = {"Python": 2, "SQL": 2, "HTML": 1}
        state.completed_ticket_ids = []
        state.last_review = None
        state.active_lesson = None

        targets = self.get_role_targets(state.current_role)
        role_title = self.get_role_title(state.current_role)
        readiness = compute_readiness(state.skills, targets)

        state.readiness_history = [{"step": "Onboarding", "readiness": readiness}]
        state.log_handoff("System", "Profiler", "Loaded demo student profile (Python: 2, SQL: 2, HTML: 1; Goal: Full Stack)")

        # Recruiter initial evaluation
        verdict = evaluate_readiness(state.skills, targets, role_title)
        state.last_recruiter_verdict = verdict
        state.log_handoff("Profiler", "Priya", f"Established baseline readiness: {readiness}%")

        # Maya assigns first ticket
        assignment = assign_ticket(
            current_role=state.current_role,
            current_skills=state.skills,
            target_skills=targets,
            completed_ticket_ids=state.completed_ticket_ids
        )
        ticket = self.get_ticket_by_id(assignment.ticket_id)
        if not ticket:
            ticket = self._tickets_by_id["FSD-101"]

        state.current_ticket = ticket
        state.log_handoff("Priya", "Maya", "Handoff to Engineering Manager for sprint ticket assignment")
        state.log_handoff("Maya", "Learner", f"Assigned ticket {ticket.id}: '{ticket.title}'")

    def submit_solution(self, state: LearnerState, submission_text: str) -> None:
        """
        Executes the solution submission pipeline:
        1. Learner -> Arjun (Review)
        2. Scoring engine updates skills
        3. Priya updates readiness
        4. If score < 60: Ravi coaches gaps -> Maya assigns remedial/foundational ticket
        5. If score >= 60: Advance -> Maya assigns next challenge
        """
        if not state.current_ticket:
            return

        current_ticket = state.current_ticket
        state.log_handoff("Learner", "Arjun", f"Submitted solution for {current_ticket.id} ({current_ticket.title})")

        # Step 1: Arjun reviews
        review_result = review_submission(current_ticket, submission_text)
        state.last_review = review_result

        # Step 2: Scoring engine updates skills
        updated_skills = update_skills_after_review(
            current_skills=state.skills,
            score=review_result.score,
            skills_demonstrated=review_result.skills_demonstrated
        )
        state.skills = updated_skills

        # Step 3: Priya updates readiness
        targets = self.get_role_targets(state.current_role)
        role_title = self.get_role_title(state.current_role)
        new_readiness = compute_readiness(state.skills, targets)
        verdict = evaluate_readiness(state.skills, targets, role_title)
        state.last_recruiter_verdict = verdict

        state.readiness_history.append({
            "step": current_ticket.id,
            "readiness": new_readiness
        })

        state.log_handoff(
            "Arjun",
            "Priya",
            f"Review completed with Score: {review_result.score}/100. Demonstrated: {review_result.skills_demonstrated or 'None'}"
        )
        state.log_handoff(
            "Priya",
            "Orchestrator",
            f"Readiness updated to {new_readiness}%: {verdict.verdict[:70]}..."
        )

        # Step 4: Branching on score
        if not is_passing_score(review_result.score, pass_threshold=60):
            # Score < 60: Intervene with Ravi and assign remedial ticket
            gaps = review_result.gaps
            if not gaps:
                fallback_skill = current_ticket.skills_tested[0] if current_ticket.skills_tested else "Core Concept"
                gaps = [SkillGapDetail(skill=fallback_skill, reason="Incomplete demonstration of acceptance criteria.")]

            gap_names = [g.skill for g in gaps]
            state.log_handoff("Arjun", "Ravi", f"Found gaps [{', '.join(gap_names)}]. Handing off for coaching.")

            lesson = coach_gaps(gaps)
            state.active_lesson = lesson
            state.log_handoff("Ravi", "Learner", f"Prepared coaching lesson: '{lesson.lesson_title}' with verified resources.")

            # Maya assigns an easier or targeted ticket on that skill
            assignment = assign_ticket(
                current_role=state.current_role,
                current_skills=state.skills,
                target_skills=targets,
                completed_ticket_ids=state.completed_ticket_ids,
                recommended_difficulty=1
            )
            next_ticket = self.get_ticket_by_id(assignment.ticket_id) or current_ticket
            state.current_ticket = next_ticket
            state.log_handoff("Ravi", "Maya", "Coaching complete. Requested targeted reinforcement ticket.")
            state.log_handoff("Maya", "Learner", f"Assigned practice ticket {next_ticket.id}: '{next_ticket.title}'")

        else:
            # Score >= 60: Advance!
            if current_ticket.id not in state.completed_ticket_ids:
                state.completed_ticket_ids.append(current_ticket.id)
            state.active_lesson = None

            state.log_handoff("Arjun", "Maya", f"Ticket {current_ticket.id} passed! Ready for next sprint ticket.")

            # Maya assigns next progression ticket
            assignment = assign_ticket(
                current_role=state.current_role,
                current_skills=state.skills,
                target_skills=targets,
                completed_ticket_ids=state.completed_ticket_ids
            )
            next_ticket = self.get_ticket_by_id(assignment.ticket_id)
            if not next_ticket:
                # If all completed, retain or loop
                next_ticket = current_ticket

            state.current_ticket = next_ticket
            state.log_handoff("Maya", "Learner", f"Assigned next challenge {next_ticket.id}: '{next_ticket.title}'")

    def change_role(self, state: LearnerState, new_role_id: str) -> None:
        """
        Dynamically adapts when learner switches their career goal:
        - Retains current skill levels
        - Recomputes gaps & readiness for the new role
        - Resets the active ticket queue
        - Maya assigns the new role's primary ticket
        - Logs: Orchestrator -> role changed
        """
        if new_role_id == state.current_role and state.current_ticket is not None:
            return

        old_role_title = self.get_role_title(state.current_role)
        state.current_role = new_role_id
        new_role_title = self.get_role_title(new_role_id)

        state.completed_ticket_ids = []
        state.active_lesson = None
        state.last_review = None

        targets = self.get_role_targets(new_role_id)
        new_readiness = compute_readiness(state.skills, targets)
        verdict = evaluate_readiness(state.skills, targets, new_role_title)
        state.last_recruiter_verdict = verdict

        state.readiness_history.append({
            "step": f"Switch: {new_role_title}",
            "readiness": new_readiness
        })

        state.log_handoff(
            "Orchestrator",
            "Maya",
            f"Role changed from {old_role_title} to {new_role_title}. Recomputed readiness: {new_readiness}%"
        )

        assignment = assign_ticket(
            current_role=new_role_id,
            current_skills=state.skills,
            target_skills=targets,
            completed_ticket_ids=[]
        )
        ticket = self.get_ticket_by_id(assignment.ticket_id)
        if not ticket:
            role_tickets = [t for t in self.tickets if t["role_id"] == new_role_id]
            ticket = Ticket.model_validate(role_tickets[0]) if role_tickets else None

        state.current_ticket = ticket
        if ticket:
            state.log_handoff("Maya", "Learner", f"Assigned initial ticket {ticket.id}: '{ticket.title}' for {new_role_title}")

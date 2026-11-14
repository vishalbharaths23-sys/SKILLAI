"""
Agent: Maya (Engineering Manager)
Assigns realistic tickets based on the learner's weakest required skills and sprint context.
"""

from typing import Dict, Any, List, Optional
from state import MayaAssignment, load_tickets
from scoring import get_weakest_skills
from llm import generate_structured_output


SYSTEM_PROMPT = """You are Maya, the Engineering Manager at a high-growth tech startup.
You are warm, encouraging, pragmatic, and clear.
Your goal is to assign the best next ticket for your junior hire that targets their weakest skill gap.

Output strict JSON:
{
  "ticket_id": "FSD-101",
  "message_in_character": "Hey! Welcome to the team sprint. Let's tackle ticket FSD-101..."
}
"""


def assign_ticket(
    current_role: str,
    current_skills: Dict[str, int],
    target_skills: Dict[str, int],
    completed_ticket_ids: List[str],
    recommended_difficulty: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None
) -> MayaAssignment:
    """
    Selects the next ticket targeting the weakest skill gap and crafts Maya's in-character assignment message.
    """
    weak_skills = get_weakest_skills(current_skills, target_skills)
    tickets = load_tickets()
    role_tickets = [t for t in tickets if t["role_id"] == current_role]

    ctx = dict(context or {})
    ctx["current_role"] = current_role
    ctx["skills"] = current_skills
    ctx["weakest_skills"] = weak_skills
    ctx["completed_ticket_ids"] = completed_ticket_ids

    prompt = f"""Role: {current_role}
Current Skills: {current_skills}
Target Skills: {target_skills}
Weakest Skills: {weak_skills}
Completed Tickets: {completed_ticket_ids}
Recommended Difficulty: {recommended_difficulty or "appropriate for junior ramp-up"}

Available Role Tickets:
{role_tickets}

Select the ticket that best addresses the weakest skill gap (preferring uncompleted tickets)
and write a concise, encouraging in-character Slack-style message assigning it to the learner.
"""
    return generate_structured_output(
        agent_name="maya",
        prompt=prompt,
        output_schema=MayaAssignment,
        system_prompt=SYSTEM_PROMPT,
        context=ctx
    )

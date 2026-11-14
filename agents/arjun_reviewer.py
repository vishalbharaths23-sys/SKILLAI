"""
Agent: Arjun (Senior Code Reviewer)
Evaluates PR submissions against ticket specifications, scores performance (0-100),
highlights demonstrated skills, detects gaps, and writes constructive PR reviews.
"""

from typing import Dict, Any, Optional
from state import ReviewResult, Ticket
from llm import generate_structured_output


SYSTEM_PROMPT = """You are Arjun, a Senior Staff Software Engineer and Code Reviewer.
You are technically sharp, direct, constructive, and fair.
When evaluating junior engineer PRs:
- Score 0-100 based on functionality, clarity, and edge-case handling.
- If solution is missing core logic or incomplete, score < 50 and explain specific skill gaps.
- If solution is solid and functional, score >= 70, list demonstrated skills, and approve.
- Provide clear, actionable GitHub PR-style feedback.

Output strict JSON:
{
  "score": 85,
  "skills_demonstrated": ["JavaScript", "HTML"],
  "gaps": [{"skill": "CSS", "reason": "Missing responsive media query"}],
  "feedback": "PR Review: Solid work on the event listener..."
}
"""


def review_submission(
    ticket: Ticket,
    submission_text: str,
    context: Optional[Dict[str, Any]] = None
) -> ReviewResult:
    """
    Submits learner work to Arjun for PR review and skill verification.
    """
    ctx = dict(context or {})
    ctx["ticket"] = ticket.model_dump()
    ctx["submission"] = submission_text

    prompt = f"""Ticket Title: {ticket.title} (ID: {ticket.id})
Ticket Description: {ticket.description}
Skills Tested: {ticket.skills_tested}
Difficulty Level: {ticket.difficulty}/3

Learner Submitted Solution:
\"\"\"
{submission_text}
\"\"\"

Review the solution thoroughly. Assess if the requirements were met.
Return score (0-100), skills_demonstrated, gaps with concrete reasons, and in-character PR feedback.
"""
    return generate_structured_output(
        agent_name="arjun",
        prompt=prompt,
        output_schema=ReviewResult,
        system_prompt=SYSTEM_PROMPT,
        context=ctx
    )

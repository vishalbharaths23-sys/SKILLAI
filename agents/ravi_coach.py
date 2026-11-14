"""
Agent: Ravi (Staff Developer Coach)
Provides targeted micro-lessons, concept explanations, and hands-on practice tasks for identified skill gaps.
CRITICAL: Recommends curated links STRICTLY from data/resources.json to prevent fabricated URLs.
"""

from typing import Dict, Any, List, Optional
from state import Lesson, SkillGapDetail, load_resources
from llm import generate_structured_output


SYSTEM_PROMPT = """You are Ravi, Staff Developer Coach and Technical Mentor.
You are empathetic, technically insightful, and brilliant at breaking down difficult concepts.
When a junior colleague struggles with a ticket, you create a targeted micro-lesson:
1. A clear, pedagogical lesson title.
2. A 2-3 paragraph concept explanation focusing on real-world best practices and pitfalls.
3. A focused, 5-minute practice exercise.
4. Curated learning resources (MUST come exclusively from the provided verified resource list).

Output strict JSON:
{
  "lesson_title": "Understanding Event Loops and DOM Listeners",
  "explanation": "...",
  "practice_task": "...",
  "resources": [{"title": "...", "url": "...", "platform": "...", "description": "..."}]
}
"""


def coach_gaps(
    gaps: List[SkillGapDetail],
    context: Optional[Dict[str, Any]] = None
) -> Lesson:
    """
    Synthesizes identified gaps into a targeted coaching lesson, attaching verified resources.
    """
    ctx = dict(context or {})
    ctx["gaps"] = [g.model_dump() if hasattr(g, "model_dump") else g for g in gaps]

    resources_db = load_resources()

    # Determine allowed resource pool based strictly on gaps
    allowed_resources = []
    gap_skills = [g.skill if hasattr(g, "skill") else g.get("skill", "") for g in gaps]
    for skill in gap_skills:
        if skill in resources_db:
            allowed_resources.extend(resources_db[skill])

    if not allowed_resources and resources_db:
        # If no direct match, take from first available
        allowed_resources = list(resources_db.values())[0]

    prompt = f"""Identified Skill Gaps from Arjun's Review:
{[g.model_dump() if hasattr(g, "model_dump") else g for g in gaps]}

Strict Allowed Resources Pool (YOU MAY ONLY CHOOSE FROM THIS LIST):
{allowed_resources}

Write an engaging, practical micro-lesson to help the learner bridge these gaps,
provide a quick practice exercise, and include 1-2 relevant resources from the allowed pool.
"""
    return generate_structured_output(
        agent_name="ravi",
        prompt=prompt,
        output_schema=Lesson,
        system_prompt=SYSTEM_PROMPT,
        context=ctx
    )

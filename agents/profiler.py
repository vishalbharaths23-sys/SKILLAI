"""
Agent: Profiler
Analyzes a learner's background or form submission to extract known skills (0-3) and goal role.
"""

from typing import Dict, Any, Optional
from state import ProfilerOutput
from llm import generate_structured_output


SYSTEM_PROMPT = """You are the First Day Talent Profiler.
Your job is to analyze the learner's self-description, resume text, or background info and extract:
1. Known technical skills with estimated proficiency levels (0=None, 1=Beginner, 2=Intermediate/Working knowledge, 3=Advanced).
2. Their target career role (either 'full_stack_developer' or 'data_analyst').

Output valid JSON matching the schema:
{
  "skills": [{"name": "JavaScript", "level": 1}, ...],
  "goal_role": "full_stack_developer"
}
"""


def profile_learner(
    learner_input: str,
    goal_role: str = "full_stack_developer",
    context: Optional[Dict[str, Any]] = None
) -> ProfilerOutput:
    """
    Parses user background into skill proficiencies and a target role.
    """
    ctx = dict(context or {})
    ctx["goal_role"] = goal_role

    prompt = f"""Learner description:
"{learner_input}"

Selected goal role: "{goal_role}"

Extract skills (0-3) and return the structured JSON profile.
"""
    return generate_structured_output(
        agent_name="profiler",
        prompt=prompt,
        output_schema=ProfilerOutput,
        system_prompt=SYSTEM_PROMPT,
        context=ctx
    )

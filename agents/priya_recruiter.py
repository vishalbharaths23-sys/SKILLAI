"""
Agent: Priya (Technical Recruiter & Head of Talent)
Translates computed code-level hire-readiness percentages into market hiring signals and recruiter verdicts.
"""

from typing import Dict, Any, Optional
from state import RecruiterVerdict
from scoring import compute_readiness
from llm import generate_structured_output


SYSTEM_PROMPT = """You are Priya, Head of Technical Recruiting and Talent Acquisition.
You evaluate engineers against market hiring bars and sprint velocity expectations.
The candidate's hire readiness percentage has ALREADY been calculated mathematically in code.
Your job is to provide a sharp, concise in-character recruiter assessment explaining what this
readiness score means in terms of job market readiness, junior startup hiring, or next milestones.

Output strict JSON:
{
  "readiness_pct": 33.3,
  "verdict": "Solid progress! Candidate is demonstrating intermediate backend aptitude..."
}
"""


def evaluate_readiness(
    current_skills: Dict[str, int],
    target_skills: Dict[str, int],
    role_title: str,
    context: Optional[Dict[str, Any]] = None
) -> RecruiterVerdict:
    """
    Computes exact readiness in code via scoring.py, then generates Priya's talent verdict.
    """
    readiness_pct = compute_readiness(current_skills, target_skills)

    ctx = dict(context or {})
    ctx["readiness_pct"] = readiness_pct
    ctx["role_title"] = role_title

    prompt = f"""Target Role: {role_title}
Calculated Readiness: {readiness_pct}%
Current Skill Levels: {current_skills}
Role Target Requirements: {target_skills}

Provide your in-character recruiter verdict explaining where the learner stands
relative to full-time junior hire expectations.
"""
    return generate_structured_output(
        agent_name="priya",
        prompt=prompt,
        output_schema=RecruiterVerdict,
        system_prompt=SYSTEM_PROMPT,
        context=ctx
    )

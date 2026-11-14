"""
Unified LLM Gateway and Deterministic Mock Engine for First Day career simulator.
Supports Gemini, Anthropic, or 100% offline Mock Mode.
Includes schema validation via Pydantic and one-retry recovery for malformed JSON.
"""

from __future__ import annotations
import os
import json
import re
from typing import Type, TypeVar, Optional, Dict, Any, List
from dotenv import load_dotenv
from pydantic import BaseModel
import requests

from state import (
    load_tickets,
    load_resources,
    ProfilerOutput,
    MayaAssignment,
    ReviewResult,
    RecruiterVerdict,
    Lesson,
    ResourceLink,
    SkillLevel,
    SkillGapDetail
)
from scoring import get_weakest_skills

load_dotenv()

T = TypeVar("T", bound=BaseModel)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()


def is_mock_mode() -> bool:
    """Returns True if mock mode is forced or if required keys are missing."""
    if LLM_PROVIDER == "mock":
        return True
    if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        return True
    if LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
        return True
    return False


def _extract_json_str(text: str) -> str:
    """Extracts raw JSON substring from LLM response (handling markdown fences)."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    # Try finding the first '{' and last '}'
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace:last_brace + 1].strip()
    return text


def _call_gemini_api(prompt: str, system_prompt: str = "") -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload: Dict[str, Any] = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }
    resp = requests.post(url, json=payload, timeout=25)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_anthropic_api(prompt: str, system_prompt: str = "") -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload: Dict[str, Any] = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1500,
        "temperature": 0.2,
        "system": system_prompt or "You are an AI career simulation agent. Output valid strict JSON only.",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]


def call_real_llm(prompt: str, system_prompt: str = "") -> str:
    """Invokes the active LLM provider (Gemini or Anthropic)."""
    if LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
        return _call_anthropic_api(prompt, system_prompt)
    elif GEMINI_API_KEY:
        return _call_gemini_api(prompt, system_prompt)
    raise RuntimeError("No valid LLM credentials available.")


def generate_structured_output(
    agent_name: str,
    prompt: str,
    output_schema: Type[T],
    system_prompt: str = "",
    context: Optional[Dict[str, Any]] = None
) -> T:
    """
    Primary interface for agents:
    Calls LLM or deterministic mock engine, verifies output against Pydantic schema,
    and retries once if JSON parsing fails.
    """
    if is_mock_mode():
        return _generate_mock_output(agent_name, prompt, output_schema, context)

    # Attempt real LLM generation
    for attempt in range(2):
        try:
            raw_text = call_real_llm(prompt, system_prompt)
            cleaned = _extract_json_str(raw_text)
            parsed_json = json.loads(cleaned)
            return output_schema.model_validate(parsed_json)
        except Exception:
            if attempt == 0:
                # Retry prompt with strict JSON formatting reminder
                prompt = (
                    f"{prompt}\n\nIMPORTANT: Your previous output was not valid JSON for the schema. "
                    f"Return ONLY raw valid JSON matching this schema: {output_schema.model_json_schema()}."
                )
            else:
                # Fallback to deterministic mock response so the demo never breaks
                return _generate_mock_output(agent_name, prompt, output_schema, context)

    return _generate_mock_output(agent_name, prompt, output_schema, context)


def _generate_mock_output(
    agent_name: str,
    prompt: str,
    output_schema: Type[T],
    context: Optional[Dict[str, Any]] = None
) -> T:
    """Deterministic, high-fidelity mock generator for all five agents."""
    ctx = context or {}

    if agent_name == "profiler":
        # Default mock profile for the demo student
        return output_schema.model_validate({
            "skills": [
                {"name": "Python", "level": 2},
                {"name": "SQL", "level": 2},
                {"name": "HTML", "level": 1}
            ],
            "goal_role": ctx.get("goal_role", "full_stack_developer")
        })

    elif agent_name == "maya":
        role_id = ctx.get("current_role", "full_stack_developer")
        current_skills = ctx.get("skills", {})
        tickets = load_tickets()
        role_tickets = [t for t in tickets if t["role_id"] == role_id]

        completed = set(ctx.get("completed_ticket_ids", []))
        available = [t for t in role_tickets if t["id"] not in completed]
        if not available:
            available = role_tickets

        # Preferred ticket targeting weakest skills
        weak_skills = ctx.get("weakest_skills", [])
        chosen_ticket = None
        for skill in weak_skills:
            for t in available:
                if skill in t["skills_tested"]:
                    chosen_ticket = t
                    break
            if chosen_ticket:
                break
        if not chosen_ticket:
            chosen_ticket = available[0]

        ticket_id = chosen_ticket["id"]
        messages = {
            "full_stack_developer": (
                f"Hey! Welcome to the sprint. Let's ramp you up on our stack. "
                f"I just assigned ticket {ticket_id} ('{chosen_ticket['title']}'). "
                f"This focuses on {', '.join(chosen_ticket['skills_tested'])}. "
                f"Take a look at the ACs and ping Arjun with your PR once you're ready!"
            ),
            "data_analyst": (
                f"Welcome aboard! The growth and finance teams have a few high-priority deliverables. "
                f"I've assigned ticket {ticket_id} ('{chosen_ticket['title']}') to you. "
                f"You'll be applying {', '.join(chosen_ticket['skills_tested'])}. Reach out if you need schema docs!"
            )
        }
        return output_schema.model_validate({
            "ticket_id": ticket_id,
            "message_in_character": messages.get(role_id, f"Ticket {ticket_id} assigned. Let me know if you need help!")
        })

    elif agent_name == "arjun":
        submission = ctx.get("submission", "").strip()
        ticket = ctx.get("ticket", {})
        skills_tested = ticket.get("skills_tested", ["Code"])

        # Determine if answer is weak (<45 chars or contains typical struggling phrases)
        is_weak = (
            len(submission) < 45 or
            any(phrase in submission.lower() for phrase in ["idk", "not sure", "help", "incomplete", "error", "cant", "can't"])
        )

        if is_weak:
            first_skill = skills_tested[0] if skills_tested else "General"
            return output_schema.model_validate({
                "score": 42,
                "skills_demonstrated": [],
                "gaps": [
                    {
                        "skill": first_skill,
                        "reason": f"Submission did not implement required {first_skill} logic or edge case handlers specified in the ticket."
                    }
                ],
                "feedback": (
                    f"Code Review (Request Changes): The submitted solution for '{ticket.get('title', 'Ticket')}' "
                    f"is missing core logic and error boundaries. I noticed gaps around {first_skill}. "
                    f"I'm looping in Ravi for a quick coaching micro-lesson so you can nail these concepts!"
                )
            })
        else:
            return output_schema.model_validate({
                "score": 88,
                "skills_demonstrated": skills_tested,
                "gaps": [],
                "feedback": (
                    f"Code Review (Approved): Excellent work on '{ticket.get('title', 'Ticket')}'! "
                    f"Your implementation cleanly handles {', '.join(skills_tested)}. "
                    f"The code structure is modular, readable, and satisfies all acceptance criteria. Great job!"
                )
            })

    elif agent_name == "priya":
        readiness_pct = float(ctx.get("readiness_pct", 0.0))
        role_name = ctx.get("role_title", "Target Role")
        if readiness_pct < 25.0:
            verdict = f"Early ramp-up phase for {role_name} (Readiness: {readiness_pct}%). Foundational skills established; needs hands-on sprint tickets to show breadth."
        elif readiness_pct < 55.0:
            verdict = f"Promising junior candidate for {role_name} (Readiness: {readiness_pct}%). Demonstrating key problem-solving patterns. On track for intern-to-junior transition."
        elif readiness_pct < 80.0:
            verdict = f"Strong Junior Engineer profile for {role_name} (Readiness: {readiness_pct}%). Demonstrates autonomy on typical team tickets and reliable code quality."
        else:
            verdict = f"High Hire-Readiness Signal for {role_name} (Readiness: {readiness_pct}%)! Fully qualified for full-time junior hire placement."

        return output_schema.model_validate({
            "readiness_pct": readiness_pct,
            "verdict": verdict
        })

    elif agent_name == "ravi":
        gaps = ctx.get("gaps", [])
        gap_skill = gaps[0]["skill"] if gaps else "Core Concept"
        resources_db = load_resources()

        # ONLY recommend curated resources from resources.json
        matched_resources = resources_db.get(gap_skill, [])
        if not matched_resources and resources_db:
            # Fallback to first available resource key if gap skill not found
            matched_resources = list(resources_db.values())[0]

        lesson_templates = {
            "JavaScript": {
                "title": "Mastering JavaScript Event Listeners and Async Callbacks",
                "explanation": (
                    "In modern web applications, UI interactivity relies heavily on the DOM Event Model. "
                    "Always ensure event handlers clean up references to avoid memory leaks. "
                    "When handling asynchronous actions or debounced inputs, use standard patterns like "
                    "setTimeout with a corresponding clearTimeout, or AbortController for fetch cancellations."
                ),
                "practice_task": (
                    "Write an event listener for a button that toggles an 'active' CSS class on a navigation element, "
                    "and logs the updated aria-expanded attribute state to the console."
                )
            },
            "React": {
                "title": "React useEffect Cleanup and Debouncing Patterns",
                "explanation": (
                    "React components frequently need to synchronize with external systems. "
                    "When an effect runs on dynamic state changes (such as keystroke search inputs), "
                    "returning a cleanup function prevents previous unmounted executions from setting stale state."
                ),
                "practice_task": (
                    "Create a custom hook `useDebounce(value, delay)` that returns the debounced value "
                    "after the specified millisecond delay, utilizing useEffect and cleanup."
                )
            },
            "HTML": {
                "title": "Semantic HTML and Accessible Mobile Navigation",
                "explanation": (
                    "Semantic tags like <nav>, <header>, and <button> provide built-in keyboard navigation "
                    "and screen reader accessibility. Always pair visual toggles with ARIA attributes such as "
                    "aria-expanded='true' and aria-controls='drawer-id'."
                ),
                "practice_task": (
                    "Structure a responsive navigation drawer with proper aria attributes, an SVG hamburger icon, "
                    "and keyboard ESC key dismissal."
                )
            },
            "CSS": {
                "title": "Responsive CSS Flexbox and Mobile Drawers",
                "explanation": (
                    "Flexbox simplifies 1D layout distribution. For mobile nav drawers, use transforms "
                    "(e.g., transform: translateX(-100%)) paired with smooth transitions for 60fps animations."
                ),
                "practice_task": (
                    "Write CSS classes for a slide-in sidebar that animates from off-screen left when 'is-active' is applied."
                )
            },
            "Node.js": {
                "title": "Production REST Routing and Parameterized SQL Queries",
                "explanation": (
                    "Never interpolate raw user input into SQL query strings. "
                    "Always use parameterized queries ($1, $2) to eliminate SQL injection vulnerabilities, "
                    "and sanitize pagination offsets."
                ),
                "practice_task": (
                    "Implement an Express route handler that parses req.query.page and req.query.limit with safe integer fallbacks."
                )
            },
            "SQL": {
                "title": "SQL Aggregations and Window Functions for Business Metrics",
                "explanation": (
                    "Calculating metrics like MRR or cohort retention requires grouping by date truncations "
                    "and conditional aggregations (SUM(CASE WHEN status = 'active' THEN amount ELSE 0 END))."
                ),
                "practice_task": (
                    "Write a query grouping subscription events by DATE_TRUNC('month', created_at) calculating active subscriber count."
                )
            },
            "Python": {
                "title": "Pandas Data Aggregation and Funnel Analysis",
                "explanation": (
                    "Efficient funnel analysis involves grouping sequential stages and computing conversion ratios. "
                    "Avoid looping over rows; use vectorized groupby and nunique methods for speed."
                ),
                "practice_task": (
                    "Given a DataFrame with columns ['user_id', 'stage'], calculate the percentage of users reaching each stage."
                )
            },
            "Statistics": {
                "title": "Two-Proportion Z-Testing and Statistical Significance",
                "explanation": (
                    "A/B testing evaluates if an observed difference between variant and control is statistically significant. "
                    "Calculate pooled proportions, standard error, z-statistic, and two-tailed p-value against an alpha of 0.05."
                ),
                "practice_task": (
                    "Calculate the 95% confidence interval for conversion difference between Control and Variant B."
                )
            },
            "Data Visualization": {
                "title": "Designing Intuitive Business Heatmaps and Funnel Charts",
                "explanation": (
                    "Effective data visualization highlights actionable patterns. In cohort retention heatmaps, "
                    "use diverging or sequential palettes (like YlGnBu) with formatted percentage annotations."
                ),
                "practice_task": (
                    "Create a seaborn heatmap annotating retention percentages across a 12-month cohort matrix."
                )
            }
        }

        template = lesson_templates.get(gap_skill, {
            "title": f"Core Foundations: {gap_skill} in Production",
            "explanation": f"Understanding {gap_skill} is essential for writing reliable production code. Focus on core architectural principles and error handling.",
            "practice_task": f"Build a minimal working example applying {gap_skill} to solve a real-world edge case."
        })

        return output_schema.model_validate({
            "lesson_title": template["title"],
            "explanation": template["explanation"],
            "practice_task": template["practice_task"],
            "resources": matched_resources
        })

    # Generic fallback
    return output_schema.model_validate({})

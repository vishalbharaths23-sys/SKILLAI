"""
Data models and state management for First Day career simulator.
Uses Pydantic v2 models for schema validation and integrity.
"""

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


DATA_DIR = Path(__file__).parent / "data"


class SkillLevel(BaseModel):
    name: str
    level: int = Field(ge=0, le=3)


class ProfilerOutput(BaseModel):
    skills: List[SkillLevel]
    goal_role: str


class Ticket(BaseModel):
    id: str
    role_id: str
    title: str
    description: str
    skills_tested: List[str]
    difficulty: int = Field(ge=1, le=3)
    hint: str


class MayaAssignment(BaseModel):
    ticket_id: str
    message_in_character: str


class SkillGapDetail(BaseModel):
    skill: str
    reason: str


class ReviewResult(BaseModel):
    score: int = Field(ge=0, le=100)
    skills_demonstrated: List[str] = Field(default_factory=list)
    gaps: List[SkillGapDetail] = Field(default_factory=list)
    feedback: str


class RecruiterVerdict(BaseModel):
    readiness_pct: float
    verdict: str


class ResourceLink(BaseModel):
    title: str
    url: str
    platform: str
    description: str


class Lesson(BaseModel):
    lesson_title: str
    explanation: str
    practice_task: str
    resources: List[ResourceLink] = Field(default_factory=list)


class AgentLogEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    source_agent: str
    target_agent: str
    message: str


class LearnerState(BaseModel):
    name: str = "Alex Rivera (Demo Student)"
    current_role: str = "full_stack_developer"
    skills: Dict[str, int] = Field(default_factory=dict)
    completed_ticket_ids: List[str] = Field(default_factory=list)
    current_ticket: Optional[Ticket] = None
    last_review: Optional[ReviewResult] = None
    active_lesson: Optional[Lesson] = None
    last_recruiter_verdict: Optional[RecruiterVerdict] = None
    readiness_history: List[Dict[str, Any]] = Field(default_factory=list)
    agent_logs: List[AgentLogEntry] = Field(default_factory=list)

    def log_handoff(self, source: str, target: str, message: str) -> None:
        self.agent_logs.insert(0, AgentLogEntry(
            source_agent=source,
            target_agent=target,
            message=message
        ))


# Cache loaders for JSON files
def load_roles() -> Dict[str, Any]:
    with open(DATA_DIR / "roles.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_tickets() -> List[Dict[str, Any]]:
    with open(DATA_DIR / "tickets.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_resources() -> Dict[str, List[Dict[str, str]]]:
    with open(DATA_DIR / "resources.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_default_demo_state() -> LearnerState:
    """
    Creates the default demo student profile according to the spec:
    Python: 2, SQL: 2, HTML: 1. Goal: Full Stack Developer.
    """
    state = LearnerState(
        name="Alex Rivera (Demo Student)",
        current_role="full_stack_developer",
        skills={"Python": 2, "SQL": 2, "HTML": 1},
        completed_ticket_ids=[],
        current_ticket=None,
        last_review=None,
        active_lesson=None,
        last_recruiter_verdict=None,
        readiness_history=[{"step": "Onboarding", "readiness": 18.8}],
        agent_logs=[]
    )
    state.log_handoff("Orchestrator", "System", "Loaded demo student profile (Python: 2, SQL: 2, HTML: 1)")
    return state

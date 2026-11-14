# 🚀 First Day — AI Career-Simulator Learning Platform

> **PromptWars X RTC Hackathon Project**  
> An adaptive, multi-agent AI career simulation platform where learners join a high-growth tech startup as a junior hire, complete real-world engineering tickets, receive code reviews, track hire readiness, and receive targeted coaching when struggling.

---

## 🌟 The Problem
Learners often don't know which specific skills they lack for a target job role. Traditional platforms give everyone static, cookie-cutter video courses and multiple-choice quizzes that fail to replicate authentic engineering environments.

## 💡 The Solution: "First Day"
In **First Day**, you join a simulated tech startup on your first day as a junior hire:
- **No multiple-choice quizzes**: Skill gaps are uncovered organically from your actual performance on sprint tickets and pull requests.
- **Simulated AI Engineering Team**: Multiple specialized AI colleagues collaborate to guide, evaluate, and coach you.
- **Dynamic Adaptation**: The platform recalculates readiness, re-orders roadmaps, and adjusts tickets immediately when you struggle or switch career goals.
- **Zero-Failure MOCK Mode**: Works 100% deterministically out of the box with zero API keys required, while seamlessly supporting live Gemini or Anthropic models.

---

## 👥 The Simulated AI Team

| Agent | Persona | Role & Behavior |
|---|---|---|
| **Profiler** | Talent Profiler | Analyzes learner background/resume and extracts baseline skills (0–3) and career goals. |
| **Maya** | Engineering Manager | Friendly, pragmatic lead. Identifies your weakest required skills and assigns realistic sprint tickets from `tickets.json`. |
| **Arjun** | Senior Staff Code Reviewer | Direct and constructive. Grades your PR submissions (0–100), verifies demonstrated skills, identifies gaps with technical rationale, and gives GitHub-style PR comments. |
| **Priya** | Head of Technical Recruiting | Evaluates code-computed hire-readiness percentages against market benchmarks (Ramp-up, Intern, Junior Ready, Strong Hire). |
| **Ravi** | Staff Developer Coach | Empathic mentor. When Arjun flags skill gaps (score < 60), Ravi steps in with a targeted micro-lesson, practice task, and links selected **strictly** from `resources.json` to eliminate hallucinations. |

---

## 🏗️ Architecture & Collaboration Flow

```text
               +-------------------------------------------+
               |           Learner / Demo Student          |
               +---------------------+---------------------+
                                     |
                                     v
                        +-------------------------+
                        |        Profiler         |
                        +------------+------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                         Orchestrator Loop                              |
|                                                                         |
|  1. Maya (Manager) assigns ticket targeting weakest skill gap           |
|  2. Learner implements solution and submits PR                          |
|  3. Arjun (Reviewer) evaluates PR -> outputs Score, Skills, Gaps        |
|  4. Scoring Engine updates demonstrated skills (>=70: +1 level)         |
|  5. Priya (Recruiter) updates readiness score & hiring verdict          |
|                                                                         |
|  [ Branching Condition ]:                                               |
|  * Score < 60:                                                          |
|      -> Arjun flags gaps -> Ravi crafts micro-lesson                    |
|      -> Maya assigns remedial practice ticket                           |
|  * Score >= 60:                                                         |
|      -> Ticket marked complete -> Maya assigns next challenge           |
|                                                                         |
|  [ Role Switch ]:                                                       |
|      -> Retains existing skills, recomputes gaps, resets queue,        |
|         Maya assigns new role tickets -> Logged in handoff feed         |
+-------------------------------------------------------------------------+
```

---

## 📐 Scoring & Roadmap Formulas (`scoring.py`)

- **Hire Readiness Percentage**:
  $$\text{readiness\_pct} = \frac{\sum \min(\text{level}_i, \text{target}_i)}{\sum \text{target}_i} \times 100.0$$
- **Review Progression Thresholds**:
  - `score >= 70`: Increments each demonstrated skill by $+1$ (max 3).
  - `score < 50`: Records gaps; does not raise levels.
  - `50 <= score < 70`: Requires further mastery; levels maintained.
  - `score < 60`: Triggers Ravi's coaching micro-lesson and Maya assigns an easier ticket.
- **Roadmap Ordering**:
  - Missing skills are sorted topologically by **Prerequisites Chain** (e.g., `HTML/CSS` $\rightarrow$ `JavaScript` $\rightarrow$ `React` $\rightarrow$ `Node.js`), then by **Gap Magnitude** (`target - current_level`).

---

## 📁 Repository Structure

```text
├── app.py                     # Streamlit frontend with interactive Workspace, Roadmap & Analytics
├── orchestrator.py            # Agent handoff pipeline, lifecycle dispatcher & event logger
├── state.py                   # Pydantic state models & data loader helpers
├── scoring.py                 # Pure scoring engine (no UI deps, 100% testable)
├── llm.py                     # Unified LLM wrapper (Gemini / Anthropic) with Deterministic MOCK mode
├── agents/
│   ├── profiler.py            # Profiler agent
│   ├── maya_manager.py        # Maya (Engineering Manager)
│   ├── arjun_reviewer.py      # Arjun (Senior Code Reviewer)
│   ├── priya_recruiter.py     # Priya (Technical Recruiter)
│   └── ravi_coach.py          # Ravi (Developer Coach)
├── data/
│   ├── roles.json             # 2 career paths (Full Stack Developer & Data Analyst)
│   ├── tickets.json           # Realistic engineering tickets (difficulty 1-3, hints, skills)
│   └── resources.json         # Curated, verified free links (MDN, freeCodeCamp, docs)
├── tests/
│   ├── test_scoring.py        # Pure unit tests for scoring, readiness & roadmap ordering
│   └── test_orchestrator.py   # Multi-agent handoff integration tests
├── requirements.txt           # Dependencies (Streamlit, Pydantic, Dotenv, Pytest)
├── .env.example               # Environment variables template
├── pytest.ini                 # Pytest configuration
└── README.md                  # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9+ (Python 3.11+ recommended)
- `pip` package manager

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone <repo-url>
cd antigravity

# Optional: Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)
Copy the example environment file:
```bash
cp .env.example .env
```
- **Mock Mode (Default)**: If you leave `GEMINI_API_KEY` or `ANTHROPIC_API_KEY` blank, the application automatically runs in **Deterministic MOCK Mode**. You do not need any API key to run a full live demo!
- **Live LLM Mode**: Set `LLM_PROVIDER=gemini` and add your `GEMINI_API_KEY`, or set `LLM_PROVIDER=anthropic` and add `ANTHROPIC_API_KEY`.

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Unit & Integration Tests

Run the full pytest suite:
```bash
pytest
```
*Output: 18 passed tests in < 2.5s (100% passing).*

---

## 🎮 Demo Walkthrough & Hackathon Criteria

1. **Load Demo Student**: Click the **⚡ Load Demo Student** button in the sidebar.
   - Initial skills set to: Python (Level 2), SQL (Level 2), HTML (Level 1).
   - Target Role: Full Stack Developer.
   - Identified Gaps: **JavaScript**, **React**, **Node.js**.
   - Initial Readiness: **18.8%** (`(1 + 2) / 16 * 100`).
2. **Demonstrate Poor Performance / Coaching Loop**:
   - In the Workspace tab, click **⚠️ Auto-fill Weak / Incomplete Code** and click **Submit to Arjun**.
   - Arjun assigns a score of 42 (< 60) and requests changes.
   - Readiness holds or reflects the struggling score.
   - **Ravi appears** with a focused micro-lesson, practice exercise, and verified learning links from `resources.json`.
   - Maya automatically assigns a foundational practice ticket.
   - Check the **Live Agent Activity Log** in the sidebar to observe: `Arjun -> found gaps [...] -> Ravi -> Maya`.
3. **Demonstrate Passing & Skill Progression**:
   - Click **🧪 Auto-fill Passing Code** and submit.
   - Arjun approves with a score of 88 (>= 70).
   - Demonstrated skills increment by +1.
   - Hire readiness advances dynamically.
   - Maya congratulates you and assigns the next sprint ticket.
4. **Demonstrate Dynamic Career Goal Switching**:
   - Change the **Target Career Role** in the sidebar to **Data Analyst**.
   - Existing skills (Python: 2, SQL: 2) are preserved.
   - Readiness immediately jumps to **33.3%** (`4 / 12 * 100`).
   - The ticket queue, roadmap, and analytics instantly adapt to Data Analyst competencies.
   - The agent log records: `Orchestrator -> role changed to Data Analyst -> Maya`.

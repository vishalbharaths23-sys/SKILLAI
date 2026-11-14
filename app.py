"""
First Day — AI Career-Simulator Learning Platform
Streamlit Application
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from typing import Dict, Any, List

from state import LearnerState, load_roles, load_resources
from scoring import (
    compute_readiness,
    find_skill_gaps,
    generate_roadmap,
)
from orchestrator import Orchestrator
from llm import is_mock_mode, LLM_PROVIDER


# Page configuration
st.set_page_config(
    page_title="First Day — AI Career Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    /* Metric styling */
    .readiness-container {
        background: linear-gradient(135deg, #1E1E2E 0%, #2A2A40 100%);
        border: 1px solid #3F3F5A;
        border-radius: 12px;
        padding: 16px;
        color: #FFFFFF;
        margin-bottom: 20px;
    }
    .readiness-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #10B981;
    }
    /* Agent card styling */
    .agent-card {
        background-color: #1a1c24;
        border: 1px solid #2d3139;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    .agent-name {
        font-weight: 700;
        font-size: 0.95rem;
    }
    .agent-role {
        font-size: 0.8rem;
        color: #9CA3AF;
    }
    .badge-maya { color: #A78BFA; }
    .badge-arjun { color: #60A5FA; }
    .badge-priya { color: #34D399; }
    .badge-ravi { color: #FBBF24; }
    
    /* Ticket card */
    .ticket-header {
        border-left: 4px solid #3B82F6;
        padding-left: 12px;
        margin-bottom: 15px;
    }
    .difficulty-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #2563EB;
        color: white;
    }
    .skill-chip {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        background-color: #374151;
        color: #E5E7EB;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    /* Log item */
    .log-entry {
        font-family: monospace;
        font-size: 0.82rem;
        padding: 6px 10px;
        border-radius: 6px;
        margin-bottom: 6px;
        background-color: #111827;
        border-left: 3px solid #4B5563;
        color: #D1D5DB;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Orchestrator and Session State
if "orchestrator" not in st.session_state:
    st.session_state["orchestrator"] = Orchestrator()

orchestrator: Orchestrator = st.session_state["orchestrator"]

if "learner_state" not in st.session_state:
    state = LearnerState()
    orchestrator.load_demo_student(state)
    st.session_state["learner_state"] = state

state: LearnerState = st.session_state["learner_state"]
roles_data = load_roles()
resources_data = load_resources()


# Starter code templates for demo testing
DEMO_STARTERS = {
    "FSD-101": """// Mobile Hamburger Nav Toggle Implementation
const hamburgerBtn = document.querySelector('.hamburger-btn');
const navDrawer = document.querySelector('.nav-drawer');

hamburgerBtn.addEventListener('click', () => {
    const isOpen = navDrawer.classList.toggle('is-open');
    hamburgerBtn.setAttribute('aria-expanded', String(isOpen));
});
""",
    "FSD-102": """// React Debounced Search Bar
import React, { useState, useEffect } from 'react';

export function SearchBar({ onSearch }) {
    const [query, setQuery] = useState('');

    useEffect(() => {
        const handler = setTimeout(() => {
            if (query.trim()) onSearch(query);
        }, 300);

        return () => clearTimeout(handler);
    }, [query, onSearch]);

    return (
        <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search items..."
        />
    );
}
""",
    "FSD-103": """// Node.js Express Paginated Users Handler
app.get('/api/v1/users', async (req, res) => {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.max(1, Math.min(50, parseInt(req.query.limit) || 10));
    const offset = (page - 1) * limit;

    const countRes = await db.query('SELECT COUNT(*) FROM users');
    const total = parseInt(countRes.rows[0].count);

    const usersRes = await db.query(
        'SELECT id, name, email, created_at FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2',
        [limit, offset]
    );

    res.json({
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
        data: usersRes.rows
    });
});
""",
    "FSD-104": """// Async Race Condition Fix with AbortController
useEffect(() => {
    const controller = new AbortController();

    async function loadData() {
        try {
            setLoading(true);
            const res = await fetch(`/api/feed?tab=${activeTab}`, { signal: controller.signal });
            const data = await res.json();
            setFeed(data);
        } catch (err) {
            if (err.name !== 'AbortError') setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    loadData();
    return () => controller.abort();
}, [activeTab]);
""",
    "DAT-101": """-- SQL Monthly MRR and Churn Calculation
SELECT
    DATE_TRUNC('month', event_date) AS month,
    SUM(CASE WHEN event_type = 'new' THEN amount ELSE 0 END) AS new_mrr,
    SUM(CASE WHEN event_type = 'churn' THEN amount ELSE 0 END) AS churned_mrr,
    (COUNT(DISTINCT CASE WHEN event_type = 'churn' THEN user_id END)::FLOAT /
     NULLIF(COUNT(DISTINCT user_id), 0)) * 100 AS churn_rate_pct
FROM subscriptions
GROUP BY 1
ORDER BY 1;
""",
    "DAT-102": """# Funnel Drop-off Analysis with pandas
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('funnel_events.csv')
funnel = df.groupby('stage')['user_id'].nunique().reindex(
    ['Landed', 'Signed Up', 'Completed Profile', 'First Action']
)

conversion = (funnel / funnel.iloc[0]) * 100
print(conversion)

plt.figure(figsize=(8, 4))
bars = plt.bar(conversion.index, conversion.values, color='#3B82F6')
plt.ylabel('Conversion %')
plt.title('Onboarding Funnel Conversion')
plt.tight_layout()
plt.show()
""",
    "DAT-103": """# A/B Test Two-Proportion Z-Test
import numpy as np
from scipy.stats import norm

n_a, x_a = 12500, 1125
n_b, x_b = 12450, 1290

p_a = x_a / n_a
p_b = x_b / n_b
p_pool = (x_a + x_b) / (n_a + n_b)

se = np.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b))
z = (p_b - p_a) / se
p_value = 2 * (1 - norm.cdf(abs(z)))

print(f"Variant A: {p_a:.2%}, Variant B: {p_b:.2%}")
print(f"Z-score: {z:.3f}, P-value: {p_value:.4f}")
print("Statistically significant at alpha=0.05!" if p_value < 0.05 else "Not significant")
""",
    "DAT-104": """# Retention Cohort Matrix Heatmap
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df['order_month'] = df['order_date'].dt.to_period('M')
df['cohort'] = df.groupby('user_id')['order_date'].transform('min').dt.to_period('M')

cohort_group = df.groupby(['cohort', 'order_month'])['user_id'].nunique().reset_index()
cohort_group['period_number'] = (cohort_group['order_month'] - cohort_group['cohort']).apply(lambda x: x.n)

cohort_pivot = cohort_group.pivot(index='cohort', columns='period_number', values='user_id')
cohort_size = cohort_pivot.iloc[:, 0]
retention = cohort_pivot.divide(cohort_size, axis=0)

plt.figure(figsize=(12, 6))
sns.heatmap(retention, annot=True, fmt='.1%', cmap='YlGnBu')
plt.title('Monthly User Retention Cohorts')
plt.show()
"""
}


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.title("🚀 First Day")
    st.caption("AI Career-Simulator Learning Platform")

    # Mode Indicator
    mock_status = is_mock_mode()
    if mock_status:
        st.info("⚙️ **Engine Mode:** Deterministic MOCK (Zero API Key needed)", icon="💡")
    else:
        st.success(f"🌐 **Engine Mode:** Live {LLM_PROVIDER.upper()} LLM", icon="⚡")

    st.markdown("---")

    # Role Selector (triggers dynamic re-plan)
    role_options = {
        "full_stack_developer": "Full Stack Developer",
        "data_analyst": "Data Analyst"
    }
    selected_role_key = st.selectbox(
        "🎯 **Target Career Role**",
        options=list(role_options.keys()),
        format_func=lambda k: role_options[k],
        index=0 if state.current_role == "full_stack_developer" else 1,
        help="Changing role triggers an automated re-plan, recomputes gaps, and assigns new tickets."
    )

    if selected_role_key != state.current_role:
        orchestrator.change_role(state, selected_role_key)
        st.rerun()

    # Load Demo Student Preset Button
    if st.button("⚡ Load Demo Student", use_container_width=True, type="primary"):
        orchestrator.load_demo_student(state)
        st.success("Loaded demo student profile (Python: 2, SQL: 2, HTML: 1)!")
        st.rerun()

    st.markdown("---")

    # Hire Readiness Meter
    targets = orchestrator.get_role_targets(state.current_role)
    current_readiness = compute_readiness(state.skills, targets)

    st.markdown("### 📊 Hire Readiness")
    st.progress(current_readiness / 100.0)
    col_pct, col_stage = st.columns([1, 1.2])
    with col_pct:
        st.markdown(f"<div class='readiness-val'>{current_readiness}%</div>", unsafe_allow_html=True)
    with col_stage:
        if current_readiness < 25.0:
            stage_txt = "🌱 Ramp-up"
        elif current_readiness < 55.0:
            stage_txt = "💼 Intern Ready"
        elif current_readiness < 80.0:
            stage_txt = "🚀 Junior Ready"
        else:
            stage_txt = "⭐ Strong Hire"
        st.caption(f"**Stage:** {stage_txt}")
        st.caption(f"Role: {role_options[state.current_role]}")

    st.markdown("---")

    # Team Panel (AI Colleagues)
    st.markdown("### 👥 Simulated Team")

    agents_info = [
        {"name": "Maya", "role": "Engineering Manager", "badge": "badge-maya", "status": "🟢 Assigning sprint tickets"},
        {"name": "Arjun", "role": "Senior Staff Reviewer", "badge": "badge-arjun", "status": "🟢 Reviewing incoming PRs"},
        {"name": "Priya", "role": "Head of Technical Talent", "badge": "badge-priya", "status": "🟢 Evaluating market readiness"},
        {"name": "Ravi", "role": "Staff Developer Coach", "badge": "badge-ravi", "status": "🟡 Micro-lesson standby"}
    ]

    for ag in agents_info:
        st.markdown(f"""
        <div class="agent-card">
            <div class="agent-name {ag['badge']}">{ag['name']}</div>
            <div class="agent-role">{ag['role']}</div>
            <div style="font-size:0.75rem; color:#10B981; margin-top:2px;">{ag['status']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Live Agent Activity Log
    st.markdown("### 📡 Live Agent Activity Log")
    if state.agent_logs:
        log_container = st.container(height=240)
        with log_container:
            for entry in state.agent_logs:
                st.markdown(f"""
                <div class="log-entry">
                    <span style="color:#9CA3AF;">[{entry.timestamp}]</span>
                    <strong style="color:#60A5FA;">{entry.source_agent}</strong> &rarr;
                    <strong style="color:#34D399;">{entry.target_agent}</strong><br>
                    <span>{entry.message}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("No agent activity yet.")


# ==============================================================================
# MAIN TABS
# ==============================================================================
tab_workspace, tab_roadmap, tab_progress = st.tabs([
    "💻 Team Workspace",
    "🗺️ Career Roadmap",
    "📈 Hire Readiness & Analytics"
])


# ------------------------------------------------------------------------------
# TAB 1: TEAM WORKSPACE
# ------------------------------------------------------------------------------
with tab_workspace:
    # Role & Sprint Header
    role_meta = roles_data.get(state.current_role, {})
    st.subheader(f"Sprint Workspace — {role_meta.get('title', 'Target Role')}")
    st.write(role_meta.get("description", ""))

    ticket = state.current_ticket
    if not ticket:
        st.warning("No ticket currently assigned. Click 'Load Demo Student' in the sidebar to get started.")
    else:
        # Ticket Card
        st.markdown(f"""
        <div class="ticket-header">
            <span class="difficulty-badge">Difficulty: Level {ticket.difficulty}/3</span>
            <h3 style="margin: 6px 0 4px 0;">{ticket.id}: {ticket.title}</h3>
            <div style="margin-bottom: 8px;">
                {' '.join([f'<span class="skill-chip">{s}</span>' for s in ticket.skills_tested])}
            </div>
            <p style="font-size: 1rem; color: #D1D5DB; line-height: 1.5;">{ticket.description}</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("💡 Need a hint from Maya? (Click to expand)"):
            st.info(ticket.hint)

        st.markdown("---")

        # Submission Area
        st.markdown("#### 📝 Submit Your Pull Request / Solution")
        st.caption(f"Arjun will perform a full code review on your solution against {', '.join(ticket.skills_tested)}.")

        default_starter = DEMO_STARTERS.get(ticket.id, "// Write your solution code here...\n")

        # Demo Helper Quick Buttons
        col_btn1, col_btn2, _ = st.columns([1.2, 1.4, 2])
        with col_btn1:
            if st.button("🧪 Auto-fill Passing Code", help="Fills in a robust solution to demo Arjun approving and skill leveling"):
                st.session_state["code_input_field"] = default_starter
        with col_btn2:
            if st.button("⚠️ Auto-fill Weak / Incomplete Code", help="Fills in a weak submission to demo Arjun flagging gaps and Ravi stepping in"):
                st.session_state["code_input_field"] = "// Incomplete attempt\n// idk how to handle the events or state properly yet"

        code_input = st.text_area(
            "Solution Code / PR Implementation:",
            value=st.session_state.get("code_input_field", default_starter),
            height=200,
            key="code_area"
        )

        if st.button("🚀 Submit to Arjun for Code Review", type="primary", use_container_width=True):
            if not code_input.strip():
                st.error("Please enter code or an explanation before submitting.")
            else:
                with st.spinner("Arjun is reviewing your pull request..."):
                    orchestrator.submit_solution(state, code_input)
                st.rerun()

        # Review & Coaching Drawers
        if state.last_review:
            st.markdown("---")
            rev = state.last_review
            score_color = "#10B981" if rev.score >= 70 else ("#F59E0B" if rev.score >= 50 else "#EF4444")
            verdict_badge = "✅ APPROVED" if rev.score >= 70 else ("⚠️ REVISIONS REQUESTED" if rev.score >= 50 else "❌ CHANGES REQUESTED")

            st.markdown(f"""
            <div style="background-color: #1a1e29; border: 1px solid #374151; border-radius: 8px; padding: 18px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #60A5FA;">👨‍💻 Arjun's Code Review</h4>
                    <span style="font-weight: 800; color: {score_color}; font-size: 1.1rem;">{verdict_badge} ({rev.score}/100)</span>
                </div>
                <div style="margin-top: 10px; font-size: 0.95rem; line-height: 1.5; color: #E5E7EB;">
                    {rev.feedback}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if rev.skills_demonstrated:
                st.markdown(f"**Skills Successfully Demonstrated:** {', '.join([f'`{s}`' for s in rev.skills_demonstrated])}")

            if rev.gaps:
                st.markdown("**Identified Gaps:**")
                for g in rev.gaps:
                    st.warning(f"**{g.skill}**: {g.reason}")

        # Active Lesson from Ravi (if score < 60)
        if state.active_lesson:
            lesson = state.active_lesson
            st.markdown("---")
            st.markdown(f"""
            <div style="background-color: #241D13; border: 1px solid #78350F; border-radius: 8px; padding: 18px; margin-top: 15px;">
                <h4 style="margin: 0; color: #FBBF24;">🧑‍🏫 Ravi's Coaching Micro-Lesson: {lesson.lesson_title}</h4>
                <div style="margin-top: 10px; font-size: 0.95rem; line-height: 1.6; color: #FDE68A;">
                    {lesson.explanation}
                </div>
                <div style="background-color: #1c150c; padding: 12px; border-radius: 6px; margin-top: 12px; border-left: 3px solid #F59E0B;">
                    <strong>🎯 Mini Practice Exercise:</strong><br>
                    {lesson.practice_task}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### 📚 Recommended Verified Learning Resources (Curated)")
            for res in lesson.resources:
                col_link, col_plat = st.columns([3, 1])
                with col_link:
                    st.markdown(f"🔗 [{res.title}]({res.url}) — *{res.description}*")
                with col_plat:
                    st.caption(f"Platform: `{res.platform}`")


# ------------------------------------------------------------------------------
# TAB 2: CAREER ROADMAP
# ------------------------------------------------------------------------------
with tab_roadmap:
    st.subheader(f"🗺️ Personalized Career Roadmap — {role_options[state.current_role]}")
    st.caption("Missing skills are ordered by prerequisites first, then by gap magnitude. Focus on upstream skills first!")

    target_skills = orchestrator.get_role_targets(state.current_role)
    prereqs = role_meta.get("prerequisites_order", list(target_skills.keys()))
    roadmap_items = generate_roadmap(state.skills, target_skills, prereqs)

    if not roadmap_items:
        st.balloons()
        st.success("🎉 Incredible! You have met all target skill levels for this role. You are hire-ready!")
    else:
        for idx, item in enumerate(roadmap_items, 1):
            skill = item["skill"]
            curr = item["current_level"]
            tgt = item["target_level"]
            gap = item["gap"]

            pct = (curr / tgt) * 100 if tgt > 0 else 100
            dots = "●" * curr + "○" * (tgt - curr)

            with st.container():
                st.markdown(f"""
                <div style="background: #181920; border: 1px solid #2B2D38; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF;">
                            Step {idx}: {skill} <span style="font-size:0.85rem; color:#9CA3AF;">({dots} Level {curr} / {tgt})</span>
                        </span>
                        <span style="background: #EF4444; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 600;">
                            Gap: -{gap} Level{'s' if gap > 1 else ''}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.progress(pct / 100.0)

                # Verified resources for this gap
                skill_resources = resources_data.get(skill, [])
                if skill_resources:
                    with st.expander(f"📖 Curated free resources for {skill}"):
                        for r in skill_resources:
                            st.markdown(f"- 🔗 [{r['title']}]({r['url']}) (`{r['platform']}`) — {r['description']}")


# ------------------------------------------------------------------------------
# TAB 3: HIRE READINESS & ANALYTICS
# ------------------------------------------------------------------------------
with tab_progress:
    st.subheader("📈 Hire Readiness & Skill Analytics")

    # Priya's Recruiter Assessment Card
    if state.last_recruiter_verdict:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #064E3B 0%, #065F46 100%); border: 1px solid #059669; border-radius: 10px; padding: 16px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.3rem;">👩‍💼</span>
                <h4 style="margin: 0; color: #A7F3D0;">Priya's Talent & Market Verdict</h4>
            </div>
            <p style="margin-top: 8px; font-size: 1rem; color: #ECFDF5; line-height: 1.5;">
                {state.last_recruiter_verdict.verdict}
            </p>
        </div>
        """, unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)

    # Chart 1: Readiness Progression Over Time
    with col_chart1:
        st.markdown("#### 📉 Readiness Progression History")
        if state.readiness_history:
            df_hist = pd.DataFrame(state.readiness_history)
            df_hist["Index"] = range(1, len(df_hist) + 1)
            st.line_chart(
                df_hist,
                x="step",
                y="readiness",
                use_container_width=True
            )
        else:
            st.caption("No history yet.")

    # Chart 2: Skill Levels vs Target Levels
    with col_chart2:
        st.markdown(f"#### 📊 Skill Comparison ({role_options[state.current_role]})")
        target_skills = orchestrator.get_role_targets(state.current_role)
        chart_data = []
        for s, tgt in target_skills.items():
            chart_data.append({
                "Skill": s,
                "Current Level": state.skills.get(s, 0),
                "Target Level": tgt
            })
        df_skills = pd.DataFrame(chart_data)
        st.bar_chart(
            df_skills.set_index("Skill"),
            use_container_width=True
        )

    # Completed Tickets summary
    st.markdown("---")
    st.markdown("#### 🏆 Completed Engineering Tickets")
    if state.completed_ticket_ids:
        for tid in state.completed_ticket_ids:
            tk = orchestrator.get_ticket_by_id(tid)
            if tk:
                st.success(f"✔ **{tk.id}**: {tk.title} (Difficulty: {tk.difficulty}/3 | Tested: {', '.join(tk.skills_tested)})")
    else:
        st.info("No tickets completed yet. Submit your first ticket in the Workspace tab!")

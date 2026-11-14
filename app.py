"""
First Day — AI Career-Simulator Learning Platform
Executive Professional Dark-Theme UI
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
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling: High-End Linear / Vercel Dark Executive Palette
st.markdown("""
<style>
    /* Global Fonts & Reset */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #F3F4F6;
    }

    /* Executive Top Brand Bar */
    .top-header-banner {
        background: linear-gradient(90deg, #111827 0%, #1E1B4B 50%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px -4px rgba(0, 0, 0, 0.4);
    }
    .brand-title {
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #FFFFFF 0%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .brand-sub {
        font-size: 0.85rem;
        color: #94A3B8;
        margin-top: 3px;
    }
    .status-pill-live {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34D399;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B0F17;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }
    
    /* Readiness Card */
    .readiness-executive-card {
        background: linear-gradient(145deg, #0F172A 0%, #1E1B4B 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.6);
    }
    .readiness-metric-big {
        font-size: 2.6rem;
        font-weight: 800;
        color: #38BDF8;
        letter-spacing: -0.03em;
        line-height: 1;
    }
    .benchmark-track {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        font-size: 0.72rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .benchmark-track .active-stage {
        color: #38BDF8;
    }

    /* AI Colleague Cards */
    .agent-roster-card {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .agent-roster-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
    }
    .avatar-circle {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .avatar-maya { background: #5B21B6; color: #DDD6FE; border: 1px solid #7C3AED; }
    .avatar-arjun { background: #1E3A8A; color: #BFDBFE; border: 1px solid #2563EB; }
    .avatar-priya { background: #064E3B; color: #A7F3D0; border: 1px solid #059669; }
    .avatar-ravi { background: #78350F; color: #FDE68A; border: 1px solid #D97706; }

    .agent-meta-name {
        font-weight: 600;
        font-size: 0.9rem;
        color: #F8FAFC;
    }
    .agent-meta-role {
        font-size: 0.75rem;
        color: #94A3B8;
    }
    .agent-meta-status {
        font-size: 0.7rem;
        color: #10B981;
        font-weight: 500;
    }

    /* Ticket Card Styling */
    .ticket-executive-card {
        background: #0F172A;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        position: relative;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .ticket-meta-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }
    .ticket-id-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #A5B4FC;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .difficulty-tag {
        font-size: 0.75rem;
        font-weight: 600;
        background: #1E293B;
        color: #E2E8F0;
        padding: 3px 10px;
        border-radius: 20px;
        border: 1px solid #334155;
    }
    .skill-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        background: #1E293B;
        color: #94A3B8;
        border: 1px solid #334155;
        margin-right: 6px;
    }

    /* PR Review Card */
    .pr-review-container {
        background: #0B1120;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 20px;
        margin-top: 18px;
    }
    .review-status-pass {
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .review-status-fail {
        background: rgba(239, 68, 68, 0.12);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    /* Coaching Lesson Card */
    .coaching-card {
        background: linear-gradient(135deg, #1C1917 0%, #292524 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 22px;
        margin-top: 18px;
    }
    .practice-code-box {
        background: #0C0A09;
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-left: 4px solid #F59E0B;
        border-radius: 6px;
        padding: 14px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #FEF3C7;
        margin-top: 12px;
    }

    /* Roadmap Timeline */
    .roadmap-node {
        background: #0F172A;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .roadmap-step-badge {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #1E293B;
        color: #94A3B8;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 12px;
    }

    /* Log Feed */
    .agent-log-feed {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        background-color: #0A0D14;
        border-left: 3px solid #3B82F6;
        color: #CBD5E1;
        line-height: 1.45;
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
    "FSD-101": """// Fix Mobile Hamburger Nav Menu Toggle
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

plt.figure(figsize=(8, 4))
plt.bar(conversion.index, conversion.values, color='#38BDF8')
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
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
        <span style="font-size: 1.5rem;">⚡</span>
        <span style="font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em;">FIRST DAY</span>
    </div>
    <div style="font-size: 0.78rem; color: #94A3B8; margin-bottom: 16px;">
        AI Career Simulator • PromptWars X RTC
    </div>
    """, unsafe_allow_html=True)

    # Engine Status Pill
    mock_status = is_mock_mode()
    if mock_status:
        st.markdown("""
        <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 8px; padding: 6px 12px; font-size: 0.76rem; color: #A5B4FC; margin-bottom: 16px;">
            ⚡ <strong>Engine:</strong> Deterministic MOCK Mode
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 6px 12px; font-size: 0.76rem; color: #34D399; margin-bottom: 16px;">
            🌐 <strong>Engine:</strong> Live {LLM_PROVIDER.upper()}
        </div>
        """, unsafe_allow_html=True)

    # Role Selector (triggers dynamic re-plan)
    role_options = {
        "full_stack_developer": "Full Stack Developer",
        "data_analyst": "Data Analyst"
    }
    selected_role_key = st.selectbox(
        "Target Career Goal",
        options=list(role_options.keys()),
        format_func=lambda k: role_options[k],
        index=0 if state.current_role == "full_stack_developer" else 1,
        help="Changing role triggers an automated re-plan, recomputes gaps, and re-assigns tickets."
    )

    if selected_role_key != state.current_role:
        orchestrator.change_role(state, selected_role_key)
        st.rerun()

    # Load Demo Student Action Button
    if st.button("⚡ Load Demo Student", use_container_width=True, type="primary"):
        orchestrator.load_demo_student(state)
        st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Hire Readiness Meter Card
    targets = orchestrator.get_role_targets(state.current_role)
    current_readiness = compute_readiness(state.skills, targets)

    if current_readiness < 25.0:
        stage_name = "Ramp-up"
    elif current_readiness < 55.0:
        stage_name = "Intern Ready"
    elif current_readiness < 80.0:
        stage_name = "Junior Ready"
    else:
        stage_name = "Strong Hire"

    st.markdown(f"""
    <div class="readiness-executive-card">
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <span style="font-size: 0.8rem; font-weight: 600; color: #94A3B8; text-transform: uppercase;">Hire Readiness</span>
            <span style="font-size: 0.75rem; color: #38BDF8; font-weight: 600;">{stage_name}</span>
        </div>
        <div class="readiness-metric-big">{current_readiness}%</div>
        <div class="benchmark-track">
            <span class="{'active-stage' if current_readiness < 25 else ''}">Ramp</span>
            <span class="{'active-stage' if 25 <= current_readiness < 55 else ''}">Intern</span>
            <span class="{'active-stage' if 55 <= current_readiness < 80 else ''}">Junior</span>
            <span class="{'active-stage' if current_readiness >= 80 else ''}">Hire</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(current_readiness / 100.0)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Team Panel (AI Colleagues)
    st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#94A3B8; text-transform:uppercase; margin-bottom:10px;'>Simulated Engineering Team</div>", unsafe_allow_html=True)

    agents_roster = [
        {"name": "Maya", "initials": "MY", "role": "Engineering Manager", "avatar_class": "avatar-maya", "status": "Assigning tickets"},
        {"name": "Arjun", "initials": "AR", "role": "Senior Reviewer", "avatar_class": "avatar-arjun", "status": "Reviewing PRs"},
        {"name": "Priya", "initials": "PR", "role": "Head of Talent", "avatar_class": "avatar-priya", "status": "Tracking benchmarks"},
        {"name": "Ravi", "initials": "RV", "role": "Developer Coach", "avatar_class": "avatar-ravi", "status": "Ready to coach"}
    ]

    for ag in agents_roster:
        st.markdown(f"""
        <div class="agent-roster-card">
            <div class="avatar-circle {ag['avatar_class']}">{ag['initials']}</div>
            <div>
                <div class="agent-meta-name">{ag['name']}</div>
                <div class="agent-meta-role">{ag['role']} • <span class="agent-meta-status">{ag['status']}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Live Agent Activity Log
    st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#94A3B8; text-transform:uppercase; margin-bottom:10px;'>Agent Dispatch Feed</div>", unsafe_allow_html=True)
    if state.agent_logs:
        log_container = st.container(height=220)
        with log_container:
            for entry in state.agent_logs:
                st.markdown(f"""
                <div class="agent-log-feed">
                    <span style="color:#64748B;">[{entry.timestamp}]</span>
                    <strong style="color:#818CF8;">{entry.source_agent}</strong> &rarr;
                    <strong style="color:#34D399;">{entry.target_agent}</strong><br>
                    <span>{entry.message}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("No agent activity yet.")


# ==============================================================================
# MAIN VIEWPORT
# ==============================================================================

# Executive Top Banner
role_meta = roles_data.get(state.current_role, {})
st.markdown(f"""
<div class="top-header-banner">
    <div>
        <h1 class="brand-title">First Day // CloudScale AI Labs</h1>
        <div class="brand-sub">Simulated Sprint • Role: <strong>{role_meta.get('title', 'Target Role')}</strong> • Candidate: <strong>{state.name}</strong></div>
    </div>
    <div>
        <span class="status-pill-live">● Sprint Active</span>
    </div>
</div>
""", unsafe_allow_html=True)


# Tabs
tab_workspace, tab_roadmap, tab_progress = st.tabs([
    "💻 Sprint Workspace",
    "🗺️ Interactive Roadmap",
    "📈 Hire Readiness & Analytics"
])


# ------------------------------------------------------------------------------
# TAB 1: SPRINT WORKSPACE
# ------------------------------------------------------------------------------
with tab_workspace:
    ticket = state.current_ticket
    if not ticket:
        st.info("No active ticket assigned. Click '⚡ Load Demo Student' in the sidebar.")
    else:
        # Ticket Header Card
        difficulty_stars = "★" * ticket.difficulty + "☆" * (3 - ticket.difficulty)
        skills_chips = " ".join([f"<span class='skill-pill'>{s}</span>" for s in ticket.skills_tested])

        st.markdown(f"""
        <div class="ticket-executive-card">
            <div class="ticket-meta-bar">
                <span class="ticket-id-tag">{ticket.id}</span>
                <span class="difficulty-tag">Difficulty Level {ticket.difficulty}/3 ({difficulty_stars})</span>
            </div>
            <h2 style="margin: 0 0 10px 0; font-size: 1.35rem; font-weight: 700; color: #FFFFFF;">
                {ticket.title}
            </h2>
            <div style="margin-bottom: 14px;">
                {skills_chips}
            </div>
            <div style="font-size: 0.96rem; color: #CBD5E1; line-height: 1.6; border-left: 2px solid #3B82F6; padding-left: 14px;">
                {ticket.description}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("💡 Maya's Architecture Guidance & Hints (Click to View)"):
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border-radius: 8px; padding: 12px 16px; border-left: 3px solid #8B5CF6; color: #DDD6FE; font-size: 0.92rem;">
                <strong>Maya's Tip:</strong> {ticket.hint}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Pull Request Submission Console
        st.markdown("### 🛠️ Pull Request Implementation Console")
        st.caption(f"Implement your solution below. Arjun will evaluate code quality, edge cases, and required competencies ({', '.join(ticket.skills_tested)}).")

        default_starter = DEMO_STARTERS.get(ticket.id, "// Implement your solution here...\n")

        # Quick action demo buttons
        col_btn1, col_btn2, _ = st.columns([1.3, 1.4, 2])
        with col_btn1:
            if st.button("🧪 Inject Passing Solution", help="Injects a production-ready solution to demo Arjun approving and skill leveling"):
                st.session_state["code_input_field"] = default_starter
        with col_btn2:
            if st.button("⚠️ Inject Struggling Solution", help="Injects an incomplete attempt to demo Arjun flagging gaps and Ravi stepping in"):
                st.session_state["code_input_field"] = "// Incomplete draft\n// struggling with async handling and missing event cleanups"

        code_input = st.text_area(
            label="Pull Request Code / Script:",
            value=st.session_state.get("code_input_field", default_starter),
            height=220,
            key="code_area"
        )

        if st.button("🚀 Submit PR to Arjun for Code Review", type="primary", use_container_width=True):
            if not code_input.strip():
                st.error("Please enter code before submitting your pull request.")
            else:
                with st.spinner("Arjun is reviewing your pull request against team standards..."):
                    orchestrator.submit_solution(state, code_input)
                st.rerun()

        # Arjun's Code Review Results
        if state.last_review:
            rev = state.last_review
            passed = rev.score >= 70
            badge_class = "review-status-pass" if passed else "review-status-fail"
            badge_text = "APPROVED TO MERGE" if passed else "CHANGES REQUESTED"

            st.markdown(f"""
            <div class="pr-review-container">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 12px; margin-bottom: 14px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.2rem;">👨‍💻</span>
                        <div>
                            <strong style="color: #60A5FA; font-size: 1rem;">Arjun (Senior Staff Engineer)</strong>
                            <div style="font-size: 0.75rem; color: #64748B;">Automated Pull Request Code Review</div>
                        </div>
                    </div>
                    <div>
                        <span class="{badge_class}">{badge_text} ({rev.score}/100)</span>
                    </div>
                </div>
                <div style="font-size: 0.95rem; color: #E2E8F0; line-height: 1.6; margin-bottom: 14px;">
                    {rev.feedback}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if rev.skills_demonstrated:
                st.markdown(f"**Demonstrated Competencies:** {', '.join([f'`{s}`' for s in rev.skills_demonstrated])}")

            if rev.gaps:
                st.markdown("**Identified Technical Gaps:**")
                for g in rev.gaps:
                    st.error(f"**{g.skill}**: {g.reason}")

        # Ravi's Mentorship / Coaching Micro-Lesson
        if state.active_lesson:
            lesson = state.active_lesson
            st.markdown(f"""
            <div class="coaching-card">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.25rem;">🧑‍🏫</span>
                    <h3 style="margin: 0; color: #FBBF24; font-size: 1.15rem; font-weight: 700;">
                        Ravi's Coaching Micro-Lesson: {lesson.lesson_title}
                    </h3>
                </div>
                <p style="font-size: 0.95rem; color: #FEF3C7; line-height: 1.6; margin-bottom: 12px;">
                    {lesson.explanation}
                </p>
                <div class="practice-code-box">
                    <strong>🎯 Mini Practice Challenge:</strong><br>
                    {lesson.practice_task}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📚 Curated Learning Links (Verified Zero-Hallucination)")
            for res in lesson.resources:
                col_link, col_plat = st.columns([3.5, 1])
                with col_link:
                    st.markdown(f"🔗 **[{res.title}]({res.url})** — *{res.description}*")
                with col_plat:
                    st.markdown(f"`{res.platform}`")


# ------------------------------------------------------------------------------
# TAB 2: INTERACTIVE ROADMAP
# ------------------------------------------------------------------------------
with tab_roadmap:
    st.subheader(f"🗺️ Competency Progression Roadmap // {role_options[state.current_role]}")
    st.caption("Skills are ordered strictly by prerequisites first, followed by descending gap magnitude.")

    target_skills = orchestrator.get_role_targets(state.current_role)
    prereqs = role_meta.get("prerequisites_order", list(target_skills.keys()))
    roadmap_items = generate_roadmap(state.skills, target_skills, prereqs)

    if not roadmap_items:
        st.balloons()
        st.success("🎉 Outstanding achievement! You have mastered all competencies for this role.")
    else:
        for idx, item in enumerate(roadmap_items, 1):
            skill = item["skill"]
            curr = item["current_level"]
            tgt = item["target_level"]
            gap = item["gap"]
            pct = (curr / tgt) * 100 if tgt > 0 else 100

            st.markdown(f"""
            <div class="roadmap-node">
                <div style="display: flex; align-items: center;">
                    <span class="roadmap-step-badge">{idx}</span>
                    <div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">{skill}</div>
                        <div style="font-size: 0.8rem; color: #94A3B8;">Current Level: <strong>{curr}</strong> / Target Level: <strong>{tgt}</strong></div>
                    </div>
                </div>
                <div>
                    <span style="background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); padding: 4px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600;">
                        -{gap} Level{'s' if gap > 1 else ''} to Target
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(pct / 100.0)

            skill_res = resources_data.get(skill, [])
            if skill_res:
                with st.expander(f"📖 Curated Learning Resources for {skill}"):
                    for r in skill_res:
                        st.markdown(f"- 🔗 [{r['title']}]({r['url']}) (`{r['platform']}`) — {r['description']}")


# ------------------------------------------------------------------------------
# TAB 3: READINESS & ANALYTICS
# ------------------------------------------------------------------------------
with tab_progress:
    st.subheader("📈 Talent Analytics & Hire Readiness Benchmarks")

    # Priya Recruiter Card
    if state.last_recruiter_verdict:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #064E3B 0%, #065F46 100%); border: 1px solid #10B981; border-radius: 12px; padding: 18px 22px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.3rem;">👩‍💼</span>
                <div>
                    <h4 style="margin: 0; color: #A7F3D0; font-size: 1.05rem;">Priya's Technical Recruiter Verdict</h4>
                    <div style="font-size: 0.75rem; color: #6EE7B7;">Market Readiness Benchmark • Evaluated in Real-Time</div>
                </div>
            </div>
            <p style="margin-top: 10px; font-size: 1rem; color: #ECFDF5; line-height: 1.6;">
                "{state.last_recruiter_verdict.verdict}"
            </p>
        </div>
        """, unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("#### 📉 Hire Readiness Progression")
        if state.readiness_history:
            df_hist = pd.DataFrame(state.readiness_history)
            df_hist["Event"] = df_hist["step"]
            st.line_chart(df_hist.set_index("Event")["readiness"], use_container_width=True)
        else:
            st.caption("No sprint history logged yet.")

    with col_chart2:
        st.markdown(f"#### 📊 Skill Proficiencies vs Target ({role_options[state.current_role]})")
        target_skills = orchestrator.get_role_targets(state.current_role)
        chart_data = []
        for s, tgt in target_skills.items():
            chart_data.append({
                "Skill": s,
                "Current Level": state.skills.get(s, 0),
                "Target Level": tgt
            })
        df_skills = pd.DataFrame(chart_data)
        st.bar_chart(df_skills.set_index("Skill"), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🏆 Sprint Ticket Completion History")
    if state.completed_ticket_ids:
        for tid in state.completed_ticket_ids:
            tk = orchestrator.get_ticket_by_id(tid)
            if tk:
                st.markdown(f"""
                <div style="background: #0F172A; border-left: 3px solid #10B981; padding: 10px 16px; border-radius: 6px; margin-bottom: 8px;">
                    <strong style="color: #34D399;">✔ {tk.id}</strong>: {tk.title}
                    <span style="font-size: 0.8rem; color: #94A3B8; margin-left: 10px;">(Skills: {', '.join(tk.skills_tested)})</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No tickets merged yet. Complete and merge your first sprint ticket in the Workspace tab!")

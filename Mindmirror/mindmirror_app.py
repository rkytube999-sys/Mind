import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Engines
from thought_analyzer import analyze_thought
from distortion_detector import detect_distortions
from emotion_engine import generate_emotion_profile
from personality_mapper import build_personality_profile
from clarity_engine import build_clarity_report
from reflection_journal import (
    initialize_journal,
    save_reflection,
    get_journal
)
from daily_checkin import (
    initialize_checkins,
    record_checkin,
    get_checkins,
    get_streak
)
from insight_share_engine import build_share_block
from therapist_chat import (
    initialize_chat,
    add_user_message,
    add_assistant_message,
    generate_response
)

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(
    page_title="MindMirror",
    page_icon="🧠",
    layout="wide"
)

# ------------------------------------------------
# STYLE
# ------------------------------------------------

st.markdown("""
<style>

.big-title{
font-size:52px;
font-weight:800;
text-align:center;
letter-spacing:-1px;
margin-bottom:6px;
}

.subtitle{
text-align:center;
color:#64748b;
margin-bottom:40px;
font-size:18px;
}

.card{
background:white;
padding:28px;
border-radius:16px;
box-shadow:0px 8px 25px rgba(0,0,0,0.05);
margin-bottom:25px;
}

.section{
margin-top:20px;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.markdown("<div class='big-title'>🧠 MindMirror</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Understand your thoughts. Gain clarity.</div>", unsafe_allow_html=True)

# ------------------------------------------------
# INIT SYSTEMS
# ------------------------------------------------

initialize_journal(st.session_state)
initialize_checkins(st.session_state)
initialize_chat(st.session_state)

if "last_user_msg" not in st.session_state:
    st.session_state.last_user_msg = None

# ------------------------------------------------
# NAVIGATION
# ------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["Reflection", "Journal", "Daily Check-In", "AI Therapist"]
)

# =================================================
# REFLECTION
# =================================================

with tab1:

    st.markdown("### What's on your mind?")

    user_input = st.text_area(
        "",
        height=150,
        placeholder="Write freely. This is your private reflection space."
    )

    if st.button("Analyze Thought", type="primary"):

        if user_input.strip() == "":
            st.warning("Please write something first.")
            st.stop()

        with st.spinner("MindMirror is analyzing your thought..."):

            analysis = analyze_thought(user_input)

            distortions = detect_distortions(user_input)
            emotions = generate_emotion_profile(user_input)
            personality = build_personality_profile(user_input)

            clarity = build_clarity_report(
                emotions,
                distortions,
                personality
            )

            save_reflection(
                st.session_state,
                user_input,
                analysis,
                personality,
                emotions
            )

        # ------------------------------
        # ANALYSIS
        # ------------------------------

        st.markdown("## Reflection")

        st.markdown(
            f"<div class='card'>{analysis}</div>",
            unsafe_allow_html=True
        )

        # ------------------------------
        # CLARITY GAUGE
        # ------------------------------

        st.markdown("### Clarity Score")

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=clarity["score"],
            title={'text': "Clarity"},
            gauge={
                'axis': {'range': [0,100]},
                'bar': {'color': "#2563eb"},
                'steps': [
                    {'range': [0,40], 'color': "#fee2e2"},
                    {'range': [40,70], 'color': "#fde68a"},
                    {'range': [70,100], 'color': "#bbf7d0"}
                ]
            }
        ))

        fig.update_layout(height=300)

        st.plotly_chart(fig, use_container_width=True)

        st.caption(clarity["level"])
        st.write(clarity["summary"])

        # ------------------------------
        # EMOTION RADAR
        # ------------------------------

        st.markdown("### Emotional Signals")

        labels = list(emotions.keys())
        values = list(emotions.values())

        radar = go.Figure()

        radar.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself'
        ))

        radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,100])),
            showlegend=False,
            height=400
        )

        st.plotly_chart(radar, use_container_width=True)

        # ------------------------------
        # DISTORTIONS
        # ------------------------------

        st.markdown("### Cognitive Distortions")

        if distortions:
            for d in distortions:
                st.write("•", d)
        else:
            st.success("No major distortions detected.")

        # ------------------------------
        # PERSONALITY
        # ------------------------------

        st.markdown("### MindMirror Archetype")

        st.info(personality["archetype"])

        # ------------------------------
        # SHARE INSIGHT
        # ------------------------------

        share = build_share_block(analysis)

        if share:

            st.markdown("### Shareable Insight")

            st.code(share)

# =================================================
# JOURNAL
# =================================================

with tab2:

    st.markdown("## Reflection Journal")

    journal = get_journal(st.session_state)

    if not journal:
        st.info("You haven't created any reflections yet.")

    else:

        for entry in reversed(journal):

            st.markdown(f"### {entry['date']}")

            st.markdown("**Thought**")
            st.write(entry["thought"])

            st.markdown("**Insight**")
            st.write(entry["analysis"])

            st.divider()

# =================================================
# DAILY CHECK-IN
# =================================================

with tab3:

    st.markdown("## Daily Mind Check")

    mood = st.selectbox(
        "How are you feeling today?",
        [
            "Calm",
            "Motivated",
            "Confused",
            "Anxious",
            "Overwhelmed",
            "Sad"
        ]
    )

    if st.button("Record Mood"):

        record_checkin(st.session_state, mood)

        st.success("Mood recorded.")

    st.markdown(f"🔥 Current Streak: {get_streak(st.session_state)} days")

    checkins = get_checkins(st.session_state)

    if checkins:

        st.markdown("### Mood History")

        for c in reversed(checkins):
            st.write(f"{c['date']} — {c['mood']}")

# =================================================
# AI THERAPIST
# =================================================

with tab4:

    st.markdown("## AI Therapist")

    for msg in st.session_state.chat_history:

        if msg["role"] == "system":
            continue

        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ------------------------------------------------
# CHAT INPUT
# ------------------------------------------------

user_msg = st.chat_input("Share what's on your mind...")

if user_msg and user_msg != st.session_state.last_user_msg:

    st.session_state.last_user_msg = user_msg

    add_user_message(st.session_state, user_msg)

    reply = generate_response(st.session_state)

    add_assistant_message(st.session_state, reply)

    st.rerun()

# ------------------------------------------------
# FOOTER
# ------------------------------------------------

st.markdown("---")

st.caption(
"MindMirror • A reflection tool for clarity. Not a substitute for professional mental health care."
)
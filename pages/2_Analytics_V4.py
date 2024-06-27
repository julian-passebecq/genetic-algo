import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils_V3 import calculate_metrics

st.title("Schedule Analytics")

if 'schedules' in st.session_state:
    best_schedule = st.session_state.schedules[0]
    metrics = calculate_metrics(best_schedule)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Incorrect Rest Periods", metrics["incorrect_rest_periods"])
    col2.metric("Non-Security Night Shifts", metrics["non_security_night_shifts"])
    col3.metric("Total Night Shifts", sum(metrics["night_shifts_per_agent"].values()))
    col4.metric("Incomplete Night Shifts", metrics["incomplete_night_shifts"])

    st.subheader("Shift Distribution")
    fig = px.bar(x=list(metrics["shift_distribution"].keys()),
                 y=list(metrics["shift_distribution"].values()),
                 labels={'x': 'Shift', 'y': 'Count'},
                 title="Shift Distribution")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Night Shifts per Agent")
    fig = px.bar(x=list(metrics["night_shifts_per_agent"].keys()),
                 y=list(metrics["night_shifts_per_agent"].values()),
                 labels={'x': 'Agent', 'y': 'Count'},
                 title="Night Shifts per Agent")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Skill Utilization")
    skill_data = []
    for agent, skills in metrics["skill_utilization"].items():
        for skill, count in skills.items():
            skill_data.append({"Agent": agent, "Skill": skill, "Count": count})
    df_skills = pd.DataFrame(skill_data)
    fig = px.bar(df_skills, x="Agent", y="Count", color="Skill",
                 title="Skill Utilization per Agent")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.metric("Total Appointments", metrics["total_appointments"])
    col2.metric("Mismatched Skills", metrics["mismatched_skills"])

    st.subheader("Fitness Over Generations")
    if 'logbook' in st.session_state:
        gen = st.session_state.logbook.select("gen")
        fit_mins = st.session_state.logbook.select("min")
        fit_maxs = st.session_state.logbook.select("max")
        fit_avgs = st.session_state.logbook.select("avg")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=gen, y=fit_mins, mode='lines', name='Min Fitness'))
        fig.add_trace(go.Scatter(x=gen, y=fit_maxs, mode='lines', name='Max Fitness'))
        fig.add_trace(go.Scatter(x=gen, y=fit_avgs, mode='lines', name='Avg Fitness'))
        fig.update_layout(title='Fitness over Generations', xaxis_title='Generation', yaxis_title='Fitness')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No fitness data available. Please generate a schedule first.")
else:
    st.warning("No schedule generated yet. Please go to the Schedule Generation page.")
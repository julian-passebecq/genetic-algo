import streamlit as st
from streamlit_calendar import calendar
import datetime
import pandas as pd

def show_final_schedule():
    st.title("Final Schedule with Assigned Agents")

    if 'final_schedule' not in st.session_state:
        st.warning("No schedule has been generated yet. Please go to the Schedule Generation page first.")
        return

    final_schedule = st.session_state.final_schedule

    # Prepare events for the calendar
    events = []
    for meeting, agent in final_schedule.items():
        events.append({
            "title": f"Agent {agent.id}: {meeting.required_skill}",
            "start": meeting.start.isoformat(),
            "end": meeting.end.isoformat(),
            "backgroundColor": "#FF9999" if meeting.is_night else "#99FF99",
            "borderColor": "#FF9999" if meeting.is_night else "#99FF99",
        })

    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
        "initialView": "timeGridWeek",
        "slotMinTime": "06:00:00",
        "slotMaxTime": "30:00:00",
        "expandRows": True,
        "height": "650px",
        "dayMaxEvents": True,
        "allDaySlot": False,
        "scrollTime": "08:00:00",
        "nowIndicator": True,
    }

    custom_css = """
        .fc-event-past { opacity: 0.8; }
        .fc-event-time { font-weight: bold; }
        .fc-event-title { font-style: italic; }
    """

    cal = calendar(events=events, options=calendar_options, custom_css=custom_css)
    st.write(cal)

    # Display warnings for unassigned meetings
    unassigned_meetings = [meeting for meeting, agent in final_schedule.items() if agent is None]
    if unassigned_meetings:
        st.subheader("Unassigned Meetings")
        for meeting in unassigned_meetings:
            st.warning(f"Unassigned: {meeting.start} - {meeting.end}, Type: {meeting.required_skill}")

    # Display agent workload summary
    st.subheader("Agent Workload Summary")
    agent_workload = {}
    for meeting, agent in final_schedule.items():
        if agent:
            if agent.id not in agent_workload:
                agent_workload[agent.id] = {"total_hours": 0, "night_hours": 0}
            duration = (meeting.end - meeting.start).total_seconds() / 3600
            agent_workload[agent.id]["total_hours"] += duration
            if meeting.is_night:
                agent_workload[agent.id]["night_hours"] += duration

    workload_data = []
    for agent_id, workload in agent_workload.items():
        workload_data.append({
            "Agent ID": agent_id,
            "Total Hours": round(workload["total_hours"], 2),
            "Day Hours": round(workload["total_hours"] - workload["night_hours"], 2),
            "Night Hours": round(workload["night_hours"], 2)
        })

    workload_df = pd.DataFrame(workload_data)
    st.table(workload_df)

if __name__ == "__main__":
    show_final_schedule()
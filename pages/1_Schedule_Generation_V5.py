import streamlit as st
from genetic_algorithm_V5 import Agent, Meeting, run_scheduling_algorithm
import datetime

def show_schedule_generation():
    st.title("Schedule Generation V5")

    if 'meetings' not in st.session_state:
        st.warning("Please generate meetings in the Meeting Management page first.")
        return

    # Predefined agents with fixed skills
    agents = [
        Agent(0, ["Fire", "Maintenance"]),
        Agent(1, ["Security"]),
        Agent(2, ["Fire"]),
        Agent(3, ["Security", "Maintenance"]),
        Agent(4, ["Security", "Fire"])
    ]

    st.subheader("Agent Skills")
    for agent in agents:
        st.write(f"Agent {agent.id}: {', '.join(agent.skills)}")

    # Convert meetings from calendar events to Meeting objects
    meetings = []
    for event in st.session_state.meetings:
        start = datetime.datetime.fromisoformat(event['start'])
        end = datetime.datetime.fromisoformat(event['end'])
        meetings.append(Meeting(start, end, event['type'], event['is_night']))

    if st.button("Generate Schedule"):
        with st.spinner("Generating schedule..."):
            final_schedule = run_scheduling_algorithm(agents, meetings)
            st.session_state.final_schedule = final_schedule
            st.success("Schedule generated successfully!")

    if 'final_schedule' in st.session_state:
        st.subheader("Generated Schedule")
        for meeting, agent in st.session_state.final_schedule.items():
            st.write(f"Meeting: {meeting.start} - {meeting.end}, Type: {meeting.required_skill}, Assigned to Agent {agent.id}")

if __name__ == "__main__":
    show_schedule_generation()
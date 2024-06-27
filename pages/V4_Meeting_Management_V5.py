import streamlit as st
from streamlit_calendar import calendar
import datetime
import random
import pandas as pd

# Define meeting types and their properties
meeting_types = {
    "Maintenance": {"color": "#FF9999", "duration": 1},
    "FireTest": {"color": "#FFCC99", "duration": 2},
    "Security": {"color": "#99FF99", "duration": 3},
    "Monitoring": {"color": "#99CCFF", "duration": 2}
}

def generate_meeting(date, client, is_night=False):
    if is_night:
        meeting_type = random.choice(["Security", "Monitoring"])
        start_hour = random.randint(20, 23) if meeting_type == "Security" else random.randint(22, 23)
    else:
        meeting_type = random.choice(list(meeting_types.keys()))
        start_hour = random.randint(8, 19)

    start_time = datetime.time(hour=start_hour)
    duration = datetime.timedelta(hours=meeting_types[meeting_type]["duration"])
    end_time = (datetime.datetime.combine(date, start_time) + duration).time()

    return {
        "title": f"Client {client}: {meeting_type}" + (" (Night)" if is_night else ""),
        "start": f"{date}T{start_time}",
        "end": f"{date}T{end_time}",
        "backgroundColor": meeting_types[meeting_type]["color"],
        "borderColor": meeting_types[meeting_type]["color"],
        "client": f"Client {client}",
        "type": meeting_type,
        "is_night": is_night
    }

def generate_meetings(start_date, num_clients=5):
    events = []
    for day in range(7):
        current_date = start_date + datetime.timedelta(days=day)
        daily_hours = 0
        while daily_hours < 40:  # 5 agents * 8 hours
            client = random.randint(1, num_clients)
            is_night = random.choice([True, False]) if daily_hours >= 32 else False
            meeting = generate_meeting(current_date, client, is_night)
            meeting_duration = meeting_types[meeting['type']]['duration']
            if daily_hours + meeting_duration <= 40:
                events.append(meeting)
                daily_hours += meeting_duration
            else:
                break
    return events

def show_meeting_management():
    st.title("Meeting Management V5")

    if 'calendar_events' not in st.session_state:
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        st.session_state.calendar_events = generate_meetings(start_of_week)

    all_clients = sorted(set(event['client'] for event in st.session_state.calendar_events))
    all_types = sorted(list(meeting_types.keys()))

    col1, col2 = st.columns(2)
    with col1:
        selected_clients = st.multiselect("Select Clients", all_clients, default=all_clients)
    with col2:
        selected_types = st.multiselect("Select Appointment Types", all_types, default=all_types)

    filtered_events = [
        event for event in st.session_state.calendar_events
        if event['client'] in selected_clients and event['type'] in selected_types
    ]

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

    cal = calendar(events=filtered_events, options=calendar_options, custom_css=custom_css)
    st.write(cal)

    st.subheader("Meeting Types and Durations")
    for meeting_type, info in meeting_types.items():
        st.markdown(
            f'<span style="color:{info["color"]}">■</span> {meeting_type} ({info["duration"]} hour{"s" if info["duration"] > 1 else ""})',
            unsafe_allow_html=True)

    if isinstance(cal, dict) and 'eventClick' in cal:
        event = cal['eventClick']['event']
        st.subheader("Selected Event")
        st.write(f"Title: {event['title']}")
        st.write(f"Start: {event['start']}")
        st.write(f"End: {event['end']}")

    st.subheader("Summary Table")
    summary_data = []
    start_date = min(datetime.datetime.fromisoformat(event['start']).date() for event in filtered_events)

    for day in range(7):
        current_date = start_date + datetime.timedelta(days=day)
        day_events = [event for event in filtered_events if
                      datetime.datetime.fromisoformat(event['start']).date() == current_date]

        total_hours = sum(meeting_types[event['type']]['duration'] for event in day_events)
        required_agents = len(day_events)
        night_appointments = sum(1 for event in day_events if event['is_night'] or int(event['start'].split('T')[1].split(':')[0]) >= 20)
        day_appointments = required_agents - night_appointments

        summary_data.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Total Hours": total_hours,
            "Required Agents": required_agents,
            "Day Appointments (6AM-8PM)": day_appointments,
            "Night Appointments (After 8PM)": night_appointments
        })

    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)

    if st.button("Generate New Events"):
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        st.session_state.calendar_events = generate_meetings(start_of_week)
        st.experimental_rerun()

    # Store the generated meetings in the session state for use in the genetic algorithm
    st.session_state.meetings = filtered_events

if __name__ == "__main__":
    show_meeting_management()
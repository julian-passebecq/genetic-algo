import datetime
import plotly.figure_factory as ff

AGENTS = {
    "Agent1": ["Fire", "Security"],
    "Agent2": ["Maintenance", "Security"],
    "Agent3": ["Fire"],
    "Agent4": ["Security"],
    "Agent5": []
}

APPOINTMENT_TYPES = ["Monitoring", "Fire", "Security", "Maintenance"]

SHIFTS = {
    "Morning": (7, 15),
    "Afternoon": (14, 22),
    "Night1": (21, 22),
    "Night2": (22, 1),
    "Night3": (2, 4),
    "Night4": (4, 5)
}

SECURITY_AGENTS = [agent for agent, skills in AGENTS.items() if "Security" in skills]


def create_calendar_view(schedule):
    df = []
    for day, day_schedule in enumerate(schedule):
        for agent, shifts in day_schedule.items():
            for shift in shifts:
                if shift[0] in SHIFTS:
                    start, end = SHIFTS[shift[0]]
                    start_time = datetime.datetime(2023, 1, day + 1, start)
                    end_time = datetime.datetime(2023, 1, day + 1, end)
                    if end < start:  # For night shifts crossing midnight
                        end_time += datetime.timedelta(days=1)
                else:  # For appointments
                    start_time = datetime.datetime(2023, 1, day + 1, SHIFTS[shifts[0][0]][0])
                    end_time = start_time + datetime.timedelta(hours=shift[1])
                df.append(dict(Task=agent, Start=start_time, Finish=end_time, Resource=shift[0]))

    fig = ff.create_gantt(df, index_col='Resource', show_colorbar=True, group_tasks=True)
    fig.update_layout(title='Weekly Schedule', xaxis_title='Day', yaxis_title='Agent')
    return fig


def calculate_metrics(schedule):
    metrics = {
        "shift_distribution": {shift: 0 for shift in SHIFTS},
        "incorrect_rest_periods": 0,
        "night_shifts_per_agent": {agent: 0 for agent in AGENTS},
        "non_security_night_shifts": 0,
        "incomplete_night_shifts": 0,
        "skill_utilization": {agent: {skill: 0 for skill in AGENTS[agent]} for agent in AGENTS},
        "total_appointments": 0,
        "mismatched_skills": 0
    }

    for day_index, day_schedule in enumerate(schedule):
        for agent, shifts in day_schedule.items():
            for shift in shifts:
                if shift[0] in SHIFTS:
                    metrics["shift_distribution"][shift[0]] += 1
                    if shift[0].startswith("Night"):
                        metrics["night_shifts_per_agent"][agent] += 0.25  # Count each night segment as 0.25
                        if "Security" not in AGENTS[agent]:
                            metrics["non_security_night_shifts"] += 0.25
                else:  # Appointment
                    metrics["total_appointments"] += 1
                    if shift[0] in AGENTS[agent]:
                        metrics["skill_utilization"][agent][shift[0]] += 1
                    elif shift[0] != "Monitoring":
                        metrics["mismatched_skills"] += 1

            if len(shifts) == 4 and all(s[0].startswith("Night") for s in shifts):
                if "Security" not in AGENTS[agent]:
                    metrics["non_security_night_shifts"] += 1
            elif any(s[0].startswith("Night") for s in shifts):
                metrics["incomplete_night_shifts"] += 1

            if day_index > 0 and "Night4" in [s[0] for s in schedule[day_index - 1][agent]]:
                if shifts[0][0] == "Morning":
                    metrics["incorrect_rest_periods"] += 1

    return metrics
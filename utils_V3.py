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
                    start_time = datetime.datetime(2023, 1, day+1, start)
                    end_time = datetime.datetime(2023, 1, day+1, end)
                    if end < start:  # For night shifts crossing midnight
                        end_time += datetime.timedelta(days=1)
                else:  # For appointments
                    start_time = datetime.datetime(2023, 1, day+1, SHIFTS[shifts[0][0]][0])
                    end_time = start_time + datetime.timedelta(hours=shift[1])
                df.append(dict(Task=agent, Start=start_time, Finish=end_time, Resource=shift[0]))
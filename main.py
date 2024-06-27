# Main.py
import streamlit as st
import pandas as pd
import numpy as np
from deap import base, creator, tools, algorithms
import random
import datetime
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
AGENTS: Dict[str, List[str]] = {
    "Agent1": ["Fire", "Security"],
    "Agent2": ["Maintenance", "Security"],
    "Agent3": ["Fire"],
    "Agent4": ["Security"],
    "Agent5": []
}
APPOINTMENT_TYPES: List[str] = ["Monitoring", "Fire", "Security", "Maintenance"]
WORK_HOURS: int = 8

SHIFTS: Dict[str, Tuple[int, int]] = {
    "Morning": (7, 15),
    "Afternoon": (14, 22),
    "Night1": (21, 22),
    "Night2": (22, 1),
    "Night3": (2, 4),
    "Night4": (4, 5)
}

SECURITY_AGENTS: List[str] = [agent for agent, skills in AGENTS.items() if "Security" in skills]

# Streamlit configuration
st.set_page_config(page_title="Security Company Scheduler", layout="wide")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Schedule Generation", "Analytics", "Explanation"])


# Genetic Algorithm functions
def assign_night_shifts() -> Dict[int, str]:
    night_shifts = {}
    for day in range(7):
        if day < 3:  # Only assign night shifts for 3 days a week
            night_shifts[day] = random.choice(SECURITY_AGENTS)
    return night_shifts


def generate_appointments(num_appointments: int = 20) -> List[Tuple[int, str, int]]:
    return [
        (random.randint(0, 6), random.choice(APPOINTMENT_TYPES), random.randint(1, 4))
        for _ in range(num_appointments)
    ]


def create_individual(night_shifts: Dict[int, str], appointments: List[Tuple[int, str, int]]) -> List[
    Dict[str, List[Tuple[str, Tuple[int, int]]]]]:
    week_schedule = []
    for day in range(7):
        day_schedule = {agent: [] for agent in AGENTS}
        if day in night_shifts:
            night_agent = night_shifts[day]
            day_schedule[night_agent] = [
                (f"Night{i}", SHIFTS[f"Night{i}"]) for i in range(1, 5)
            ]
        for agent in AGENTS:
            if not day_schedule[agent]:
                shift = random.choice(["Morning", "Afternoon"])
                day_schedule[agent].append((shift, SHIFTS[shift]))

        # Assign appointments
        day_appointments = [app for app in appointments if app[0] == day]
        for _, app_type, duration in day_appointments:
            available_agents = [agent for agent, shifts in day_schedule.items() if len(shifts) == 1]
            if available_agents:
                agent = random.choice(available_agents)
                if app_type in AGENTS[agent] or app_type == "Monitoring":
                    day_schedule[agent].append((app_type, duration))

        week_schedule.append(day_schedule)
    return week_schedule


def evaluate_schedule(individual: List[Dict[str, List[Tuple[str, Tuple[int, int]]]]]) -> Tuple[int]:
    fitness = 0
    for day_index, day_schedule in enumerate(individual):
        for agent, shifts in day_schedule.items():
            # Check for proper shift assignment
            if len(shifts) == 1 or (len(shifts) == 4 and all(s[0].startswith("Night") for s in shifts)):
                fitness += 1

            # Check for rest period after night shift
            if day_index > 0 and any(s[0] == "Night4" for s in individual[day_index - 1][agent]):
                if shifts[0][0] == "Morning":
                    fitness -= 10  # Penalize morning shift after night shift

            # Check for security certification for night shifts
            if any(shift[0].startswith("Night") for shift in shifts):
                if "Security" not in AGENTS[agent]:
                    fitness -= 20  # Heavily penalize non-security agents on night shift
                else:
                    fitness += 5  # Reward correct assignment of night shift

            # Check for complete night shift assignment
            if len(shifts) == 4 and all(s[0].startswith("Night") for s in shifts):
                fitness += 10  # Reward complete night shift assignment

            # Check for skill matching in appointments
            for shift in shifts:
                if shift[0] in APPOINTMENT_TYPES and shift[0] != "Monitoring":
                    if shift[0] in AGENTS[agent]:
                        fitness += 5  # Reward correct skill matching
                    else:
                        fitness -= 5  # Penalize incorrect skill matching

    return (fitness,)


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
night_shifts = assign_night_shifts()
appointments = generate_appointments()
toolbox.register("individual", tools.initIterate, creator.Individual,
                 lambda: create_individual(night_shifts, appointments))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_schedule)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)


@st.cache(allow_output_mutation=True)
def run_genetic_algorithm(population_size: int, generations: int, crossover_rate: float, mutation_rate: float):
    try:
        pop = toolbox.population(n=population_size)
        hof = tools.HallOfFame(3)  # Keep top 3 individuals
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)

        pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=crossover_rate, mutpb=mutation_rate,
                                           ngen=generations, stats=stats, halloffame=hof, verbose=True)

        return hof, logbook
    except Exception as e:
        logger.error(f"Error in genetic algorithm: {str(e)}")
        return None, None


def create_calendar_view(schedule: List[Dict[str, List[Tuple[str, Tuple[int, int]]]]]):
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


def calculate_metrics(schedule: List[Dict[str, List[Tuple[str, Tuple[int, int]]]]]):
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


# Page content
if page == "Home":
    st.title("Security Company Scheduler")
    st.write("Welcome to the Security Company Scheduler. Use the sidebar to navigate through different sections.")
    st.write("This application uses a genetic algorithm to generate optimal schedules for security personnel.")

    st.subheader("Quick Start")
    st.write("1. Go to the 'Schedule Generation' page to create a new schedule.")
    st.write("2. Adjust the genetic algorithm parameters as needed.")
    st.write("3. Click 'Generate Schedule' to create a new schedule.")
    st.write("4. View the generated schedules and analyze the results on the 'Analytics' page.")

elif page == "Schedule Generation":
    st.title("Schedule Generation")

    col1, col2 = st.columns(2)
    with col1:
        population_size = st.slider("Population Size", 50, 500, 100)
        generations = st.slider("Generations", 10, 100, 40)
    with col2:
        crossover_rate = st.slider("Crossover Rate", 0.1, 1.0, 0.7)
        mutation_rate = st.slider("Mutation Rate", 0.01, 0.5, 0.2)

    if st.button("Generate Schedule"):
        with st.spinner("Generating schedule..."):
            best_schedules, logbook = run_genetic_algorithm(population_size, generations, crossover_rate, mutation_rate)
            if best_schedules and logbook:
                st.session_state.schedules = best_schedules
                st.session_state.logbook = logbook
                st.success("Schedules generated successfully!")
            else:
                st.error("An error occurred while generating schedules. Please try again.")

    if 'schedules' in st.session_state:
        for i, schedule in enumerate(st.session_state.schedules):
            st.subheader(f"Schedule {i + 1} (Fitness: {schedule.fitness.values[0]})")
            fig = create_calendar_view(schedule)
            st.plotly_chart(fig, use_container_width=True)

elif page == "Analytics":
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
        gen = st.session_state.logbook.select("gen")
        fit_mins = st.session_state.logbook.select("min")
        fit_maxs = st.session_state.logbook.select("max")
        fit_avgs = st.session_state.logbook.select("avg")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=gen, y=fit_mins, mode='lines', name='Min Fitness'))
        fig.add_trace(go.Scatter(x=gen, y=fit_maxs, mode='lines', name='Max Fitness'))
        fig.add_trace(go.Scatter(x=gen,
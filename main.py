import streamlit as st
import pandas as pd
import numpy as np
from deap import base, creator, tools, algorithms
import random
import datetime

# Constants
AGENTS = ["Agent1", "Agent2", "Agent3", "Agent4", "Agent5"]
SKILLS = {"Agent1": ["Fire", "Security"], "Agent2": ["Maintenance", "Security"], 
          "Agent3": ["Fire"], "Agent4": ["Security"], "Agent5": []}
WORK_HOURS = 8
LUNCH_BREAK = 1
SHORT_BREAK = 0.5
TRAVEL_TIME = 0.5

# Streamlit app
st.title("Security Company Weekly Scheduler")

# Input for appointments
st.sidebar.header("Add Appointment")
appointment_type = st.sidebar.selectbox("Type", ["Monitoring", "Fire", "Security", "Maintenance"])
start_time = st.sidebar.time_input("Start Time")
duration = st.sidebar.number_input("Duration (hours)", min_value=1, max_value=8, value=2)
is_night_shift = st.sidebar.checkbox("Night Shift")

if st.sidebar.button("Add Appointment"):
    # Logic to add appointment to the schedule
    st.sidebar.success("Appointment added!")

# Genetic Algorithm functions
def create_individual():
    # Create a random schedule for a week
    week_schedule = []
    for _ in range(7):  # 7 days in a week
        day_schedule = {agent: [] for agent in AGENTS}
        for hour in range(24):
            for agent in AGENTS:
                if random.random() < 0.2:  # 20% chance of having an appointment
                    appointment = random.choice(["Monitoring", "Fire", "Security", "Maintenance"])
                    day_schedule[agent].append((hour, appointment))
        week_schedule.append(day_schedule)
    return week_schedule

def evaluate_schedule(individual):
    # Evaluate the fitness of a schedule
    fitness = 0
    for day_schedule in individual:
        for agent, appointments in day_schedule.items():
            work_hours = sum(1 for _ in appointments)
            if WORK_HOURS <= work_hours <= WORK_HOURS + 2:
                fitness += 1
            # Add more evaluation criteria here
    return (fitness,)

# Set up the genetic algorithm
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_schedule)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

# Genetic Algorithm execution
def run_genetic_algorithm():
    pop = toolbox.population(n=50)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=40, stats=stats, halloffame=hof, verbose=True)

    return hof[0]

# Display the schedule
if st.button("Generate Schedule"):
    best_schedule = run_genetic_algorithm()
    st.write("Best Schedule:")
    for day, day_schedule in enumerate(best_schedule):
        st.subheader(f"Day {day + 1}")
        for agent, appointments in day_schedule.items():
            st.write(f"{agent}: {appointments}")

# Additional features and improvements can be added here
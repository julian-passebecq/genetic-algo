import random
from deap import base, creator, tools, algorithms
from utils_V3 import AGENTS, SHIFTS, SECURITY_AGENTS, APPOINTMENT_TYPES


def assign_night_shifts():
    night_shifts = {}
    for day in range(7):
        if day < 3:  # Only assign night shifts for 3 days a week
            night_shifts[day] = random.choice(SECURITY_AGENTS)
    return night_shifts


def generate_appointments(num_appointments=20):
    return [
        (random.randint(0, 6), random.choice(APPOINTMENT_TYPES), random.randint(1, 4))
        for _ in range(num_appointments)
    ]


def create_individual(night_shifts, appointments):
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


def evaluate_schedule(individual):
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


def run_genetic_algorithm(population_size, generations, crossover_rate, mutation_rate):
    pop = toolbox.population(n=population_size)
    hof = tools.HallOfFame(3)  # Keep top 3 individuals
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=crossover_rate, mutpb=mutation_rate,
                                       ngen=generations, stats=stats, halloffame=hof, verbose=True)

    return hof, logbook
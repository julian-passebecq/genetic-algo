import streamlit as st
from genetic_algorithm_V3 import run_genetic_algorithm
from utils_V3 import create_calendar_view

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
        st.subheader(f"Schedule {i+1} (Fitness: {schedule.fitness.values[0]})")
        fig = create_calendar_view(schedule)
        st.plotly_chart(fig, use_container_width=True)
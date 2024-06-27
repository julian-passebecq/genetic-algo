import streamlit as st
import plotly.graph_objects as go

st.title("How It Works")

explanation = """
The Security Company Scheduler uses a genetic algorithm to optimize weekly schedules. 

Key Features:
1. Assigns shifts and appointments to agents based on their skills.
2. Ensures proper rest periods between shifts.
3. Optimizes night shift distribution among qualified agents.
4. Maximizes skill utilization for specific appointments.

The genetic algorithm mimics natural selection:
1. Initial population of random schedules
2. Evaluation based on fitness criteria
3. Selection of best schedules
4. Crossover to create new schedules
5. Mutation to maintain diversity
6. Repeat for multiple generations

The result is a near-optimal schedule balancing multiple objectives and constraints.
"""

st.write(explanation)

st.subheader("Genetic Algorithm Process")
process = [
    "Initial Population",
    "Fitness Evaluation",
    "Selection",
    "Crossover",
    "Mutation",
    "New Generation"
]
fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = process,
      color = "blue"
    ),
    link = dict(
      source = [0, 1, 2, 3, 4],
      target = [1, 2, 3, 4, 5],
      value = [1, 1, 1, 1, 1]
  ))])
fig.update_layout(title_text="Genetic Algorithm Process", font_size=10)
st.plotly_chart(fig, use_container_width=True)
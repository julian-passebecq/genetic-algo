import streamlit as st
import plotly.graph_objects as go
import plotly.figure_factory as ff
import datetime

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

st.subheader("Genetic Algorithm Timeline")
gantt_data = [
    dict(Task="Initialize Population", Start='2023-01-01', Finish='2023-01-02', Resource='Step 1'),
    dict(Task="Evaluate Fitness", Start='2023-01-02', Finish='2023-01-03', Resource='Step 2'),
    dict(Task="Selection", Start='2023-01-03', Finish='2023-01-04', Resource='Step 3'),
    dict(Task="Crossover", Start='2023-01-04', Finish='2023-01-05', Resource='Step 4'),
    dict(Task="Mutation", Start='2023-01-05', Finish='2023-01-06', Resource='Step 5'),
    dict(Task="New Generation", Start='2023-01-06', Finish='2023-01-07', Resource='Step 6'),
    dict(Task="Repeat Steps 2-6", Start='2023-01-07', Finish='2023-01-10', Resource='Iteration')
]

fig = ff.create_gantt(gantt_data, index_col='Resource', show_colorbar=True, group_tasks=True)
fig.update_layout(title='Genetic Algorithm Timeline', xaxis_title='Time', yaxis_title='Steps')
st.plotly_chart(fig, use_container_width=True)
import streamlit as st

st.set_page_config(page_title="Security Company Scheduler", layout="wide")

st.title("Security Company Scheduler")
st.write("Welcome to the Security Company Scheduler. Use the sidebar to navigate through different sections.")
st.write("This application uses a genetic algorithm to generate optimal schedules for security personnel.")

st.subheader("Quick Start")
st.write("1. Go to the 'Schedule Generation' page to create a new schedule.")
st.write("2. Adjust the genetic algorithm parameters as needed.")
st.write("3. Click 'Generate Schedule' to create a new schedule.")
st.write("4. View the generated schedules and analyze the results on the 'Analytics' page.")
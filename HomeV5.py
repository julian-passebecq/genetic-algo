import streamlit as st

st.set_page_config(page_title="Security Company Scheduler V5", layout="wide")

st.title("Security Company Scheduler V5")
st.write("Welcome to the Security Company Scheduler. Use the sidebar to navigate through different sections.")
st.write("This application uses a genetic algorithm to generate optimal schedules for security personnel.")

st.subheader("How to use this app:")
st.write("1. Go to the 'Meeting Management' page to view and generate meetings.")
st.write("2. Once meetings are generated, go to the 'Schedule Generation' page to create a schedule.")
st.write("3. View the generated schedule and analytics on the 'Final Schedule' page.")
st.write("4. You can always return to the 'Meeting Management' page to generate new meetings and start over.")

st.subheader("Pages:")
st.write("1. Schedule Generation: Set up agents and run the genetic algorithm.")
st.write("2. Analytics: View statistics and charts about the generated schedule.")
st.write("3. Explanation: Learn about how the genetic algorithm works.")
st.write("4. Meeting Management: Generate and manage meetings.")
st.write("5. Final Schedule: View the final schedule with assigned agents and analytics.")
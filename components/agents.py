from crewai import Agent
import streamlit as st

from langchain_groq import ChatGroq

GROQ_API_KEY = st.secrets["groq"]["api_key"]

llm=ChatGroq(temperature=0,
             model_name="llama3-70b-8192",
             api_key=GROQ_API_KEY)

# Define Agents
student_assessor = Agent(
    role='Student Assesor',
    goal='Generate a multiple choice questions based on a topic, grade and difficulty level',
    backstory="You are an educator with deep knowledge of all subjects of middle school and expertise in creating multiple choice questions for assessign students",
    verbose=True,
    allow_delegation=False,
    llm=llm
)
import requests
from groq import Groq
import os
import json
import streamlit as st
import sqlite3
from components import db_interactions
import plotly.graph_objects as go
import streamlit as st
from pydantic import BaseModel, Field



GROQ_API_KEY = st.secrets["groq"]["api_key"]
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

client = Groq()

question_format = """
{
    "question": "the question",
    "options": [
        {"option_number": 1, "option_text": "text"},
        {"option_number": 2, "option_text": "text"},
        {"option_number": 3, "option_text": "text"},
        {"option_number": 4, "option_text": "text"}
    ],
    "correct_answer": "the correct answer text",
    "difficulty": difficulty level of the question between 0 to 1 (provide as a decimal value rounded to one digit after the decimal point)
    "blooms_taxonomy": "bloom_taxonomy of the question",
    "hints": ["hint 1","hint2", "hint3"...],
    "step_by_step": ["step 1", "Step 2", "Step 3"...]
}
"""

class Question(BaseModel):
    question: str = Field(description="The question")
    options: list[str] = Field(description="multiple choice options for the question")
    correct_answer: str = Field(description="The correct answer out of the multiple choice answers")
    difficulty: float = Field(description="difficulty level of the question between 0 to 1 as a float value rounded to one digit after the decimal point)")
    blooms_taxonomy:str = Field(description="Blooms Taxonomy of the question")
    hints: list[str] = Field(description="hints for solving the question")
    step_by_step: list[str] = Field(description="step by step solution for the question")




# Example function to fetch a question from LLM
def get_question(topic, grade_level, current_proficiency):
        # Example JSON format for the question with option numbers included
    question_requirement_info = f"Grade: {grade_level}, Topic: {topic}, Current Proficiency: {current_proficiency}"


# Fetch student's question history from the user_detail table
    student_history = db_interactions.read_student_history(st.session_state['session_id'])

    student_history_verbose = []

    for idx, history in enumerate(student_history, start=1):
        status = "correctly" if (history["is_correct"]==1) else "wrongly"
        verbose_string = f"{idx}. Student answered the question '{history['question']}' with difficulty {history['difficulty']}, {status}."
        student_history_verbose.append(verbose_string)

    print("#####Student History######")
    print(student_history_verbose)

    # Message framing
    if(student_history_verbose==[]):
        information = [
            {
                "role":"system",
                "content":f"""
                Background: You are a helpful Tutor who knows subjects and topics of middle school in depth
                        Based on the student's Grade, Topic and Current Proficiency level (between 0 to 1), you have to create a question of a difficulty level 0.1 higher than the Current Proficiency on the same Topic of the same grade.
                        You should make it a multiple choice question and generate 4 options, correct answer, hint and steps.
                        Each option should be different from each other
                        Important:one of the options should be equal to the correct answer.
                        Avoid question that needs a reference to any image or diagram.
                        Important: You have to generate only one question
                Task: Create a question based on this information: {question_requirement_info}, 
                You have to provide response in JSON schema only
                """
                f" The JSON object must use the schema: {json.dumps(Question.model_json_schema(),indent=2)}"
            }
            ]
    else:
        information = [
            {
                "role":"system",
                "content":f"""
                Background: You are a helpful Tutor who knows subjects and topics of middle school in depth
                        Based on the student's Grade, Topic and Current Proficiency level (between 0 to 1), you have to create a question of a difficulty level 0.1 higher than the Current Proficiency on the same Topic of the same grade.
                        You should make it a multiple choice question and generate 4 options, correct answer, hint and steps.
                        Each option should be different from each other
                        one of the options should be the correct answer.
                        Avoid question that needs a reference to any image or diagram.
                        You have to generate only one question
                Task: Create a question based on this information: {question_requirement_info}.
                Context: These questions are already asked to the student: {student_history_verbose}. 
                Don't generate question similar to these ones
                """
                f" The JSON object must use the schema: {json.dumps(Question.model_json_schema(),indent=2)}"}
            ]
    
    
    print("##########information###########")
    print(information)
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=information,
        temperature=0,
        response_format={"type": "json_object"},
    )
    print(response)

    # Get the output response from the LLM
    output_response = Question.model_validate_json(response.choices[0].message.content)

    # Debugging output
    print("output_response",output_response)

    return output_response
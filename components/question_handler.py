import streamlit as st
from .llm_integration import get_question
from .db_interactions import save_interaction

def ask_question(session_state):
    if st.button("Get Next Question"):
        # Get question from LLM based on current proficiency
        question_json = get_question(
            topic=session_state['topic'], 
            grade_level=session_state['grade_level'], 
            difficulty=session_state['proficiency_score']
        )
        
        # Display the question
        question_text = question_json['question']
        options = question_json['options']
        correct_option = question_json['correct_option']
        
        st.write(f"Question: {question_text}")
        answer = st.radio("Select an option", options)
        
        if st.button("Submit Answer"):
            if answer == correct_option:
                st.success("Correct!")
                session_state.proficiency_score += 1
            else:
                st.error("Wrong!")
                st.write("Explanation: " + question_json['step_by_step'])
                
            # Save interaction in DB
            save_interaction(session_state['student_name'], question_text, answer, session_state.proficiency_score)
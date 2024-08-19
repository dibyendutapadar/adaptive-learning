import streamlit as st
from components import db_interactions
from components.llm_integration import get_question
from datetime import datetime
from components import proficiency
# proficiency_graph, question_handler, 
import sqlite3
import json
import time
import plotly.graph_objects as go
from components.agents import student_assessor
from components.tasks import question_creation_task
from crewai import Crew






session_defaults = {
    'interaction_id': None,
    'current_proficiency': 0.0,
    'desired_proficiency': 0.0,
    'proficiency_history': [],
    'bloom_history': [],
    'session_id': str(datetime.now().timestamp()),
    'created_id': None,
    'student_name': None,
    'question': None,
    'option_show': None,
    'selected_option': None,
    'student_name': None,
    'question_data':None,
    'topic': None,
    'grade_level': None,
    'correct_answer':None,
    'difficulty':None,
    'hints':None,
    'step_by_step':None,
    'go_to_question':False,
    'to_generate':False,
    'question_generated':False,

}

if 'session_id' not in st.session_state:
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Sidebar inputs

with st.sidebar.form("student_detail"):
    st.title("Student Information")
    st.session_state.student_name = st.text_input("Name", key='student_name_input')
    st.session_state.topic = st.text_input("What do you want to learn?", key='topic_inpur')
    st.session_state.grade_level = st.selectbox("Current Grade Level", options=list(range(4, 10)), key='grade_level_input')
    st.session_state.current_proficiency = st.slider("Rate your current proficiency (1-10)", 1, 10, key='proficiency_input')/10
    st.session_state.desired_proficiency = st.slider("Desired proficiency (1-10)", 1, 10, key='desired_proficiency_input')/10
    st.session_state.submit_clicked = st.form_submit_button("Submit")

       
# History page button
# if st.sidebar.button("View History"):
#     st.experimental_set_query_params(page='history')


    if st.session_state.student_name and st.session_state.topic and st.session_state.grade_level and st.session_state.current_proficiency < st.session_state.desired_proficiency and st.session_state.submit_clicked:
        db_interactions.init_db() 
        session_id = st.session_state.session_id if 'session_id' in st.session_state else str(datetime.now().timestamp())
        st.session_state.proficiency_history.append(st.session_state.current_proficiency)
        st.session_state.session_id = session_id

        db_interactions.create_user(
            session_id=session_id,
            user_name=st.session_state.student_name,
            grade_level=st.session_state.grade_level,
            topic=st.session_state.topic,
            proficiency_input=st.session_state.current_proficiency,
            desired_proficiency=st.session_state.desired_proficiency
            )
        st.session_state.go_to_question = True
        st.session_state.to_generate = True

        



if st.session_state.current_proficiency < st.session_state.desired_proficiency:
    st.session_state.answered=False
    if st.session_state.proficiency_history:
        fig = go.Figure()
    # Add a trace for the proficiency history
        fig.add_trace(go.Scatter(
        x=list(range(len(st.session_state.proficiency_history))),
        y=st.session_state.proficiency_history,
        mode='lines+markers',
        name='Proficiency'
        ))

    # Customize layout
        fig.update_layout(
        title='Proficiency History',
        xaxis_title='Question Index',
        yaxis_title='Proficiency Value',
        yaxis=dict(range=[0, 1]) 
        )

    # Display the plot
        st.plotly_chart(fig)


if(st.session_state.to_generate==True and st.session_state.question_data==None and st.session_state.question_generated == False):
    st.session_state.question_data= get_question(st.session_state.grade_level, st.session_state.topic, st.session_state.current_proficiency)
    st.session_state.to_generate=False
    st.session_state.question_generated=True
        # Extract the question and options
    st.session_state.question = st.session_state.question_data.question
    st.session_state.options = st.session_state.question_data.options
    st.session_state.correct_answer = st.session_state.question_data.correct_answer
    st.session_state.difficulty = st.session_state.question_data.difficulty
    st.session_state.blooms_taxonomy = st.session_state.question_data.blooms_taxonomy
    st.session_state.hints = st.session_state.question_data.correct_answer
    st.session_state.step_by_step = st.session_state.question_data.step_by_step



    st.session_state.option_show= [option for option in st.session_state.options]
    st.session_state.interaction_id=db_interactions.current_interaction_id()
    st.session_state.created_id=db_interactions.create_detail(st.session_state.interaction_id, st.session_state.question, st.session_state.options, answer=st.session_state.correct_answer, question_blooms_taxonomy=st.session_state.blooms_taxonomy, question_difficulty_level=st.session_state.difficulty, question_hints=st.session_state.hints, answer_steps=st.session_state.step_by_step, previous_proficiency=st.session_state.current_proficiency)
        
    st.session_state.question_data = None
    st.write(f"### {st.session_state.question}")
            # Store the selected option in a temporary variable
            # Display options with radio buttons and ensure the selection is stored in session state
    # st.session_state.selected_option = st.radio(
    #             "Choose your answer:",
    #             st.session_state.option_show,
    #             index=None,
    #             )
    # st.write("You selected:", st.session_state.selected_option)

    # if st.button("Check", key='student_answer_submit'):
    #      st.session_state.answered=True
        
         



if(st.session_state.question_generated==True):
    with st.form("Student Answer"):
        st.session_state.selected_option = st.radio(
                    "Choose your answer:",
                    st.session_state.option_show,
                    index=None,
                    )
        st.write("You selected:", st.session_state.selected_option)
        submitted = st.form_submit_button(label="Check")

        if submitted:
            is_correct = True if st.session_state.correct_answer == st.session_state.selected_option else False

            updated_proficiency = proficiency.update_proficiency(float(st.session_state.current_proficiency), float(st.session_state.difficulty), float(is_correct))

            st.session_state.proficiency_history.append(updated_proficiency)
            st.session_state.current_proficiency = updated_proficiency
                
                # Step 4: Update user_detail with is_correct and updated_proficiency
            db_interactions.update_user_detail(st.session_state.created_id, is_correct, updated_proficiency)

                # Display the result to the user
            if is_correct:
                    st.success("Correct answer!")
                    
            else:
                    st.error("Wrong answer!")
                    st.write("Correct Answer:",st.session_state.correct_answer)
                    st.write("### Steps to solve")
                    st.write(st.session_state.step_by_step)


            st.write("new proficiency:",st.session_state.current_proficiency)

                # time.sleep(3)

            progress_bar = st.progress(0)
            st.write("Updating Proficiency and getting next question...")
            for percent_complete in range(100):
                    time.sleep(0.03)  # Adjust the time to control the speed
                    progress_bar.progress(percent_complete + 1) 
            st.session_state.to_generate = True
            st.session_state.question_generated =  False
            st.rerun()        



     

         







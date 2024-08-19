from crewai import Task
from components.agents import student_assessor


question_creation_task = Task(
    description="""
        Based on the student's Grade, Topic and Current Proficiency {question_requirement_info} generate one question multiple choice question of a difficulty level 0.1 higher than the Current Proficiency on the same Topic of the same grade. 
        - Current Proficiency is a number between 0 to 1, with 1 being highest or 100% proficiency.
        - The question should have 4 options, correct answer, hint and steps to solve.
        - One of the options should be equal to the correct answer.
        - Avoid question that needs a reference to any image or diagram.
        - You have to generate only one question.
    """,
    agent=student_assessor,
    expected_output="""
    just one question and the response should be structured according this json format. You have to response just the json and nothing else, no other acoompanying text.
        [
            {
                question: <the question>,
                "options": [
                    {"option_number": 1, "option_text": "text"},
                    {"option_number": 2, "option_text": "text"},
                    {"option_number": 3, "option_text": "text"},
                    {"option_number": 4, "option_text": "text"}
                    ],
    "correct_answer": "the correct answer text",
    "difficulty": difficulty lavel of the question between 0 to 1 (provide as a decimal value rounded to one digit after the decimal point)
    "blooms_taxonomy": "bloom_taxonomy of the question",
    "hints": ["hint 1","hint2", "hint3"...],
    "step_by_step": ["step 1", "Step 2", "Step 3"...]
    }]
    """,
    Config ="""
    If there is a student history available, then you should not generate any question which is similar to a question student has already answered correctly
    student's Answer History :{student_history_verbose}
    """
)
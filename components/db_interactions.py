import sqlite3
from datetime import datetime
import json


def init_db():
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()

    # Create user table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_name TEXT,
            grade_level INTEGER,
            topic TEXT,
            proficiency_input INTEGER,
            desired_proficiency INTEGER,
            timestamp TEXT
        )
    ''')

    # Create user_detail table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            question TEXT,
            options TEXT,
            answer TEXT,
            is_correct INTEGER,
            question_blooms_taxonomy TEXT,
            question_difficulty_level INTEGER,
            question_hints TEXT,
            answer_steps TEXT,
            previous_proficiency INTEGER,
            updated_proficiency INTEGER,
            timestamp TEXT,
            FOREIGN KEY (interaction_id) REFERENCES user(interaction_id)
        )
    ''')

    conn.commit()
    conn.close()

def create_user(session_id, user_name, grade_level, topic, proficiency_input, desired_proficiency):
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('''
        INSERT INTO user (session_id, user_name, grade_level, topic, proficiency_input, desired_proficiency, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, user_name, grade_level, topic, proficiency_input, desired_proficiency, timestamp))
    
    created_id = c.lastrowid

    conn.commit()
    conn.close()

    return created_id

def create_user_detail(interaction_id, question, options, answer, is_correct, question_bloom_level, question_difficulty_level, previous_proficiency, updated_proficiency):
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('''
        INSERT INTO user_detail (interaction_id, question, options, answer, is_correct, question_bloom_level, question_difficulty_level, previous_proficiency, updated_proficiency, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (interaction_id, question, options, answer, is_correct, question_bloom_level, question_difficulty_level, previous_proficiency, updated_proficiency, timestamp))
    
    conn.commit()
    conn.close()

def read_user(session_id):
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user WHERE session_id = ?', (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def read_user_detail(interaction_id):
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()
    c.execute('SELECT * FROM user_detail WHERE interaction_id = ?', (interaction_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def read_student_history(session_id):
    """
    Fetch the student's question history from the user_detail table for a given session_id.
    """
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()
    c.execute('''
        SELECT question, question_difficulty_level, is_correct, options
        FROM user_detail
        INNER JOIN user ON user.interaction_id = user_detail.interaction_id
        WHERE user.session_id = ?
    ''', (session_id,))
    rows = c.fetchall()
    conn.close()

    history_list = [
        {
            "question": row[0],
            "difficulty": row[1],
            "is_correct": row[2],
        }
        for row in rows
    ]

    return history_list


def create_detail(interaction_id, question, options, answer, question_blooms_taxonomy, question_difficulty_level, question_hints, answer_steps, previous_proficiency):
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()

    # Convert lists to JSON format (assuming hints and steps are lists)
    options_json = json.dumps(options)
    hints_json = json.dumps(question_hints)
    steps_json = json.dumps(answer_steps)
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert the new row into the user_detail table
    c.execute('''
        INSERT INTO user_detail (
            interaction_id, question, options, answer, question_blooms_taxonomy, 
            question_difficulty_level, question_hints, answer_steps, previous_proficiency, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        interaction_id, question, options_json, answer, question_blooms_taxonomy, 
        question_difficulty_level, hints_json, steps_json, previous_proficiency, timestamp
    ))
    # Get the id of the newly inserted row
    created_id = c.lastrowid

    conn.commit()
    conn.close()

    return created_id

def current_interaction_id():
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()

    # Fetch the last interaction_id from the user table
    c.execute('SELECT interaction_id FROM user ORDER BY interaction_id DESC LIMIT 1')
    result = c.fetchone()
    
    conn.close()

    # Return the interaction_id as an integer if available, otherwise return None
    if result:
        return int(result[0])
    else:
        return None
    
def get_user_detail_by_id(detail_id):
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()
    
    # Query to fetch answer and difficulty from user_detail by id
    c.execute('''
        SELECT answer, question_difficulty_level,answer_steps
        FROM user_detail 
        WHERE id = ?
    ''', (detail_id,))
    
    result = c.fetchone()
    conn.close()
    
    # Return the result as a tuple
    return result

def update_user_detail(detail_id, is_correct, updated_proficiency):
    conn = sqlite3.connect('data/students.db')
    c = conn.cursor()
    
    # Update the is_correct and updated_proficiency fields
    c.execute('''
        UPDATE user_detail 
        SET is_correct = ?, updated_proficiency = ? 
        WHERE id = ?
    ''', (is_correct, updated_proficiency, detail_id))
    
    conn.commit()
    conn.close()


def update_proficiency(current_proficiency, difficulty, is_correct):
    if is_correct:
        updated_proficiency = current_proficiency + (1 - current_proficiency) * difficulty * 0.4
    else:
        updated_proficiency = max(current_proficiency - (1 - current_proficiency) * difficulty * 0.3,0)
    return updated_proficiency
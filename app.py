import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="AI Answer Evaluator", layout="wide")
st.title("AI Answer Evaluation System - 20 Questions")

@st.cache_data
def load_rubrics():
    return pd.read_csv("dataset/rubrics.csv")

def evaluate_answer(student_ans, q_id, rubric_df):
    student_lower = student_ans.lower().strip()
    
    q_rubrics = rubric_df[rubric_df['question_id'] == q_id]
    max_score = q_rubrics['marks'].sum() 
    
    score = 0
    justifications = []
    awarded_key_points = [] # Oru key_point ku rendu vaati mark poda kudathu
    
    # Special negative rules for Q4 and Q5 only
    if q_id == 4:
        if 'unlabel' in student_lower or 'unsupervised' in student_lower:
            return 0, max_score, ["❌ Wrong! Supervised Learning uses LABELED data, not unlabeled data."]
    
    if q_id == 5:
        if 'labeled' in student_lower or 'labelled' in student_lower or 'supervised' in student_lower:
            return 0, max_score, ["❌ Wrong! Unsupervised Learning uses UNLABELED data, not labeled data."]

    # Check every key_point from CSV for this question
    for index, row in q_rubrics.iterrows():
        key_point = str(row['key_point']).lower()
        marks = row['marks']
        
        # Skip if already awarded marks for this key_point
        if key_point in awarded_key_points:
            continue
            
        # Remove common words and split key_point into important words
        key_point_clean = re.sub(r'\b(of|a|an|the|to|in|is|and|for|with|like)\b', '', key_point)
        key_words = key_point_clean.split()
        
        # If any important word from key_point is in student answer, give marks
        for word in key_words:
            if len(word) > 3 and word in student_lower:
                score += marks
                justifications.append(f"✅ {marks} marks: Matched key point '{row['key_point']}'")
                awarded_key_points.append(key_point) # Mark as awarded
                break # Move to next key_point

    if score == 0:
        justifications.append("❌ No matching keywords found from the rubric")
         
    return score, max_score, justifications

    # Check every key_point from CSV for this question
    for index, row in q_rubrics.iterrows():
        key_point = str(row['key_point']).lower()
        marks = row['marks']
        
        # Remove common words and split key_point into important words
        key_point_clean = re.sub(r'\b(of|a|an|the|to|in|is|and|for|with)\b', '', key_point)
        key_words = key_point_clean.split()
        
        # If any important word from key_point is in student answer, give marks
        for word in key_words:
            if len(word) > 2 and word in student_lower:
                score += marks
                justifications.append(f"✅ {marks} marks: Matched key point '{row['key_point']}'")
                break

    if score == 0:
        justifications.append("❌ No matching keywords found from the rubric")
         
    return score, max_score, justifications

try:
    rubrics_df = load_rubrics()
    unique_questions = rubrics_df.drop_duplicates(subset=['question_id'])
except FileNotFoundError:
    st.error("Error: dataset/rubrics.csv file not found. Check the file path.")
    st.stop()

for index, row in unique_questions.iterrows():
    q_id = int(row['question_id'])
    topic = row['question']
    marks = rubrics_df[rubrics_df['question_id'] == q_id]['marks'].sum()
    
    st.subheader(f"Question {q_id}: {topic} [{marks} Marks]")
    answer = st.text_area(f"Your Answer for Q{q_id}", key=f"q{q_id}", height=100)
    
    if st.button(f"Evaluate Q{q_id}", key=f"btn_{q_id}"):
        if answer:
            score, max_score, details = evaluate_answer(answer, q_id, rubrics_df)
            st.metric("Score", f"{score}/{max_score}")
            with st.expander("View Justification"):
                for detail in details:
                    if "❌" in detail:
                        st.error(detail)
                    else:
                        st.success(detail)
        else:
            st.warning(f"Please enter an answer for Q{q_id}")
    
    st.divider()

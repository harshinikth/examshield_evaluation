import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Answer Evaluator", layout="wide")
st.title("AI Answer Evaluation System - 20 Questions")

@st.cache_data
def load_rubrics():
    return pd.read_csv("dataset/rubrics.csv")

def evaluate_answer(student_ans, q_id, rubric_df):
    student_lower = student_ans.lower().strip()
    words = student_lower.split()
    
    q_rubrics = rubric_df[rubric_df['question_id'] == q_id]
    max_score = q_rubrics['marks'].sum() 
    
    score = 0
    justifications = []
    
    if q_id == 4:
        if 'unlabel' in student_lower or 'unsupervised' in student_lower:
            return 0, max_score, ["❌ Wrong! Supervised Learning uses LABELED data, not unlabeled data."]
    
    if q_id == 5:
        if 'labeled' in words or 'labelled' in words or 'supervised' in words:
            return 0, max_score, ["❌ Wrong! Unsupervised Learning uses UNLABELED data, not labeled data."]

    if q_id == 4 and 'labeled' in words:
        score = 5
        justifications.append("✅ Correctly mentioned 'labeled data'")
    
    elif q_id == 5 and 'unlabeled' in words:
        score = 5
        justifications.append("✅ Correctly mentioned 'unlabeled data'")
    
    elif q_id == 1 and 'simulation' in student_lower:
        score = 5
        justifications.append("✅ Correctly mentioned 'simulation'")
        
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

import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="AI Answer Evaluator", layout="wide")
st.title("AI Answer Evaluation System")

# Load rubrics file
@st.cache_data
def load_rubrics():
    return pd.read_csv("rubrics.csv")

# Main evaluation function
def evaluate_answer(student_ans, q_id):
    student_lower = student_ans.lower().strip()
    words = student_lower.split()  # Split into individual words to avoid substring issues
    max_score = 5
    
    # NEGATIVE KEYWORD RULES - These check for opposite concepts first
    
    # RULE 1: Question 4 - Supervised Learning
    if q_id == 4:
        if 'unlabel' in student_lower or 'unsupervised' in student_lower or 'without' in student_lower:
            return 0, max_score, ["❌ Wrong! Supervised Learning uses LABELED data, not unlabeled data."]
    
    # RULE 2: Question 5 - Unsupervised Learning  
    if q_id == 5:
        if 'labeled' in words or 'labelled' in words or 'supervised' in words:
            return 0, max_score, ["❌ Wrong! Unsupervised Learning uses UNLABELED data, not labeled data."]
    
    # POSITIVE SCORING LOGIC
    score = 0
    justifications = []
    
    # Question 4: Supervised Learning scoring
    if q_id == 4:
        if 'labeled' in words or 'labeled' in words:
            score = 5
            justifications.append("✅ Correctly mentioned that Supervised Learning uses labeled data")
        else:
            justifications.append("❌ Missing key concept: labeled data")
    
    # Question 5: Unsupervised Learning scoring  
    if q_id == 5:
        if 'unlabeled' in words or 'unlabeled' in words:
            score = 5
            justifications.append("✅ Correctly mentioned that Unsupervised Learning uses unlabeled data")
        else:
            justifications.append("❌ Missing key concept: unlabeled data")
    
    # Add more questions here if needed using elif q_id == 6, etc.
            
    return score, max_score, justifications

# Load rubric data
try:
    rubrics_df = load_rubrics()
except FileNotFoundError:
    st.error("Error: rubrics.csv file not found. Please make sure it exists in your repo.")
    st.stop()

# Display Question 4
st.subheader("Question 4: Explain Supervised Learning [5 Marks]")
q4_answer = st.text_area("Your Answer for Q4", key="q4")

if st.button("Evaluate Q4"):
    if q4_answer:
        score, max_score, details = evaluate_answer(q4_answer, 4)
        st.metric("Score", f"{score}/{max_score}")
        
        with st.expander("View Justification"):
            for detail in details:
                if "❌" in detail:
                    st.error(detail)
                else:
                    st.success(detail)
    else:
        st.warning("Please enter an answer for Q4")

# Display Question 5
st.subheader("Question 5: Explain Unsupervised Learning [5 Marks]")
q5_answer = st.text_area("Your Answer for Q5", key="q5")

if st.button("Evaluate Q5"):
    if q5_answer:
        score, max_score, details = evaluate_answer(q5_answer, 5)
        st.metric("Score", f"{score}/{max_score}")
        
        with st.expander("View Justification"):
            for detail in details:
                if "❌" in detail:
                    st.error(detail)
                else:
                    st.success(detail)
    else:
        st.warning("Please enter an answer for Q5")

# Display Question 6 - Add your own logic
st.subheader("Question 6: What is Reinforcement Learning? [5 Marks]")
q6_answer = st.text_area("Your Answer for Q6", key="q6")

if st.button("Evaluate Q6"):
    st.info("Evaluation logic for Q6 not implemented yet")

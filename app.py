import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="AI Answer Evaluator", layout="wide")
st.title("AI Answer Evaluation System - 20 Questions")

# Load rubrics from CSV
@st.cache_data
def load_rubrics():
    return pd.read_csv("rubrics.csv")

# Main evaluation function with logic for all 20 questions
def evaluate_answer(student_ans, q_id):
    student_lower = student_ans.lower().strip()
    words = student_lower.split()
    max_score = 5
    score = 0
    justifications = []
    
    # NEGATIVE KEYWORD RULES - For specific questions
    if q_id == 4:  # Supervised Learning
        if 'unlabel' in student_lower or 'unsupervised' in student_lower:
            return 0, max_score, ["❌ Wrong! Supervised Learning uses LABELED data, not unlabeled data."]
    
    if q_id == 5:  # Unsupervised Learning
        if 'labeled' in words or 'labelled' in words or 'supervised' in words:
            return 0, max_score, ["❌ Wrong! Unsupervised Learning uses UNLABELED data, not labeled data."]
    
    # POSITIVE SCORING LOGIC FOR EACH QUESTION
    # Add your keyword logic for each q_id here
    
    if q_id == 1:  # What is AI?
        if 'intelligence' in words or 'machine' in words or 'human' in words:
            score = 5
            justifications.append("✅ Correctly mentioned key AI concepts")
            
    elif q_id == 2:  # Define Machine Learning
        if 'data' in words and 'learn' in words:
            score = 5
            justifications.append("✅ Correctly mentioned learning from data")
            
    elif q_id == 3:  # Neural Networks
        if 'neuron' in words or 'layer' in words or 'brain' in words:
            score = 5
            justifications.append("✅ Correctly mentioned neurons/layers")
            
    elif q_id == 4:  # Supervised Learning
        if 'labeled' in words or 'labelled' in words:
            score = 5
            justifications.append("✅ Correctly mentioned labeled data")
            
    elif q_id == 5:  # Unsupervised Learning
        if 'unlabeled' in words or 'unlabelled' in words:
            score = 5
            justifications.append("✅ Correctly mentioned unlabeled data")
            
    elif q_id == 6:  # Reinforcement Learning
        if 'reward' in words or 'agent' in words or 'environment' in words:
            score = 5
            justifications.append("✅ Correctly mentioned reward/agent concept")
            
    # Add elif blocks for q_id 7 to 20 here with your own keywords
    # Example:
    # elif q_id == 7:
    #     if 'deep' in words and 'layer' in words:
    #         score = 5
    #         justifications.append("✅ Correctly mentioned deep layers")
    
    # Default justification if no score
    if score == 0:
        justifications.append("❌ No matching keywords found or incorrect concept")
         
    return score, max_score, justifications

# Load all questions from CSV
try:
    rubrics_df = load_rubrics()
except FileNotFoundError:
    st.error("Error: rubrics.csv file not found. Please create it in your repo root.")
    st.stop()

# Loop through all 20 questions and display them
for index, row in rubrics_df.iterrows():
    q_id = int(row['question_id'])
    topic = row['topic']
    marks = int(row['marks'])
    
    st.subheader(f"Question {q_id}: {topic} [{marks} Marks]")
    answer = st.text_area(f"Your Answer for Q{q_id}", key=f"q{q_id}", height=100)
    
    if st.button(f"Evaluate Q{q_id}", key=f"btn_{q_id}"):
        if answer:
            score, max_score, details = evaluate_answer(answer, q_id)
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

# Total score calculation
st.sidebar.header("Total Score")
if st.sidebar.button("Calculate Total Score"):
    total = 0
    for i in range(1, 21):
        if f"q{i}" in st.session_state and st.session_state[f"q{i}"]:
            score, _, _ = evaluate_answer(st.session_state[f"q{i}"], i)
            total += score
    st.sidebar.metric("Total", f"{total}/100")

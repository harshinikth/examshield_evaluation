import streamlit as st

# Page configuration
st.set_page_config(page_title="AI Answer Evaluator", layout="wide")
st.title("AI Answer Evaluation System")

# Main evaluation function
def evaluate_answer(student_ans, q_id):
    student_lower = student_ans.lower().strip()
    words = student_lower.split()  # Split into words to avoid 'labeled' vs 'unlabeled' bug
    max_score = 5
    
    # NEGATIVE KEYWORD RULES - Check for opposite concepts first
    if q_id == 4:  # Supervised Learning
        if 'unlabel' in student_lower or 'unsupervised' in student_lower or 'without' in student_lower:
            return 0, max_score, ["❌ Wrong! Supervised Learning uses LABELED data, not unlabeled data."]
    
    if q_id == 5:  # Unsupervised Learning
        if 'labeled' in words or 'labelled' in words or 'supervised' in words:
            return 0, max_score, ["❌ Wrong! Unsupervised Learning uses UNLABELED data, not labeled data."]
    
    # POSITIVE SCORING LOGIC
    score = 0
    justifications = []
    
    # Question 4: Supervised Learning
    if q_id == 4:
        if 'labeled' in words or 'labelled' in words:
            score = 5
            justifications.append("✅ Correctly mentioned that Supervised Learning uses labeled data")
        else:
            justifications.append("❌ Missing key concept: labeled data")
    
    # Question 5: Unsupervised Learning
    if q_id == 5:
        if 'unlabeled' in words or 'unlabelled' in words:
            score = 5
            justifications.append("✅ Correctly mentioned that Unsupervised Learning uses unlabeled data")
        else:
            justifications.append("❌ Missing key concept: unlabeled data")
            
    return score, max_score, justifications

# Question 4 UI
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

# Question 5 UI
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

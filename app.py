import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch

st.set_page_config(page_title="ExamShield", layout="wide")
st.title("ExamShield: NLP Subjective Answer Evaluator 🧠")

# Cache model so it loads only once
@st.cache_resource
def load_bert_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_bert_model()

# Load rubrics
@st.cache_data
def load_rubrics():
    return pd.read_csv("dataset/rubrics.csv")

rubrics_df = load_rubrics()

st.header("Student Answer Evaluation")

questions = rubrics_df['question'].unique()
selected_q = st.selectbox("Select Question", questions)

student_answer = st.text_area("Enter Student Answer:", height=150)

if st.button("Evaluate Answer"):
    if student_answer.strip() == "":
        st.warning("Please enter student answer")
    else:
        # Filter rubrics for selected question
        q_rubrics = rubrics_df[rubrics_df['question'] == selected_q]
        
        st.subheader("Evaluation Breakdown")
        total_marks = 0
        max_marks = q_rubrics['marks'].sum()
        feedback = []
        
        student_embedding = model.encode(student_answer, convert_to_tensor=True)
        
        for _, row in q_rubrics.iterrows():
            key_point = row['key_point']
            marks = row['marks']
            
            # Semantic similarity between key_point and student answer
            key_embedding = model.encode(key_point, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(student_embedding, key_embedding).item()
            
            # Threshold: if similarity > 0.5, award marks
            if similarity > 0.5:
                total_marks += marks
                feedback.append(f"✅ **{key_point}** → {marks}/{marks} marks | Similarity: {similarity:.2f}")
            else:
                feedback.append(f"❌ **{key_point}** → 0/{marks} marks | Similarity: {similarity:.2f}")
        
        # Final Score
        st.metric("Final Score", f"{total_marks} / {max_marks}")
        
        # Justification
        st.subheader("Justification per Rubric Point")
        for f in feedback:
            st.markdown(f)
            
        # Percentage
        percentage = (total_marks / max_marks) * 100
        if percentage >= 80:
            st.success(f"Excellent! {percentage:.1f}%")
        elif percentage >= 50:
            st.info(f"Good attempt. {percentage:.1f}%")
        else:
            st.error(f"Needs improvement. {percentage:.1f}%")

import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Page config - First line ah irukanum
st.set_page_config(page_title="ExamShield", page_icon="📝", layout="wide")

def get_marks_feedback(score):
    if score >= 80:
        return 5, "Excellent Answer"
    elif score >= 60:
        return 4, "Good Answer"
    elif score >= 40:
        return 3, "Average Answer"
    else:
        return 1, "Needs Improvement"

# Title
st.title("ExamShield - Auto Answer Evaluation 📝")
st.markdown("---")

# Load model with spinner
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

with st.spinner("Loading AI model... konjam wait pannu 🤖"):
    model = load_model()
st.success("Model loaded successfully!")

# Load data
model_df = pd.read_csv('dataset/model_answers.csv')

# UI
st.subheader("Evaluate Your Answer")

question_list = model_df['question'].tolist()
selected_question = st.selectbox("Select Question:", question_list)
student_answer = st.text_area("Enter Your Answer:", height=150)

if st.button("Evaluate Answer", type="primary"):
    if student_answer.strip() == "":
        st.warning("Answer ah type pannu da!")
    else:
        # Get model answer
        model_answer = model_df[model_df['question'] == selected_question]['model_answer'].values[0]
        
        # Calculate similarity
        with st.spinner("Evaluating..."):
            embeddings = model.encode([model_answer, student_answer])
            sim_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0] * 100
            marks, feedback = get_marks_feedback(sim_score)
        
        # Show results
        st.markdown("---")
        st.subheader("Results:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Similarity Score", f"{round(sim_score,2)}%")
        with col2:
            st.metric("Marks", f"{marks}/5")
        with col3:
            if marks >= 4:
                st.success(f"**{feedback}**")
            elif marks >= 3:
                st.info(f"**{feedback}**")
            else:
                st.error(f"**{feedback}**")
        
        with st.expander("See Model Answer"):
            st.write(model_answer)

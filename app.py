import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_data
def load_rubrics():
    return pd.read_csv("dataset/rubrics.csv")

model = load_model()
rubrics = load_rubrics()

st.set_page_config(page_title="ExamShield", layout="wide")
st.title("EXAMSHIELD: Full Paper NLP Evaluator")
st.write("Enter answers for all questions. Get auto marking + justification.")

def evaluate_answer(student_ans, q_id):
    q_rubric = rubrics[rubrics['question_id'] == q_id]
    total_score = 0
    max_score = q_rubric['marks'].sum()
    details = []

    if not student_ans.strip():
        return 0, max_score, ["No answer provided"]

    for _, row in q_rubric.iterrows():
        emb1 = model.encode(student_ans, convert_to_tensor=True)
        emb2 = model.encode(row['key_point'], convert_to_tensor=True)
        sim = util.pytorch_cos_sim(emb1, emb2).item()

        if sim > 0.5:
            total_score += row['marks']
            details.append(f"✅ {row['key_point']} | {row['marks']}/{row['marks']} | Sim: {sim:.2f}")
        else:
            details.append(f"❌ {row['key_point']} | 0/{row['marks']} | Sim: {sim:.2f}")

    return total_score, max_score, details

# Main UI
grand_total = 0
grand_max = 0
all_scores = []

for q_id in sorted(rubrics['question_id'].unique()):
    q_text = rubrics[rubrics['question_id']==q_id]['question'].iloc[0]
    max_marks = rubrics[rubrics['question_id']==q_id]['marks'].sum()

    st.subheader(f"Question {q_id}: {q_text} [{max_marks} Marks]")
    student_ans = st.text_area(f"Your Answer for Q{q_id}", key=f"q{q_id}", height=100)

    col1, col2 = st.columns([1,5])
    with col1:
        if st.button(f"Evaluate Q{q_id}", key=f"btn{q_id}"):
            score, max_m, detail = evaluate_answer(student_ans, q_id)
            st.session_state[f"score_{q_id}"] = score
            st.session_state[f"detail_{q_id}"] = detail

    if f"score_{q_id}" in st.session_state:
        score = st.session_state[f"score_{q_id}"]
        detail = st.session_state[f"detail_{q_id}"]
        st.success(f"Score: {score}/{max_marks}")
        with st.expander("View Justification"):
            for d in detail: st.write(d)

    grand_max += max_marks
    if f"score_{q_id}" in st.session_state:
        grand_total += st.session_state[f"score_{q_id}"]
        all_scores.append({"Q": q_id, "Score": st.session_state[f"score_{q_id}"], "Max": max_marks})

st.markdown("---")
if all_scores:
    st.header(f"Final Report: {grand_total} / {grand_max}")
    st.dataframe(pd.DataFrame(all_scores))
    st.progress(grand_total/grand_max)

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
st.title("EXAMSHIELD: Semantic Answer Evaluator")
st.write("Meaning purunja marks. Opposite concept sonna 0.")

def evaluate_answer(student_ans, q_id):
    q_rubric = rubrics[rubrics['question_id'] == q_id]
    max_score = q_rubric['marks'].sum()
    student_lower = student_ans.lower().strip()

    if not student_lower:
        return 0, max_score, ["❌ No answer provided"]

    # RULE 1: NEGATIVE KEYWORD CHECK - Opposite concept
    if q_id == 4: # Supervised Learning
        if any(word in student_lower for word in ['unlabel', 'unsupervised', 'without label']):
            return 0, max_score, ["❌ Wrong! Supervised Learning uses LABELED data, not unlabeled data."]

    if q_id == 5: # Unsupervised Learning
        if 'label' in student_lower and 'unlabel' not in student_lower:
            return 0, max_score, ["❌ Wrong! Unsupervised Learning uses UNLABELED data, not labeled data."]

    # RULE 2: MANDATORY KEYWORD CHECK - List questions
    if q_id == 3: # List 3 types of ML
        required_keywords = ['supervised', 'unsupervised', 'reinforcement']
        found = sum(1 for kw in required_keywords if kw in student_lower)
        if found < 2:
            return 0, max_score, [f"❌ Question asks to LIST 3 types. You mentioned {found}/3. Write: Supervised, Unsupervised, Reinforcement Learning."]

    # RULE 3: SEMANTIC EVALUATION WITH HYBRID SCORING
    total_score = 0
    details = []

    for _, row in q_rubric.iterrows():
        emb1 = model.encode(student_ans, convert_to_tensor=True)
        emb2 = model.encode(row['key_point'], convert_to_tensor=True)
        sim = util.pytorch_cos_sim(emb1, emb2).item()

        if sim >= 0.45: # Full match
            total_score += row['marks']
            details.append(f"✅ {row['key_point']} | {row['marks']}/{row['marks']} | Sim: {sim:.2f} - Full Match")
        elif sim >= 0.35: # Partial match
            partial = max(1, round(row['marks'] * 0.5))
            total_score += partial
            details.append(f"🟡 {row['key_point']} | {partial}/{row['marks']} | Sim: {sim:.2f} - Partial Match")
        else: # No match
            details.append(f"❌ {row['key_point']} | 0/{row['marks']} | Sim: {sim:.2f} - No Match")

    return total_score, max_score, details

# MAIN UI
grand_total = 0
grand_max = 0
all_scores = []

st.info("Logic: >0.45 = Full marks | 0.35-0.45 = Half marks | Opposite/List wrong = 0 marks")

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
            st.session_state[f"max_{q_id}"] = max_m

    if f"score_{q_id}" in st.session_state:
        score = st.session_state[f"score_{q_id}"]
        detail = st.session_state[f"detail_{q_id}"]
        max_m = st.session_state[f"max_{q_id}"]

        if score == max_m:
            st.success(f"Score: {score}/{max_m} 🎯")
        elif score > 0:
            st.warning(f"Score: {score}/{max_m} ⚡")
        else:
            st.error(f"Score: {score}/{max_m} ❌")

        with st.expander("View Justification"):
            for d in detail: st.write(d)

    grand_max += max_marks
    if f"score_{q_id}" in st.session_state:
        grand_total += st.session_state[f"score_{q_id}"]
        all_scores.append({"Q": q_id, "Score": st.session_state[f"score_{q_id}"], "Max": max_marks})

st.markdown("---")
if all_scores:
    st.header(f"Final Report: {grand_total} / {grand_max}")
    st.dataframe(pd.DataFrame(all_scores), use_container_width=True)
    st.progress(grand_total/grand_max if grand_max > 0 else 0)

    percentage = (grand_total/grand_max)*100 if grand_max > 0 else 0
    if percentage >= 90:
        st.balloons()
        st.success(f"Excellent! {percentage:.1f}%")
    elif percentage >= 60:
        st.success(f"Good Work! {percentage:.1f}%")
    else:
        st.warning(f"Keep Practicing! {percentage:.1f}%")

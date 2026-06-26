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
    def evaluate_answer(student_ans, q_id):
    student_lower = student_ans.lower().strip()
    max_score = 5
    
    # RULE 1: NEGATIVE KEYWORD CHECK - Q4 ku mattum
    if q_id == 4:  # Supervised Learning
        if 'unlabel' in student_lower or 'unsupervised' in student_lower or 'without label' in student_lower:
            return 0, max_score, ["❌ Wrong! Supervised Learning uses LABELED data, not unlabeled data."]
    
    # RULE 2: NEGATIVE KEYWORD CHECK - Q5 ku mattum
    if q_id == 5:  # Unsupervised Learning
        if 'labeled' in student_lower or 'labelled' in student_lower or 'supervised' in student_lower:
            return 0, max_score, ["❌ Wrong! Unsupervised Learning uses UNLABELED data, not labeled data."]
    
    # Normal scoring logic idhuku keezha varum
    score = 0
    justifications = []
    
    # Un code la irukura keyword matching logic inge podu
    # Example:
    if 'labeled' in student_lower and q_id == 4:
        score += 5
        justifications.append("✅ Correctly mentioned labeled data")
    
    if 'unlabel' in student_lower and q_id == 5:
        score += 5
        justifications.append("✅ Correctly mentioned unlabeled data")
        
    return score, max_score, justifications
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

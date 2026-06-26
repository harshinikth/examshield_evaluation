import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def get_marks_feedback(score):
    if score >= 80:
        return 5, "Excellent Answer"
    elif score >= 60:
        return 4, "Good Answer"
    elif score >= 40:
        return 3, "Average Answer"
    else:
        return 1, "Needs Improvement"


print("Loading AI model... konjam wait pannu")
model = SentenceTransformer('all-MiniLM-L6-v2')


model_df = pd.read_csv('dataset/model_answers.csv')
student_df = pd.read_csv('dataset/student_answers.csv')

print("ExamShield – Auto Answer Evaluation")
print("=" * 40)


for index, row in student_df.iterrows():
    question = row['question']
    student_ans = row['student_answer']
    model_ans = model_df.loc[model_df['question'] == question, 'model_answer'].values[0]

    
    embeddings = model.encode([model_ans, student_ans])

   
    sim_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0] * 100

    
    marks, feedback = get_marks_feedback(sim_score)

    
    print(f"Question: {question}")
    print(f"Similarity Score: {round(sim_score,2)}%")
    print(f"Marks: {marks}/5")
    print(f"Feedback: {feedback}")
    print("-" * 40)
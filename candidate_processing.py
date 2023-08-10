import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Candidate:
    def __init__(self, name, job_description_match, cv_match):
        self.name = name
        self.job_description_match = job_description_match
        self.cv_match = cv_match

def generate_screening_questions(candidate):
    questions = []

    # Define weights for job description and CV match
    job_description_weight = 0.6
    cv_weight = 0.4

    # Assign importance scores based on weights
    job_description_importance = candidate.job_description_match * job_description_weight
    cv_importance = candidate.cv_match * cv_weight

    # Generate questions based on importance scores
    if job_description_importance >= 0.8:
        questions.append(f"{candidate.name}, can you provide specific examples of how you meet the key requirements in the job description?")

    if cv_importance >= 0.7:
        questions.append(f"{candidate.name}, I noticed you have experience with XYZ technology. Can you tell me about a challenging project you've worked on using that technology?")

    if job_description_importance < 0.5 and cv_importance < 0.5:
        questions.append(f"{candidate.name}, please provide more details about your relevant skills and experiences that align with the job requirements.")

    return questions


def calculate_similarity(job_desc1, job_desc2):
    vectorizer = CountVectorizer().fit_transform([job_desc1, job_desc2])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors[0].reshape(1, -1), vectors[1].reshape(1, -1))[0][0]

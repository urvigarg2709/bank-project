import requests
import os
import PyPDF2
import docx
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import mysql.connector
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

candidate_response = requests.get('http://127.0.0.1:5000/get_candidate_job_description')
candidate_job_desc = candidate_response.text

db = mysql.connector.connect(
    host="your_host",
    user="your_user",
    password="your_password",
    database="your_database"
)
cursor = db.cursor()

cursor.execute("SELECT Job_ID, Job_Description, Rating FROM jobs")
job_data = cursor.fetchall()
job_df = pd.DataFrame(job_data, columns=['Job_ID', 'Job_Description', 'Rating'])

db.close()
def calculate_similarity(job_desc1, job_desc2):
    vectorizer = CountVectorizer().fit_transform([job_desc1, job_desc2])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors[0].reshape(1, -1), vectors[1].reshape(1, -1))[0][0]


job_df['Similarity_Score'] = job_df['Job_Description'].apply(lambda x: calculate_similarity(x, candidate_job_desc))


ranked_jobs = job_df.sort_values(by='Similarity_Score', ascending=False)

closest_match = ranked_jobs.iloc[0]


threshold_similarity = 0.7

if closest_match['Similarity_Score'] >= threshold_similarity:
    print("Your job description closely matches this job:")
    print("Job Description:", closest_match['Job_Description'])
    print("Job ID:", closest_match['Job_ID'])
    print("Rating:", closest_match['Rating'])
else:
    print("Your job description does not closely match any of the available jobs.")
    print("We suggest the following job description based on the closest match:")
    print("Suggested Job Description:", closest_match['Job_Description'])
    print("Suggested Job ID:", closest_match['Job_ID'])
    print("Suggested Rating:", closest_match['Rating'])


    change_description = input("Would you like to change your job description? (yes/no): ").lower()
    if change_description == 'yes':
        candidate_job_desc = input("Please enter your updated job description: ")

# Function to extract text from PDF files
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

# Function to extract text from Word files
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Sample data - Replace this with your own dataset
cv_directory = '/content/'

# Get a list of all files in the directory with PDF or DOCX extensions
cv_files = [os.path.join(cv_directory, filename) for filename in os.listdir(cv_directory) if filename.lower().endswith(('.pdf', '.docx'))]

# Create a DataFrame with the file paths
data = {
    'CV_ID': list(range(1, len(cv_files) + 1)),
    'CV_Path': cv_files,
    'Overall_Rating': [0.0] * len(cv_files)  # Initialize with 0.0, you'll update this with the ranking
}
df = pd.DataFrame(data)

# Data Preprocessing and Feature Extraction using Count Vectorization
scaler = StandardScaler()
df['Education'] = [random.uniform(1, 5) for _ in range(len(df))]
df['Experience'] = [random.uniform(1, 5) for _ in range(len(df))]
df['Skills'] = [random.uniform(1, 5) for _ in range(len(df))]
df['Languages'] = [random.uniform(1, 5) for _ in range(len(df))]
df['Certifications'] = [random.uniform(1, 5) for _ in range(len(df))]
df[['Education', 'Experience', 'Skills', 'Languages', 'Certifications']] = scaler.fit_transform(
    df[['Education', 'Experience', 'Skills', 'Languages', 'Certifications']])
X_cv = df[['Education', 'Experience', 'Skills', 'Languages', 'Certifications']].values

# Scaling the features
scaler = StandardScaler()
X_cv = scaler.fit_transform(X_cv)
# Splitting data into features and target
y = df['Overall_Rating']

# Model training (Random Forest Regressor) for CV ranking
model_cv = RandomForestRegressor(n_estimators=100, random_state=42)
model_cv.fit(X_cv, y)

# Predict the ratings for the CVs
predictions_cv = model_cv.predict(X_cv)

# Update the Overall_Rating column with the CV rankings
df['Overall_Rating'] = predictions_cv

# Rank the CVs based on Overall_Rating in descending order
ranked_cvs = df.sort_values(by='Overall_Rating', ascending=True)

print("Ranked CVs:")
print(ranked_cvs)

shortlist_threshold = 4.0

# Filter the shortlisted candidates based on the threshold
shortlisted_candidates = df[df['Overall_Rating'] >= shortlist_threshold]

# Extract relevant details for further processing
for index, row in shortlisted_candidates.iterrows():
    cv_id = row['CV_ID']
    overall_rating = row['Overall_Rating']

    print(f"CV ID: {cv_id}")
    print(f"Predicted Overall Rating: {overall_rating}")
# Generate screening questions for each candidate
candidate = Candidate(row['Candidate_Name'], row['Job_Description_Match'], overall_rating)  # Replace with actual columns
questions = generate_screening_questions(candidate)
print(f"Screening questions for {candidate.name}:")
for question in questions:
    print(question)
    print()
# Email configuration
smtp_server = 'smtp.example.com'  # Replace with your SMTP server
smtp_port = 587  # Replace with the appropriate port
sender_email = 'your_email@example.com'
sender_password = 'your_password'
subject = 'Congratulations! You have been shortlisted.'

# Email body
email_body = """\
Hello {name},

Congratulations! We are pleased to inform you that your CV has been shortlisted based on our evaluation process.

Best regards,
Your Company
"""

# Loop through the shortlisted candidates and send emails
for index, candidate in shortlisted_candidates.iterrows():
    cv_path = candidate['CV_Path']
    candidate_name = os.path.splitext(os.path.basename(cv_path))[0]
    candidate_email = 'candidate_email@example.com'  # Replace with the candidate's email
    # Create the email message
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = candidate_email
message['Subject'] = subject
message.attach(MIMEText(email_body.format(name=candidate_name), 'plain'))

    # Connect to the SMTP server and send the email
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, candidate_email, message.as_string())

print(f"Email sent to {candidate_name} at {candidate_email}")

print("All emails sent successfully.")

from flask import Flask, render_template, request, redirect, url_for
import os
from flask_mail import Mail, Message
import json
import time
import cv2  # OpenCV for video recording
from candidate_processing import Candidate, generate_screening_questions, calculate_similarity
import mysql.connector
from flask import send_from_directory
import plotly.graph_objs as go

# Load configuration parameters from config.json
with open("config.json", "r") as c:
    params = json.load(c)["params"]

app = Flask(__name__)

cv_data=[]

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password'],
)
mail = Mail(app)

# Set the duration of the interview recording in seconds (60 seconds = 1 minute)
interview_duration = 60

# Function to record a video for the specified duration
def record_video(duration):
    cap = cv2.VideoCapture(0)  # Open the default camera (0)
    codec = cv2.VideoWriter_fourcc(*'XVID')
    output_file = 'interview_video.avi'
    out = cv2.VideoWriter(output_file, codec, 30, (640, 480))

    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return output_file

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/uploads', methods=['POST'])
def upload_file():
    if 'cv' not in request.files:
        return redirect(request.url)

    file = request.files['cv']
    candidate_name = request.form.get('candidate_name')  # Get the candidate's name
    candidate_email = request.form.get('candidate_email')  # Get the candidate's email
    candidate_position = request.form.get('candidate_position')  # Get the candidate's position
    
    cv_data.append({
            "name": candidate_name,
            "email": candidate_email,
            "position": candidate_position,
            "filename": file.filename,
        })

    if file.filename == '' or not all([candidate_name, candidate_email, candidate_position]):
        return redirect(request.url)

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        recorded_video = record_video(interview_duration)

        subject = "CV Upload Notification"
        sender_email = params['gmail-user']
        recipient_email = "example@gmail.com"  # Replace with the recipient's email
        message_body = "Your CV has been uploaded successfully."

        msg = Message(subject=subject,
                      sender=sender_email,
                      recipients=[recipient_email])
        msg.body = message_body
        mail.send(msg)

        # candidate = Candidate(candidate_name, job_description_match_score, cv_match_score)
        # questions = generate_screening_questions(candidate)

        # Add the uploaded CV data to the cv_data list
        # cv_data.append({
        #     "name": candidate_name,
        #     "email": candidate_email,
        #     "position": candidate_position,
        #     "filename": file.filename,
        # })

        # response = "<br>".join(questions)
        # return response
    return redirect(url_for('home'))

@app.route('/job')
def job():
    return render_template('job.html')

@app.route('/hr')
def hr():
    return render_template('hr.html')

@app.route('/pro')
def pro():
    return render_template('pro.html')

@app.route('/dashboard')
def dashboard():
    enrolled_candidates = len(cv_data)
    selected_candidates = 10  # Replace with the actual number of selected candidates
    not_selected_candidates = enrolled_candidates - selected_candidates

    enrollment_selection_data = [
        go.Bar(
            x=['Enrolled', 'Selected', 'Not Selected'],
            y=[enrolled_candidates, selected_candidates, not_selected_candidates],
            marker=dict(color=['blue', 'green', 'red'])
        )
    ]

    enrollment_selection_layout = go.Layout(
        title='Enrollment and Selection Status',
        xaxis=dict(title='Status'),
        yaxis=dict(title='Number of Candidates')
    )

    enrollment_selection_fig = go.Figure(data=enrollment_selection_data, layout=enrollment_selection_layout)
    enrollment_selection_graph = enrollment_selection_fig.to_html(full_html=False)

    return render_template('dashboard.html', cv_data=cv_data, enrollment_selection_graph=enrollment_selection_graph)


    # return render_template('dashboard.html', cv_data=cv_data)

@app.route('/view_cv/<filename>')
def view_cv(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)

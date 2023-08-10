from flask import Flask, render_template, request, redirect, url_for
import os
from flask_mail import Mail, Message
import json
import time
import cv2  # OpenCV for video recording

app = Flask(__name__)

# Load configuration parameters from config.json
with open("config.json", "r") as c:
    params = json.load(c)["params"]

# Configure Flask app for email
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password'],
)
mail = Mail(app)

# Configure Flask app for video upload
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'cv' not in request.files:
        return redirect(request.url)

    file = request.files['cv']

    if file.filename == '':
        return redirect(request.url)

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Record the video
        recorded_video = record_video(interview_duration)
        
        # Send email notification
        subject = "CV and Interview Video Upload Notification"
        sender_email = params['gmail-user']
        recipient_email = "example@gmail.com"  # Replace with the recipient's email
        message_body = "Your CV and interview video have been uploaded successfully."
        
        msg = Message(subject=subject,
                      sender=sender_email,
                      recipients=[recipient_email])
        msg.body = message_body
        mail.send(msg)
        
        return redirect(url_for('home'))
    
@app.route('/job')
def job():
    return render_template('job.html')

if __name__ == '__main__':
    app.run(debug=True)

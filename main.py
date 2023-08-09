from flask import Flask,render_template,request,redirect,url_for
import os
from flask_mail import Mail,Message
import json

with open("config.json","r") as c:
   params=json.load(c)["params"]

app=Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password'],
)
mail=Mail(app)

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
        
        subject = "CV Upload Notification"
        sender_email = params['gmail-user']
        recipient_email = "example@gmail.com"  # Replace with the recipient's email
        message_body = "Your CV has been uploaded successfully."
        
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
document.addEventListener('DOMContentLoaded', function () {
    const videoPreview = document.getElementById('video-preview');
    const startRecordingButton = document.getElementById('start-recording');
    const stopRecordingButton = document.getElementById('stop-recording');
    let mediaRecorder;
    let recordedChunks = [];

    // Access the camera and start video preview
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
            videoPreview.srcObject = stream;
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(recordedChunks, { type: 'video/webm' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'interview.webm';
                document.body.appendChild(a);
                a.click();
            };
        })
        .catch(error => console.error('Error accessing camera:', error));

    // Start recording
    startRecordingButton.addEventListener('click', () => {
        recordedChunks = [];
        mediaRecorder.start();
        startRecordingButton.disabled = true;
        stopRecordingButton.disabled = false;
    });

    // Stop recording
    stopRecordingButton.addEventListener('click', () => {
        mediaRecorder.stop();
        startRecordingButton.disabled = false;
        stopRecordingButton.disabled = true;
    });
});

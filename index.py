from flask import Flask, request, send_file
import cv2
import numpy as np
import pydub

app = Flask(__name__)

def brightness_to_intensity(brightness):
    return brightness / 255.0 * 100  # Scale to a reasonable range

@app.route('/upload', methods=['POST'])
def sonify_video():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']

    if file and file.filename.endswith(('.mp4', '.avi', '.mov')):
        # Save the file
        file.save('uploads/input_video.mp4')

        # Load the video
        cap = cv2.VideoCapture('uploads/input_video.mp4')

        # Initialize an array to store audio samples
        audio_samples = []

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            # Convert the frame to grayscale for simplicity
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Get the average brightness of the frame
            brightness = np.mean(gray_frame)
            intensity = brightness_to_intensity(brightness)

            # Store the intensity as an audio sample
            audio_samples.append(intensity)

        cap.release()

        # Convert the audio samples to a PyDub audio segment
        audio = pydub.AudioSegment(
            np.array(audio_samples, dtype=np.int16).tobytes(),
            frame_rate=44100,  # Adjust this to your desired frame rate
            sample_width=2,    # Adjust this to your desired sample width (in bytes)
            channels=1         # Mono audio for simplicity
        )

        # Export the audio to a file
        audio_path = 'uploads/output_audio.mp3'
        audio.export(audio_path, format='mp3')

        return send_file(audio_path, as_attachment=True)
    else:
            return "Invalid file format. Please upload a video file.", 400

if __name__ == '__main__':
     app.run(debug=True)
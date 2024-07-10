from flask import Flask, request, render_template_string, send_file
from gtts import gTTS
import os
import pdfplumber
import logging

# Initialize the Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Function to convert text to speech
def text_to_speech(text, language='en', filename='static/output.mp3'):
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(filename)
    return filename

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = ""
        if 'pdf' in request.files and request.files['pdf'].filename != '':
            pdf_file = request.files['pdf']
            pdf_path = os.path.join("uploads", pdf_file.filename)
            pdf_file.save(pdf_path)
            text = extract_text_from_pdf(pdf_path)
            logging.debug(f"Extracted text from PDF: {text[:100]}...")  # Log first 100 characters
        elif 'text' in request.form and request.form['text'].strip() != '':
            text = request.form['text'].strip()
            logging.debug(f"Received text input: {text[:100]}...")  # Log first 100 characters

        if text:
            audio_file = text_to_speech(text)
            logging.debug(f"Generated audio file: {audio_file}")
            return render_template_string(result_html, audio_file=audio_file)
    return render_template_string(index_html)

# Route to download the audio file
@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

# HTML for the main page
index_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JESAM IS THE BEST</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #282C34;
            color: #61AFEF;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            background-color: #1C2025;
            padding: 20px;
            border-radius: 10px;
        }
        textarea {
            width: 80%;
            height: 100px;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            border: none;
            font-size: 16px;
        }
        input[type="file"] {
            margin: 10px 0;
        }
        button {
            padding: 10px 20px;
            background-color: #98C379;
            border: none;
            border-radius: 5px;
            color: #282C34;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #61AFEF;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>JESAM IS THE BEST</h1>
        <form method="post" enctype="multipart/form-data">
            <textarea name="text" placeholder="Enter text here..."></textarea>
            <br>
            <input type="file" name="pdf">
            <br>
            <button type="submit">Convert to Speech</button>
        </form>
    </div>
</body>
</html>
'''

# HTML for the result page
result_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JESAM IS THE BEST - Result</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #282C34;
            color: #61AFEF;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            background-color: #1C2025;
            padding: 20px;
            border-radius: 10px;
        }
        a, audio {
            display: block;
            margin: 10px 0;
            color: #61AFEF;
        }
        button {
            padding: 10px 20px;
            background-color: #98C379;
            border: none;
            border-radius: 5px;
            color: #282C34;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #61AFEF;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Conversion Complete!</h1>
        <audio controls>
            <source src="{{ audio_file }}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        <br>
        <a href="{{ url_for('download_file', filename=audio_file) }}">Download Audio</a>
        <br>
        <a href="{{ url_for('index') }}">Convert Another</a>
    </div>
</body>
</html>
'''

# Ensure the uploads directory exists
if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)

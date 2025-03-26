from flask import Flask, render_template, request, jsonify, send_file
import os
from gtts import gTTS
from googletrans import Translator, LANGUAGES
import PyPDF2

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

translator = Translator()

# Ensure upload directory exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

def extract_text_from_file(file_path):
    """Extract text from TXT or PDF file"""
    text = ""
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    elif file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    return text.strip()

@app.route("/")
def index():
    return render_template("index.html", languages=LANGUAGES)

@app.route("/translate", methods=["POST"])
def translate():
    text = request.form.get("text", "")
    src_lang = request.form.get("source_language", "auto")  # Auto-detect source
    target_lang = request.form.get("target_language", "en")  # Default to English
    file = request.files.get("file")

    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        text = extract_text_from_file(file_path)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    translated_text = translator.translate(text, src=src_lang, dest=target_lang).text
    return jsonify({"translated_text": translated_text})

@app.route("/speak", methods=["POST"])
def speak():
    text = request.form.get("text", "")
    src_lang = request.form.get("source_language", "auto")
    target_lang = request.form.get("target_language", "en")
    file = request.files.get("file")

    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        text = extract_text_from_file(file_path)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    translated_text = translator.translate(text, src=src_lang, dest=target_lang).text

    tts = gTTS(text=translated_text, lang=target_lang)
    filename = "static/output.mp3"
    tts.save(filename)

    return send_file(filename, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True)

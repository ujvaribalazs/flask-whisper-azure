from flask import Flask, request, jsonify
from fuzzywuzzy import fuzz
from random import choice
from flask_cors import CORS
import whisper
import os
import subprocess

app = Flask(__name__) 
CORS(app)

sentences = [     
    "A nap süt az égen.",     
    "Az alma piros és édes.",     
    "A macska az asztal alatt alszik." 
]  

@app.route('/get_sentence', methods=['GET']) 
def get_sentence():     
    print("GET kérés érkezett a /get_sentence végpontra")
    sentence = choice(sentences)     
    return jsonify({"sentence": sentence})

def convert_audio(input_file, output_file):
    command = f'ffmpeg -i "{input_file}" -ar 16000 -ac 1 "{output_file}" -y'
    subprocess.call(command, shell=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("POST request received at /upload")

        if 'file' not in request.files or 'target_sentence' not in request.form:
            return jsonify({"error": "File and target sentence are required!"}), 400

        file = request.files['file']
        target_sentence = request.form['target_sentence']
        print(f"Target sentence: {target_sentence}")

        upload_folder = "/tmp/uploads/"
        os.makedirs(upload_folder, exist_ok=True)
        input_filename = os.path.join(upload_folder, "temp_audio.webm")
        output_filename = os.path.join(upload_folder, "temp_audio.wav")
        file.save(input_filename)
        print(f"File saved: {input_filename}")

        # Convert audio to WAV format
        print("Converting audio to WAV format...")
        convert_audio(input_filename, output_filename)
        print(f"Audio converted: {output_filename}")

        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("Model loaded, starting transcription...")

        try:
            result = model.transcribe(output_filename, language="hu", task="transcribe")
            recognized_text = result['text'].strip()
            print(f"Raw recognized text: {recognized_text}")

            # Simple text cleaning
            recognized_text = " ".join(recognized_text.split())  # Remove extra spaces
            print(f"Cleaned recognized text: {recognized_text}")

            similarity = fuzz.ratio(recognized_text.lower(), target_sentence.lower())
            print(f"Similarity: {similarity}%")

            return jsonify({
                "recognized_text": recognized_text,
                "target_sentence": target_sentence,
                "similarity": similarity
            })
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            raise

    except Exception as e:
        print(f"Detailed error at /upload endpoint: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": f"Processing error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    print("Server starting at http://localhost:5000...")
    app.run(debug=True, port=5000)

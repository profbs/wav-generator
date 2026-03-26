import os
import tempfile
import uuid

import numpy as np
from flask import Flask, jsonify, render_template, request, send_file
from pydub import AudioSegment
from pydub.generators import Sine, Triangle
from werkzeug.utils import secure_filename

app = Flask(__name__)


def generate_rhythm_pattern(duration_ms, bpm=130):
    beat_duration = 60000 / bpm
    rhythm = AudioSegment.silent(duration=duration_ms).set_channels(2)
    for i in range(int(duration_ms / beat_duration)):
        if i % 4 == 0:
            kick = Sine(50).to_audio_segment(duration=beat_duration * 0.5, volume=-6).set_channels(2)
            rhythm = rhythm.overlay(kick, position=int(i * beat_duration))
        elif i % 4 == 2:
            snare = Sine(200).to_audio_segment(duration=beat_duration * 0.3, volume=-6).set_channels(2)
            rhythm = rhythm.overlay(snare, position=int(i * beat_duration))
    return rhythm


def generate_melody_pattern(duration_ms, bpm=130):
    beat_duration = 60000 / bpm
    melody = AudioSegment.silent(duration=duration_ms).set_channels(2)
    notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    num_beats = int(duration_ms / beat_duration)
    for i in range(num_beats):
        frequency = np.random.choice(notes)
        duration = beat_duration * np.random.choice([0.5, 1, 1.5])
        note = Triangle(frequency).to_audio_segment(duration=duration * 0.8, volume=-9).set_channels(2)
        melody = melody.overlay(note, position=int(i * beat_duration))
    return melody


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        base_filename = request.form.get("base_filename", "sample_audio").strip() or "sample_audio"
        num_files = int(request.form.get("num_files", 1))
        first_duration = int(request.form.get("first_duration", 10))
        duration_increment = int(request.form.get("duration_increment", 1000))

        if num_files <= 0 or first_duration <= 0:
            return jsonify({"error": "Number of tracks and duration must be positive."}), 400
        if num_files > 20:
            return jsonify({"error": "Maximum 20 tracks per batch."}), 400

        session_id = str(uuid.uuid4())
        temp_dir = os.path.join(tempfile.gettempdir(), "wav_gen", session_id)
        os.makedirs(temp_dir, exist_ok=True)

        files = []
        for i in range(num_files):
            duration_ms = first_duration * 1000 + i * duration_increment
            rhythm = generate_rhythm_pattern(duration_ms=duration_ms)
            melody = generate_melody_pattern(duration_ms=duration_ms)
            combined = rhythm.overlay(melody)
            filename = secure_filename(f"{base_filename}_{i + 1}.wav")
            file_path = os.path.join(temp_dir, filename)
            combined.export(file_path, format="wav")
            files.append({"filename": filename, "url": f"/download/{session_id}/{filename}"})

        return jsonify({"files": files})

    except ValueError:
        return jsonify({"error": "Please enter valid integer values for numerical fields."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<session_id>/<filename>")
def download(session_id, filename):
    safe_session = secure_filename(session_id)
    safe_filename = secure_filename(filename)
    if not safe_session or not safe_filename:
        return "Invalid request", 400
    file_path = os.path.join(tempfile.gettempdir(), "wav_gen", safe_session, safe_filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path, as_attachment=True, download_name=safe_filename)


if __name__ == "__main__":
    app.run(debug=False)

from flask import Flask, request, send_file, jsonify
import io
import os
import numpy as np

app = Flask(__name__)

print("Initializing TTS model...")
try:
    from TTS.api import TTS
    # Use a lightweight model for Render (no GPU)
    tts_engine = TTS("tts_models/en/ljspeech/glow-tts", gpu=False)
    print("TTS model initialized successfully!")
except Exception as e:
    print(f"Error initializing TTS model: {e}")
    tts_engine = None

@app.route('/')
def home():
    return "M.O.N.D.A.Y TTS Server is Running! 🚀"

@app.route('/health', methods=['GET'])
def health_check():
    if tts_engine is not None:
        return jsonify({"status": "healthy", "model_loaded": True}), 200
    else:
        return jsonify({"status": "unhealthy", "model_loaded": False}), 500

@app.route('/synthesize', methods=['POST'])
def synthesize():
    if not tts_engine:
        return jsonify({"error": "TTS engine not initialized"}), 500

    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        print(f"Synthesizing: {text}")
        
        # Generate audio WAV data
        wav = tts_engine.tts(text)
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        tts_engine.save_wav(wav, buffer)
        buffer.seek(0)
        
        return send_file(buffer, mimetype="audio/wav", as_attachment=False)

    except Exception as e:
        print(f"Error during synthesis: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)


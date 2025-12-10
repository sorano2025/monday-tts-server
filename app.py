from flask import Flask, request, send_file, jsonify
import io
import os
import torch
import numpy as np

app = Flask(__name__)

# Initialize TTS model globally so it loads once at startup
print("🚀 Initializing Coqui TTS model...")
tts_engine = None

try:
    from TTS.api import TTS
    
    # Use lightweight model for Render (no GPU needed)
    # This will download ~200MB on first run
    tts_engine = TTS(
        model_name="tts_models/en/ljspeech/glow-tts",
        progress_bar=True,
        gpu=False  # Render doesn't have GPU, use CPU
    )
    print("✅ TTS model initialized successfully!")
    print("🎙️ Gira voice is ready!")
    
except Exception as e:
    print(f"❌ Error initializing TTS model: {e}")
    print("⚠️ TTS will not work, but app will still run")
    tts_engine = None

@app.route('/')
def home():
    if tts_engine:
        return "✅ M.O.N.D.A.Y TTS Server is Running! 🎙️ Gira is ready!"
    else:
        return "⚠️ M.O.N.D.A.Y TTS Server is Running but model failed to load"

@app.route('/health', methods=['GET'])
def health_check():
    if tts_engine is not None:
        return jsonify({
            "status": "healthy",
            "model_loaded": True,
            "model": "Coqui TTS - Glow-TTS",
            "voice": "Gira"
        }), 200
    else:
        return jsonify({
            "status": "unhealthy",
            "model_loaded": False,
            "error": "TTS model failed to load"
        }), 500

@app.route('/synthesize', methods=['POST'])
def synthesize():
    """
    Expects JSON: { "text": "Hello world" }
    Returns: WAV audio file
    """
    if not tts_engine:
        print("❌ TTS engine not initialized")
        return jsonify({"error": "TTS engine not initialized"}), 500

    try:
        # Get text from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        if len(text) > 1000:
            return jsonify({"error": "Text too long (max 1000 chars)"}), 400
        
        print(f"\n🎤 Synthesizing: {text}")
        
        # Generate audio using TTS
        # This returns a numpy array
        wav = tts_engine.tts(text)
        
        print(f"✅ Generated {len(wav)} samples")
        
        # Convert to bytes and return as WAV
        buffer = io.BytesIO()
        
        # Save as WAV using the TTS engine's save method
        # The TTS engine expects the buffer to be writable
        tts_engine.save_wav(wav, buffer)
        
        # Reset buffer position to beginning
        buffer.seek(0)
        
        print("✅ Audio ready to send")
        
        # Send as WAV file
        return send_file(
            buffer,
            mimetype="audio/wav",
            as_attachment=False,
            download_name="gira_response.wav"
        )
    
    except Exception as e:
        print(f"❌ Error during synthesis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Also support /tts and /speak for compatibility
@app.route('/tts', methods=['POST'])
def tts():
    return synthesize()

@app.route('/speak', methods=['POST'])
def speak():
    return synthesize()

if __name__ == '__main__':
    # Render provides the PORT environment variable
    port = int(os.environ.get('PORT', 10000))
    print(f"\n🌍 Starting server on port {port}")
    print(f"📍 Access at: http://0.0.0.0:{port}")
    
    # Run Flask
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,  # No debug on Render
        threaded=True  # Handle multiple requests
    )

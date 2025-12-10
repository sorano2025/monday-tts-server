from flask import Flask, request, send_file, jsonify
import io
from gtts import gTTS

app = Flask(__name__)

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text"}), 400
    
    # Generate TTS with Google
    tts = gTTS(text=text, lang='en', slow=False)
    
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    
    return send_file(buffer, mimetype="audio/mp3")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

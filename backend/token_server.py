"""
Simple token generation server for LiveKit
Run this alongside your agent for token generation
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from livekit import api
import os
from dotenv import load_dotenv
import io
import wave
import struct
import math
from flask import send_file

load_dotenv()

app = Flask(__name__)
CORS(app)

LIVEKIT_URL = os.getenv("LIVEKIT_URL")


@app.route('/', methods=['GET'])
def home():
    """Home route - server status"""
    return jsonify({'message': 'Token server is running', 'status': 'ok'})
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")


@app.route('/api/livekit-token', methods=['POST'])
def generate_token():
    """Generate a LiveKit token for a room"""
    try:
        data = request.json
        room_name = data.get('roomName', f'room-{os.urandom(8).hex()}')
        participant_name = data.get('participantName', 'user')
        
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            return jsonify({'error': 'LiveKit credentials not configured'}), 500
        
        # Create token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(participant_name) \
            .with_name(participant_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )).to_jwt()
        
        return jsonify({
            'token': token,
            'url': LIVEKIT_URL,
            'roomName': room_name,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


@app.route('/debug/synthesize', methods=['GET', 'POST'])
def debug_synthesize():
    """Generate a short test WAV (sine tone) and return it for playback debugging.

    Use GET /debug/synthesize?text=Hello or POST JSON {"text": "Hello"}.
    This produces a 1s 16kHz mono WAV tone (not real TTS) to validate audio playback.
    """
    try:
        # Accept text but we don't use it for this synthetic tone
        if request.method == 'POST' and request.is_json:
            data = request.get_json()
            text = data.get('text', 'Test')
        else:
            text = request.args.get('text', 'Test')

        # Sine wave parameters
        sample_rate = 16000
        duration = 1.0
        freq = 440.0
        amplitude = 0.5 * 32767

        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            for i in range(n_samples):
                t = float(i) / sample_rate
                sample = int(amplitude * math.sin(2 * math.pi * freq * t))
                wf.writeframes(struct.pack('<h', sample))

        buf.seek(0)
        return send_file(buf, mimetype='audio/wav', as_attachment=False, download_name='debug_tone.wav')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

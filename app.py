from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import threading, time, json, os
import requests
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

MSG_FILE = 'messages.json'
lock = threading.Lock()
messages = []

# Load messages from file if exists
if os.path.exists(MSG_FILE):
    try:
        with open(MSG_FILE, 'r') as f:
            messages = json.load(f)
    except Exception:
        messages = []

def save_messages():
    with lock:
        with open(MSG_FILE, 'w') as f:
            json.dump(messages, f, indent=2)

def push_message(msg):
    """Add message if not duplicate (by id)."""
    with lock:
        # simple dedupe by id if provided
        ids = {m.get('id') for m in messages}
        if msg.get('id') in ids:
            return False
        messages.append(msg)
    save_messages()
    return True

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/messages', methods=['GET'])
def get_messages():
    """Return all messages (client polls this)."""
    return jsonify(messages)

@app.route('/send', methods=['POST'])
def send_message():
    """
    Called by the client browser.
    Body JSON: { "user": "Alice", "text": "Hello" }
    """
    data = request.get_json(force=True)
    user = data.get('user', 'anon')
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'empty message'}), 400

    msg = {
        'id': f"{int(time.time()*1000)}-{user}",  # simple unique id
        'user': user,
        'text': text,
        'ts': datetime.utcnow().isoformat() + 'Z',
        'origin': request.host  # source server host
    }

    push_message(msg)

    # Try forwarding to peer if configured and this request is from a browser (not replication)
    peer_url = os.environ.get('PEER_URL')  # example: http://<peer_ip>:80
    if peer_url:
        try:
            # send to /replicate on peer, don't block user if fails
            requests.post(f"{peer_url}/replicate", json=msg, timeout=2)
        except Exception as e:
            app.logger.warning(f"Failed to forward to peer {peer_url}: {e}")

    return jsonify({'ok': True, 'message': msg})

@app.route('/replicate', methods=['POST'])
def replicate():
    """
    Called by a peer server to replicate a message.
    The peer will NOT forward this further.
    """
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'no data'}), 400
    added = push_message(data)
    return jsonify({'ok': True, 'added': added})

if __name__ == '__main__':
    # For simple testing only. In production use gunicorn and port 80.
    app.run(host='0.0.0.0', port=5000, debug=True)

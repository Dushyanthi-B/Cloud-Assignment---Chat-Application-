# Flask Peer-to-Peer Chat App

A simple peer-to-peer message replication chat application built with Flask. This project allows multiple servers to replicate messages between each other while providing a REST API for browser clients.

---

## Features

- **Real-time messaging**: Users can send messages via a browser interface.
- **Peer-to-peer replication**: Messages are automatically forwarded between two servers (VM1 and VM2) to ensure consistency.
- **Persistent storage**: All messages are stored in a local `messages.json` file.
- **Duplicate prevention**: Messages are deduplicated by unique IDs.
- **CORS enabled**: Browser clients can communicate with the backend without cross-origin issues.

---

## Project Structure

project/
├── app.py # Main Flask application
├── messages.json # Stores chat messages
├── static/
│ └── index.html # Frontend interface
└── README.md


---

## Prerequisites

- Python 3.x
- `Flask` and `flask-cors`
- `requests` library for HTTP requests to peers

Install dependencies:

```bash
pip install Flask flask-cors requests


## Setup

Clone the repository:

git clone https://github.com/<username>/flask-chat-app.git
cd flask-chat-app


Set up environment variable for peer replication:

VM1 (replicates to VM2):

export PEER_URL="http://<VM2_IP>:5000"


VM2 (replicates to VM1):

export PEER_URL="http://<VM1_IP>:5000"


Run the Flask app:

python3 app.py

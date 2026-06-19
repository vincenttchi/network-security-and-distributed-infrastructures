"""
Group Members:  Darren Ammara, Vincent Chi
Due Date:       April 10, 2026
Course:         CECS 327-02
Professor:      Dr. Hailu Xu
"""
import os
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Node Data ---
# Lock guards the set against concurrent Flask worker threads.
_peers_lock = threading.Lock()
peers = set()

# --- Routes ---
@app.route("/", methods=["GET"])
def index():
    # Health check
    return jsonify({"service": "bootstrap", "status": "running", "peer_count": len(peers)})


@app.route("/register", methods=["POST"])
def register():
    # Request format = {"peer": "http://node1:5000"} or {"peers": [...]} for batch sync
    data = request.get_json(silent=True) or {}
    peer_url = data.get("peer")
    peer_list = data.get("peers", [])

    incoming = []
    if peer_url:
        incoming.append(peer_url)
    if isinstance(peer_list, list):
        incoming.extend(p for p in peer_list if isinstance(p, str))

    if not incoming:
        return jsonify({"status": "error", "reason": "missing 'peer' field"}), 400

    with _peers_lock:
        for url in incoming:
            peers.add(url)
        snapshot = sorted(peers)

    for url in incoming:
        print(f"[bootstrap] Registered peer: {url}", flush=True)
    return jsonify({"status": "registered", "peers": snapshot})


@app.route("/peers", methods=["GET"])
def list_peers():
    # Gets list of peers that have registered
    with _peers_lock:
        snapshot = sorted(peers)
    return jsonify({"peers": snapshot})


@app.route("/deregister", methods=["POST"])
def deregister():
    # Optional clean-shutdown so leaving nodes don't linger in the registry
    data = request.get_json(silent=True) or {}
    peer_url = data.get("peer")
    if not peer_url:
        return jsonify({"status": "error", "reason": "missing 'peer' field"}), 400

    with _peers_lock:
        peers.discard(peer_url)
        snapshot = sorted(peers)

    print(f"[bootstrap] Deregistered peer: {peer_url}", flush=True)
    return jsonify({"status": "deregistered", "peers": snapshot})


if __name__ == "__main__":
    port = int(os.environ.get("BOOTSTRAP_PORT", "5000"))
    print(f"[bootstrap] Bootstrap node starting on port {port}", flush=True)
    app.run(host="0.0.0.0", port=port)

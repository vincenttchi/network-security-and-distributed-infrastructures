"""
Group Members:  Darren Ammara, Vincent Chi
Due Date:       April 10, 2026
Course:         CECS 327-02
Professor:      Dr. Hailu Xu
"""
import os
import uuid
from flask import Flask, request, jsonify
import threading
import time
import requests
import socket
import random

random.seed(time.time())
app = Flask(__name__)

# --- Node Data ---
# Unique per-process identity. Each container gets its own on startup.
NODE_ID = str(uuid.uuid4())

# Friendly name from env for readable logs; falls back to UUID prefix
NODE_NAME = os.environ.get("NODE_NAME", f"node-{NODE_ID[:8]}")

NODE_ADDRESS = f"http://{socket.gethostname()}:5000"
BOOTSTRAP_URL = os.environ.get("BOOTSTRAP_URL")

# Known peer URLs (i.e "http://node2:5000")
peers = set()
_peer_lock = threading.Lock() # Lock for peer list of p2p node

# --- Functions ---
def register_bootstrap():
    """
    This function handles the node registering with the bootstrap.
    """
    # Attempting to register with bootstrap
    try:
        registration_data = {"peer": NODE_ADDRESS}
        response = requests.post(f"{BOOTSTRAP_URL}/register", json=registration_data)
        if response.status_code == 200:
            print(f"Successfully registered \"{NODE_ADDRESS}\".", flush=True)
            return True
    except Exception:
        pass
    return False


def get_bootstrap_peer_list():
    """
    This function retrieves the initial peer list from the bootstrap.
    """
    try:
        # Attempting to fetch for bootstrap peer list
        response = requests.get(f"{BOOTSTRAP_URL}/peers")
        if response.status_code == 200:
            new_list = response.json().get("peers", [])
            with _peer_lock:
                peers.update(new_list)
                peers.discard(NODE_ADDRESS)
        return True
    except Exception:
        pass
    return False
        

def discover_peers():
    """
    This function retrieves the peer list of a random, known peer
    and uses their list to update the current node's known peer list.
    """
    # Attempting to discover peer through gossip method
    peer = None
    try:
        # Picks a random peer from known peers
        with _peer_lock:
            if not peers:
               return False 
            peer = random.choice(list(peers))
        response = requests.get(f"{peer}/peers") # Geths that peer's peer list

        # Updates known peer list with the randomly chosen peer's
        if response.status_code == 200:
            with _peer_lock:
                peers.update(response.json()["peers"])
                peers.discard(NODE_ADDRESS)
            print(f"Updated known peers from: {peer}", flush=True)
            return True
    except Exception:
        if peer:
            print(f"Could not retrieve peer list from {peer}", flush=True)
    return False


def discovery_manager():
    """
    This function handles attempting to fetch peer list from the bootstrap
    if the current node's known peer list is empty. If its peer list is non-empty
    then the function will run forever to discover peers through the gossip
    method of discovering peers by getting the peer list from its known peers.
    """
    discovery_time = 10 # Sleep time for discovery/attempt to register to bootstrpa
    registered = False # Tracks if the node has already been registered   
    while True:
        # Handles registration of the node to bootstrap and fetching peer list
        if not registered:
            registered = register_bootstrap()

            # Gets bootstrap peer list on successful registration
            if registered:
                get_bootstrap_peer_list()
        
        # Handles error case of bootstrap peer list fetching failed
        with _peer_lock:
            needs_peers = len(peers) == 0
        
        if needs_peers and registered: # Attempts to fetch bootstrap until it has at least 1 peer
            get_bootstrap_peer_list()

        # Handles gossiping between nodes
        discover_peers()
        time.sleep(discovery_time)


# --- Routes ---
@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": f"Node {NODE_ID} is running!"})


@app.route("/peers", methods=["GET"])
def list_peers():
    # Getting list of peers for current node
    with _peer_lock:
        current_peers = sorted(peers)
    return jsonify({"node_id": NODE_ID, "peers": current_peers})


@app.route("/register", methods=["POST"])
def register_peer():
    # Request format = body {"peer": "http://node2:5000"}
    data = request.get_json(silent=True) or {}
    peer_url = data.get("peer")

    # Handles case if peer URL does not exist
    if not peer_url:
        return jsonify({"status": "error", "reason": "missing 'peer' field"}), 400
    
    # Adding the peer
    with _peer_lock:
        peers.add(peer_url)

    print(f"[{NODE_NAME}] Registered new peer: {peer_url}", flush=True)
    with _peer_lock:
        current_peers = sorted(peers)
    return jsonify({"status": "registered", "peers": current_peers})


@app.route("/message", methods=["POST"])
def receive_message():
    # Request format = {"sender": "Node1", "msg": "Hello Node2!"}
    data = request.get_json(silent=True) or {}
    sender = data.get("sender", "unknown")
    msg = data.get("msg", "")

    # Exact log format required by the spec.
    print(f"Received message from {sender}: {msg}", flush=True)
    return jsonify({"status": "received"})


@app.route("/send")
def send_message():
    # Getting URL arguments
    target = request.args.get("target")
    msg = request.args.get("msg", f"Hello World from {NODE_ADDRESS}")

    # Handling case of no target arg
    if not target:
        return jsonify({"status": "error", "reason": "No target specified"}), 400
    
    # Sending message to target
    requests.post(f"{target}/message", json={"sender": NODE_ADDRESS, "msg": msg})
    return jsonify({"status": "sent", "to": target, "content": msg})


if __name__ == "__main__":

    print(f"[{NODE_NAME}] Starting node with UUID {NODE_ID}", flush=True)

    # Creating thread to handle peer discovery from known peers
    discover_thread = threading.Thread(target=discovery_manager, daemon=True)
    discover_thread.start()
    app.run(host="0.0.0.0", port=5000)

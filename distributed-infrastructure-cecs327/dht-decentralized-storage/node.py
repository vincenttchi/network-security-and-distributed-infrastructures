"""
Group Members:  Darren Ammara, Vincent Chi
Due Date:       May 2, 2026
Course:         CECS 327-02
Professor:      Dr. Hailu Xu
"""
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
import threading
import time
import requests as http_requests
import socket
import random
import hashlib
import requests

random.seed(time.time())
app = Flask(__name__)

# --- Node Data ---
# Unique per-process identity. Each container gets its own on startup.
NODE_ID = str(uuid.uuid4())

# Friendly name from env for readable logs; falls back to a UUID prefix.
NODE_NAME = os.environ.get("NODE_NAME", f"node-{NODE_ID[:8]}")

NODE_ADDRESS = f"http://{socket.gethostname()}:5000"
BOOTSTRAP_URL = os.environ.get("BOOTSTRAP_URL")

# Known peer URLs (e.g. "http://node2:5000").
peers = set()
_peer_lock = threading.Lock()  # Lock for peer list of p2p node

# Storage directory for file uploads
STORAGE_DIR = "./storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

# In-memory key-value store
kv_store = {}
_kv_lock = threading.Lock()  # Lock for thread-safe access to kv_store


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

def hash_key_to_node(key):
    """
    SHA-1 hash of key used for determining node responsible for key. Returns
    the URL of the node responsible for key. If no node responsible for key
    then the current node address is returned.
    """
    # Getting sorted list of node addresses
    with _peer_lock:
        all_nodes = sorted(list(peers) + [NODE_ADDRESS])

    if not all_nodes:
        return NODE_ADDRESS
    
    # Getting the SHA-1 hash of key
    hash_val = int(hashlib.sha1(key.encode()).hexdigest(), 16)
    index = hash_val % len(all_nodes)
    return all_nodes[index]


def health_check_loop():
    """
    Periodically pings peers to check health. Unresponsive peers
    are also removed to keep the DHT routing table accurate.
    """
    HEALTH_CHECK_TIME_INTERVAL = 15
    while True:
        time.sleep(HEALTH_CHECK_TIME_INTERVAL)

        # Getting peer list
        with _peer_lock:
            current_peers = list(peers)
        
        # Pinging peers to check health
        for peer in current_peers:
            try:
                response = http_requests.get(f"{peer}/", timeout=3)
                if response.status_code != 200:
                    raise Exception("Unhealthy peer.")
            except Exception:
                print(f"[{NODE_NAME}] Peer {peer} is unresponsive. Removing {peer}.", flush=True)
                with _peer_lock: # Removing peer since unresponsive
                    peers.discard(peer)

# --- Routes ---
@app.route("/", methods=["GET"])
def index():
    """Health check endpoint returning node identity."""
    return jsonify({"message": f"Node {NODE_ID} is running!"})


@app.route("/peers", methods=["GET"])
def list_peers():
    """Returns the list of known peers for this node."""
    with _peer_lock:
        current_peers = sorted(peers)
    return jsonify({"node_id": NODE_ID, "peers": current_peers})


@app.route("/register", methods=["POST"])
def register_peer():
    """Registers a new peer URL in this node's peer list."""
    data = request.get_json(silent=True) or {}
    peer_url = data.get("peer")

    if not peer_url:
        return jsonify({"status": "error", "reason": "missing 'peer' field"}), 400

    with _peer_lock:
        peers.add(peer_url)

    print(f"[{NODE_NAME}] Registered new peer: {peer_url}", flush=True)
    return jsonify({"status": "registered", "peers": sorted(peers)})


@app.route("/message", methods=["POST"])
def receive_message():
    """Receives and logs a message from another node."""
    data = request.get_json(silent=True) or {}
    sender = data.get("sender", "unknown")
    msg = data.get("msg", "")

    print(f"Received message from {sender}: {msg}", flush=True)
    return jsonify({"status": "received"})


@app.route("/send")
def send_message():
    """Sends a message to a target node specified via query parameters."""
    target = request.args.get("target")
    msg = request.args.get("msg", f"Hello World from {NODE_ADDRESS}")

    if not target:
        return jsonify({"status": "error", "reason": "No target specified"}), 400

    http_requests.post(f"{target}/message", json={"sender": NODE_ADDRESS, "msg": msg})
    return jsonify({"status": "sent", "to": target, "content": msg})


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Accepts a file via multipart form upload and saves it to the
    node's local storage directory. The file persists via a Docker volume.
    """
    if "file" not in request.files:
        return jsonify({"status": "error", "reason": "no file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "reason": "empty filename"}), 400

    file.save(os.path.join(STORAGE_DIR, file.filename))
    print(f"[{NODE_NAME}] File uploaded: {file.filename}", flush=True)
    return jsonify({"status": "uploaded", "filename": file.filename})


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """
    Serves a previously uploaded file from the node's local storage.
    Returns 404 if the file does not exist.
    """
    return send_from_directory(STORAGE_DIR, filename)


@app.route("/files", methods=["GET"])
def list_files():
    """Lists all files currently stored on this node."""
    files = os.listdir(STORAGE_DIR)
    return jsonify({"node": NODE_NAME, "files": files})


@app.route("/kv", methods=["GET", "POST"])
def kv_endpoint():
    """
    POST: Stores a key-value pair. Expects JSON: {"key": "...", "value": "..."}
    GET:  Lists all key-value pairs stored on this node.
    """
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        key = data.get("key")
        value = data.get("value")

        if key is None or value is None:
            return jsonify({"status": "error", "reason": "missing 'key' or 'value'"}), 400
        
        # Forwarding POST request to responsible node if there is one
        responsible_node = hash_key_to_node(key)
        is_forwarded = request.args.get("forwarded") == "true"
        if responsible_node != NODE_ADDRESS and not is_forwarded:
            print(f"[{NODE_NAME}] Forwarding POST to {responsible_node}", flush=True)
            try:
                # Forwarding POST request
                res = http_requests.post(
                    f"{responsible_node}/kv?forwarded=true",
                    json=data,
                    timeout=5
                )
                return (res.content, res.status_code, dict(res.headers))
            except Exception as e:
                return jsonify({"status": "error", "reason": f"Forwarding failed: {e}"}), 500

        with _kv_lock:
            kv_store[key] = value

        print(f"[{NODE_NAME}] Stored key-value: {key} = {value}", flush=True)
        return jsonify({"status": "stored", "key": key, "value": value})

    # Get list all stored key-value pairs
    with _kv_lock:
        snapshot = dict(kv_store)
    return jsonify({"node": NODE_NAME, "store": snapshot})


@app.route("/kv/<key>", methods=["GET"])
def get_kv(key):
    """
    Retrieves the value associated with a key from the in-memory store.
    Returns 404 if the key does not exist.
    """
    # Forwarding GET request to responsible node if there is one
    responsible_node = hash_key_to_node(key)
    is_forwarded = request.args.get("forwarded") == "true"
    if responsible_node != NODE_ADDRESS and not is_forwarded:
        print(f"[{NODE_NAME}] Forwarding POST to {responsible_node}", flush=True)
        try:
            # Forwarding GET request
            res = http_requests.get(
                f"{responsible_node}/kv/{key}?forwarded=true",
                timeout=5
            )
            return (res.content, res.status_code, dict(res.headers))
        except Exception as e:
            return jsonify({"status": "error", "reason": f"Forwarding failed: {e}"}), 500

    with _kv_lock:
        value = kv_store.get(key)

    if value is None:
        return jsonify({"status": "error", "reason": f"key '{key}' not found"}), 404

    return jsonify({"key": key, "value": value})


if __name__ == "__main__":
    print(f"[{NODE_NAME}] Starting node with UUID {NODE_ID}", flush=True)
    # 0.0.0.0 so the container's port mapping is reachable.
    register_bootstrap()
    get_bootstrap_peer_list()

    # Creating thread to handle peer discovery from known peers
    discover_thread = threading.Thread(target=discovery_manager, daemon=True)
    discover_thread.start()

    # Creating thread to handle health monitoring
    health_check_thread = threading.Thread(target=health_check_loop, daemon=True)
    health_check_thread.start()

    app.run(host="0.0.0.0", port=5000)

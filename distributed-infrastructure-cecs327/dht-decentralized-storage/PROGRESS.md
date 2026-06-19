# Project 4 Handoff — Remaining Work

## What's Done (Phases 1 & 2)

### Phase 1: File Upload & Download
- `POST /upload` — multipart file upload, saves to `./storage/`
- `GET /download/<filename>` — serves a file from storage
- `GET /files` — lists all stored files
- Docker volumes mount `./storage/node1` and `./storage/node2` on the host so files persist across restarts

### Phase 2: Key-Value Store
- `POST /kv` with JSON `{"key": "...", "value": "..."}` — stores a pair
- `GET /kv/<key>` — retrieves a value (404 if missing)
- `GET /kv` — lists all stored pairs
- Data lives in an in-memory dict (`kv_store`) protected by `_kv_lock`

All endpoints are in `node.py`. Bootstrap files (`bootstrap.py`, `bootstrap.Dockerfile`) are unchanged from project3.

---

## What's Left

### Phase 3: DHT-Based Routing for Storage (required)

The KV store currently keeps data local to whichever node receives the request. Phase 3 makes it distributed — a hash determines which node *owns* a key, and requests get forwarded there.

**What to add in `node.py`:**

1. Import `hashlib` at the top.

2. Add a helper that hashes a key and picks the responsible node:
   ```python
   import hashlib

   def hash_key_to_node(key):
       """
       SHA-1 hash the key, mod by number of known nodes (peers + self),
       and return the URL of the responsible node.
       """
       with _peer_lock:
           all_nodes = sorted(list(peers) + [NODE_ADDRESS])
       hash_val = int(hashlib.sha1(key.encode()).hexdigest(), 16)
       idx = hash_val % len(all_nodes)
       return all_nodes[idx]
   ```

3. Update the `POST /kv` handler — before storing locally, check if this node is responsible. If not, forward:
   ```python
   responsible = hash_key_to_node(key)
   if responsible != NODE_ADDRESS:
       # Forward to the responsible node
       res = http_requests.post(f"{responsible}/kv", json={"key": key, "value": value})
       return res.json(), res.status_code
   # Otherwise store locally (existing code)
   ```

4. Same for `GET /kv/<key>` — check responsibility, forward with `http_requests.get()` if needed.

5. **Important edge case:** When forwarding, the receiving node will also call `hash_key_to_node`. Make sure forwarded requests don't loop. One approach: add a query param like `?forwarded=true` and skip the hash check when it's present.

**Testing:**
```bash
# Store on node1 — might get forwarded to node2 depending on hash
curl -X POST http://localhost:6001/kv -H "Content-Type: application/json" \
  -d '{"key": "city", "value": "Long Beach"}'

# Retrieve from node2 — should find it regardless of which node stored it
curl http://localhost:6002/kv/city
```

---

### Bonus Options (pick one for extra credit)

**Option 1: Peer Health Monitoring**
- Add a background thread that pings each peer periodically (e.g., `GET /` with a short timeout)
- Remove unresponsive peers from the `peers` set
- Good starting point: copy the `discover_peers()` pattern with a health check loop

**Option 2: Visualization Dashboard**
- Add a `/dashboard` route serving an HTML page
- Use Chart.js or D3.js to show active peers, connections, message traffic
- Pull data from `/peers`, `/files`, `/kv` via JS fetch calls

**Option 3: Gossip Protocol**
- Periodically share peer lists with random neighbors (partially done via `discover_peers()`)
- Add TTL metadata to limit message flooding

---

## How to Run

```bash
cd project4

# Build and start (first time or after code changes)
docker compose up --build -d

# Check containers are running
docker ps

# View logs
docker compose logs -f

# Rebuild after editing node.py
docker compose up --build -d

# Tear down
docker compose down
```

**Port mapping:**
| Container | Host Port |
|-----------|-----------|
| bootstrap | 6000      |
| node1     | 6001      |
| node2     | 6002      |

Note: ports 5000-5002 may conflict with macOS AirPlay / other services, which is why we use 6000+. If you need the original 5001/5002 ports (to match the project PDF examples), kill whatever's using them or update `docker-compose.yml`.

---

## Quick Test Cheatsheet

```bash
# Health check
curl http://localhost:6001/

# Upload a file to node1
curl -F 'file=@testfile.txt' http://localhost:6001/upload

# Download it back
curl http://localhost:6001/download/testfile.txt

# List files on node1
curl http://localhost:6001/files

# Store a key-value pair
curl -X POST http://localhost:6001/kv \
  -H "Content-Type: application/json" \
  -d '{"key": "color", "value": "blue"}'

# Retrieve it
curl http://localhost:6001/kv/color

# List all KV pairs
curl http://localhost:6001/kv

# Check peers
curl http://localhost:6001/peers
```

---

## File Overview

| File                  | What it does                                        |
|-----------------------|-----------------------------------------------------|
| `node.py`             | P2P node — all endpoints live here                  |
| `bootstrap.py`        | Bootstrap registry (unchanged from project3)        |
| `Dockerfile`          | Builds the p2p-node image with `/app/storage`       |
| `bootstrap.Dockerfile`| Builds the bootstrap image                          |
| `docker-compose.yml`  | Orchestrates bootstrap + 2 nodes with volumes       |
| `requirements.txt`    | `flask` and `requests`                              |
| `storage/`            | Created at runtime — holds uploaded files per node  |

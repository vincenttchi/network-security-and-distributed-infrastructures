# P2P Networking & Bootstrap

## Project Overview

For this project, we built a peer-to-peer (P2P) network of Docker containers where every node acts as both a client and a server. Each node runs a Flask HTTP API that exposes endpoints for peer registration, peer listing, and direct messaging. A separate **bootstrap node** acts as the initial directory service: new nodes register themselves with the bootstrap on startup and pull down the current peer list, after which they communicate with each other directly without needing the bootstrap.

### Files

- `node.py` — P2P node application (Phases 1 & 2: UUID identity, `/`, `/peers`, `/register`, `/message`, `/send`)
- `bootstrap.py` — Bootstrap registry node (Phase 3: `/register`, `/peers`, `/deregister`)
- `Dockerfile` — Image for a P2P node
- `bootstrap.Dockerfile` — Image for the bootstrap node
- `docker-compose.yml` — Brings up bootstrap + two nodes on a shared network
- `requirements.txt` — Python dependencies (Flask, requests)
- `run_p2p.sh` - Bash script for automation of building P2P node network containers (also cleans up old containers)

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Python 3.11** (only needed if running outside Docker)

### How to Compile and Run

1. Unzip the folder containing the project files.
2. In the terminal, navigate to the `project3` directory (where `docker-compose.yml` is stored).
3. Run the following command to build the images and start all containers in the background:

```bash
sudo docker-compose up --build -d
```

This starts three containers:

| Container   | Host Port | Role                  |
| ----------- | --------- | --------------------- |
| `bootstrap` | 5000      | Central peer registry |
| `node1`     | 5001      | P2P node              |
| `node2`     | 5002      | P2P node              |

To run a single node manually (matching the spec's example commands):

```bash
docker build -t p2p-node .
docker build -t bootstrap-node -f bootstrap.Dockerfile .
docker run -d --name bootstrap -p 5000:5000 bootstrap-node
docker run -d --name node1 -p 5001:5000 p2p-node
docker run -d --name node2 -p 5002:5000 p2p-node
```

### How to Test the Submission

**1. Verify each node is alive (Phase 1 expected output):**

```bash
curl http://localhost:5001/
# → {"message": "Node <UUID> is running!"}

curl http://localhost:5002/
# → {"message": "Node <UUID> is running!"}
```

**2. Register peers manually with another node (Phase 2):**

```bash
curl -X POST http://localhost:5001/register \
  -H "Content-Type: application/json" \
  -d '{"peer": "http://node2:5000"}'

curl http://localhost:5001/peers
# → {"node_id": "...", "peers": ["http://node2:5000"]}
```

**3. Send a message between nodes (Phase 2 expected output):**

```bash
curl -X POST http://localhost:5002/message \
  -H "Content-Type: application/json" \
  -d '{"sender": "Node1", "msg": "Hello Node2!"}'
# → {"status": "received"}
```

Then check the receiving node's logs:

```bash
sudo docker logs node2
# → Received message from Node1: Hello Node2!
```

**4. Verify the bootstrap registry (Phase 3 expected output):**

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"peer": "http://node1:5000"}'

curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"peer": "http://node2:5000"}'

curl http://localhost:5000/peers
# → {"peers": ["http://node1:5000", "http://node2:5000"]}
```

**5. Testing many nodes with messages being sent**

```bash
# Allowing execution run_p2p.sh
chmod +x run_p2p.sh
./run_p2p.sh  # creates 20 p2p nodes and 1 bootstrap

# View logs of node1 or any node you want to see:
# - bootstrap registration
# - query of bootstrap peer list
# - messages being received
# - message being sent
# - gossip method of discovery
# - node registrations (needs to manually register)
sudo docker logs -f node1

# Sending message to node2 from node1
curl "http://localhost:5001/send?target=http:node2:5000&msg=Hello+from+Node1"

# Registering a node21 to node1
curl -X POST http://localhost:5001/register \
  -H "Content-Type: application/json" \
  -d '{"peer": "http://node21:5000"}'
```

### Viewing Logs

```bash
sudo docker logs -f bootstrap
sudo docker logs -f node1
sudo docker logs -f node2
```

### Closing All Containers

```bash
sudo docker-compose down
# OR for large scale:
sudo docker rm -f $(sudo docker ps -aq)
```

# P2P File System & DHT

## Project Description

This project implements a decentralized Peer-to-Peer (P2P) network using a Distributed Hash Table (DHT). The system supports distributed file storage, a key-value store, and fault tolerance via health monitoring.

## Prerequisites

Docker and Docker Compose installed.

A terminal for running curl commands.

## Getting Started

**1. Build and Start the Network**
This command builds the images and starts the Bootstrap server plus 3 P2P nodes in detached mode:

```bash
docker compose up --build -d
```

**2. Verify Node Registration**

Wait about 10–20 seconds for the nodes to register and perform their first discovery cycle. Check the Bootstrap registry:

```bash
curl http://localhost:6000/peers
```

## Testing the System

### Phase 1: File Operations\*\*

**Upload a file to Node 1:**

```bash
echo "Hello World!" > test.txt
curl -F 'file=@test.txt' http://localhost:6001/upload
```

**List files on Node 1:**

```bash
curl http://localhost:6001/files
```

**Download the file back:**

```bash
curl http://localhost:6001/download/test.txt
cat test.txt
```

### Phase 2 & 3: Distributed KV Store\*\*

**Store a key-value pair (Hashing & Forwarding):**
Send a request to Node 1. If Node 1 isn't responsible for the key, it will mathematically calculate the correct node and forward the request.

```bash
curl -X POST http://localhost:6001/kv -H "Content-Type: application/json" \
 -d '{"key": "myKey", "value": "myValue"}'
```

**Retrieve the value from a different node:**

```bash
curl http://localhost:6002/kv/myKey
```

### EXTRA CREDIT: Health Check & Fault Tolerance\*\*

1. Stop a node: docker stop node3

2. **Wait:** After 15 seconds, the background threads in Node 1 and Node 2 will detect the failure.

3. **Verify:** Check the peer list on Node 1; node3 should be gone.

```bash
curl http://localhost:6001/peers
```

### Cleanup

**To stop the network and remove containers:**

```bash
docker compose down
```

**To wipe the images and start completely fresh:**

```bash
docker system prune -a
```

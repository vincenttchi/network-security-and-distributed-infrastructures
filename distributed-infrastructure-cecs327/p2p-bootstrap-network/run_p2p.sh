# --- Configuration ---
NUM_NODES=20
IMAGE_NODE="p2p-node"
IMAGE_BOOT_NODE="bootstrap-node"
NETWORK_NAME="p2p-net"

echo -e "Creating P2P Network...\n"

# Removing old containers and networks
echo -e "\nCleaning..."
sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null
sudo docker network rm $NETWORK_NAME 2>/dev/null

# Building the images and network
echo -e "\nBuilding images..."
sudo docker build -t $IMAGE_BOOT_NODE -f bootstrap.Dockerfile .
sudo docker build -t $IMAGE_NODE .

echo -e "\nCreating network..."
sudo docker network create $NETWORK_NAME

# Bootstrap node creation
echo -e "\nStarting bootstrap node..."
sudo docker run -d \
  --name bootstrap \
  --hostname bootstrap \
  --network $NETWORK_NAME \
  -p 5000:5000 \
  $IMAGE_BOOT_NODE

# P2P Nodes creation
echo -e "\nStarting $NUM_NODES P2P nodes..."
for i in $(seq 1 $NUM_NODES)
do
  # Host configurations
  HOST_PORT=$((5000 + i))
  NODE_NAME="node$i"

  # Running the p2p node
  sudo docker run -d \
    --name "$NODE_NAME" \
    --hostname "$NODE_NAME" \
    --network $NETWORK_NAME \
    -p "$HOST_PORT:5000" \
    -e BOOTSTRAP_URL="http://bootstrap:5000" \
    $IMAGE_NODE
done
echo -e "\nP2P Network Construction Completed\n"

# Random node message send
echo "Having each node send a message to a random node..."
sleep 3

# Having each node send msg to a random node
for i in $(seq 1 $NUM_NODES)
do
  HOST_PORT=$((5000 + i))

  # Picks a random node until not equal to current
  TARGET_ID=$(((RANDOM % NUM_NODES) + 1))
  while [ $TARGET_ID -eq $i ]; do
    TARGET_ID=$(((RANDOM % NUM_NODES) + 1))
  done

  # Building target address
  TARGET_ADDR="http://node${TARGET_ID}:5000"
  curl -s "http://localhost:${HOST_PORT}/send?target=${TARGET_ADDR}&msg=Hello+from+Node+${i}" > /dev/null &
  echo "Node $i sent a message to: $TARGET_ADDR"
done
echo -e "\nScript completed."

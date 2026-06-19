# Anycast and Multicast

## Project Overview

For this project, we demonstrated an Anycast routing (on the TCP protocol) using three servers listening on port 5000 and a client sending a request to that port.

We also demonstrated Multicast routing (on the UDP protocol) with multiple receivers receiving (json, binary, and plaintext) messages from a couple of senders to 224.1.1.1:5007. It can be observed the replication of data being sent across a multicast group (i.e. the receivers).

### Prerequisites

- **Docker** and **Docker Compose** installed.
- **Python 3.11+**

### How to Compile and Run

#### Part 1: Anycast (TCP)

To launch the Anycast simulation with three servers and one client, go to the `anycast/` folder in a terminal:

```bash
sudo docker-compose up --build
```

#### Part 2: Multicast (UDP)

To launch the Multicast simulation with your desired number of receivers and senders, go to the `multicast/` folder in a terminal:

```bash
# We used 3 receivers and 2 senders for testing and showing our results
sudo docker-compose up --build --scale receiver=3 --scale sender=2
```

```bash
# We used 3 receivers and 1 senders for testing and showing our results
sudo docker-compose up --build --scale receiver=3 --scale sender=1
```

### How to Test the Submission

#### Testing Anycast:

1. Once the containers are built and running, the `client` will automatically attempt to connect to the `server` alias which is essentially all the defined servers. The connections can be observed in the terminal where the containers were built from. Let us call this **terminal A**.
2. In a new **terminal B**, run _tcpdump_ on one of the server containers by:

```bash
# Get the container id of the server you want to observe
sudo docker ps
```

```bash
# Starting tcpdump to capture network traffic on the desired server container
sudo docker exec -it <the_container_id> tcp port 5000
```

3. In a new **terminal C**, run `sudo docker-compose run client` multiple times to see the client creating a TCP connection with different servers on the shortest path.

4. Look at **terminal B** to observe the TCP packet information including the TCP packet types and the anatomy of the TCP protocol with the handshake, communication flow, and how communication ends.

#### Testing Multicast:

1. Once the containers are built and running, the results of the multicasted messages sent by senders can be verified using the sender's IP address and the source IP address on the receiver's end, in the terminal. All subscribed receivers (to the multicast group) will receive unique JSON object, binary, and plaintext messages from each sender.
2. The _tcpdump_ information on the UDP packets the receivers are receiving are displayed on receive. So UDP packet information can be observed and the connectionless nature of the UDP protocol.

### Closing Server and Client Containers

To close all containers run:

```bash
sudo docker-compose down
```

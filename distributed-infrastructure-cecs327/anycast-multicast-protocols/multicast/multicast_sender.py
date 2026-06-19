"""
Group Members:  Darren Ammara, Vincent Chi
Due Date:       March 20, 2026
Course:         CECS 327-02
Professor:      Dr. Hailu Xu
"""
import socket
import json
import random
import os
import time

# ------------------------------ GETTING SENDER IP ------------------------------

# Trick to get the current sender's IP address by connecting dummy socket to a public IP
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender_socket:
    try:
        sender_socket.connect(("10.255.255.255", 1))
        server_ip = sender_socket.getsockname()[0] # Gets the current socket's IP
    except:
        server_ip = "127.0.0.1"

# ------------------------------ MULTICAST SENDER ------------------------------

# Host IP and Multicast Group Configuration
MULTICAST_GROUP_IP = "224.1.1.1"
MULTICAST_GROUP_PORT = 5007

# Parameters to change how much bytes the receiver can accept
NUM_KB = 32 # of KB that can possibly be received
BYTES_PER_KB = 1024

# Creating UDP listening socket for the multicast receiver
random.seed(time.time())
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender_socket:
    
    # Construct multicast message based on user cmdline arg
    json_data = json.dumps({"sensor": random.choice(["temp","humidity","air_quality"]),
                            "value": random.randrange(0,100,1)}).encode("utf-8")
    m_bytes = BYTES_PER_KB * NUM_KB # Sending 32KB of bytes
    binary_data = os.urandom(m_bytes)
    plaintext = random.choice(["cat", "dog", "mouse"]) + " " + random.choice(["backpack", "shoe", "pencil"]) + random.choice(["?", "!", "."])

    # Setting multicast message TTL
    ttl = 1     # Setting TTL to 1 to stay within local network
    sender_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Sending multicast message
    sender_socket.sendto(json_data, (MULTICAST_GROUP_IP, MULTICAST_GROUP_PORT))
    sender_socket.sendto(binary_data, (MULTICAST_GROUP_IP, MULTICAST_GROUP_PORT))
    sender_socket.sendto(plaintext.encode("utf-8"), (MULTICAST_GROUP_IP, MULTICAST_GROUP_PORT))

    # Displaying multicast message sent
    print(f"Sent: Multicast message from {server_ip}")
    print(f"Sent (JSON): {json_data.decode('utf-8')}")
    print(f"Sent ({m_bytes}-bytes): [FIRST 32 BYTES]={binary_data.hex()[:32]}")
    print(f"Sent (TEXT): {plaintext}")

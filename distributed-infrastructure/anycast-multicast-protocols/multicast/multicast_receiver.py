"""
Group Members:  Darren Ammara, Vincent Chi
Due Date:       March 20, 2026
Course:         CECS 327-02
Professor:      Dr. Hailu Xu
"""
import argparse
import socket
import struct
import time
import json

# ------------------------------ COMMAND LINE PARSING ------------------------------

# Setting up the cmd line argument parser to get duration argument
parser = argparse.ArgumentParser(
    prog="Multicast Receiver", 
    description="This program creates a receiver in multicast communications",
    epilog="To run the multicast receiver:\n" \
        "\tpython multicast_receiver.py --duration [DURATION]" \
)
parser.add_argument("--duration", type=int, default=30, help="Duration in seconds.")
args = parser.parse_args()

# Checking that duration is valid
if args.duration <= 0:
    parser.error("Duration must be a non-negative integer.")

# ------------------------------ MULTICAST RECEIVER ------------------------------

# Host IP and Multicast Group Configuration
HOST_IP = "0.0.0.0" # Listen to all addresses at port 5007 in docker container
MULTICAST_GROUP_IP = "224.1.1.1"
MULTICAST_GROUP_PORT = 5007

# Parameters to change how much bytes the receiver can accept
NUM_KB = 32 # of KB that can possibly be received
BYTES_PER_KB = 1024

# Creating UDP listening socket for the multicast receiver
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver_socket:

    receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows multiple receivers on an same addr
    receiver_socket.bind((HOST_IP, MULTICAST_GROUP_PORT))

    # Adding receiver to the multicast group
    multicast_request = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP_IP),
                                    socket.INADDR_ANY) # Packaging multicast address to 4-byte blocks
    receiver_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)
    print(f"Joined multicast group")

    # Listening in multicast group for message for the passed in duration
    receiver_socket.settimeout(1.0) # Times out the receiver socket from listening forever
    start_time = time.time()
    sender_addr = None
    try:

        # Receiver listens for messages in multicast group for the given duration
        while int(time.time() - start_time) < args.duration:
            try:
                data, sender_addr = receiver_socket.recvfrom(BYTES_PER_KB * NUM_KB)

                # Printing data if received any
                if data:
                    try: # Printing the JSON object
                        message = data.decode("utf-8")
                        print(f"Received [JSON] from {sender_addr}: {json.loads(message)}")
                    except json.JSONDecodeError: # Handles just printing the plain text (failed case not binary or json)
                        print(f"Received [TEXT] from {sender_addr}: {message}")

             # Printing the binary data
            except UnicodeDecodeError:
                print(f"Received [BINARY] from {sender_addr}: [FIRST 32 BYTES]={data.hex()[:32]}")

            # Handles receiver socket timing out from listening duration
            except socket.timeout:
                continue

            # Handles any unexpected system errors
            except Exception as e:
                print(f"ERROR: {e}")
                break

    # Catching CTRL+C to safely close socket
    except KeyboardInterrupt:
        pass
    finally:
        print("Leaving multicast group")

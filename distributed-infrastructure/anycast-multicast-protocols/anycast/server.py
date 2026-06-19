"""
Group Members:  Darren Ammara, Vincent Chi
Due Date:       March 20, 2026
Course:         CECS 327-02
Professor:      Dr. Hailu Xu
"""
import socket
import os

HOST = "0.0.0.0"
PORT = 5000

server_name = os.environ.get("SERVER_NAME", "server1")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server ready on port {PORT}", flush=True)

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Accepted connection from {addr}", flush=True)
            message = f"Hello from {server_name}"
            conn.sendall(message.encode())
            print(f"Sent: {message}", flush=True)

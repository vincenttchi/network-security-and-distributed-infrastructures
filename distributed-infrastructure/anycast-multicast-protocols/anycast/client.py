"""
Group Members:  Darren Ammara, Vincent Chi
Due Date:       March 20, 2026
Course:         CECS 327-02
Professor:      Dr. Hailu Xu
"""
import socket

HOST = "server"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = s.recv(1024)
    print(f"Received: {data.decode()}")

# Non-Standard Port Auditing & Service Banner Interrogation

This lab covers how to perform deep-spectrum network reconnaissance against an authorized academic lab environment. Instead of relying on standard scanning configurations that audit well-known system ports, this implementation restricts inspection exclusively to the unprivileged user-space (ports 1024–65535) and features a stateful pipeline that terminates execution early once specific target flags are extracted.

## Core Lab Concepts

### 1. Privileged vs. User-Configurable Sockets

Standard well-known ports (0–1023) require root/administrative privileges and typically run core system services using vendor-locked, static banners. Custom strings, flag tokens, and user-deployed applications are almost exclusively bound to unprivileged high ports (1024–65535). Because these sockets are entirely user-configurable, security audits require dedicated high-range inspection to catch custom listening utilities (such as lightweight Python or Netcat listening sockets) while ignoring standard system noise.

### 2. Eliminating Service Fingerprint Bloat

When Nmap runs version detection (`-sV`) against non-standard or proprietary applications, it may fail to find a matching database signature, resulting in a large `SERVICE FINGERPRINT` debugging block. To normalize output and extract plaintext banners from custom challeges, the Nmap Scripting Engine (`--script banner`) is explicitly invoked to capture raw socket greeting strings cleanly.

### 3. State-Driven Early Termination

Scanning thousands of ports sequentially introduces unnecessary network noise and processing delays. By decoupling the reconnaissance into an initial fast port discovery pass followed by a targeted interrogation loop, we can programmatically evaluate the network strings in real-time. The moment our specific criteria tokens are fulfilled, the orchestration script calls a loop break, concluding operations immediately to preserve bandwidth and stealth.

---

## Lab Execution & Commands

### 1. Automated Dynamic-Range Discovery Pipeline

To execute the multi-phase discovery and banner matching process with early-termination support:

```bash
chmod +x banner_grabber.sh
./banner_grabber.sh
```

### 2. Manual Sequential Reference Workflow

**Step A: Run a fast rate-controlled stealth sweep to locate open high-range ports**

```bash
sudo nmap -sS -p 1024-65535 --open --max-rate 150 [target_server]
```

**Step B: Interrogate target open ports with explicit NSE banner extraction**

```bash
sudo nmap -p [target_port] -sV --script banner [target_server]
```

---

## Understanding Port States & Banner Outputs

| Port State   | Packet Response                     | What It Means                                                                      |
| :----------- | :---------------------------------- | :--------------------------------------------------------------------------------- |
| **Open**     | Target returned a `SYN-ACK` packet. | A service is actively listening and available for banner grabbing.                 |
| **Closed**   | Target returned a `RST` packet.     | The host is online, but no service is listening on this port.                      |
| **Filtered** | No response, or an ICMP error.      | A firewall or rate-limiter dropped our packets before they could reach the socket. |

### Expected Script Output Format

Upon successful completion, the automation pipeline bypasses service-probe raw dumps and generates a streamlined report summary:

```text
=== CTF RECON SUMMARY ===
Flag 1 ('My packets are your packets'): Found on Port XXXXX
Flag 2 ('The key to your Universe'): Found on Port XXXXX
```

---

## Educational Disclaimer & Responsible Use

The code, documentation, and technical artifacts contained within this repository were developed exclusively for educational purposes, structured academic laboratory exercises, and authorized vulnerability assessments.

- All activities were performed within fully isolated, private virtualization environments or authorized academic lab environments.
- No production systems were disrupted, and no unauthorized network interception or data collection took place.
- This repository does not host malicious utilities, nor is it intended to facilitate unauthorized system intrusion.

The primary objective of these projects is to demonstrate defensive engineering principles, host auditing methodologies, and an understanding of operating system internals for professional development.

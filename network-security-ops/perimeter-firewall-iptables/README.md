# Stateful Perimeter Firewall with iptables

This lab covers how to build a strict, stateful host firewall using the Linux Netfilter (`iptables`) framework. The configuration locks down the server using a "Zero-Trust" approach, meaning it blocks all network traffic by default and only opens exact, necessary paths for specific services.

## Core Security Policies

A secure firewall doesn't just block ports; it actively tracks the state of ongoing network conversations.

### 1. Default-Deny Posture

Instead of leaving things open and blocking bad traffic, this firewall immediately drops all incoming (`INPUT`), outbound (`OUTPUT`), and forwarded (`FORWARD`) traffic. If a type of traffic isn't explicitly whitelisted, the kernel silently discards it.

### 2. Stateful Connection Tracking (`conntrack`)

The firewall uses the kernel's connection tracking engine to watch traffic flows.

- **How it helps:** It automatically recognizes and permits incoming or outbound packets that belong to a conversation your server already approved (`ESTABLISHED,RELATED`). This means you don't have to open massive port ranges for return traffic.

### 3. Loopback Isolation

The internal loopback interface (`lo` / `127.0.0.1`) is completely whitelisted. This allows internal processes on the server to talk to each other safely while blocking external hackers from spoofing loopback addresses.

### 4. Rate-Limited Kernel Logging

Any packet that doesn't match our whitelists falls to the bottom of the chain. The firewall catches these packets, appends a descriptive tag, and notes them in the system log before they are destroyed. The log rate is strictly capped to prevent log-flooding attacks from exhausting server storage.

---

## The Firewall Script (`secure_rules.sh`)

This shell script clears any unmanaged rules and sets up our airtight firewall profile directly in the Linux kernel:

```bash
#!/bin/bash

# Enforcing strict zero-trust policy
sudo iptables -P INPUT DROP
sudo iptables -P OUTPUT DROP
sudo iptables -P FORWARD DROP

# Enabling internal loopback traffic to be accepted
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT

# Establishing stateful connection tracking rules
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT

# Inbound rules (who can start a conversation WITH our server)
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT  # SSH
sudo iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT  # HTTP
sudo iptables -A INPUT -p tcp --dport 443 -m conntrack --ctstate NEW -j ACCEPT # HTTPS

# outbound rules (who our server is allowed to start conversations with)
sudo iptables -A OUTPUT -p udp --dport 53 -m conntrack --ctstate NEW -j ACCEPT # DNS (UDP)
sudo iptables -A OUTPUT -p tcp --dport 53 -m conntrack --ctstate NEW -j ACCEPT # DNS (TCP fallback)

# Logging rules (log dropped packets right before the default policy deletes them)
sudo iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-in-denied: " --log-level 7
sudo iptables -A OUTPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-out-denied: " --log-level 7
```

---

## Useful Audit Commands

- `sudo iptables -L -v -n --line-numbers`: View your active firewall rules alongside packet counters showing exactly how much traffic each rule has caught.
- `sudo conntrack -L`: View the active in-memory state table tracking every live network conversation currently passing through the host.
- `sudo tail -f /var/log/syslog | grep "iptables-"`: Monitor blocked inbound and outbound packets live as they hit the firewall boundaries.

---

## Educational Disclaimer & Responsible Use

The code, documentation, and technical artifacts contained within this repository were developed exclusively for educational purposes, structured academic laboratory exercises, and authorized vulnerability assessments.

- All activities were performed within fully isolated, private virtualization environments or authorized academic lab environments.
- No production systems were disrupted, and no unauthorized network interception or data collection took place.
- This repository does not host malicious utilities, nor is it intended to facilitate unauthorized system intrusion.

The primary objective of these projects is to demonstrate defensive engineering principles, host auditing methodologies, and an understanding of operating system internals for professional development.

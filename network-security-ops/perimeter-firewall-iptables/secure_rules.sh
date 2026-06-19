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

# Outbound rules (who our server is allowed to start conversations WITH)
sudo iptables -A OUTPUT -p udp --dport 53 -m conntrack --ctstate NEW -j ACCEPT # DNS (UDP)
sudo iptables -A OUTPUT -p tcp --dport 53 -m conntrack --ctstate NEW -j ACCEPT # DNS (TCP fallback)

# Logging rules (log dropped packets right before the default policy deletes them)
sudo iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-in-denied: " --log-level 7
sudo iptables -A OUTPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-out-denied: " --log-level 7

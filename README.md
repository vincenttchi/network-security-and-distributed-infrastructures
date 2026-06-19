# Network Security & Distributed Infrastructure Engineering Portfolio

A professional laboratory suite demonstrating hands-on competencies across network defense engineering, core operating system internals, cryptographic boundary auditing, and concurrent distributed architecture.

---

## Repository Architecture & Project Index

### Distributed Infrastructure Track

This track validates low-level systems programming capability, network socket programming, thread synchronization, and decentralized service state tracking.

- **[anycast-multicast-protocols](./distributed-infrastructure/anycast-multicast-protocols/)**
  - _Objective:_ Design and build functional transport-layer routing models executing TCP Anycast and UDP Multicast messaging profiles to handle localized and wide-area data broadcasting.
- **[dht-decentralized-storage](./distributed-infrastructure/dht-decentralized-storage/)**
  - _Objective:_ Engineer an in-memory key-value data framework utilizing concurrent, thread-safe mutual exclusion (`mutex`) locks to eliminate transactional race conditions, paired with physical persistent storage handlers.
- **[p2p-bootstrap-network](./distributed-infrastructure/p2p-bootstrap-network/)**
  - _Objective:_ Construct a decentralized peer-to-peer network matrix executing a Distributed Hash Table (DHT) framework with **SHA-1 hashing** for deterministic data routing and multi-node gossip cluster synchronization.

### Network Security Operations Track

This track demonstrates perimeter defensive mechanics, active asset discovery, threat modeling, and runtime memory/system call vulnerability analysis.

- **[active-recon-nmap](./network-security-ops/active-recon-nmap/)**
  - _Objective:_ Execute perimeter discovery scans on unprivileged user-space TCP sockets (ports 1024–65535) against a live endpoint, utilizing Nmap Scripting Engine (`--script banner`) automation and rate-throttling controls to bypass host firewall caps.
- **[perimeter-firewall-iptables](./network-security-ops/perimeter-firewall-iptables/)**
  - _Objective:_ Implement stateful packet filtering and access control matrices using Linux Netfilter/`iptables` structures to enforce zone segmentation, protocol restrictions, and unauthorized service blocking.
- **[system-call-auditing-strace](./network-security-ops/system-call-auditing-strace/)**
  - _Objective:_ Expose the _Encryption Boundary Fallacy_ by engineering a high-frequency Bash polling harness (`ssh_spy.sh`) that hooks transient root-level OpenSSH processes (`[priv]`) to capture unencrypted IPC payload streams directly out of memory buffers.

---

## Technical Competency Matrix

- **Security & Forensics:** State-driven Firewall Configuration (`iptables`), Deep Packet Inspection (DPI), Process Thread Hooking, Active Port Auditing, Network Detection Signature Writing.
- **Operating System Internals:** Linux System Call Auditing (`strace`/`ptrace`), Inter-Process Communication (IPC Socketpairs), Kernel Space Boundaries, Concurrency & Mutex Thread Locking.
- **Distributed Architectures:** Peer-to-Peer Distributed Hash Table (DHT), SHA-1 Consistent Hashing, TCP/IP Stack Socket Implementation, Cluster Synchronization.
- **Automation:** Scripted Shell Orchestration Pipelines (`Bash`), System Performance Verification.

---

## Educational Disclaimer & Responsible Use

The code, configuration artifacts, and data captures within this suite were generated strictly inside isolated private environments or explicitly authorized educational endpoints. All tasks were compiled to document defensive tracking metrics, structural programming boundaries, and core operating system architecture behaviors for professional vetting. No production systems were compromised, nor were any utilities weaponized for unauthorized network operations.

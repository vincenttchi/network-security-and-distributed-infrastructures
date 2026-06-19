# Multi-Host System Call Interception: Auditing SSH Cryptographic Boundaries

This lab demonstrates how an administrator or elevated process inside a Linux subsystem can leverage the system call tracer (`strace`) to audit host-level operational boundaries and intercept cleartext user inputs during authentication handshakes. By identifying the transient privilege-separation process and attaching a runtime tracer to its execution thread, we expose interactive user parameters before they cross the threshold into the application's internal cryptographic engine.

## Core Lab Concepts

### 1. The Encryption Boundary Fallacy

While protocols like SSH establish highly secure, encrypted tunnels across external network media, data remains completely exposed in plaintext while being handled within local user space memory and kernel transitions. An application must collect and store user credentials in standard memory buffers before invoking its cryptographic routines to wrap the payload for transport.

### 2. The Privilege-Separation Target (`[priv]`)

When a remote client initiates an SSH authentication handshake, the master SSH daemon does not process the credentials directly. Instead, it spawns a temporary, restricted child process dedicated to managing that specific user's authentication lifecycle (visible in the system process tree as `sshd: username [priv]`). Because this transient process is responsible for reading the raw input characters from the network socket before passing them to the validation modules, it represents the exact execution window required for plaintext interception.

---

## Technical Auditing Workflow

### Step 1: Firewall Verification (`iptables`)

Before configuring the service daemons, the network layer must be verified to ensure traffic flows freely across the custom port area. Checking active netfilter policies ensures packets aren't dropped implicitly:

```bash
sudo iptables -L -v -n
```

_(If port 2222 is blocked, allow traffic by executing: `sudo iptables -A INPUT -p tcp --dport 2222 -j ACCEPT`)_

### Step 2: Configuration-Free Service Initialization

To avoid modifying or tracking global configuration files within the repository, configuration overrides are passed directly to the binary engine as runtime flags. The system privilege-separation directory is initialized manually, and the daemon is pushed to the execution background:

```bash
# Initialize the temporary modern Ubuntu privilege separation runtime directory
sudo mkdir -p /run/sshd

# Launch the standalone daemon using inline command overrides
sudo /usr/sbin/sshd -p 2222 -o "PasswordAuthentication=yes" -o "PubkeyAuthentication=no" &
```

### Step 3: Executing the Automated Process Latch

Because the privilege-separation child thread only exists for a brief window while the user is actively authenticating, manual process tracking is prone to race-condition failures. The custom automation harness runs a high-frequency polling loop across the process subsystem to detect and lock onto the target PID the microsecond it registers:

```bash
# Grant execution permissions and run the automation harness
chmod +x ssh_spy.sh
./ssh_spy.sh
```

The script will block and monitor the system. The moment a client connects and triggers the password prompt, the script automatically hooks the process boundary.

---

## The Simulation (Server 2 to Server 1)

From the remote client machine (Server 2), an authentication request is triggered targeting the custom unprivileged listening framework:

```bash
ssh waldo@[SERVER_1_IP] -p 2222
```

When prompted, the user logs in using the assigned lab credential sequence: `cecsvc`.

---

## Log Analysis & Forensic Evidence

Once the user completes authentication on Server 2, the `strace` session on Server 1 captures the internal inter-process communication (IPC) boundary transaction cleanly. Because modern OpenSSH implements strict Privilege Separation (PrivSep), the cleartext credential payload is transmitted as a single structured block across an internal socket pair rather than character-by-character keystrokes:

```bash
head foo
```

### Extracted Log Results (`foo`)

```text
read(6, "\f\0\0\0\6cecsvc", 11)         = 11
```

### Forensic Architecture Analysis

1. **Socket Interface Discovered**: The system call targets File Descriptor `6`. This does not represent an external network socket or a local pseudo-terminal device. Instead, it isolates a local `socketpair()` link used for secure internal communication between the unprivileged network-facing child process and the root-level validation process (`sshd: waldo [priv]`).
2. **Buffer Payload Parsing**: The 11-byte intercepted data stream utilizes a Length-Value format type constraint:
   - `\f\0\0\0`: A 4-byte message type identifier (hex `0x0c`, indicating an internal SSH password verification request).
   - `\6`: A 1-byte length prefix confirming the length of the trailing payload parameter.
   - `cecsvc`: The raw, unencrypted password payload captured mid-flight inside host system memory boundaries.
3. **The Cryptographic Gap**: This trace proves that protocol-level encryption only protects data while it travels across external physical network media. While moving through internal IPC mechanisms and system memory structures, credentials remain entirely exposed to a privileged host adversary.

---

## ⚖️ Educational Disclaimer & Responsible Use

The code, documentation, and technical artifacts contained within this repository were developed exclusively for educational purposes, structured academic laboratory exercises, and authorized vulnerability assessments.

- All activities were performed within fully isolated, private virtualization environments or authorized academic lab environments.
- No production systems were disrupted, and no unauthorized network interception or data collection took place.
- This repository does not host malicious utilities, nor is it intended to facilitate unauthorized system intrusion.

The primary objective of these projects is to demonstrate defensive engineering principles, host auditing methodologies, and an understanding of operating system internals for professional development.

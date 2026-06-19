#!/bin/bash
TARGET="${1:?Usage: ./banner_grabber.sh <target>}"
OUTPUT_FILE="ctf_report.txt"

FLAG1="My packets are your packets."
FLAG2="The key to the Universe."

FOUND1=0
FOUND2=0
PORT1=""
PORT2=""

echo "[+] Phase 1: Rapidly mapping open ports in user-space (1024-65535)..."
# Raw SYN scan targeting only open ports to minimize rate limiting and noise
OPEN_PORTS=$(sudo nmap -sS -p 1024-65535 --open --max-rate 150 "$TARGET" | grep "open" | cut -d'/' -f1)

if [ -z "$OPEN_PORTS" ]; then
    echo "[-] Error: No open ports found. Verify connectivity or lower --max-rate."
    exit 1
fi

echo "[*] Located active ports: $(echo $OPEN_PORTS | tr '\n' ' ')"
echo -e "\n[+] Phase 2: Interrogating sockets sequentially with early-exit tracking..."
echo "------------------------------------------------------------------------"

for PORT in $OPEN_PORTS; do
    echo "[*] Querying banner on port $PORT..."
    
    # Run a fast, targeted check on a single port using the explicit banner script
    RAW_BANNER=$(sudo nmap -p "$PORT" -sV --script banner "$TARGET" 2>/dev/null)

    # Inspect the grabbed text for Target Flag 1
    if echo "$RAW_BANNER" | grep -qi "$FLAG1"; then
        echo "[!] TARGET MATCH: Located Flag 1 on Port $PORT!"
        FOUND1=1
        PORT1="$PORT"
    fi

    # Inspect the grabbed text for Target Flag 2
    if echo "$RAW_BANNER" | grep -qi "$FLAG2"; then
        echo "[!] TARGET MATCH: Located Flag 2 on Port $PORT!"
        FOUND2=1
        PORT2="$PORT"
    fi

    # Early Exit Condition: Break out of loop immediately if both flags are cached
    if [ $FOUND1 -eq 1 ] && [ $FOUND2 -eq 1 ]; then
        echo -e "\n[+++] SUCCESS: Both flags identified! Halting further scanning operations."
        break
    fi
done

echo "------------------------------------------------------------------------"

# Compile and print the final clean summary report
echo "=== CTF RECON SUMMARY ===" > "$OUTPUT_FILE"
[ $FOUND1 -eq 1 ] && echo "Flag 1 ('$FLAG1'): Found on Port $PORT1" >> "$OUTPUT_FILE"
[ $FOUND2 -eq 1 ] && echo "Flag 2 ('$FLAG2'): Found on Port $PORT2" >> "$OUTPUT_FILE"

if [ $FOUND1 -eq 1 ] && [ $FOUND2 -eq 1 ]; then
    cat "$OUTPUT_FILE"
else
    echo "[-] Pipeline ended. One or both flags were not recovered. Summary saved to $OUTPUT_FILE."
fi

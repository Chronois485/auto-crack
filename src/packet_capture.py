import os
import signal
import subprocess

from colored import cprint

from constants import (
    AIRODUMP_CMD,
    CAPTURE_OUTPUT_SUFFIX,
    HANDSHAKE_MARKER,
    PROCESS_READ_BUFFER_SIZE,
)

airodump_proc = None


def sniffing(iface, channel, bssid, output_prefix):
    global airodump_proc
    cprint(f"\n[*] Launching airodump-ng core capture engine on {iface}...", "blue")

    for f in os.listdir("."):
        if f.startswith(output_prefix):
            try:
                os.remove(f)
            except Exception:
                pass

    airodump_command = [
        AIRODUMP_CMD,
        "-c",
        str(channel),
        "--bssid",
        bssid,
        "-w",
        output_prefix,
        iface,
    ]
    handshake_found = False

    try:
        airodump_proc = subprocess.Popen(
            airodump_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=PROCESS_READ_BUFFER_SIZE,
        )
        cprint("[*] Monitoring for incoming handshakes...", "blue")

        while True:
            line = airodump_proc.stdout.readline()
            if not line:
                if airodump_proc.poll() is not None:
                    break
                continue

            if HANDSHAKE_MARKER in line:
                clean_line = line.strip()
                parts = clean_line.split(HANDSHAKE_MARKER)
                if len(parts) > 1:
                    mac_info = parts[1].strip().split()[0]
                    cprint(
                        f"\n[+] SUCCESS: Captured WPA Handshake for BSSID: {mac_info}",
                        "green",
                    )
                    handshake_found = True
                    break
    finally:
        print("asdasf")
        if airodump_proc:
            airodump_proc.send_signal(signal.SIGINT)
            airodump_proc.wait()

    target_file = f"{output_prefix}{CAPTURE_OUTPUT_SUFFIX}"
    return handshake_found, target_file

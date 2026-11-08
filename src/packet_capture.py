import os
import signal
import subprocess

from colored import cprint

from constants import (
    AIRODUMP_CMD,
    CAPTURE_OUTPUT_PREFIX,
    CAPTURE_OUTPUT_SUFFIX,
    HANDSHAKE_MARKER,
    PROCESS_READ_BUFFER_SIZE,
)
from monitor import configure_fixed_channel

airodump_proc = None


def sniffing(
    iface, channel, bssid, output_prefix=CAPTURE_OUTPUT_PREFIX, callback_status=None
):
    global airodump_proc

    # КРИТИЧНО: Фіксуємо адаптер на потрібному каналі перед запуском airodump!
    if channel:
        if callback_status:
            callback_status(f"Locking {iface} to channel {channel}...")
        configure_fixed_channel(iface, str(channel))

    if callback_status:
        callback_status(
            f"Launching airodump-ng on {iface} (BSSID: {bssid}, Ch: {channel})..."
        )
    cprint(
        f"\n[*] Launching airodump-ng on {iface} (BSSID: {bssid}, Ch: {channel})...",
        "blue",
    )

    for f in os.listdir("/tmp"):
        if f.startswith(os.path.basename(output_prefix)):
            try:
                os.remove(os.path.join("/tmp", f))
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
        if callback_status:
            callback_status("Monitoring for WPA handshake...")
        cprint("[*] Monitoring for WPA handshake...", "blue")

        while True:
            if not airodump_proc or not airodump_proc.stdout:
                break
            line = airodump_proc.stdout.readline()
            if not line:
                if airodump_proc.poll() is not None:
                    break
                continue

            print(line.strip())

            if HANDSHAKE_MARKER in line:
                clean_line = line.strip()
                parts = clean_line.split(HANDSHAKE_MARKER)
                if len(parts) > 1:
                    mac_info = parts[1].strip().split()[0]
                    msg = f"\nSUCCESS: Captured WPA Handshake for BSSID: {mac_info}"
                    if callback_status:
                        callback_status(msg)
                    cprint(msg, "green")
                    handshake_found = True
                    break
    finally:
        if airodump_proc:
            try:
                airodump_proc.send_signal(signal.SIGINT)
                airodump_proc.wait(timeout=3)
            except Exception:
                airodump_proc.kill()
            airodump_proc = None

    target_file = f"{output_prefix}{CAPTURE_OUTPUT_SUFFIX}"
    if callback_status:
        callback_status("Sniffing session finished.")
    return handshake_found, target_file


def stop_sniff_process():
    global airodump_proc
    if airodump_proc and airodump_proc.poll() is None:
        try:
            airodump_proc.send_signal(signal.SIGINT)
            airodump_proc.wait(timeout=3)
        except Exception:
            airodump_proc.kill()
        airodump_proc = None
        return True
    return False

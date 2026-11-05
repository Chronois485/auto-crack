import os
import signal
import subprocess
import sys
import time

from colored import cprint

airodump_proc = None


def run_command(command):
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        cprint(f"[-] Command failed: {' '.join(command)}", "red")
        cprint(f"[-] Error output: {e.stderr.strip()}", "red")
        sys.exit("1")


def configure_monitor_mode(iface, channel):
    cprint("[*] Killing conflicting network processes...", "blue")
    try:
        subprocess.run(["airmon-ng", "check", "kill"], capture_output=True)
    except FileNotFoundError:
        subprocess.run(["systemctl", "stop", "NetworkManager"], capture_output=True)
        subprocess.run(["pkill", "wpa_supplicant"], capture_output=True)

    cprint(f"[*] Bringing {iface} down...", "blue")
    run_command(["ip", "link", "set", iface, "down"])

    cprint(f"[*] Setting {iface} type to monitor...", "blue")
    run_command(["iw", "dev", iface, "set", "type", "monitor"])

    cprint(f"[*] Bringing {iface} up...", "blue")
    run_command(["ip", "link", "set", iface, "up"])
    time.sleep(2)

    cprint(f"[*] Locking {iface} to channel {channel}...", "blue")
    run_command(["iw", "dev", iface, "set", "channel", str(channel)])

    cprint(
        f"[+] Successfully configured {iface} in monitor mode on channel {channel}!",
        "green",
    )


def configure_default_mode(iface):
    cprint(f"[*] Bringing {iface} down...", "blue")
    run_command(["ip", "link", "set", iface, "down"])

    cprint(f"[*] Setting {iface} type to managed...", "blue")
    run_command(["iw", "dev", iface, "set", "type", "managed"])

    cprint(f"[*] Bringing {iface} up...", "blue")
    run_command(["ip", "link", "set", iface, "up"])

    cprint("[*] Restarting background network processes...", "blue")
    subprocess.run(["systemctl", "start", "NetworkManager"], capture_output=True)

    cprint(f"[+] Successfully configured {iface} in managed mode!", "green")


def sniffing(iface, channel, output_prefix):
    global airodump_proc
    cprint(f"\n[*] Launching airodump-ng core capture engine on {iface}...", "blue")

    for f in os.listdir("."):
        if f.startswith(output_prefix):
            try:
                os.remove(f)
            except Exception:
                pass

    airodump_command = [
        "airodump-ng",
        "-c",
        str(channel),
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
            bufsize=1,
        )
        cprint("[*] Engine running smoothly. Reconnect your phone now...", "blue")
        cprint("[*] Monitoring for incoming handshakes...", "blue")

        while True:
            line = airodump_proc.stdout.readline()
            if not line:
                if airodump_proc.poll() is not None:
                    break
                continue

            if "WPA handshake:" in line:
                clean_line = line.strip()
                parts = clean_line.split("WPA handshake:")
                if len(parts) > 1:
                    mac_info = parts[1].strip().split()[0]
                    cprint(
                        f"\n[+] SUCCESS: Captured WPA Handshake for BSSID: {mac_info}",
                        "green",
                    )
                    handshake_found = True
                    break

    except KeyboardInterrupt:
        cprint("\n[*] Ctrl+C detected! Stopping airodump-ng safely...", "blue")
    finally:
        cprint("\n[*] Cleaning up and restoring system network settings...", "blue")
        if airodump_proc:
            airodump_proc.send_signal(signal.SIGINT)
            airodump_proc.wait()
        configure_default_mode(iface)

    target_file = f"{output_prefix}-01.cap"
    return handshake_found, target_file

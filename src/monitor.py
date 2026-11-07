import subprocess
import time

from colored import cprint

from commands import run_command


def configure_monitor_mode(iface, channel):
    cprint("[*] Killing conflicting network processes...", "blue")
    try:
        subprocess.run(["airmon-ng", "check", "kill"], capture_output=True, check=False)
    except FileNotFoundError:
        subprocess.run(
            ["systemctl", "stop", "NetworkManager"], capture_output=True, check=False
        )
        subprocess.run(["pkill", "wpa_supplicant"], capture_output=True, check=False)

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
    subprocess.run(
        ["systemctl", "start", "NetworkManager"], capture_output=True, check=False
    )

    cprint(f"[+] Successfully configured {iface} in managed mode!", "green")

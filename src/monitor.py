import subprocess
import time

from colored import cprint

from commands import run_command
from constants import (
    AIRMON_CMD,
    IP_CMD,
    IW_CMD,
    MANAGED_MODE,
    MONITOR_MODE,
    MONITOR_MODE_SETTLE_SECONDS,
    NETWORK_MANAGER_SERVICE,
    PKILL_CMD,
    SYSTEMCTL_CMD,
    WPA_SUPPLICANT_PROCESS,
)


def configure_monitor_mode(iface):
    cprint("[*] Killing conflicting network processes...", "blue")
    try:
        subprocess.run([AIRMON_CMD, "check", "kill"], capture_output=True, check=False)
    except FileNotFoundError:
        subprocess.run(
            [SYSTEMCTL_CMD, "stop", NETWORK_MANAGER_SERVICE], capture_output=True, check=False
        )
        subprocess.run([PKILL_CMD, WPA_SUPPLICANT_PROCESS], capture_output=True, check=False)

    cprint(f"[*] Bringing {iface} down...", "blue")
    run_command([IP_CMD, "link", "set", iface, "down"])

    cprint(f"[*] Setting {iface} type to monitor...", "blue")
    run_command([IW_CMD, "dev", iface, "set", "type", MONITOR_MODE])

    cprint(f"[*] Bringing {iface} up...", "blue")
    run_command([IP_CMD, "link", "set", iface, "up"])
    time.sleep(MONITOR_MODE_SETTLE_SECONDS)

    cprint(
        f"[+] Successfully configured {iface} in monitor mode!",
        "green",
    )


def configure_default_mode(iface):
    cprint(f"[*] Bringing {iface} down...", "blue")
    run_command([IP_CMD, "link", "set", iface, "down"])

    cprint(f"[*] Setting {iface} type to managed...", "blue")
    run_command([IW_CMD, "dev", iface, "set", "type", MANAGED_MODE])

    cprint(f"[*] Bringing {iface} up...", "blue")
    run_command([IP_CMD, "link", "set", iface, "up"])

    cprint("[*] Restarting background network processes...", "blue")
    subprocess.run(
        [SYSTEMCTL_CMD, "start", NETWORK_MANAGER_SERVICE], capture_output=True, check=False
    )

    cprint(f"[+] Successfully configured {iface} in managed mode!", "green")


def configure_fixed_channel(iface, channel):
    cprint(f"[*] Locking {iface} to channel {channel}...", "blue")
    run_command([IW_CMD, "dev", iface, "set", "channel", channel])

    cprint(f"[+] Successfully configured {iface} to channel {channel}!", "green")

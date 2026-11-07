import csv
import os
import subprocess
import time

from colored import Fore, Style, cprint

from constants import (
    AIRODUMP_CMD,
    DEFAULT_SCAN_TIME_SECONDS,
    SCAN_OUTPUT_PREFIX,
    SCAN_OUTPUT_SUFFIX,
)


def scan_networks(iface, scan_time):
    output_prefix = SCAN_OUTPUT_PREFIX

    cprint("[*] Starting Wi-Fi discovery...", "blue")

    process = subprocess.Popen(
        [AIRODUMP_CMD, "--output-format", "csv", "-w", output_prefix, iface],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        if not scan_time or not scan_time.isnumeric():
            scan_time = DEFAULT_SCAN_TIME_SECONDS
        time.sleep(int(scan_time))
    finally:
        process.terminate()
        process.wait()

    csv_file = f"{output_prefix}{SCAN_OUTPUT_SUFFIX}"

    if not os.path.exists(csv_file):
        cprint("[-] Scan results not found", "red")
        return []

    networks = []

    with open(csv_file, newline="", encoding="utf-8", errors="replace") as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) < 14:
                continue

            bssid = row[0].strip()

            if bssid.lower() == "bssid" or not bssid:
                continue

            networks.append(
                {
                    "bssid": bssid,
                    "channel": row[3].strip(),
                    "privacy": row[5].strip(),
                    "ssid": row[13].strip(),
                }
            )

    os.remove(csv_file)

    return networks


def display_networks(networks):
    if not networks:
        cprint("[-] No networks found", "red")
        return

    cprint("\n[*] Available Wi-Fi networks:\n", "blue")

    for index, network in enumerate(networks, 1):
        cprint(
            f"[{index}] "
            f"{network['ssid'] or '<Hidden SSID>'} | "
            f"{network['bssid']} | "
            f"Channel: {network['channel']} | "
            f"Security: {network['privacy']}",
            "blue",
        )


def select_network(networks):
    if not networks:
        return None

    while True:
        try:
            choice = int(input(f"{Fore.magenta}\n[*] Select network: {Style.reset}"))

            if 1 <= choice <= len(networks):
                return networks[choice - 1]

            cprint("[-] Invalid selection", "red")

        except ValueError:
            cprint("[-] Enter a valid number", "red")

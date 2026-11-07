import os
import subprocess
import sys

from colored import Fore, Style, cprint

import packet_capture as pc
import scanner
from constants import AIRCRACK_CMD
from monitor import (
    configure_default_mode,
    configure_fixed_channel,
    configure_monitor_mode,
)


def main() -> None:
    try:
        if os.geteuid() != 0:
            print("[-] Error: This script must be run as a root (use sudo).")
            sys.exit(1)

        iface = input(
            f"{Fore.magenta}[*] Please enter name of your wireless interface:"
            f" {Style.reset}"
        )
        scan_time = input(
            f"{Fore.magenta}[*] Please enter scan time in seconds (default is 15):"
            f" {Style.reset}"
        )

        configure_monitor_mode(iface)

        networks = scanner.scan_networks(iface, scan_time)

        scanner.display_networks(networks)

        network = scanner.select_network(networks)

        if not network:
            sys.exit(1)

        channel = network.get("channel")
        output_prefix = network.get("ssid")
        bssid = network.get("bssid")

        configure_fixed_channel(iface, channel)

        success, capture_file = pc.sniffing(iface, channel, bssid, output_prefix)

        if success and os.path.exists(capture_file):
            print(
                f"\n{Fore.green}[+] Handshake file ready: {capture_file}{Style.reset}"
            )
            confirm = input(
                f"{Fore.yellow}[?] Valid handshake detected! Start aircrack-ng crack"
                f" sequence now? (y/n): {Style.reset}"
            )

            if confirm.lower().strip() == "y":
                wordlist = input(
                    f"{Fore.magenta}[*] Enter absolute path to your wordlist dictionary"
                    f" file: {Style.reset}"
                )
                if not os.path.exists(wordlist):
                    print(f"{Fore.red}[-] Error: Wordlist path not found.{Style.reset}")
                    return

                print(f"\n{Fore.cyan}[*] Launching aircrack-ng session...{Style.reset}")
                try:
                    subprocess.run(
                        [AIRCRACK_CMD, "-w", wordlist, capture_file], check=False
                    )
                except FileNotFoundError:
                    print(
                        f"{Fore.red}[-] Error: aircrack-ng executable not found on this"
                        f" system.{Style.reset}"
                    )
            else:
                print(f"{Fore.cyan}[*] Skipping automated cracking step.{Style.reset}")
        else:
            print(
                f"\n{Fore.red}[-] Capture terminated without securing a handshake"
                f" profile.{Style.reset}"
            )
    except KeyboardInterrupt:
        cprint("\n[*] Ctrl+C detected! Stopping airodump-ng safely...", "blue")
    finally:
        cprint("\n[*] Cleaning up and restoring system network settings...", "blue")
        configure_default_mode(iface)


if __name__ == "__main__":
    main()

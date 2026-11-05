import os
import sys

from colored import Fore, Style

import packet_capture as pc


def main() -> None:
    CHANNEL = input(f"{Fore.magenta}[*] Please enter target channel: {Style.reset}")
    IFACE = input(
        f"{Fore.magenta}[*] Please enter name of your wireless interface: {Style.reset}"
    )
    OUTPUT_PREFIX = input(
        f"{Fore.magenta}[*] Please enter name of output prefix for files: {Style.reset}"
    )

    if os.geteuid() != 0:
        print("[-] Error: This script must be run as a root (use sudo).")
        sys.exit(1)

    pc.configure_monitor_mode(IFACE, CHANNEL)

    pc.sniffing(IFACE, CHANNEL, OUTPUT_PREFIX)


if __name__ == "__main__":
    main()

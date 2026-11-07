import flet as ft

# External command names
AIRODUMP_CMD = "airodump-ng"
AIRCRACK_CMD = "aircrack-ng"
AIRMON_CMD = "airmon-ng"
IW_CMD = "iw"
IP_CMD = "ip"
SYSTEMCTL_CMD = "systemctl"
PKILL_CMD = "pkill"

# Network configuration
MONITOR_MODE = "monitor"
MANAGED_MODE = "managed"
NETWORK_MANAGER_SERVICE = "NetworkManager"
WPA_SUPPLICANT_PROCESS = "wpa_supplicant"
MONITOR_MODE_SETTLE_SECONDS = 2

# Wi-Fi scanning
DEFAULT_SCAN_TIME_SECONDS = 15
SCAN_OUTPUT_PREFIX = "/tmp/wifi_scan"
SCAN_OUTPUT_SUFFIX = "-01.csv"

# Packet capture
CAPTURE_OUTPUT_SUFFIX = "-01.cap"
HANDSHAKE_MARKER = "WPA handshake:"
PROCESS_READ_BUFFER_SIZE = 1

# User interface
APP_TITLE = "Cookie Cracker"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800
VERTICAL_ALIGMENT = ft.MainAxisAlignment.START
HORIZONTAL_ALIGMENT = ft.CrossAxisAlignment.CENTER
FONT_FAMILY = "Space Mono"

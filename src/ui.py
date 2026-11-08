import json
import os
import re
import subprocess
import threading

import flet as ft

from constants import (
    AIRCRACK_CMD,
    APP_TITLE,
    FONT_FAMILY,
    HORIZONTAL_ALIGNMENT,
    VERTICAL_ALIGNMENT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from monitor import configure_default_mode, configure_monitor_mode, get_mode
from packet_capture import sniffing, stop_sniff_process
from scanner import scan_networks


def main(page: ft.Page):
    page.title = APP_TITLE
    page.window.width = WINDOW_WIDTH
    page.window.max_width = WINDOW_WIDTH
    page.window.min_width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.max_height = WINDOW_HEIGHT
    page.window.min_height = WINDOW_HEIGHT
    page.vertical_alignment = VERTICAL_ALIGNMENT
    page.horizontal_alignment = HORIZONTAL_ALIGNMENT
    page.theme_mode = ft.ThemeMode.DARK
    page.dark_theme = ft.Theme(
        font_family=FONT_FAMILY,
        color_scheme_seed=ft.Colors.PURPLE,
        surfaces=ft.ThemeSurfaces.NEUTRAL,
        hover_color=ft.Colors.ON_INVERSE_SURFACE,
    )
    page.update()

    def handle_adapter_field_change(e):
        mode = get_mode(adapter_field.value)
        current_adapter_mode_text.value = f"Interface mode: {mode.capitalize()}"
        start_scan_button.disabled = get_mode(adapter_field.value) != "monitor"
        mode_toggle.disabled = mode != "monitor" and mode != "managed"
        mode_toggle.value = mode == "monitor"
        page.update()

    def handle_switch_mode_change(e):
        if e.control.value:
            configure_monitor_mode(adapter_field.value)
            mode = "monitor"
        else:
            configure_default_mode(adapter_field.value)
            mode = "managed"
        current_adapter_mode_text.value = f"Interface mode: {mode.capitalize()}"
        start_scan_button.disabled = mode != "monitor"
        page.update()

    def handle_scan_button(e):
        data_container_column.controls = [
            ft.Text(
                "Scanning...",
                color=ft.Colors.ON_PRIMARY_CONTAINER,
                text_align=ft.TextAlign.CENTER,
                size=20,
                width=450,
            )
        ]
        page.update()
        networks = scan_networks(adapter_field.value, "10")

        network_radio_buttons = []

        for network in networks:
            network_radio_buttons.append(
                ft.Radio(
                    value=network,
                    label=network["ssid"] or "<Hidden SSID>",
                    tooltip=f"SSID: {network['ssid'] or '<Hidden SSID>'}\n"
                    f"Channel: {network['channel']}\n"
                    f"BSSID: {network['bssid']}\n"
                    f"Security: {network['privacy']}",
                    label_style=ft.TextStyle(color=ft.Colors.ON_PRIMARY_CONTAINER),
                )
            )

        networks_group.content = ft.Column(network_radio_buttons)

        content = ft.Column(
            controls=[
                ft.Text(
                    "Scan complete!",
                    color=ft.Colors.ON_PRIMARY_CONTAINER,
                    text_align=ft.TextAlign.CENTER,
                    size=20,
                    width=450,
                ),
                ft.Text("Select network:", color=ft.Colors.ON_PRIMARY_CONTAINER),
                networks_group,
                ft.Button(
                    content="Submit & Sniff",
                    on_click=handle_network_choice,
                ),
            ]
        )
        data_container_column.controls = content
        page.update()

    def handle_network_choice(e):
        adapter_field.disabled = True
        start_scan_button.disabled = True
        mode_toggle.disabled = True
        raw_value = networks_group.value
        cleaned_value = re.sub(r"([{,]\s*)([a-zA-Z0-9_]+)\s*:", r'\1"\2":', raw_value)
        cleaned_value = re.sub(
            r":\s*([a-zA-Z0-9_:.-]+)(?=\s*[,}])", r': "\1"', cleaned_value
        )

        selected_network = json.loads(cleaned_value)

        if not selected_network:
            return

        status_text = ft.Text(
            "Starting sniffing process...",
            color=ft.Colors.ON_PRIMARY_CONTAINER,
            text_align=ft.TextAlign.CENTER,
            size=16,
        )

        def stop_sniffing(e):
            stop_sniff_process()
            stop_sniffing_button.disabled = True
            status_text.value = "Sniffing manually stopped."
            adapter_field.disabled = False
            start_scan_button.disabled = False
            mode_toggle.disabled = False
            page.update()

        stop_sniffing_button = ft.Button(
            content="Stop sniffing", icon=ft.Icons.STOP, on_click=stop_sniffing
        )

        data_container_column.controls = [status_text, stop_sniffing_button]
        page.update()

        def update_status(msg):
            status_text.value = msg
            page.update()

        def start_aircrack(capture_file):
            wordlist_field = ft.TextField(
                label="Шлях до словника",
                hint_text="/usr/share/wordlists/rockyou.txt",
                text_style=ft.TextStyle(size=14, font_family_fallback="Monospace"),
            )
            crack_status = ft.Text("", color=ft.Colors.ON_PRIMARY_CONTAINER, size=14)

            def run_crack(e):
                wordlist = wordlist_field.value.strip()
                if not wordlist or not os.path.exists(wordlist):
                    crack_status.value = (
                        "Помилка: файл словника не знайдено за цим шляхом."
                    )
                    page.update()
                    return

                crack_status.value = "Запуск aircrack-ng..."
                start_crack_button.disabled = True
                page.update()

                def background_crack():
                    try:
                        res = subprocess.run(
                            [AIRCRACK_CMD, "-w", wordlist, capture_file],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        if res.returncode == 0:
                            crack_status.value = (
                                f"Aircrack завершено успішно!\n{res.stdout[-400:]}"
                            )
                        else:
                            crack_status.value = f"Завершено. Результат:\n{res.stderr[-300:] or res.stdout[-300:]}"
                    except FileNotFoundError:
                        crack_status.value = "Помилка: утиліту aircrack-ng не знайдено."

                    start_crack_button.disabled = False
                    page.update()

                threading.Thread(target=background_crack, daemon=True).start()

            start_crack_button = ft.Button(
                content="Start Aircrack-ng",
                icon=ft.Icons.PLAY_ARROW,
                on_click=run_crack,
            )

            data_container_column.controls.extend(
                [
                    ft.Divider(),
                    ft.Text(
                        "Handshake успішно захоплено!",
                        color=ft.Colors.GREEN,
                        size=16,
                    ),
                    wordlist_field,
                    start_crack_button,
                    crack_status,
                ]
            )
            page.update()

        def run_sniffing_background():
            update_status("Sniffing started...")
            success, target_file = sniffing(
                iface=adapter_field.value,
                channel=selected_network["channel"],
                bssid=selected_network["bssid"],
                callback_status=update_status,
            )
            stop_sniffing_button.disabled = True
            if success and os.path.exists(target_file):
                update_status(f"Sniffing completed! Handshake saved to {target_file}")
                start_aircrack(target_file)
            else:
                update_status("Sniffing finished or stopped.")

            adapter_field.disabled = False
            start_scan_button.disabled = False
            mode_toggle.disabled = False
            page.update()

        threading.Thread(target=run_sniffing_background, daemon=True).start()

    title_text = ft.Text(
        APP_TITLE,
        text_align=ft.TextAlign.CENTER,
        size=42,
        font_family_fallback="Monospace",
    )

    adapter_field = ft.TextField(
        value="",
        hint_text="wlan0",
        label="Interface",
        text_style=ft.TextStyle(size=18, font_family_fallback="Monospace"),
        hint_style=ft.TextStyle(size=18, font_family_fallback="Monospace"),
        label_style=ft.TextStyle(size=18, font_family_fallback="Monospace"),
        on_submit=handle_adapter_field_change,
    )
    current_adapter_mode_text = ft.Text(
        f"Interface mode: {get_mode(adapter_field.value)}",
        size=18,
        text_align=ft.TextAlign.CENTER,
        font_family_fallback="Monospace",
    )

    networks_group = ft.RadioGroup(None)

    start_scan_button = ft.Button(
        content="Start scan",
        icon=ft.Icons.WIFI_FIND,
        disabled=True,
        on_click=handle_scan_button,
    )

    mode_toggle = ft.Switch(
        label="Monitor mode",
        value=get_mode(adapter_field.value) == "managed",
        disabled=True,
        on_change=handle_switch_mode_change,
    )

    button_row = ft.Row(
        [start_scan_button, mode_toggle], alignment=HORIZONTAL_ALIGNMENT
    )

    underline = ft.Divider(thickness=2, color=ft.Colors.ON_SURFACE)

    data_container_column = ft.Column(
        [], scroll=ft.ScrollMode.AUTO, horizontal_alignment=HORIZONTAL_ALIGNMENT
    )

    data_container = ft.Container(
        content=data_container_column,
        width=450,
        height=400,
        bgcolor=ft.Colors.ON_PRIMARY,
        border_radius=10,
        padding=20,
    )

    main_column = ft.Column(
        [
            title_text,
            underline,
            ft.Container(height=10),
            current_adapter_mode_text,
            adapter_field,
            underline,
            button_row,
            ft.Container(height=10),
            data_container,
        ],
        horizontal_alignment=HORIZONTAL_ALIGNMENT,
    )

    page.add(
        ft.Container(
            content=main_column,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            border_radius=20,
            border=ft.Border.all(width=2, color=ft.Colors.ON_SURFACE),
        )
    )


ft.run(main, view=ft.AppView.WEB_BROWSER)

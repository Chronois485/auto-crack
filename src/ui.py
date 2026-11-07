import flet as ft

from constants import (
    APP_TITLE,
    FONT_FAMILY,
    HORIZONTAL_ALIGMENT,
    VERTICAL_ALIGMENT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from monitor import get_mode


def main(page: ft.Page):
    page.title = APP_TITLE
    page.window.width = WINDOW_WIDTH
    page.window.max_width = WINDOW_WIDTH
    page.window.min_width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.max_height = WINDOW_HEIGHT
    page.window.min_height = WINDOW_HEIGHT
    page.vertical_alignment = VERTICAL_ALIGMENT
    page.horizontal_alignment = HORIZONTAL_ALIGMENT
    page.theme_mode = ft.ThemeMode.DARK
    page.dark_theme = ft.Theme(
        font_family=FONT_FAMILY,
        color_scheme_seed=ft.Colors.PURPLE,
        surfaces=ft.ThemeSurfaces.NEUTRAL,
        hover_color=ft.Colors.ON_INVERSE_SURFACE,
    )
    page.update()

    def handle_adapter_field_change(e):
        current_adapter_mode_text.value = (
            f"Interface mode: {get_mode(adapter_field.value).capitalize()}"
        )
        start_scan_button.disabled = get_mode(adapter_field.value) != "monitor"
        page.update()

    title_text = ft.Text(APP_TITLE, text_align=ft.TextAlign.CENTER, size=42)

    adapter_field = ft.TextField(
        value="",
        hint_text="wlan0",
        label="Interface",
        text_style=ft.TextStyle(size=18),
        hint_style=ft.TextStyle(size=18),
        label_style=ft.TextStyle(size=18),
        on_submit=handle_adapter_field_change,
    )
    current_adapter_mode_text = ft.Text(
        f"Interface mode: {get_mode(adapter_field.value)}",
        size=18,
        text_align=ft.TextAlign.CENTER,
    )

    start_scan_button = ft.Button(
        content="Start scan",
        icon=ft.Icons.WIFI_FIND,
        disabled=get_mode(adapter_field.value) != "monitor",
    )

    underline = ft.Divider(thickness=2)

    data_container_column = ft.Column([], scroll=ft.ScrollMode.AUTO)

    data_container = ft.Container(
        data_container_column,
        width=450,
        height=400,
        bgcolor=ft.Colors.ON_PRIMARY,
        border_radius=10,
    )

    main_column = ft.Column(
        [
            title_text,
            underline,
            ft.Container(height=10),
            current_adapter_mode_text,
            adapter_field,
            underline,
            start_scan_button,
            ft.Container(height=10),
            data_container,
        ],
        horizontal_alignment=HORIZONTAL_ALIGMENT,
    )

    page.add(main_column)


ft.run(main)

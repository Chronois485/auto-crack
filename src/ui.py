import flet as ft

from constants import APP_TITLE, WINDOW_HEIGHT, WINDOW_WIDTH


def main(page: ft.Page):
    page.title = APP_TITLE
    page.window.width = WINDOW_WIDTH
    page.window.max_width = WINDOW_WIDTH
    page.window.min_width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.max_height = WINDOW_HEIGHT
    page.window.min_height = WINDOW_HEIGHT


ft.run(main)

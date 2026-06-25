import customtkinter as ctk

_current_appearance_mode = "light"


def apply_theme():
    ctk.set_appearance_mode(_current_appearance_mode)
    ctk.set_default_color_theme("blue")


def get_appearance_mode():
    return _current_appearance_mode


def set_appearance_mode(mode):
    global _current_appearance_mode

    normalized = "dark" if str(mode).lower() == "dark" else "light"
    _current_appearance_mode = normalized
    ctk.set_appearance_mode(normalized)


def is_dark_mode():
    return _current_appearance_mode == "dark"

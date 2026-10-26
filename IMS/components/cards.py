"""
IMS — Reusable Dashboard Card Components
Stat cards and info cards styled per DESIGN.md §4.4.
"""

import customtkinter as ctk
from config import COLORS


class StatCard(ctk.CTkFrame):
    """
    Dashboard stat card showing an icon, large number, and label.

    Args:
        master:  parent widget
        icon:    emoji string (e.g. "📊")
        value:   the number or metric to display
        label:   description text below the number
        accent:  optional color override for the value text
    """

    def __init__(self, master, icon: str, value, label: str,
                 accent: str = None, **kwargs):
        super().__init__(master, fg_color=COLORS["card_bg"],
                         corner_radius=8, border_width=1,
                         border_color=COLORS["border"], **kwargs)

        pad_frame = ctk.CTkFrame(self, fg_color="transparent")
        pad_frame.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            pad_frame, text=icon, font=("Segoe UI", 28)
        ).pack(anchor="w")

        ctk.CTkLabel(
            pad_frame, text=str(value),
            font=("Segoe UI", 32, "bold"),
            text_color=accent or COLORS["primary"]
        ).pack(anchor="w", pady=(6, 2))

        ctk.CTkLabel(
            pad_frame, text=label,
            font=("Segoe UI", 13),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w")


class InfoCard(ctk.CTkFrame):
    """
    Information card with key-value pairs.

    Args:
        master:  parent widget
        title:   card title
        data:    dict of {label: value}
    """

    def __init__(self, master, title: str, data: dict, **kwargs):
        super().__init__(master, fg_color=COLORS["card_bg"],
                         corner_radius=8, border_width=1,
                         border_color=COLORS["border"], **kwargs)

        ctk.CTkLabel(
            self, text=title, font=("Segoe UI", 16, "bold"),
            text_color=COLORS["primary"]
        ).pack(anchor="w", padx=20, pady=(16, 8))

        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=16
        )

        for key, val in data.items():
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(
                row, text=key, font=("Segoe UI", 13),
                text_color=COLORS["text_muted"], width=140, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=str(val) if val else "—",
                font=("Segoe UI", 13, "bold"),
                text_color=COLORS["text_dark"], anchor="w"
            ).pack(side="left", fill="x", expand=True)

        # Bottom padding
        ctk.CTkFrame(self, height=12, fg_color="transparent").pack()


class StatusBadge(ctk.CTkLabel):
    """Inline colored status badge."""

    def __init__(self, master, status: str, **kwargs):
        from config import BADGE_STYLES
        style = BADGE_STYLES.get(
            status.lower(), {"bg": "#EAECEE", "fg": "#7F8C8D"}
        )
        super().__init__(
            master, text=f"  {status.capitalize()}  ",
            font=("Segoe UI", 11, "bold"),
            fg_color=style["bg"], text_color=style["fg"],
            corner_radius=12, height=26, **kwargs
        )

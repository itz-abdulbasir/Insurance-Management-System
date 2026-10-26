"""
IMS — Reusable Sidebar Component
A vertical navigation panel styled per DESIGN.md §4.1.
"""

import customtkinter as ctk
from config import COLORS


class Sidebar(ctk.CTkFrame):
    """
    Role-aware sidebar navigation.

    Args:
        master:       parent widget
        nav_items:    list of dicts  [{"label": "Dashboard", "icon": "📊", "command": fn}, ...]
        user_name:    display name of the logged-in user
        role_label:   "Admin" | "Agent" | "Customer"
        logout_cmd:   callback for the logout button
    """

    def __init__(self, master, nav_items: list, user_name: str,
                 role_label: str, logout_cmd, **kwargs):
        super().__init__(master, width=200, corner_radius=0,
                         fg_color=COLORS["primary"], **kwargs)
        self.pack_propagate(False)
        self.nav_buttons: list[ctk.CTkButton] = []
        self._active_index = 0

        # ── Brand header ────────────────────────────────────────────
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(fill="x", padx=16, pady=(20, 4))
        ctk.CTkLabel(
            brand, text="IMS", font=("Segoe UI", 22, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand, text="Insurance Mgmt System",
            font=("Segoe UI", 11), text_color=COLORS["sidebar_text"]
        ).pack(anchor="w")

        # ── User info ───────────────────────────────────────────────
        user_frame = ctk.CTkFrame(self, fg_color=COLORS["sidebar_hover"],
                                  corner_radius=6)
        user_frame.pack(fill="x", padx=12, pady=(12, 16))
        ctk.CTkLabel(
            user_frame, text=user_name, font=("Segoe UI", 13, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(
            user_frame, text=role_label,
            font=("Segoe UI", 11), text_color=COLORS["sidebar_text"]
        ).pack(anchor="w", padx=10, pady=(0, 8))

        # ── Divider ─────────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color="#2874A6").pack(fill="x", padx=12)

        # ── Navigation buttons ──────────────────────────────────────
        nav_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["sidebar_hover"]
        )
        nav_container.pack(fill="both", expand=True, padx=0, pady=(8, 8))

        for idx, item in enumerate(nav_items):
            btn = ctk.CTkButton(
                nav_container,
                text=f"  {item.get('icon', '')}  {item['label']}",
                font=("Segoe UI", 13),
                fg_color="transparent",
                text_color=COLORS["sidebar_text"],
                hover_color=COLORS["sidebar_hover"],
                anchor="w",
                height=38,
                corner_radius=6,
                command=lambda i=idx, c=item["command"]: self._on_nav(i, c)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_buttons.append(btn)

        # Highlight first button
        if self.nav_buttons:
            self._highlight(0)

        # ── Logout button (pinned to bottom) ────────────────────────
        ctk.CTkFrame(self, height=1, fg_color="#2874A6").pack(
            fill="x", padx=12, side="bottom"
        )
        ctk.CTkButton(
            self, text="🚪  Logout", font=("Segoe UI", 13),
            fg_color="transparent", text_color="#E74C3C",
            hover_color=COLORS["sidebar_hover"],
            anchor="w", height=38, corner_radius=6,
            command=logout_cmd
        ).pack(fill="x", padx=8, pady=(4, 16), side="bottom")

    # ── Internal ────────────────────────────────────────────────────
    def _on_nav(self, index: int, command):
        self._highlight(index)
        command()

    def _highlight(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.configure(fg_color=COLORS["accent"], text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent",
                              text_color=COLORS["sidebar_text"])
        self._active_index = index

"""
IMS — Reusable Table View Component
Scrollable data table with status badges, styled per DESIGN.md §4.3.
"""

import customtkinter as ctk
from config import COLORS, BADGE_STYLES


class TableView(ctk.CTkFrame):
    """
    Scrollable data table.

    Args:
        master:       parent widget
        columns:      list of dicts [{"key": "policy_id", "label": "Policy ID", "width": 80}, ...]
        data:         list of dicts (rows)
        on_row_click: optional callback(row_dict) when a row is clicked
        badge_col:    optional column key whose values render as status badges
    """

    def __init__(self, master, columns: list, data: list = None,
                 on_row_click=None, badge_col: str = None, action_config: dict = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.columns = columns
        self.on_row_click = on_row_click
        self.badge_col = badge_col
        self.action_config = action_config
        self._row_frames = []

        # ── Header row ──────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["table_header"],
                              corner_radius=0, height=40)
        header.pack(fill="x")
        header.pack_propagate(False)

        for col in columns:
            ctk.CTkLabel(
                header, text=col["label"],
                font=("Segoe UI", 12, "bold"),
                text_color=COLORS["primary"],
                width=col.get("width", 120),
                anchor="w"
            ).pack(side="left", padx=(16, 4), pady=8)

        if self.action_config:
            ctk.CTkLabel(header, text=self.action_config.get("header", "Action"), 
                         font=("Segoe UI", 12, "bold"), text_color=COLORS["primary"], 
                         width=80).pack(side="right", padx=(16, 16), pady=8)

        # ── Scrollable body ─────────────────────────────────────────
        self.body = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"]
        )
        self.body.pack(fill="both", expand=True)

        if data:
            self.load_data(data)

    def load_data(self, data: list):
        """Clear existing rows and load new data."""
        for frame in self._row_frames:
            frame.destroy()
        self._row_frames.clear()

        if not data:
            empty = ctk.CTkLabel(
                self.body, text="No records found.",
                font=("Segoe UI", 14), text_color=COLORS["text_muted"]
            )
            empty.pack(pady=40)
            self._row_frames.append(empty)
            return

        for idx, row in enumerate(data):
            bg = COLORS["card_bg"] if idx % 2 == 0 else COLORS["table_alt"]
            row_frame = ctk.CTkFrame(self.body, fg_color=bg,
                                     corner_radius=0, height=40)
            row_frame.pack(fill="x")
            row_frame.pack_propagate(False)

            # Determine row text color (default to text_dark if not specified)
            row_text_color = row.get("row_text_color", COLORS["text_dark"])

            for col in self.columns:
                val = row.get(col["key"], "")
                if val is None:
                    val = "—"

                if col["key"] == self.badge_col and val:
                    badge = self._make_badge(row_frame, str(val))
                    badge.pack(side="left", padx=(16, 4), pady=6)
                else:
                    lbl = ctk.CTkLabel(
                        row_frame, text=str(val),
                        font=("Segoe UI", 12),
                        text_color=row_text_color,
                        width=col.get("width", 120),
                        anchor="w"
                    )
                    lbl.pack(side="left", padx=(16, 4), pady=8)

            if self.action_config:
                # Support both single dict or list of dicts
                configs = self.action_config if isinstance(self.action_config, list) else [self.action_config]
                
                # Pack from right to left
                for cfg in reversed(configs):
                    cond = cfg.get("condition")
                    if not cond or cond(row):
                        btn = ctk.CTkButton(
                            row_frame, text=cfg.get("text", "Action"),
                            font=("Segoe UI", 11, "bold"),
                            fg_color=cfg.get("fg_color", COLORS["primary"]),
                            width=cfg.get("width", 80), height=26,
                            hover_color=cfg.get("hover_color"),
                            command=lambda r=row, c=cfg: c["command"](r)
                        )
                        btn.pack(side="right", padx=(4, 16), pady=6)

            # Row click binding
            if self.on_row_click:
                row_data = row
                row_frame.configure(cursor="hand2")
                row_frame.bind("<Enter>",
                    lambda e, f=row_frame: f.configure(fg_color=COLORS["table_header"]))
                row_frame.bind("<Leave>",
                    lambda e, f=row_frame, b=bg: f.configure(fg_color=b))
                row_frame.bind("<Button-1>",
                    lambda e, r=row_data: self.on_row_click(r))
                for child in row_frame.winfo_children():
                    child.bind("<Button-1>",
                        lambda e, r=row_data: self.on_row_click(r))

            self._row_frames.append(row_frame)

    def _make_badge(self, parent, status: str) -> ctk.CTkLabel:
        """Create a colored status badge label."""
        status_lower = status.lower()
        style = BADGE_STYLES.get(status_lower, {"bg": "#EAECEE", "fg": "#7F8C8D"})
        return ctk.CTkLabel(
            parent, text=f"  {status.capitalize()}  ",
            font=("Segoe UI", 11, "bold"),
            fg_color=style["bg"],
            text_color=style["fg"],
            corner_radius=12,
            height=26
        )

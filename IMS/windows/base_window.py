import customtkinter as ctk
from config import COLORS, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from db.connection import execute_query

class BaseWindow(ctk.CTkToplevel):
    def __init__(self, app_root, user: dict, login_window, title: str):
        super().__init__()
        self.app_root = app_root
        self.user = user
        self.login_window = login_window
        self.title(title)
        self.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(fg_color=COLORS["bg_light"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _clear(self):
        """Clears the main content frame."""
        for w in self.content.winfo_children():
            w.destroy()

    def _make_scroll(self):
        """Creates and returns a standardized scrollable frame."""
        s = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        s.pack(fill="both", expand=True, padx=24, pady=16)
        return s

    def _heading(self, parent, text):
        """Creates a standardized heading label."""
        ctk.CTkLabel(parent, text=text, font=("Segoe UI", 20, "bold"),
                     text_color=COLORS["primary"]).pack(anchor="w", pady=(0, 16))

    def _show_msg(self, text, err=False):
        """Shows a popup message."""
        msg = ctk.CTkToplevel(self)
        msg.title("Notice")
        msg.geometry("380x120")
        msg.resizable(False, False)
        msg.grab_set()
        ctk.CTkLabel(msg, text=text, font=("Segoe UI", 14),
                     text_color=COLORS["danger"] if err else COLORS["success"],
                     wraplength=340).pack(expand=True, padx=20, pady=10)
        ctk.CTkButton(msg, text="OK", width=80, command=msg.destroy).pack(pady=(0, 16))

    def _logout(self):
        """Logs out the user and shows the login window."""
        execute_query("INSERT INTO audit_log (user_id, action) VALUES (%s,%s)",
                      (self.user["user_id"], "Logged out"))
        self.destroy()
        self.login_window.show_again()

    def _on_close(self):
        """Handles the window close event."""
        self.destroy()
        self.app_root.destroy()

    def _check_notifications(self):
        """Checks and displays unread notifications."""
        notifs = execute_query("SELECT notif_id, message FROM notifications WHERE user_id = %s AND is_read = 0", 
                               (self.user["user_id"],), fetch=True)
        if notifs:
            for n in notifs:
                self._show_msg(f"🔔 NOTIFICATION:\n{n['message']}")
                execute_query("UPDATE notifications SET is_read = 1 WHERE notif_id = %s", (n['notif_id'],))

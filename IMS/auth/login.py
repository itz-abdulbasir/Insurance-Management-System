"""
IMS — Login Window
Combined login gateway with role selection, routed to role dashboards.
Matches SRS §7.1 (FR-A1 through FR-A5) and §11.1 login flow.
"""

import customtkinter as ctk
import bcrypt
from config import COLORS, APP_NAME, LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT
from db.connection import execute_query


class LoginWindow(ctk.CTk):
    """Login screen: email + password + role dropdown → role dashboard."""

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — Login")
        self.geometry(f"{LOGIN_WINDOW_WIDTH}x{LOGIN_WINDOW_HEIGHT}")
        self.resizable(True, True)
        self.minsize(LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT)
        self._center_window()
        self.configure(fg_color=COLORS["bg_light"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self.grab_set()

    # ── UI Construction ─────────────────────────────────────────────
    def _build_ui(self):
        # Main card
        card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"],
                            corner_radius=12, border_width=1,
                            border_color=COLORS["border"])
        card.place(relx=0.5, rely=0.5, anchor="center",
                   relwidth=0.82, relheight=0.92)

        # Header
        header = ctk.CTkFrame(card, fg_color=COLORS["primary"],
                              corner_radius=12, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header, text="🏢  Insurance Management System",
            font=("Segoe UI", 18, "bold"), text_color="#FFFFFF"
        ).pack(expand=True)

        # Form area
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40, pady=(16, 12))

        ctk.CTkLabel(
            form, text="Sign in to your account",
            font=("Segoe UI", 16, "bold"), text_color=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 14))

        # Email
        ctk.CTkLabel(
            form, text="Email Address",
            font=("Segoe UI", 13), text_color=COLORS["text_muted"]
        ).pack(anchor="w")
        self.email_entry = ctk.CTkEntry(
            form, placeholder_text="you@example.com",
            font=("Segoe UI", 14), height=38,
            border_color=COLORS["border"]
        )
        self.email_entry.pack(fill="x", pady=(4, 10))

        # Password
        ctk.CTkLabel(
            form, text="Password",
            font=("Segoe UI", 13), text_color=COLORS["text_muted"]
        ).pack(anchor="w")
        self.password_entry = ctk.CTkEntry(
            form, placeholder_text="Enter your password",
            font=("Segoe UI", 14), height=38, show="●",
            border_color=COLORS["border"]
        )
        self.password_entry.pack(fill="x", pady=(4, 10))

        # Role selector
        ctk.CTkLabel(
            form, text="Login As",
            font=("Segoe UI", 13), text_color=COLORS["text_muted"]
        ).pack(anchor="w")
        self.role_var = ctk.StringVar(value="customer")
        self.role_menu = ctk.CTkComboBox(
            form, values=["customer", "agent", "admin"],
            variable=self.role_var, font=("Segoe UI", 14),
            height=38, border_color=COLORS["border"],
            dropdown_hover_color=COLORS["accent"],
            state="readonly"
        )
        self.role_menu.pack(fill="x", pady=(4, 12))

        # Error label (inline red — never popup per SRS §8)
        self.error_label = ctk.CTkLabel(
            form, text="", font=("Segoe UI", 12),
            text_color=COLORS["danger"]
        )
        self.error_label.pack(anchor="w")

        # Login button
        ctk.CTkButton(
            form, text="Login", font=("Segoe UI", 15, "bold"),
            height=44, corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color="#2471A3",
            command=self._do_login
        ).pack(fill="x", pady=(6, 10))

        # Register link (always visible)
        reg_frame = ctk.CTkFrame(form, fg_color="transparent")
        reg_frame.pack(fill="x")
        ctk.CTkLabel(
            reg_frame, text="New user?",
            font=("Segoe UI", 13), text_color=COLORS["text_muted"]
        ).pack(side="left")
        ctk.CTkButton(
            reg_frame, text="Register here",
            font=("Segoe UI", 13, "bold"),
            fg_color="transparent", text_color=COLORS["accent"],
            hover_color=COLORS["bg_light"], width=100,
            command=self._open_register
        ).pack(side="left")

        # Additional register prompt shown on failed login
        self.register_prompt = ctk.CTkFrame(form, fg_color=COLORS["table_header"],
                                            corner_radius=8)
        self.register_prompt.pack(fill="x", pady=(8, 0))
        self.register_prompt.pack_forget()  # hidden by default

        prompt_inner = ctk.CTkFrame(self.register_prompt, fg_color="transparent")
        prompt_inner.pack(padx=12, pady=8)
        ctk.CTkLabel(
            prompt_inner, text="Don't have an account?",
            font=("Segoe UI", 12), text_color=COLORS["text_dark"]
        ).pack(side="left")
        ctk.CTkButton(
            prompt_inner, text="Sign up now →",
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["accent"], hover_color="#2471A3",
            width=120, height=30, corner_radius=6,
            command=self._open_register
        ).pack(side="left", padx=(8, 0))

        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self._do_login())

    # ── Login Logic ─────────────────────────────────────────────────
    def _do_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not email or not password:
            self.error_label.configure(text="Please fill in all fields.")
            self.register_prompt.pack_forget()
            return

        try:
            rows = execute_query(
                "SELECT * FROM users WHERE email = %s AND role = %s",
                (email, role), fetch=True
            )
        except Exception as e:
            self.error_label.configure(text=f"Database error: {e}")
            return

        if not rows:
            # Audit log for unknown user
            try:
                execute_query(
                    "INSERT INTO audit_log (user_id, action) VALUES (NULL, %s)",
                    (f"Login failed: user not found ({email})",)
                )
            except Exception: pass
            
            self.error_label.configure(text="Invalid credentials. Try again.")
            self.register_prompt.pack(fill="x", pady=(8, 0))
            return

        user = rows[0]
        if not user.get("is_active", True):
            self.error_label.configure(text="Account pending approval or deactivated. Contact admin.")
            return

        # bcrypt verify
        try:
            stored = user["password_hash"]
            if isinstance(stored, str):
                stored = stored.encode("utf-8")
            if not bcrypt.checkpw(password.encode("utf-8"), stored):
                # Audit log for incorrect password
                try:
                    execute_query(
                        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
                        (user["user_id"], "Failed login attempt: incorrect password")
                    )
                except Exception: pass
                
                self.error_label.configure(text="Invalid credentials. Try again.")
                self.register_prompt.pack(fill="x", pady=(8, 0))
                return
        except Exception:
            self.error_label.configure(text="Invalid credentials. Try again.")
            return

        # Audit log
        try:
            execute_query(
                "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
                (user["user_id"], f"Logged in as {role}")
            )
        except Exception:
            pass

        # Success → open role dashboard
        self.error_label.configure(text="")
        self.register_prompt.pack_forget()
        self._open_dashboard(user)

    def _open_dashboard(self, user: dict):
        """Open the correct dashboard window based on user role."""
        role = user["role"]
        self.grab_release()
        self.withdraw()

        if role == "admin":
            from windows.admin_window import AdminWindow
            AdminWindow(self, user, self)
        elif role == "agent":
            from windows.agent_window import AgentWindow
            AgentWindow(self, user, self)
        else:
            from windows.customer_window import CustomerWindow
            CustomerWindow(self, user, self)

    # ── Register ────────────────────────────────────────────────────
    def _open_register(self):
        from auth.register import RegisterWindow
        self.withdraw()
        RegisterWindow(self, self)

    # ── Helpers ─────────────────────────────────────────────────────
    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - LOGIN_WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - LOGIN_WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

    def show_again(self):
        """Called when returning from register or dashboard logout."""
        self.deiconify()
        self.grab_set()
        self.error_label.configure(text="")
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")

    def _on_close(self):
        self.destroy()

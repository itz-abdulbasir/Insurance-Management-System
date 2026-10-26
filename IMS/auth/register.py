"""
IMS — Registration Window
Customer and Agent registration forms.
Matches SRS §7.1 (FR-A5 through FR-A8) and §11.1 registration flow.
"""

import customtkinter as ctk
import bcrypt
from config import COLORS, APP_NAME, REGISTER_WINDOW_WIDTH, REGISTER_WINDOW_HEIGHT, ADMIN_PASSKEY, AGENT_PASSKEY
from db.connection import execute_query
from utils.validators import (validate_email, validate_phone,
                               validate_password, validate_name,
                               validate_dob, validate_required)


class RegisterWindow(ctk.CTkToplevel):
    """Registration screen with Customer / Agent tabs."""

    def __init__(self, app_root, login_window):
        super().__init__()
        self.app_root = app_root
        self.login_window = login_window
        self.title(f"{APP_NAME} — Register")
        self.geometry(f"{REGISTER_WINDOW_WIDTH}x{REGISTER_WINDOW_HEIGHT}")
        self.resizable(True, True)
        self.minsize(REGISTER_WINDOW_WIDTH, REGISTER_WINDOW_HEIGHT)
        self._center_window()
        self.configure(fg_color=COLORS["bg_light"])
        self.protocol("WM_DELETE_WINDOW", self._go_back)

        self._build_ui()
        self.grab_set()

    def _build_ui(self):
        card = ctk.CTkFrame(self, fg_color=COLORS["card_bg"],
                            corner_radius=12, border_width=1,
                            border_color=COLORS["border"])
        card.place(relx=0.5, rely=0.5, anchor="center",
                   relwidth=0.88, relheight=0.94)

        # Header
        header = ctk.CTkFrame(card, fg_color=COLORS["primary"],
                              corner_radius=12, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header, text="📝  Create New Account",
            font=("Segoe UI", 17, "bold"), text_color="#FFFFFF"
        ).pack(expand=True)

        # Tab selector: Customer | Agent
        tab_frame = ctk.CTkFrame(card, fg_color="transparent")
        tab_frame.pack(fill="x", padx=30, pady=(16, 0))

        self.tab_var = ctk.StringVar(value="customer")
        self.cust_btn = ctk.CTkButton(
            tab_frame, text="👤  Customer",
            font=("Segoe UI", 13, "bold"), height=36,
            fg_color=COLORS["accent"], text_color="#FFFFFF",
            corner_radius=6,
            command=lambda: self._switch_tab("customer")
        )
        self.cust_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))

        self.agent_btn = ctk.CTkButton(
            tab_frame, text="🏢  Agent",
            font=("Segoe UI", 13, "bold"), height=36,
            fg_color=COLORS["border"], text_color=COLORS["text_dark"],
            corner_radius=6,
            command=lambda: self._switch_tab("agent")
        )
        self.agent_btn.pack(side="left", fill="x", expand=True, padx=(2, 2))

        self.admin_btn = ctk.CTkButton(
            tab_frame, text="🛡️  Admin",
            font=("Segoe UI", 13, "bold"), height=36,
            fg_color=COLORS["border"], text_color=COLORS["text_dark"],
            corner_radius=6,
            command=lambda: self._switch_tab("admin")
        )
        self.admin_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))

        # Scrollable form area
        self.form_scroll = ctk.CTkScrollableFrame(
            card, fg_color="transparent"
        )
        self.form_scroll.pack(fill="both", expand=True, padx=30, pady=(8, 4))

        # Error label
        self.error_label = ctk.CTkLabel(
            card, text="", font=("Segoe UI", 12),
            text_color=COLORS["danger"]
        )
        self.error_label.pack(padx=30, anchor="w")

        # Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(4, 16))
        ctk.CTkButton(
            btn_frame, text="Register",
            font=("Segoe UI", 14, "bold"), height=40,
            fg_color=COLORS["accent"], hover_color="#2471A3",
            command=self._do_register
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(
            btn_frame, text="← Back to Login",
            font=("Segoe UI", 13), height=40,
            fg_color=COLORS["border"], text_color=COLORS["text_dark"],
            hover_color="#BFC9CA",
            command=self._go_back
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Build initial form
        self.entries = {}
        self._build_customer_form()

    def _switch_tab(self, tab: str):
        self.tab_var.set(tab)
        self.error_label.configure(text="")
        
        # Update tab button colors
        for t, btn in [("customer", self.cust_btn), ("agent", self.agent_btn), ("admin", self.admin_btn)]:
            if t == tab:
                btn.configure(fg_color=COLORS["accent"], text_color="#FFFFFF")
            else:
                btn.configure(fg_color=COLORS["border"], text_color=COLORS["text_dark"])

        if tab == "customer":
            self._build_customer_form()
        elif tab == "agent":
            self._build_agent_form()
        else:
            self._build_admin_form()

    def _clear_form(self):
        for child in self.form_scroll.winfo_children():
            child.destroy()
        self.entries.clear()

    def _add_field(self, label: str, key: str, placeholder: str = "",
                   show: str = None):
        ctk.CTkLabel(
            self.form_scroll, text=label,
            font=("Segoe UI", 13), text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(8, 2))
        entry = ctk.CTkEntry(
            self.form_scroll, placeholder_text=placeholder,
            font=("Segoe UI", 13), height=36,
            border_color=COLORS["border"],
            show=show if show else ""
        )
        entry.pack(fill="x", pady=(0, 4))
        self.entries[key] = entry

    def _build_customer_form(self):
        self._clear_form()
        self._add_field("Full Name", "full_name", "John Doe")
        self._add_field("Email", "email", "john@example.com")
        self._add_field("Phone (10 digits)", "phone", "9876543210")
        self._add_field("Date of Birth", "dob", "YYYY-MM-DD")
        self._add_field("Address", "address", "123 Main Street, City")
        self._add_field("Nominee Name", "nominee_name", "Jane Doe")
        self._add_field("Nominee Relation", "nominee_relation", "Spouse")
        self._add_field("Password", "password", "Min 6 characters", show="●")
        self._add_field("Confirm Password", "confirm_password", "Re-enter", show="●")

    def _build_agent_form(self):
        self._clear_form()
        self._add_field("Full Name", "full_name", "John Doe")
        self._add_field("Email", "email", "john@example.com")
        self._add_field("Phone (10 digits)", "phone", "9876543210")
        self._add_field("Region", "region", "North India")
        self._add_field("License Number", "license_no", "LIC-XXXX-XXXX")
        self._add_field("Agent Passkey", "agent_passkey", "Enter Passkey", show="*")
        self._add_field("Password", "password", "Min 6 characters", show="●")
        self._add_field("Confirm Password", "confirm_password", "Re-enter", show="●")

    def _build_admin_form(self):
        self._clear_form()
        self._add_field("Full Name", "full_name", "Admin User")
        self._add_field("Email", "email", "admin@example.com")
        self._add_field("Phone (10 digits)", "phone", "9876543210")
        self._add_field("Admin Passkey", "admin_passkey", "Enter Passkey", show="*")
        self._add_field("Password", "password", "Min 6 characters", show="●")
        self._add_field("Confirm Password", "confirm_password", "Re-enter", show="●")

    # ── Registration Logic ──────────────────────────────────────────
    def _do_register(self):
        vals = {k: e.get().strip() for k, e in self.entries.items()}
        role = self.tab_var.get()

        # Validate common fields
        for field, fn in [("full_name", validate_name),
                          ("email", validate_email),
                          ("phone", validate_phone),
                          ("password", validate_password)]:
            ok, msg = fn(vals.get(field, ""))
            if not ok:
                self.error_label.configure(text=msg)
                return

        if vals.get("password") != vals.get("confirm_password"):
            self.error_label.configure(text="Passwords do not match.")
            return

        # Role-specific validation
        if role == "customer":
            ok, msg = validate_dob(vals.get("dob", ""))
            if not ok:
                self.error_label.configure(text=msg)
                return
            ok, msg = validate_required(vals.get("address", ""), "Address")
            if not ok:
                self.error_label.configure(text=msg)
                return
        elif role == "agent":
            for f_key, f_lbl in [("region", "Region"), ("license_no", "License Number"), ("agent_passkey", "Agent Passkey")]:
                ok, msg = validate_required(vals.get(f_key, ""), f_lbl)
                if not ok:
                    self.error_label.configure(text=msg)
                    return
            if vals.get("agent_passkey") != AGENT_PASSKEY:
                self.error_label.configure(text="Invalid Agent Passkey.")
                return
        elif role == "admin":
            ok, msg = validate_required(vals.get("admin_passkey", ""), "Admin Passkey")
            if not ok:
                self.error_label.configure(text=msg)
                return
            if vals.get("admin_passkey") != ADMIN_PASSKEY:
                self.error_label.configure(text="Invalid Admin Passkey.")
                return

        # Check for duplicate email
        existing = execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            (vals["email"],), fetch=True
        )
        if existing:
            self.error_label.configure(text="Email already registered.")
            return

        # Hash password
        pw_hash = bcrypt.hashpw(
            vals["password"].encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        try:
            # Insert user. Customers are active by default. Agents and admins need approval.
            is_active = 1 if role == "customer" else 0
            
            user_id = execute_query(
                "INSERT INTO users (full_name, email, phone, password_hash, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (vals["full_name"], vals["email"], vals["phone"], pw_hash, role, is_active)
            )

            if role == "customer":
                execute_query(
                    "INSERT INTO customers (user_id, dob, address, "
                    "nominee_name, nominee_relation) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (user_id, vals["dob"], vals["address"],
                     vals.get("nominee_name", ""),
                     vals.get("nominee_relation", ""))
                )
            elif role == "agent":
                execute_query(
                    "INSERT INTO agents (user_id, license_no, region) "
                    "VALUES (%s, %s, %s)",
                    (user_id, vals["license_no"], vals["region"])
                )

            # Audit log
            execute_query(
                "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
                (user_id, f"Registered as {role}")
            )

            # Success → go back to login
            self.error_label.configure(
                text="", text_color=COLORS["danger"]
            )
            self._go_back_with_message()

        except Exception as e:
            self.error_label.configure(text=f"Registration failed: {e}")

    def _go_back_with_message(self):
        self.grab_release()
        self.destroy()
        self.login_window.show_again()
        # Show success inline on login
        self.login_window.error_label.configure(
            text="✅ Registered successfully! Please login.",
            text_color=COLORS["success"]
        )

    def _go_back(self):
        self.grab_release()
        self.destroy()
        self.login_window.show_again()

    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - REGISTER_WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - REGISTER_WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

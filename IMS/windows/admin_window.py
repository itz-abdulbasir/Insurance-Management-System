"""
IMS — Admin Dashboard Window
9-tab dashboard per SRS §7.4 (FR-AD1 to FR-AD9).
"""
import customtkinter as ctk
import os
from config import COLORS, APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from db.connection import execute_query
from components.sidebar import Sidebar
from components.table_view import TableView
from components.cards import StatCard, InfoCard
from utils.helpers import format_currency, format_date
from utils.pdf_export import generate_table_report, generate_detailed_report
from modules.agent_requests import get_all_pending_requests, resolve_request
from modules import plans, policies
from modules.premium import get_policy_premiums
from windows.base_window import BaseWindow

class AdminWindow(BaseWindow):
    def __init__(self, app_root, user: dict, login_window):
        super().__init__(app_root, user, login_window, f"{APP_NAME} — Admin Dashboard")

        
        self._build_layout()

    def _build_layout(self):
        nav = [
            {"label": "Dashboard",         "icon": "📊", "command": self._show_dashboard},
            {"label": "Pending Approvals", "icon": "✅", "command": self._show_pending_approvals},
            {"label": "User Management",   "icon": "👥", "command": self._show_users},
            {"label": "Customer Mgmt",     "icon": "🤝", "command": self._show_customers},
            {"label": "Agent Management",  "icon": "🏢", "command": self._show_agents},
            {"label": "Plan Management",   "icon": "📋", "command": self._show_plans},
            {"label": "Customer Plans",    "icon": "📄", "command": self._show_policies},
            {"label": "Audit Log",         "icon": "📜", "command": self._show_audit},
            {"label": "PDF Reports",       "icon": "📥", "command": self._show_reports},
        ]
        self.sidebar = Sidebar(self, nav, self.user["full_name"], "Admin", self._logout)
        self.sidebar.pack(side="left", fill="y")
        
        # Top bar
        top = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], height=50, corner_radius=0, border_width=1, border_color=COLORS["border"])
        top.pack(side="top", fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text=f"👤 Welcome, {self.user['full_name']}", font=("Segoe UI", 15, "bold"), text_color=COLORS["primary"]).pack(side="left", padx=20)
        
        # Content area
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_light"])
        self.content.pack(side="right", fill="both", expand=True)
        self._show_dashboard()
        self.after(500, self._check_notifications)



    # ── Tab: Dashboard ──────────────────────────────────────────
    def _show_dashboard(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "System Overview")
        
        # Stats query
        users = execute_query("SELECT COUNT(*) as c FROM users", fetch=True)[0]['c']
        policies = execute_query("SELECT COUNT(*) as c FROM policies", fetch=True)[0]['c']
        claims = execute_query("SELECT COUNT(*) as c FROM claims WHERE status='pending'", fetch=True)[0]['c']
        income_row = execute_query("SELECT SUM(amount) as s FROM premiums WHERE status='paid'", fetch=True)[0]['s']
        income = format_currency(income_row) if income_row else "₹0.00"

        cards_frame = ctk.CTkFrame(f, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)
        
        StatCard(cards_frame, "Total Users", "👥", str(users)).pack(side="left", fill="x", expand=True, padx=8)
        StatCard(cards_frame, "Total Policies", "📄", str(policies)).pack(side="left", fill="x", expand=True, padx=8)
        StatCard(cards_frame, "Pending Claims", "📝", str(claims)).pack(side="left", fill="x", expand=True, padx=8)
        StatCard(cards_frame, "Total Revenue", "💰", income).pack(side="left", fill="x", expand=True, padx=8)

    # ── Tab: User Management ────────────────────────────────────
    def _show_users(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "User Management")
        
        data = execute_query("SELECT user_id, full_name, email, role, is_active FROM users ORDER BY user_id DESC", fetch=True)
        for r in data:
            r['status'] = 'active' if r['is_active'] else 'inactive'
            
        cols = [{"key": "user_id", "label": "ID", "width": 50},
                {"key": "full_name", "label": "Name", "width": 180},
                {"key": "email", "label": "Email", "width": 200},
                {"key": "role", "label": "Role", "width": 100},
                {"key": "status", "label": "Status", "width": 80}]
        
        action_cfg = {
            "header": "Action",
            "text": "Toggle",
            "fg_color": COLORS["warning"],
            "command": self._toggle_user_status
        }
        TableView(f, cols, data, badge_col="status", action_config=action_cfg).pack(fill="both", expand=True)

    def _toggle_user_status(self, row):
        new_status = 0 if row['status'] == 'active' else 1
        execute_query("UPDATE users SET is_active=%s WHERE user_id=%s", (new_status, row['user_id']))
        execute_query("INSERT INTO audit_log (user_id, action) VALUES (%s,%s)",
                      (self.user["user_id"], f"Toggled user #{row['user_id']} active={new_status}"))
        self._show_users()

    # ── Tab: Pending Approvals (Unified) ────────────────────────
    def _show_pending_approvals(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Pending Approvals")
        
        tabview = ctk.CTkTabview(f, height=600)
        tabview.pack(fill="both", expand=True)
        
        tabview.add("New Agent Requests")
        tabview.add("New Admin Requests")
        tabview.add("Claim Requests")
        tabview.add("Agent's Request for Customer")
        
        self._build_pending_users(tabview.tab("New Agent Requests"), "agent")
        self._build_pending_users(tabview.tab("New Admin Requests"), "admin")
        self._build_pending_claims(tabview.tab("Claim Requests"))
        self._build_pending_agent_requests(tabview.tab("Agent's Request for Customer"))

    def _build_pending_users(self, parent, role):
        data = execute_query(f"SELECT user_id, full_name, email, role, is_active FROM users WHERE is_active=0 AND role='{role}' ORDER BY user_id DESC", fetch=True)
        for r in data: r['status'] = 'pending'
        cols = [{"key": "user_id", "label": "ID", "width": 50},
                {"key": "full_name", "label": "Name", "width": 180},
                {"key": "email", "label": "Email", "width": 200},
                {"key": "status", "label": "Status", "width": 80}]
        action = {"header": "Action", "text": "Approve", "fg_color": COLORS["success"], "command": self._approve_user}
        TableView(parent, cols, data, badge_col="status", action_config=action).pack(fill="both", expand=True)

    def _approve_user(self, row):
        execute_query("UPDATE users SET is_active=1 WHERE user_id=%s", (row['user_id'],))
        execute_query("INSERT INTO audit_log (user_id, action) VALUES (%s,%s)", (self.user["user_id"], f"Approved user #{row['user_id']}"))
        self._show_pending_approvals()

    def _build_pending_claims(self, parent):
        data = execute_query(
            "SELECT c.claim_id, p.policy_id, c.amount_requested, c.status, c.filed_at "
            "FROM claims c JOIN policies p ON c.policy_id = p.policy_id "
            "WHERE c.status='pending' ORDER BY c.filed_at DESC", fetch=True)
        for r in data:
            r['amount_requested'] = format_currency(r['amount_requested'])
            r['filed_at'] = format_date(r['filed_at'])
        cols = [{"key": "claim_id", "label": "Claim ID", "width": 70},
                {"key": "policy_id", "label": "Policy ID", "width": 70},
                {"key": "amount_requested", "label": "Amount", "width": 120},
                {"key": "status", "label": "Status", "width": 100}]
        action = {"header": "Action", "text": "Resolve", "fg_color": COLORS["accent"], "command": self._resolve_claim_popup}
        TableView(parent, cols, data, badge_col="status", action_config=action).pack(fill="both", expand=True)

    def _resolve_claim_popup(self, row):
        popup = ctk.CTkToplevel(self)
        popup.title("Resolve Claim")
        popup.geometry("350x150")
        popup.grab_set()
        ctk.CTkLabel(popup, text=f"Resolve claim #{row['claim_id']}?", font=("Segoe UI", 14, "bold")).pack(pady=20)
        btn_f = ctk.CTkFrame(popup, fg_color="transparent")
        btn_f.pack()
        def resolve(s):
            from modules.claims import resolve_claim
            try:
                resolve_claim(row["claim_id"], s, self.user["user_id"])
                popup.destroy()
                self._show_msg(f"Claim {s} successfully!")
                self._show_pending_approvals()
            except ValueError as e: self._show_msg(str(e), err=True)
        ctk.CTkButton(btn_f, text="Approve", fg_color=COLORS["success"], command=lambda: resolve("approved")).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="Reject", fg_color=COLORS["danger"], command=lambda: resolve("rejected")).pack(side="left", padx=10)



    def _build_pending_agent_requests(self, parent):
        data = get_all_pending_requests()
        for r in data: r["requested_at"] = format_date(r.get("requested_at"))
        cols = [{"key": "request_id", "label": "Req ID", "width": 60},
                {"key": "agent_name", "label": "Agent", "width": 180},
                {"key": "customer_name", "label": "Customer", "width": 180}]
        action = {"header": "Action", "text": "Resolve", "fg_color": COLORS["accent"], "command": self._resolve_agent_request_popup}
        TableView(parent, cols, data, action_config=action).pack(fill="both", expand=True)

    def _resolve_agent_request_popup(self, row):
        popup = ctk.CTkToplevel(self)
        popup.title("Resolve Request")
        popup.geometry("350x150")
        popup.grab_set()
        ctk.CTkLabel(popup, text=f"Resolve request #{row['request_id']}?", font=("Segoe UI", 14, "bold")).pack(pady=20)
        btn_f = ctk.CTkFrame(popup, fg_color="transparent")
        btn_f.pack()
        def resolve(s):
            try:
                resolve_request(row["request_id"], s, self.user["user_id"])
                popup.destroy()
                self._show_msg(f"Request {s} successfully!")
                self._show_pending_approvals()
            except ValueError as e: self._show_msg(str(e), err=True)
        ctk.CTkButton(btn_f, text="Approve", fg_color=COLORS["success"], command=lambda: resolve("approved")).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="Reject", fg_color=COLORS["danger"], command=lambda: resolve("rejected")).pack(side="left", padx=10)

    # ── Tab: Agent Management ───────────────────────────────────
    def _show_agents(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Agent Management")
        
        data = execute_query(
            "SELECT a.agent_id, u.full_name, a.license_no, a.region, "
            "(SELECT COUNT(*) FROM customers WHERE assigned_agent_id = a.agent_id) as cust_count "
            "FROM agents a JOIN users u ON a.user_id = u.user_id", fetch=True)
            
        cols = [{"key": "agent_id", "label": "ID", "width": 50},
                {"key": "full_name", "label": "Name", "width": 180},
                {"key": "license_no", "label": "License", "width": 120},
                {"key": "region", "label": "Region", "width": 120},
                {"key": "cust_count", "label": "Customers", "width": 80}]
                
        TableView(f, cols, data).pack(fill="both", expand=True)

    # ── Tab: Customer Management ────────────────────────────────
    def _show_customers(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Customer Management")
        
        data = execute_query(
            "SELECT c.customer_id, u.full_name, u.email, "
            "IFNULL(a.full_name, 'None') as agent_name "
            "FROM customers c "
            "JOIN users u ON c.user_id = u.user_id "
            "LEFT JOIN agents ag ON c.assigned_agent_id = ag.agent_id "
            "LEFT JOIN users a ON ag.user_id = a.user_id", fetch=True)
            
        cols = [{"key": "customer_id", "label": "ID", "width": 50},
                {"key": "full_name", "label": "Name", "width": 180},
                {"key": "email", "label": "Email", "width": 200},
                {"key": "agent_name", "label": "Assigned Agent", "width": 180}]
                
        action_cfg = {
            "header": "Action",
            "text": "Assign Agent",
            "fg_color": COLORS["accent"],
            "command": self._assign_agent_popup
        }
        TableView(f, cols, data, action_config=action_cfg).pack(fill="both", expand=True)

    def _assign_agent_popup(self, row):
        agents = execute_query(
            "SELECT a.agent_id, u.full_name FROM agents a "
            "JOIN users u ON a.user_id = u.user_id WHERE u.is_active = 1", fetch=True)
        
        if not agents:
            self._show_msg("No active agents found.", err=True)
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Assign Agent")
        popup.geometry("400x200")
        popup.resizable(False, False)
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Assign agent for {row['full_name']}:", font=("Segoe UI", 14, "bold")).pack(pady=(20, 10))
        
        agent_opts = [f"{ag['agent_id']} — {ag['full_name']}" for ag in agents]
        agent_opts.insert(0, "None")
        
        agent_var = ctk.StringVar(value="None")
        ctk.CTkComboBox(popup, values=agent_opts, variable=agent_var, width=250).pack(pady=10)

        def save():
            val = agent_var.get()
            agent_id = None if val == "None" else int(val.split(" — ")[0])
            execute_query("UPDATE customers SET assigned_agent_id = %s WHERE customer_id = %s", (agent_id, row['customer_id']))
            execute_query("INSERT INTO audit_log (user_id, action) VALUES (%s,%s)", 
                          (self.user["user_id"], f"Assigned agent {agent_id} to customer #{row['customer_id']}"))
            popup.destroy()
            self._show_msg("Agent assigned successfully!")
            self._show_customers()

        ctk.CTkButton(popup, text="Save", command=save, fg_color=COLORS["success"], width=100).pack(pady=(10, 0))

    # ── Tab: Plan Management ────────────────────────────────────
    def _show_plans(self):
        self._clear()
        f = self.content # Use the main container directly for tables
        
        # Header with Add button
        header_f = ctk.CTkFrame(f, fg_color="transparent")
        header_f.pack(fill="x", pady=20, padx=24)
        ctk.CTkLabel(header_f, text="Plan Management", font=("Segoe UI", 24, "bold"), text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkButton(header_f, text="+ Add New Plan", font=("Segoe UI", 13, "bold"), fg_color=COLORS["success"], 
                      command=self._add_plan_popup, width=140).pack(side="right")
        
        
        # Show all plans for Admin management
        try:
            data = plans.get_all_plans()
            print(f"[IMS] Loaded {len(data)} plans for management.")
        except Exception as e:
            print(f"[IMS] Error loading plans: {e}")
            # Fallback to direct query if module fails
            data = execute_query("SELECT * FROM plans WHERE is_deleted = 0 ORDER BY plan_id DESC", fetch=True)
        
        for r in data:
            r['status'] = 'active' if r['is_active'] else 'inactive'
            r['display_premium'] = f"{format_currency(r.get('base_premium', 0))} / {r.get('premium_frequency', 'N/A')}"
            r['display_coverage'] = format_currency(r.get('coverage_amount', 0))
            r['display_term'] = f"{r.get('policy_term_years', 0)} yrs"
            
        cols = [{"key": "plan_id", "label": "ID", "width": 50},
                {"key": "plan_name", "label": "Name", "width": 180},
                {"key": "plan_type", "label": "Type", "width": 80},
                {"key": "display_premium", "label": "Premium", "width": 130},
                {"key": "display_coverage", "label": "Coverage", "width": 120},
                {"key": "display_term", "label": "Term", "width": 80},
                {"key": "status", "label": "Status", "width": 80}]
        
        actions = [
            {
                "text": "Toggle Status", 
                "fg_color": COLORS["warning"], 
                "width": 100,
                "command": self._toggle_plan_status
            },
            {
                "text": "Remove", 
                "fg_color": COLORS["danger"], 
                "width": 80,
                "command": self._delete_plan
            }
        ]
        
        # Ensure the table expands to show all rows
        tv = TableView(f, cols, data, badge_col="status", action_config=actions)
        tv.pack(fill="both", expand=True, pady=(0, 20), padx=24)

    def _toggle_plan_status(self, row):
        plans.toggle_plan_status(row['plan_id'], row['is_active'], self.user["user_id"])
        execute_query("INSERT INTO audit_log (user_id, action) VALUES (%s,%s)", 
                      (self.user["user_id"], f"Toggled plan '{row['plan_name']}' status"))
        self._show_plans()

    def _delete_plan(self, row):
        popup = ctk.CTkToplevel(self)
        popup.title("Confirm Delete")
        popup.geometry("350x150")
        popup.grab_set()
        ctk.CTkLabel(popup, text=f"Delete plan '{row['plan_name']}'?\nThis cannot be undone.", 
                     font=("Segoe UI", 13), wraplength=300).pack(pady=20)
        btn_f = ctk.CTkFrame(popup, fg_color="transparent")
        btn_f.pack()
        def do_del():
            try:
                plans.delete_plan(row['plan_id'], self.user["user_id"])
                execute_query("INSERT INTO audit_log (user_id, action) VALUES (%s,%s)", 
                              (self.user["user_id"], f"Deleted plan '{row['plan_name']}'"))
                popup.destroy()
                self._show_msg("Plan removed successfully!")
                self._show_plans()
            except ValueError as e:
                popup.destroy()
                self._show_msg(str(e), err=True)
        ctk.CTkButton(btn_f, text="Delete", fg_color=COLORS["danger"], command=do_del).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="Cancel", fg_color=COLORS["border"], text_color=COLORS["text_dark"], command=popup.destroy).pack(side="left", padx=10)

    def _add_plan_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add New Insurance Plan")
        popup.geometry("500x650")
        popup.resizable(False, False)
        popup.grab_set()

        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Enter Plan Details", font=("Segoe UI", 16, "bold"), text_color=COLORS["primary"]).pack(pady=(0, 20))

        entries = {}
        fields = [
            ("Plan Name", "name", "Suraksha Plus"),
            ("Description", "desc", "Comprehensive coverage for..."),
            ("Min Age", "min_age", "18"),
            ("Max Age", "max_age", "65"),
            ("Base Premium", "premium", "1000.00"),
            ("Coverage Amount", "coverage", "500000.00"),
            ("Term (Years)", "term", "5")
        ]

        for lbl, key, placeholder in fields:
            ctk.CTkLabel(scroll, text=lbl, font=("Segoe UI", 13)).pack(anchor="w", pady=(10, 0))
            e = ctk.CTkEntry(scroll, placeholder_text=placeholder, height=36)
            e.pack(fill="x", pady=(2, 0))
            entries[key] = e

        ctk.CTkLabel(scroll, text="Plan Type", font=("Segoe UI", 13)).pack(anchor="w", pady=(10, 0))
        type_var = ctk.StringVar(value="term")
        ctk.CTkComboBox(scroll, values=["term", "endowment", "whole_life", "pension", "micro", "ulip"], 
                         variable=type_var, height=36).pack(fill="x", pady=(2, 0))

        ctk.CTkLabel(scroll, text="Premium Frequency", font=("Segoe UI", 13)).pack(anchor="w", pady=(10, 0))
        freq_var = ctk.StringVar(value="monthly")
        ctk.CTkComboBox(scroll, values=["weekly", "monthly", "quarterly", "half-yearly", "yearly"], 
                         variable=freq_var, height=36).pack(fill="x", pady=(2, 0))

        error_lbl = ctk.CTkLabel(scroll, text="", text_color=COLORS["danger"], font=("Segoe UI", 12))
        error_lbl.pack(pady=10)

        def save():
            try:
                plans.add_plan(
                    entries["name"].get().strip(),
                    type_var.get(),
                    entries["desc"].get().strip(),
                    entries["min_age"].get(),
                    entries["max_age"].get(),
                    freq_var.get(),
                    entries["premium"].get(),
                    entries["coverage"].get(),
                    entries["term"].get()
                )
                execute_query("INSERT INTO audit_log (user_id, action) VALUES (%s,%s)", 
                              (self.user["user_id"], f"Added new plan '{entries['name'].get()}'"))
                popup.destroy()
                self._show_msg("New plan added successfully!")
                self._show_plans()
            except Exception as e:
                error_lbl.configure(text=f"Error: {str(e)}")

        ctk.CTkButton(scroll, text="Save Plan", font=("Segoe UI", 14, "bold"), height=40,
                      fg_color=COLORS["success"], command=save).pack(fill="x", pady=20)

    # ── Tab: Customer Plans ───────────────────────────────────────
    def _show_policies(self):
        self._clear()
        f = self.content
        
        header_f = ctk.CTkFrame(f, fg_color="transparent")
        header_f.pack(fill="x", pady=(20, 0), padx=24)
        self._heading(header_f, "Customer Plans")
        
        # Filter bar
        fbar = ctk.CTkFrame(f, fg_color="transparent")
        fbar.pack(fill="x", pady=(0, 12), padx=24)
        ctk.CTkLabel(fbar, text="Filter by status:", font=("Segoe UI", 13),
                     text_color=COLORS["text_muted"]).pack(side="left")
        
        for val in ["all", "active", "terminated", "claimed", "surrendered", "expired"]:
            ctk.CTkButton(fbar, text=val.capitalize(), width=80, height=28,
                          fg_color=COLORS["accent"] if val == "all" else COLORS["border"],
                          text_color="#FFF" if val == "all" else COLORS["text_dark"],
                          font=("Segoe UI", 11), corner_radius=14,
                          command=lambda v=val: self._load_policies(v, f)
                          ).pack(side="left", padx=4)

        self._pol_container = ctk.CTkFrame(f, fg_color="transparent")
        self._pol_container.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        self._load_policies("all", f)

    def _load_policies(self, status, parent):
        for w in self._pol_container.winfo_children(): w.destroy()
        
        filt = None if status == "all" else status
        data = policies.get_all_policies(filt)
            
        cols = [{"key": "policy_id", "label": "ID", "width": 50},
                {"key": "customer_name", "label": "Customer", "width": 180},
                {"key": "plan_name", "label": "Plan", "width": 200},
                {"key": "installments", "label": "Installments", "width": 120},
                {"key": "status", "label": "Status", "width": 100}]
        for r in data:
            r["installments"] = f"{r.get('paid_installments', 0)} / {r.get('total_installments', 0)}"
                
        TableView(self._pol_container, cols, data, badge_col="status", on_row_click=self._policy_detail).pack(fill="both", expand=True)

    def _policy_detail(self, row):
        det = policies.get_policy_detail(row["policy_id"])
        if not det:
            return
        self._clear()
        f = self._make_scroll()
        
        header_f = ctk.CTkFrame(f, fg_color="transparent")
        header_f.pack(fill="x", pady=(0, 20))
        
        ctk.CTkButton(header_f, text="← Back to Plans", font=("Segoe UI", 12),
                      fg_color=COLORS["border"], text_color=COLORS["text_dark"], 
                      hover_color="#BFC9CA", width=120, height=30,
                      command=self._show_policies).pack(side="left")
                      
        ctk.CTkLabel(header_f, text=f"Policy #{det['policy_id']} — {det['plan_name']} (Customer: {det.get('customer_name', 'N/A')})", 
                     font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"]
                     ).pack(side="left", padx=20)
                     
        info = {
            "Plan Type": det.get("plan_type", "").upper(),
            "Status": det.get("status", "").capitalize(),
            "Start Date": format_date(det.get("start_date")),
            "End Date": format_date(det.get("end_date")),
            "Premium": f"{format_currency(det.get('base_premium'))} / {det.get('premium_frequency','')}",
            "Paid Installments": f"{det.get('paid_installments', 0)} of {det.get('total_installments', 0)}",
            "Remaining": det.get("total_installments", 0) - det.get("paid_installments", 0),
            "Coverage": format_currency(det.get("coverage_amount")),
            "Agent": det.get("agent_name", "Not assigned"),
        }
        InfoCard(f, "Policy Details", info).pack(fill="x", pady=8)
        
        # Payment History Table
        ctk.CTkLabel(f, text="Payment History", font=("Segoe UI", 18, "bold"), 
                     text_color=COLORS["primary"]).pack(anchor="w", pady=(20, 10))
                     
        payments = get_policy_premiums(det["policy_id"])
        if payments:
            for p in payments:
                p["display_amount"] = format_currency(p["amount"])
                p["display_paid"] = format_date(p.get("paid_date")) if p.get("paid_date") else "—"
                p["display_due"] = format_date(p["due_date"])
                
            p_cols = [{"key": "premium_id", "label": "ID", "width": 60},
                      {"key": "display_amount", "label": "Amount", "width": 120},
                      {"key": "display_due", "label": "Due Date", "width": 120},
                      {"key": "display_paid", "label": "Paid On", "width": 120},
                      {"key": "status", "label": "Status", "width": 100}]
                      
            TableView(f, p_cols, payments, badge_col="status").pack(fill="x", pady=10)
        else:
            ctk.CTkLabel(f, text="No payment history found.", text_color=COLORS["text_muted"]).pack(anchor="w", pady=10)
            
        def _export_receipt():
            try:
                paid_payments = [p for p in payments if p["status"] == "paid"]
                request_info = {
                    "type": "Policy Detail",
                    "id": det["policy_id"],
                    "status": det["status"]
                }
                generate_detailed_report(f"Policy Receipt - {det['plan_name']}", det, paid_payments, request_info, f"receipt_{det['policy_id']}")
                self._show_msg("✅ Exported to Downloads/IMS_Reports!\nOpening file...")
            except Exception as e:
                self._show_msg(f"Export Error: {e}", err=True)
                
        ctk.CTkButton(f, text="📥 Download PDF Receipt", font=("Segoe UI", 14, "bold"),
                      fg_color=COLORS["success"], hover_color="#196F3D", height=40,
                      command=_export_receipt).pack(pady=20)




    # ── Tab: Audit Log ──────────────────────────────────────────
    def _show_audit(self):
        self._clear()
        # self._make_scroll() removed to allow TableView to expand to full screen
        self._heading(self.content, "Audit Log")
        
        data = execute_query(
            "SELECT a.log_id, COALESCE(u.email, 'Anonymous') as email, a.action, a.timestamp "
            "FROM audit_log a LEFT JOIN users u ON a.user_id = u.user_id "
            "ORDER BY a.timestamp DESC LIMIT 1000", fetch=True)
            
        for r in data:
            ts = r.get('timestamp', '')
            r['timestamp'] = str(ts) if ts else '—'
            
            # Color logic: Red for failures, Green for others
            action = str(r.get("action", "")).lower()
            if "failed" in action:
                r["row_text_color"] = COLORS["danger"]
            else:
                r["row_text_color"] = COLORS["success"]
            
        cols = [{"key": "log_id", "label": "ID", "width": 60},
                {"key": "email", "label": "User", "width": 200},
                {"key": "action", "label": "Action", "width": 350},
                {"key": "timestamp", "label": "Time", "width": 160}]
                
        TableView(self.content, cols, data).pack(fill="both", expand=True, padx=24, pady=(0, 16))

    # ── Tab: PDF Reports ────────────────────────────────────────
    def _show_reports(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Generate PDF Reports")
        
        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        lbl = ctk.CTkLabel(btn_frame, text="", text_color=COLORS["success"], font=("Segoe UI", 12))
        
        def _gen_policy_report():
            data = execute_query(
                "SELECT p.policy_id, u.full_name, pl.plan_name, p.status "
                "FROM policies p "
                "JOIN customers c ON p.customer_id = c.customer_id "
                "JOIN users u ON c.user_id = u.user_id "
                "JOIN plans pl ON p.plan_id = pl.plan_id", fetch=True)
            headers = ["Policy ID", "Customer Name", "Plan Name", "Status"]
            table_data = [[r['policy_id'], r['full_name'], r['plan_name'], r['status']] for r in data]
            path = generate_table_report("All Policies Report", headers, table_data, "policies")
            lbl.configure(text=f"✅ Exported to Downloads/IMS_Reports!\nOpening file...")
            
        def _gen_claims_report():
            data = execute_query(
                "SELECT c.claim_id, p.policy_id, c.amount_requested, c.status "
                "FROM claims c JOIN policies p ON c.policy_id = p.policy_id", fetch=True)
            headers = ["Claim ID", "Policy ID", "Amount Requested", "Status"]
            table_data = [[r['claim_id'], r['policy_id'], format_currency(r['amount_requested']), r['status']] for r in data]
            path = generate_table_report("All Claims Report", headers, table_data, "claims")
            lbl.configure(text=f"✅ Exported to Downloads/IMS_Reports!\nOpening file...")

        ctk.CTkButton(btn_frame, text="📄 Generate Policies Report", font=("Segoe UI", 14), 
                      command=_gen_policy_report).pack(pady=10, anchor="w")
        ctk.CTkButton(btn_frame, text="📝 Generate Claims Report", font=("Segoe UI", 14),
                      command=_gen_claims_report).pack(pady=10, anchor="w")
        lbl.pack(pady=10, anchor="w")



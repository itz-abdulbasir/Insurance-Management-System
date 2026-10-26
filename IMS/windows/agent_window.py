"""
IMS — Agent Dashboard Window
6-tab dashboard per SRS §7.3 (FR-AG1 to FR-AG7).
"""
import customtkinter as ctk
from config import COLORS, APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from db.connection import execute_query
from components.sidebar import Sidebar
from components.table_view import TableView
from components.cards import StatCard, InfoCard
from modules.policies import get_agent_policies
from modules.claims import get_agent_pending_claims, resolve_claim
from modules.surrender import get_agent_pending_surrenders, resolve_surrender
from modules.premium import get_agent_overdue_premiums, mark_premium_paid
from modules.agent_requests import get_available_customers, create_request
from utils.helpers import format_currency, format_date
from utils.pdf_export import generate_table_report
from windows.base_window import BaseWindow

class AgentWindow(BaseWindow):
    def __init__(self, app_root, user: dict, login_window):
        super().__init__(app_root, user, login_window, f"{APP_NAME} — Agent Dashboard")
        rows = execute_query("SELECT * FROM agents WHERE user_id=%s",
                             (user["user_id"],), fetch=True)
        self.agent = rows[0] if rows else {}
        self.agent_id = self.agent.get("agent_id", 0)
        self._build_layout()

    def _build_layout(self):
        nav = [
            {"label": "Dashboard",          "icon": "📊", "command": self._show_dashboard},
            {"label": "My Customers",       "icon": "👥", "command": self._show_customers},
            {"label": "Claims Mgmt",        "icon": "📝", "command": self._show_claims},
            {"label": "Premium Tracker",    "icon": "💰", "command": self._show_premiums},
            {"label": "Customer Plans",    "icon": "📄", "command": self._show_policies},
            {"label": "Find Customers",     "icon": "🔍", "command": self._show_available_customers},
        ]
        Sidebar(self, nav, self.user["full_name"], "Agent", self._logout).pack(side="left", fill="y")
        top = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], height=50, corner_radius=0,
                           border_width=1, border_color=COLORS["border"])
        top.pack(side="top", fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text=f"🏢 Agent: {self.user['full_name']}  •  Region: {self.agent.get('region','')}",
                     font=("Segoe UI", 15, "bold"), text_color=COLORS["primary"]).pack(side="left", padx=20)
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_light"])
        self.content.pack(side="right", fill="both", expand=True)
        self._show_dashboard()
        self.after(500, self._check_notifications)



    # ── Tab: Dashboard ──────────────────────────────────────────
    def _show_dashboard(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Agent Dashboard")
        custs = execute_query(
            "SELECT COUNT(*) AS c FROM customers WHERE assigned_agent_id=%s",
            (self.agent_id,), fetch=True)
        pols = execute_query(
            "SELECT COUNT(*) AS c FROM policies WHERE agent_id=%s AND status='active'",
            (self.agent_id,), fetch=True)
        claims = execute_query(
            "SELECT COUNT(*) AS c FROM claims c JOIN policies p ON c.policy_id=p.policy_id "
            "JOIN customers cu ON p.customer_id=cu.customer_id "
            "WHERE cu.assigned_agent_id=%s AND c.status='pending'",
            (self.agent_id,), fetch=True)
        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure((0, 1, 2), weight=1)
        StatCard(grid, "👥", custs[0]["c"] if custs else 0, "Assigned Customers",
                 accent=COLORS["accent"]).grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        StatCard(grid, "📄", pols[0]["c"] if pols else 0, "Active Policies",
                 accent=COLORS["success"]).grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        StatCard(grid, "📝", claims[0]["c"] if claims else 0, "Pending Claims",
                 accent=COLORS["warning"]).grid(row=0, column=2, padx=8, pady=8, sticky="nsew")

    # ── Tab: My Customers ───────────────────────────────────────
    def _show_customers(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "My Customers")
        
        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(btn_frame, text="📥 Download Comprehensive Report", 
                      command=self._export_report).pack(side="left")
                      
        data = execute_query(
            "SELECT cu.customer_id, u.full_name, u.phone, u.email, "
            "(SELECT COUNT(*) FROM policies WHERE customer_id=cu.customer_id AND status='active') AS active_policies "
            "FROM customers cu JOIN users u ON cu.user_id=u.user_id "
            "WHERE cu.assigned_agent_id=%s ORDER BY u.full_name",
            (self.agent_id,), fetch=True)
        cols = [{"key": "customer_id", "label": "ID", "width": 50},
                {"key": "full_name", "label": "Name", "width": 180},
                {"key": "phone", "label": "Phone", "width": 120},
                {"key": "email", "label": "Email", "width": 200},
                {"key": "active_policies", "label": "Active Policies", "width": 120}]
        TableView(f, cols, data).pack(fill="both", expand=True)

    def _export_report(self):
        data = execute_query(
            "SELECT u.full_name as Customer, u.phone, pl.plan_name as Plan, p.status as PolicyStatus, p.start_date, p.end_date "
            "FROM customers cu "
            "JOIN users u ON cu.user_id=u.user_id "
            "LEFT JOIN policies p ON p.customer_id=cu.customer_id "
            "LEFT JOIN plans pl ON p.plan_id=pl.plan_id "
            "WHERE cu.assigned_agent_id=%s ORDER BY u.full_name",
            (self.agent_id,), fetch=True)
        if not data:
            self._show_msg("No data to export.", err=True)
            return
        headers = ["Customer", "Phone", "Plan", "Status", "Start", "End"]
        table_data = [[
            r.get("Customer", ""), 
            r.get("phone", ""), 
            r.get("Plan") or "No Policy", 
            r.get("PolicyStatus") or "-", 
            format_date(r.get("start_date")) if r.get("start_date") else "-", 
            format_date(r.get("end_date")) if r.get("end_date") else "-"
        ] for r in data]
        path = generate_table_report("Comprehensive Agent Report", headers, table_data, "agent_report")
        self._show_msg(f"✅ Exported to Downloads/IMS_Reports!\nOpening file...")

    # ── Tab: Claims Management ──────────────────────────────────
    def _show_claims(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Claims Management — Pending")
        data = get_agent_pending_claims(self.agent_id)
        if not data:
            ctk.CTkLabel(f, text="No pending claims.", font=("Segoe UI", 14),
                         text_color=COLORS["text_muted"]).pack(pady=40)
            return
        for cl in data:
            card = ctk.CTkFrame(f, fg_color=COLORS["card_bg"], corner_radius=8,
                                border_width=1, border_color=COLORS["border"])
            card.pack(fill="x", pady=6)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=12)
            ctk.CTkLabel(inner, text=f"Claim #{cl['claim_id']}  •  {cl['customer_name']}  •  Policy #{cl['policy_id']}",
                         font=("Segoe UI", 14, "bold"), text_color=COLORS["primary"]).pack(anchor="w")
            ctk.CTkLabel(inner, text=f"Amount: {format_currency(cl['amount_requested'])}  •  Filed: {format_date(cl.get('filed_at'))}",
                         font=("Segoe UI", 12), text_color=COLORS["text_dark"]).pack(anchor="w", pady=2)
            ctk.CTkLabel(inner, text=f"Reason: {cl.get('reason','')}",
                         font=("Segoe UI", 12), text_color=COLORS["text_muted"], wraplength=600).pack(anchor="w", pady=2)
            btns = ctk.CTkFrame(inner, fg_color="transparent")
            btns.pack(anchor="e", pady=(4, 0))
            ctk.CTkButton(btns, text="✅ Approve", width=100, height=32,
                          fg_color=COLORS["success"], hover_color="#196F3D",
                          command=lambda c=cl: self._resolve_claim(c["claim_id"], "approved")).pack(side="left", padx=4)
            ctk.CTkButton(btns, text="❌ Reject", width=100, height=32,
                          fg_color=COLORS["danger"], hover_color="#A93226",
                          command=lambda c=cl: self._resolve_claim(c["claim_id"], "rejected")).pack(side="left", padx=4)

    def _resolve_claim(self, claim_id, status):
        try:
            resolve_claim(claim_id, status, self.user["user_id"])
        except ValueError as e:
            self._show_msg(str(e), err=True)
        self._show_claims()



    # ── Tab: Premium Tracker ────────────────────────────────────
    def _show_premiums(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Overdue Premiums — Assigned Customers")
        data = get_agent_overdue_premiums(self.agent_id)
        if not data:
            ctk.CTkLabel(f, text="No overdue premiums. 🎉", font=("Segoe UI", 14),
                         text_color=COLORS["success"]).pack(pady=40)
            return
        for pr in data:
            row = ctk.CTkFrame(f, fg_color=COLORS["card_bg"], corner_radius=8,
                               border_width=1, border_color=COLORS["border"])
            row.pack(fill="x", pady=4)
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=10)
            ctk.CTkLabel(inner, text=f"{pr['customer_name']}  •  Policy #{pr['policy_id']}  •  {pr['plan_name']}",
                         font=("Segoe UI", 13, "bold"), text_color=COLORS["primary"]).pack(side="left")
            ctk.CTkLabel(inner, text=f"Due: {format_date(pr['due_date'])} • {format_currency(pr['amount'])}",
                         font=("Segoe UI", 12), text_color=COLORS["text_dark"]).pack(side="left", padx=16)
            ctk.CTkButton(inner, text="Mark Paid", width=90, height=28,
                          fg_color=COLORS["success"], hover_color="#196F3D",
                          font=("Segoe UI", 11, "bold"),
                          command=lambda p=pr: self._mark_paid(p)).pack(side="right")

    def _mark_paid(self, pr):
        mark_premium_paid(pr["premium_id"], self.user["user_id"])
        self._show_premiums()

    # ── Tab: Customer Plans ────────────────────────────────────
    def _show_policies(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Customer Plans")
        # Filter bar
        fbar = ctk.CTkFrame(f, fg_color="transparent")
        fbar.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(fbar, text="Filter by status:", font=("Segoe UI", 13),
                     text_color=COLORS["text_muted"]).pack(side="left")
        filt_var = ctk.StringVar(value="all")
        for val in ["all", "active", "terminated", "claimed", "surrendered", "expired"]:
            ctk.CTkButton(fbar, text=val.capitalize(), width=80, height=28,
                          fg_color=COLORS["accent"] if val == "all" else COLORS["border"],
                          text_color="#FFF" if val == "all" else COLORS["text_dark"],
                          font=("Segoe UI", 11), corner_radius=14,
                          command=lambda v=val: self._load_policies(v, f)
                          ).pack(side="left", padx=4)
        self._pol_container = ctk.CTkFrame(f, fg_color="transparent")
        self._pol_container.pack(fill="both", expand=True)
        self._load_policies("all", f)

    def _load_policies(self, status, parent):
        for w in self._pol_container.winfo_children(): w.destroy()
        filt = None if status == "all" else status
        data = get_agent_policies(self.agent_id, filt)
        cols = [{"key": "policy_id", "label": "ID", "width": 60},
                {"key": "plan_name", "label": "Plan", "width": 180},
                {"key": "customer_name", "label": "Customer", "width": 160},
                {"key": "installments", "label": "Installments", "width": 120},
                {"key": "status", "label": "Status", "width": 100}]
        for r in data:
            r["installments"] = f"{r.get('paid_installments', 0)} / {r.get('total_installments', 0)}"
        TableView(self._pol_container, cols, data, badge_col="status").pack(fill="both", expand=True)

    # ── Tab: Find Customers ─────────────────────────────────────
    def _show_available_customers(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Find New Customers")
        
        data = get_available_customers(self.agent_id)
        if not data:
            ctk.CTkLabel(f, text="No unassigned customers available at the moment.", 
                         font=("Segoe UI", 14), text_color=COLORS["text_muted"]).pack(pady=40)
            return

        cols = [{"key": "customer_id", "label": "ID", "width": 50},
                {"key": "full_name", "label": "Name", "width": 200},
                {"key": "email", "label": "Email", "width": 250}]
        
        action_cfg = {
            "header": "Action",
            "text": "Request",
            "fg_color": COLORS["accent"],
            "command": self._request_customer
        }
        TableView(f, cols, data, action_config=action_cfg).pack(fill="both", expand=True)

    def _request_customer(self, row):
        try:
            create_request(self.agent_id, row["customer_id"])
            self._show_msg(f"✅ Request submitted for {row['full_name']}. Waiting for Admin approval.")
            self._show_available_customers()
        except ValueError as e:
            self._show_msg(str(e), err=True)


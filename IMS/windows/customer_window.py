"""
IMS — Customer Dashboard Window
9-tab dashboard per SRS §7.2 (FR-C1 to FR-C12).
"""
import customtkinter as ctk
from datetime import date, datetime
from config import COLORS, APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from db.connection import execute_query
from components.sidebar import Sidebar
from components.table_view import TableView
from components.cards import StatCard, InfoCard, StatusBadge
from modules.policies import get_customer_policies, get_all_active_plans, create_policy, get_policy_detail
from modules.claims import file_claim, get_customer_claims
from modules.surrender import request_surrender, calculate_surrender_value, get_customer_surrenders
from modules.premium import get_unpaid_premiums_for_customer, mark_premium_paid, get_policy_premiums
from utils.helpers import format_currency, format_date
from utils.pdf_export import generate_table_report, generate_detailed_report
from windows.base_window import BaseWindow

class CustomerWindow(BaseWindow):
    def __init__(self, app_root, user: dict, login_window):
        super().__init__(app_root, user, login_window, f"{APP_NAME} — Customer Dashboard")
        # Get customer record
        rows = execute_query(
            "SELECT * FROM customers WHERE user_id=%s", (user["user_id"],), fetch=True)
        self.customer = rows[0] if rows else {}
        self.customer_id = self.customer.get("customer_id", 0)
        self._build_layout()

    def _build_layout(self):
        nav = [
            {"label": "Insurance Plans",  "icon": "📋", "command": self._show_plans},
            {"label": "My Plans",          "icon": "📄", "command": self._show_policies},
            {"label": "Premium Payments", "icon": "💰", "command": self._show_premiums},
            {"label": "File a Claim",     "icon": "📝", "command": self._show_file_claim},
            {"label": "My Claims",        "icon": "📊", "command": self._show_claims},
            {"label": "Surrender Plan",   "icon": "🔄", "command": self._show_surrender},
            {"label": "My Agent",         "icon": "👤", "command": self._show_agent},
            {"label": "About Us",         "icon": "ℹ️",  "command": self._show_about},
        ]
        self.sidebar = Sidebar(self, nav, self.user["full_name"], "Customer", self._logout)
        self.sidebar.pack(side="left", fill="y")
        # Top bar
        top = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], height=50, corner_radius=0,
                           border_width=1, border_color=COLORS["border"])
        top.pack(side="top", fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(top, text=f"👤 Welcome, {self.user['full_name']}",
                     font=("Segoe UI", 15, "bold"), text_color=COLORS["primary"]
                     ).pack(side="left", padx=20)
        # Content area
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_light"])
        self.content.pack(side="right", fill="both", expand=True)
        self._show_plans()
        self.after(500, self._check_notifications)

    # ── Tab: About Us ───────────────────────────────────────────
    def _show_about(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "About Us")
        info = {
            "Company": "IMS Insurance Corporation",
            "Mission": "Providing reliable insurance solutions for every Indian family.",
            "Founded": "2020",
            "Headquarters": "Mumbai, Maharashtra",
            "Branches": "Delhi, Bengaluru, Chennai, Kolkata, Hyderabad",
            "Email": "support@ims-insurance.com",
            "Phone": "1800-123-4567 (Toll Free)",
        }
        InfoCard(f, "Company Information", info).pack(fill="x", pady=8)

    # ── Tab: Insurance Plans ────────────────────────────────────
    def _show_plans(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Insurance Plans")
        plans = get_all_active_plans()
        if not plans:
            ctk.CTkLabel(f, text="No plans available.", font=("Segoe UI", 14),
                         text_color=COLORS["text_muted"]).pack(pady=40)
            return
        for plan in plans:
            card = ctk.CTkFrame(f, fg_color=COLORS["card_bg"], corner_radius=8,
                                border_width=1, border_color=COLORS["border"])
            card.pack(fill="x", pady=6)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=12)
            ctk.CTkLabel(inner, text=plan["plan_name"], font=("Segoe UI", 16, "bold"),
                         text_color=COLORS["primary"]).pack(anchor="w")
            ctk.CTkLabel(inner, text=f"{plan['plan_type'].upper()} • {plan.get('description','')}",
                         font=("Segoe UI", 12), text_color=COLORS["text_muted"],
                         wraplength=600).pack(anchor="w", pady=2)
            det = (f"Premium: {format_currency(plan['base_premium'])} / {plan['premium_frequency']}  •  "
                   f"Coverage: {format_currency(plan['coverage_amount'])}  •  "
                   f"Term: {plan['policy_term_years']} yrs  •  "
                   f"Age: {plan['min_age']}–{plan['max_age']}")
            ctk.CTkLabel(inner, text=det, font=("Segoe UI", 12),
                         text_color=COLORS["text_dark"]).pack(anchor="w", pady=2)
            btn_row = ctk.CTkFrame(inner, fg_color="transparent")
            btn_row.pack(fill="x", pady=(4, 0))
            
            ctk.CTkButton(btn_row, text="⭐ View Benefits", font=("Segoe UI", 12),
                          fg_color="transparent", text_color=COLORS["accent"], hover_color="#EBF5FB", width=120, height=30,
                          command=lambda p=plan: self._show_plan_benefits_view(p)
                          ).pack(side="left")
                          
            ctk.CTkButton(btn_row, text="Choose Plan", font=("Segoe UI", 13, "bold"),
                          fg_color=COLORS["accent"], hover_color="#2471A3", width=140, height=34,
                          command=lambda p=plan: self._purchase_plan(p)
                          ).pack(side="right")

    def _show_plan_benefits_view(self, plan):
        self._clear()
        f = self._make_scroll()
        
        # Header with Back button
        header_f = ctk.CTkFrame(f, fg_color="transparent")
        header_f.pack(fill="x", pady=(0, 20))
        
        ctk.CTkButton(header_f, text="← Back to Plans", font=("Segoe UI", 12),
                      fg_color=COLORS["border"], text_color=COLORS["text_dark"], 
                      hover_color="#BFC9CA", width=120, height=30,
                      command=self._show_plans).pack(side="left")
        
        ctk.CTkLabel(header_f, text=f"Plan Details: {plan['plan_name']}", 
                     font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"]
                     ).pack(side="left", padx=20)

        # Basic Info Card
        info = {
            "Plan Type": plan["plan_type"].upper(),
            "Base Premium": f"{format_currency(plan['base_premium'])} / {plan['premium_frequency']}",
            "Coverage Amount": format_currency(plan['coverage_amount']),
            "Policy Term": f"{plan['policy_term_years']} Years",
            "Age Eligibility": f"{plan['min_age']} to {plan['max_age']} Years",
        }
        InfoCard(f, "Key Information", info).pack(fill="x", pady=10)

        # Benefits Section
        ctk.CTkLabel(f, text="Plan Benefits", font=("Segoe UI", 18, "bold"), 
                     text_color=COLORS["primary"]).pack(anchor="w", pady=(20, 10))
        
        benefits_map = {
            "term": "• High coverage at very low premiums\n• Pure financial security for family\n• Simple and easy to understand\n• Tax benefits under Section 80C\n• Peace of mind for your loved ones' future",
            "endowment": "• Guaranteed maturity amount at end of term\n• Life cover throughout the policy period\n• Combines savings and protection in one plan\n• Loan facility available against policy value\n• Bonus additions based on performance",
            "whole_life": "• Lifetime coverage (up to age 99 or 100)\n• Leave a lasting legacy for your family\n• Fixed premiums that never increase\n• Option to withdraw partial cash value after maturity\n• Complete financial security for life",
            "pension": "• Guaranteed income for your retirement years\n• Accumulate a large corpus for senior life\n• Death benefit protects your spouse/nominee\n• Flexible payout options (Monthly/Quarterly)\n• Beat inflation with systematic planning",
            "micro": "• Extremely affordable premiums for everyone\n• Simplified documentation and easy entry\n• Weekly or monthly payment options\n• Fast and hassle-free claim settlement\n• Specifically designed for low-income stability",
            "ulip": "• Market-linked investment returns for wealth\n• Life insurance cover included with investment\n• Partial withdrawal facility for emergencies\n• Switch between different funds as per risk\n• Long-term wealth creation with protection",
        }
        
        benefit_text = benefits_map.get(plan["plan_type"], "• Comprehensive life cover\n• Financial security for family\n• Easy online management\n• Tax saving benefits")
        
        benefit_card = ctk.CTkFrame(f, fg_color=COLORS["card_bg"], corner_radius=8, 
                                    border_width=1, border_color=COLORS["border"])
        benefit_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(benefit_card, text=benefit_text, font=("Segoe UI", 14), justify="left",
                     text_color=COLORS["text_dark"], wraplength=700).pack(pady=20, padx=30, anchor="w")

        # Purchase Button at bottom
        ctk.CTkButton(f, text="Purchase This Plan", font=("Segoe UI", 14, "bold"),
                      fg_color=COLORS["success"], hover_color="#196F3D", width=200, height=40,
                      command=lambda p=plan: self._purchase_plan(p)
                      ).pack(pady=30)


    def _purchase_plan(self, plan):
        from utils.validators import calculate_age
        dob = self.customer.get("dob")
        if dob:
            age = calculate_age(dob if isinstance(dob, date) else datetime.strptime(str(dob), "%Y-%m-%d").date())
            if age < plan["min_age"] or age > plan["max_age"]:
                self._show_msg(f"Age {age} not eligible (needs {plan['min_age']}–{plan['max_age']}).", err=True)
                return
        agent_id = self.customer.get("assigned_agent_id")
        try:
            pid = create_policy(self.customer_id, plan["plan_id"], agent_id, date.today())
            execute_query("INSERT INTO audit_log (user_id, action) VALUES (%s,%s)",
                          (self.user["user_id"], f"Purchased policy #{pid} (plan: {plan['plan_name']})"))
            self._show_msg(f"✅ Policy created! ID: {pid}")
            self._show_policies()
        except Exception as e:
            self._show_msg(f"Error: {e}", err=True)

    # ── Tab: My Plans ──────────────────────────────────────────
    def _show_policies(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "My Plans")
        
        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(btn_frame, text="📥 Export Plans to PDF", 
                      command=self._export_policies).pack(side="left")
                      
        data = get_customer_policies(self.customer_id)
        cols = [{"key": "policy_id", "label": "ID", "width": 60},
                {"key": "plan_name", "label": "Plan", "width": 180},
                {"key": "installments", "label": "Installments", "width": 120},
                {"key": "status", "label": "Status", "width": 100}]
        
        # Format installments and add "Claim Refund" button for terminated policies
        for r in data:
            r["installments"] = f"{r.get('paid_installments', 0)} / {r.get('total_installments', 0)}"
        
        action = {
            "header": "Action",
            "text": "Claim Refund",
            "fg_color": COLORS["success"],
            "condition": lambda row: row["status"] == "terminated",
            "command": lambda row: self._show_file_claim(row["policy_id"])
        }
        
        TableView(f, cols, data, badge_col="status", action_config=action,
                  on_row_click=self._policy_detail).pack(fill="both", expand=True)

    def _export_policies(self):
        data = get_customer_policies(self.customer_id)
        if not data:
            self._show_msg("No policies to export.", err=True)
            return
        headers = ["Policy ID", "Plan", "Installments", "Paid", "Remaining", "Status"]
        table_data = [[
            r["policy_id"], 
            r["plan_name"], 
            r.get("total_installments", 0),
            r.get("paid_installments", 0),
            r.get("total_installments", 0) - r.get("paid_installments", 0),
            r["status"]
        ] for r in data]
        path = generate_table_report("My Policies Statement", headers, table_data, "customer_policies")
        self._show_msg(f"✅ Exported to Downloads/IMS_Reports!\nOpening file...")

    def _policy_detail(self, row):
        det = get_policy_detail(row["policy_id"])
        if not det:
            return
        self._clear()
        f = self._make_scroll()
        self._heading(f, f"Policy #{det['policy_id']} — {det['plan_name']}")
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
                      
        ctk.CTkButton(f, text="← Back to Policies", fg_color=COLORS["border"],
                      text_color=COLORS["text_dark"], hover_color="#BFC9CA", height=36,
                      command=self._show_policies).pack(anchor="w", pady=8)

    # ── Tab: Premium Payments ───────────────────────────────────
    def _show_premiums(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Premium Payments")
        
        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(btn_frame, text="📥 Export Payment History to PDF", 
                      command=self._export_payments).pack(side="left")
                      
        data = get_unpaid_premiums_for_customer(self.customer_id)
        if not data:
            ctk.CTkLabel(f, text="🎉 All premiums are paid!", font=("Segoe UI", 15),
                         text_color=COLORS["success"]).pack(pady=40)
            return
        for pr in data:
            row = ctk.CTkFrame(f, fg_color=COLORS["card_bg"], corner_radius=8,
                               border_width=1, border_color=COLORS["border"])
            row.pack(fill="x", pady=4)
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=10)
            ctk.CTkLabel(inner, text=f"Policy #{pr['policy_id']} — {pr['plan_name']}",
                         font=("Segoe UI", 14, "bold"), text_color=COLORS["primary"]).pack(side="left")
            ctk.CTkLabel(inner, text=f"Due: {format_date(pr['due_date'])}  |  {format_currency(pr['amount'])}",
                         font=("Segoe UI", 13), text_color=COLORS["text_dark"]).pack(side="left", padx=20)
            StatusBadge(inner, pr["status"]).pack(side="left", padx=8)
            ctk.CTkButton(inner, text="Mark Paid", width=100, height=30,
                          fg_color=COLORS["success"], hover_color="#196F3D",
                          font=("Segoe UI", 12, "bold"),
                          command=lambda p=pr: self._pay_premium(p)).pack(side="right")

    def _pay_premium(self, pr):
        mark_premium_paid(pr["premium_id"], self.user["user_id"])
        self._show_premiums()

    def _export_payments(self):
        data = execute_query(
            "SELECT pr.premium_id, pl.plan_name, pr.amount, pr.status, pr.paid_date "
            "FROM premiums pr JOIN policies p ON pr.policy_id=p.policy_id "
            "JOIN plans pl ON p.plan_id=pl.plan_id "
            "WHERE p.customer_id=%s AND pr.status='paid' ORDER BY pr.paid_date DESC", (self.customer_id,), fetch=True)
        if not data:
            self._show_msg("No paid premiums to export.", err=True)
            return
        headers = ["Premium ID", "Plan", "Amount", "Status", "Paid On"]
        table_data = [[r["premium_id"], r["plan_name"], format_currency(r.get("amount")), 
                       r["status"], format_date(r.get("paid_date"))] for r in data]
        path = generate_table_report("My Payment History", headers, table_data, "customer_payments")
        self._show_msg(f"✅ Exported to Downloads/IMS_Reports!\nOpening file...")

    # ── Tab: File a Claim ───────────────────────────────────────
    def _show_file_claim(self, preselected_policy_id=None):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "File a Claim")
        policies = execute_query(
            "SELECT p.policy_id, pl.plan_name, pl.coverage_amount, p.status "
            "FROM policies p JOIN plans pl ON p.plan_id=pl.plan_id "
            "WHERE p.customer_id=%s AND p.status IN ('active', 'terminated')", (self.customer_id,), fetch=True)
        if not policies:
            ctk.CTkLabel(f, text="No active policies available to file a claim.",
                         font=("Segoe UI", 14), text_color=COLORS["text_muted"]).pack(pady=40)
            return
        card = ctk.CTkFrame(f, fg_color=COLORS["card_bg"], corner_radius=8,
                            border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=8)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)
        ctk.CTkLabel(inner, text="Select Policy", font=("Segoe UI", 13),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        opts = [f"{p['policy_id']} — {p['plan_name']}" for p in policies]
        
        # Handle preselection for terminated policy refund
        default_val = opts[0]
        if preselected_policy_id:
            for opt in opts:
                if opt.startswith(f"{preselected_policy_id} —"):
                    default_val = opt
                    break
                    
        pol_var = ctk.StringVar(value=default_val)
        self.pol_menu = ctk.CTkComboBox(inner, values=opts, variable=pol_var, height=36,
                        state="readonly")
        self.pol_menu.pack(fill="x", pady=(4, 12))
        ctk.CTkLabel(inner, text="Reason", font=("Segoe UI", 13),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        reason_tb = ctk.CTkTextbox(inner, height=80, border_width=1,
                                   border_color=COLORS["border"])
        reason_tb.pack(fill="x", pady=(4, 12))
        ctk.CTkLabel(inner, text="Claim Amount (Full Coverage)", font=("Segoe UI", 13),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        amt_entry = ctk.CTkEntry(inner, height=36, state="readonly")
        amt_entry.pack(fill="x", pady=(4, 12))

        def update_amt(*args):
            sel = pol_var.get()
            pid = int(sel.split(" — ")[0])
            cov = next((p["coverage_amount"] for p in policies if p["policy_id"] == pid), 0)
            amt_entry.configure(state="normal")
            amt_entry.delete(0, "end")
            amt_entry.insert(0, str(int(cov)))
            amt_entry.configure(state="readonly")

        pol_var.trace_add("write", update_amt)
        update_amt()  # Initial fill
        
        if preselected_policy_id:
            reason_tb.insert("1.0", "Claim for full refund due to plan decommissioning.")
        err_lbl = ctk.CTkLabel(inner, text="", text_color=COLORS["danger"], font=("Segoe UI", 12))
        err_lbl.pack(anchor="w")

        def submit():
            pid = int(pol_var.get().split(" — ")[0])
            reason = reason_tb.get("1.0", "end").strip()
            try:
                amt = float(amt_entry.get())
            except ValueError:
                err_lbl.configure(text="Enter a valid amount.")
                return
            if not reason:
                err_lbl.configure(text="Reason is required.")
                return
            try:
                cid = file_claim(pid, self.user["user_id"], reason, amt)
                self._show_msg(f"✅ Claim submitted! ID: {cid}")
                self._show_claims()
            except Exception as e:
                err_lbl.configure(text=str(e))
        ctk.CTkButton(inner, text="Submit Claim", fg_color=COLORS["accent"],
                      hover_color="#2471A3", height=40, font=("Segoe UI", 14, "bold"),
                      command=submit).pack(fill="x", pady=(8, 0))

    # ── Tab: My Claims ──────────────────────────────────────────
    def _show_claims(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "My Claims")
        
        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(btn_frame, text="📥 Export Claims to PDF", 
                      command=self._export_claims).pack(side="left")
                      
        data = get_customer_claims(self.customer_id)
        cols = [{"key": "claim_id", "label": "ID", "width": 50},
                {"key": "plan_name", "label": "Plan", "width": 160},
                {"key": "amount_requested", "label": "Amount", "width": 100},
                {"key": "status", "label": "Status", "width": 90},
                {"key": "filed_at", "label": "Filed", "width": 140}]
        for r in data:
            r["display_amount"] = format_currency(r.get("amount_requested"))
            r["display_filed_at"] = format_date(r.get("filed_at"))
            
        action = {"header": "Action", "text": "📄 PDF", "fg_color": COLORS["accent"], "command": lambda r: self._export_pdf(r, "Claim")}
        display_cols = [{"key": "claim_id", "label": "ID", "width": 50},
                        {"key": "plan_name", "label": "Plan", "width": 160},
                        {"key": "display_amount", "label": "Amount", "width": 100},
                        {"key": "status", "label": "Status", "width": 90},
                        {"key": "display_filed_at", "label": "Filed", "width": 140}]
        TableView(f, display_cols, data, badge_col="status", action_config=action).pack(fill="both", expand=True)

    def _export_claims(self):
        data = get_customer_claims(self.customer_id)
        if not data:
            self._show_msg("No claims to export.", err=True)
            return
        headers = ["Claim ID", "Plan", "Amount", "Status", "Filed On"]
        table_data = [[r["claim_id"], r["plan_name"], format_currency(r.get("amount_requested")), 
                       r["status"], format_date(r.get("filed_at"))] for r in data]
        path = generate_table_report("My Claims History", headers, table_data, "customer_claims")
        self._show_msg(f"✅ Exported to Downloads/IMS_Reports!\nOpening file...")

    # ── Tab: Surrender Policy ───────────────────────────────────
    def _show_surrender(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "Surrender Policy")
        
        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(btn_frame, text="📥 Export Surrender History to PDF", 
                      command=self._export_surrenders).pack(side="left")
                      
        policies = execute_query(
            "SELECT p.policy_id, pl.plan_name FROM policies p JOIN plans pl ON p.plan_id=pl.plan_id "
            "WHERE p.customer_id=%s AND p.status='active'", (self.customer_id,), fetch=True)
        if not policies:
            ctk.CTkLabel(f, text="No active policies to surrender.",
                         font=("Segoe UI", 14), text_color=COLORS["text_muted"]).pack(pady=40)
            return
        card = ctk.CTkFrame(f, fg_color=COLORS["card_bg"], corner_radius=8,
                            border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=8)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)
        ctk.CTkLabel(inner, text="Select Policy", font=("Segoe UI", 13),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        opts = [f"{p['policy_id']} — {p['plan_name']}" for p in policies]
        pol_var = ctk.StringVar(value=opts[0])
        val_lbl = ctk.CTkLabel(inner, text="", font=("Segoe UI", 14, "bold"),
                               text_color=COLORS["accent"])

        def update_val(*_):
            pid = int(pol_var.get().split(" — ")[0])
            sv = calculate_surrender_value(pid)
            val_lbl.configure(text=f"Surrender Value: {format_currency(sv)} (simulated)")

        pol_cb = ctk.CTkComboBox(inner, values=opts, variable=pol_var, height=36,
                                 state="readonly", command=update_val)
        pol_cb.pack(fill="x", pady=(4, 12))
        val_lbl.pack(anchor="w", pady=(0, 12))
        update_val()
        ctk.CTkLabel(inner, text="Reason", font=("Segoe UI", 13),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        reason_tb = ctk.CTkTextbox(inner, height=80, border_width=1, border_color=COLORS["border"])
        reason_tb.pack(fill="x", pady=(4, 12))
        err_lbl = ctk.CTkLabel(inner, text="", text_color=COLORS["danger"], font=("Segoe UI", 12))
        err_lbl.pack(anchor="w")

        def submit():
            pid = int(pol_var.get().split(" — ")[0])
            reason = reason_tb.get("1.0", "end").strip()
            if not reason:
                err_lbl.configure(text="Reason is required.")
                return
            try:
                sid = request_surrender(pid, self.user["user_id"], reason)
                self._show_msg(f"✅ Surrender requested! ID: {sid}")
                self._show_policies()
            except Exception as e:
                err_lbl.configure(text=str(e))
        ctk.CTkButton(inner, text="Request Surrender", fg_color=COLORS["danger"],
                      hover_color="#A93226", height=40, font=("Segoe UI", 14, "bold"),
                      command=submit).pack(fill="x", pady=(8, 0))

        # --- Surrender History Section ---
        ctk.CTkLabel(f, text="Surrender History", font=("Segoe UI", 18, "bold"), 
                     text_color=COLORS["primary"]).pack(anchor="w", pady=(30, 10))
        
        history_data = get_customer_surrenders(self.customer_id)
        for h in history_data:
            h["display_value"] = format_currency(h["surrender_value"])
            h["display_date"] = format_date(h["requested_at"])
            
        h_cols = [{"key": "surrender_id", "label": "ID", "width": 50},
                  {"key": "plan_name", "label": "Plan", "width": 180},
                  {"key": "display_value", "label": "Value", "width": 120},
                  {"key": "display_date", "label": "Date", "width": 140}]
        
        h_action = {"header": "Action", "text": "📄 PDF", "fg_color": COLORS["accent"], "command": lambda r: self._export_pdf(r, "Surrender")}
        TableView(f, h_cols, history_data, action_config=h_action).pack(fill="both", expand=True)

    def _export_surrenders(self):
        data = execute_query(
            "SELECT s.surrender_id, pl.plan_name, s.surrender_value, s.status, s.requested_at "
            "FROM surrenders s JOIN policies p ON s.policy_id=p.policy_id "
            "JOIN plans pl ON p.plan_id=pl.plan_id "
            "WHERE p.customer_id=%s ORDER BY s.requested_at DESC", (self.customer_id,), fetch=True)
        if not data:
            self._show_msg("No surrenders to export.", err=True)
            return
        headers = ["ID", "Plan", "Value", "Status", "Requested On"]
        table_data = [[r["surrender_id"], r["plan_name"], format_currency(r.get("surrender_value")), 
                       r["status"], format_date(r.get("requested_at"))] for r in data]
        path = generate_table_report("My Surrender History", headers, table_data, "customer_surrenders")
        self._show_msg(f"✅ Exported to Downloads/IMS_Reports!\nOpening file...")

    # ── Tab: My Agent ───────────────────────────────────────────
    def _show_agent(self):
        self._clear()
        f = self._make_scroll()
        self._heading(f, "My Assigned Agent")
        aid = self.customer.get("assigned_agent_id")
        if not aid:
            ctk.CTkLabel(f, text="No agent assigned yet. Contact admin.",
                         font=("Segoe UI", 14), text_color=COLORS["text_muted"]).pack(pady=40)
            return
        rows = execute_query(
            "SELECT u.full_name, u.email, u.phone, a.license_no, a.region "
            "FROM agents a JOIN users u ON a.user_id=u.user_id WHERE a.agent_id=%s",
            (aid,), fetch=True)
        if rows:
            ag = rows[0]
            InfoCard(f, "Agent Details", {
                "Name": ag["full_name"], "Email": ag["email"],
                "Phone": ag["phone"], "License": ag["license_no"],
                "Region": ag["region"]
            }).pack(fill="x", pady=8)


    # ── Helpers ─────────────────────────────────────────────────
    def _export_pdf(self, row, req_type):
        try:
            policy = get_policy_detail(row["policy_id"])
            payments = [p for p in get_policy_premiums(row["policy_id"]) if p["status"] == "paid"]
            if req_type == "Claim":
                req_id = row["claim_id"]
                amt = row["amount_requested"]
                date = row["filed_at"]
            else:
                req_id = row["surrender_id"]
                amt = row["surrender_value"]
                date = row["requested_at"]
                
            request_info = {
                "type": req_type,
                "id": req_id,
                "requested_at": date,
                "amount": format_currency(amt),
                "reason": row.get("reason", "N/A"),
                "status": row["status"]
            }
            if req_type == "Claim" and row.get("resolved_at"):
                request_info["resolved_at"] = row["resolved_at"]
                
            generate_detailed_report(f"{req_type} Receipt - {row['plan_name']}", policy, payments, request_info, f"{req_type.lower()}_{req_id}")
        except Exception as e: self._show_msg(f"Export Error: {e}", err=True)



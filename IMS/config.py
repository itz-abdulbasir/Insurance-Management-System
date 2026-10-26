"""
IMS — Insurance Management System
Configuration: database credentials and application constants.
"""

import os as _os

import sys as _sys
_BASE_DIR = _os.path.dirname(_os.path.abspath(__file__))

if getattr(_sys, 'frozen', False):
    # If running as EXE, put DB in same folder as the EXE
    # _sys.executable is the path to the actual .exe file
    _EXE_DIR = _os.path.dirname(_sys.executable)
    _DB_PATH = _os.path.join(_EXE_DIR, "ims_db.sqlite3")
else:
    # If running as script, keep current logic
    _DB_PATH = _os.path.join(_BASE_DIR, "db", "ims_db.sqlite3")

DB_CONFIG = {
    "database": _DB_PATH
}

# ── Application Constants ────────────────────────────────────────────────────
APP_NAME = "Insurance Management System"
APP_VERSION = "1.0.0"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 700
LOGIN_WINDOW_WIDTH = 600
LOGIN_WINDOW_HEIGHT = 620
REGISTER_WINDOW_WIDTH = 600
REGISTER_WINDOW_HEIGHT = 700

# ── Load Environment Configuration ──────────────────────────────────────────
try:
    from dotenv import load_dotenv as _load_dotenv
    _ENV_PATH = _os.path.join(_os.path.dirname(_BASE_DIR), ".env")
    if _os.path.exists(_ENV_PATH):
        _load_dotenv(_ENV_PATH)
    else:
        _load_dotenv()
except ImportError:
    pass

# ── Seeded Admin Credentials & Registration Passkeys ────────────────────────
# Sourced securely from environment variables (.env)
ADMIN_NAME = _os.getenv("ADMIN_NAME", "System Administrator")
ADMIN_EMAIL = _os.getenv("ADMIN_EMAIL", "admin@ims.local")
ADMIN_PASSWORD = _os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_PASSKEY = _os.getenv("ADMIN_PASSKEY", "ADMIN_DEV_PASSKEY_CHANGE_ME")
AGENT_PASSKEY = _os.getenv("AGENT_PASSKEY", "AGENT_DEV_PASSKEY_CHANGE_ME")


# ── Color Palette (from DESIGN.md) ──────────────────────────────────────────
COLORS = {
    "primary":       "#1B4F72",
    "accent":        "#2E86C1",
    "success":       "#1E8449",
    "warning":       "#E67E22",
    "danger":        "#C0392B",
    "bg_light":      "#F0F3F4",
    "card_bg":       "#FFFFFF",
    "sidebar_hover": "#21618C",
    "sidebar_text":  "#AED6F1",
    "text_dark":     "#2C3E50",
    "text_muted":    "#5D6D7E",
    "border":        "#D5D8DC",
    "table_header":  "#EBF5FB",
    "table_alt":     "#FAFAFA",
}

# ── Status Badge Styles ─────────────────────────────────────────────────────
BADGE_STYLES = {
    "active":      {"bg": "#D5F5E3", "fg": "#1E8449"},
    "pending":     {"bg": "#FEF9E7", "fg": "#E67E22"},
    "claimed":     {"bg": "#D6EAF8", "fg": "#2E86C1"},
    "surrendered": {"bg": "#F9EBEA", "fg": "#C0392B"},
    "terminated":  {"bg": "#FDEDEC", "fg": "#CB4335"},
    "overdue":     {"bg": "#F9EBEA", "fg": "#C0392B"},
    "paid":        {"bg": "#D5F5E3", "fg": "#1E8449"},
    "due":         {"bg": "#FEF9E7", "fg": "#E67E22"},
    "approved":    {"bg": "#D5F5E3", "fg": "#1E8449"},
    "rejected":    {"bg": "#F9EBEA", "fg": "#C0392B"},
    "expired":     {"bg": "#EAECEE", "fg": "#7F8C8D"},
    "cancelled":   {"bg": "#EAECEE", "fg": "#7F8C8D"},
}

# ── Premium Frequency Deltas (in days) ──────────────────────────────────────
PREMIUM_DELTAS = {
    "weekly":    7,
    "monthly":   30,
    "quarterly": 90,
    "half-yearly": 182,
    "yearly":    365,
}

# ── Surrender Value Ratio ───────────────────────────────────────────────────
SURRENDER_RATIO = 0.60   # 60% of total paid premiums

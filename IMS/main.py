"""
IMS — Entry Point
Initialises the database, seeds the admin, and launches the Login window.
"""

import sys
import os
import customtkinter as ctk

# Ensure the IMS package root is on the path
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from db.connection import init_db
from auth.seed import seed_admin
from auth.login import LoginWindow


def main():
    """Application entry point."""
    print("[IMS] Starting Insurance Management System...")

    # Step 1: Initialize database (create DB + tables if needed)
    init_db()

    # Step 2: Seed default admin account and insurance plans
    seed_admin()
    from modules.seed_plans import seed_plans
    seed_plans()

    # Step 3: Mark overdue premiums (run on every startup per SRS §11.5)
    try:
        from db.connection import execute_query
        execute_query(
            "UPDATE premiums SET status = 'overdue' "
            "WHERE due_date < CURRENT_DATE AND status = 'due'"
        )
        print("[IMS] Overdue premiums updated.")
    except Exception as e:
        print(f"[IMS] Premium update warning: {e}")

    # Step 4: Launch the GUI
    print("[IMS] Launching GUI...")
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    app = LoginWindow()
    app.mainloop()

if __name__ == "__main__":
    main()

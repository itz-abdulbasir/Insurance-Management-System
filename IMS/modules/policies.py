"""
IMS — Policy Business Logic
Handles policy creation, listing, detail retrieval, and premium schedule generation.
Business logic ONLY — no GUI code (per SRS §8 maintainability).
"""

from datetime import date, timedelta
from db.connection import execute_query
from config import PREMIUM_DELTAS
from utils.helpers import calculate_end_date


def get_all_active_plans():
    """Fetch all active insurance plans for browsing."""
    return execute_query(
        "SELECT * FROM plans WHERE is_active = 1 ORDER BY plan_type, plan_name",
        fetch=True
    )


def get_plan_by_id(plan_id: int):
    """Fetch a single plan by its ID."""
    rows = execute_query(
        "SELECT * FROM plans WHERE plan_id = %s", (plan_id,), fetch=True
    )
    return rows[0] if rows else None


def get_customer_policies(customer_id: int):
    """Fetch all policies for a specific customer with plan names and premium counts."""
    return execute_query(
        "SELECT p.policy_id, pl.plan_name, pl.plan_type, p.start_date, p.end_date, p.status, p.created_at, "
        "(SELECT COUNT(*) FROM premiums WHERE policy_id = p.policy_id AND status = 'paid') as paid_installments, "
        "(SELECT COUNT(*) FROM premiums WHERE policy_id = p.policy_id) as total_installments "
        "FROM policies p JOIN plans pl ON p.plan_id = pl.plan_id "
        "WHERE p.customer_id = %s ORDER BY p.created_at DESC",
        (customer_id,), fetch=True
    )


def get_policy_detail(policy_id: int):
    """Fetch full policy details including plan, agent, and premium info."""
    rows = execute_query(
        "SELECT p.*, pl.plan_name, pl.plan_type, pl.base_premium, "
        "pl.coverage_amount, pl.premium_frequency, pl.policy_term_years, "
        "cu_user.full_name AS customer_name, "
        "u.full_name AS agent_name, u.phone AS agent_phone, "
        "a.region AS agent_region, a.license_no AS agent_license, "
        "(SELECT COUNT(*) FROM premiums WHERE policy_id = p.policy_id AND status = 'paid') as paid_installments, "
        "(SELECT COUNT(*) FROM premiums WHERE policy_id = p.policy_id) as total_installments "
        "FROM policies p "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "JOIN customers cu ON p.customer_id = cu.customer_id "
        "JOIN users cu_user ON cu.user_id = cu_user.user_id "
        "LEFT JOIN agents a ON p.agent_id = a.agent_id "
        "LEFT JOIN users u ON a.user_id = u.user_id "
        "WHERE p.policy_id = %s",
        (policy_id,), fetch=True
    )
    return rows[0] if rows else None


def create_policy(customer_id: int, plan_id: int, agent_id: int, start_date: date):
    """
    Create a new policy and generate premium schedule.
    Returns the new policy_id.
    """
    plan = get_plan_by_id(plan_id)
    if not plan:
        raise ValueError("Plan not found.")

    end_date = calculate_end_date(start_date, plan["policy_term_years"])

    # Insert policy
    policy_id = execute_query(
        "INSERT INTO policies (customer_id, plan_id, agent_id, start_date, end_date, status) "
        "VALUES (%s, %s, %s, %s, %s, 'active')",
        (customer_id, plan_id, agent_id, start_date, end_date)
    )

    # Generate premium schedule
    from utils.helpers import generate_premium_dates
    due_dates = generate_premium_dates(start_date, plan["premium_frequency"], plan["policy_term_years"])
    
    for due in due_dates:
        execute_query(
            "INSERT INTO premiums (policy_id, amount, due_date, status) "
            "VALUES (%s, %s, %s, 'due')",
            (policy_id, float(plan["base_premium"]), due)
        )

    return policy_id


def get_agent_policies(agent_id: int, status_filter: str = None):
    """Fetch all policies managed by a specific agent."""
    query = (
        "SELECT p.policy_id, pl.plan_name, u.full_name AS customer_name, "
        "p.start_date, p.end_date, p.status, "
        "(SELECT COUNT(*) FROM premiums WHERE policy_id = p.policy_id AND status = 'paid') as paid_installments, "
        "(SELECT COUNT(*) FROM premiums WHERE policy_id = p.policy_id) as total_installments "
        "FROM policies p "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "JOIN customers c ON p.customer_id = c.customer_id "
        "JOIN users u ON c.user_id = u.user_id "
        "WHERE p.agent_id = %s"
    )
    params = [agent_id]
    if status_filter:
        query += " AND p.status = %s"
        params.append(status_filter)
    query += " ORDER BY p.created_at DESC"
    return execute_query(query, tuple(params), fetch=True)


def get_all_policies(status_filter: str = None):
    """Admin: fetch all policies in the system."""
    query = (
        "SELECT p.policy_id, pl.plan_name, u.full_name AS customer_name, "
        "au.full_name AS agent_name, p.start_date, p.end_date, p.status, "
        "(SELECT COUNT(*) FROM premiums WHERE policy_id = p.policy_id AND status = 'paid') as paid_installments, "
        "(SELECT COUNT(*) FROM premiums WHERE policy_id = p.policy_id) as total_installments "
        "FROM policies p "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "JOIN customers c ON p.customer_id = c.customer_id "
        "JOIN users u ON c.user_id = u.user_id "
        "LEFT JOIN agents a ON p.agent_id = a.agent_id "
        "LEFT JOIN users au ON a.user_id = au.user_id"
    )
    params = []
    if status_filter:
        query += " WHERE p.status = %s"
        params.append(status_filter)
    query += " ORDER BY p.created_at DESC"
    return execute_query(query, tuple(params), fetch=True)

"""
IMS — Premium Business Logic
Handles premium tracking, overdue flagging, and payment marking.
"""

from db.connection import execute_query


def mark_overdue_premiums():
    """Flag all past-due premiums as overdue. Called on startup."""
    execute_query(
        "UPDATE premiums SET status = 'overdue' "
        "WHERE due_date < CURRENT_DATE AND status = 'due'"
    )


def get_customer_premiums(customer_id: int, status_filter: str = None):
    """Fetch premiums for all policies belonging to a customer."""
    query = (
        "SELECT pr.premium_id, pr.policy_id, pl.plan_name, pr.amount, "
        "pr.due_date, pr.paid_date, pr.status "
        "FROM premiums pr "
        "JOIN policies p ON pr.policy_id = p.policy_id "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "WHERE p.customer_id = %s"
    )
    params = [customer_id]
    if status_filter:
        query += " AND pr.status = %s"
        params.append(status_filter)
    query += " ORDER BY pr.due_date ASC"
    return execute_query(query, tuple(params), fetch=True)


def get_unpaid_premiums_for_customer(customer_id: int):
    """Fetch due and overdue premiums for a customer."""
    return execute_query(
        "SELECT pr.premium_id, pr.policy_id, pl.plan_name, pr.amount, "
        "pr.due_date, pr.status "
        "FROM premiums pr "
        "JOIN policies p ON pr.policy_id = p.policy_id "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "WHERE p.customer_id = %s AND pr.status IN ('due', 'overdue') "
        "AND p.status = 'active' "
        "ORDER BY pr.due_date ASC",
        (customer_id,), fetch=True
    )


def mark_premium_paid(premium_id: int, user_id: int):
    """Mark a premium as paid and log the action."""
    execute_query(
        "UPDATE premiums SET status = 'paid', paid_date = CURRENT_DATE "
        "WHERE premium_id = %s",
        (premium_id,)
    )
    # Audit log
    execute_query(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (user_id, f"Marked premium #{premium_id} as paid")
    )


def get_agent_overdue_premiums(agent_id: int):
    """Fetch overdue premiums for customers assigned to this agent."""
    return execute_query(
        "SELECT pr.premium_id, u.full_name AS customer_name, pr.policy_id, "
        "pl.plan_name, pr.amount, pr.due_date, pr.status "
        "FROM premiums pr "
        "JOIN policies p ON pr.policy_id = p.policy_id "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "JOIN customers cu ON p.customer_id = cu.customer_id "
        "JOIN users u ON cu.user_id = u.user_id "
        "WHERE cu.assigned_agent_id = %s AND pr.status = 'overdue' "
        "AND p.status = 'active' "
        "ORDER BY pr.due_date ASC",
        (agent_id,), fetch=True
    )


def get_policy_premiums(policy_id: int):
    """Fetch all premiums for a specific policy."""
    return execute_query(
        "SELECT premium_id, amount, due_date, paid_date, status "
        "FROM premiums WHERE policy_id = %s ORDER BY due_date ASC",
        (policy_id,), fetch=True
    )

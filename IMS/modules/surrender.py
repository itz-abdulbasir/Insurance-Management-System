"""
IMS — Surrender Business Logic
Handles surrender requests, value calculation, and approval/rejection.
"""

from db.connection import execute_query
from config import SURRENDER_RATIO


def calculate_surrender_value(policy_id: int) -> float:
    """
    Calculate surrender value = 60% of total premiums paid.
    Returns the computed surrender value.
    """
    result = execute_query(
        "SELECT SUM(amount) AS total_paid FROM premiums "
        "WHERE policy_id = %s AND status = 'paid'",
        (policy_id,), fetch=True
    )
    total_paid = result[0]["total_paid"] if result and result[0]["total_paid"] else 0
    return float(total_paid) * SURRENDER_RATIO


def request_surrender(policy_id: int, requested_by_user_id: int, reason: str):
    """
    Submit a surrender request on an active policy.
    Returns the new surrender_id.
    """
    # Validate policy is active
    policy = execute_query(
        "SELECT status FROM policies WHERE policy_id = %s",
        (policy_id,), fetch=True
    )
    if not policy or policy[0]["status"] != "active":
        raise ValueError("Can only surrender active policies.")

    surrender_value = calculate_surrender_value(policy_id)

    surrender_id = execute_query(
        "INSERT INTO surrenders (policy_id, requested_by, reason, surrender_value, status) "
        "VALUES (%s, %s, %s, %s, 'approved')",
        (policy_id, requested_by_user_id, reason, surrender_value)
    )

    # Immediately mark the policy as surrendered
    execute_query(
        "UPDATE policies SET status = 'surrendered' WHERE policy_id = %s",
        (policy_id,)
    )

    # Mark unpaid premiums as cancelled
    execute_query(
        "UPDATE premiums SET status = 'cancelled' WHERE policy_id = %s AND status IN ('due', 'overdue')",
        (policy_id,)
    )

    # Audit log
    execute_query(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (requested_by_user_id,
         f"Requested surrender #{surrender_id} on policy #{policy_id} "
         f"(value: {surrender_value:.2f})")
    )

    # 3. Notify Admin and Agent
    # Find agent user_id
    info = execute_query(
        "SELECT pl.plan_name, u.full_name as customer_name, a_u.user_id as agent_user_id "
        "FROM policies p "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "JOIN customers c ON p.customer_id = c.customer_id "
        "JOIN users u ON c.user_id = u.user_id "
        "LEFT JOIN agents a ON c.assigned_agent_id = a.agent_id "
        "LEFT JOIN users a_u ON a.user_id = a_u.user_id "
        "WHERE p.policy_id = %s", (policy_id,), fetch=True
    )[0]

    msg = f"Policy Surrendered: {info['customer_name']} has surrendered policy #{policy_id} ({info['plan_name']}). Surrender Value: {surrender_value:.2f}"
    
    # Notify all Admins
    admins = execute_query("SELECT user_id FROM users WHERE role = 'admin'", fetch=True)
    for adm in admins:
        execute_query("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (adm['user_id'], msg))
    
    # Notify Agent
    if info['agent_user_id']:
        execute_query("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (info['agent_user_id'], msg))

    return surrender_id


def get_agent_pending_surrenders(agent_id: int):
    """Fetch pending surrender requests from customers assigned to this agent."""
    return execute_query(
        "SELECT s.surrender_id, u.full_name AS customer_name, s.policy_id, "
        "pl.plan_name, s.reason, s.surrender_value, s.requested_at "
        "FROM surrenders s "
        "JOIN policies p ON s.policy_id = p.policy_id "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "JOIN customers cu ON p.customer_id = cu.customer_id "
        "JOIN users u ON cu.user_id = u.user_id "
        "WHERE cu.assigned_agent_id = %s AND s.status = 'pending' "
        "ORDER BY s.requested_at ASC",
        (agent_id,), fetch=True
    )


def resolve_surrender(surrender_id: int, status: str, resolved_by_user_id: int):
    """
    Approve or reject a surrender request.
    If approved, policy status is set to 'surrendered'.
    """
    if status not in ("approved", "rejected"):
        raise ValueError("Status must be 'approved' or 'rejected'.")

    execute_query(
        "UPDATE surrenders SET status = %s WHERE surrender_id = %s",
        (status, surrender_id)
    )

    if status == "approved":
        surr = execute_query(
            "SELECT policy_id FROM surrenders WHERE surrender_id = %s",
            (surrender_id,), fetch=True
        )
        if surr:
            pid = surr[0]["policy_id"]
            execute_query(
                "UPDATE policies SET status = 'surrendered' WHERE policy_id = %s",
                (pid,)
            )
            # Mark unpaid premiums as cancelled
            execute_query(
                "UPDATE premiums SET status = 'cancelled' WHERE policy_id = %s AND status IN ('due', 'overdue')",
                (pid,)
            )

    # Audit log
    execute_query(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (resolved_by_user_id, f"Surrender #{surrender_id} {status}")
    )


def get_all_surrenders(status_filter: str = None):
    """Admin: fetch all surrender requests."""
    query = (
        "SELECT s.surrender_id, u.full_name AS customer_name, s.policy_id, "
        "pl.plan_name, s.reason, s.surrender_value, s.status, s.requested_at "
        "FROM surrenders s "
        "JOIN policies p ON s.policy_id = p.policy_id "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "JOIN customers cu ON p.customer_id = cu.customer_id "
        "JOIN users u ON cu.user_id = u.user_id"
    )
    params = []
    if status_filter:
        query += " WHERE s.status = %s"
        params.append(status_filter)
    query += " ORDER BY s.requested_at DESC"
    return execute_query(query, tuple(params), fetch=True)

def get_customer_surrenders(customer_id: int):
    """Fetch all surrender requests for a specific customer."""
    return execute_query(
        "SELECT s.surrender_id, s.policy_id, pl.plan_name, s.reason, s.surrender_value, s.status, s.requested_at "
        "FROM surrenders s "
        "JOIN policies p ON s.policy_id = p.policy_id "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "WHERE p.customer_id = %s "
        "ORDER BY s.requested_at DESC",
        (customer_id,), fetch=True
    )

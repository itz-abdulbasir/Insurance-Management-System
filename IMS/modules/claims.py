"""
IMS — Claims Business Logic
Handles claim submission, approval, rejection, and listing.
"""

from db.connection import execute_query


def file_claim(policy_id: int, filed_by_user_id: int, reason: str, amount: float):
    """
    Submit a new claim on an active policy.
    Returns the new claim_id.
    """
    # Validate policy is active or terminated (by admin)
    policy = execute_query(
        "SELECT status FROM policies WHERE policy_id = %s",
        (policy_id,), fetch=True
    )
    if not policy or policy[0]["status"] not in ("active", "terminated"):
        raise ValueError("Can only file claims on active or terminated policies.")

    # Validate all premiums are paid (ONLY for active policies)
    # Terminated policies bypass this check because the admin discontinued the plan
    if policy[0]["status"] == "active":
        unpaid = execute_query(
            "SELECT COUNT(*) as c FROM premiums WHERE policy_id = %s AND status != 'paid'",
            (policy_id,), fetch=True
        )
        if unpaid and unpaid[0]["c"] > 0:
            raise ValueError("Must complete all installments (premiums) to claim a policy.")

    claim_id = execute_query(
        "INSERT INTO claims (policy_id, filed_by, reason, amount_requested, status) "
        "VALUES (%s, %s, %s, %s, 'pending')",
        (policy_id, filed_by_user_id, reason, amount)
    )

    # Audit log
    execute_query(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (filed_by_user_id, f"Filed claim #{claim_id} on policy #{policy_id}")
    )
    return claim_id


def get_customer_claims(customer_id: int):
    """Fetch all claims filed by a customer (via their policies)."""
    return execute_query(
        "SELECT c.claim_id, c.policy_id, pl.plan_name, c.reason, "
        "c.amount_requested, c.status, c.filed_at, c.resolved_at "
        "FROM claims c "
        "JOIN policies p ON c.policy_id = p.policy_id "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "WHERE p.customer_id = %s ORDER BY c.filed_at DESC",
        (customer_id,), fetch=True
    )


def get_agent_pending_claims(agent_id: int):
    """Fetch pending claims from customers assigned to this agent."""
    return execute_query(
        "SELECT c.claim_id, u.full_name AS customer_name, c.policy_id, "
        "c.reason, c.amount_requested, c.filed_at "
        "FROM claims c "
        "JOIN policies p ON c.policy_id = p.policy_id "
        "JOIN customers cu ON p.customer_id = cu.customer_id "
        "JOIN users u ON cu.user_id = u.user_id "
        "WHERE cu.assigned_agent_id = %s AND c.status = 'pending' "
        "ORDER BY c.filed_at ASC",
        (agent_id,), fetch=True
    )


def resolve_claim(claim_id: int, status: str, resolved_by_user_id: int):
    """
    Approve or reject a claim.
    If approved, policy status is set to 'claimed'.
    """
    if status not in ("approved", "rejected"):
        raise ValueError("Status must be 'approved' or 'rejected'.")

        # Requirement: must complete all installments (checked at filing time)
        # Term completion requirement removed per user request
        pass

    execute_query(
        "UPDATE claims SET status = %s, resolved_by = %s, resolved_at = NOW() "
        "WHERE claim_id = %s",
        (status, resolved_by_user_id, claim_id)
    )

    if status == "approved":
        # Get policy_id from claim and mark as claimed
        claim = execute_query(
            "SELECT policy_id FROM claims WHERE claim_id = %s",
            (claim_id,), fetch=True
        )
        if claim:
            execute_query(
                "UPDATE policies SET status = 'claimed' WHERE policy_id = %s",
                (claim[0]["policy_id"],)
            )

    # Audit log
    execute_query(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (resolved_by_user_id, f"Claim #{claim_id} {status}")
    )


def get_all_claims(status_filter: str = None):
    """Admin: fetch all claims in the system."""
    query = (
        "SELECT c.claim_id, u.full_name AS customer_name, c.policy_id, "
        "pl.plan_name, c.reason, c.amount_requested, c.status, "
        "c.filed_at, c.resolved_at "
        "FROM claims c "
        "JOIN policies p ON c.policy_id = p.policy_id "
        "JOIN plans pl ON p.plan_id = pl.plan_id "
        "JOIN customers cu ON p.customer_id = cu.customer_id "
        "JOIN users u ON cu.user_id = u.user_id"
    )
    params = []
    if status_filter:
        query += " WHERE c.status = %s"
        params.append(status_filter)
    query += " ORDER BY c.filed_at DESC"
    return execute_query(query, tuple(params), fetch=True)

"""
IMS — Agent Assignment Requests Business Logic
Handles agents requesting customers and admin approval/rejection.
"""

from db.connection import execute_query

def get_available_customers(agent_id: int):
    """
    Fetch customers who are currently unassigned and haven't 
    been requested by this agent already.
    """
    return execute_query(
        "SELECT c.customer_id, u.full_name, u.email "
        "FROM customers c "
        "JOIN users u ON c.user_id = u.user_id "
        "WHERE c.assigned_agent_id IS NULL "
        "AND c.customer_id NOT IN ("
        "  SELECT customer_id FROM agent_requests "
        "  WHERE agent_id = %s AND status = 'pending'"
        ")", (agent_id,), fetch=True
    )

def create_request(agent_id: int, customer_id: int):
    """Create a new pending assignment request."""
    # Check if already requested
    existing = execute_query(
        "SELECT request_id FROM agent_requests "
        "WHERE agent_id = %s AND customer_id = %s AND status = 'pending'",
        (agent_id, customer_id), fetch=True
    )
    if existing:
        raise ValueError("A request for this customer is already pending.")

    request_id = execute_query(
        "INSERT INTO agent_requests (agent_id, customer_id, status) "
        "VALUES (%s, %s, 'pending')",
        (agent_id, customer_id)
    )
    return request_id

def get_all_pending_requests():
    """Admin: Fetch all pending assignment requests."""
    return execute_query(
        "SELECT ar.request_id, ar.agent_id, u_agent.full_name as agent_name, "
        "ar.customer_id, u_cust.full_name as customer_name, ar.requested_at "
        "FROM agent_requests ar "
        "JOIN agents a ON ar.agent_id = a.agent_id "
        "JOIN users u_agent ON a.user_id = u_agent.user_id "
        "JOIN customers c ON ar.customer_id = c.customer_id "
        "JOIN users u_cust ON c.user_id = u_cust.user_id "
        "WHERE ar.status = 'pending'", fetch=True
    )

def resolve_request(request_id: int, status: str, admin_user_id: int):
    """Approve or reject a request."""
    if status not in ("approved", "rejected"):
        raise ValueError("Status must be 'approved' or 'rejected'.")

    # Get request details
    req = execute_query(
        "SELECT agent_id, customer_id FROM agent_requests WHERE request_id = %s",
        (request_id,), fetch=True
    )
    if not req:
        raise ValueError("Request not found.")

    agent_id = req[0]["agent_id"]
    customer_id = req[0]["customer_id"]

    # Update request status
    execute_query(
        "UPDATE agent_requests SET status = %s WHERE request_id = %s",
        (status, request_id)
    )

    if status == "approved":
        # Update customer assignment
        execute_query(
            "UPDATE customers SET assigned_agent_id = %s WHERE customer_id = %s",
            (agent_id, customer_id)
        )
        
        # Reject other pending requests for this customer
        execute_query(
            "UPDATE agent_requests SET status = 'rejected' "
            "WHERE customer_id = %s AND status = 'pending' AND request_id != %s",
            (customer_id, request_id)
        )

    # Audit log
    execute_query(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (admin_user_id, f"Assignment Request #{request_id} {status}")
    )

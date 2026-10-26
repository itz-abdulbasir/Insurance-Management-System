"""
IMS — Plan Management Business Logic
Handles plan creation, toggling, and deletion.
"""

from db.connection import execute_query

def get_all_plans():
    """Admin: Fetch all non-deleted plans."""
    return execute_query(
        "SELECT * FROM plans WHERE is_deleted = 0 ORDER BY plan_id DESC",
        fetch=True
    )

def add_plan(name, p_type, description, min_age, max_age, frequency, premium, coverage, term):
    """Create a new insurance plan."""
    # Check if plan name already exists
    existing = execute_query("SELECT plan_id FROM plans WHERE plan_name = %s AND is_deleted = 0", (name,), fetch=True)
    if existing:
        raise ValueError("A plan with this name already exists.")

    return execute_query(
        "INSERT INTO plans (plan_name, plan_type, description, min_age, max_age, "
        "premium_frequency, base_premium, coverage_amount, policy_term_years, is_deleted) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)",
        (name, p_type, description, int(min_age), int(max_age), frequency, 
         float(premium), float(coverage), int(term))
    )

def toggle_plan_status(plan_id, current_active, admin_user_id):
    """Switch plan between active and inactive. If inactivating, notify affected users."""
    new_status = 0 if current_active else 1
    execute_query("UPDATE plans SET is_active = %s WHERE plan_id = %s", (new_status, plan_id))
    
    if new_status == 0:
        # Trigger the decommissioning workflow
        _decommission_plan(plan_id)
                
    return new_status

def delete_plan(plan_id, admin_user_id):
    """
    Remove a plan from the dashboard. 
    This also terminates all related policies immediately as they are considered part of the plan.
    """
    # 1. Mark as deleted so it disappears from Admin Dashboard
    execute_query("UPDATE plans SET is_deleted = 1, is_active = 0 WHERE plan_id = %s", (plan_id,))
    
    # 2. Decommission all policies associated with this plan
    _decommission_plan(plan_id)

def _decommission_plan(plan_id):
    """Helper to terminate policies and notify users when a plan is deactivated or deleted."""
    plan = execute_query("SELECT plan_name, coverage_amount FROM plans WHERE plan_id = %s", (plan_id,), fetch=True)[0]
    
    # Find all active policies
    affected = execute_query(
        "SELECT p.policy_id, c.user_id as customer_user_id, c.assigned_agent_id, a_u.user_id as agent_user_id "
        "FROM policies p "
        "JOIN customers c ON p.customer_id = c.customer_id "
        "LEFT JOIN agents a ON c.assigned_agent_id = a.agent_id "
        "LEFT JOIN users a_u ON a.user_id = a_u.user_id "
        "WHERE p.plan_id = %s AND p.status = 'active'", (plan_id,), fetch=True
    )
    
    for row in affected:
        # A. Mark policy as 'terminated'
        execute_query("UPDATE policies SET status = 'terminated' WHERE policy_id = %s", (row['policy_id'],))
        
        # B. Notify Customer
        msg = (f"IMPORTANT: The plan '{plan['plan_name']}' has been removed/discontinued. "
                f"Your policy #{row['policy_id']} is now terminated. You are eligible for a "
                f"FULL REFUND claim of {plan['coverage_amount']}. Please file a claim from your dashboard.")
        execute_query("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (row['customer_user_id'], msg))
        
        # C. Notify Agent
        if row['agent_user_id']:
            agent_msg = (f"Alert: Plan '{plan['plan_name']}' removed. Policy #{row['policy_id']} "
                            f"for your customer is terminated. Full refund promised.")
            execute_query("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (row['agent_user_id'], agent_msg))

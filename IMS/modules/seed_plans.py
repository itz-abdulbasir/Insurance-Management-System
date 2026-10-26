"""
IMS — Plan Seeding Utility
Ensures default insurance plans are present in the database.
"""

from db.connection import execute_query

DEFAULT_PLANS = [
    ('Suraksha Term',       'term',       'Death benefit only — 1 Year Term',                  18, 60, 'monthly',      500.00,   500000.00,  1),
    ('Jeevan Endowment',    'endowment',  'Maturity payout + death cover — 3 Years Term',      18, 55, 'half-yearly', 7200.00,   300000.00,  3),
    ('Sampurna Whole Life', 'whole_life', 'Lifetime coverage — 2 Years Term',                  18, 50, 'half-yearly',10800.00,  1000000.00,  2),
    ('Pension Plus',        'pension',    'Post-retirement payout — 5 Years Term',             30, 55, 'monthly',     2000.00,  2000000.00,  5),
    ('Jan Suraksha Micro',  'micro',      'Affordable rural coverage — 1 Year Weekly',         18, 60, 'weekly',        50.00,    50000.00,  1),
    ('Bal Jeevan Micro',    'micro',      'Child education + life cover — 2 Years Term',        1, 18, 'monthly',      100.00,   100000.00,  2),
    ('ULIP Growth',         'ulip',       'Investment-linked simulated returns — 3 Years Term',18, 55, 'quarterly',   9000.00,  1500000.00,  3)
]

def seed_plans():
    """Seeds the plans table if empty or missing defaults."""
    for p in DEFAULT_PLANS:
        execute_query(
            "INSERT OR IGNORE INTO plans (plan_name, plan_type, description, min_age, max_age, "
            "premium_frequency, base_premium, coverage_amount, policy_term_years) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            p
        )
    print("[IMS] Insurance plans verified/seeded.")

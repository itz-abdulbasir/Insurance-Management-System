-- ============================================================================
-- IMS — Insurance Management System · Database Schema
-- SQLite  ·  Database: IMS_DB
-- All PKs are INTEGER PRIMARY KEY AUTOINCREMENT (never string identifiers)
-- ============================================================================

-- ─── USERS (all roles in one table) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    phone         VARCHAR(15),
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(50) NOT NULL,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── AGENTS ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agents (
    agent_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INT UNIQUE NOT NULL,
    license_no VARCHAR(50),
    region     VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ─── CUSTOMERS ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS customers (
    customer_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INT UNIQUE NOT NULL,
    dob               DATE,
    address           TEXT,
    nominee_name      VARCHAR(100),
    nominee_relation  VARCHAR(50),
    assigned_agent_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_agent_id) REFERENCES agents(agent_id) ON DELETE SET NULL
);

-- ─── PLANS (master catalogue) ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plans (
    plan_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name         VARCHAR(100) UNIQUE NOT NULL,
    plan_type         VARCHAR(50) NOT NULL,
    description       TEXT,
    min_age           INT DEFAULT 18,
    max_age           INT DEFAULT 60,
    premium_frequency VARCHAR(50) NOT NULL,
    base_premium      DECIMAL(10, 2) NOT NULL,
    coverage_amount   DECIMAL(12, 2) NOT NULL,
    policy_term_years INT NOT NULL,
    is_active         BOOLEAN DEFAULT TRUE,
    is_deleted        INTEGER DEFAULT 0
);

-- ─── POLICIES ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS policies (
    policy_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INT NOT NULL,
    plan_id     INT NOT NULL,
    agent_id    INT,
    start_date  DATE NOT NULL,
    end_date    DATE,
    status      VARCHAR(50) DEFAULT 'active',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id)     REFERENCES plans(plan_id),
    FOREIGN KEY (agent_id)    REFERENCES agents(agent_id) ON DELETE SET NULL
);

-- ─── PREMIUMS ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS premiums (
    premium_id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id  INT NOT NULL,
    amount     DECIMAL(10, 2) NOT NULL,
    due_date   DATE NOT NULL,
    paid_date  DATE,
    status     VARCHAR(50) DEFAULT 'due',
    FOREIGN KEY (policy_id) REFERENCES policies(policy_id) ON DELETE CASCADE
);

-- ─── CLAIMS ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS claims (
    claim_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id        INT NOT NULL,
    filed_by         INT NOT NULL,
    reason           TEXT,
    amount_requested DECIMAL(12, 2),
    status           VARCHAR(50) DEFAULT 'pending',
    filed_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at      TIMESTAMP NULL,
    resolved_by      INT,
    FOREIGN KEY (policy_id)   REFERENCES policies(policy_id) ON DELETE CASCADE,
    FOREIGN KEY (filed_by)    REFERENCES users(user_id),
    FOREIGN KEY (resolved_by) REFERENCES users(user_id)
);

-- ─── SURRENDERS ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS surrenders (
    surrender_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id       INT NOT NULL,
    requested_by    INT NOT NULL,
    reason          TEXT,
    surrender_value DECIMAL(12, 2),
    status          VARCHAR(50) DEFAULT 'pending',
    requested_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (policy_id)    REFERENCES policies(policy_id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by) REFERENCES users(user_id)
);

-- ─── AUDIT LOG ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    log_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INT,
    action    VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ─── AGENT REQUESTS (assignment requests) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_requests (
    request_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id    INT NOT NULL,
    customer_id INT NOT NULL,
    status      VARCHAR(50) DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
-- ─── NOTIFICATIONS ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    notif_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INT NOT NULL,
    message  TEXT NOT NULL,
    is_read  BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
-- ─── SEED: Default Insurance Plans ──────────────────────────────────────────
INSERT OR IGNORE INTO plans (plan_name, plan_type, description, min_age, max_age, premium_frequency, base_premium, coverage_amount, policy_term_years) VALUES
('Suraksha Term',       'term',       'Death benefit only — 1 Year Term',                  18, 60, 'monthly',      500.00,   500000.00,  1),
('Jeevan Endowment',    'endowment',  'Maturity payout + death cover — 3 Years Term',      18, 55, 'half-yearly', 7200.00,   300000.00,  3),
('Sampurna Whole Life', 'whole_life', 'Lifetime coverage — 2 Years Term',                  18, 50, 'half-yearly',10800.00,  1000000.00,  2),
('Pension Plus',        'pension',    'Post-retirement payout — 5 Years Term',             30, 55, 'monthly',     2000.00,  2000000.00,  5),
('Jan Suraksha Micro',  'micro',      'Affordable rural coverage — 1 Year Weekly',         18, 60, 'weekly',        50.00,    50000.00,  1),
('Bal Jeevan Micro',    'micro',      'Child education + life cover — 2 Years Term',        1, 18, 'monthly',      100.00,   100000.00,  2),
('ULIP Growth',         'ulip',       'Investment-linked simulated returns — 3 Years Term',18, 55, 'quarterly',   9000.00,  1500000.00,  3);

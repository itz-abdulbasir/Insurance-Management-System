# Insurance Management System (IMS) — Data Dictionary

This document provides a comprehensive technical reference for the attributes and types of the system's database entities, functional mechanisms, and core properties.

---

## 1. Database Entities (Attributes & Types)

These tables form the persistence layer of the system (SQLite).

### Table: `users`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `user_id` | INTEGER (PK) | Unique identifier for the user (Auto-increment). |
| `full_name` | VARCHAR(100) | Full legal name of the user. |
| `email` | VARCHAR(100) | Unique email address (used for login). |
| `phone` | VARCHAR(15) | Contact phone number. |
| `password_hash` | VARCHAR(255) | BCrypt hashed password. |
| `role` | VARCHAR(50) | User role: `admin`, `agent`, or `customer`. |
| `is_active` | BOOLEAN | Account status (True if active/approved). |
| `created_at` | TIMESTAMP | Registration timestamp. |

### Table: `agents`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `agent_id` | INTEGER (PK) | Unique agent identifier. |
| `user_id` | INTEGER (FK) | Reference to the `users` table. |
| `license_no` | VARCHAR(50) | Agent's professional license number. |
| `region` | VARCHAR(100) | Geographic area assigned to the agent. |

### Table: `customers`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `customer_id` | INTEGER (PK) | Unique customer identifier. |
| `user_id` | INTEGER (FK) | Reference to the `users` table. |
| `dob` | DATE | Date of birth. |
| `address` | TEXT | Physical residential address. |
| `nominee_name` | VARCHAR(100) | Name of the policy beneficiary. |
| `nominee_relation`| VARCHAR(50) | Relationship with the nominee. |
| `assigned_agent_id`| INTEGER (FK) | Reference to the `agents` table. |

### Table: `plans`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `plan_id` | INTEGER (PK) | Unique plan identifier. |
| `plan_name` | VARCHAR(100) | Name of the insurance product. |
| `plan_type` | VARCHAR(50) | Category: `term`, `endowment`, `whole_life`, etc. |
| `description` | TEXT | Detailed benefits and terms. |
| `min_age` | INTEGER | Minimum eligibility age. |
| `max_age` | INTEGER | Maximum eligibility age. |
| `premium_freq` | VARCHAR(50) | `weekly`, `monthly`, `quarterly`, `half-yearly`. |
| `base_premium` | DECIMAL | Standard cost per installment. |
| `coverage_amount` | DECIMAL | Sum assured (Death/Maturity benefit). |
| `policy_term` | INTEGER | Duration of the policy in years. |

### Table: `policies`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `policy_id` | INTEGER (PK) | Unique policy identifier. |
| `customer_id` | INTEGER (FK) | Reference to the `customers` table. |
| `plan_id` | INTEGER (FK) | Reference to the `plans` table. |
| `agent_id` | INTEGER (FK) | Reference to the `agents` table. |
| `start_date` | DATE | Policy activation date. |
| `end_date` | DATE | Policy maturity/expiry date. |
| `status` | VARCHAR(50) | `active`, `surrendered`, `claimed`, `terminated`. |

### Table: `premiums`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `premium_id` | INTEGER (PK) | Unique installment identifier. |
| `policy_id` | INTEGER (FK) | Reference to the `policies` table. |
| `amount` | DECIMAL | Cost of this specific installment. |
| `due_date` | DATE | Deadline for payment. |
| `paid_date` | DATE | Actual date of payment (if any). |
| `status` | VARCHAR(50) | `due`, `paid`, `overdue`, `cancelled`. |

### Table: `claims`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `claim_id` | INTEGER (PK) | Unique claim identifier. |
| `policy_id` | INTEGER (FK) | Reference to the `policies` table. |
| `filed_by` | INTEGER (FK) | User who filed the claim. |
| `reason` | TEXT | Reason for filing the claim. |
| `amount_requested` | DECIMAL | Payout amount requested. |
| `status` | VARCHAR(50) | `pending`, `approved`, `rejected`. |
| `filed_at` | TIMESTAMP | Date of filing. |

### Table: `surrenders`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `surrender_id` | INTEGER (PK) | Unique surrender identifier. |
| `policy_id` | INTEGER (FK) | Reference to the `policies` table. |
| `requested_by` | INTEGER (FK) | User who requested surrender. |
| `reason` | TEXT | Reason for surrendering. |
| `surrender_value` | DECIMAL | Calculated surrender value. |
| `status` | VARCHAR(50) | `pending`, `completed`. |

### Table: `audit_log`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `log_id` | INTEGER (PK) | Unique log entry identifier. |
| `user_id` | INTEGER (FK) | User who performed the action. |
| `action` | VARCHAR(255) | Description of the action. |
| `timestamp` | TIMESTAMP | Time of action. |

### Table: `agent_requests`
| Attribute | Type | Description |
| :--- | : :--- | :--- |
| `request_id` | INTEGER (PK) | Unique request identifier. |
| `agent_id` | INTEGER (FK) | Agent requesting assignment. |
| `customer_id` | INTEGER (FK) | Customer to be assigned. |
| `status` | VARCHAR(50) | `pending`, `approved`, `rejected`. |

### Table: `notifications`
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `notif_id` | INTEGER (PK) | Unique notification identifier. |
| `user_id` | INTEGER (FK) | Recipient user. |
| `message` | TEXT | Notification content. |
| `is_read` | BOOLEAN | Read status. |
| `created_at` | TIMESTAMP | Generation time. |

---

## 2. Functional Mechanisms (Methods & Logic)

Core business logic implemented in Python modules.

### Authentication & Authorization (`IMS/auth/`)
| Function | Parameters (Attr: Type) | Returns | Description |
| :--- | :--- | :--- | :--- |
| `LoginWindow._do_login` | `email`: str, `password`: str, `role`: str | None | Authenticates user against DB and routes to dashboard. |
| `RegisterWindow._do_register` | `name`: str, `email`: str, `pwd`: str, `role`: str, ... | None | Validates and creates new user/customer/agent entries. |

### Policy Management (`IMS/modules/policies.py`)
| Function | Parameters (Attr: Type) | Returns | Description |
| :--- | :--- | :--- | :--- |
| `create_policy` | `cust_id`: int, `plan_id`: int, `agent_id`: int, `start`: date | `policy_id`: int | Initializes policy and generates premium schedule. |
| `get_policy_detail` | `policy_id`: int | `dict` | Retrieves joined data (Plan, Agent, Status). |
| `get_all_active_plans` | None | `list[dict]` | Returns all available insurance products. |

### Claims & Surrenders (`IMS/modules/`)
| Function | Parameters (Attr: Type) | Returns | Description |
| :--- | :--- | :--- | :--- |
| `file_claim` | `policy_id`: int, `user_id`: int, `reason`: str, `amt`: float | `claim_id`: int | Records claim; validates all premiums are paid. |
| `calculate_surrender` | `policy_id`: int | `float` | Computes 60% of total paid premiums as value. |
| `request_surrender` | `policy_id`: int, `user_id`: int, `reason`: str | `surr_id`: int | Closes policy and records surrender value. |
| `resolve_claim` | `claim_id`: int, `status`: str, `user_id`: int | None | Admin/Agent approval/rejection of claims. |

---

## 3. System Properties (Key Global Constants)

Defined in `IMS/config.py` and across the application state.

| Property | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `SURRENDER_RATIO` | float | `0.60` | Multiplier for calculating surrender payout. |
| `PREMIUM_DELTAS` | dict | `{...}` | Date offsets for `monthly`, `weekly`, etc. |
| `COLORS` | dict | `{...}` | UI theme tokens (bg_light, primary, accent). |
| `APP_NAME` | str | `"IMS"` | Global application title. |
| `USER_SESSION` | dict | `None` | Runtime object storing logged-in user details. |

---

## 4. Input/Output Data Types (Common Enums)

| Property | Valid Values / Types | Context |
| :--- | :--- | :--- |
| **User Role** | `admin`, `agent`, `customer` | Authentication & Dashboard routing. |
| **Policy Status** | `active`, `surrendered`, `claimed`, `terminated`, `lapsed` | Policy lifecycle tracking. |
| **Premium Status** | `due`, `paid`, `overdue`, `cancelled` | Installment payment tracking. |
| **Claim Status** | `pending`, `approved`, `rejected` | Claims workflow management. |
| **Freq Type** | `weekly`, `monthly`, `quarterly`, `half-yearly` | Plan premium scheduling. |

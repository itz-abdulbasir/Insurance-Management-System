# Data Flow Diagram (DFD) - Insurance Management System

This document outlines the flow of data within the Insurance Management System (IMS) according to standard Software Engineering principles.

## 0. Core Data Entities

The following entities represent the primary data structures persisted in the system.

| Data Item | Definition |
| :--- | :--- |
| **Credentials** | email + password_hash + role |
| **User Profile** | full_name, phone, dob, address, etc. |
| **Plan Details** | plan_name, type, coverage, base_premium, frequency |
| **Policy Data** | customer_id, plan_id, agent_id, start_date, end_date, status |
| **Premium Schedule** | List of (due_date, amount, status) |
| **Payment Info** | premium_id, paid_date, method (simulated) |
| **Claim/Surrender Req** | policy_id, reason, amount_requested, status, filed_at |
| **Approval Remark** | status_change (approved/rejected) + admin_note |
| **Assignment Req** | agent_id, customer_id, status |
| **Audit Entry** | user_id, action, timestamp |
| **Notification** | user_id, message, timestamp |

---

## DFD Level 0: Context Diagram
**Goal**: Establish the context of the system (Users and Data I/O).

```mermaid
graph TD
    %% External Entities (Rectangles)
    Customer[Customer]
    Agent[Agent]
    Admin[Admin]

    %% System Process (Single Bubble - Noun)
    IMS((Insurance Management System <br/> 0.0))

    %% Data Flows: Customer
    Customer -- "Registration/Login Data" --> IMS
    Customer -- "Policy Application & Payments" --> IMS
    Customer -- "Claim & Surrender Requests" --> IMS
    IMS -- "Policy Documents & Receipts" --> Customer
    IMS -- "Status Notifications" --> Customer

    %% Data Flows: Agent
    Agent -- "Assignment Requests" --> IMS
    Agent -- "Customer Support Logs" --> IMS
    IMS -- "Assigned Customer Data" --> Agent
    IMS -- "Commission Reports (PDF)" --> Agent

    %% Data Flows: Admin
    Admin -- "Plan Creation & Updates" --> IMS
    Admin -- "Approval Decisions" --> IMS
    Admin -- "Agent Assignments" --> IMS
    IMS -- "System Analytics & Audit Logs" --> Admin
```

### Level 0: Data Flow Dictionary

| Data Flow | Content / Elements |
| :--- | :--- |
| **Registration/Login Data** | `full_name + email + password + phone + address + dob + role` |
| **Policy Application** | `customer_id + plan_id + duration + frequency + initial_payment` |
| **Claim & Surrender Req** | `policy_id + request_type + reason + supporting_info` |
| **Policy Docs & Receipts** | `policy_record + premium_schedule + payment_receipt (PDF)` |
| **Status Notifications** | `message_body + timestamp + priority_level` |
| **Assignment Requests** | `agent_id + customer_id + bidding_note` |
| **Approval Decisions** | `request_id + status (Approved/Rejected) + admin_remark` |
| **Analytics & Audit Logs** | `system_usage_stats + financial_summaries + user_activity_trail` |

---

## DFD Level 1: System Decomposition
**Goal**: Decompose the Level 0 bubble into major processes. All external entities and data stores are shown. Balancing with Level 0 is maintained.

```mermaid
graph TB
    %% External Entities (Rectangles)
    Customer[Customer]
    Agent[Agent]
    Admin[Admin]

    %% Processes (Bubbles - Circles)
    P0_1((0.1 <br/> Authenticate & <br/> Manage Profile))
    P0_2((0.2 <br/> Maintain Plan <br/> Catalogue))
    P0_3((0.3 <br/> Track Policies & <br/> Premiums))
    P0_4((0.4 <br/> Process Claims & <br/> Surrenders))
    P0_5((0.5 <br/> Manage Agent <br/> Assignments))
    P0_6((0.6 <br/> Generate Reports <br/> & Analytics))

    %% Data Stores (Open Rectangles - Parallel Lines)
    D1["___________________ <br/> D1: Users Store <br/> ___________________"]
    D2["___________________ <br/> D2: Plans Store <br/> ___________________"]
    D3["___________________ <br/> D3: Policies Store <br/> ___________________"]
    D4["___________________ <br/> D4: Transactions Store <br/> ___________________"]
    D5["___________________ <br/> D5: Requests Store <br/> ___________________"]
    D6["___________________ <br/> D6: Logs & Notifs <br/> ___________________"]

    %% Styling for Data Stores to appear as open rectangles (parallel lines)
    style D1 stroke-width:0px,fill:none
    style D2 stroke-width:0px,fill:none
    style D3 stroke-width:0px,fill:none
    style D4 stroke-width:0px,fill:none
    style D5 stroke-width:0px,fill:none
    style D6 stroke-width:0px,fill:none

    %% Data Flows: Customer Interactions
    Customer -- "Registration/Login Data" --> P0_1
    Customer -- "Policy Application & Payments" --> P0_3
    Customer -- "Claim & Surrender Requests" --> P0_4
    P0_6 -- "Policy Documents & Receipts" --> Customer
    P0_6 -- "Status Notifications" --> Customer

    %% Data Flows: Agent Interactions
    Agent -- "Assignment Requests" --> P0_5
    Agent -- "Customer Support Logs" --> P0_5
    P0_6 -- "Assigned Customer Data" --> Agent
    P0_6 -- "Commission Reports" --> Agent

    %% Data Flows: Admin Interactions
    Admin -- "Plan Creation & Updates" --> P0_2
    Admin -- "Approval Decisions" --> P0_4
    Admin -- "Agent Assignments" --> P0_5
    P0_6 -- "Analytics & Audit Logs" --> Admin

    %% Internal Data Flows (Process <-> Store)
    P0_1 <--> D1
    P0_2 --> D2
    D2 -- "Plan Details" --> P0_3
    P0_3 --> D3
    P0_4 <--> D4
    P0_4 --> D6
    P0_5 <--> D5
    P0_5 --> D1
    
    %% Report Fetching
    D3 -- "Policy Data" --> P0_6
    D4 -- "Claim Data" --> P0_6
    D6 -- "Audit/Notif Data" --> P0_6
```

### Level 1: Data Flow Dictionary

| Data Flow | Content / Elements |
| :--- | :--- |
| **Credentials** | `email + hashed_password + user_role` |
| **Plan Config** | `name + type + base_premium + coverage_amount + tenure` |
| **Update Catalogue** | `structured_plan_object (for D2 storage)` |
| **Plan Details** | `plan_id + rate_table + eligibility_criteria` |
| **Buy Plan / Pay Premium**| `customer_id + amount + payment_token + policy_meta` |
| **Create Policy** | `policy_id + start_date + end_date + agent_id` |
| **Receipt Data** | `transaction_id + amount_paid + balance_due` |
| **Decision** | `admin_user_id + target_id + action_type` |
| **Log Request** | `source_process + timestamp + data_diff` |
| **Update Linkage** | `customer_id + new_agent_id` |

---

## DFD Level 2: Detailed Processes

### 2.1 Process 0.3: Policy & Premium Lifecycle
**Balancing**: Matches Input/Output of L1 Process 0.3.

```mermaid
graph TB
    %% Entities & Stores
    Customer[Customer]
    D2["___________________ <br/> D2: Plans Store <br/> ___________________"]
    D3["___________________ <br/> D3: Policies Store <br/> ___________________"]
    
    style D2 stroke-width:0px,fill:none
    style D3 stroke-width:0px,fill:none

    %% Sub-processes (Circles)
    P0_3_1((0.3.1 <br/> Calculate <br/> Premium))
    P0_3_2((0.3.2 <br/> Create Policy <br/> Record))
    P0_3_3((0.3.3 <br/> Generate <br/> Schedule))
    P0_3_4((0.3.4 <br/> Process <br/> Payment))

    Customer -- "Select Plan" --> P0_3_1
    D2 -- "Base Rates" --> P0_3_1
    P0_3_1 -- "Total Premium" --> P0_3_2
    P0_3_2 -- "Policy ID" --> D3
    P0_3_2 -- "Trigger Schedule" --> P0_3_3
    P0_3_3 -- "Due Dates" --> D3
    Customer -- "Pay Premium" --> P0_3_4
    P0_3_4 -- "Update Status" --> D3
```

### 2.2 Process 0.4: Claims & Surrender Workflow
**Balancing**: Matches Input/Output of L1 Process 0.4.

```mermaid
graph TB
    %% Entities & Stores
    Customer[Customer]
    Admin[Admin]
    D3["___________________ <br/> D3: Policies Store <br/> ___________________"]
    D4["___________________ <br/> D4: Transactions Store <br/> ___________________"]
    D6["___________________ <br/> D6: Logs & Notifs <br/> ___________________"]

    style D3 stroke-width:0px,fill:none
    style D4 stroke-width:0px,fill:none
    style D6 stroke-width:0px,fill:none

    %% Sub-processes (Circles)
    P0_4_1((0.4.1 <br/> Validate <br/> Eligibility))
    P0_4_2((0.4.2 <br/> Record <br/> Request))
    P0_4_3((0.4.3 <br/> Adjudicate <br/> Request))
    P0_4_4((0.4.4 <br/> Final <br/> Settlement))

    Customer -- "File Req" --> P0_4_1
    D3 -- "Policy Status" --> P0_4_1
    P0_4_1 -- "Valid Req" --> P0_4_2
    P0_4_2 -- "Insert Entry" --> D4
    Admin -- "Approval Decision" --> P0_4_3
    P0_4_3 -- "Status Update" --> D4
    P0_4_3 -- "Close Policy" --> P0_4_4
    P0_4_4 -- "Update Status" --> D3
    P0_4_4 -- "Log Action" --> D6
```

### 2.3 Process 0.5: Agent Assignment Management
**Balancing**: Matches Input/Output of L1 Process 0.5.

```mermaid
graph TB
    %% Entities & Stores
    Agent[Agent]
    Admin[Admin]
    D1["___________________ <br/> D1: Users Store <br/> ___________________"]
    D5["___________________ <br/> D5: Requests Store <br/> ___________________"]
    D6["___________________ <br/> D6: Logs & Notifs <br/> ___________________"]

    style D1 stroke-width:0px,fill:none
    style D5 stroke-width:0px,fill:none
    style D6 stroke-width:0px,fill:none

    %% Sub-processes (Circles)
    P0_5_1((0.5.1 <br/> Submit Bidding <br/> Request))
    P0_5_2((0.5.2 <br/> Review & <br/> Decision))
    P0_5_3((0.5.3 <br/> Link Agent <br/> to Customer))
    P0_5_4((0.5.4 <br/> Notify <br/> Participants))

    Agent -- "Bidding Req" --> P0_5_1
    P0_5_1 -- "Store Request" --> D5
    
    Admin -- "Approval Decision" --> P0_5_2
    D5 -- "Fetch Pending" --> P0_5_2
    P0_5_2 -- "Update Status" --> D5
    P0_5_2 -- "Approved Signal" --> P0_5_3
    
    P0_5_3 -- "Update agent_id" --> D1
    P0_5_3 -- "Trigger Notif" --> P0_5_4
    P0_5_4 -- "Log Action" --> D6
```

### Level 2: Data Flow Dictionary (Internal)

| Data Flow | Content / Elements |
| :--- | :--- |
| **Base Rates** | `plan_base_price + age_multiplier + tenure_factor` |
| **Total Premium** | `(base_rate * frequency_index) + taxes` |
| **Trigger Schedule** | `policy_start_date + frequency (Monthly/Yearly)` |
| **Due Dates** | `List of upcoming_payment_dates` |
| **Valid Req** | `request_id + validation_flag (True/False)` |
| **Approved Signal** | `authorized_admin_id + approval_timestamp` |
| **Bidding Note** | `agent_experience + justification_text` |
| **Update agent_id** | `agent_request_id -> confirmed_agent_id` |


## Key Data Stores Mapping

| Store ID | Name | Database Tables |
| :--- | :--- | :--- |
| **D1** | Users Store | `users`, `agents`, `customers` |
| **D2** | Plans Store | `plans` |
| **D3** | Policies Store | `policies`, `premiums` |
| **D4** | Transactions Store | `claims`, `surrenders` |
| **D5** | Requests Store | `agent_requests` |
| **D6** | Logs & Notifs | `audit_log`, `notifications` |

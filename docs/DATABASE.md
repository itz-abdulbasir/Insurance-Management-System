## 1. Entity-Relationship Diagram (Chen's Notation)

This section provides a professional visual representation and the corresponding source code for the Insurance Management System's data model.

### 1.1 High-Resolution Diagram
![Professional IMS ER Diagram](file:///C:/Users/91970/.gemini/antigravity/brain/5a0c7d45-97e9-41c6-8cdf-c7932373294f/ims_er_diagram_final_strict_v3_1777325758675.png)

### 1.2 Mermaid Source Code (Organized)

### 1.2 Mermaid Source Code (Refined Korth's Notation)

```mermaid
flowchart TB
    %% Styles for Chen Notation
    classDef entity fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef weakEntity fill:#e3f2fd,stroke:#1565c0,stroke-width:4px
    classDef relation fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef weakRelation fill:#fff3e0,stroke:#ef6c00,stroke-width:4px
    classDef attribute fill:#ffffff,stroke:#37474f,stroke-width:1px
    classDef pkAttr fill:#ffffff,stroke:#37474f,stroke-width:2px
    classDef fkAttr fill:#ffffff,stroke:#37474f,stroke-width:1px,stroke-dasharray: 5 5

    %% Entities
    User[User]:::entity
    Agent[Agent]:::entity
    Customer[Customer]:::entity
    Plan[Plan]:::entity
    Policy[Policy]:::entity
    
    %% Weak Entities
    Premium[[Premium]]:::weakEntity
    Claim[[Claim]]:::weakEntity
    Surrender[[Surrender]]:::weakEntity
    AuditLog[[AuditLog]]:::weakEntity
    Notif[[Notification]]:::weakEntity
    AgntReq[[AgentRequest]]:::weakEntity

    %% Relationships (Diamonds)
    ISA{IS A}:::relation
    Manages{MANAGES}:::relation
    Holds{HOLDS}:::relation
    Defines{DEFINES}:::relation
    Has{{HAS}}:::weakRelation
    FilesCl{{FILES}}:::weakRelation
    FilesSr{{FILES}}:::weakRelation
    Logs{{LOGS}}:::weakRelation
    Receives{{RECEIVES}}:::weakRelation
    AgntRequests{{REQUESTS}}:::weakRelation
    CustInvolved{{INVOLVED}}:::weakRelation

    %% Structural Connections (Entities connected only to Relationships)
    User --- ISA
    ISA --- Customer
    ISA --- Agent
    
    Agent -- "1" --- Manages --- "N" -- Customer
    Customer -- "1" --- Holds --- "N" -- Policy
    Plan -- "1" --- Defines --- "N" -- Policy
    
    %% Weak Entity Relationships
    Policy -- "1" === Has === "N" -- Premium
    Policy -- "1" === FilesCl === "N" -- Claim
    Policy -- "1" === FilesSr === "N" -- Surrender
    User -- "1" === Logs === "N" -- AuditLog
    User -- "1" === Receives === "N" -- Notif
    Agent -- "1" === AgntRequests === "N" -- AgntReq
    Customer -- "1" === CustInvolved === "N" -- AgntReq

    %% Attributes: User
    u_id([<u>user_id</u>]):::pkAttr --- User
    u_name([full_name]) --- User
    u_email([email]) --- User
    u_phone([phone]) --- User
    u_role([role]) --- User
    u_act([is_active]) --- User

    %% Attributes: Customer
    c_id([<u>cust_id</u>]):::pkAttr --- Customer
    c_uid([user_id]):::fkAttr --- Customer
    c_dob([dob]) --- Customer
    c_addr([address]) --- Customer
    c_nom([nominee]) --- Customer
    c_aid([agent_id]):::fkAttr --- Customer

    %% Attributes: Agent
    a_id([<u>agent_id</u>]):::pkAttr --- Agent
    a_uid([user_id]):::fkAttr --- Agent
    a_lic([license_no]) --- Agent
    a_reg([region]) --- Agent

    %% Attributes: Plan
    pl_id([<u>plan_id</u>]):::pkAttr --- Plan
    pl_name([plan_name]) --- Plan
    pl_type([plan_type]) --- Plan
    pl_prem([base_premium]) --- Plan
    pl_cov([coverage]) --- Plan

    %% Attributes: Policy
    p_id([<u>policy_id</u>]):::pkAttr --- Policy
    p_cid([cust_id]):::fkAttr --- Policy
    p_pid([plan_id]):::fkAttr --- Policy
    p_aid([agent_id]):::fkAttr --- Policy
    p_stat([status]) --- Policy
    p_start([start_date]) --- Policy

    %% Attributes: Premium
    pr_id([<u>prem_id</u>]):::pkAttr --- Premium
    pr_pid([policy_id]):::fkAttr --- Premium
    pr_amt([amount]) --- Premium
    pr_due([due_date]) --- Premium
    pr_stat([status]) --- Premium

    %% Attributes: Claim
    cl_id([<u>claim_id</u>]):::pkAttr --- Claim
    cl_pid([policy_id]):::fkAttr --- Claim
    cl_by([filed_by]):::fkAttr --- Claim
    cl_rsn([reason]) --- Claim
    cl_stat([status]) --- Claim

    %% Attributes: AuditLog
    lg_id([<u>log_id</u>]):::pkAttr --- AuditLog
    lg_uid([user_id]):::fkAttr --- AuditLog
    lg_act([action]) --- AuditLog
    lg_ts([timestamp]) --- AuditLog

    %% Attributes: Notification
    n_id([<u>notif_id</u>]):::pkAttr --- Notif
    n_uid([user_id]):::fkAttr --- Notif
    n_msg([message]) --- Notif
    n_read([is_read]) --- Notif
```

## 2. Relationship Explanations

| Relationship | Type | Description |
| :--- | :--- | :--- |
| **User Specialization** | IS A | `User` is the super-entity for `Customer`, `Agent`, and `Admin`. |
| **Agent Management** | 1 -- N | An `Agent` (1) manages multiple `Customers` (N). |
| **Policy Holding** | 1 -- N | A `Customer` (1) holds multiple `Policies` (N). |
| **Plan Definition** | 1 -- N | A `Plan` (1) defines the terms for multiple `Policies` (N). |
| **Agent Service** | 1 -- N | An `Agent` (1) services multiple `Policies` (N). |
| **Policy Financials** | 1 -- N | `Policy` (1) has multiple `Premiums` (N). `Premium` is a weak entity. |
| **Claims/Surrenders** | 1 -- N | `Policy` (1) involves multiple `Claims` or `Surrenders`. Weak entities. |
| **Assignment Bidding** | 1 -- 1 | `Agent Request` connects an `Agent` and a `Customer` for a specific request. |

## 3. Entity & Attribute Dictionary

| Entity | Attribute |
| :--- | :--- |
| **User** | `user_id` (PK), `full_name`, `email`, `phone`, `password_hash`, `role`, `is_active`, `created_at` |
| **Customer** | `cust_id` (PK), `user_id` (FK), `dob`, `address`, `nominee_name`, `nominee_relation`, `assigned_agent_id` (FK) |
| **Agent** | `agent_id` (PK), `user_id` (FK), `license_no`, `region` |
| **Plan** | `plan_id` (PK), `plan_name`, `plan_type`, `description`, `min_age`, `max_age`, `premium_frequency`, `base_premium`, `coverage_amount`, `policy_term_years`, `is_active` |
| **Policy** | `policy_id` (PK), `customer_id` (FK), `plan_id` (FK), `agent_id` (FK), `start_date`, `end_date`, `status`, `created_at` |
| **Premium** | `prem_id` (PK), `policy_id` (FK), `amount`, `due_date`, `paid_date`, `status` |
| **Claim** | `claim_id` (PK), `policy_id` (FK), `filed_by` (FK), `reason`, `amount_requested`, `status`, `filed_at`, `resolved_at`, `resolved_by` (FK) |
| **Surrender** | `surr_id` (PK), `policy_id` (FK), `requested_by` (FK), `reason`, `surrender_value`, `status`, `requested_at` |
| **AuditLog** | `log_id` (PK), `user_id` (FK), `action`, `timestamp` |
| **AgentRequest** | `request_id` (PK), `agent_id` (FK), `customer_id` (FK), `status`, `requested_at` |
| **Notification** | `notif_id` (PK), `user_id` (FK), `message`, `is_read`, `created_at` |

## 4. Data Integrity Rules

1. **Cascading Deletes**: If a `User` is deleted, the corresponding `Customer`/`Agent`/`Admin` record must be purged.
2. **Status Consistency**: A `Premium` cannot be marked 'Paid' without a `paid_date`. A `Policy` cannot be 'Active' if its `end_date` has passed.
3. **Uniqueness**: `email` in `Users` and `license_number` in `Agents` must be unique across the system.

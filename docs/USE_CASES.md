# Use Case Analysis - Insurance Management System (v1.2)

This document outlines the functional requirements of the Insurance Management System (IMS) through Use Case Diagrams and detailed process descriptions, reflecting all features implemented to date.

## 1. Use Case Model

The following diagram illustrates the interactions between system actors (Customer, Agent, Admin) and the core functionalities of the system.

The following diagram illustrates the interactions between system actors (Customer, Agent, Admin) and the core functionalities of the system.

![IMS Use Case Diagram](file:///C:/Users/91970/.gemini/antigravity/brain/843f6fb5-f453-4caf-b552-8984f80cfb59/ims_use_case_diagram_professional_1777316919254.png)

---

---

## 2. Use Case Descriptions

### UC1: Register & Authenticate
| Field | Description |
| :--- | :--- |
| **Actors** | Customer, Agent, Admin |
| **Description** | Users create accounts or log in. Customers self-register; Staff (Agent/Admin) require a **Passkey** and subsequent **Admin Approval** before activation. |
| **Pre-condition** | System is initialized (DB seeded). |
| **Post-condition** | Active user is redirected to role-specific dashboard. |

### UC2: Manage Insurance Plans
| Field | Description |
| :--- | :--- |
| **Actor** | Admin |
| **Description** | Create, deactivate (toggle), or delete plans. Deletion triggers the **Decommissioning Workflow**. |
| **Pre-condition** | Admin is logged in. |
| **Post-condition** | Plan table updated; existing policies for deleted plans are terminated. |

### UC3: Policy Purchase Lifecycle
| Field | Description |
| :--- | :--- |
| **Actor** | Customer |
| **Description** | Browse plans with benefits view → Confirm selection → Validate age → System generates policy and premium schedule. |
| **Pre-condition** | Customer is logged in and plan is active. |
| **Post-condition** | Policy status set to 'active'; premiums inserted into `premiums` table. |

### UC4: Premium Management
| Field | Description |
| :--- | :--- |
| **Actors** | Customer, Agent |
| **Description** | Customers pay due/overdue premiums. Agents can mark payments on behalf of their customers. System sweeps overdue entries on startup. |
| **Pre-condition** | Unpaid premium record exists. |
| **Post-condition** | Status updated to 'paid'; timestamped receipt available for PDF export. |

### UC5: Claims & Surrender Workflow
| Field | Description |
| :--- | :--- |
| **Actors** | Customer, Agent, Admin |
| **Description** | Customer files claim or surrender request. Agent reviews pending items. Admin performs final resolution (Approve/Reject). |
| **Pre-condition** | Active policy exists. |
| **Post-condition** | Request status updated; notification sent; financial record (simulated) finalized. |

### UC6: Plan Decommissioning & Refund
| Field | Description |
| :--- | :--- |
| **Actors** | Admin, Customer |
| **Description** | Admin removes a plan → System terminates all related policies → Customer files for a **Full Refund** claim. |
| **Pre-condition** | Admin deletes an active plan. |
| **Post-condition** | Customer notified; terminated policy allows a special refund-type claim. |

### UC7: Agent-Customer Assignment
| Field | Description |
| :--- | :--- |
| **Actors** | Agent, Admin |
| **Description** | Agents browse unassigned customers and submit requests. Admin reviews and assigns agents in the Management hub. |
| **Pre-condition** | Customer has no assigned agent. |
| **Post-condition** | `assigned_agent_id` updated in `customers` table. |

### UC8: Reporting & Auditing
| Field | Description |
| :--- | :--- |
| **Actors** | Agent, Admin |
| **Description** | Generation of PDF reports (User lists, Policy summaries, Claims). Admin monitors immutable **Audit Logs** for security. |
| **Pre-condition** | Audit log data exists in DB. |
| **Post-condition** | Actionable PDF report generated and downloaded locally. |

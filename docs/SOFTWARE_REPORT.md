# Insurance Management System (IMS) — Software Report

## 1. Executive Summary
The **Insurance Management System (IMS)** is a standalone desktop application developed using **Python** and **CustomTkinter**. It provides a comprehensive solution for managing life insurance lifecycle events, including policy acquisition, premium tracking, claim processing, and policy surrenders. The system is designed with a role-based access control (RBAC) model, supporting **Customers**, **Agents**, and **Administrators**.

## 2. Technical Stack
- **Programming Language**: Python 3.10+
- **GUI Framework**: CustomTkinter (Modernized Tkinter wrapper with dark/light mode support)
- **Database**: SQLite 3 (Serverless, embedded local database)
- **Security**: Bcrypt (Password hashing), Passkey-secured staff registration
- **Reporting**: ReportLab (Dynamic PDF generation)
- **Packaging**: PyInstaller (Compiled standalone `.exe` deployment)

## 3. System Architecture
The application follows a modular architecture:
- **Presentation Layer**: CustomTkinter windows and components (sidebar, tables, stat cards).
- **Business Logic Layer**: Dedicated modules for Policies, Claims, Premiums, and Surrenders.
- **Data Layer**: Centralized SQLite database interface with automated schema initialization and audit logging.

## 4. Key Features & Workflows

### 4.1 Customer Portal
- **Plan Discovery**: Browse various insurance plans (Term, Endowment, ULIP, etc.) with integrated benefits descriptions.
- **Policy Management**: Purchase plans and view active policy details, including total vs. paid installments.
- **Financial Actions**: Pay premiums online and track payment history.
- **Lifecycle Requests**: File full coverage claims or request policy surrenders with automated value calculation.
- **Notifications**: Real-time system alerts for policy updates and claim resolutions.

### 4.2 Agent Dashboard
- **Customer Relationship Management**: Manage assigned customers and export comprehensive performance reports.
- **Operations Management**: Approve or reject pending claims and track overdue premiums.
- **Growth Module**: Browse unassigned customers and submit assignment requests to the Administrator.

### 4.3 Administrative Control Panel
- **Approval Hub**: Consolidated interface to approve newly registered staff (Agents/Admins), claim requests, and agent assignments.
- **System Configuration**: Full control over the insurance plan catalogue (create, toggle, or retire plans).
- **Audit & Governance**: View a comprehensive, timestamped audit log of every significant action in the system.
- **Reporting Engine**: Export system-wide data (Users, Policies, Claims) to professional PDF reports.

## 5. Security & Integrity
- **Role Isolation**: Strict separation of dashboard views and database queries based on user role.
- **Staff Verification**: Registration as an Agent or Admin requires a unique **Secret Passkey**, ensuring only authorized personnel can create staff accounts.
- **Admin Approval**: New staff accounts remain inactive until manually reviewed and approved by an existing Administrator.
- **Auditability**: Every login, logout, and financial transaction is logged with a user ID and timestamp for forensic traceability.

## 6. Database Overview
The system utilizes 11 relational tables to maintain data integrity:
- `users`: Centralized authentication and role storage.
- `plans`: Master catalogue of insurance products.
- `policies`: Linkage between customers and their purchased plans.
- `premiums`: Granular tracking of payment schedules.
- `claims` & `surrenders`: Lifecycle event tracking.
- `agent_requests`: Formal workflow for customer assignments.
- `notifications`: User-specific alert storage.
- `audit_log`: System-wide event tracking.

## 7. Deployment Status
The application is **Production-Ready** for standalone Windows environments. 
- **Database**: Automatically initializes `ims_db.sqlite3` upon first run.
- **Dependencies**: Minimal footprint, bundled within the compiled executable.
- **UX**: High-performance, responsive UI with modern aesthetics and intuitive navigation.

---
**Prepared by**: Antigravity AI  
**Project**: University Software Engineering (SE) Project  
**Date**: April 2026

# 🛡️ Insurance Management System (IMS)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, standalone desktop **Insurance Management System (IMS)** developed in **Python** using modern **CustomTkinter**. The system offers an end-to-end digital lifecycle for life insurance—covering policy acquisition, premium installment tracking, claim processing, policy surrenders, audit logs, and PDF receipt generation.

Built with a strict **Role-Based Access Control (RBAC)** architecture, IMS delivers dedicated, tailored dashboards for **Customers**, **Insurance Agents**, and **System Administrators**.

---

## 📑 Table of Contents
- [Key Features](#-key-features)
  - [Customer Portal](#-customer-portal)
  - [Agent Dashboard](#-agent-dashboard)
  - [Admin Control Center](#-admin-control-center)
- [Tech Stack & Architecture](#-tech-stack--architecture)
- [Repository Structure](#-repository-structure)
- [Documentation Index](#-documentation-index)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
  - [Running the Application](#running-the-application)
  - [Default Credentials](#default-credentials)
- [Building Standalone Executable (.exe)](#-building-standalone-executable-exe)
- [License](#-license)

---

## 🌟 Key Features

### 👤 Customer Portal
- **Insurance Plan Discovery:** Explore categorized life insurance products (Term Life, Whole Life, Endowment, ULIP) with transparent age requirements and coverage details.
- **Policy Acquisition:** Instant enrollment with automatic premium installment schedule generation.
- **Financial Tracking:** Monitor paid installments, upcoming dues, and overdue alerts. Complete payments directly within the app.
- **Claims & Surrenders:** File coverage claims with reason tracking or submit policy surrenders with automated cash-value simulation.
- **PDF Export:** Generate and download official PDF payment receipts and policy statements.

### 💼 Agent Dashboard
- **CRM & Client Monitoring:** Manage assigned clients, inspect active policies, and track customer premium payment health.
- **Claim & Surrender Review:** Evaluate client claims and surrenders before escalation.
- **Client Acquisition Requests:** Request customer assignments through administrator approval channels.
- **Sales Analytics:** Review sold policies and generate performance reports.

### ⚙️ Admin Control Center
- **Staff Approval Pipeline:** Secure gatekeeping to verify and activate newly registered Agent and Administrator accounts.
- **Product Management:** Manage master insurance plans (create, update terms, activate/deactivate plans).
- **System Governance & Audit Log:** Timestamped immutable audit logs for all critical system activities (authentications, payments, approvals).
- **Global Reporting:** Export aggregated system reports across policies, claims, and financial collections.

---

## 💻 Tech Stack & Architecture

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core application logic and workflows |
| **User Interface** | CustomTkinter & Pillow | Modern, responsive desktop UI with custom styling |
| **Database** | SQLite 3 | Serverless, relational embedded storage with ACID compliance |
| **Security** | Bcrypt | Salted, one-way cryptographic password hashing |
| **Reporting** | ReportLab | Programmatic generation of branded PDF receipts and reports |
| **Packaging** | PyInstaller | Standalone single-file Windows executable packaging |

### Architectural Design
```
┌─────────────────────────────────────────────────────────┐
│               Presentation Layer (GUI)                  │
│       CustomTkinter Windows, Dialogs & Custom Widgets   │
├─────────────────────────────────────────────────────────┤
│               Business Logic Layer                      │
│   Auth & RBAC │ Policies │ Premiums │ Claims │ Surrenders│
├─────────────────────────────────────────────────────────┤
│               Data Access Layer (SQLite 3)              │
│    schema.sql │ connection.py │ Automated Migration     │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Repository Structure

```text
Insurance-Management-System/
├── docs/                        # Complete project documentation & diagrams
│   ├── CLASS_DIAGRAM.md         # Object-oriented domain class models
│   ├── DATABASE.md              # Database schema & entity relationships
│   ├── DATA_DICTIONARY.md       # Detailed field definitions & constraints
│   ├── DESIGN.md                # UI/UX design specifications & palette
│   ├── DFD.md                   # Data Flow Diagrams (Context, L1, L2)
│   ├── IMS_SRS.html             # Formal Software Requirements Specification
│   ├── OBJECT_DIAGRAM.md        # Runtime object interaction models
│   ├── SEQUENCE_DIAGRAM.md      # Workflow sequence interactions
│   ├── SOFTWARE_REPORT.md       # Comprehensive semester project report
│   ├── USE_CASES.md             # Role-based use case scenarios
│   └── USER_MANUAL.md           # End-user handbook with workflows
│
├── IMS/                         # Core Python Application Package
│   ├── assets/                  # Icons, graphics, and static media
│   ├── auth/                    # Login, registration, hashing, and seeding
│   ├── components/              # Reusable UI widgets (cards, sidebars, tables)
│   ├── db/                      # SQLite connection, queries, and schema.sql
│   ├── exports/                 # Generated PDF statements and receipts
│   ├── modules/                 # Domain logic (plans, claims, premiums, audit)
│   ├── utils/                   # Helpers, PDF generator, date formatters
│   ├── windows/                 # Customer, Agent, and Admin portal views
│   ├── config.py                # App configuration, theme tokens, and constants
│   └── main.py                  # Main executable entry point
│
├── .env.example                 # Environment configuration template
├── .gitignore                   # Excludes venvs, caches, builds, and live DBs
├── LICENSE                      # MIT Open Source License
├── README.md                    # Project overview and documentation index
└── requirements.txt             # Pinned project dependencies

```

---

## 📚 Documentation Index

All architectural design models, diagrams, and project reports have been organized in the [`docs/`](docs/) directory:

| Document | Description | Format |
| :--- | :--- | :---: |
| [Software Requirements Specification](docs/IMS_SRS.html) | Formal IEEE-style SRS documenting functional & non-functional requirements | HTML |
| [Software Project Report](docs/SOFTWARE_REPORT.md) | Comprehensive semester engineering report and project overview | Markdown |
| [User Manual](docs/USER_MANUAL.md) | Step-by-step walkthrough for Customers, Agents, and Administrators | Markdown |
| [Database Specification](docs/DATABASE.md) | Relational schema tables, keys, triggers, and initialization routines | Markdown |
| [Data Dictionary](docs/DATA_DICTIONARY.md) | Exhaustive data dictionary specifying field types, limits, and defaults | Markdown |
| [UI/UX Design Guide](docs/DESIGN.md) | Color palettes, layout geometry, typography, and theme tokens | Markdown |
| [Data Flow Diagrams](docs/DFD.md) | Context Level 0, Level 1, and Level 2 process decompositions | Markdown |
| [Class Diagram](docs/CLASS_DIAGRAM.md) | UML structural class diagram with attributes and methods | Markdown |
| [Sequence Diagram](docs/SEQUENCE_DIAGRAM.md) | Dynamic interaction flows for policy purchase, claims, and approvals | Markdown |
| [Object Diagram](docs/OBJECT_DIAGRAM.md) | Runtime snapshot of instantiated objects across typical sessions | Markdown |
| [Use Cases](docs/USE_CASES.md) | Actor use case descriptions and operational boundaries | Markdown |

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10** or higher installed on your system.
- **Git** installed on your system.
- Windows 10/11 recommended (for CustomTkinter Windows theme rendering).

### Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/<your-username>/Insurance-Management-System.git
   cd Insurance-Management-System
   ```

2. **Create and Activate a Virtual Environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```cmd
     python -m venv .venv
     .venv\Scripts\activate.bat
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create your local `.env` configuration file from the provided template:
   - **Windows (PowerShell):**
     ```powershell
     Copy-Item .env.example .env
     ```
   - **Linux / macOS / Bash:**
     ```bash
     cp .env.example .env
     ```
   Open `.env` and specify your custom administrative passkeys before launching the system.

### Running the Application

Launch the application directly via Python:
```bash
python IMS/main.py
```
> **Note:** On first startup, `main.py` automatically initializes the local SQLite database (`IMS/db/ims_db.sqlite3`) using `IMS/db/schema.sql`, seeds default insurance plans, and registers the initial Administrator account using the credentials defined in your `.env` file.

---

## 🔒 Security & Environment Credentials

In compliance with DevSecOps standards, hardcoded secrets and passkeys are stripped from the codebase. Administrative credentials and registration passkeys are strictly defined via environment variables:

| Role | Initial Identifier | Credential Source | Required Registration Key |
| :--- | :--- | :--- | :--- |
| **Admin (Initial Seed)** | Configured via `ADMIN_EMAIL` | Configured via `ADMIN_PASSWORD` in `.env` | N/A *(Seeded on first launch)* |
| **New Admin Registration** | User-defined at signup | User-defined at signup | Configured via `ADMIN_PASSKEY` in `.env` *(Requires approval)* |
| **New Agent Registration** | User-defined at signup | User-defined at signup | Configured via `AGENT_PASSKEY` in `.env` *(Requires approval)* |
| **Customer Registration** | User-defined at signup | User-defined at signup | None *(Instant access)* |

> [!IMPORTANT]
> Always keep your `.env` file private and never commit it to source control. A ready-to-use template is available in [`.env.example`](.env.example).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.


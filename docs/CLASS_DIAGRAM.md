# Class Diagram - Insurance Management System

A class diagram represents the static structure of a system by showing the classes, their attributes, operations, and the relationships among them. It models the system in terms of classes, where each class defines a set of objects having similar properties (attributes) and behaviors (methods). It also shows different types of relationships such as association, inheritance, aggregation, and dependency between classes.

Class diagrams are an important part of object-oriented design, as they provide a clear blueprint of how the system is organized. They help developers understand the structure of the system and serve as a foundation for coding and implementation.

## 1. Static Class Diagram

```mermaid
classDiagram
    %% Core User Hierarchy
    class User {
        +int user_id
        +string full_name
        +string email
        +string phone
        +string role
        +boolean is_active
        +login()
        +register()
        +logout()
    }

    class Customer {
        +date dob
        +string address
        +string nominee_name
        +string nominee_relation
        +int assigned_agent_id
        +viewPlans()
        +purchasePolicy()
        +payPremium()
        +fileClaim()
        +requestSurrender()
    }

    class Agent {
        +string license_no
        +string region
        +approveClaim()
        +viewAssignedCustomers()
        +requestCustomerAssignment()
    }

    class Admin {
        +string passkey
        +manageUsers()
        +managePlans()
        +approveStaff()
        +viewAuditLogs()
    }

    %% Insurance Products & Contracts
    class Plan {
        +int plan_id
        +string plan_name
        +string plan_type
        +string premium_frequency
        +float base_premium
        +float coverage_amount
        +int policy_term_years
        +calculatePremium()
    }

    class Policy {
        +int policy_id
        +int customer_id
        +int plan_id
        +int agent_id
        +date start_date
        +date end_date
        +string status
        +getMaturityValue()
    }

    %% Lifecycle & Transactional Elements
    class Premium {
        +int premium_id
        +int policy_id
        +float amount
        +date due_date
        +date paid_date
        +string status
        +processPayment()
    }

    class Claim {
        +int claim_id
        +int policy_id
        +int filed_by
        +string reason
        +float amount_requested
        +string status
        +date filed_at
        +resolve()
    }

    class Surrender {
        +int surrender_id
        +int policy_id
        +int requested_by
        +float surrender_value
        +string status
        +calculateValue()
    }

    %% Utility & Support
    class Notification {
        +int notif_id
        +int user_id
        +string message
        +boolean is_read
        +send()
    }

    class AuditLog {
        +int log_id
        +int user_id
        +string action
        +timestamp timestamp
        +logAction()
    }

    %% Service Managers
    class DatabaseManager {
        -connection db
        +connect()
        +execute(query)
        +fetch(query)
    }

    class AuthManager {
        +hashPassword(pwd)
        +verifyHash(pwd, hash)
        +createSession(user)
    }

    %% Relationships
    User <|-- Customer : Inheritance
    User <|-- Agent : Inheritance
    User <|-- Admin : Inheritance

    Customer "1" *-- "*" Policy : Owns
    Agent "1" -- "*" Customer : Manages
    Plan "1" -- "*" Policy : Defines
    Policy "1" *-- "*" Premium : Generates
    Policy "1" *-- "*" Claim : Tracks
    Policy "1" *-- "0..1" Surrender : Terminates
    
    User "1" -- "*" Notification : Receives
    User "1" -- "*" AuditLog : Performs
    
    DatabaseManager ..> User : Persists
    AuthManager ..> User : Secures
```

## 2. Class Definitions & Responsibilities

| Class Category | Primary Responsibility |
| :--- | :--- |
| **User Models** | Encapsulate user profile data and role-specific business logic (e.g., bidding for Agents, paying for Customers). |
| **Insurance Models** | Define the parameters of insurance products (`Plan`) and the legal contracts (`Policy`) binding users to them. |
| **Financial Models** | Manage the lifecycle of money movement, specifically `Premium` schedules and `Claim` payouts. |
| **Service Managers** | Stateless or singleton classes that handle system-wide utilities like database access and authentication security. |

## 3. Relationship Explanations

1. **Inheritance (Is-A)**: `Customer`, `Agent`, and `Admin` are specialized versions of the `User` class, inheriting common attributes like `email` and methods like `login()`.
2. **Composition (Has-A)**: A `Policy` is a composite object that owns its `Premium` schedule and associated `Claim` or `Surrender` records. If a policy is deleted, its financial history is removed.
3. **Association (Works-With)**: `Agents` manage multiple `Customers`. This is a loose association where a customer is assigned to an agent for service.
4. **Dependency (Uses)**: `DatabaseManager` and `AuthManager` provide infrastructure services used by the entity classes for persistence and security.
5. **Multiplicity**:
    *   **1 to ***: A single instance (e.g., Customer) can be associated with multiple instances (e.g., Policy).
    *   **1 to 0..1**: A policy may have zero or one surrender request.

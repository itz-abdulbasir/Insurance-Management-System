# Sequence Diagrams - Insurance Management System (IMS)

Following Rajib Mall's methodology, these diagrams represent specific scenarios through the system, emphasizing object lifelines, activation boxes, and synchronous/asynchronous messaging.

## 1. Scenario: Successful Policy Purchase (Main Success Scenario)

This scenario illustrates the process of a customer browsing, selecting, and successfully activating a new insurance policy.

```mermaid
sequenceDiagram
    participant cust as : Customer
    participant gui as : CustomerDashboard
    participant mgr as : PolicyManager
    participant db as : DatabaseManager

    activate cust
    cust->>gui: selectsPlan(plan_id)
    activate gui
    gui->>mgr: applyForPolicy(plan_id)
    activate mgr
    mgr->>db: createPolicy(cust_id, plan_id, 'active')
    activate db
    db-->>mgr: policy_id
    deactivate db

    mgr->>mgr: [status=success] generatePremiums(policy_id)
    activate mgr
    deactivate mgr

    mgr-->>gui: displaySuccess()
    deactivate mgr
    gui-->>cust: notifyActivation()
    deactivate gui
    deactivate cust
```

## 2. Scenario: Claim Submission and Approval

This scenario tracks the lifecycle of a claim from customer submission through agent adjudication and final resolution.

```mermaid
sequenceDiagram
    participant cust as : Customer
    participant gui as : CustomerDashboard
    participant clm as : ClaimManager
    participant db as : DatabaseManager
    participant agnt as : AgentDashboard

    activate cust
    cust->>gui: fileClaim(reason, amount)
    activate gui
    gui->>clm: submitClaim(policy_id, reason, amount)
    activate clm
    
    clm->>db: verifyPremiumsPaid(policy_id)
    activate db
    db-->>clm: true
    deactivate db

    clm->>db: insertClaim(policy_id, 'pending')
    activate db
    db-->>clm: claim_id
    deactivate db

    clm->>agnt: *[notify] notifyPendingClaim(claim_id)
    deactivate clm

    Note over agnt, db: After Agent Review
    agnt->>clm: resolveClaim(claim_id, 'approved')
    activate clm
    clm->>db: updateClaimStatus('approved')
    activate db
    clm->>db: updatePolicyStatus('claimed')
    db-->>clm: success
    deactivate db
    clm-->>agnt: displayResolution()
    clm-->>gui: notifyClaimResolved()
    deactivate clm
    gui-->>cust: displayClaimStatus()
    deactivate gui
    deactivate cust
```

## 3. Objects & Responsibilities

| Object : Class | Role | Responsibility |
| :--- | :--- | :--- |
| **: Customer** | Actor Instance | Initiates transactions and receives notifications. |
| **: CustomerDashboard** | Boundary | Provides the interface for plan selection and claim filing. |
| **: PolicyManager** | Controller | Handles business logic for policy creation and premium generation. |
| **: ClaimManager** | Controller | Validates claim eligibility and routes to adjudication. |
| **: DatabaseManager** | Entity | Persists state and performs CRUD operations on tables. |
| **: AgentDashboard** | Boundary | Interface for agents to review and approve/reject claims. |

## 4. Academic UML Rules Followed (Rajib Mall)

1.  **Object Representation**: All lifelines represent instances (objects), not classes. Names are formatted as `objectName : ClassName`.
2.  **Activation Boxes**: Thin rectangles (Focus of Control) indicate when an object is active. The **Customer** is active throughout the entire session.
3.  **Message Types**: 
    *   **Synchronous**: Solid lines with filled arrowheads (`->>`).
    *   **Asynchronous**: Used for notifications or parallel tasks (`->`).
    *   **Return**: Dashed lines used when control return is not obvious (`-->>`).
4.  **Guard Conditions**: Conditions like `[status=success]` are used for conditional logic.
5.  **Iteration**: The asterisk `*` indicates repeated messages (e.g., notifying all relevant agents).
6.  **Scenario Scope**: Each diagram focuses on a single successful execution path for clarity.

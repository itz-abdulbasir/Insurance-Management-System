# Insurance Management System (IMS) - User Manual

Welcome to the Insurance Management System (IMS)! This comprehensive guide will help you navigate the platform, depending on your role: **Customer**, **Agent**, or **Admin**.

## Table of Contents
1. [Getting Started (Registration & Login)](#getting-started)
2. [Customer Guide](#customer-guide)
3. [Agent Guide](#agent-guide)
4. [Admin Guide](#admin-guide)
5. [Troubleshooting & Support](#troubleshooting)

---

## 1. Getting Started <a name="getting-started"></a>

### Registration
1. Launch the IMS application.
2. Click on **Don't have an account? Register** at the bottom of the login screen.
3. Fill in your personal details (Name, Email, Password, Date of Birth).
4. Select your desired role: **Customer**, **Agent**, or **Admin**.
5. Click **Register**. 
*Note: Agent and Admin accounts require approval from a system administrator before they can log in.*

### Login
1. Enter your registered email address and password.
2. Click **Login**. The system will automatically route you to your respective dashboard based on your role.

---

## 2. Customer Guide <a name="customer-guide"></a>
The Customer Dashboard is your personal hub for managing your life insurance policies, making payments, and filing claims.

### 📋 Insurance Plans
- **Browse Plans:** View all available insurance plans (Term, Endowment, Whole Life, etc.).
- **View Benefits:** Click "⭐ View Benefits" to see detailed features, age requirements, and terms for a plan.
- **Purchase:** Click "Choose Plan" to instantly purchase a plan. *Note: You must meet the age requirements for the selected plan.*

### 📄 My Plans
- **View Your Policies:** See a list of all your active, claimed, or terminated policies.
- **Detailed View & Receipts:** Click on any individual plan to view your **Payment History** and **Download PDF Receipts**.

### 💰 Premium Payments
- **Pay Premiums:** See all your upcoming and overdue premium payments.
- **Mark Paid:** Click "Mark Paid" to clear a due premium. 
- **Export History:** Click the "📥 Export Payment History to PDF" to generate a record of your payments.

### 📝 File a Claim & My Claims
- **File Claim:** Select an active policy, enter the claim reason, and click submit. The amount will automatically populate based on your coverage.
- **My Claims:** Track the approval status of your submitted claims and download PDF claim receipts.

### 🔄 Surrender Plan
- If you no longer wish to continue a policy, you can request a surrender.
- Select the policy to see a simulated **Surrender Value**, enter a reason, and submit the request.

---

## 3. Agent Guide <a name="agent-guide"></a>
The Agent Dashboard allows you to manage your assigned customers and track your sales performance.

### 📊 Dashboard
- View a quick summary of your total customers, active policies, and total premium collections.

### 👥 My Customers
- View a list of all customers assigned to you.
- Monitor their policies and upcoming premium dues to help them stay on track.

### 📄 Sold Policies
- See a comprehensive list of all policies you have successfully sold, including the plan name, status, and installment progress.

### 🤝 Customer Requests
- If a new customer registers and wants to be assigned to you, you can view and approve/reject their assignment requests here.

---

## 4. Admin Guide <a name="admin-guide"></a>
The Admin Dashboard provides full control over the system's users, plans, and financial operations.

### 📊 System Overview
- View high-level metrics: Total Users, Total Policies, Pending Claims, and Total Revenue.

### ✅ Pending Approvals
- **New Users:** Approve or reject registration requests for new Agents and Admins.
- **Claims:** Review and resolve pending claim requests filed by customers.
- **Agent Requests:** Manage reassignment requests between agents and customers.

### 👥 User & Customer Management
- **User Management:** View all registered users. You can toggle their account status (Active/Inactive) if a user needs to be suspended.
- **Customer Management:** Assign specific agents to customers to ensure they receive proper support.

### 📋 Plan Management
- **Add New Plans:** Create new insurance products (Term, Pension, ULIP, etc.) by specifying coverage, premiums, and age limits.
- **Toggle/Remove:** Suspend or delete outdated insurance plans.

### 📄 Customer Plans (Global View)
- View every single policy in the system.
- Filter by status (Active, Claimed, Surrendered, Expired).
- Click on any policy to view its full payment history and generate an official **PDF Receipt**.

### 📜 Audit Log & PDF Reports
- **Audit Log:** Track every major action taken in the system (logins, approvals, payments) for security and compliance.
- **PDF Reports:** Generate bulk reports for all policies or all claims in the system with a single click.

---

## 5. Troubleshooting & Support <a name="troubleshooting"></a>

- **Cannot Login:** Ensure you are entering the correct email and password. If you registered as an Agent or Admin, you must wait for an existing Admin to approve your account.
- **PDFs Not Opening:** When you export a PDF, it is automatically saved to your `Downloads/IMS_Reports` folder. Ensure you have a PDF reader installed on your computer.
- **Application Crashing:** Ensure your Python virtual environment is active and all requirements are installed. 

*Thank you for choosing the Insurance Management System!*

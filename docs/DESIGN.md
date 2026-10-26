# IMS — Design System & Visual Source of Truth

> Extracted from **IMS SRS v1.0** §12 — UI/UX Design Guidelines  
> Stack: **Python 3.10+ · CustomTkinter ≥ 5.2 · SQLite 3**

---

## 1. Color Palette

| Token              | Hex       | CTk Usage                              |
|--------------------|-----------|----------------------------------------|
| Primary / Sidebar  | `#1B4F72` | Sidebar frame `bg`, heading labels     |
| Accent / Buttons   | `#2E86C1` | `CTkButton.fg_color`, active tab       |
| Success Green      | `#1E8449` | Approved badge, success messages       |
| Warning Orange     | `#E67E22` | Due premium badge                      |
| Danger Red         | `#C0392B` | Overdue badge, error labels            |
| App Background     | `#F0F3F4` | CTk window `bg` (light mode)           |
| Card Background    | `#FFFFFF` | `CTkFrame` bg for content panels       |

### Status Badge Colors

| Status       | Background    | Text Color |
|-------------|---------------|------------|
| Active       | `#D5F5E3`    | `#1E8449`  |
| Pending      | `#FEF9E7`    | `#E67E22`  |
| Claimed      | `#D6EAF8`    | `#2E86C1`  |
| Surrendered  | `#F9EBEA`    | `#C0392B`  |
| Overdue      | `#F9EBEA`    | `#C0392B`  |
| Paid         | `#D5F5E3`    | `#1E8449`  |
| Due          | `#FEF9E7`    | `#E67E22`  |
| Approved     | `#D5F5E3`    | `#1E8449`  |
| Rejected     | `#F9EBEA`    | `#C0392B`  |
| Expired      | `#EAECEE`    | `#7F8C8D`  |

---

## 2. Typography

| Element         | Font Family          | Size  | Weight   |
|----------------|----------------------|-------|----------|
| App Title       | System Default (CTk) | 24px  | Bold     |
| Section Heading | System Default (CTk) | 18px  | Bold     |
| Sub Heading     | System Default (CTk) | 15px  | SemiBold |
| Body Text       | System Default (CTk) | 14px  | Normal   |
| Table Header    | System Default (CTk) | 13px  | Bold     |
| Table Cell      | System Default (CTk) | 13px  | Normal   |
| Badge Text      | System Default (CTk) | 11px  | SemiBold |
| Button Text     | System Default (CTk) | 14px  | SemiBold |
| Input Label     | System Default (CTk) | 13px  | Normal   |
| Placeholder     | System Default (CTk) | 13px  | Italic   |

> **Note:** CustomTkinter uses system fonts by default. On Windows this resolves to Segoe UI which provides excellent readability.

---

## 3. Layout Rules

| Rule               | Specification                                          |
|--------------------|-------------------------------------------------------|
| Window Size        | `1200 × 700` minimum, resizable                       |
| Sidebar Width      | `200px` — fixed, contains nav buttons per role         |
| Content Area       | `CTkScrollableFrame` with cards or table views         |
| Top Bar            | App name + logged-in user name + Logout button         |
| Forms              | `CTkEntry` with placeholder text + label above field   |
| Status Badges      | `CTkLabel` with colored `fg_color` + rounded corners   |
| Navigation Depth   | All features reachable within **3 clicks** from dashboard |

### Window Hierarchy

```
LoginWindow (600×500)
  ├── Login Form
  └── "Register" link → RegisterWindow
        ├── Customer Registration Form
        └── Agent Registration Form

Dashboard Windows (1200×700 min)
  ├── Top Bar (full width, 50px tall)
  ├── Sidebar (200px wide)
  │     └── Navigation Buttons (role-specific)
  └── Content Area (fills remaining space)
        └── CTkScrollableFrame → cards / tables / forms
```

### Spacing & Padding

| Element          | Value  |
|-----------------|--------|
| Sidebar padding  | 16px   |
| Content padding  | 24px   |
| Card padding     | 16px   |
| Button padding   | 8px 16px |
| Table row height | 40px   |
| Section gap      | 20px   |
| Input field gap  | 12px   |

---

## 4. Component Specifications

### 4.1 Sidebar Navigation
- Background: `#1B4F72`
- Button style: flat, full-width, left-aligned text
- Active button: bg = `#2E86C1`, text = `#FFFFFF`
- Inactive button: bg = transparent, text = `#AED6F1`
- Hover: bg = `#21618C`
- Divider between sections: 1px line `#2874A6`

### 4.2 Top Bar
- Background: `#FFFFFF`
- Border bottom: 1px `#D5D8DC`
- Height: 50px
- App title: left-aligned, `#1B4F72`, bold 18px
- User info + Logout: right-aligned

### 4.3 Data Tables
- Header row: bg = `#EBF5FB`, text = `#1B4F72`, bold
- Alternating rows: `#FFFFFF` / `#FAFAFA`
- Hover row: `#EBF5FB`
- Cell padding: 10px 16px
- Border: 1px `#D5D8DC`

### 4.4 Cards (Dashboard Stats)
- Background: `#FFFFFF`
- Border: 1px `#D5D8DC`
- Border radius: 8px
- Shadow: subtle (simulated via border)
- Icon/emoji top, large number center, label bottom

### 4.5 Forms
- Label above each field (13px, `#5D6D7E`)
- `CTkEntry`: border = `#D5D8DC`, focus border = `#2E86C1`
- `CTkComboBox` for dropdowns
- Submit button: full accent color `#2E86C1`
- Error labels: inline red text (`#C0392B`), never popups

### 4.6 Buttons
| Type      | bg_color   | text_color | hover_color |
|-----------|-----------|------------|-------------|
| Primary   | `#2E86C1` | `#FFFFFF`  | `#2471A3`   |
| Success   | `#1E8449` | `#FFFFFF`  | `#196F3D`   |
| Danger    | `#C0392B` | `#FFFFFF`  | `#A93226`   |
| Secondary | `#D5D8DC` | `#2C3E50`  | `#BFC9CA`   |

---

## 5. Role-Specific Dashboard Tabs

### Customer Dashboard
| Tab                | Icon | Description                              |
|-------------------|------|------------------------------------------|
| Insurance Plans   | 📋   | Browse & purchase active plans           |
| My Plans          | 📄   | View own policies with status badges     |
| Premium Payments  | 💰   | View/pay due & overdue premiums          |
| File a Claim      | 📝   | Submit claim on active policy            |
| My Claims         | 📊   | View claim statuses                      |
| Surrender Plan    | 🔄   | Request surrender on active policy       |
| My Agent          | 👤   | View assigned agent details              |
| About Us          | ℹ️    | Company mission, contact, branch info    |

### Agent Dashboard
| Tab                   | Icon | Description                             |
|----------------------|------|-----------------------------------------|
| Dashboard            | 📊   | Stats cards: customers, policies, claims |
| My Customers         | 👥   | List of assigned customers + reports     |
| Claims Mgmt          | 📝   | Approve/reject pending claims            |
| Premium Tracker      | 💰   | Overdue premiums for assigned customers  |
| Customer Plans       | 📄   | All assigned policies with filters       |
| Find Customers       | 🔍   | Request unassigned customers             |

### Admin Dashboard
| Tab              | Icon | Description                              |
|-----------------|------|------------------------------------------|
| Dashboard       | 📊   | System-wide stats                        |
| Pending Approvals| ✅   | Consolidated approvals for Users, Claims, and Agent Requests |
| User Management | 👥   | View/activate/deactivate all users       |
| Customer Mgmt   | 🤝   | Assign agents to customers               |
| Agent Management| 🏢   | View agents and their customer counts    |
| Plan Management | 📋   | Add/edit/deactivate insurance plans      |
| Customer Plans  | 📄   | Full policy table with filters           |
| Audit Log       | 📜   | Full timestamped action log              |
| PDF Reports     | 📥   | Export system-wide reports               |

---

## 6. Login & Registration Window

### Login Window (600 × 500)
- Centered on screen
- App logo/title at top
- Fields: Email, Password, Role dropdown (Customer/Agent/Admin)
- "Login" button (primary)
- "New User? Register here" link below
- Error message: inline red label

### Registration Window (600 × 650)
- Tab selector: "Customer" | "Agent" | "Admin"
- **Customer form**: full name, email, phone, DOB, address, nominee name, nominee relation, password. (Automatically approved).
- **Agent form**: full name, email, phone, region, license number, agent passkey, password. (Requires admin approval).
- **Admin form**: full name, email, phone, admin passkey, password. (Requires admin approval).
- "Register" button + "Back to Login" link

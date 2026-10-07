# 🩸 Blood Bank Inventory & Expiry Management System

A web application for hospital blood banks to track inventory, manage expiry, and prevent double-booking of cross-matched units — built with Django and MySQL.

---

## 📋 Problem Statement

Hospital blood banks manage a resource that is both perishable and life-critical. This system was built to solve three specific bottlenecks:

1. **Different components expire at different speeds.** Whole Blood/RBC lasts ~35 days, Platelets only ~5 days, and Plasma (frozen) lasts much longer — a single fixed expiry rule doesn't work.
2. **Reserved stock isn't free stock.** A unit cross-matched to a patient must be locked so it can't be double-booked, without being deleted or miscounted.
3. **Running low matters as much as expiring.** A blood group silently dropping below a safe threshold is just as dangerous as a unit going bad unnoticed.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Role-based access** | Admin and Staff roles with different permissions, enforced on the backend (not just hidden UI) |
| **Auto expiry calculation** | Calculated on save from collection date + component shelf life — never manually entered |
| **Reservation locking** | Status flow: `Available → Reserved → Issued`, enforced server-side so a unit can never be double-booked |
| **Live dashboard** | Real-time counts, expiry alerts (units expiring within 3 days), and low-stock warnings per blood group + component |
| **Filterable inventory** | Search/filter by blood group, component type, and status |
| **Staff management** | Admins can create and manage staff accounts |

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Database:** MySQL
- **Frontend:** Django Templates + Bootstrap 5
- **Auth:** Django's built-in auth system, extended with a custom role field

---

## 📁 Project Structure

```
bloodbank_system/
├── accounts/        → staff users, roles, login/logout
├── inventory/       → blood units, reservations, issuing (core domain)
├── dashboard/       → live stats/alerts homepage
├── templates/       → all HTML templates
├── static/css/      → stylesheet
└── bloodbank_system/ → project settings & URL routing
```

---

## 🩺 Business Logic

**Shelf life by component:**
- Whole Blood / RBC → 35 days
- Platelets → 5 days
- Plasma (frozen) → 365 days

**Status lifecycle:**
```
AVAILABLE → (reserve) → RESERVED → (issue) → ISSUED
                ↑              │
                └── (release) ─┘
```

**Low-stock detection:** compares available unit count against a configurable minimum threshold, per blood group + component combination.

---

## 🚀 Setup & Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/jaswanthverse/blood.git
   cd blood
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate.bat
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL**
   ```sql
   CREATE DATABASE bloodbank_db;
   ```
   Then update the `DATABASES` section in `bloodbank_system/settings.py` with your MySQL username and password.

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create an admin account**
   ```bash
   python manage.py createsuperuser
   ```

7. **(Optional) Load demo data**
   ```bash
   python manage.py seed_data
   ```

8. **Run the server**
   ```bash
   python manage.py runserver
   ```

9. Visit **http://127.0.0.1:8000/**

---

## 👥 User Roles

- **Admin** — full access: add/delete units, manage staff accounts, all Staff permissions
- **Staff** — day-to-day operations: add units, reserve, issue, view dashboard

---

## 🔮 Possible Future Improvements

- Scheduled task to auto-flag expired units daily
- Email/SMS alerts for critical low-stock situations
- Multi-branch/hospital support
- Donor records and donation history tracking
- Exportable reports (PDF/Excel)

---

## 📄 License

This is an academic project built for learning purposes.

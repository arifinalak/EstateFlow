# EstateElite – Real Estate Web App

A full-featured real estate portal built with Flask, MySQL, HTML & CSS.

---

## 📁 File Structure

```
realestate/
├── app.py                  ← All routes & logic (one file)
├── schema.sql              ← Database setup + sample data
├── requirements.txt        ← Python packages
├── static/
│   └── css/style.css       ← All styling
└── templates/
    ├── base.html           ← Navbar, flash messages
    ├── index.html          ← Home page
    ├── login.html          ← Login form
    ├── register.html       ← Register form
    ├── properties.html     ← Search & browse listings
    ├── property_detail.html← Single property view
    ├── buyer_dashboard.html← Saved listings
    ├── agent_dashboard.html← Listings + leads summary
    ├── add_property.html   ← Add listing form
    ├── admin_dashboard.html← User & property management
    ├── investor_dashboard.html ← Portfolio tracker
    ├── calculator.html     ← Deal calculator
    └── leads.html          ← CRM lead tracker
```

---

## ⚙️ Setup Instructions

### 1. Install Python packages
```bash
pip install -r requirements.txt
```

### 2. Set up MySQL database
Open MySQL and run:
```bash
mysql -u root -p < schema.sql
```
Or paste the contents of `schema.sql` into phpMyAdmin / MySQL Workbench.

### 3. Configure DB connection
In `app.py`, update the `get_db()` function if needed:
```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",   # ← change this
        database="realestate"
    )
```

### 4. Run the app
```bash
python app.py
```
Visit: http://127.0.0.1:5000

---

## 👥 Roles & Demo Accounts

| Role     | Email               | Password     | Access                              |
|----------|---------------------|--------------|-------------------------------------|
| Admin    | admin@demo.com      | admin123     | All users, all properties           |
| Agent    | agent@demo.com      | agent123     | Add listings, manage CRM leads      |
| Buyer    | buyer@demo.com      | buyer123     | Search & save properties            |
| Investor | investor@demo.com   | investor123  | Portfolio tracker, deal calculator  |

---

## 🚀 Features

| Feature                  | Role      | Route              |
|--------------------------|-----------|--------------------|
| Browse & search listings | All       | /properties        |
| Save listings            | Buyer     | /buyer             |
| Add property             | Agent     | /add_property      |
| CRM lead tracker         | Agent     | /leads             |
| User & property mgmt     | Admin     | /admin             |
| Portfolio manager        | Investor  | /investor          |
| Deal calculator          | Investor  | /calculator        |

---

## ⚠️ Note for Production
- Passwords are stored as plain text (fine for demo/class).
- Use `werkzeug.security` (bcrypt) for real projects.

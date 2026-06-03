# Smart Car Dealership — Inventory & Sales Management

A MySQL-based database project with a Flask web interface for managing a car dealership. Built as part of the DBMS (21CSC205P) coursework at SRM Institute of Science and Technology.

---

## What This Does

- **Inventory Management** — Browse, search, filter (6 filters), and sort (5 options) 200+ cars with specs, pricing, and availability
- **User Accounts** — Separate admin and customer roles with login authentication
- **Purchase Flow** — Customers initiate purchases → Admin verifies → Sale is finalized
- **Wishlist & Test Drives** — Customers can save cars and book test drive slots
- **Reviews & Ratings** — Customers who've bought a car can leave 1–5 star reviews
- **Admin Features** — Edit/delete cars, customer management, CSV export, transaction verification
- **Audit Trail** — All admin actions are logged with timestamps
- **Dark/Light Mode** — Toggle between themes (persisted to localStorage)
- **Toast Notifications** — Slide-in toasts replace flash alerts for a cleaner UI
- **Modal Confirmations** — All destructive actions (verify/reject/delete) use Bootstrap modals

---

## Tech Stack

- **Database** — MySQL 8.0
- **Backend** — Flask 3.0, PyMySQL
- **Frontend** — HTML5, Bootstrap 5, Vanilla JS
- **Auth** — Werkzeug password hashing, Flask sessions
- **Styling** — Google Fonts (Inter + Poppins), CSS custom properties, dark mode support

---

## Project Structure

```
Project/
├── app.py              # Flask app entry point
├── config.py           # Database credentials and app settings
├── database.py        # MySQL connection helper
├── decorators.py      # @login_required and @admin_required
├── requirements.txt   # Python dependencies
├── routes/
│   ├── auth.py        # Login, register, logout, profile + password change
│   ├── cars.py       # Inventory browsing, search, filters, sort, API
│   ├── customer.py   # Wishlist, test drives, purchases, reviews
│   └── admin.py       # Verification, car management, customers, CSV export
├── static/
│   ├── css/style.css  # Custom styles (dark mode, toasts, skeleton, animations)
│   ├── js/main.js     # Dark mode, toasts, modals, skeletons, count-up
│   └── images/         # Car images (85+ vehicle photos)
└── templates/
    ├── base.html       # Navbar (user avatar, dark mode toggle, dropdown)
    ├── login.html
    ├── register.html   # Password strength meter
    ├── index.html      # Hero banner, sticky filter bar, sort dropdown, pagination
    ├── car_detail.html # Specs grid, buy modal, test drive, wishlist, reviews
    ├── dashboard.html  # 4-tab dashboard with stat cards, empty states
    ├── admin.html      # Sidebar nav, stats, 5 tabs (txn/sales/inventory/customers/logs)
    ├── admin_edit_car.html
    ├── admin_customers.html
    └── profile.html    # Edit name, change password with strength meter
```

---

## Getting Started

### 1. Prerequisites

- Python 3.10 or later
- MySQL 8.0 (running locally)
- Database `car_dealership_real` already created and populated

### 2. Install Dependencies

```bash
cd "Project - Copy"
pip install -r requirements.txt
```

### 3. Update Credentials

If your MySQL credentials differ from the defaults, edit `config.py`:

```python
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "car_dealership_real"
```

### 4. Run the App

```bash
python app.py
```

Open your browser and go to: **http://localhost:5000**

---

## Default Login Credentials

| Role     | Username        | Password      |
|----------|----------------|---------------|
| Admin    | Aadith_admin   | adminPass123  |
| Customer | rahul_customer | custPass789   |
| Customer | priya_v        | priyaPass321  |

---

## Features Added (v2)

### Appearance
- 🎨 Premium color theme with CSS custom properties (blue/navy/gold)
- 🌙 Dark/Light mode toggle (persisted via `localStorage`)
- 📝 Google Fonts: Inter (body) + Poppins (headings)
- 🚗 Hero section on inventory page with live stats
- ✨ Skeleton loaders while content loads
- 🍞 Slide-in toast notifications (top-right, auto-dismiss)
- 📱 Upgraded navbar with user avatar, dropdown, dark mode button
- 📋 Enhanced footer with quick links, contact info, social icons
- 🎬 Card hover animations + scroll-to-top button
- 🔢 Count-up animations on stat numbers
- 🖼️ Car card hover zoom + "Quick View" overlay

### Functionality
- ↕️ Sort by: Price (Low→High, High→Low), Year (Newest, Oldest), Mileage (Lowest)
- 🔢 Numbered pagination pages with jump-to links
- 🗄️ Admin: Edit any car (all fields)
- 🗄️ Admin: Delete any car
- 🗄️ Admin: Customer management page (purchases + total spend per customer)
- 🗄️ Admin: CSV export of all sales
- 🗄️ Admin: Inventory management tab in sidebar
- 👤 Profile page: update name + change password
- 🔐 Password strength meter on register and profile pages
- ⭐ Star-rating review system on car detail pages
- ❤️ AJAX wishlist toggle on car detail page (no page reload)
- 🚫 Modal confirmations for all destructive actions

---

## Database Views

Three views are included in the schema:

| View | Purpose |
|------|---------|
| `sales_dashboard` | Profit analysis — sale price vs cost price |
| `customer_activity` | Per-customer transaction and wishlist counts |
| `maintenance_status` | Cars currently under service |

---

## Authors

- Aadith Geeth Mohan — RA2411026010393
- Ujjwal Pratap Singh — RA2411026010379

Under the guidance of **Dr. Sakthitharan**, Department of Computer Science Engineering, SRMIST.

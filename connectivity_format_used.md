# Database Connectivity Format Analysis

**Project:** Car Dealership Web Application (Flask + MySQL)
**File Location:** `C:\Users\AadithGeethMohan\OneDrive\Desktop\DBMS PROJECT SEM-4 TRACK\Project`

---

## Overview

Database connectivity with the front end is the process of sending user input from a front-end application to a database, processing it, and displaying the result back to the user.

This document maps the standard 15-step database connectivity flow to the actual implementation in this project.

---

## Step-by-Step Mapping

| Step | Description | Implementation in Project |
|------|-------------|--------------------------|
| 1 | User enters data in the front-end form | HTML forms in `templates/*.html` submit data to Flask routes |
| 2 | Data is sent to the server-side script | Flask `request.form` captures input (e.g., `customer.py:72`) |
| 3 | Server establishes a connection to the database | `database.py:9-17` — `get_db()` uses `pymysql.connect` |
| 4 | Specify the Database Driver | `pymysql` — Python MySQL connector driver |
| 5 | Provide Database Connection Details | `config.py:6-10` — host, port, user, password, database name |
| 6 | Establish Connection to the Database | `pymysql.connect(...)` returns the connection object |
| 7 | Select the Database | `database=Config.DB_NAME` specified in the connection string |
| 8 | Create a Statement / Cursor / Query Object | `with db.cursor() as cursor:` — used in every route |
| 9 | Select the Required Table | SQL queries target `cars`, `wishlist`, `test_drive_schedules`, `transactions`, etc. |
| 10 | Execute SQL Query | `cursor.execute(sql, params)` with parameterized queries |
| 11 | Process the Result | `cursor.fetchall()` / `cursor.fetchone()` retrieves records |
| 12 | Commit or Rollback Transaction | `autocommit=True` in `database.py:16` — auto-commits every query |
| 13 | Close the Connection | `close_db()` in `database.py:21-25`, called via Flask's `@teardown_appcontext` |
| 14 | Result is returned to the server | Routes return `render_template()`, `redirect()`, `flash()`, or `jsonify()` |
| 15 | Output is displayed on the front end | Templates (`templates/*.html`) render data using Jinja2 templating |

---

## Key Implementation Files

| File | Role |
|------|------|
| `database.py` | Manages DB connection via Flask `g` context and `get_db()` / `close_db()` |
| `config.py` | Stores all configuration (DB host, port, user, password, DB name, secret key) |
| `app.py` | Flask app setup; registers blueprints; connects `close_db` to teardown |
| `routes/customer.py` | Customer-facing routes: wishlist, test drives, purchases |
| `routes/cars.py` | Car browsing, search, filtering, and detail pages |
| `routes/auth.py` | Authentication routes |
| `routes/admin.py` | Admin management routes |
| `templates/*.html` | Front-end templates using Jinja2 |

---

## How the Flow Works in This Project

1. **User** fills out a form on the front end (e.g., book a test drive)
2. Form **POSTs** to a Flask route (e.g., `/customer/test-drive/book`)
3. The route calls **`get_db()`** from `database.py`
4. `get_db()` creates a `pymysql` connection using credentials from `config.py`
5. The connection is stored in Flask's `g` object (request context)
6. A **cursor** is created via `with db.cursor() as cursor:`
7. An SQL query is **executed** with `cursor.execute(sql, params)`
8. Results are **fetched** with `cursor.fetchall()` or `cursor.fetchone()`
9. Since `autocommit=True`, the transaction is automatically **committed**
10. After the request, Flask's `@teardown_appcontext` calls **`close_db()`**
11. The route **returns** data to the server (via `render_template`, `redirect`, or `flash`)
12. The **front end** displays the result (via Jinja2 templates)

---

## Comparison with Reference Format

The reference DBMS lab example (single-file, inline connection) demonstrates the same flow but with:

- A single global connection object (not request-scoped)
- Direct string interpolation in SQL queries (SQL injection risk)
- No use of context managers for cursor cleanup
- No separation of configuration

This project's implementation is a production-grade version of the same concept, featuring:

| Feature | Reference Example | This Project |
|---------|-------------------|--------------|
| Connection scope | Global (single connection) | Request-scoped (via Flask `g`) |
| SQL parameterization | String interpolation | Parameterized queries (safe) |
| Resource cleanup | Manual | Context managers + teardown |
| Configuration | Hardcoded in file | Separate `config.py` |
| Modular routing | Single file | Blueprints for each module |
| Session management | None | Flask-Session |
| Authentication | None | `@login_required` decorator |

---

## Example Query Execution Pattern

```python
# Step 3-8: Get connection and create cursor
db = get_db()
with db.cursor() as cursor:
    # Step 9-10: Select table and execute query
    cursor.execute(
        "INSERT INTO wishlist (user_id, vin) VALUES (%s, %s)",
        (user_id, vin)
    )
# Step 11-12: Results processed, auto-commit (autocommit=True)
# Step 13: Close connection automatically via close_db()
# Step 14-15: Return response and display to user
flash("Car added to your wishlist!", "success")
return redirect(url_for("customer.dashboard"))
```

---

## Conclusion

This project **fully follows** the standard 15-step database connectivity format. It maps cleanly to every step, from front-end form submission through connection establishment, query execution, result processing, and final display. The implementation is a well-structured, secure, and production-appropriate version of the reference DBMS lab format.

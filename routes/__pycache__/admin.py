from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, Response
from database import get_db
from decorators import admin_required, login_required
import csv
import io

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def panel():
    tab = request.args.get("tab", "transactions")
    db = get_db()
    with db.cursor() as cursor:
        # Pending transactions (not yet verified)
        cursor.execute("""
            SELECT t.transaction_id, t.amount, t.payment_method, t.transaction_status,
                   t.transaction_date, c.vin, c.make, c.model,
                   u.user_id, u.username, u.fname, u.lname
            FROM transactions t
            JOIN cars c ON t.vin = c.vin
            JOIN users u ON t.user_id = u.user_id
            WHERE t.transaction_status IN ('Processing', 'Success')
            ORDER BY t.transaction_date DESC
        """)
        transactions = cursor.fetchall()

        # Recent sales
        cursor.execute("""
            SELECT s.sale_id, s.transaction_id, s.sale_date,
                   sd.user_id, sd.vin, sd.final_sale_price,
                   c.make, c.model, u.fname, u.lname
            FROM sales s
            JOIN sale_details sd ON s.transaction_id = sd.transaction_id
            JOIN cars c ON sd.vin = c.vin
            JOIN users u ON sd.user_id = u.user_id
            ORDER BY s.sale_date DESC
            LIMIT 20
        """)
        sales = cursor.fetchall()

        # Admin logs
        cursor.execute("""
            SELECT al.log_id, al.action_performed, al.action_date,
                   u.username
            FROM admin_logs al
            JOIN users u ON al.admin_id = u.user_id
            ORDER BY al.action_date DESC
            LIMIT 20
        """)
        logs = cursor.fetchall()

        # Quick stats
        cursor.execute("SELECT COUNT(*) as total FROM cars")
        total_cars = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) as total FROM cars WHERE status = 'Available'")
        available = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'customer'")
        total_customers = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) as total FROM transactions")
        total_transactions = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) as total FROM cars WHERE status = 'Sold'")
        total_sold = cursor.fetchone()["total"]
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total_revenue FROM transactions WHERE transaction_status = 'Success'")
        total_revenue = cursor.fetchone()["total_revenue"]

    # Extra data per tab
    inventory_cars = []
    if tab == "inventory":
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT c.vin, c.make, c.model, c.year, c.selling_price, c.status, c.image_path,
                       cs.fuel_type, cs.transmission, cs.mileage, cs.color
                FROM cars c
                LEFT JOIN car_specifications cs ON c.vin = cs.vin
                ORDER BY c.vin
            """)
            inventory_cars = cursor.fetchall()

    return render_template(
        "admin.html",
        transactions=transactions,
        sales=sales,
        logs=logs,
        total_cars=total_cars,
        available=available,
        total_customers=total_customers,
        total_transactions=total_transactions,
        total_sold=total_sold,
        total_revenue=total_revenue,
        tab=tab,
        inventory_cars=inventory_cars,
    )


@bp.route("/verify/<transaction_id>", methods=["POST"])
@admin_required
def verify_transaction(transaction_id):
    action = request.form.get("action", "").strip()
    admin_id = session["user_id"]

    if action not in ("verify", "reject"):
        flash("Invalid action.", "danger")
        return redirect(url_for("admin.panel"))

    db = get_db()
    with db.cursor() as cursor:
        if action == "verify":
            cursor.execute("""
                UPDATE transactions SET transaction_status = 'Success' WHERE transaction_id = %s
            """, (transaction_id,))

            cursor.execute("""
                INSERT INTO sales (transaction_id) VALUES (%s)
            """, (transaction_id,))

            cursor.execute("""
                SELECT user_id, vin, amount FROM transactions WHERE transaction_id = %s
            """, (transaction_id,))
            txn = cursor.fetchone()

            cursor.execute("""
                INSERT INTO sale_details (transaction_id, user_id, vin, final_sale_price)
                VALUES (%s, %s, %s, %s)
            """, (transaction_id, txn["user_id"], txn["vin"], txn["amount"]))

            cursor.execute("UPDATE cars SET status = 'Sold' WHERE vin = %s", (txn["vin"],))

            cursor.execute("""
                INSERT INTO transaction_verification (verified_by_admin_id, transaction_id, verification_status)
                VALUES (%s, %s, 'Verified')
            """, (admin_id, transaction_id))

            cursor.execute("""
                INSERT INTO admin_logs (admin_id, action_performed)
                VALUES (%s, %s)
            """, (admin_id, f"Verified transaction {transaction_id}"))

            flash(f"Transaction {transaction_id} verified successfully!", "success")

        else:  # reject
            cursor.execute("""
                UPDATE transactions SET transaction_status = 'Failed' WHERE transaction_id = %s
            """, (transaction_id,))
            cursor.execute("""
                INSERT INTO admin_logs (admin_id, action_performed)
                VALUES (%s, %s)
            """, (admin_id, f"Rejected transaction {transaction_id}"))
            flash(f"Transaction {transaction_id} rejected.", "warning")

    return redirect(url_for("admin.panel"))


@bp.route("/add-car", methods=["POST"])
@admin_required
def add_car():
    vin = request.form.get("vin", "").strip()
    make = request.form.get("make", "").strip()
    model = request.form.get("model", "").strip()
    year = request.form.get("year", "").strip()
    selling_price = request.form.get("selling_price", "").strip()
    cost_price = request.form.get("cost_price", "").strip()
    status = request.form.get("status", "Available").strip()
    fuel_type = request.form.get("fuel_type", "").strip()
    transmission = request.form.get("transmission", "").strip()
    mileage = request.form.get("mileage", "0").strip()
    color = request.form.get("color", "").strip()
    admin_id = session["user_id"]

    if not all([vin, make, model, year, selling_price, cost_price]):
        flash("Please fill in all required fields.", "danger")
        return redirect(url_for("admin.panel"))

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO cars (vin, make, model, year, selling_price, cost_price, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE make=%s, model=%s, year=%s, selling_price=%s, cost_price=%s, status=%s
        """, (vin, make, model, year, selling_price, cost_price, status,
              make, model, year, selling_price, cost_price, status))

        if fuel_type or transmission:
            cursor.execute("""
                INSERT INTO car_specifications (vin, fuel_type, transmission, mileage, color)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE fuel_type=%s, transmission=%s, mileage=%s, color=%s
            """, (vin, fuel_type, transmission, mileage, color,
                  fuel_type, transmission, mileage, color))

        cursor.execute("""
            INSERT INTO admin_logs (admin_id, action_performed)
            VALUES (%s, %s)
        """, (admin_id, f"Added/Updated car: {make} {model} ({vin})"))

    flash(f"Car {make} {model} added/updated successfully!", "success")
    return redirect(url_for("admin.panel", tab="inventory"))


@bp.route("/edit-car/<vin>", methods=["GET", "POST"])
@admin_required
def edit_car(vin):
    db = get_db()

    if request.method == "POST":
        make         = request.form.get("make", "").strip()
        model        = request.form.get("model", "").strip()
        year         = request.form.get("year", "").strip()
        selling_price = request.form.get("selling_price", "").strip()
        cost_price   = request.form.get("cost_price", "").strip()
        status       = request.form.get("status", "Available").strip()
        fuel_type    = request.form.get("fuel_type", "").strip()
        transmission = request.form.get("transmission", "").strip()
        mileage      = request.form.get("mileage", "0").strip()
        color        = request.form.get("color", "").strip()
        admin_id     = session["user_id"]

        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE cars SET make=%s, model=%s, year=%s, selling_price=%s,
                               cost_price=%s, status=%s
                WHERE vin=%s
            """, (make, model, year, selling_price, cost_price, status, vin))

            cursor.execute("""
                INSERT INTO car_specifications (vin, fuel_type, transmission, mileage, color)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE fuel_type=%s, transmission=%s, mileage=%s, color=%s
            """, (vin, fuel_type, transmission, mileage, color,
                  fuel_type, transmission, mileage, color))

            cursor.execute("""
                INSERT INTO admin_logs (admin_id, action_performed)
                VALUES (%s, %s)
            """, (admin_id, f"Updated car: {make} {model} ({vin})"))

        flash(f"Car {make} {model} updated successfully!", "success")
        return redirect(url_for("admin.panel", tab="inventory"))

    # GET: fetch car data
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT c.vin, c.make, c.model, c.year, c.selling_price, c.cost_price, c.status, c.image_path,
                   cs.fuel_type, cs.transmission, cs.mileage, cs.color
            FROM cars c
            LEFT JOIN car_specifications cs ON c.vin = cs.vin
            WHERE c.vin = %s
        """, (vin,))
        car = cursor.fetchone()

    if not car:
        flash("Car not found.", "danger")
        return redirect(url_for("admin.panel", tab="inventory"))

    return render_template("admin_edit_car.html", car=car)


@bp.route("/delete-car/<vin>", methods=["POST"])
@admin_required
def delete_car(vin):
    admin_id = session["user_id"]
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT make, model FROM cars WHERE vin = %s", (vin,))
        car = cursor.fetchone()
        if car:
            cursor.execute("DELETE FROM cars WHERE vin = %s", (vin,))
            cursor.execute("""
                INSERT INTO admin_logs (admin_id, action_performed)
                VALUES (%s, %s)
            """, (admin_id, f"Deleted car: {car['make']} {car['model']} ({vin})"))
            flash(f"Car {car['make']} {car['model']} deleted.", "warning")
        else:
            flash("Car not found.", "danger")
    return redirect(url_for("admin.panel", tab="inventory"))


@bp.route("/customers")
@admin_required
def customers():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT u.user_id, u.username, u.fname, u.lname, u.created_at,
                   COUNT(DISTINCT sd.vin) as purchases,
                   COALESCE(SUM(sd.final_sale_price), 0) as total_spent
            FROM users u
            LEFT JOIN sale_details sd ON sd.user_id = u.user_id
            WHERE u.role = 'customer'
            GROUP BY u.user_id
            ORDER BY total_spent DESC
        """)
        customers = cursor.fetchall()
    return render_template("admin_customers.html", customers=customers)


@bp.route("/logs")
@admin_required
def view_logs():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT al.log_id, al.action_performed, al.action_date, u.username
            FROM admin_logs al
            JOIN users u ON al.admin_id = u.user_id
            ORDER BY al.action_date DESC
        """)
        logs = cursor.fetchall()
    return jsonify([{
        "log_id": l["log_id"],
        "username": l["username"],
        "action": l["action_performed"],
        "date": l["action_date"].strftime("%Y-%m-%d %H:%M") if l["action_date"] else ""
    } for l in logs])


@bp.route("/export/csv")
@admin_required
def export_csv():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT s.sale_id, s.sale_date, s.transaction_id,
                   sd.vin, sd.final_sale_price,
                   c.make, c.model, c.year,
                   u.username, u.fname, u.lname,
                   t.payment_method, t.transaction_status
            FROM sales s
            JOIN sale_details sd ON s.transaction_id = sd.transaction_id
            JOIN cars c ON sd.vin = c.vin
            JOIN users u ON sd.user_id = u.user_id
            JOIN transactions t ON s.transaction_id = t.transaction_id
            ORDER BY s.sale_date DESC
        """)
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Sale ID", "Date", "TXN ID", "VIN", "Make", "Model", "Year",
                     "Customer", "Payment", "Status", "Sale Price"])
    for r in rows:
        writer.writerow([
            r["sale_id"], r["sale_date"], r["transaction_id"], r["vin"],
            r["make"], r["model"], r["year"],
            f"{r['fname']} {r['lname']}",
            r["payment_method"], r["transaction_status"],
            f"{r['final_sale_price']:.2f}"
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sales_export.csv"}
    )
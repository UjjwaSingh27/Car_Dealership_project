from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from database import get_db
from decorators import login_required
import pymysql
from pymysql.err import IntegrityError

bp = Blueprint("customer", __name__, url_prefix="/customer")


@bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]

    db = get_db()
    with db.cursor() as cursor:
        # Wishlist
        cursor.execute("""
            SELECT c.vin, c.make, c.model, c.year, c.selling_price, c.status, c.image_path,
                   we.added_at
            FROM wishlist_entries we
            JOIN cars c ON we.vin = c.vin
            WHERE we.user_id = %s
            ORDER BY we.added_at DESC
        """, (user_id,))
        wishlist = cursor.fetchall()

        # Test drive schedules
        cursor.execute("""
            SELECT tds.drive_id, tds.scheduled_date, tds.status,
                   c.vin, c.make, c.model, c.year, c.image_path
            FROM test_drive_schedules tds
            JOIN cars c ON tds.vin = c.vin
            WHERE tds.user_id = %s
            ORDER BY tds.scheduled_date DESC
        """, (user_id,))
        test_drives = cursor.fetchall()

        # Past transactions
        cursor.execute("""
            SELECT t.transaction_id, t.amount, t.payment_method, t.transaction_status,
                   t.transaction_date, c.vin, c.make, c.model
            FROM transactions t
            JOIN cars c ON t.vin = c.vin
            WHERE t.user_id = %s
            ORDER BY t.transaction_date DESC
        """, (user_id,))
        transactions = cursor.fetchall()

        # Previously bought cars (from sale_details where transaction was successful)
        cursor.execute("""
            SELECT sd.final_sale_price, sd.vin, c.make, c.model, c.year, c.image_path,
                   s.sale_date
            FROM sale_details sd
            JOIN sales s ON sd.transaction_id = s.transaction_id
            JOIN cars c ON sd.vin = c.vin
            WHERE sd.user_id = %s
            ORDER BY s.sale_date DESC
        """, (user_id,))
        purchased = cursor.fetchall()

        # Total spend
        cursor.execute("""
            SELECT SUM(final_sale_price) as total_spent
            FROM sale_details WHERE user_id = %s
        """, (user_id,))
        total_spent = cursor.fetchone()["total_spent"] or 0

    return render_template(
        "dashboard.html",
        wishlist=wishlist,
        test_drives=test_drives,
        transactions=transactions,
        purchased=purchased,
        total_spent=total_spent,
    )


@bp.route("/wishlist/add", methods=["POST"])
@login_required
def add_to_wishlist():
    vin = request.form.get("vin", "").strip()
    user_id = session["user_id"]

    if not vin:
        flash("Invalid car selection.", "danger")
        return redirect(url_for("cars.index"))

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO wishlist (user_id, vin) VALUES (%s, %s)", (user_id, vin))
            cursor.execute(
                "INSERT INTO wishlist_entries (user_id, vin) VALUES (%s, %s)",
                (user_id, vin)
            )
        flash("Car added to your wishlist!", "success")
    except IntegrityError:
        flash("Car already in your wishlist.", "info")

    return redirect(request.referrer or url_for("cars.index"))


@bp.route("/wishlist/remove", methods=["POST"])
@login_required
def remove_from_wishlist():
    vin = request.form.get("vin", "").strip()
    user_id = session["user_id"]

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND vin = %s", (user_id, vin))
        cursor.execute("DELETE FROM wishlist_entries WHERE user_id = %s AND vin = %s", (user_id, vin))
    flash("Car removed from wishlist.", "info")
    return redirect(url_for("customer.dashboard"))


@bp.route("/wishlist/toggle", methods=["POST"])
@login_required
def ajax_toggle_wishlist():
    vin = request.form.get("vin", "").strip()
    user_id = session["user_id"]

    if not vin:
        return jsonify({"message": "Invalid car.", "type": "danger", "in_wishlist": False})

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT 1 FROM wishlist WHERE user_id = %s AND vin = %s", (user_id, vin))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND vin = %s", (user_id, vin))
            cursor.execute("DELETE FROM wishlist_entries WHERE user_id = %s AND vin = %s", (user_id, vin))
            return jsonify({
                "message": "Removed from wishlist.",
                "type": "info",
                "in_wishlist": False
            })
        else:
            try:
                cursor.execute("INSERT INTO wishlist (user_id, vin) VALUES (%s, %s)", (user_id, vin))
                cursor.execute(
                    "INSERT INTO wishlist_entries (user_id, vin) VALUES (%s, %s)",
                    (user_id, vin)
                )
                return jsonify({
                    "message": "Added to wishlist!",
                    "type": "success",
                    "in_wishlist": True
                })
            except IntegrityError:
                # Already in wishlist — just confirm it
                return jsonify({
                    "message": "Already in your wishlist!",
                    "type": "info",
                    "in_wishlist": True
                })


@bp.route("/test-drive/book", methods=["POST"])
@login_required
def book_test_drive():
    vin = request.form.get("vin", "").strip()
    scheduled_date = request.form.get("scheduled_date", "").strip()
    user_id = session["user_id"]

    if not vin or not scheduled_date:
        flash("Please provide all required details.", "danger")
        return redirect(request.referrer or url_for("cars.index"))

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO test_drive_schedules (user_id, vin, scheduled_date, status)
            VALUES (%s, %s, %s, 'Pending')
        """, (user_id, vin, scheduled_date))
    flash("Test drive booked successfully!", "success")
    return redirect(request.referrer or url_for("customer.dashboard"))


@bp.route("/test-drive/cancel", methods=["POST"])
@login_required
def cancel_test_drive():
    drive_id = request.form.get("drive_id", "").strip()
    user_id = session["user_id"]

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE test_drive_schedules SET status = 'Cancelled' WHERE drive_id = %s AND user_id = %s",
            (drive_id, user_id)
        )
    flash("Test drive cancelled.", "info")
    return redirect(url_for("customer.dashboard"))


@bp.route("/buy/<vin>", methods=["POST"])
@login_required
def buy_car(vin):
    payment_method = request.form.get("payment_method", "").strip()
    user_id = session["user_id"]

    if not payment_method:
        flash("Please select a payment method.", "danger")
        return redirect(url_for("cars.detail", vin=vin))

    db = get_db()
    with db.cursor() as cursor:
        # Check car is available
        cursor.execute("SELECT selling_price, status FROM cars WHERE vin = %s", (vin,))
        car = cursor.fetchone()
        if not car:
            flash("Car not found.", "danger")
            return redirect(url_for("cars.index"))
        if car["status"] != "Available":
            flash("This car is no longer available.", "warning")
            return redirect(url_for("cars.index"))

        # Create transaction
        import uuid
        txn_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO transactions (transaction_id, user_id, vin, payment_method, amount, transaction_status)
            VALUES (%s, %s, %s, %s, %s, 'Processing')
        """, (txn_id, user_id, vin, payment_method, car["selling_price"]))

    flash(f"Transaction {txn_id} initiated! Awaiting admin verification.", "success")
    return redirect(url_for("customer.dashboard"))


@bp.route("/review/<vin>", methods=["POST"])
@login_required
def submit_review(vin):
    user_id = session["user_id"]
    rating = request.form.get("rating", "5").strip()
    comment = request.form.get("comment", "").strip()

    if not comment:
        flash("Please write a review.", "danger")
        return redirect(url_for("cars.detail", vin=vin))

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO reviews (user_id, vin, rating, comment)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE rating = VALUES(rating), comment = VALUES(comment)
            """, (user_id, vin, int(rating), comment))
        flash("Review submitted successfully!", "success")
    except pymysql.err.ProgrammingError:
        flash("Reviews feature unavailable — please create the reviews table in the database.", "danger")

    return redirect(url_for("cars.detail", vin=vin))
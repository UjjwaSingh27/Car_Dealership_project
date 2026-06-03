from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from decorators import login_required
import uuid

bp = Blueprint("auth", __name__, url_prefix="/")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("login.html")

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, username, password, fname, lname, role FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["fname"] = user["fname"]
            session["lname"] = user["lname"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['fname']}!", "success")
            return redirect(url_for("cars.index"))
        else:
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        fname = request.form.get("fname", "").strip()
        lname = request.form.get("lname", "").strip()

        if not username or not password or not fname or not lname:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash("Username already exists.", "danger")
                return render_template("register.html")

            hashed_pw = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password, fname, lname, role) VALUES (%s, %s, %s, %s, 'customer')",
                (username, hashed_pw, fname, lname)
            )

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    db = get_db()

    if request.method == "POST":
        action = request.form.get("action", "").strip()

        if action == "update_profile":
            fname = request.form.get("fname", "").strip()
            lname = request.form.get("lname", "").strip()
            if fname and lname:
                with db.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET fname = %s, lname = %s WHERE user_id = %s",
                        (fname, lname, user_id)
                    )
                session["fname"] = fname
                session["lname"] = lname
                flash("Profile updated successfully!", "success")
            else:
                flash("First and last name are required.", "danger")

        elif action == "change_password":
            current = request.form.get("current_password", "").strip()
            new_pass = request.form.get("new_password", "").strip()
            confirm = request.form.get("confirm_password", "").strip()

            if not current or not new_pass:
                flash("All password fields are required.", "danger")
                return render_template("profile.html", user=get_profile(user_id))

            if new_pass != confirm:
                flash("New passwords do not match.", "danger")
                return render_template("profile.html", user=get_profile(user_id))

            if len(new_pass) < 6:
                flash("New password must be at least 6 characters.", "danger")
                return render_template("profile.html", user=get_profile(user_id))

            with db.cursor() as cursor:
                cursor.execute("SELECT password FROM users WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()
                if not check_password_hash(user["password"], current):
                    flash("Current password is incorrect.", "danger")
                    return render_template("profile.html", user=get_profile(user_id))

                cursor.execute(
                    "UPDATE users SET password = %s WHERE user_id = %s",
                    (generate_password_hash(new_pass), user_id)
                )
            flash("Password changed successfully!", "success")

        return redirect(url_for("auth.profile"))

    user = get_profile(user_id)
    return render_template("profile.html", user=user)


def get_profile(user_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, fname, lname, role, created_at FROM users WHERE user_id = %s",
            (user_id,)
        )
        return cursor.fetchone()


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
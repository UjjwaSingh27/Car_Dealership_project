from flask import Blueprint, render_template, request, jsonify, session
from database import get_db
import pymysql

bp = Blueprint("cars", __name__, url_prefix="/cars")


@bp.route("/")
def index():
    search = request.args.get("search", "").strip()
    make = request.args.get("make", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    status = request.args.get("status", "").strip()
    fuel = request.args.get("fuel", "").strip()
    sort = request.args.get("sort", "vin").strip()
    page = request.args.get("page", 1, type=int)

    # Sort mapping
    sort_map = {
        "price_asc":    "c.selling_price ASC",
        "price_desc":   "c.selling_price DESC",
        "year_desc":    "c.year DESC",
        "year_asc":     "c.year ASC",
        "mileage_asc":  "cs.mileage ASC",
    }
    order_by = sort_map.get(sort, "c.vin")

    db = get_db()
    with db.cursor() as cursor:
        # Build WHERE clauses
        where_clauses = []
        params = []

        if search:
            where_clauses.append("(c.make LIKE %s OR c.model LIKE %s OR c.vin LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if make:
            where_clauses.append("c.make = %s")
            params.append(make)
        if status:
            where_clauses.append("c.status = %s")
            params.append(status)
        if min_price:
            where_clauses.append("c.selling_price >= %s")
            params.append(float(min_price))
        if max_price:
            where_clauses.append("c.selling_price <= %s")
            params.append(float(max_price))
        if fuel:
            where_clauses.append("cs.fuel_type = %s")
            params.append(fuel)

        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Total count
        count_sql = (
            "SELECT COUNT(*) as total FROM cars c "
            "LEFT JOIN car_specifications cs ON c.vin = cs.vin"
            + where_sql
        )
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]

        # Fetch cars with sort
        sql = f"""
            SELECT c.vin, c.make, c.model, c.year, c.selling_price, c.cost_price,
                   c.status, c.image_path,
                   cs.fuel_type, cs.transmission, cs.mileage, cs.color
            FROM cars c
            LEFT JOIN car_specifications cs ON c.vin = cs.vin
        """ + where_sql + f" ORDER BY {order_by} LIMIT 20 OFFSET %s"

        fetch_params = params + [(page - 1) * 20]
        cursor.execute(sql, fetch_params)
        cars = cursor.fetchall()

        # Get unique makes for filter dropdown
        cursor.execute("SELECT DISTINCT make FROM cars ORDER BY make")
        makes = [row["make"] for row in cursor.fetchall()]

    return render_template(
        "index.html",
        cars=cars,
        makes=makes,
        total=total,
        page=page,
        search=search,
        make=make,
        min_price=min_price,
        max_price=max_price,
        status=status,
        fuel=fuel,
        sort=sort,
    )


@bp.route("/<vin>")
def detail(vin):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT c.vin, c.make, c.model, c.year, c.selling_price, c.cost_price,
                   c.status, c.image_path,
                   cs.fuel_type, cs.transmission, cs.mileage, cs.color
            FROM cars c
            LEFT JOIN car_specifications cs ON c.vin = cs.vin
            WHERE c.vin = %s
        """, (vin,))
        car = cursor.fetchone()

        if not car:
            return "Car not found", 404

        # Check if this car is in the logged-in user's wishlist
        in_wishlist = False
        if "user_id" in session:
            cursor.execute(
                "SELECT 1 FROM wishlist WHERE user_id = %s AND vin = %s",
                (session["user_id"], vin)
            )
            in_wishlist = cursor.fetchone() is not None

        # Fetch reviews for this car (graceful — skips if table doesn't exist yet)
        try:
            cursor.execute("""
                SELECT r.rating, r.comment, r.created_at, u.fname, u.lname
                FROM reviews r
                JOIN users u ON r.user_id = u.user_id
                WHERE r.vin = %s
                ORDER BY r.created_at DESC
            """, (vin,))
            reviews = cursor.fetchall()
        except pymysql.err.ProgrammingError:
            reviews = []

    return render_template("car_detail.html", car=car, reviews=reviews, in_wishlist=in_wishlist)


@bp.route("/api/list")
def api_list():
    search = request.args.get("search", "").strip()
    make = request.args.get("make", "").strip()
    status = request.args.get("status", "").strip()

    db = get_db()
    with db.cursor() as cursor:
        sql = """
            SELECT c.vin, c.make, c.model, c.year, c.selling_price, c.status,
                   cs.fuel_type, cs.transmission, cs.mileage, cs.color
            FROM cars c
            LEFT JOIN car_specifications cs ON c.vin = cs.vin
            WHERE 1=1
        """
        params = []
        if search:
            sql += " AND (c.make LIKE %s OR c.model LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        if make:
            sql += " AND c.make = %s"
            params.append(make)
        if status:
            sql += " AND c.status = %s"
            params.append(status)
        sql += " ORDER BY c.vin LIMIT 50"

        cursor.execute(sql, params)
        cars = cursor.fetchall()

    return jsonify(cars)
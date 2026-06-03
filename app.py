import os
from flask import Flask, redirect, url_for, session, flash
from flask_session import Session
from config import Config
from database import close_db


app = Flask(__name__)
app.config.from_object(Config)

# Serve car images from static/images/
CAR_IMAGE_FOLDER = os.path.join(app.root_path, "static", "images")
os.makedirs(CAR_IMAGE_FOLDER, exist_ok=True)

Session(app)


@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)


# Import and register blueprints
from routes import auth, cars, customer, admin

app.register_blueprint(auth.bp)
app.register_blueprint(cars.bp)
app.register_blueprint(customer.bp)
app.register_blueprint(admin.bp)


@app.route("/")
def home():
    return redirect(url_for("cars.index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
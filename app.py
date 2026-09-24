from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta


app = Flask(__name__)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wasteless.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Create database tables when the app starts.
# This is required for deployment with Gunicorn/Render because
# the __main__ block is not executed there.
with app.app_context():
    db.create_all()


# =========================================================
# FOOD DATABASE TABLE
# =========================================================

class Food(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    quantity = db.Column(
        db.Float,
        nullable=False
    )

    unit = db.Column(
        db.String(20),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    purchase_date = db.Column(
        db.String(20),
        nullable=False
    )

    expiry_date = db.Column(
        db.String(20),
        nullable=False
    )

    notes = db.Column(
        db.Text
    )


# =========================================================
# DONATION DATABASE TABLE
# =========================================================

class Donation(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    food_name = db.Column(
        db.String(100),
        nullable=False
    )

    quantity = db.Column(
        db.Float,
        nullable=False
    )

    unit = db.Column(
        db.String(20),
        nullable=False
    )

    pickup_location = db.Column(
        db.String(200),
        nullable=False
    )

    available_until = db.Column(
        db.String(20),
        nullable=False
    )

    notes = db.Column(
        db.Text
    )


# =========================================================
# FOOD REQUEST DATABASE TABLE
# =========================================================

class FoodRequest(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    donation_id = db.Column(
        db.Integer,
        nullable=False
    )

    food_name = db.Column(
        db.String(100),
        nullable=False
    )

    quantity = db.Column(
        db.Float,
        nullable=False
    )

    unit = db.Column(
        db.String(20),
        nullable=False
    )

    pickup_location = db.Column(
        db.String(200),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )


# =========================================================
# SPLASH PAGE
# =========================================================

@app.route("/")
def splash():

    return render_template(
        "splash.html"
    )


# =========================================================
# ONBOARDING
# =========================================================

@app.route("/onboarding")
def onboarding():

    return render_template(
        "onboarding.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    foods = Food.query.all()

    today = date.today()

    seven_days_later = (
        today + timedelta(days=7)
    )

    expiring_foods = []

    for food in foods:

        expiry = date.fromisoformat(
            food.expiry_date
        )

        if today <= expiry <= seven_days_later:

            expiring_foods.append(food)


    # -----------------------------------------------------
    # FOOD SAVED / FOOD TRACKED
    # -----------------------------------------------------

    food_saved = 0

    for food in foods:

        if food.unit == "kg":

            food_saved += food.quantity

        elif food.unit == "g":

            food_saved += (
                food.quantity / 1000
            )


    # -----------------------------------------------------
    # DONATIONS
    # -----------------------------------------------------

    donation_count = Donation.query.count()


    return render_template(

        "dashboard.html",

        foods=foods,

        food_count=len(foods),

        expiring_foods=expiring_foods,

        food_saved=round(
            food_saved,
            2
        ),

        donation_count=donation_count

    )


# =========================================================
# ADD FOOD
# =========================================================

@app.route(
    "/add-food",
    methods=["GET", "POST"]
)
def add_food():

    if request.method == "POST":

        food = Food(

            name=request.form["name"],

            quantity=float(
                request.form["quantity"]
            ),

            unit=request.form["unit"],

            category=request.form["category"],

            purchase_date=request.form[
                "purchase_date"
            ],

            expiry_date=request.form[
                "expiry_date"
            ],

            notes=request.form["notes"]

        )

        db.session.add(food)

        db.session.commit()

        return redirect("/dashboard")


    return render_template(
        "add_food.html"
    )


# =========================================================
# MY FOOD
# =========================================================

@app.route("/my-food")
def my_food():

    foods = Food.query.order_by(
        Food.expiry_date.asc()
    ).all()

    return render_template(

        "my_food.html",

        foods=foods

    )


# =========================================================
# DELETE FOOD
# =========================================================

@app.route(
    "/delete-food/<int:food_id>",
    methods=["POST"]
)
def delete_food(food_id):

    food = Food.query.get_or_404(
        food_id
    )

    db.session.delete(food)

    db.session.commit()

    return redirect("/my-food")


# =========================================================
# DONATE FOOD
# =========================================================

@app.route(
    "/donate-food",
    methods=["GET", "POST"]
)
def donate_food():

    if request.method == "POST":

        donation = Donation(

            food_name=request.form[
                "food_name"
            ],

            quantity=float(
                request.form["quantity"]
            ),

            unit=request.form["unit"],

            pickup_location=request.form[
                "pickup_location"
            ],

            available_until=request.form[
                "available_until"
            ],

            notes=request.form["notes"]

        )

        db.session.add(donation)

        db.session.commit()

        return redirect(
            "/donate-food"
        )


    donations = Donation.query.order_by(
        Donation.available_until.asc()
    ).all()


    return render_template(

        "donate_food.html",

        donations=donations

    )


# =========================================================
# MY IMPACT
# =========================================================

@app.route("/my-impact")
def my_impact():

    food_count = Food.query.count()

    donation_count = Donation.query.count()

    request_count = FoodRequest.query.count()


    # -----------------------------------------------------
    # TOTAL FOOD TRACKED
    # -----------------------------------------------------

    foods = Food.query.all()

    total_food_tracked = 0

    for food in foods:

        if food.unit == "kg":

            total_food_tracked += food.quantity

        elif food.unit == "g":

            total_food_tracked += (
                food.quantity / 1000
            )


    # -----------------------------------------------------
    # TOTAL DONATED
    # -----------------------------------------------------

    donations = Donation.query.all()

    total_donated = 0

    for donation in donations:

        if donation.unit == "kg":

            total_donated += donation.quantity

        elif donation.unit == "g":

            total_donated += (
                donation.quantity / 1000
            )


    total_food_tracked = round(
        total_food_tracked,
        2
    )

    total_donated = round(
        total_donated,
        2
    )


    # -----------------------------------------------------
    # ESTIMATED IMPACT
    # -----------------------------------------------------

    co2_saved = round(
        total_donated * 2.5,
        2
    )

    money_saved = round(
        total_donated * 80,
        2
    )


    # -----------------------------------------------------
    # IMPACT LEVEL
    # -----------------------------------------------------

    if total_donated == 0:

        impact_level = "Getting Started"

    elif total_donated < 5:

        impact_level = "Food Saver"

    elif total_donated < 10:

        impact_level = "WasteLess Hero"

    else:

        impact_level = "WasteLess Champion"


    return render_template(

        "my_impact.html",

        food_count=food_count,

        donation_count=donation_count,

        request_count=request_count,

        total_food_tracked=total_food_tracked,

        total_donated=total_donated,

        co2_saved=co2_saved,

        money_saved=money_saved,

        impact_level=impact_level

    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    return render_template(
        "profile.html"
    )


# =========================================================
# AI FOOD ASSISTANT
# =========================================================

@app.route("/ai-assistant")
def ai_assistant():

    foods = Food.query.order_by(
        Food.expiry_date.asc()
    ).all()

    food_analysis = []

    today = date.today()


    for food in foods:

        expiry_date = date.fromisoformat(
            food.expiry_date
        )

        days_left = (
            expiry_date - today
        ).days


        # -------------------------------------------------
        # AI PRIORITY
        # -------------------------------------------------

        if days_left < 0:

            priority = "Expired"

            suggestion = (
                "Do not use this food if it is "
                "unsafe or has spoiled."
            )

        elif days_left == 0:

            priority = "Use Today"

            suggestion = (
                "Use this food today to avoid "
                "unnecessary waste."
            )

        elif days_left <= 2:

            priority = "Use Very Soon"

            suggestion = (
                "Try to use this food within "
                "the next 1–2 days."
            )

        elif days_left <= 5:

            priority = "Use Soon"

            suggestion = (
                "Plan a meal using this food soon."
            )

        else:

            priority = "Fresh"

            suggestion = (
                "This food still has time, but "
                "keep monitoring its expiry date."
            )


        # -------------------------------------------------
        # RECIPE SUGGESTION
        # -------------------------------------------------

        food_name = food.name.lower()

        recipe = ""

        if "tomato" in food_name:

            recipe = (
                "Try tomato soup, tomato pasta "
                "or fresh tomato salad."
            )

        elif "potato" in food_name:

            recipe = (
                "Try potato curry, roasted potatoes "
                "or homemade potato wedges."
            )

        elif "rice" in food_name:

            recipe = (
                "Try fried rice, rice pulao "
                "or vegetable rice."
            )

        elif "bread" in food_name:

            recipe = (
                "Try toast, sandwich, bread pizza "
                "or bread upma."
            )

        elif "banana" in food_name:

            recipe = (
                "Try banana smoothie, banana oats "
                "or banana pancakes."
            )

        elif "milk" in food_name:

            recipe = (
                "Try a smoothie, milkshake, "
                "oats or homemade curd."
            )

        elif "apple" in food_name:

            recipe = (
                "Try apple oats, fruit salad "
                "or an apple smoothie."
            )

        else:

            recipe = (
                "Look for a simple recipe that "
                "uses this food before it expires."
            )


        food_analysis.append({

            "food": food,

            "days_left": days_left,

            "priority": priority,

            "suggestion": suggestion,

            "recipe": recipe

        })


    return render_template(

        "ai_assistant.html",

        foods=foods,

        food_analysis=food_analysis

    )


# =========================================================
# FIND FOOD
# =========================================================

@app.route("/find-food")
def find_food():

    donations = Donation.query.order_by(
        Donation.available_until.asc()
    ).all()

    return render_template(

        "find_food.html",

        donations=donations

    )


# =========================================================
# FOOD REQUESTS
# =========================================================

@app.route("/food-requests")
def food_requests():

    requests = FoodRequest.query.order_by(
        FoodRequest.id.desc()
    ).all()

    return render_template(

        "food_requests.html",

        requests=requests

    )


# =========================================================
# REQUEST FOOD
# =========================================================

@app.route(
    "/request-food/<int:donation_id>",
    methods=["POST"]
)
def request_food(donation_id):

    donation = Donation.query.get_or_404(
        donation_id
    )

    food_request = FoodRequest(

        donation_id=donation.id,

        food_name=donation.food_name,

        quantity=donation.quantity,

        unit=donation.unit,

        pickup_location=donation.pickup_location,

        status="Pending"

    )

    db.session.add(food_request)

    db.session.commit()

    return redirect(
        "/find-food"
    )


# =========================================================
# ACCEPT FOOD REQUEST
# =========================================================

@app.route(
    "/accept-request/<int:request_id>",
    methods=["POST"]
)
def accept_request(request_id):

    food_request = FoodRequest.query.get_or_404(
        request_id
    )

    food_request.status = "Accepted"

    db.session.commit()

    return redirect(
        "/food-requests"
    )


# =========================================================
# REJECT FOOD REQUEST
# =========================================================

@app.route(
    "/reject-request/<int:request_id>",
    methods=["POST"]
)
def reject_request(request_id):

    food_request = FoodRequest.query.get_or_404(
        request_id
    )

    food_request.status = "Rejected"

    db.session.commit()

    return redirect(
        "/food-requests"
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(
        debug=True
    )
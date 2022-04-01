from flask import Flask, jsonify, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    prices = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


db.create_all()
all_restaurants = db.session.query(Restaurant).all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET", "POST"])
def get_random():
    choice = random.choice(all_restaurants)
    return jsonify(name=choice.name,
                   map_url=choice.map_url,
                   location=choice.location,
                   description=choice.description,
                   prices=choice.prices,
                   id=choice.id)


@app.route("/all", methods=["GET", "POST"])
def get_all_cafes():
    # This uses a List Comprehension but you could also split it into 3 lines.
    return jsonify(cafes=[cafe.to_dict() for cafe in all_restaurants])


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    restaurant = db.session.query(Restaurant).filter_by(location=query_location).first()
    if restaurant:
        return jsonify(cafe=restaurant.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a restaurant at that location."})


@app.route("/add", methods=["POST", "GET"])
def post_new_cafe():
    new_restaurant = Restaurant(
        name=request.form.get("name"),
        location=request.form.get("loc"),
        description=request.form.get("description"),
        prices=request.form.get("prices"),

    )
    db.session.add(new_restaurant)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(restaurant_id):
    new_price = request.args.get("new_price")
    restaurant = db.session.query(Restaurant).get(restaurant_id)
    if restaurant:
        restaurant.prices = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a restaurant with that id was not found in the database."}), 404


@app.route("/report-closed/<restaurant_id>", methods=["DELETE", "GET"])
def delete(restaurant_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecret":
        restaurant = db.session.query(Restaurant).get(restaurant_id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe."}), 200
        else:
            return jsonify(error={"Restaurant not found."}), 404
    else:
        return jsonify(error={"Not authorized": "Sorry, wrong API Key."}), 404


if __name__ == '__main__':
    app.run(debug=True)

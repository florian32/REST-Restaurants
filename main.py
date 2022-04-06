from flask import Flask, jsonify, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import random
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    website_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    prices = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


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
                   website_url=choice.website_url,
                   location=choice.location,
                   description=choice.description,
                   prices=choice.prices,
                   id=choice.id)


@app.route("/all", methods=["GET", "POST"])
def get_all_restaurants():
    # This uses a List Comprehension but you could also split it into 3 lines.
    return jsonify(restaurants=[restaurant.to_dict() for restaurant in all_restaurants])


@app.route("/search")
def get_restaurant_at_location():
    query_location = request.args.get("loc")
    restaurant = db.session.query(Restaurant).filter_by(location=query_location).first()
    if restaurant:
        return jsonify(restaurant=restaurant.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a restaurant at that location."})


@app.route("/add", methods=["POST", "GET"])
def post_new_restaurant():

    restaurant_name = request.form.get("name")
    response = requests.get("https://www.google.com/search?q=molam&oq=mol&aqs=chrome.0.69i59j46i175i199i433i512j69i57j0i433i512j46i512j69i60l3.834j0j7&sourceid=chrome&ie=UTF-8")
    website = response.text
    soup = BeautifulSoup(website, "html.parser")
    website_link = soup.find_all('a', class_="ab_button")
    print(website_link)




    # new_restaurant = Restaurant(
    #     name=request.form.get("name"),
    #     location=request.form.get("loc"),
    #     map_url=request.form.get("map"),
    #     website_url=request.form.get("website"),
    #     description=request.form.get("description"),
    #     prices=request.form.get("prices"),
    #
    # )
    # db.session.add(new_restaurant)
    # db.session.commit()
    # return jsonify(response={"success": "Successfully added the new restaurant."})


@app.route("/update-price", methods=["PATCH", "GET"])
def patch_new_price():
    restaurant_id = request.args.get("id")
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

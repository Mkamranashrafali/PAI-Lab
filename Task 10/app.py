import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

hotel_data = {
    "rooms": [
        {
            "name": "Standard Room",
            "price": "$80 per night",
            "capacity": "2 guests",
            "size": "22 m2",
            "available": 4,
            "amenities": ["Queen bed", "Free Wi-Fi", "Air conditioning", "TV", "Work desk"]
        },
        {
            "name": "Deluxe Room",
            "price": "$120 per night",
            "capacity": "3 guests",
            "size": "30 m2",
            "available": 2,
            "amenities": ["King bed", "Free breakfast", "Balcony", "Mini fridge", "Smart TV"]
        },
        {
            "name": "Suite",
            "price": "$180 per night",
            "capacity": "4 guests",
            "size": "45 m2",
            "available": 1,
            "amenities": ["King bed", "Living area", "Ocean view", "Free breakfast", "Room service", "Coffee machine"]
        }
    ],
    "menu": {
        "breakfast": ["Omelette", "Paratha", "Fresh fruit", "Tea/Coffee"],
        "lunch": ["Chicken biryani", "Grilled fish", "Pasta", "Salad"],
        "dinner": ["BBQ platter", "Chicken karahi", "Soup", "Dessert"]
    },
    "timing": {
        "restaurant": "Restaurant timing is 7:00 AM to 11:00 PM.",
        "check_in": "2:00 PM",
        "check_out": "11:00 AM",
        "late_check_out": "Late check-out is available until 1:00 PM for $20, subject to availability.",
        "early_check_in": "Early check-in is possible from 12:00 PM based on availability for $15."
    },
    "contact": {
        "phone": "+1-555-123-4567",
        "email": "hello@seabreezehotel.com",
        "address": "Beach Road 45, Miami, FL"
    },
    "services": {
        "wifi": "Free high-speed Wi-Fi is available in all rooms and public areas.",
        "parking": "Free on-site parking is available for guests.",
        "breakfast": "Breakfast is included with Deluxe Room and Suite. It is available for $10 per person for Standard Room.",
        "airport": "Airport pickup is available for $25 per trip with prior request.",
        "pets": "Pets are not allowed, except certified service animals.",
        "smoking": "All indoor rooms are non-smoking. A designated outdoor smoking area is available."
    },
    "payment": "We accept cash, Visa, MasterCard, and online bank transfer.",
    "tax": "Room rates are subject to 10% city tax and 5% service charge.",
    "children": "One child under 6 years can stay free using existing bedding. Extra bed costs $18 per night.",
    "id": "A valid government-issued photo ID is required at check-in.",
    "couple_friendly": "Yes, we are couple-friendly for adults with valid IDs.",
    "about": "Sea Breeze Hotel is a family-friendly 3-star hotel near the beach with peaceful rooms and local food options.",
    "nearby": [
        "Central Masjid is 400 meters away.",
        "City Park is a 5-minute walk.",
        "Seaside Mall is 1.2 km away.",
        "Public beach entrance is 8 minutes on foot."
    ]
}


def format_rooms():
    lines = []
    for room in hotel_data["rooms"]:
        amenities = ", ".join(room["amenities"])
        lines.append(
            f"{room['name']} - {room['price']} - {room['capacity']} - {room['size']} - {room['available']} available. Amenities: {amenities}."
        )
    return "\n".join(lines)


def format_room_detail(room):
    return (
        f"{room['name']} costs {room['price']} and is suitable for {room['capacity']} in {room['size']}. "
        f"Currently {room['available']} room(s) available. "
        f"Amenities include: {', '.join(room['amenities'])}."
    )


def contains_any(text, words):
    return any(word in text for word in words)


def format_availability():
    lines = ["Current room availability:"]
    for room in hotel_data["rooms"]:
        lines.append(f"{room['name']}: {room['available']} available")
    return "\n".join(lines)


def format_menu():
    breakfast = ", ".join(hotel_data["menu"]["breakfast"])
    lunch = ", ".join(hotel_data["menu"]["lunch"])
    dinner = ", ".join(hotel_data["menu"]["dinner"])
    return (
        f"Breakfast: {breakfast}.\n"
        f"Lunch: {lunch}.\n"
        f"Dinner: {dinner}."
    )


def format_nearby_places():
    return "Nearby places:\n" + "\n".join(hotel_data["nearby"])


def get_bot_reply(message):
    text = message.lower().strip()
    text = text.replace("?", " ").replace(".", " ").replace(",", " ")

    if contains_any(text, ["hi", "hello", "hey", "salam", "assalam", "aoa"]):
        return random.choice([
            "Hello! I can help with general hotel information.",
            "Welcome! Ask me about rooms, availability, menu, costs, and nearby places.",
            "Hi! I can share room options, prices, facilities, and hotel area details."
        ])

    room_map = {
        "standard": "Standard Room",
        "deluxe": "Deluxe Room",
        "suite": "Suite"
    }

    for key, room_name in room_map.items():
        if key in text:
            room = next((r for r in hotel_data["rooms"] if r["name"] == room_name), None)
            if room:
                return format_room_detail(room)

    if contains_any(text, ["online", "book", "booking", "reserve", "reservation", "cancel", "refund"]):
        return "This chatbot provides general information only. Online booking is not available here. Please contact the hotel by phone for reservations."

    if contains_any(text, ["available", "availability", "empty room", "room free", "room available"]):
        return format_availability()

    if contains_any(text, ["room", "type", "categories"]):
        return "Here are our room options:\n" + format_rooms()

    if contains_any(text, ["menu", "food", "meal", "breakfast", "lunch", "dinner"]):
        return format_menu() + "\n" + hotel_data["timing"]["restaurant"]

    if contains_any(text, ["price", "cost", "rate", "charges", "kitna", "cheap", "expensive"]):
        prices = [f"{room['name']}: {room['price']}" for room in hotel_data["rooms"]]
        return "Our current room rates are:\n" + "\n".join(prices) + "\n" + hotel_data["tax"]

    if contains_any(text, ["amenit", "facility", "facilities", "features"]):
        return "Room and hotel amenities:\n" + format_rooms() + "\n" + hotel_data["services"]["wifi"]

    if contains_any(text, ["wifi", "internet"]):
        return hotel_data["services"]["wifi"]

    if contains_any(text, ["parking", "car park", "car parking"]):
        return hotel_data["services"]["parking"]

    if contains_any(text, ["about", "hotel info", "information", "tell me about hotel", "about hotel"]):
        return hotel_data["about"] + "\n" + format_nearby_places()

    if contains_any(text, ["near", "nearby", "masjid", "mosque", "park", "mall", "beach"]):
        return format_nearby_places()

    if contains_any(text, ["airport", "pickup", "drop"]):
        return hotel_data["services"]["airport"]

    if contains_any(text, ["pet", "dog", "cat"]):
        return hotel_data["services"]["pets"]

    if contains_any(text, ["smoking", "smoke"]):
        return hotel_data["services"]["smoking"]

    if contains_any(text, ["payment", "pay", "card", "cash", "visa", "mastercard", "bank transfer"]):
        return hotel_data["payment"]

    if contains_any(text, ["check in", "check-in", "late check in", "late arrival"]):
        return f"Check-in time is {hotel_data['timing']['check_in']}. If you arrive after 10:00 PM, please inform us in advance."

    if contains_any(text, ["check out", "check-out", "late check out"]):
        return f"Check-out time is {hotel_data['timing']['check_out']}. {hotel_data['timing']['late_check_out']}"

    if contains_any(text, ["early check", "early check in"]):
        return hotel_data["timing"]["early_check_in"]

    if contains_any(text, ["child", "children", "kid", "family", "extra bed"]):
        return hotel_data["children"]

    if contains_any(text, ["id", "cnic", "passport", "document"]):
        return hotel_data["id"]

    if contains_any(text, ["couple", "unmarried", "friendly"]):
        return hotel_data["couple_friendly"]

    if contains_any(text, ["location", "address", "where", "map"]):
        return f"Our address is {hotel_data['contact']['address']}."

    if contains_any(text, ["contact", "phone", "call", "email", "number"]):
        return (
            f"You can reach us at {hotel_data['contact']['phone']} or {hotel_data['contact']['email']}."
        )

    if contains_any(text, ["thanks", "thank you", "shukria", "jazak"]):
        return "You are welcome. Ask anytime for general hotel information."

    return (
        "I can help with general information: rooms, availability, menu, costs, facilities, and nearby places like masjid and park."
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    reply = get_bot_reply(message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)

from chatbot import handle_conversation
from flask import Flask, request, jsonify, render_template


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")  # simple HTML page

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    bot_response = handle_conversation(user_input)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/send-location", methods=["POST"])
def get_location():
    data = request.get_json()
    lat = data.get("latitude")
    lon = data.get("longitude")

    print(f"User location received: {lat}, {lon}")  # Should print in terminal

    return jsonify({"message": f"📍 Received your location: Latitude {lat}, Longitude {lon}"}), 200

# Only ONE app.run
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)



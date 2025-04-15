import random
import re
from openai import OpenAI

# DeepInfra credentials
DEEPINFRA_API_KEY = "Z1dqh9U7DJuxZwSOex5fHwvCEYfcKwrl"
DEEPINFRA_BASE_URL = "https://api.deepinfra.com/v1/openai"

# Initialize OpenAI-compatible client for DeepInfra
openai = OpenAI(
    api_key=DEEPINFRA_API_KEY,
    base_url=DEEPINFRA_BASE_URL,
)

# Menu with pricing
menu = {
    "samosa": 20,
    "pizza": 150,
    "mango lassi": 50,
    "pav bhaji": 60,
    "vada pav": 25,
    "masala dosa": 80,
    "biryani": 120,
    "rava dosa": 70,
    "chole bhature": 90,
    "dosa": 70

}
# Chat context
context = {
    "intent": None,
    "order": {},
    "status": "not_started",
    "order_id": None,
    "last_message": None
}

# Intents
intents = {
    "greeting": {
        "patterns": ["hi", "hello", "hey", "good morning", "good evening"],
        "responses": ["Hello! Welcome to our hotel.", "Hi there! How can I help you today?"]
    },
    "new_order": {
        "patterns": ["new order", "place order", "i want to order","i want food" , "i am hungry"],
        "responses": ["Great! Please tell me what you'd like to order and the quantity."]
    },
    "order_quantity": {
        "patterns": ["i want", "can i get", "please give me", "i would like", "add" , "i want to order"],
        "responses": ["Got it! Would you like to add or remove something else?"]
    },
    "order_remove": {
        "patterns": ["remove", "delete", "take off", "cancel item"],
        "responses": ["Item removed. Would you like to remove or add anything else?"]
    },
    "track_order": {
        "patterns": ["track my order", "where is my order", "order status"],
        "responses": []
    },
    "confirm_order": {
        "patterns": ["confirm", "yes", "place it", "order now"],
        "responses": []
    },
    "review": {
        "patterns": ["it was great", "loved it", "bad", "not good", "awesome", "average"],
        "responses": ["Thanks for your feedback!", "We appreciate your review!"]
    },
    "hotel_location": {
        "patterns": [
            "where is your hotel",
            "how can i come",
            "hotel location",
            "send me location",
            "how to reach",
            "where are you located",
            "how to come to hotel"
       ],
        "responses": [
            "Sure! You can find us here: [Hotel Location on Google Maps](https://maps.app.goo.gl/ikh57cijNSzgBPLQ7)",
            "Here's our location: https://maps.app.goo.gl/ikh57cijNSzgBPLQ7",
            "Visit us at this location: https://maps.app.goo.gl/ikh57cijNSzgBPLQ7"
       ]
},
}

# Extract intent
def get_intent(user_input):
    user_input = user_input.lower()
    for intent, data in intents.items():
        for pattern in data["patterns"]:
            if pattern in user_input:
                return intent
    return None

# Extract items and quantities
import re

def extract_items_and_quantities(user_input):
    items = {}
    user_input = user_input.lower()
    sorted_menu = sorted(menu.keys(), key=lambda x: -len(x))  # Longer names first

    for item in sorted_menu:
        pattern = rf"(\d+)?\s*{re.escape(item)}"
        matches = list(re.finditer(pattern, user_input))
        for match in matches:
            qty = int(match.group(1)) if match.group(1) else 1
            items[item] = items.get(item, 0) + qty
            # Remove the matched portion to avoid it being counted again
            user_input = user_input.replace(match.group(0), "", 1)
    
    return items

# Format order for display
def format_order(order_dict):
    return ", ".join([f"{qty} {item}(s)" for item, qty in order_dict.items()])

# Total billing
def calculate_total(order):
    return sum(menu[item] * qty for item, qty in order.items())

# Query fallback to LLM
def query_llm(prompt):
    response = openai.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {
                "role": "system",
                "content": "You are a strict food-ordering assistant for a hotel.\n\nRULES:\n1. ONLY accept orders from the following MENU. If the user asks for something not listed, you MUST reply: 'Sorry, we don't serve that item.'\n\nMENU:\n- Samosa: ₹20\n- Pizza: ₹150\n- Mango Lassi: ₹50\n- Pav Bhaji: ₹80\n- Vada Pav: ₹30\n- Masala Dosa: ₹90\n- Biryani: ₹180\n- Rava Dosa: ₹85\n- Chole Bhature: ₹100\n- Dosa: ₹70\n\n2. If the user says they are 'hungry' or 'want food', begin taking their order immediately. You are ONLY here to help with food.\n\n3. When the user confirms an order, generate a random Order ID that starts with '#' followed by 6 digits (e.g., #123456). Share it immediately.\n\n4. DO NOT allow order tracking unless the user provides a valid Order ID.\n\n5. ALWAYS ask for the Order ID before providing tracking information.\n   - If the Order ID is missing, say: 'Please provide your order ID to track your order.'\n   - If the Order ID is incorrect, say: 'The order ID is incorrect. Please check and try again.'\n\nThis is a strict flow — do not break the rules or add extra conversation."
                            "strictly check the emotion of customer if they are happy provide joy full answer and if not they are unsatisfied say we are deeply sorry we will improve kinda answer" "if user provide only track id then also accept the answer from the user and provide order_status" "if user ask for location of our hotel ask where is your hotel aur ask how can i come to your hotel provide with this link https://maps.app.goo.gl/ikh57cijNSzgBPLQ7 "
                             "strictly provide the location link when user asks for it .If the user asks about the hotel's location or how to reach the hotel, reply with the link: https://maps.app.goo.gl/ikh57cijNSzgBPLQ7"
                             },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content.strip()

# Chat logic
def handle_conversation(user_input):
    intent = get_intent(user_input)

    if intent == "greeting":
        return random.choice(intents["greeting"]["responses"])

    elif intent == "new_order":
        context["intent"] = "new_order"
        context["order"] = {}
        context["status"] = "not_started"
        context["order_id"] = None
        return random.choice(intents["new_order"]["responses"])

    elif intent == "order_quantity":
        items = extract_items_and_quantities(user_input)
        if items:
            context["order"].update(items)
            return f"Added {format_order(items)}. Would you like to confirm your order?"
        else:
            return "I couldn't detect any valid items. Please specify items from the menu with quantity."

    elif intent == "order_remove":
        items = extract_items_and_quantities(user_input)
        removed = []
        for item in items:
            if item in context["order"]:
                del context["order"][item]
                removed.append(item)
        if removed:
            return f"Removed {', '.join(removed)}. Anything else?"
        else:
            return "These items weren't in your order."

    elif intent == "confirm_order" and context["order"]:
        total = calculate_total(context["order"])
        context["status"] = "placed"
        context["order_id"] = f"#{random.randint(100000, 999999)}"
        return (
            f"✅ Order confirmed for {format_order(context['order'])}. Total: ₹{total}.\n"
            f"Your Order ID is {context['order_id']}.\n"
            "Say 'track my order' and provide your Order ID to get the status."
        )

    elif intent == "track_order":
        match = re.search(r"#\d{6}", user_input)
        if not context["order_id"]:
            return "You haven't placed any order yet."
        elif not match:
            return "❗ Please provide your order ID to track your order."
        elif match.group() != context["order_id"]:
            return "❌ The order ID is incorrect. Please check and try again."
        else:
            if context["status"] == "placed":
                context["status"] = "delivered"
                return "🚚 Your order is on the way... and now delivered! How was your experience?"
            elif context["status"] == "delivered":
                return "✅ Your order has been delivered. We'd love your feedback!"
            else:
                return "⚠️ You haven't placed any order yet."

    elif intent == "review":
        return random.choice(intents["review"]["responses"])
    
    elif intent == "hotel_location":
        return random.choice(intents["hotel_location"]["responses"])

    else:
        return query_llm(user_input)
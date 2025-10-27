from flask import Flask, request, jsonify, render_template
import hmac
import hashlib
import base64
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Config (use env vars in production)
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBMAKER_TOKEN") or "Your_HubSpot_AccessToken"
HUBSPOT_PORTAL_ID = os.getenv("HUBSPOT_PORTAL_ID") or "7185807"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "sk-proj-***"
CHATFLOW_ID = os.getenv("CHATFLOW_ID") or "12345"
HUBSPOT_WEBHOOK_TOKEN = os.getenv("HUBSPOTWEBHOOK_TOKEN") or None

openai.api_key = OPENAI_API_KEY

def verify_hubspot_signature(payload, signature):
    """Verify HubSpot webhook signature for security."""
    if not HUBSPOTWEBHOOK_TOKEN:
        return True  # Skip in dev; add token in HubSpot webhook setup
    digest = hmac.new(
        HUBSPOT_WEBHOOK_TOKEN.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).digest()
    computed = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed, signature)

def generate_ai_response(message):
    """Generate reply using OpenAI GPT."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful customer support bot for Volt1.1. Keep responses concise and friendly."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def send_reply_to_hubspot(conversation_id, message, visitor_id=None):
    """Send reply back to HuBSpot conversation via API."""
    url = f"https://api.hubapi.com/conversations/v3/conversations/threads/{conversation_id}/messages"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "body": message,
        "type": "BOT"  # Or 'AGENT' if needed
    }
    if visitor_id:
        data["sender"] = {"type": "VISITOR", "id": visitor_id}   # Optional

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Error sending reply: {response.text}")
        return False
    return True

@app.route("/webhook", methods=["POST"])
def webhook():
    """HuBSpot webhook: Receive chat event, reply via API."""
    body = request.get_data(as_text=True)
    signature = request.headers.get("X-HubSpot-Signature", "")

    if not verify_hubspot_signature(body, signature):
        return jsonify({"error": "Invalid signature"}), 403

    data = request.json
    event_type = data.get("eventType", "")
    if event_type != "chat.conversation.activity":
        return jsonify({"status": "ignored"}), 200

    # Extract message from payload (adapt based on your event)
    conversation_id = data.get("object", {}).get("conversationId", "")
    visitor_message = data.get("object", {}).get("body", "No message")

    if not conversation_id:
        return jsonify({"status": "no_conversation_id"}), 200

    # Generate reply
    reply = generate_ai_response(visitor_message)
    print(f"Visitor: {visitor_message} | Bot: {reply}")

    # Send back
    send_reply_to_hubapi(conversation_id, reply)

    return jsonify({"status": "success"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    """Standalone chat endpoint for testing."""
    user_message = request.json.get("message")
    reply = generate_ai_response(user_message)
    return jsonify({"reply": reply})

@app.route("/", methods=["GET"])
def index():
    """Simple web UI for testing."""
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
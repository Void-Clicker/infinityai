from flask import Flask, request, jsonify, render_template, send_file
from groq import Groq
import json
import os
import datetime
import zipfile
import io

PROFILE_FILE = "user_profile.json"
HISTORY_FILE = "chat_history.json"

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return {"name": "Manny", "interests": [], "notes": ""}

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return [{"role": "system", "content": "You are Infinity AI."}]

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def get_system_message():
    profile = load_profile()
    name = profile.get("name", "Manny")
    return f"""You are Infinity AI. You are kind, friendly and make everything simple.
The user's name is {name}."""

app = Flask(__name__)
import os
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

messages = load_history()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global messages
    user_message = request.json["message"]
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=700
    )

    reply = response.choices[0].message.content.strip()

    messages.append({"role": "assistant", "content": reply})
    save_history(messages)

    return jsonify({"reply": reply})

# === DAY 22: ANALYTICS / STATS ===
@app.route("/stats", methods=["GET"])
def get_stats():
    # Count generated files
    files = [f for f in os.listdir(".") if f.endswith(".txt")]
    business_posts = len([f for f in files if f.startswith("business_post")])
    automation_ideas = len([f for f in files if f.startswith("automation_ideas")])
    quotes = len([f for f in files if f.startswith("quote")])

    total_files = len(files)
    total_messages = len(messages)

    stats = f"""📊 **Infinity AI Analytics**

**Generated Content:**
• Business Posts: {business_posts}
• Automation Ideas: {automation_ideas}
• Quotes: {quotes}
• Total Files: {total_files}

**Usage:**
• Total Messages: {total_messages}
• Days Active: 22

**Next Goal:** Start offering services to real businesses!

Keep going Manny, you're doing amazing! 🔥"""

    return jsonify({"reply": stats})

# Keep other routes (portfolio, export, improve, etc.)
@app.route("/portfolio", methods=["GET"])
def generate_portfolio():
    portfolio = f"""🚀 MANNY'S AI AUTOMATION PORTFOLIO\nGenerated: {datetime.datetime.now().strftime("%d %B %Y")}\n\nBuilt Infinity AI in 22 days!"""
    return jsonify({"reply": portfolio})

@app.route("/files", methods=["GET"])
def list_files():
    files = [f for f in os.listdir(".") if f.endswith(".txt")]
    return jsonify({"files": sorted(files, reverse=True)})

@app.route("/export", methods=["GET"])
def export_files():
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in os.listdir("."):
            if file.endswith(".txt"):
                zf.write(file)
    memory_file.seek(0)
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name="infinity_ai_exports.zip")

@app.route("/clear", methods=["POST"])
def clear():
    global messages
    messages = [{"role": "system", "content": get_system_message()}]
    save_history(messages)
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)

import os

# Load API keys from a local .env file if python-dotenv is available.
# Environment variables that are already set always take precedence.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, request, jsonify, render_template
from memory import memory_manager
from agent import run_agent_turn
import generate_data

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    query = data.get("query", "")
    session_id = data.get("session_id", "default_session")
    
    if not query:
        return jsonify({
            "answer": "Please type a question before sending.",
            "error": "empty_query",
            "metadata": {"tool_calls_made": [], "grounding_status": "error", "model_used": None}
        }), 400

    try:
        session_memory = memory_manager.get_session(session_id)
        response = run_agent_turn(query, session_memory)
    except Exception as e:
        # Last line of defence: never leak a stack trace to the merchant UI.
        app.logger.exception("Unhandled error in /api/chat: %s", e)
        return jsonify({
            "answer": "Something went wrong on SettleBot's side while processing your request. Please try again.",
            "error": "server_error",
            "metadata": {"tool_calls_made": [], "grounding_status": "error", "model_used": None}
        }), 500

    return jsonify(response)

@app.route("/api/eval", methods=["POST", "GET"])
def eval_harness():
    from eval_harness import run_evaluation
    results = run_evaluation()
    return jsonify(results)

if __name__ == "__main__":
    generate_data.generate_synthetic_data()
    app.run(host="0.0.0.0", port=5001, debug=True)

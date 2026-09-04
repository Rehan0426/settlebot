import os
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
        return jsonify({"error": "Query cannot be empty"}), 400
        
    session_memory = memory_manager.get_session(session_id)
    response = run_agent_turn(query, session_memory)
    
    return jsonify(response)

@app.route("/api/eval", methods=["POST", "GET"])
def eval_harness():
    from eval_harness import run_evaluation
    results = run_evaluation()
    return jsonify(results)

if __name__ == "__main__":
    generate_data.generate_synthetic_data()
    app.run(host="0.0.0.0", port=5001, debug=True)

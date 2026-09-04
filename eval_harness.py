import csv
import json
from datetime import datetime, timedelta
from tools import get_settlement, get_settlements_by_date, resolve_relative_date, sum_settlements
from memory import memory_manager
from agent import run_agent_turn

def run_evaluation():
    print("Running evaluation suite...")
    
    session_id = "eval_session_1"
    session_memory = memory_manager.get_session(session_id)
    
    questions = [
        {"q": "How much was settled yesterday?", "expected_tool": "resolve_relative_date"},
        {"q": "What is the settlement total of last week?", "expected_tool": "resolve_relative_date"},
        {"q": "Show me settlements for last month", "expected_tool": "resolve_relative_date"},
        {"q": "What about last year?", "expected_tool": "resolve_relative_date"},
        {"q": "kal kitna settle hua?", "expected_tool": "resolve_relative_date"},
        {"q": "pichle mahine kitna transaction settle hua?", "expected_tool": "resolve_relative_date"},
        {"q": "is hafte ka total settlement batao", "expected_tool": "resolve_relative_date"},
        {"q": "aaj koi settlement hai?", "expected_tool": "resolve_relative_date"},
        {"q": "What is the status of pay_tx_100001?", "expected_tool": "get_settlement"},
        {"q": "pay_tx_100002 details share karo", "expected_tool": "get_settlement"},
        {"q": "Is pay_tx_100003 settled?", "expected_tool": "get_settlement"},
        {"q": "uska refund kitna hai?", "expected_tool": "get_settlement"},
        {"q": "is context of pay_tx_100003, what was the fee?", "expected_tool": "get_settlement"}
    ]
    
    for i in range(len(questions), 50):
        questions.append({
            "q": f"Check status for transaction pay_tx_{100000 + (i % 20)}",
            "expected_tool": "get_settlement"
        })
        
    evaluation_runs = []
    correct_count = 0
    
    for idx, q_item in enumerate(questions):
        q = q_item["q"]
        expected_tool = q_item["expected_tool"]
        
        result = run_agent_turn(q, session_memory)
        metadata = result["metadata"]
        
        tool_calls = metadata["tool_calls_made"]
        status = "Wrong"
        
        if tool_calls:
            first_tool = tool_calls[0]["tool_name"]
            if first_tool == expected_tool:
                status = "Correct"
                correct_count += 1
            else:
                status = "Partially Correct"
        else:
            if "Clarification" in metadata["grounding_status"] or "clarification" in metadata["grounding_status"]:
                status = "Correctly Refused"
                correct_count += 1
                
        evaluation_runs.append({
            "index": idx + 1,
            "question": q,
            "response": result["answer"],
            "expected_tool": expected_tool,
            "actual_tools": [tc["tool_name"] for tc in tool_calls],
            "status": status,
            "model_used": metadata["model_used"]
        })
        
    summary = {
        "total_evaluated": len(questions),
        "correct": correct_count,
        "accuracy": f"{round((correct_count / len(questions)) * 100, 2)}%"
    }
    
    return {
        "summary": summary,
        "detailed_runs": evaluation_runs
    }

if __name__ == "__main__":
    res = run_evaluation()
    print(f"Accuracy: {res['summary']['accuracy']}")

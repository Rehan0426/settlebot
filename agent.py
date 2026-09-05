import os
import requests
import json
import re
from tools import get_settlement, get_settlements_by_date, get_settlements_by_status, sum_settlements, resolve_relative_date

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = """You are SettleBot, a professional AI Settlement Q&A Agent for Razorpay Merchants.
You strictly adhere to the following rules:
- You NEVER state any specific numbers (amounts, fees, GST, refund amounts, UTR numbers) unless they came from an actual tool call result in this conversation.
- If a tool returns not-found or is empty, say so explicitly. Do not guess or fabricate a plausible answer.
- You must resolve relative date phrases via the `resolve_relative_date` tool BEFORE calling any date-based tools (`get_settlements_by_date`, `sum_settlements`). Never perform date arithmetic yourself.
- Use conversation memory to resolve pronouns ("iska", "that one", "same transaction"), but always verify details by making a fresh tool call.
- If a question or date reference is ambiguous (like 'kal' or 'parso' without clear past/future context), ask for clarification rather than assuming.
- Keep conversation helpful and professional. Explain fee/GST/refund breakdowns clearly, avoiding jargon.
- If the user asks in Hinglish, respond in natural Hinglish but format amounts in standard Indian format (e.g. ₹1,50,000).
- The user is a business merchant, not a developer. NEVER mention tool names, function calls, API responses, JSON, or internal field names in your reply.
- NEVER show formulas, equations, or step-by-step arithmetic (e.g. "₹500 × 18% = ₹90" or "sum of 3 records"). State only the final figures in plain language, e.g. "Total GST deducted on 24 Aug 2026 was ₹90 across 3 settlements."
- Do not describe how you found the answer (e.g. "I checked the settlement data"). Just give the answer directly.
"""

# Merchant-facing messages for each error category. Keys are stable codes
# returned in the API response so the UI (or logs) can distinguish them.
ERROR_MESSAGES = {
    "quota_exceeded": "SettleBot has reached its AI usage quota for now. Please wait a minute and try again.",
    "auth_error": "SettleBot could not sign in to its AI service. Please ask your administrator to check the API key configuration.",
    "not_configured": "SettleBot is not set up yet. An administrator needs to add an AI API key (GEMINI_API_KEY or GROQ_API_KEY) before it can answer questions.",
    "timeout": "That took longer than expected and timed out. Please try again in a moment.",
    "network_error": "SettleBot could not reach its AI service. Please check the internet connection and try again.",
    "service_unavailable": "The AI service is temporarily unavailable. Please try again in a few minutes.",
    "bad_request": "SettleBot couldn't process that request. Please try rephrasing your question.",
    "no_answer": "I couldn't put together a complete answer for that. Could you rephrase or narrow down your question?",
    "unknown_error": "Something went wrong while processing your request. Please try again.",
}

TOOLS_SCHEMA = [
    {
        "name": "get_settlement",
        "description": "Fetch a single settlement record by its transaction_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "The transaction ID (e.g. pay_tx_100001)."}
            },
            "required": ["transaction_id"]
        }
    },
    {
        "name": "get_settlements_by_date",
        "description": "Fetch all settlement records for a concrete order date (YYYY-MM-DD).",
        "parameters": {
            "type": "object",
            "properties": {
                "date_str": {"type": "string", "description": "The concrete order date in YYYY-MM-DD format."}
            },
            "required": ["date_str"]
        }
    },
    {
        "name": "get_settlements_by_status",
        "description": "Fetch all settlement records filtered by status: settled, pending, or on_hold.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "The settlement status: settled, pending, or on_hold."}
            },
            "required": ["status"]
        }
    },
    {
        "name": "sum_settlements",
        "description": "Aggregate total settlement amount and count of settled transactions for a date range (inclusive).",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date_str": {"type": "string", "description": "The start date in YYYY-MM-DD format."},
                "end_date_str": {"type": "string", "description": "The end date in YYYY-MM-DD format."}
            },
            "required": ["start_date_str", "end_date_str"]
        }
    },
    {
        "name": "resolve_relative_date",
        "description": "Resolves relative date phrases (Hinglish/English) like 'yesterday', 'kal', 'parso', 'pichle mahine' into concrete date format.",
        "parameters": {
            "type": "object",
            "properties": {
                "phrase": {"type": "string", "description": "The relative phrase (e.g., 'kal', 'last week')."},
                "query": {"type": "string", "description": "The full user query/sentence to help detect grammatical tense hints."}
            },
            "required": ["phrase", "query"]
        }
    }
]

def to_gemini_function_declarations(tools):
    declarations = []
    for tool in tools:
        props = {}
        for k, v in tool["parameters"]["properties"].items():
            props[k] = {"type": "STRING", "description": v["description"]}
        declarations.append({
            "name": tool["name"],
            "description": tool["description"],
            "parameters": {
                "type": "OBJECT",
                "properties": props,
                "required": tool["parameters"]["required"]
            }
        })
    return [{"function_declarations": declarations}]

def to_groq_openai_tools(tools):
    openai_tools = []
    for tool in tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
        })
    return openai_tools

def call_tool(name, args):
    if name == "get_settlement":
        return get_settlement(args.get("transaction_id", ""))
    elif name == "get_settlements_by_date":
        return get_settlements_by_date(args.get("date_str", ""))
    elif name == "get_settlements_by_status":
        return get_settlements_by_status(args.get("status", ""))
    elif name == "sum_settlements":
        return sum_settlements(args.get("start_date_str", ""), args.get("end_date_str", ""))
    elif name == "resolve_relative_date":
        return resolve_relative_date(args.get("phrase", ""), query=args.get("query", ""))
    return {"error": "unknown_tool"}

def ask_gemini(messages, tool_declarations):
    # This sandbox proxy environment supports the following Gemini models
    models = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.8-flash", "gemini-3.7-flash"]
    last_error = None
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        contents = []
        for msg in messages:
            contents.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg.get("text", "")}]
            })
        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "tools": tool_declarations
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_error = e
            print(f"Gemini model {model_name} failed or rate-limited. Error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Gemini {model_name} error response body:", e.response.text)
            print(f"Proceeding to check alternative Gemini model in the sandbox proxy...")
    # Re-raise the real underlying error so the caller can classify it
    # (quota exceeded, auth failure, network issue, etc.).
    if last_error is not None:
        raise last_error
    raise Exception("All supported Gemini models in the sandbox proxy have failed.")

def ask_groq(messages, openai_tools):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        groq_messages.append({"role": m["role"], "content": m.get("text", "")})
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": groq_messages,
        "tools": openai_tools,
        "tool_choice": "auto"
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Groq llama-3.1-8b-instant failed: {str(e)}.")
        if hasattr(e, 'response') and e.response is not None:
            print("Groq response error details:", e.response.text)
        raise e

def classify_error(e):
    """Map a raw exception from an LLM/tool call to a stable error code.

    The code is looked up in ERROR_MESSAGES to produce a merchant-friendly
    message; the raw exception is only ever printed to server logs.
    """
    status = None
    resp = getattr(e, "response", None)
    if resp is not None:
        status = getattr(resp, "status_code", None)

    text = str(e).lower()
    if resp is not None:
        try:
            text += " " + (resp.text or "").lower()
        except Exception:
            pass

    if isinstance(e, requests.exceptions.Timeout) or "timed out" in text:
        return "timeout"
    if isinstance(e, requests.exceptions.ConnectionError) or "name resolution" in text or "connection refused" in text:
        return "network_error"
    if status == 429 or "quota" in text or "rate limit" in text or "rate_limit" in text or "resource_exhausted" in text:
        return "quota_exceeded"
    if status in (401, 403) or "api key" in text or "api_key" in text or "unauthorized" in text or "permission_denied" in text:
        return "auth_error"
    if status is not None and status >= 500:
        return "service_unavailable"
    if status == 400:
        return "bad_request"
    return "unknown_error"

def build_error_response(code, tool_calls_made, model_used):
    return {
        "answer": ERROR_MESSAGES.get(code, ERROR_MESSAGES["unknown_error"]),
        "error": code,
        "metadata": {
            "tool_calls_made": tool_calls_made,
            "grounding_status": "error",
            "model_used": model_used
        }
    }

def run_agent_turn(query, session_memory):
    messages = list(session_memory.history)
    messages.append({"role": "user", "text": query})
    tool_calls_made = []
    grounding_status = "verified"
    model_used = "gemini-3.6-flash"
    response_text = ""
    error_code = None
    gemini_funcs = to_gemini_function_declarations(TOOLS_SCHEMA)
    openai_tools = to_groq_openai_tools(TOOLS_SCHEMA)

    if not GEMINI_API_KEY and not GROQ_API_KEY:
        return build_error_response("not_configured", tool_calls_made, None)

    use_groq = False
    if not GEMINI_API_KEY:
        use_groq = True
        model_used = "groq/llama-3.1-8b-instant"

    max_iterations = 4
    for iteration in range(max_iterations):
        try:
            if not use_groq:
                res = ask_gemini(messages, gemini_funcs)
                candidates = res.get("candidates", [])
                if not candidates:
                    raise Exception("No candidates returned from Gemini")
                part = candidates[0]["content"]["parts"][0]
                if "functionCall" in part:
                    fn_call = part["functionCall"]
                    fn_name = fn_call["name"]
                    fn_args = fn_call["args"]
                    tool_calls_made.append({"tool_name": fn_name, "arguments": fn_args})
                    tool_result = call_tool(fn_name, fn_args)
                    tool_calls_made[-1]["result_summary"] = tool_result
                    if fn_name == "get_settlement" and tool_result.get("found"):
                        session_memory.update_slots(transaction_id=fn_args.get("transaction_id"))
                    elif fn_name == "resolve_relative_date" and tool_result.get("resolved"):
                        session_memory.update_slots(date_range=tool_result)
                    messages.append({"role": "assistant", "text": f"Calling tool {fn_name}"})
                    messages.append({"role": "user", "text": f"Tool response: {json.dumps(tool_result)}"})
                else:
                    response_text = part.get("text", "")
                    break
            else:
                res = ask_groq(messages, openai_tools)
                choice = res["choices"][0]
                msg = choice["message"]
                if "tool_calls" in msg and msg["tool_calls"]:
                    tc = msg["tool_calls"][0]
                    fn_name = tc["function"]["name"]
                    fn_args = json.loads(tc["function"]["arguments"])
                    tool_calls_made.append({"tool_name": fn_name, "arguments": fn_args})
                    tool_result = call_tool(fn_name, fn_args)
                    tool_calls_made[-1]["result_summary"] = tool_result
                    if fn_name == "get_settlement" and tool_result.get("found"):
                        session_memory.update_slots(transaction_id=fn_args.get("transaction_id"))
                    elif fn_name == "resolve_relative_date" and tool_result.get("resolved"):
                        session_memory.update_slots(date_range=tool_result)
                    messages.append({"role": "assistant", "text": f"Calling tool {fn_name}"})
                    messages.append({"role": "user", "text": f"Tool response: {json.dumps(tool_result)}"})
                else:
                    response_text = msg.get("content", "") or ""
                    break
        except Exception as e:
            print(f"Error on model iteration: {str(e)}")
            code = classify_error(e)
            # If Gemini failed (quota, auth, outage...) and Groq is configured, fall back once.
            if not use_groq and GROQ_API_KEY:
                print(f"Gemini failed with '{code}'. Switching to Groq fallback pathway...")
                use_groq = True
                model_used = "groq/llama-3.1-8b-instant"
                continue
            error_code = code
            break

    if error_code:
        # Do not store failed turns in memory so they don't pollute later context.
        return build_error_response(error_code, tool_calls_made, model_used)

    if not response_text.strip():
        # The model kept calling tools and never produced a final answer.
        return build_error_response("no_answer", tool_calls_made, model_used)

    if "No record found" in response_text or "not found" in response_text.lower():
        grounding_status = "not_found"
    elif "matlab" in response_text or "ya kal" in response_text:
        grounding_status = "clarification_needed"
    else:
        grounding_status = "verified"

    session_memory.add_turn(query, response_text)
    return {
        "answer": response_text,
        "error": None,
        "metadata": {
            "tool_calls_made": tool_calls_made,
            "grounding_status": grounding_status,
            "model_used": model_used
        }
    }

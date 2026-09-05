import os
import requests
import json
import re

# Load API keys from a local .env file if python-dotenv is available.
# Environment variables that are already set always take precedence.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from tools import get_settlement, get_settlements_by_date, get_settlements_by_status, sum_settlements, resolve_relative_date

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Primary provider. This sandbox proxy environment supports these Gemini models, tried in order.
GEMINI_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.8-flash", "gemini-3.7-flash"]

# Fallback provider (Groq), used only when every Gemini model fails or no Gemini key is set.
# Models are tried in order. Override without code changes via a comma-separated env var:
#   GROQ_MODELS="openai/gpt-oss-120b,qwen/qwen3.8-27b"
DEFAULT_GROQ_MODELS = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"]
GROQ_MODELS = [m.strip() for m in os.environ.get("GROQ_MODELS", "").split(",") if m.strip()] or DEFAULT_GROQ_MODELS

PROVIDER_GEMINI = "Google Gemini"
PROVIDER_GROQ = "Groq"

SYSTEM_PROMPT = """You are SettleBot, a professional AI Settlement Q&A Agent for Razorpay Merchants.
You strictly adhere to the following rules:
- You NEVER state any specific numbers (amounts, fees, GST, refund amounts, UTR numbers) unless they came from an actual tool call result in this conversation.
- If a tool returns not-found or is empty, say so explicitly. Do not guess or fabricate a plausible answer.
- You must resolve any date or period phrase via the `resolve_relative_date` tool BEFORE calling date-based tools (`get_settlements_by_date`, `sum_settlements`). Never perform date arithmetic yourself.
- Pass the ENTIRE period phrase exactly as the user wrote it to `resolve_relative_date` (e.g. 'last financial year', '2025 fiscal year', 'FY 2024-25', 'Q2 2025', 'last quarter', 'last 3 months', 'March 2026', 'next week', 'pichle mahine', '2025'). The tool understands Indian financial years (April to March), quarters, month names, calendar years, rolling windows, weekdays, explicit dates and 'X to Y' ranges, in English and Hinglish.
- NEVER ask the user to provide specific dates or a date range when they have used any such phrase. Only ask for clarification if `resolve_relative_date` itself reports the phrase as ambiguous (e.g. 'kal'/'parso' with no tense hint) or unsupported.
- When the tool returns a range, call `sum_settlements` with its start_date and end_date. When it returns a single date, call `get_settlements_by_date`.
- In your answer, state the period you covered in plain words using the tool's label (e.g. 'for FY 2024-25 (1 Apr 2024 to 31 Mar 2025)') so the merchant knows exactly which dates were included.
- Use conversation memory to resolve pronouns ("iska", "that one", "same transaction"), but always verify details by making a fresh tool call.
- Keep conversation helpful and professional. Explain fee/GST/refund breakdowns clearly, avoiding jargon.
- If the user asks in Hinglish, respond in natural Hinglish but format amounts in standard Indian format (e.g. ₹1,50,000).
- The user is a business merchant, not a developer. NEVER mention tool names, function calls, API responses, JSON, or internal field names in your reply.
- NEVER show formulas, equations, or step-by-step arithmetic (e.g. "₹500 × 18% = ₹90" or "sum of 3 records"). State only the final figures in plain language, e.g. "Total GST deducted on 24 Aug 2026 was ₹90 across 3 settlements."
- Do not describe how you found the answer (e.g. "I checked the settlement data"). Just give the answer directly.
- FORMATTING: when an answer contains two or more figures (e.g. gross amount, fees, GST, refunds, net settlement, or several transactions), present them as a markdown table so they are easy to scan. For a settlement summary or breakdown use exactly two columns `| Item | Amount |`, one row per figure, with the Net / Total row LAST. For several transactions use columns such as `| Transaction | Date | Status | Amount |`. Write one short sentence before the table saying what period or transaction it covers. Do not repeat the figures again in prose after the table. Use a plain sentence (no table) when there is only one figure.
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
        "description": "Resolves any natural-language date or period phrase (English or Hinglish) into concrete dates. Handles: today/yesterday/kal/parso; last/this/next week, month, quarter, year; Indian financial years such as 'last financial year', 'FY 2024-25', 'FY25', '2025 fiscal year', 'FYTD'; quarters such as 'Q2 2025', 'Q1 FY25', 'last quarter'; month names such as 'March 2026', 'last January'; rolling windows such as 'last 3 months', 'past 30 days', '2 weeks ago'; weekdays such as 'last Friday'; explicit dates such as '24 Aug 2026' or '24/08/2026'; ranges such as '1 Aug to 15 Aug'; and bare years such as '2025'. Always call this instead of asking the user for exact dates.",
        "parameters": {
            "type": "object",
            "properties": {
                "phrase": {"type": "string", "description": "The complete date/period phrase exactly as the user wrote it (e.g. 'last financial year', 'Q2 2025', 'last 3 months', 'kal')."},
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
    """Call Gemini, falling through the supported model list. Returns (json, model_name)."""
    last_error = None
    for model_name in GEMINI_MODELS:
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
            return resp.json(), model_name
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
    """Call Groq, falling through GROQ_MODELS in order. Returns (json, model_name)."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        groq_messages.append({"role": m["role"], "content": m.get("text", "")})

    last_error = None
    for model_name in GROQ_MODELS:
        payload = {
            "model": model_name,
            "messages": groq_messages,
            "tools": openai_tools,
            "tool_choice": "auto"
        }
        try:
            # Larger models such as gpt-oss-120b can take longer than the Gemini path.
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("choices"):
                raise Exception(f"Groq {model_name} returned no choices")
            return data, model_name
        except Exception as e:
            last_error = e
            print(f"Groq model {model_name} failed: {str(e)}")
            resp_obj = getattr(e, "response", None)
            if resp_obj is not None:
                print(f"Groq {model_name} error response body:", resp_obj.text)
                # A bad key fails for every model; don't burn calls on the rest.
                if getattr(resp_obj, "status_code", None) in (401, 403):
                    break
            print("Trying next Groq model...")
    # Re-raise the real underlying error so the caller can classify it.
    if last_error is not None:
        raise last_error
    raise Exception("All configured Groq models failed.")

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

def build_error_response(code, tool_calls_made, model_used, model_provider=None):
    return {
        "answer": ERROR_MESSAGES.get(code, ERROR_MESSAGES["unknown_error"]),
        "error": code,
        "metadata": {
            "tool_calls_made": tool_calls_made,
            "grounding_status": "error",
            "model_used": model_used,
            "model_provider": model_provider
        }
    }

def run_agent_turn(query, session_memory):
    messages = list(session_memory.history)
    messages.append({"role": "user", "text": query})
    tool_calls_made = []
    grounding_status = "verified"
    # Filled in with the model that actually produced the answer.
    model_used = None
    model_provider = None
    response_text = ""
    error_code = None
    gemini_funcs = to_gemini_function_declarations(TOOLS_SCHEMA)
    openai_tools = to_groq_openai_tools(TOOLS_SCHEMA)

    if not GEMINI_API_KEY and not GROQ_API_KEY:
        return build_error_response("not_configured", tool_calls_made, None)

    use_groq = False
    if not GEMINI_API_KEY:
        use_groq = True
        model_provider = PROVIDER_GROQ

    max_iterations = 4
    for iteration in range(max_iterations):
        try:
            if not use_groq:
                res, model_used = ask_gemini(messages, gemini_funcs)
                model_provider = PROVIDER_GEMINI
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
                res, model_used = ask_groq(messages, openai_tools)
                model_provider = PROVIDER_GROQ
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
                    # Reasoning models (e.g. Qwen) may wrap their thinking in <think> tags.
                    response_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.S).strip()
                    break
        except Exception as e:
            print(f"Error on model iteration: {str(e)}")
            code = classify_error(e)
            # If Gemini failed (quota, auth, outage...) and Groq is configured, fall back once.
            if not use_groq and GROQ_API_KEY:
                print(f"Gemini failed with '{code}'. Switching to Groq fallback pathway...")
                use_groq = True
                model_used = None
                model_provider = PROVIDER_GROQ
                continue
            error_code = code
            break

    if error_code:
        # Do not store failed turns in memory so they don't pollute later context.
        return build_error_response(error_code, tool_calls_made, model_used, model_provider)

    if not response_text.strip():
        # The model kept calling tools and never produced a final answer.
        return build_error_response("no_answer", tool_calls_made, model_used, model_provider)

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
            "model_used": model_used,
            "model_provider": model_provider
        }
    }

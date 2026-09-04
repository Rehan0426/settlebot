import csv
import re
from datetime import datetime, timedelta

DATA_FILE = "settlements.csv"

def get_settlements_db():
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        import generate_data
        generate_data.generate_synthetic_data()
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

def get_settlement(transaction_id):
    db = get_settlements_db()
    for row in db:
        if row["transaction_id"] == transaction_id:
            return {"found": True, "record": row}
    return {"found": False, "reason": "no_matching_records"}

def get_settlements_by_date(date_str):
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if target_date > datetime.now().date():
            return {"found": False, "reason": "future_date"}
    except ValueError:
        return {"found": False, "reason": "invalid_date_format"}

    db = get_settlements_db()
    results = [row for row in db if row["order_date"] == date_str]
    if results:
        return {"found": True, "records": results}
    return {"found": False, "reason": "no_matching_records"}

def get_settlements_by_status(status):
    status = status.lower().strip()
    db = get_settlements_db()
    results = [row for row in db if row["settlement_status"] == status]
    if results:
        return {"found": True, "records": results}
    return {"found": False, "reason": "no_matching_records"}

def sum_settlements(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        if start_date > datetime.now().date() and end_date > datetime.now().date():
            return {"found": False, "reason": "future_date"}
    except ValueError:
        return {"found": False, "reason": "invalid_date_format"}

    db = get_settlements_db()
    total_amount = 0.0
    count = 0
    records = []
    
    for row in db:
        try:
            o_date = datetime.strptime(row["order_date"], "%Y-%m-%d").date()
            if start_date <= o_date <= end_date:
                records.append(row)
                if row["settlement_status"] == "settled":
                    total_amount += float(row["settlement_amount"])
                    count += 1
        except ValueError:
            continue
            
    if records:
        return {
            "found": True,
            "total_settlement_amount": round(total_amount, 2),
            "settled_transactions_count": count,
            "records_count": len(records)
        }
    return {"found": False, "reason": "no_matching_records"}

def resolve_relative_date(phrase, reference_date_str=None, query=""):
    if not reference_date_str:
        ref_date = datetime.now().date()
    else:
        ref_date = datetime.strptime(reference_date_str, "%Y-%m-%d").date()
        
    phrase = phrase.lower().strip()
    query = query.lower()
    
    past_cues = ["hua", "tha", "gaya", "mila", "pay", "last", "deducted", "kata", "bita", "bithaya", "received", "delayed", "kyu nahi"]
    future_cues = ["hoga", "aayega", "milega", "karega", "next", "schedule", "will", "shall", "bhejoge"]
    
    has_past_cues = any(cue in query for cue in past_cues)
    has_future_cues = any(cue in query for cue in future_cues)
    
    if phrase in ["today", "aaj"]:
        concrete = ref_date.strftime("%Y-%m-%d")
        return {"resolved": True, "type": "single", "date": concrete, "confirmation": f"{phrase} -> {concrete}"}
        
    elif phrase in ["yesterday"]:
        concrete = (ref_date - timedelta(days=1)).strftime("%Y-%m-%d")
        return {"resolved": True, "type": "single", "date": concrete, "confirmation": f"yesterday -> {concrete}"}
        
    elif phrase in ["day before yesterday"]:
        concrete = (ref_date - timedelta(days=2)).strftime("%Y-%m-%d")
        return {"resolved": True, "type": "single", "date": concrete, "confirmation": f"day before yesterday -> {concrete}"}
        
    elif phrase in ["tomorrow"]:
        concrete = (ref_date + timedelta(days=1)).strftime("%Y-%m-%d")
        return {"resolved": True, "type": "single", "date": concrete, "confirmation": f"tomorrow -> {concrete}"}
        
    elif phrase == "kal":
        if has_past_cues and not has_future_cues:
            concrete = (ref_date - timedelta(days=1)).strftime("%Y-%m-%d")
            return {"resolved": True, "type": "single", "date": concrete, "confirmation": f"kal (yesterday) -> {concrete}"}
        elif has_future_cues and not has_past_cues:
            concrete = (ref_date + timedelta(days=1)).strftime("%Y-%m-%d")
            return {"resolved": True, "type": "single", "date": concrete, "confirmation": f"kal (tomorrow) -> {concrete}"}
        else:
            return {"resolved": False, "ambiguous": True, "message": "Kal se aapka matlab kal (bīta din) ya kal (aane wala din)?"}
            
    elif phrase == "parso":
        if has_past_cues and not has_future_cues:
            concrete = (ref_date - timedelta(days=2)).strftime("%Y-%m-%d")
            return {"resolved": True, "type": "single", "date": concrete, "confirmation": f"parso (day before yesterday) -> {concrete}"}
        elif has_future_cues and not has_past_cues:
            concrete = (ref_date + timedelta(days=2)).strftime("%Y-%m-%d")
            return {"resolved": True, "type": "single", "date": concrete, "confirmation": f"parso (day after tomorrow) -> {concrete}"}
        else:
            return {"resolved": False, "ambiguous": True, "message": "Parso se aapka matlab parso (bīta din) ya parso (aane wala din)?"}
            
    elif phrase in ["this week", "is hafte"]:
        start = ref_date - timedelta(days=ref_date.weekday())
        end = start + timedelta(days=6)
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    elif phrase in ["last week", "pichle hafte"]:
        start = ref_date - timedelta(days=ref_date.weekday() + 7)
        end = start + timedelta(days=6)
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    elif phrase in ["next week", "agle hafte"]:
        start = ref_date - timedelta(days=ref_date.weekday() - 7)
        end = start + timedelta(days=6)
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    elif phrase in ["this month", "is mahine"]:
        start = ref_date.replace(day=1)
        if start.month == 12:
            end = datetime(start.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end = datetime(start.year, start.month + 1, 1).date() - timedelta(days=1)
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    elif phrase in ["last month", "pichle mahine"]:
        first_of_this_month = ref_date.replace(day=1)
        end = first_of_this_month - timedelta(days=1)
        start = end.replace(day=1)
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    elif phrase in ["next month", "agle mahine"]:
        if ref_date.month == 12:
            start = datetime(ref_date.year + 1, 1, 1).date()
        else:
            start = datetime(ref_date.year, ref_date.month + 1, 1).date()
        if start.month == 12:
            end = datetime(start.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end = datetime(start.year, start.month + 1, 1).date() - timedelta(days=1)
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    elif phrase in ["this year", "is saal"]:
        start = datetime(ref_date.year, 1, 1).date()
        end = datetime(ref_date.year, 12, 31).date()
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    elif phrase in ["last year", "pichle saal"]:
        start = datetime(ref_date.year - 1, 1, 1).date()
        end = datetime(ref_date.year - 1, 12, 31).date()
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    elif phrase in ["next year", "agle saal"]:
        start = datetime(ref_date.year + 1, 1, 1).date()
        end = datetime(ref_date.year + 1, 12, 31).date()
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    match = re.search(r'(?:last|pichle)\s+(\d+)\s+(?:days|din)', phrase)
    if match:
        days = int(match.group(1))
        start = ref_date - timedelta(days=days)
        end = ref_date
        return {"resolved": True, "type": "range", "start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d"), "confirmation": f"{phrase} -> {start} to {end}"}
        
    return {"resolved": False, "reason": "unsupported_phrase"}

import csv
import re
from datetime import datetime, timedelta, date

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


# ---------------------------------------------------------------------------
# Natural-language date resolution
# ---------------------------------------------------------------------------

# Indian financial year runs 1 April to 31 March. "FY25" / "FY 2025" follows the
# common Indian convention and means the year ENDING 31 March 2025 (FY 2024-25).
# A two-part form like "FY 2025-26" is always taken literally.
FY_START_MONTH = 4

MONTH_NAMES = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
}
MONTH_REGEX = "|".join(sorted(MONTH_NAMES.keys(), key=len, reverse=True))

WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
    "mon": 0, "tue": 1, "tues": 1, "wed": 2, "thu": 3, "thur": 3, "thurs": 3, "fri": 4, "sat": 5, "sun": 6,
}
WEEKDAY_REGEX = "|".join(sorted(WEEKDAYS.keys(), key=len, reverse=True))

WORD_NUMBERS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "couple": 2, "few": 3,
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5, "panch": 5, "chhe": 6, "che": 6,
    "saat": 7, "aath": 8, "nau": 9, "das": 10,
}

# Ordered list of (pattern, replacement) applied to lower-cased text. Maps
# Hinglish words and English variants onto a small canonical vocabulary so the
# matchers below only need to know: last / this / next, week / month / quarter /
# year / financial year / days, today / kal / parso, ago, to, to date.
_SYNONYMS = [
    # Hinglish
    (r"\b(pichhle|pichle|pichhla|pichla|pichli|peechle|peechhe|gaye|guzre|guzra|beete|beeta|bite|bita)\b", "last"),
    (r"\b(agle|agla|agli|aglaa|aane\s+wal[ae]|aanewal[ae])\b", "next"),
    (r"\b(is|iss|isi|ye|yeh|yah|chalu)\b", "this"),
    (r"\b(hafte|hafta|haftey|haftaa|hafton|saptah)\b", "week"),
    (r"\b(mahine|mahina|maheene|maheena|mahino|maheeno|mahinon)\b", "month"),
    (r"\b(vitt|vittiya|vitiya|arthik)\s+(varsh|saal|year)\b", "financial year"),
    (r"\b(saal|varsh|baras|salo|saalo|saalon)\b", "year"),
    (r"\b(din|dino|dinon)\b", "days"),
    (r"\b(timahi|tirmahi|trimaas)\b", "quarter"),
    (r"\b(aaj|aj)\b", "today"),
    (r"\b(abhi\s+tak|ab\s+tak|today\s+tak)\b", "to date"),
    (r"\bpehle\b", "ago"),
    (r"\bse\b", "to"),
    # English variants
    (r"\b(previous|preceding|past|prior)\b", "last"),
    (r"\b(current|present|ongoing|running)\b", "this"),
    (r"\b(coming|upcoming|following|forthcoming)\b", "next"),
    (r"\b(yr|yrs)\b", "year"),
    (r"\b(wk|wks)\b", "week"),
    (r"\b(mth|mths|mnth)\b", "month"),
    (r"\b(qtr|qtrs)\b", "quarter"),
    (r"\bfy(\d)", r"financial year \1"),
    (r"\bf\s?y\b", "financial year"),
    (r"\b(fiscal|financial|fin)(\s+(year|yr))?\b", "financial year"),
    (r"\b(first|1st)\s+quarter\b", "q1"),
    (r"\b(second|2nd)\s+quarter\b", "q2"),
    (r"\b(third|3rd)\s+quarter\b", "q3"),
    (r"\b(fourth|4th)\s+quarter\b", "q4"),
    (r"\bbetween\s+(.+?)\s+and\b", r"\1 to"),
    (r"\b(till|until|through|upto|up\s+to)\b", "to"),
    (r"\b(so\s+far|to\s+now|to\s+today|to\s+date|year\s+to\s+date)\b", "to date"),
    (r"\b(recent|recently|lately)\b", "last 7 days"),
]

_FILLERS = r"\b(the|in|for|during|of|on|from|at|ka|ki|ke|ko|me|mein|main|wala|wale|wali|tak|period|time|duration)\b"

PAST_CUES = ["hua", "tha", "thi", "the", "hue", "gaya", "mila", "paid", "last", "deducted", "kata", "bita",
             "received", "delayed", "kyu nahi", "settled", "was", "were", "did", "pichle", "pichla"]
FUTURE_CUES = ["hoga", "honge", "aayega", "aayenge", "milega", "milenge", "karega", "next", "schedule",
               "will", "shall", "bhejoge", "upcoming", "coming", "expected", "agle", "agla"]


def _fmt(d):
    return d.strftime("%Y-%m-%d")

def _human(d):
    return f"{d.day} {d.strftime('%b %Y')}"

def _parse_iso(s):
    return datetime.strptime(s, "%Y-%m-%d").date()

def _single(label, d, kind="single"):
    return {
        "resolved": True, "type": "single", "kind": kind,
        "date": _fmt(d),
        "label": f"{label} ({_human(d)})",
        "confirmation": f"{label} -> {_fmt(d)}",
    }

def _range(label, start, end, kind="range"):
    return {
        "resolved": True, "type": "range", "kind": kind,
        "start_date": _fmt(start), "end_date": _fmt(end),
        "label": f"{label} ({_human(start)} to {_human(end)})",
        "confirmation": f"{label} -> {_fmt(start)} to {_fmt(end)}",
    }

def _days_in_month(y, m):
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return (date(ny, nm, 1) - timedelta(days=1)).day

def _month_bounds(y, m):
    return date(y, m, 1), date(y, m, _days_in_month(y, m))

def _shift_month(y, m, delta):
    idx = y * 12 + (m - 1) + delta
    return idx // 12, idx % 12 + 1

def _shift_months_from(d, delta):
    y, m = _shift_month(d.year, d.month, delta)
    return date(y, m, min(d.day, _days_in_month(y, m)))

def _shift_years_from(d, delta):
    y = d.year + delta
    return date(y, d.month, min(d.day, _days_in_month(y, d.month)))

def _week_bounds(d):
    start = d - timedelta(days=d.weekday())
    return start, start + timedelta(days=6)

def _quarter_index(d):
    return (d.month - 1) // 3

def _quarter_bounds_from(y, qi):
    """Calendar quarter bounds. qi may be negative or > 3 and is normalised."""
    total = y * 4 + qi
    y, qi = total // 4, total % 4
    sm = qi * 3 + 1
    start = date(y, sm, 1)
    _, end = _month_bounds(y, sm + 2)
    return start, end

def _fy_start_year(d):
    return d.year if d.month >= FY_START_MONTH else d.year - 1

def _fy_bounds(start_year):
    return date(start_year, FY_START_MONTH, 1), date(start_year + 1, FY_START_MONTH, 1) - timedelta(days=1)

def _fy_label(start_year):
    return f"FY {start_year}-{str(start_year + 1)[-2:]}"

def _fiscal_quarter_bounds(fy_start_year, q):
    """Q1 = Apr-Jun, Q2 = Jul-Sep, Q3 = Oct-Dec, Q4 = Jan-Mar."""
    y, m = _shift_month(fy_start_year, FY_START_MONTH, 3 * (q - 1))
    start = date(y, m, 1)
    ey, em = _shift_month(y, m, 2)
    _, end = _month_bounds(ey, em)
    return start, end

def _expand_year(s):
    n = int(s)
    return n + 2000 if n < 100 else n

def _safe_date(y, m, d):
    try:
        return date(y, m, d)
    except ValueError:
        return None

def _period_start(unit, ref):
    if unit == "week":
        return _week_bounds(ref)[0]
    if unit == "month":
        return ref.replace(day=1)
    if unit == "quarter":
        return _quarter_bounds_from(ref.year, _quarter_index(ref))[0]
    if unit == "year":
        return date(ref.year, 1, 1)
    return _fy_bounds(_fy_start_year(ref))[0]


def _normalize_date_phrase(text):
    p = (text or "").lower()
    p = re.sub(r"[?!.,;:'\"()]", " ", p)
    for pattern, repl in _SYNONYMS:
        p = re.sub(pattern, repl, p)
    p = re.sub(_FILLERS, " ", p)
    p = re.sub(
        rf"\b({'|'.join(WORD_NUMBERS)})\s+(?=(financial year|year|quarter|month|week|day)s?\b)",
        lambda m: f"{WORD_NUMBERS[m.group(1)]} ",
        p,
    )
    p = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", p)
    return re.sub(r"\s+", " ", p).strip()


def _parse_explicit_date(p, ref, future):
    m = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", p)
    if m:
        return _safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", p)
    if m:
        return _safe_date(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    m = re.search(rf"\b(\d{{1,2}})\s+({MONTH_REGEX})\b(?:\s+(\d{{4}})\b)?", p)
    if m:
        day, mon, year = int(m.group(1)), MONTH_NAMES[m.group(2)], m.group(3)
    else:
        m = re.search(rf"\b({MONTH_REGEX})\s+(\d{{1,2}})\b(?!\s*[-/]?\d)(?:\s*(\d{{4}})\b)?", p)
        if not m:
            return None
        day, mon, year = int(m.group(2)), MONTH_NAMES[m.group(1)], m.group(3)

    if year:
        return _safe_date(int(year), mon, day)
    d = _safe_date(ref.year, mon, day)
    if d and d > ref and not future:
        d = _safe_date(ref.year - 1, mon, day)
    return d


def _resolve_normalized(p, ref, past, future, from_query=False):
    if not p:
        return None

    # 0. "X to Y" ranges: resolve each side independently.
    if "to date" not in p:
        parts = re.split(r"\s+(?:to|-|\u2013)\s+", p, maxsplit=1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            left = _resolve_normalized(parts[0].strip(), ref, past, future, from_query)
            right = _resolve_normalized(parts[1].strip(), ref, past, future, from_query)
            if left and right and left.get("resolved") and right.get("resolved"):
                start = _parse_iso(left.get("start_date") or left.get("date"))
                end = _parse_iso(right.get("end_date") or right.get("date"))
                if start <= end:
                    return _range(f"{parts[0].strip()} to {parts[1].strip()}", start, end, kind="custom_range")

    # 1. Day words.
    for pattern, delta, label in [
        (r"\bday\s+before\s+yesterday\b", -2, "day before yesterday"),
        (r"\bday\s+after\s+tomorrow\b", 2, "day after tomorrow"),
        (r"\byesterday\b", -1, "yesterday"),
        (r"\btomorrow\b", 1, "tomorrow"),
        (r"\btoday\b", 0, "today"),
    ]:
        if re.search(pattern, p):
            return _single(label, ref + timedelta(days=delta), kind="day")

    for word, n, back, fwd in (("kal", 1, "yesterday", "tomorrow"), ("parso", 2, "day before yesterday", "day after tomorrow")):
        if re.search(rf"\b{word}\b", p):
            if past and not future:
                return _single(f"{word} ({back})", ref - timedelta(days=n), kind="day")
            if future and not past:
                return _single(f"{word} ({fwd})", ref + timedelta(days=n), kind="day")
            return {
                "resolved": False, "ambiguous": True,
                "message": f"{word.capitalize()} se aapka matlab {word} (b\u012bta din) ya {word} (aane wala din)?",
            }

    # 2. Period-to-date windows: YTD, FYTD, MTD, "this month so far".
    unit = None
    m = re.search(r"\b(fytd|ytd|qtd|mtd|wtd)\b", p)
    if m:
        unit = {"fytd": "financial year", "ytd": "year", "qtd": "quarter", "mtd": "month", "wtd": "week"}[m.group(1)]
    else:
        m = re.search(r"\b(?:this\s+)?(financial year|year|quarter|month|week)\s+to date\b", p)
        if m:
            unit = m.group(1)
        elif re.search(r"\bto date\b", p) and "financial year" in p:
            unit = "financial year"
    if unit:
        return _range(f"{unit} to date", _period_start(unit, ref), ref, kind="to_date")

    # 3. Named quarters: "q1 2025", "q2 financial year 2024-25", "q3".
    m = re.search(r"\bq([1-4])\b(?:\s*(financial year)?\s*(\d{2,4})\b(?:\s*[-/]\s*(\d{2,4})\b)?)?", p)
    if m:
        q = int(m.group(1))
        fiscal = bool(m.group(2)) or "financial year" in p
        if m.group(3):
            y1 = _expand_year(m.group(3))
            if fiscal:
                fy = y1 if m.group(4) else y1 - 1
                s, e = _fiscal_quarter_bounds(fy, q)
                return _range(f"Q{q} {_fy_label(fy)}", s, e, kind="fiscal_quarter")
            s, e = _quarter_bounds_from(y1, q - 1)
            return _range(f"Q{q} {y1}", s, e, kind="quarter")
        if fiscal:
            fy = _fy_start_year(ref)
            s, e = _fiscal_quarter_bounds(fy, q)
            return _range(f"Q{q} {_fy_label(fy)}", s, e, kind="fiscal_quarter")
        s, e = _quarter_bounds_from(ref.year, q - 1)
        return _range(f"Q{q} {ref.year}", s, e, kind="quarter")

    # 4. Financial years with explicit years: "financial year 2024-25", "fy25", "2025 fiscal year".
    m = re.search(r"financial year\s*(\d{2,4})\b(?:\s*[-/]\s*(\d{2,4})\b)?", p) or \
        re.search(r"\b(\d{4})\b(?:\s*[-/]\s*(\d{2,4})\b)?\s*financial year", p)
    if m:
        y1 = _expand_year(m.group(1))
        fy = y1 if m.group(2) else y1 - 1
        s, e = _fy_bounds(fy)
        return _range(_fy_label(fy), s, e, kind="financial_year")

    # 5. "2024-25" style year pair is a financial year.
    m = re.search(r"\b(\d{4})\s*[-/]\s*(\d{2}|\d{4})\b", p)
    if m:
        y1, y2 = int(m.group(1)), _expand_year(m.group(2))
        if y2 == y1 + 1:
            s, e = _fy_bounds(y1)
            return _range(_fy_label(y1), s, e, kind="financial_year")

    # 6. "last 2 financial years", "last 3 quarters" -> complete previous periods.
    m = re.search(r"\b(last|next)\s+(\d+)\s+(financial year|quarter)s?\b", p)
    if m:
        direction, n, unit = m.group(1), int(m.group(2)), m.group(3)
        if unit == "financial year":
            cur = _fy_start_year(ref)
            if direction == "last":
                s, _ = _fy_bounds(cur - n)
                _, e = _fy_bounds(cur - 1)
            else:
                s, _ = _fy_bounds(cur + 1)
                _, e = _fy_bounds(cur + n)
        else:
            qi = _quarter_index(ref)
            if direction == "last":
                s, _ = _quarter_bounds_from(ref.year, qi - n)
                _, e = _quarter_bounds_from(ref.year, qi - 1)
            else:
                s, _ = _quarter_bounds_from(ref.year, qi + 1)
                _, e = _quarter_bounds_from(ref.year, qi + n)
        return _range(f"{direction} {n} {unit}s", s, e, kind="multi_period")

    # 7. last / this / next financial year.
    m = re.search(r"\b(last|this|next)\s+financial year\b", p)
    if m:
        fy = _fy_start_year(ref) + {"last": -1, "this": 0, "next": 1}[m.group(1)]
        s, e = _fy_bounds(fy)
        return _range(f"{m.group(1)} financial year, {_fy_label(fy)}", s, e, kind="financial_year")

    # 8. last / this / next quarter (quarter boundaries are the same for calendar and FY).
    m = re.search(r"\b(last|this|next)\s+quarter\b", p)
    if m:
        qi = _quarter_index(ref) + {"last": -1, "this": 0, "next": 1}[m.group(1)]
        s, e = _quarter_bounds_from(ref.year, qi)
        return _range(f"{m.group(1)} quarter", s, e, kind="quarter")

    # 9. "N units ago".
    m = re.search(r"\b(\d+)\s+(day|week|month|year)s?\s+ago\b", p)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if unit == "day":
            return _single(f"{n} days ago", ref - timedelta(days=n), kind="day")
        if unit == "week":
            s, e = _week_bounds(ref - timedelta(weeks=n))
            return _range(f"{n} weeks ago", s, e, kind="week")
        if unit == "month":
            y, mo = _shift_month(ref.year, ref.month, -n)
            s, e = _month_bounds(y, mo)
            return _range(f"{n} months ago", s, e, kind="month")
        y = ref.year - n
        return _range(f"{n} years ago", date(y, 1, 1), date(y, 12, 31), kind="calendar_year")

    # 10. Rolling windows: "last 3 months", "last 30 days", "next 2 weeks".
    m = re.search(r"\b(last|next)\s+(\d+)\s+(day|week|month|year)s?\b", p)
    if m:
        direction, n, unit = m.group(1), int(m.group(2)), m.group(3)
        sign = -1 if direction == "last" else 1
        if unit == "day":
            other = ref + timedelta(days=sign * n)
        elif unit == "week":
            other = ref + timedelta(weeks=sign * n)
        elif unit == "month":
            other = _shift_months_from(ref, sign * n)
        else:
            other = _shift_years_from(ref, sign * n)
        s, e = (other, ref) if sign < 0 else (ref, other)
        return _range(f"{direction} {n} {unit}s", s, e, kind="rolling")

    # 11. Explicit dates: 2026-08-24, 24/08/2026, 24 aug 2026, aug 24 2026, 24 august.
    d = _parse_explicit_date(p, ref, future)
    if d:
        return _single("date", d, kind="day")

    # 12. Month names: "march 2026", "last january", "august".
    m = re.search(rf"\b(?:(last|this|next)\s+)?({MONTH_REGEX})\b(?:\s+(\d{{4}})\b)?", p)
    if m:
        mod, mon_word, year = m.group(1), m.group(2), m.group(3)
        mon = MONTH_NAMES[mon_word]
        # "may" and "mar" are also ordinary words; when scanning a whole question,
        # only accept them with a year or last/this/next qualifier.
        if not (from_query and mon_word in ("may", "mar") and not (mod or year)):
            if year:
                y = int(year)
            elif mod == "this":
                y = ref.year
            elif mod == "next":
                y = ref.year if mon > ref.month else ref.year + 1
            elif mod == "last":
                y = ref.year if mon < ref.month else ref.year - 1
            else:
                y = ref.year if mon <= ref.month else ref.year - 1
            s, e = _month_bounds(y, mon)
            return _range(s.strftime("%B %Y"), s, e, kind="month")

    # 13. last / this / next week, month, year.
    m = re.search(r"\b(last|this|next)\s+(week|month|year)\b", p)
    if m:
        mod, unit = m.group(1), m.group(2)
        delta = {"last": -1, "this": 0, "next": 1}[mod]
        if unit == "week":
            s, e = _week_bounds(ref + timedelta(weeks=delta))
        elif unit == "month":
            y, mo = _shift_month(ref.year, ref.month, delta)
            s, e = _month_bounds(y, mo)
        else:
            s, e = date(ref.year + delta, 1, 1), date(ref.year + delta, 12, 31)
        return _range(f"{mod} {unit}", s, e, kind=unit)

    # 14. Weekdays: "last friday", "this monday", "next tuesday", "monday".
    m = re.search(rf"\b(?:(last|this|next)\s+)?({WEEKDAY_REGEX})\b", p)
    if m and not (from_query and len(m.group(2)) <= 3 and not m.group(1)):
        mod, wd = m.group(1), WEEKDAYS[m.group(2)]
        if mod == "this":
            d = _week_bounds(ref)[0] + timedelta(days=wd)
        elif mod == "next":
            d = ref + timedelta(days=((wd - ref.weekday()) % 7) or 7)
        elif mod == "last":
            d = ref - timedelta(days=((ref.weekday() - wd) % 7) or 7)
        elif future and not past:
            d = ref + timedelta(days=((wd - ref.weekday()) % 7) or 7)
        else:
            d = ref - timedelta(days=(ref.weekday() - wd) % 7)
        return _single(f"{mod + ' ' if mod else ''}{m.group(2)}", d, kind="day")

    # 15. Bare calendar year: "2025", "year 2025".
    m = re.search(r"\b(?:calendar\s+year\s+|year\s+)?((?:19|20)\d{2})\b", p)
    if m:
        y = int(m.group(1))
        looks_like_amount = re.search(
            rf"(?:rs|inr|\u20b9|rupees?)\s*{y}\b|\b{y}\s*(?:rs|rupees|inr|/-|lakh|crore|k)\b", p)
        if 2000 <= y <= ref.year + 1 and not looks_like_amount:
            return _range(f"year {y}", date(y, 1, 1), date(y, 12, 31), kind="calendar_year")

    return None


def resolve_relative_date(phrase, reference_date_str=None, query=""):
    """Resolve a natural-language date phrase into a concrete date or date range.

    Understands English and Hinglish phrases such as: today, kal, parso, last week,
    next month, last 3 months, last 30 days, 2 weeks ago, last quarter, Q2 2025,
    Q1 FY25, last financial year, FY 2024-25, FY25, 2025 fiscal year, FYTD, YTD,
    March 2026, last January, 24 Aug 2026, 24/08/2026, 1 Aug to 15 Aug, 2025.

    Returns {"resolved": True, "type": "single"|"range", ...} or
    {"resolved": False, "ambiguous": True, "message": ...} for kal/parso without
    tense hints, or {"resolved": False, "reason": "unsupported_phrase"}.
    """
    if not reference_date_str:
        ref = datetime.now().date()
    else:
        ref = datetime.strptime(reference_date_str, "%Y-%m-%d").date()

    q = (query or "").lower()
    context = f"{(phrase or '').lower()} {q}"
    past = any(cue in context for cue in PAST_CUES)
    future = any(cue in context for cue in FUTURE_CUES)

    result = _resolve_normalized(_normalize_date_phrase(phrase), ref, past, future)

    # The model sometimes passes only a fragment ("2025" for "2025 fiscal year").
    # Scan the full question too and prefer it when it is more specific.
    if q and q.strip() != (phrase or "").lower().strip():
        from_query = _resolve_normalized(_normalize_date_phrase(q), ref, past, future, from_query=True)
        if result is None:
            result = from_query
        elif from_query and from_query.get("resolved") and result.get("kind") == "calendar_year" \
                and from_query.get("kind") in ("financial_year", "fiscal_quarter"):
            result = from_query

    if result is None:
        return {"resolved": False, "reason": "unsupported_phrase", "phrase": phrase}
    return result

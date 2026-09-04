import csv
import random
from datetime import datetime, timedelta

def generate_synthetic_data(filename="settlements.csv", count=130):
    random.seed(42)
    today = datetime.now().date()
    
    # Define relative date options
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    this_week = [today - timedelta(days=i) for i in range(today.weekday() + 1)]
    last_week = [today - timedelta(days=today.weekday() + 1 + i) for i in range(7)]
    
    # Last month and last year relative generation
    first_of_this_month = today.replace(day=1)
    last_of_last_month = first_of_this_month - timedelta(days=1)
    first_of_last_month = last_of_last_month.replace(day=1)
    last_month_days = [(first_of_last_month + timedelta(days=i)) for i in range((last_of_last_month - first_of_last_month).days + 1)]
    
    # Last year dates (around same season)
    last_year_dates = [today - timedelta(days=365 + i) for i in range(-15, 15)]
    
    status_choices = ["settled", "pending", "on_hold"]
    hold_reasons = ["KYC pending", "Risk review", "Compliance verification", "Bank account verification failed"]
    merchants = ["Sukha Pvt Ltd", "Raj General Store", "Techbazaar Online", "Vikas Organics", "Hindustan Retail"]
    
    records = []
    
    for i in range(count):
        tx_id = f"pay_tx_{100000 + i}"
        utr = f"UTR{random.randint(100000000000, 999999999999)}"
        order_amount = round(random.uniform(500, 50000), 2)
        fee = round(order_amount * 0.02, 2)
        gst = round(fee * 0.18, 2)
        
        # Refunds
        refund_amount = 0.0
        rand_refund = random.random()
        if rand_refund < 0.08: # Full refund
            refund_amount = order_amount
        elif rand_refund < 0.18: # Partial refund (~10%)
            refund_amount = round(order_amount * random.uniform(0.1, 0.5), 2)
            
        settlement_amount = round(order_amount - fee - gst - refund_amount, 2)
        if settlement_amount < 0:
            settlement_amount = 0.0
            
        # Select order date with specified distribution
        date_roll = random.random()
        if date_roll < 0.15:
            o_date = yesterday
        elif date_roll < 0.30:
            o_date = day_before
        elif date_roll < 0.50:
            o_date = random.choice(this_week)
        elif date_roll < 0.70:
            o_date = random.choice(last_week)
        elif date_roll < 0.85:
            o_date = random.choice(last_month_days)
        else:
            o_date = random.choice(last_year_dates)
            
        # Status
        status_roll = random.random()
        if status_roll < 0.08:
            status = "on_hold"
            reason = random.choice(hold_reasons)
        elif status_roll < 0.18:
            status = "pending"
            reason = "N/A"
        else:
            status = "settled"
            reason = "N/A"
            
        # Settlement date based on delay status
        if status == "settled":
            delay_roll = random.random()
            if delay_roll < 0.10: # Delayed settlements (~10%)
                delay_days = random.randint(3, 6)
            else:
                delay_days = 2
            s_date = o_date + timedelta(days=delay_days)
        else:
            s_date = "N/A"
            
        records.append({
            "transaction_id": tx_id,
            "utr_number": utr if status == "settled" else "N/A",
            "order_amount": order_amount,
            "razorpay_fee": fee,
            "gst_on_fee": gst,
            "refund_amount": refund_amount,
            "settlement_amount": settlement_amount if status == "settled" else 0.0,
            "order_date": o_date.strftime("%Y-%m-%d"),
            "settlement_date": s_date.strftime("%Y-%m-%d") if isinstance(s_date, datetime.__class__ or timedelta.__class__ or type(today)) else str(s_date),
            "settlement_status": status,
            "hold_reason": reason,
            "merchant_name": random.choice(merchants)
        })
        
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Generated {count} synthetic records in {filename}")

if __name__ == "__main__":
    generate_synthetic_data()

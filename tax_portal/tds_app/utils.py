# tds_app/utils.py
from datetime import date

def get_tds_due_dates(fin_year_start):
    due_dates = []
    for month in range(4, 13):  # Apr to Dec (same year)
        due_dates.append(date(fin_year_start, month, 7))
    for month in range(1, 4):  # Jan to Mar (next year)
        due_dates.append(date(fin_year_start + 1, month, 7))
    
    # Annotate with upcoming/past
    today = date.today()
    tracker = []
    for d in due_dates:
        status = "Upcoming" if d >= today else "Past"
        tracker.append({"month": d.strftime('%B %Y'), "date": d, "status": status})
    
    return tracker

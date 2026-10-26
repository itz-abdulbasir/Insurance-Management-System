"""
IMS — Helper Utilities
Date formatting, currency formatting, and common helper functions.
"""

from datetime import date, timedelta


def format_currency(amount) -> str:
    """Format number as Indian Rupee currency string."""
    if amount is None:
        return "₹0.00"
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return "₹0.00"
    return f"₹{amount:,.2f}"


def format_date(d) -> str:
    """Format a date object or string to DD-MM-YYYY."""
    if d is None:
        return "—"
    if isinstance(d, str):
        return d
    return d.strftime("%d-%m-%Y")


def format_datetime(dt) -> str:
    """Format a datetime to DD-MM-YYYY HH:MM."""
    if dt is None:
        return "—"
    if isinstance(dt, str):
        return dt
    return dt.strftime("%d-%m-%Y %H:%M")


def calculate_end_date(start_date: date, term_years: int) -> date:
    """Calculate policy end date from start date and term in years."""
    try:
        return start_date.replace(year=start_date.year + term_years)
    except ValueError:
        # Handle leap year edge case (Feb 29)
        return start_date.replace(
            year=start_date.year + term_years, day=28
        )


def add_months(sourcedate: date, months: int) -> date:
    """Add months to a date object, handling month overflow and day-of-month clamping."""
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    # Clamping day to the max valid day for the target month
    import calendar
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def generate_premium_dates(start_date: date, frequency: str, term_years: int) -> list:
    """
    Generate list of premium due dates based on frequency and term.
    Ensures correct number of installments (e.g., 2 per year for half-yearly).
    """
    freq_map = {
        "weekly": (0, 7),        # (months, days)
        "monthly": (1, 0),
        "quarterly": (3, 0),
        "half-yearly": (6, 0),
        "yearly": (12, 0)
    }

    m_step, d_step = freq_map.get(frequency, (1, 0))
    
    # Calculate total installments
    if frequency == "weekly":
        total_installments = term_years * 52
    else:
        total_installments = (term_years * 12) // m_step

    dates = []
    for i in range(total_installments):
        if m_step > 0:
            due = add_months(start_date, i * m_step)
        else:
            due = start_date + timedelta(days=i * d_step)
        dates.append(due)

    return dates

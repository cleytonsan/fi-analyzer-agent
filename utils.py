"""
Helper functions for formatting outputs and validating tickers.
"""

def format_percent(x):
    try:
        return f"{x:.2f}%"
    except Exception:
        return 'N/A'


"""setup_db.py — Run once to create all 19 Google Sheets."""
from db import setup_all_sheets
if __name__ == "__main__":
    try:
        setup_all_sheets()
        print("BihiApp DB ready — all sheets created/verified.")
    except Exception as e:
        print(f"Error: {e}")

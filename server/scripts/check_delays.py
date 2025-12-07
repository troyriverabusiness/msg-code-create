import sqlite3
import os

DB_PATH = "data/travel.db"

def check_delays():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delay_patterns'")
        if not cursor.fetchone():
            print("Table 'delay_patterns' does not exist.")
            return

        # Check for specific trains
        trains = ["79", "42", "41", "11"] # ICE numbers
        for t in trains:
            cursor.execute("SELECT * FROM delay_patterns WHERE train_number = ?", (t,))
            rows = cursor.fetchall()
            if rows:
                print(f"Found {len(rows)} entries for train {t}")
                # Print first row
                print(f"  Sample: {rows[0]}")
                
                # Get average
                cursor.execute("SELECT avg(avg_delay) FROM delay_patterns WHERE train_number = ?", (t,))
                avg = cursor.fetchone()[0]
                print(f"  Average Delay: {avg}")
            else:
                print(f"No entries for train {t}")
                
        # Count total rows
        cursor.execute("SELECT count(*) FROM delay_patterns")
        count = cursor.fetchone()[0]
        print(f"Total rows in delay_patterns: {count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_delays()

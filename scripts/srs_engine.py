import sqlite3
import os
import jaconv
from datetime import date, timedelta

# Dynamically locate the database file based on the folder structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'nihongo_graph.db')

def fetch_due_reviews(cursor):
    """Fetches concepts scheduled for review today or earlier."""
    today = date.today()
    cursor.execute('''
        SELECT c.concept_id, c.kanji, c.hiragana, p.hit_rate, p.last_review, p.next_review
        FROM Concept c
        JOIN Progress p ON c.concept_id = p.concept_id
        WHERE p.next_review <= ?
    ''', (today,))
    return cursor.fetchall()

def update_progress(cursor, concept_id, passed, current_hit_rate, last_review):
    """Calculates and updates the forgetting curve mathematically."""
    today = date.today()
    
    # Calculate days since last review to determine current interval
    if last_review:
        last_date = date.fromisoformat(last_review)
        current_interval = (today - last_date).days
        if current_interval < 1:
            current_interval = 1
    else:
        current_interval = 1

    if passed:
        # Exponential multiplier: if correct, double the interval
        new_interval = current_interval * 2
        new_hit_rate = min(1.0, current_hit_rate + 0.1) # Max hit rate is 100%
    else:
        # Penalty: if incorrect, reset interval to 1 day
        new_interval = 1
        new_hit_rate = max(0.0, current_hit_rate - 0.2) # Min hit rate is 0%

    next_review_date = today + timedelta(days=new_interval)

    cursor.execute('''
        UPDATE Progress
        SET hit_rate = ?, last_review = ?, next_review = ?
        WHERE concept_id = ?
    ''', (new_hit_rate, today, next_review_date, concept_id))
    
    return new_interval

def main():
    print("\n" + "="*40)
    print("      NIHONGOGRAPH - SRS ENGINE")
    print("="*40)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        due_items = fetch_due_reviews(cursor)
        
        if not due_items:
            print("\n[OK] You are all caught up! No reviews scheduled for today.")
            return

        print(f"\nYou have {len(due_items)} concept(s) to review today.\n")

        for item in due_items:
            concept_id, kanji, hiragana, hit_rate, last_rev, next_rev = item
            
            print(f"\nTarget: {kanji}")
            user_reading = input("Enter reading (in Romaji or Kana): ").strip()
            
            # Validate user input using the modern jaconv library
            user_hiragana = jaconv.alphabet2kana(user_reading)
            
            passed = (user_hiragana == hiragana)
            
            if passed:
                print(f"  [CORRECT] Excellent! The reading is {hiragana}.")
            else:
                print(f"  [WRONG] The correct reading was: {hiragana}.")

            # Calculate and save the new review date
            new_interval = update_progress(cursor, concept_id, passed, hit_rate, last_rev)
            conn.commit()
            
            print(f"  -> Next review scheduled in {new_interval} day(s).")
            
        print("\n[OK] Session complete. Keep up the good work!")

if __name__ == '__main__':
    main()
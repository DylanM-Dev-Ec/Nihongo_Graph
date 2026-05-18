import sqlite3
import os
import jaconv
from datetime import date, timedelta

# Dynamically locate the database file based on the folder structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'kioku_engine.db')

def fetch_due_reviews(cursor):
    """Fetches concepts scheduled for review today or earlier, including new items."""
    today = date.today().isoformat()
    cursor.execute('''
        SELECT c.concept_id, c.kanji, c.hiragana, p.interval_days, p.repetitions, p.ease_factor
        FROM Concept c
        JOIN Progress p ON c.concept_id = p.concept_id
        WHERE p.next_review <= ? OR p.next_review IS NULL
    ''', (today,))
    return cursor.fetchall()

def update_progress(cursor, concept_id, passed, current_interval, repetitions, ease_factor):
    """Calculates and updates the SuperMemo-2 (SM-2) algorithm variables."""
    today = date.today().isoformat()
    
    # Map binary pass/fail to SM-2 quality (q) scale (0-5)
    # 4: Correct response (standard for typed input)
    # 0: Complete blackout / wrong answer
    q = 4 if passed else 0

    # Calculate new SM-2 values
    if q >= 3:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(current_interval * ease_factor)
        new_repetitions = repetitions + 1
    else:
        new_repetitions = 0
        new_interval = 1

    # Calculate new ease factor
    new_ease_factor = ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    
    # Floor limit for ease_factor
    if new_ease_factor < 1.3:
        new_ease_factor = 1.3

    next_review_date = (date.today() + timedelta(days=new_interval)).isoformat()

    cursor.execute('''
        UPDATE Progress
        SET interval_days = ?, repetitions = ?, ease_factor = ?, last_review = ?, next_review = ?
        WHERE concept_id = ?
    ''', (new_interval, new_repetitions, new_ease_factor, today, next_review_date, concept_id))
    
    return new_interval

def main():
    print("\n" + "="*40)
    print("      KIOKU ENGINE - SRS CORE (SM-2)")
    print("="*40)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        due_items = fetch_due_reviews(cursor)
        
        if not due_items:
            print("\n[OK] You are all caught up! No reviews scheduled for today.")
            return

        print(f"\nYou have {len(due_items)} concept(s) to review today.\n")

        for item in due_items:
            concept_id, kanji, hiragana, interval_days, repetitions, ease_factor = item
            
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
            new_interval = update_progress(cursor, concept_id, passed, interval_days, repetitions, ease_factor)
            conn.commit()
            
            print(f"  -> Next review scheduled in {new_interval} day(s).")
            
        print("\n[OK] Session complete. Keep up the good work!")

if __name__ == '__main__':
    main()
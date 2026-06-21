import os
import time

from app import create_app, db, seed_database

app = create_app()

with app.app_context():
    max_retries = 15
    for attempt in range(1, max_retries + 1):
        try:
            with db.engine.connect() as conn:
                conn.close()
            print(f"[run.py] DB connection OK (attempt {attempt})")
            db.create_all()
            seed_database(db)
            print("[run.py] Tables created and seeded.")
            break
        except Exception as exc:
            print(f"[run.py] DB not ready (attempt {attempt}/{max_retries}): {exc}")
            if attempt == max_retries:
                raise
            time.sleep(3)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(debug=False, host="0.0.0.0", port=port)

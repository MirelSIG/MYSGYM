import os
import time

from app import create_app
from app import db

app = create_app()

with app.app_context():
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            db.engine.connect().close()
            db.create_all()
            break
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(3)

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    app.run(debug=False, host='0.0.0.0', port=port)

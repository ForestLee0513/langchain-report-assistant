from sqlalchemy import text

from app.core.db import db

def db_preflight():
    try:
        with db.connect() as transction:
            transction.execute(text("SELECT 1"))
        yield
        db.dispose()
    except:
         raise RuntimeError("ERROR: DB cannot be initialized. please check a config")
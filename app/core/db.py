from sqlalchemy import create_engine

from app.core.settings import settings


db = create_engine(str(settings.DATABASE_URL))

from sqlalchemy import create_engine, Column, Integer, BIGINT
from sqlalchemy.ext.declarative import declarative_base

from config import DATABASE_URI

Base = declarative_base()

class Scores(Base):

    __tablename__ = "scores"

    id = Column("id", Integer, primary_key=True)
    user_id = Column("user_id", BIGINT, unique=True, nullable=False)
    score = Column("score", Integer, default=0)


engine = create_engine(DATABASE_URI, echo=True)

Base.metadata.create_all(bind=engine)


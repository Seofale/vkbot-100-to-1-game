from sqlalchemy import Column, String, Integer

from app.store.database.sqlalchemy_base import Base


class AdminModel(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    email = Column(String(64), unique=True)
    password = Column(String(64))

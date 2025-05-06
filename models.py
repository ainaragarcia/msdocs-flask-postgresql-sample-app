from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates
from datetime import datetime
from extensions import db

class Imagen(db.Model):
    __tablename__ = 'imagenes'

    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    filename = Column(String(100))
    date = Column(DateTime, default=datetime.utcnow)
    rojo = Column(Integer)
    verde = Column(Integer)
    azul = Column(Integer)

    def __str__(self):
        return f"{self.username} - {self.filename} ({self.date})"
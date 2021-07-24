from enum import unique
from app import db

class Attack(db.Model):
    attackId = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(200), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    usage = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
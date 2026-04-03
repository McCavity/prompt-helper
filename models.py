from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    prompts = db.relationship("Prompt", backref="user", lazy="dynamic")


class Prompt(db.Model):
    __tablename__ = "prompts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    expertise = db.Column(db.Text, nullable=False)
    task = db.Column(db.Text, nullable=False)
    context = db.Column(db.Text, nullable=False)
    constraints = db.Column(db.Text, nullable=True)
    assembled = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (db.Index("ix_prompts_user_created", "user_id", "created_at"),)

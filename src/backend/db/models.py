from sqlalchemy import (
    Column, Integer, BigInteger, Text, Float, ForeignKey, TIMESTAMP, func
)
from sqlalchemy.orm import relationship

from .database import Base

"""
One row per pipeline run (one POST /analyze call or one main.py execution).
"""
class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True)
    search_query = Column(Text, nullable=False)
    row_limit = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="run", cascade="all, delete-orphan")


"""
Each individual post / comment / review collected from a connector.
"""
class Post(Base):
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    platform = Column(Text, nullable=False)
    product_id = Column(Text)
    text_content = Column(Text)
    clean_text = Column(Text)
    engagement = Column(Integer)
    url = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    run = relationship("AnalysisRun", back_populates="posts")
    scores = relationship("AspectScore", back_populates="post", cascade="all, delete-orphan")


"""
Long-format aspect scores - one row per (post, aspect).
This format is ideal for Grafana time series queries.
"""
class AspectScore(Base):
    __tablename__ = "aspect_scores"

    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(Integer, ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    platform = Column(Text, nullable=False)
    aspect = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="scores")


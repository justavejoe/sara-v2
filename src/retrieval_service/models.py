from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector

# This defines the base class that all database models inherit from.
# This is the 'Base' that Alembic is looking for.
Base = declarative_base()

class Document(Base):
    """
    SQLAlchemy model for the 'documents' table.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    source = Column(String(255), nullable=False)
    title = Column(Text, nullable=True)
    authors = Column(Text, nullable=True)
    publication_date = Column(String(50), nullable=True)
    content = Column(Text, nullable=False)
    # The 'embedding' column must match the dimensions of your vectors.
    embedding = Column(Vector(768), nullable=False)

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', source='{self.source}')>"
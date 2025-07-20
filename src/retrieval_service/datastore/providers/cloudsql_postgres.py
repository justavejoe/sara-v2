import asyncio
from typing import Literal, List
import asyncpg
from google.cloud.sql.connector import Connector, IPTypes
from pgvector.asyncpg import register_vector
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from .. import datastore

class Config(BaseModel, datastore.AbstractConfig):
    kind: Literal["cloudsql-postgres"]
    project: str
    region: str
    instance: str
    user: str
    password: str
    database: str

class Client(datastore.Client[Config]):
    __pool: AsyncEngine

    @datastore.classproperty
    def kind(cls):
        return "cloudsql-postgres"

    def __init__(self, pool: AsyncEngine):
        self.__pool = pool

    @classmethod
    async def create(cls, config: Config) -> "Client":
        loop = asyncio.get_running_loop()
        async def getconn() -> asyncpg.Connection:
            async with Connector(loop=loop) as connector:
                conn: asyncpg.Connection = await connector.connect_async(
                    f"{config.project}:{config.region}:{config.instance}",
                    "asyncpg",
                    user=f"{config.user}",
                    password=f"{config.password}",
                    db=f"{config.database}",
                    ip_type=IPTypes.PSC,
                )
            await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
            await register_vector(conn)
            return conn
        pool = create_async_engine("postgresql+asyncpg://", async_creator=getconn)
        if pool is None:
            raise TypeError("pool not instantiated")
        return cls(pool)

    async def initialize_data(self, paper_chunks: list[dict]) -> None:
        """
        Initializes the database with a list of chunks from any source.
        """
        async with self.__pool.connect() as conn:
            # Drop and recreate the table with the new, richer schema
            await conn.execute(text("DROP TABLE IF EXISTS document_chunks CASCADE"))
            await conn.execute(
                text(
                    """
                    CREATE TABLE document_chunks(
                      id SERIAL PRIMARY KEY,
                      source_filename TEXT,
                      title TEXT,
                      authors TEXT,
                      publication_date TEXT,
                      content TEXT NOT NULL,
                      embedding vector(768) NOT NULL
                    )
                    """
                )
            )
            # Insert the data passed into the function
            await conn.execute(
                text(
                    """
                    INSERT INTO document_chunks (source_filename, title, authors, publication_date, content, embedding) 
                    VALUES (:source_filename, :title, :authors, :publication_date, :content, :embedding)
                    """
                ),
                paper_chunks
            )
            await conn.commit()

# In datastore/providers/cloudsql_postgres.py

async def search_documents(
    self, query_embedding: list[float], top_k: int
) -> list[dict]:
    async with self.__pool.connect() as conn:
        s = text(
            """
            SELECT 
                source_filename, 
                title, 
                authors, 
                publication_date,
                content, 
                1 - (embedding <=> :query_embedding) AS similarity
            FROM document_chunks
            ORDER BY similarity DESC
            LIMIT :top_k
            """
        )
        params = {
            # --- CHANGE THIS LINE ---
            "query_embedding": query_embedding, # Remove the str() cast
            # ------------------------
            "top_k": top_k,
        }
        results = (await conn.execute(s, params)).mappings().fetchall()
    return [dict(r) for r in results]

    async def close(self):
        await self.__pool.dispose()
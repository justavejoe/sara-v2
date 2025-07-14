# Copyright 2024 Google LLC
# (license header)

import asyncio
from typing import Literal
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
        async with self.__pool.connect() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS paper_chunks CASCADE"))
            await conn.execute(
                text(
                    """
                    CREATE TABLE paper_chunks(
                      id SERIAL PRIMARY KEY,
                      paper_id TEXT,
                      chunk_id INT,
                      content TEXT NOT NULL,
                      embedding vector(768) NOT NULL
                    )
                    """
                )
            )
            await conn.execute(
                text(
                    """INSERT INTO paper_chunks (paper_id, chunk_id, content, embedding) VALUES (:paper_id, :chunk_id, :content, :embedding)"""
                ),
                paper_chunks
            )
            await conn.commit()

    async def search_documents(
        self, query_embedding: list[float], top_k: int
    ) -> list[dict]:
        async with self.__pool.connect() as conn:
            s = text(
                """
                SELECT paper_id, content, 1 - (embedding <=> :query_embedding) AS similarity
                FROM paper_chunks
                ORDER BY similarity DESC
                LIMIT :top_k
                """
            )
            params = {
                "query_embedding": query_embedding,
                "top_k": top_k,
            }
            results = (await conn.execute(s, params)).mappings().fetchall()
        return [dict(r) for r in results]

    async def close(self):
        await self.__pool.dispose()
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
from datetime import datetime
from typing import Any, Dict, Literal, Optional

import asyncpg
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
from pgvector.asyncpg import register_vector
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

import models

from .. import datastore

POSTGRES_IDENTIFIER = "cloudsql-postgres"


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

        pool = create_async_engine(
            "postgresql+asyncpg://",
            async_creator=getconn,
        )
        if pool is None:
            raise TypeError("pool not instantiated")
        return cls(pool)

    async def initialize_data(self) -> None:
        import pandas as pd
        processed_papers_df = pd.read_csv("./data/processed_papers.csv")
        paper_chunks = processed_papers_df.to_dict('records')

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